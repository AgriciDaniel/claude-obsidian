#!/usr/bin/env python3
"""code-coverage-check.py — coverage & ingest-staleness lint for Mode B wiki pages.

Two checks the drift lint (`code-anchor-check.py`) does NOT cover:

  1. Coverage gaps — code that exists in the repo but has no wiki page. Rather than
     flagging every leaf directory (noise), this infers the *levels* the wiki already
     documents (the parent containers of existing `source_paths`, e.g. `app/domain/`,
     `app/workers/`) and reports sibling packages at those levels that no page maps.
     This is the "`app/domain/cluster_content/` has no page" class of gap.

  2. Ingest staleness — how far the wiki has fallen behind the repo. Reports, per
     distinct `ingest_commit`, how many commits / days behind HEAD it is, and flags
     pages whose `ingest_commit` is missing or no longer in HEAD's history (a rebase /
     force-push / wrong-repo orphan that `--sync` must repair).

Read-only; never modifies wiki pages or the repo. The fix for both is
`/wiki-code-ingest` (whole-repo / single-path) or `/wiki-code-ingest --sync`.

Feature-gated exactly like code-anchor-check.py so `/wiki-code-lint` can no-op
gracefully: exits 10 if `git` is missing, 11 if --repo is not a git work tree.
Findings themselves keep exit 0 (a finding is not a script error).

Usage:
  code-coverage-check.py                 # scan; human summary to stdout
  code-coverage-check.py --peek          # diagnostics only (git? repo? N code pages)
  code-coverage-check.py --repo PATH     # repo to compare against (default: $CODE_REPO_ROOT or vault root)
  code-coverage-check.py --report PATH   # append a "## Coverage & Staleness" section to PATH
  code-coverage-check.py --json          # machine-readable findings

Exit codes:
  0  — success (gaps/staleness may be reported in the body; that is a finding, not an error)
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

# Shared exclusions (mirror code-anchor-check.py / tiling-check.py).
EXCLUDE_TYPES = {"meta", "fold"}
EXCLUDE_FILENAMES = {
    "_index.md", "index.md", "log.md", "hot.md", "overview.md",
    "dashboard.md", "Wiki Map.md", "getting-started.md",
}
EXCLUDE_PATH_PREFIXES = ("wiki/folds/", "wiki/meta/")

# Directory names that are never "undocumented modules" — test/build/vendor noise.
EXCLUDE_DIR_NAMES = {
    "tests", "test", "__tests__", "__pycache__", "migrations", "node_modules",
    "vendor", "fixtures", "__mocks__", "dist", "build", "coverage", "docs",
}

CODE_PAGE_TYPES = {"module", "component", "dependency", "flow", "decision"}

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
    """Extract scalars and block lists from flat frontmatter (same reader as
    code-anchor-check.py). Inline `[a, b]` stays a scalar string; normalise_list
    below splits it when a list is expected."""
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


def normalise_list(value):
    """Return a list of strings from a block list, an inline `[a, b]` scalar, or a
    bare scalar."""
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str) and v]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            return [p.strip().strip('"').strip("'") for p in inner.split(",") if p.strip()]
        return [s] if s else []
    return []


def is_code_page(fm):
    if fm.get("source_type") == "code":
        return True
    if fm.get("type") in CODE_PAGE_TYPES:
        return True
    return bool(fm.get("source_paths")) or bool(fm.get("code_anchors"))


def iter_code_pages(vault_root=VAULT_ROOT):
    """Yield (rel_path, title, fm) for every Mode B code page."""
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
        if not is_code_page(fm):
            continue
        title = fm.get("title") or p.stem
        yield rel, title, fm


# ── git helpers (identical contract to code-anchor-check.py) ─────────────────
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


def child_dirs(repo, container):
    """Immediate child directories of `container` tracked at HEAD (repo-relative)."""
    arg = container.rstrip("/") + "/"
    r = subprocess.run(["git", "-C", repo, "ls-tree", "-d", "--name-only", "HEAD", arg],
                       capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def dir_has_tracked_files(repo, d):
    r = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", "HEAD", d.rstrip("/") + "/"],
                       capture_output=True, text=True, timeout=15)
    return r.returncode == 0 and bool(r.stdout.strip())


def is_ancestor(repo, commit, head):
    if not commit:
        return False
    r = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", commit, head],
                       capture_output=True, text=True, timeout=10)
    return r.returncode == 0


def commits_behind(repo, commit, head):
    r = subprocess.run(["git", "-C", repo, "rev-list", "--count", f"{commit}..{head}"],
                       capture_output=True, text=True, timeout=10)
    return int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else None


def commit_date(repo, commit):
    r = subprocess.run(["git", "-C", repo, "show", "-s", "--format=%cI", commit],
                       capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if r.returncode == 0 else None


# ── source-path normalisation ────────────────────────────────────────────────
def page_source_dirs(repo, fm):
    """Directory paths a page covers. A dir source_path → itself; a file → its parent."""
    dirs = set()
    for sp in normalise_list(fm.get("source_paths")):
        sp = sp.strip().strip("/")
        if not sp:
            continue
        full = os.path.join(repo, sp)
        if os.path.isdir(full) or sp.endswith("/"):
            dirs.add(sp)
        elif os.path.isfile(full):
            d = os.path.dirname(sp)
            if d:
                dirs.add(d)
        else:
            # path no longer on disk; treat as a dir if it has no extension
            (dirs.add(sp) if "." not in os.path.basename(sp) else dirs.add(os.path.dirname(sp) or sp))
    return {d for d in dirs if d}


def has_dedicated_page(child, covered):
    """True if some page is dedicated to `child` — a source dir equal to it, or strictly
    inside it. A page that only documents an *ancestor* (e.g. the whole `app/domain/`)
    does NOT count, otherwise one broad overview page would suppress every child gap."""
    for c in covered:
        if c == child or c.startswith(child + "/"):
            return True
    return False


# ── core scans ───────────────────────────────────────────────────────────────
def scan_coverage(repo, vault_root):
    covered = set()
    for _, _, fm in iter_code_pages(vault_root):
        covered |= page_source_dirs(repo, fm)
    # containers = the parent levels the wiki documents at
    containers = sorted({os.path.dirname(d) for d in covered if os.path.dirname(d)})
    gaps = []
    seen = set()
    for container in containers:
        for child in child_dirs(repo, container):
            if child in seen:
                continue
            seen.add(child)
            name = os.path.basename(child)
            if name in EXCLUDE_DIR_NAMES or name.startswith(".") or name.startswith("__"):
                continue
            if has_dedicated_page(child, covered):
                continue
            if not dir_has_tracked_files(repo, child):
                continue
            gaps.append({"path": child, "container": container})
    return gaps, sorted(covered), containers


def scan_staleness(repo, vault_root, head):
    by_commit = {}            # ingest_commit -> [pages]
    missing = []              # pages with no ingest_commit
    for rel, title, fm in iter_code_pages(vault_root):
        ic = (fm.get("ingest_commit") or "").strip()
        if not ic:
            missing.append({"page": rel, "title": title})
        else:
            by_commit.setdefault(ic, []).append({"page": rel, "title": title})
    summary = []
    orphaned = []
    for ic, pages in sorted(by_commit.items(), key=lambda kv: -len(kv[1])):
        anc = is_ancestor(repo, ic, head)
        if not anc:
            orphaned.append({"commit": ic, "pages": len(pages)})
            summary.append({"commit": ic, "pages": len(pages), "ancestor": False,
                            "behind": None, "date": commit_date(repo, ic)})
        else:
            summary.append({"commit": ic, "pages": len(pages), "ancestor": True,
                            "behind": commits_behind(repo, ic, head),
                            "date": commit_date(repo, ic)})
    return {"summary": summary, "missing": missing, "orphaned": orphaned}


def short(sha):
    return sha[:7] if isinstance(sha, str) and len(sha) >= 7 else (sha or "?")


def days_since(iso):
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso)
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        return (now - dt).days
    except ValueError:
        return None


def render_report(repo, head, gaps, containers, stale):
    lines = ["## Coverage & Staleness", f"- Repo: `{repo}` @ {short(head)}"]

    lines.append("")
    lines.append("### Coverage gaps (code with no wiki page)")
    if gaps:
        lines.append(f"- {len(gaps)} package(s) at documented levels "
                     f"({', '.join('`'+c+'/`' for c in containers) or 'n/a'}) have no page:")
        for g in gaps:
            lines.append(f"  - `{g['path']}/` — peer of documented modules under "
                         f"`{g['container']}/`, but no page maps it. "
                         f"Run `/wiki-code-ingest <repo> {g['path']}`.")
    else:
        lines.append("- _No coverage gaps at the documented module levels._")

    lines.append("")
    lines.append("### Ingest staleness (wiki behind repo HEAD)")
    if not stale["summary"] and not stale["missing"]:
        lines.append("- _No code pages with ingest metadata._")
    for s in stale["summary"]:
        if not s["ancestor"]:
            lines.append(f"- ⚠ `{short(s['commit'])}` ({s['pages']} page(s)) is **not in HEAD's history** "
                         f"(rebased / force-pushed / wrong repo). Re-ingest: `/wiki-code-ingest --sync`.")
        else:
            d = days_since(s["date"])
            behind = s["behind"]
            tail = []
            if behind is not None:
                tail.append(f"{behind} commit(s) behind HEAD")
            if d is not None:
                tail.append(f"{d} day(s) old")
            suffix = (" — " + ", ".join(tail)) if tail else ""
            verb = "current" if behind == 0 else "stale"
            lines.append(f"- `{short(s['commit'])}` ({s['pages']} page(s)) — {verb}{suffix}."
                         + ("" if behind == 0 else " Refresh with `/wiki-code-ingest --sync`."))
    if stale["missing"]:
        lines.append(f"- {len(stale['missing'])} code page(s) **missing `ingest_commit`** "
                     f"(drift cannot be tracked):")
        for m in stale["missing"]:
            lines.append(f"  - [[{m['title']}]] (`{m['page']}`)")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Coverage & ingest-staleness lint for Mode B wiki pages (read-only).")
    ap.add_argument("--repo", default=os.environ.get("CODE_REPO_ROOT") or str(VAULT_ROOT),
                    help="repo to compare against (default: $CODE_REPO_ROOT or vault root)")
    ap.add_argument("--vault", default=str(VAULT_ROOT),
                    help="vault root containing wiki/ (default: this script's vault)")
    ap.add_argument("--report", default=None, help="append a '## Coverage & Staleness' section to this file")
    ap.add_argument("--peek", action="store_true", help="diagnostics only; no git reads")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    vault_root = Path(args.vault)
    if not (vault_root / "wiki").is_dir():
        log(f"ERR: wiki dir not found: {vault_root / 'wiki'}")
        return EXIT_WIKI_UNREADABLE

    code_pages = list(iter_code_pages(vault_root))

    if args.peek:
        print(json.dumps({
            "git": git_available(),
            "repo": args.repo,
            "is_git_repo": is_git_repo(args.repo) if git_available() else False,
            "code_pages": len(code_pages),
        }))
        return EXIT_OK

    if not git_available():
        log("coverage-check skipped: git binary not found (exit 10)")
        return EXIT_NO_GIT
    if not is_git_repo(args.repo):
        log(f"coverage-check skipped: --repo not a git work tree: {args.repo} (exit 11)")
        return EXIT_NOT_A_REPO

    head = head_sha(args.repo)
    gaps, covered, containers = scan_coverage(args.repo, vault_root)
    stale = scan_staleness(args.repo, vault_root, head)

    if args.json:
        print(json.dumps({"repo": args.repo, "head": head, "coverage_gaps": gaps,
                          "covered_dirs": covered, "containers": containers,
                          "staleness": stale}, indent=2))
    else:
        print(f"coverage: {len(gaps)} gap(s) at documented levels; "
              f"staleness: {len(stale['summary'])} ingest_commit(s), "
              f"{len(stale['orphaned'])} orphaned, {len(stale['missing'])} page(s) missing ingest_commit")

    if args.report:
        rp = Path(args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with rp.open("a", encoding="utf-8") as fh:
            fh.write(f"\n<!-- code-coverage-check {stamp} -->\n")
            fh.write(render_report(args.repo, head, gaps, containers, stale))

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
