#!/usr/bin/env python3
"""code-signals.py — git anchors, churn, and best-effort import edges.

Part of the v1.10 Mode B code-ingest pipeline. Emits the deterministic git
signals that (a) seed the drift anchors stored in code-page frontmatter and
(b) scaffold module dependency wikilinks.

GITIGNORE GUARANTEE: every file considered comes from the same gitignore-aware
enumeration as code-scan.py. Import edges are scanned only over non-ignored
files; anchors come from `git ls-tree HEAD` (tracked files only, never ignored).

The drift anchor for a page's source path is `git rev-parse HEAD:<path>` — a blob
SHA for a file, a tree SHA for a directory. `git.json.anchors` is a precomputed
map of every tracked path → that SHA, so the ingest skill can populate
`code_anchors` without extra git calls. `wiki-lint` later recomputes the same
value to detect drift.

Usage:
  code-signals.py <repo> [--subpath PATH] [--since "90 days ago"] [--out DIR]

Outputs (JSON, atomic write):
  <out>/git.json    { generated_at, git_available, head,
                      anchors: {path: sha},
                      churn_top: [{path, commits}],
                      recent_commits: [{sha, date, subject}] }
  <out>/edges.json  { generated_at, nodes: [path],
                      edges: [{from, to, kind, external}] }

Exit codes:
  0 — success (also when not a git repo: anchors empty, edges still emitted)
  2 — usage error
  3 — repo path missing or not a directory
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent

FALLBACK_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".next",
    ".nuxt", "target", ".gradle", ".idea", ".vscode", "vendor", ".cache",
}

EXT_LANG = {
    ".py": "python", ".pyi": "python",
    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".go": "go", ".rs": "rust", ".rb": "ruby",
}
JS_EXTS = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts")


def die(code, msg):
    print(f"ERR: {msg}", file=sys.stderr)
    raise SystemExit(code)


# ── gitignore-aware enumeration (keep in sync with code-scan.py) ─────────────
def is_git_repo(repo):
    try:
        r = subprocess.run(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True, timeout=10)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_repo_files(repo, subpath=None):
    if is_git_repo(repo):
        cmd = ["git", "-C", repo, "ls-files", "--cached", "--others",
               "--exclude-standard", "-z"]
        if subpath:
            cmd += ["--", subpath]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            die(3, f"git ls-files failed: {r.stderr.strip()}")
        return sorted({p for p in r.stdout.split("\0") if p})
    base = os.path.join(repo, subpath) if subpath else repo
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in FALLBACK_IGNORE_DIRS]
        for fn in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, fn), repo))
    return sorted(out)


def write_json(out_dir, name, obj):
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=name + ".", suffix=".tmp", dir=str(out_dir))
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
        Path(tmp).replace(out_dir / name)
    except Exception:
        try:
            Path(tmp).unlink()
        except OSError:
            pass
        raise


def repo_slug(repo):
    s = re.sub(r"[^\w.-]+", "-", os.path.basename(os.path.abspath(repo)) or "repo").strip("-")
    return s or "repo"


def _git(repo, *args, timeout=60):
    return subprocess.run(["git", "-C", repo, *args],
                          capture_output=True, text=True, timeout=timeout)


# ── git signals ──────────────────────────────────────────────────────────────
def git_signals(repo, subpath, since, allowed):
    out = {"git_available": False, "head": None, "anchors": {},
           "churn_top": [], "recent_commits": []}
    if not is_git_repo(repo):
        print("warn: not a git repo — anchors/churn unavailable", file=sys.stderr)
        return out
    out["git_available"] = True

    head = _git(repo, "rev-parse", "HEAD")
    out["head"] = head.stdout.strip() if head.returncode == 0 else None

    # anchors: every tracked path (blob for files, tree for dirs) → object id.
    lt_cmd = ["ls-tree", "-r", "-t", "-z", "HEAD"]
    if subpath:
        lt_cmd += ["--", subpath]
    lt = _git(repo, *lt_cmd)
    if lt.returncode == 0:
        for rec in lt.stdout.split("\0"):
            if not rec or "\t" not in rec:
                continue
            meta, path = rec.split("\t", 1)
            parts = meta.split()
            if len(parts) >= 3:
                out["anchors"][path] = parts[2]  # <mode> <type> <object>

    # recent commits (within window), capped.
    US = "\x1f"
    log_cmd = ["log", "-n", "50", f"--since={since}",
               f"--pretty=format:%H{US}%cs{US}%s"]
    if subpath:
        log_cmd += ["--", subpath]
    lg = _git(repo, *log_cmd)
    if lg.returncode == 0:
        for line in lg.stdout.splitlines():
            if US in line:
                sha, date, subject = line.split(US, 2)
                out["recent_commits"].append({"sha": sha, "date": date, "subject": subject})

    # churn: file appearances within the window.
    churn_cmd = ["log", f"--since={since}", "--name-only", "--pretty=format:"]
    if subpath:
        churn_cmd += ["--", subpath]
    ch = _git(repo, *churn_cmd)
    if ch.returncode == 0:
        counts = {}
        for line in ch.stdout.splitlines():
            p = line.strip()
            if p and p in allowed:
                counts[p] = counts.get(p, 0) + 1
        out["churn_top"] = [{"path": p, "commits": c} for p, c in
                            sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:20]]
    return out


# ── import edges (regex, best-effort — NOT a parser) ─────────────────────────
PY_IMPORT = re.compile(r"^\s*(?:from\s+([.\w]+)\s+import\b|import\s+([.\w]+))", re.MULTILINE)
JS_IMPORT = re.compile(r"""(?:import\b[^'"]*?from\s*|import\s*|export\b[^'"]*?from\s*)['"]([^'"]+)['"]""")
JS_REQUIRE = re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)""")
GO_IMPORT = re.compile(r"""(?m)^\s*(?:import\s+)?(?:[\w.]+\s+)?"([^"]+)"\s*$""")
RS_USE = re.compile(r"^\s*use\s+([\w:]+)", re.MULTILINE)
RB_REQUIRE = re.compile(r"""(?m)^\s*require(_relative)?\s+['"]([^'"]+)['"]""")


