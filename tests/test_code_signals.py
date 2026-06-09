#!/usr/bin/env python3
"""test_code_signals.py — hermetic tests for scripts/code-signals.py.

Builds a throwaway git repo and asserts: HEAD anchors are real object SHAs,
gitignored files never appear, intra-repo python imports resolve to edges, and
the non-git path degrades gracefully.

Usage:
  python3 tests/test_code_signals.py
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "code-signals.py"

spec = importlib.util.spec_from_file_location("code_signals", HELPER)
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)


class Fail(SystemExit):
    pass


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30)


def is_hex40(s):
    return isinstance(s, str) and len(s) == 40 and all(c in "0123456789abcdef" for c in s)


def make_repo(tmp):
    repo = Path(tmp) / "repo"
    (repo / "app").mkdir(parents=True)
    (repo / "app" / "main.py").write_text("import os\nprint(os.getpid())\n", encoding="utf-8")
    (repo / "app" / "service.py").write_text(
        "from app.main import os\nfrom . import main\n", encoding="utf-8")
    (repo / ".gitignore").write_text("secret.env\n", encoding="utf-8")
    (repo / "secret.env").write_text("SECRET=1\n", encoding="utf-8")
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "t@example.com"], repo)
    run(["git", "config", "user.name", "Test"], repo)
    run(["git", "add", "app", ".gitignore"], repo)
    run(["git", "commit", "-q", "-m", "init"], repo)
    return repo


def test_anchors_and_churn():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        files = cg.list_repo_files(str(repo))
        sig = cg.git_signals(str(repo), None, "90 days ago", set(files))
        assert_true("git_available", sig["git_available"] is True)
        assert_true("head is 40-hex", is_hex40(sig["head"]), hint=str(sig["head"]))
        assert_true("file anchor present", "app/main.py" in sig["anchors"], hint=str(sig["anchors"].keys()))
        assert_true("dir anchor present (tree sha)", "app" in sig["anchors"])
        assert_true("file anchor is blob sha (40-hex)", is_hex40(sig["anchors"]["app/main.py"]))
        assert_true("gitignored file has NO anchor", "secret.env" not in sig["anchors"])
        churn_paths = {c["path"] for c in sig["churn_top"]}
        assert_true("churn includes committed file", "app/main.py" in churn_paths, hint=str(churn_paths))
        assert_true("recent_commits non-empty", len(sig["recent_commits"]) >= 1)


def test_import_edges_resolve_intra_repo():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        files = cg.list_repo_files(str(repo))
        edges = cg.import_edges(str(repo), files)["edges"]
        # service.py does `from app.main import os` → resolves to app/main.py, internal
        resolved = [e for e in edges if e["from"] == "app/service.py"
                    and e["to"] == "app/main.py" and not e["external"]]
        assert_true("intra-repo python import resolved", len(resolved) >= 1, hint=str(edges))
        # main.py imports stdlib os → unresolved, external
        ext = [e for e in edges if e["from"] == "app/main.py" and e["to"] == "os" and e["external"]]
        assert_true("stdlib import marked external", len(ext) >= 1, hint=str(edges))


def test_non_git_degrades():
    with tempfile.TemporaryDirectory() as tmp:
        plain = Path(tmp) / "plain"
        (plain / "a.py").parent.mkdir(parents=True, exist_ok=True)
        (plain / "a.py").write_text("import os\n", encoding="utf-8")
        files = cg.list_repo_files(str(plain))
        sig = cg.git_signals(str(plain), None, "90 days ago", set(files))
        assert_true("non-git: git_available False", sig["git_available"] is False)
        assert_true("non-git: head None", sig["head"] is None)
        assert_true("non-git: anchors empty", sig["anchors"] == {})
        # edges still work on the non-git file listing
        edges = cg.import_edges(str(plain), files)
        assert_true("non-git: edges computed", isinstance(edges["edges"], list))


def test_cli_writes_json():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        out = Path(tmp) / "out"
        r = subprocess.run([sys.executable, str(HELPER), str(repo), "--out", str(out)],
                           capture_output=True, text=True, timeout=30)
        assert_true("cli rc=0", r.returncode == 0, hint=r.stderr)
        git = json.loads((out / "git.json").read_text())
        edges = json.loads((out / "edges.json").read_text())
        assert_true("git.json head present", is_hex40(git["head"]))
        assert_true("edges.json has nodes", len(edges["nodes"]) >= 2)


def main():
    print("=== test_code_signals.py ===")
    test_anchors_and_churn()
    test_import_edges_resolve_intra_repo()
    test_non_git_degrades()
    test_cli_writes_json()
    print("\nAll code-signals tests passed.")


if __name__ == "__main__":
    main()
