#!/usr/bin/env python3
"""code-anchor-check.py — code-drift lint for Mode B wiki pages.

For every wiki page that carries `code_anchors` (written by /wiki-code-ingest),
recompute the current git object SHA of each anchored path and report pages whose
underlying source has changed, moved, or fallen out of the git tree since ingest.
Read-only; never modifies wiki pages or the repo.

Anchors are flat `"<path>@<sha>"` strings (split on the LAST '@'). The recorded
SHA is `git rev-parse HEAD:<path>` at ingest time — a blob SHA for a file, a tree
SHA for a directory. This lint recomputes the same value and compares.

Feature-gated like the other DragonScale lints: exits 10 if `git` is missing or
11 if --repo is not a git work tree, so `wiki-lint` can no-op gracefully. Drift
itself is a *finding*, not a script error (exit stays 0), matching how
tiling-check reports duplicate pairs at exit 0.

Usage:
  code-anchor-check.py                 # scan; human summary to stdout
  code-anchor-check.py --peek          # diagnostics only (git present? repo? N anchored pages)
  code-anchor-check.py --report PATH   # also append a "## Code Drift" section to PATH
  code-anchor-check.py --repo PATH     # repo to hash against (default: $CODE_REPO_ROOT or vault root)
  code-anchor-check.py --json          # machine-readable findings

Exit codes:
  0  — success (drift may be reported in the body; that is a finding, not an error)
  2  — usage error
  3  — unreadable wiki directory
  10 — `git` binary not found
  11 — --repo is not inside a git work tree
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = VAULT_ROOT / "wiki"

# Shared exclusions (mirror tiling-check.py). Code pages are normal pages; these
# just keep meta/index/symlink files out of the scan.
EXCLUDE_TYPES = {"meta", "fold"}
EXCLUDE_FILENAMES = {
    "_index.md", "index.md", "log.md", "hot.md", "overview.md",
    "dashboard.md", "Wiki Map.md", "getting-started.md",
}
EXCLUDE_PATH_PREFIXES = ("wiki/folds/", "wiki/meta/")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_WIKI_UNREADABLE = 3
EXIT_NO_GIT = 10
EXIT_NOT_A_REPO = 11

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
KEY_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def log(msg):
    print(msg, file=sys.stderr)


# ── flat-YAML frontmatter reader (no PyYAML; schema is flat-YAML by rule) ─────
def parse_frontmatter(text):
    """Extract scalars and block lists from flat frontmatter. Good enough for
    `type`, `title`, `ingest_commit` (scalars) and `code_anchors`,
    `source_paths` (block lists). Inline `[]` stays a scalar string."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    cur_key = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and cur_key is not None and isinstance(fm.get(cur_key), list):
            fm[cur_key].append(stripped[2:].strip().strip('"').strip("'"))
            continue
        km = KEY_RE.match(line)
        if km:
            key, rest = km.group(1), km.group(2).strip()
            if rest == "":
                cur_key = key
                fm[key] = []          # tentative block list
            else:
                cur_key = None
                fm[key] = rest.strip().strip('"').strip("'")
        else:
            cur_key = None
    return fm


def iter_code_pages(vault_root=VAULT_ROOT):
    """Yield (rel_path, title, fm, anchors) for every wiki page with code_anchors."""
    wiki_dir = vault_root / "wiki"
    for p in sorted(wiki_dir.rglob("*.md")):
        if p.is_symlink():
            continue
        rel = p.relative_to(vault_root).as_posix()
        if p.name in EXCLUDE_FILENAMES or any(rel.startswith(pre) for pre in EXCLUDE_PATH_PREFIXES):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = parse_frontmatter(text)
        if fm.get("type") in EXCLUDE_TYPES:
            continue
        anchors = [a for a in fm.get("code_anchors", []) if isinstance(a, str) and a]
        if not anchors:
            continue
        title = fm.get("title") or p.stem
        yield rel, title, fm, anchors


# ── git helpers ──────────────────────────────────────────────────────────────
def git_available():
    try:
        return subprocess.run(["git", "--version"], capture_output=True,
                              text=True, timeout=10).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def is_git_repo(repo):
    try:
        r = subprocess.run(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True, timeout=10)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def head_sha(repo):
    r = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                       capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if r.returncode == 0 else None


def object_sha(repo, path):
    """Current `git rev-parse HEAD:<path>` (blob for file, tree for dir), or None
    if the path is not in HEAD (untracked or deleted)."""
    p = path.rstrip("/")
    r = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "--quiet", f"HEAD:{p}"],
                       capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if r.returncode == 0 else None


def split_anchor(anchor):
    """'src/a.py@deadbeef' -> ('src/a.py', 'deadbeef'); split on LAST '@'."""
    if "@" not in anchor:
        return anchor, None
    path, sha = anchor.rsplit("@", 1)
    return path.strip(), sha.strip()


