#!/usr/bin/env python3
"""code-sync-check.py — code-watch queue + state manager and SessionStart surfacer.

Owns the two code-watch state files under `.vault-meta/`:
  - code-sync-queue.jsonl   append-only; one pending entry per watched commit
  - code-sync-state.json    watched repos + their sync mode + last_synced_commit

Default action (no flags) is the SessionStart surfacer: if the queue has pending
entries, print a short plain-text drift summary to stdout (which Claude Code
injects as session context). Always exits 0 and is silent in non-vault dirs, so
it is safe to wire into the global SessionStart hook.

The git hook installed by `bin/setup-code-watch.sh` calls `--enqueue`; the
`/wiki-code-watch` command calls `--register` / `--unregister` / `--status`;
`bin/code-sync-launch.sh` calls `--repo-mode`; `/wiki-code-ingest --sync` calls
`--mark-synced` after draining.

Usage:
  code-sync-check.py                              # SessionStart summary (default)
  code-sync-check.py --enqueue --repo R --commit SHA
  code-sync-check.py --register --repo R --mode in-session|autonomous
  code-sync-check.py --unregister --repo R
  code-sync-check.py --status [--json]
  code-sync-check.py --repo-mode R               # prints in-session|autonomous|(empty)
  code-sync-check.py --mark-synced --repo R [--commit SHA]

Exit codes:
  0 — success (default action always 0)
  2 — usage error
"""

import argparse
import fcntl
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
META_DIR = VAULT_ROOT / ".vault-meta"
QUEUE_PATH = META_DIR / "code-sync-queue.jsonl"
STATE_PATH = META_DIR / "code-sync-state.json"
LOCK_PATH = META_DIR / ".code-sync.lock"

MAX_PATHS_SHOWN = 8


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_display(s, cap=200):
    """Neutralize untrusted git-derived strings before they reach surfaced
    SessionStart context. A path/commit can contain newlines or control chars
    (git filesystem paths allow them); printed raw they could inject fake lines
    into the model's context. Collapse anything non-printable to '·' and cap."""
    s = str(s)
    out = "".join(ch if (ch.isprintable() and ch not in "\r\n") else "·" for ch in s)
    return out[:cap]


def real(p):
    return os.path.realpath(os.path.expanduser(p))


# ── lock (for state writes + queue rewrites) ─────────────────────────────────
def _lock():
    META_DIR.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _unlock(fd):
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _atomic_write(path, text):
    META_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        Path(tmp).replace(path)
    except Exception:
        try:
            Path(tmp).unlink()
        except OSError:
            pass
        raise


# ── state ─────────────────────────────────────────────────────────────────────
def load_state():
    if not STATE_PATH.is_file():
        return {"schema_version": 1, "configured_at": None, "watched_repos": []}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": 1, "configured_at": None, "watched_repos": []}


