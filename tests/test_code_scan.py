#!/usr/bin/env python3
"""test_code_scan.py — hermetic tests for scripts/code-scan.py.

Builds a throwaway git repo (with a gitignored file and an ignored dir) and
asserts the scan honors .gitignore, classifies languages, and writes valid JSON.
No network, no LLM. Pure stdlib + subprocess + a local `git`.

Usage:
  python3 tests/test_code_scan.py
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "code-scan.py"

spec = importlib.util.spec_from_file_location("code_scan", HELPER)
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)


class Fail(SystemExit):
    pass


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30)


def make_repo(tmp):
    repo = Path(tmp) / "repo"
    (repo / "app").mkdir(parents=True)
    (repo / "app" / "main.py").write_text("import os\nprint(os.getpid())\n", encoding="utf-8")
    (repo / "app" / "util.ts").write_text("export const x: number = 1\n", encoding="utf-8")
    (repo / "README.md").write_text("# hi\n", encoding="utf-8")
    (repo / ".gitignore").write_text("secret.env\nignored/\n", encoding="utf-8")
    (repo / "secret.env").write_text("SECRET=do-not-index\n", encoding="utf-8")
    (repo / "ignored").mkdir()
    (repo / "ignored" / "foo.py").write_text("x = 1\n", encoding="utf-8")
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "t@example.com"], repo)
    run(["git", "config", "user.name", "Test"], repo)
    run(["git", "add", "app", "README.md", ".gitignore"], repo)
    run(["git", "commit", "-q", "-m", "init"], repo)
    return repo


def test_gitignore_excluded():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        files = cs.list_repo_files(str(repo))
        assert_true("tracked python file indexed", "app/main.py" in files, hint=str(files))
        assert_true("tracked ts file indexed", "app/util.ts" in files, hint=str(files))
        assert_true("gitignored secret.env EXCLUDED", "secret.env" not in files, hint=str(files))
        assert_true("gitignored dir contents EXCLUDED", "ignored/foo.py" not in files, hint=str(files))


def test_snapshot_languages_and_loc():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        tree, langs = cs.build_snapshot(str(repo), None)
        by = {f["path"]: f for f in tree["files"]}
        assert_true("main.py language=python", by["app/main.py"]["language"] == "python")
        assert_true("main.py loc>0", by["app/main.py"]["loc"] > 0, hint=str(by["app/main.py"]))
        assert_true("util.ts language=typescript", by["app/util.ts"]["language"] == "typescript")
        assert_true("languages has python", "python" in langs["by_language"])
        assert_true("total_files excludes ignored", langs["total_files"] == len(tree["files"]))
        assert_true("primary language set", langs["primary"] in ("python", "typescript", "markdown"))


def test_subpath_scopes():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        files = cs.list_repo_files(str(repo), "app")
        assert_true("subpath app only", all(p.startswith("app/") for p in files), hint=str(files))
        assert_true("README excluded by subpath", "README.md" not in files)


def test_non_git_fallback_skips_vendor_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        plain = Path(tmp) / "plain"
        (plain / "src").mkdir(parents=True)
        (plain / "src" / "a.py").write_text("x=1\n", encoding="utf-8")
        (plain / "node_modules" / "pkg").mkdir(parents=True)
        (plain / "node_modules" / "pkg" / "index.js").write_text("module.exports={}\n", encoding="utf-8")
        files = cs.list_repo_files(str(plain))
        assert_true("non-git src indexed", "src/a.py" in files, hint=str(files))
        assert_true("non-git node_modules skipped",
                    not any("node_modules" in p for p in files), hint=str(files))


def test_cli_writes_json():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        out = Path(tmp) / "out"
        r = subprocess.run([sys.executable, str(HELPER), str(repo), "--out", str(out)],
                           capture_output=True, text=True, timeout=30)
        assert_true("cli rc=0", r.returncode == 0, hint=r.stderr)
        tree = json.loads((out / "tree.json").read_text())
        langs = json.loads((out / "languages.json").read_text())
        assert_true("tree.json has files", len(tree["files"]) >= 3)
        assert_true("languages.json has primary", langs["primary"] is not None)


def main():
    print("=== test_code_scan.py ===")
    test_gitignore_excluded()
    test_snapshot_languages_and_loc()
    test_subpath_scopes()
    test_non_git_fallback_skips_vendor_dirs()
    test_cli_writes_json()
    print("\nAll code-scan tests passed.")


if __name__ == "__main__":
    main()
