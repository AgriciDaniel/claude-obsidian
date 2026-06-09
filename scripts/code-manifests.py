#!/usr/bin/env python3
"""code-manifests.py — detect & parse dependency manifests, language-agnostically.

Part of the v1.10 Mode B code-ingest pipeline. Finds whichever dependency
manifests a repo actually has and extracts a normalized dependency list so
`/wiki-code-ingest` can synthesize `wiki/dependencies/` pages deterministically.

GITIGNORE GUARANTEE: candidate manifests are drawn ONLY from the gitignore-aware
file set (same enumeration as code-scan.py), so a vendored `node_modules/*/
package.json` or any ignored manifest is never parsed.

Usage:
  code-manifests.py <repo> [--subpath PATH] [--out DIR]

Output (JSON, atomic write):
  <out>/deps.json  { generated_at,
                     manifests_found: [{path, ecosystem, parsed}],
                     dependencies:    [{name, version, scope, ecosystem, source_manifest}],
                     ecosystems:      [..] }

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

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover - older interpreters
    tomllib = None

VAULT_ROOT = Path(__file__).resolve().parent.parent

FALLBACK_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".next",
    ".nuxt", "target", ".gradle", ".idea", ".vscode", "vendor", ".cache",
}


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


def _read(repo, rel):
    with open(os.path.join(repo, rel), "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _toml(repo, rel):
    if tomllib is None:
        return None
    try:
        with open(os.path.join(repo, rel), "rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return None


def _dep(name, version, scope, ecosystem, source):
    return {"name": name, "version": version or "", "scope": scope,
            "ecosystem": ecosystem, "source_manifest": source}


# ── per-ecosystem parsers (best-effort) ──────────────────────────────────────
def parse_package_json(repo, rel):
    try:
        data = json.loads(_read(repo, rel))
    except (OSError, json.JSONDecodeError):
        return None
    deps = []
    for key, scope in (("dependencies", "runtime"), ("devDependencies", "dev"),
                       ("peerDependencies", "peer"), ("optionalDependencies", "optional")):
        for name, ver in (data.get(key) or {}).items():
            deps.append(_dep(name, ver, scope, "npm", rel))
    return deps


def parse_pyproject(repo, rel):
    data = _toml(repo, rel)
    if data is None:
        return None
    deps = []
    for spec in (data.get("project", {}).get("dependencies") or []):
        name, ver = split_pep508(spec)
        deps.append(_dep(name, ver, "runtime", "pypi", rel))
    optional = data.get("project", {}).get("optional-dependencies") or {}
    for group, specs in optional.items():
        for spec in specs:
            name, ver = split_pep508(spec)
            deps.append(_dep(name, ver, "optional:" + group, "pypi", rel))
    poetry = data.get("tool", {}).get("poetry", {})
    for name, ver in (poetry.get("dependencies") or {}).items():
        if name.lower() == "python":
            continue
        deps.append(_dep(name, ver if isinstance(ver, str) else
                         (ver.get("version", "") if isinstance(ver, dict) else ""),
                         "runtime", "pypi", rel))
    return deps


def parse_requirements(repo, rel):
    try:
        text = _read(repo, rel)
    except OSError:
        return None
    deps = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):  # skip flags like -r, -e
            continue
        name, ver = split_pep508(line)
        if name:
            deps.append(_dep(name, ver, "runtime", "pypi", rel))
    return deps


def parse_go_mod(repo, rel):
    try:
        text = _read(repo, rel)
    except OSError:
        return None
    deps = []
    block = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("require ("):
            block = True
            continue
        if block and s == ")":
            block = False
            continue
        m = re.match(r"^(?:require\s+)?([^\s]+/[^\s]+)\s+(v[^\s/]+)", s)
        if m and (block or s.startswith("require ")):
            deps.append(_dep(m.group(1), m.group(2), "runtime", "go", rel))
    return deps


def parse_cargo(repo, rel):
    data = _toml(repo, rel)
    if data is None:
        return None
    deps = []
    for key, scope in (("dependencies", "runtime"), ("dev-dependencies", "dev"),
                       ("build-dependencies", "build")):
        for name, ver in (data.get(key) or {}).items():
            v = ver if isinstance(ver, str) else (ver.get("version", "") if isinstance(ver, dict) else "")
            deps.append(_dep(name, v, scope, "cargo", rel))
    return deps


def parse_gemfile(repo, rel):
    try:
        text = _read(repo, rel)
    except OSError:
        return None
    deps = []
    for m in re.finditer(r"""^\s*gem\s+['"]([^'"]+)['"](?:\s*,\s*['"]([^'"]+)['"])?""",
                         text, re.MULTILINE):
        deps.append(_dep(m.group(1), m.group(2) or "", "runtime", "rubygems", rel))
    return deps


def parse_composer(repo, rel):
    try:
        data = json.loads(_read(repo, rel))
    except (OSError, json.JSONDecodeError):
        return None
    deps = []
    for key, scope in (("require", "runtime"), ("require-dev", "dev")):
        for name, ver in (data.get(key) or {}).items():
            if name.lower() == "php":
                continue
            deps.append(_dep(name, ver, scope, "composer", rel))
    return deps


def split_pep508(spec):
    """('requests', '>=2,<3') from 'requests[security]>=2,<3; python_version>"3"'."""
    spec = spec.split(";", 1)[0].strip()
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*(.*)$", spec)
    if not m:
        return "", ""
    return m.group(1), m.group(2).strip()


# basename → (ecosystem, parser). Lockfiles intentionally excluded (transitive noise).
PARSERS = {
    "package.json": ("npm", parse_package_json),
    "pyproject.toml": ("pypi", parse_pyproject),
    "go.mod": ("go", parse_go_mod),
    "Cargo.toml": ("cargo", parse_cargo),
    "Gemfile": ("rubygems", parse_gemfile),
    "composer.json": ("composer", parse_composer),
}
# Manifests we recognize but only parse via the requirements rule / record-only.
REQUIREMENTS_RE = re.compile(r"^requirements.*\.txt$")
RECORD_ONLY = {"pom.xml": "maven", "build.gradle": "gradle",
               "build.gradle.kts": "gradle", "Pipfile": "pypi", "setup.py": "pypi"}


def collect(repo, subpath):
    files = list_repo_files(repo, subpath)
    manifests_found = []
    dependencies = []
    for rel in files:
        base = os.path.basename(rel)
        ecosystem = None
        deps = None
        if base in PARSERS:
            ecosystem, parser = PARSERS[base]
            deps = parser(repo, rel)
        elif REQUIREMENTS_RE.match(base):
            ecosystem, deps = "pypi", parse_requirements(repo, rel)
        elif base in RECORD_ONLY:
            ecosystem = RECORD_ONLY[base]
            deps = None  # recognized but not parsed
        else:
            continue
        parsed = deps is not None
        manifests_found.append({"path": rel, "ecosystem": ecosystem, "parsed": parsed})
        if parsed:
            dependencies.extend(deps)
    ecosystems = sorted({m["ecosystem"] for m in manifests_found})
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manifests_found": manifests_found,
        "dependencies": dependencies,
        "ecosystems": ecosystems,
    }


def main():
    ap = argparse.ArgumentParser(description="Detect & parse dependency manifests (gitignore-aware).")
    ap.add_argument("repo", help="repository root path")
    ap.add_argument("--subpath", default=None)
    ap.add_argument("--out", default=None, help="output dir (default: .raw/code/<slug>/)")
    args = ap.parse_args()

    if not os.path.isdir(args.repo):
        die(3, f"repo path is not a directory: {args.repo}")

    out_dir = Path(args.out) if args.out else (VAULT_ROOT / ".raw" / "code" / repo_slug(args.repo))
    result = collect(args.repo, args.subpath)
    write_json(out_dir, "deps.json", result)
    print(f"code-manifests: {len(result['manifests_found'])} manifest(s), "
          f"{len(result['dependencies'])} dep(s), ecosystems={result['ecosystems']} → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