def save_state(state):
    _atomic_write(STATE_PATH, json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def find_repo(state, repo):
    target = real(repo)
    for r in state.get("watched_repos", []):
        if real(r.get("path", "")) == target:
            return r
    return None


# ── queue ─────────────────────────────────────────────────────────────────────
def read_queue():
    if not QUEUE_PATH.is_file():
        return []
    rows = []
    for line in QUEUE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def append_queue(entry):
    META_DIR.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def changed_paths(repo, commit):
    # --root makes the initial commit (which has no parent) list all its files
    # instead of an empty diff; harmless for non-root commits.
    r = subprocess.run(
        ["git", "-C", repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit],
        capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return []
    return [p for p in r.stdout.splitlines() if p.strip()]


# ── actions ───────────────────────────────────────────────────────────────────
def action_enqueue(repo, commit):
    entry = {
        "ts": now_iso(),
        "repo": real(repo),
        "commit": commit,
        "changed_paths": changed_paths(repo, commit),
        "status": "pending",
    }
    append_queue(entry)
    return 0


def action_register(repo, mode):
    fd = _lock()
    try:
        state = load_state()
        existing = find_repo(state, repo)
        branch = subprocess.run(["git", "-C", repo, "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True, timeout=10).stdout.strip() or "?"
        if existing:
            existing["mode"] = mode
            existing["branch"] = branch
        else:
            state.setdefault("watched_repos", []).append({
                "path": real(repo), "branch": branch, "mode": mode,
                "last_synced_commit": None, "registered_at": now_iso(),
            })
        state["configured_at"] = now_iso()
        save_state(state)
    finally:
        _unlock(fd)
    print(f"registered: {real(repo)} (mode={mode})")
    return 0


def action_unregister(repo):
    fd = _lock()
    try:
        # target/before/state are read in the post-finally print, but only on the
        # success path — if save_state() raises, the exception propagates through
        # finally and is caught by main()'s outer handler, so the print never runs.
        state = load_state()
        target = real(repo)
        before = len(state.get("watched_repos", []))
        state["watched_repos"] = [r for r in state.get("watched_repos", [])
                                  if real(r.get("path", "")) != target]
        save_state(state)
    finally:
        _unlock(fd)
    print(f"unregistered: {target}" if before != len(state["watched_repos"]) else f"not watched: {target}")
    return 0


def action_status(as_json):
    state = load_state()
    pending = [e for e in read_queue() if e.get("status") == "pending"]
    if as_json:
        print(json.dumps({"watched_repos": state.get("watched_repos", []),
                          "pending_commits": len(pending)}, indent=2))
        return 0
    repos = state.get("watched_repos", [])
    if not repos:
        print("No repos are being watched. Run `bash bin/setup-code-watch.sh <repo>`.")
        return 0
    print("Watched repos:")
    for r in repos:
        print(f"  {r['path']}  [mode={r.get('mode','in-session')}, branch={r.get('branch','?')}, "
              f"last_synced={r.get('last_synced_commit') or 'never'}]")
    print(f"Pending commits in queue: {len(pending)}")
    return 0


def action_repo_mode(repo):
    r = find_repo(load_state(), repo)
    print(r.get("mode", "") if r else "")
    return 0


def action_mark_synced(repo, commit):
    fd = _lock()
    try:
        target = real(repo)
        rows = read_queue()
        for e in rows:
            if real(e.get("repo", "")) == target and e.get("status") == "pending":
                e["status"] = "synced"
                e["synced_at"] = now_iso()
        _atomic_write(QUEUE_PATH, "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in rows))
        state = load_state()
        r = find_repo(state, repo)
        if r and commit:
            r["last_synced_commit"] = commit
            save_state(state)
    finally:
        _unlock(fd)
    print(f"marked synced: {target}")
    return 0


def action_surface():
    """Default SessionStart action. Print a short drift summary if anything is pending."""
    pending = [e for e in read_queue() if e.get("status") == "pending"]
    if not pending:
        return 0
    by_repo = {}
    for e in pending:
        by_repo.setdefault(e.get("repo", "?"), []).extend(e.get("changed_paths", []))
    n_repos = len(by_repo)
    print(f"[code-sync] {len(pending)} new commit(s) across {n_repos} repo(s) since last wiki sync.")
    for repo, paths in by_repo.items():
        uniq = sorted(set(paths))
        shown = ", ".join(safe_display(p, cap=120) for p in uniq[:MAX_PATHS_SHOWN])
        more = f", +{len(uniq) - MAX_PATHS_SHOWN} more" if len(uniq) > MAX_PATHS_SHOWN else ""
        print(f"  {safe_display(repo)}: {len(uniq)} path(s) changed — {shown}{more}")
    print("  Run `/wiki-code-ingest --sync` to refresh the affected Mode B pages.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Code-watch queue/state manager + SessionStart surfacer.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--enqueue", action="store_true")
    g.add_argument("--register", action="store_true")
    g.add_argument("--unregister", action="store_true")
    g.add_argument("--status", action="store_true")
    g.add_argument("--repo-mode", action="store_true")
    g.add_argument("--mark-synced", action="store_true")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--commit", default=None)
    ap.add_argument("--mode", default="in-session", choices=["in-session", "autonomous"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        if args.enqueue:
            if not (args.repo and args.commit):
                print("ERR: --enqueue needs --repo and --commit", file=sys.stderr)
                return 2
            return action_enqueue(args.repo, args.commit)
        if args.register:
            if not args.repo:
                print("ERR: --register needs --repo", file=sys.stderr)
                return 2
            return action_register(args.repo, args.mode)
        if args.unregister:
            if not args.repo:
                print("ERR: --unregister needs --repo", file=sys.stderr)
                return 2
            return action_unregister(args.repo)
        if args.status:
            return action_status(args.json)
        if args.repo_mode:
            if not args.repo:
                print("ERR: --repo-mode needs --repo", file=sys.stderr)
                return 2
            return action_repo_mode(args.repo)
        if args.mark_synced:
            if not args.repo:
                print("ERR: --mark-synced needs --repo", file=sys.stderr)
                return 2
            return action_mark_synced(args.repo, args.commit)
        return action_surface()
    except Exception as e:  # never let a hook crash the session
        print(f"code-sync-check: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