# ── core scan ────────────────────────────────────────────────────────────────
def scan(repo, vault_root=VAULT_ROOT):
    findings = {"drifted": [], "moved": [], "untracked": [], "malformed": []}
    checked = 0
    clean = 0
    for rel, title, fm, anchors in iter_code_pages(vault_root):
        page_clean = True
        for anchor in anchors:
            path, stored = split_anchor(anchor)
            if stored is None or not path:
                findings["malformed"].append({"page": rel, "title": title, "anchor": anchor})
                page_clean = False
                continue
            checked += 1
            on_disk = os.path.exists(os.path.join(repo, path.rstrip("/")))
            current = object_sha(repo, path)
            if current is None:
                if on_disk:
                    findings["untracked"].append({"page": rel, "title": title, "path": path})
                else:
                    findings["moved"].append({"page": rel, "title": title, "path": path})
                page_clean = False
            elif current != stored:
                findings["drifted"].append({"page": rel, "title": title, "path": path,
                                            "was": stored, "now": current})
                page_clean = False
            else:
                clean += 1
        # (page_clean is informational; per-anchor counts above drive the report)
    return findings, checked, clean


def short(sha):
    return sha[:7] if isinstance(sha, str) and len(sha) >= 7 else (sha or "?")


def render_report(repo, head, findings, checked, clean):
    pages = sorted({f["page"] for lst in findings.values() for f in lst})
    drift_pages = len(pages)
    lines = []
    lines.append("## Code Drift")
    lines.append(f"- Repo: `{repo}` @ {short(head)}")
    lines.append(f"- Anchors checked: {checked} ({clean} clean) across "
                 f"{drift_pages} page(s) with drift/issues")
    if findings["drifted"]:
        lines.append("")
        lines.append("### Drifted (source changed since ingest)")
        for f in findings["drifted"]:
            lines.append(f"- [[{f['title']}]] (`{f['page']}`): `{f['path']}` "
                         f"{short(f['was'])} → {short(f['now'])}. Re-ingest to refresh.")
    if findings["moved"]:
        lines.append("")
        lines.append("### Moved or deleted (source path no longer in HEAD)")
        for f in findings["moved"]:
            lines.append(f"- [[{f['title']}]] (`{f['page']}`): `{f['path']}` not found at HEAD. "
                         f"Update source_paths or archive the page.")
    if findings["untracked"]:
        lines.append("")
        lines.append("### Untracked (exists on disk but outside the git tree)")
        for f in findings["untracked"]:
            lines.append(f"- [[{f['title']}]] (`{f['page']}`): `{f['path']}` is not tracked; cannot anchor.")
    if findings["malformed"]:
        lines.append("")
        lines.append("### Malformed anchors (expected `path@sha`)")
        for f in findings["malformed"]:
            lines.append(f"- [[{f['title']}]] (`{f['page']}`): `{f['anchor']}`")
    if not any(findings.values()):
        lines.append("")
        lines.append("_No code drift detected._")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Code-drift lint for Mode B wiki pages (read-only).")
    ap.add_argument("--repo", default=os.environ.get("CODE_REPO_ROOT") or str(VAULT_ROOT),
                    help="repo to hash anchors against (default: $CODE_REPO_ROOT or vault root)")
    ap.add_argument("--vault", default=str(VAULT_ROOT),
                    help="vault root containing wiki/ (default: this script's vault)")
    ap.add_argument("--report", default=None, help="append a '## Code Drift' section to this file")
    ap.add_argument("--peek", action="store_true", help="diagnostics only; no git object reads")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    vault_root = Path(args.vault)
    if not (vault_root / "wiki").is_dir():
        log(f"ERR: wiki dir not found: {vault_root / 'wiki'}")
        return EXIT_WIKI_UNREADABLE

    anchored_pages = list(iter_code_pages(vault_root))

    if args.peek:
        diag = {
            "git": git_available(),
            "repo": args.repo,
            "is_git_repo": is_git_repo(args.repo) if git_available() else False,
            "anchored_pages": len(anchored_pages),
        }
        print(json.dumps(diag))
        return EXIT_OK

    if not git_available():
        log("code-drift skipped: git binary not found (exit 10)")
        return EXIT_NO_GIT
    if not is_git_repo(args.repo):
        log(f"code-drift skipped: --repo not a git work tree: {args.repo} (exit 11)")
        return EXIT_NOT_A_REPO

    head = head_sha(args.repo)
    findings, checked, clean = scan(args.repo, vault_root)

    if args.json:
        print(json.dumps({"repo": args.repo, "head": head, "checked": checked,
                          "clean": clean, "findings": findings}, indent=2))
    else:
        total = sum(len(v) for v in findings.values())
        print(f"code-drift: {checked} anchor(s) checked, {clean} clean, {total} issue(s) "
              f"(drifted={len(findings['drifted'])}, moved={len(findings['moved'])}, "
              f"untracked={len(findings['untracked'])}, malformed={len(findings['malformed'])})")

    if args.report:
        section = render_report(args.repo, head, findings, checked, clean)
        rp = Path(args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with rp.open("a", encoding="utf-8") as fh:
            fh.write(f"\n<!-- code-anchor-check {stamp} -->\n")
            fh.write(section)

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