def lang_of(path):
    return EXT_LANG.get(os.path.splitext(path)[1].lower(), "other")


def read_text(repo, rel):
    try:
        with open(os.path.join(repo, rel), "rb") as fh:
            data = fh.read(1_000_000)
        if b"\x00" in data[:8192]:
            return None
        return data.decode("utf-8", "replace")
    except OSError:
        return None


def resolve_python(target, from_file, fileset):
    target = target.strip()
    if target.startswith("."):
        ndots = len(target) - len(target.lstrip("."))
        rest = target[ndots:]
        base = os.path.dirname(from_file)
        for _ in range(ndots - 1):
            base = os.path.dirname(base)
        rel = os.path.normpath(os.path.join(base, rest.replace(".", "/"))) if rest else base
    else:
        rel = target.replace(".", "/")
    for cand in (rel + ".py", os.path.join(rel, "__init__.py")):
        cand = os.path.normpath(cand)
        if cand in fileset:
            return cand
    return None


def resolve_relative_js(target, from_file, fileset):
    if not (target.startswith(".") or target.startswith("/")):
        return None
    base = os.path.dirname(from_file)
    rel = os.path.normpath(os.path.join(base, target))
    cands = [rel] + [rel + e for e in JS_EXTS] + [os.path.join(rel, "index" + e) for e in JS_EXTS]
    for cand in cands:
        cand = os.path.normpath(cand)
        if cand in fileset:
            return cand
    return None


def import_edges(repo, files):
    fileset = set(files)
    edges = []
    seen = set()

    def add(frm, to, kind, external):
        key = (frm, to, kind)
        if key not in seen:
            seen.add(key)
            edges.append({"from": frm, "to": to, "kind": kind, "external": external})

    for rel in files:
        lang = lang_of(rel)
        if lang == "other":
            continue
        text = read_text(repo, rel)
        if text is None:
            continue
        if lang == "python":
            for m in PY_IMPORT.finditer(text):
                target = m.group(1) or m.group(2)
                resolved = resolve_python(target, rel, fileset)
                add(rel, resolved or target, "import", resolved is None)
        elif lang in ("typescript", "javascript"):
            for rx, kind in ((JS_IMPORT, "import"), (JS_REQUIRE, "require")):
                for m in rx.finditer(text):
                    target = m.group(1)
                    resolved = resolve_relative_js(target, rel, fileset)
                    add(rel, resolved or target, kind, resolved is None)
        elif lang == "go":
            for m in GO_IMPORT.finditer(text):
                add(rel, m.group(1), "import", True)  # go: external module paths
        elif lang == "rust":
            for m in RS_USE.finditer(text):
                add(rel, m.group(1), "use", not m.group(1).startswith(("crate", "self", "super")))
        elif lang == "ruby":
            for m in RB_REQUIRE.finditer(text):
                target, relative = m.group(2), bool(m.group(1))
                resolved = resolve_relative_js(target, rel, fileset) if relative else None
                add(rel, resolved or target, "require", resolved is None)
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nodes": files,
        "edges": edges,
    }


def main():
    ap = argparse.ArgumentParser(description="Git anchors + churn + import edges (gitignore-aware).")
    ap.add_argument("repo", help="repository root path")
    ap.add_argument("--subpath", default=None)
    ap.add_argument("--since", default="90 days ago", help="git --since window for churn/commits")
    ap.add_argument("--out", default=None, help="output dir (default: .raw/code/<slug>/)")
    args = ap.parse_args()

    if not os.path.isdir(args.repo):
        die(3, f"repo path is not a directory: {args.repo}")

    out_dir = Path(args.out) if args.out else (VAULT_ROOT / ".raw" / "code" / repo_slug(args.repo))
    files = list_repo_files(args.repo, args.subpath)

    git_out = git_signals(args.repo, args.subpath, args.since, set(files))
    git_out["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    edges_out = import_edges(args.repo, files)

    write_json(out_dir, "git.json", git_out)
    write_json(out_dir, "edges.json", edges_out)
    print(f"code-signals: git={git_out['git_available']} head={git_out['head'] and git_out['head'][:7]} "
          f"anchors={len(git_out['anchors'])} edges={len(edges_out['edges'])} → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
