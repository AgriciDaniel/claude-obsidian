#!/usr/bin/env python3
"""code-scan.py — deterministic structural snapshot of a code repository.

Part of the v1.10 Mode B code-ingest pipeline. Walks a repo (or sub-path),
honoring .gitignore, and emits a language/LOC/tree snapshot into the vault's
`.raw/code/<slug>/` so `/wiki-code-ingest` can synthesize module pages from
deterministic signals instead of guessing.

GITIGNORE GUARANTEE (load-bearing): files ignored by git are NEVER indexed.
Enumeration uses `git ls-files --cached --others --exclude-standard` (tracked +
untracked-but-not-ignored, honoring .gitignore, .git/info/exclude, and the
user's global excludes). For a non-git directory it falls back to os.walk with a
small default-ignore set. The SAME filtered file list is the contract the other
two signal scripts (code-manifests.py, code-signals.py) operate on.

Usage:
  code-scan.py <repo> [--subpath PATH] [--out DIR]

  <repo>        path to the repository root
  --subpath     restrict the scan to this repo-relative sub-path (e.g. app/api)
  --out         output directory (default: .raw/code/<repo-slug>/ under the vault)

Outputs (JSON, atomic write):
  <out>/tree.json       { root, subpath, generated_at, file_count, total_loc,
                          files: [{path, language, loc, binary}],
                          dirs:  [{path, file_count, loc, languages: {lang: n}}] }
  <out>/languages.json  { by_language: {lang: {files, loc}}, total_loc,
                          total_files, primary }

Exit codes:
  0 — success
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

# Extension → language. Language-agnostic by construction: add a row to support
# a new language; no skill or pipeline change is required.
EXT_LANG = {
    ".py": "python", ".pyi": "python",
    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".java": "java", ".kt": "kotlin",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp", ".hpp": "cpp",
    ".cs": "csharp", ".php": "php", ".swift": "swift", ".scala": "scala", ".clj": "clojure",
    ".ex": "elixir", ".exs": "elixir", ".erl": "erlang", ".hs": "haskell", ".ml": "ocaml",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell", ".fish": "shell",
    ".sql": "sql", ".proto": "protobuf", ".graphql": "graphql", ".gql": "graphql",
    ".css": "css", ".scss": "scss", ".sass": "sass", ".less": "less",
    ".html": "html", ".htm": "html", ".vue": "vue", ".svelte": "svelte", ".astro": "astro",
    ".md": "markdown", ".mdx": "markdown", ".rst": "rst",
    ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".json": "json", ".xml": "xml",
    ".tf": "terraform", ".dockerfile": "dockerfile", ".lua": "lua", ".r": "r", ".dart": "dart",
}

# os.walk fallback only (non-git dirs): directories we never descend into.
FALLBACK_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".next",
    ".nuxt", "target", ".gradle", ".idea", ".vscode", "vendor", ".cache",
}


def die(code, msg):
    print(f"ERR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def language_for(path):
    name = os.path.basename(path).lower()
    if name in ("dockerfile", "makefile", "rakefile", "gemfile"):
        return {"dockerfile": "dockerfile", "makefile": "make",
                "rakefile": "ruby", "gemfile": "ruby"}[name]
    return EXT_LANG.get(os.path.splitext(path)[1].lower(), "other")


def is_git_repo(repo):
    try:
        r = subprocess.run(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True, timeout=10)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_repo_files(repo, subpath=None):
    """Return repo-relative file paths, NEVER including gitignored files.

    Primary path: `git ls-files --cached --others --exclude-standard -z` — lists
    tracked files plus untracked files that are not ignored, honoring all of
    .gitignore / .git/info/exclude / core.excludesFile. Fallback (non-git dir):
    os.walk skipping FALLBACK_IGNORE_DIRS.
    """
    if is_git_repo(repo):
        cmd = ["git", "-C", repo, "ls-files", "--cached", "--others",
               "--exclude-standard", "-z"]
        if subpath:
            cmd += ["--", subpath]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            die(3, f"git ls-files failed: {r.stderr.strip()}")
        files = [p for p in r.stdout.split("\0") if p]
        return sorted(set(files))
    # Fallback: not a git repo.
    base = os.path.join(repo, subpath) if subpath else repo
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in FALLBACK_IGNORE_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            out.append(os.path.relpath(full, repo))
    return sorted(out)


def file_stats(repo, rel):
    """(loc, binary) for one file. LOC = newline count; binary files report 0."""
    full = os.path.join(repo, rel)
    try:
        with open(full, "rb") as fh:
            data = fh.read(2_000_000)  # cap: large files contribute a capped LOC
        if b"\x00" in data[:8192]:
            return 0, True
        return data.count(b"\n"), False
    except OSError:
        return 0, False


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
    base = os.path.basename(os.path.abspath(repo)) or "repo"
    s = re.sub(r"[^\w.-]+", "-", base).strip("-")
    return s or "repo"


def build_snapshot(repo, subpath):
    files = list_repo_files(repo, subpath)
    file_rows = []
    dir_agg = {}  # dirpath -> {file_count, loc, languages}
    by_language = {}
    total_loc = 0
    for rel in files:
        lang = language_for(rel)
        loc, binary = file_stats(repo, rel)
        total_loc += loc
        file_rows.append({"path": rel, "language": lang, "loc": loc, "binary": binary})
        by_language.setdefault(lang, {"files": 0, "loc": 0})
        by_language[lang]["files"] += 1
        by_language[lang]["loc"] += loc
        d = os.path.dirname(rel) or "."
        agg = dir_agg.setdefault(d, {"file_count": 0, "loc": 0, "languages": {}})
        agg["file_count"] += 1
        agg["loc"] += loc
        agg["languages"][lang] = agg["languages"].get(lang, 0) + 1

    # Primary language = most lines of code, ties broken by file count. The
    # catch-all "other" bucket (configs, .gitignore, unknown extensions) is
    # excluded so it can never win — primary should name a real language.
    ranked = {k: v for k, v in by_language.items() if k != "other"}
    primary = None
    if ranked:
        primary = max(ranked.items(), key=lambda kv: (kv[1]["loc"], kv[1]["files"]))[0]

    dirs = [{"path": p, **v} for p, v in sorted(dir_agg.items())]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tree = {
        "root": os.path.abspath(repo),
        "subpath": subpath or "",
        "generated_at": generated_at,
        "file_count": len(file_rows),
        "total_loc": total_loc,
        "files": file_rows,
        "dirs": dirs,
    }
    languages = {
        "by_language": by_language,
        "total_loc": total_loc,
        "total_files": len(file_rows),
        "primary": primary,
    }
    return tree, languages


def main():
    ap = argparse.ArgumentParser(description="Structural snapshot of a code repo (gitignore-aware).")
    ap.add_argument("repo", help="repository root path")
    ap.add_argument("--subpath", default=None, help="restrict to this repo-relative sub-path")
    ap.add_argument("--out", default=None, help="output dir (default: .raw/code/<slug>/)")
    args = ap.parse_args()

    repo = args.repo
    if not os.path.isdir(repo):
        die(3, f"repo path is not a directory: {repo}")

    out_dir = Path(args.out) if args.out else (VAULT_ROOT / ".raw" / "code" / repo_slug(repo))

    tree, languages = build_snapshot(repo, args.subpath)
    write_json(out_dir, "tree.json", tree)
    write_json(out_dir, "languages.json", languages)
    print(f"code-scan: {tree['file_count']} files, {tree['total_loc']} LOC, "
          f"primary={languages['primary']} → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
