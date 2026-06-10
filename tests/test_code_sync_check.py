#!/usr/bin/env python3
"""test_code_sync_check.py — hermetic tests for scripts/code-sync-check.py.

Monkeypatches the module's state/queue paths into a tempdir, builds a throwaway
git repo, and exercises register / enqueue / surface / mark-synced / repo-mode.

Usage:
  python3 tests/test_code_sync_check.py
"""
import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "code-sync-check.py"

spec = importlib.util.spec_from_file_location("code_sync_check", HELPER)
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


def point_at(tmp):
    meta = Path(tmp) / ".vault-meta"
    meta.mkdir(parents=True, exist_ok=True)
    cs.META_DIR = meta
    cs.QUEUE_PATH = meta / "code-sync-queue.jsonl"
    cs.STATE_PATH = meta / "code-sync-state.json"
    cs.LOCK_PATH = meta / ".code-sync.lock"


def make_repo(tmp):
    repo = Path(tmp) / "repo"
    (repo / "app").mkdir(parents=True)
    (repo / "app" / "main.py").write_text("print(1)\n", encoding="utf-8")
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "t@example.com"], repo)
    run(["git", "config", "user.name", "Test"], repo)
    run(["git", "add", "app"], repo)
    run(["git", "commit", "-q", "-m", "init"], repo)
    return repo


def head(repo):
    return run(["git", "-C", str(repo), "rev-parse", "HEAD"], repo).stdout.strip()


def test_register_and_repo_mode():
    with tempfile.TemporaryDirectory() as tmp:
        point_at(tmp)
        repo = make_repo(tmp)
        cs.action_register(str(repo), "autonomous")
        state = json.loads(cs.STATE_PATH.read_text())
        assert_true("repo registered", len(state["watched_repos"]) == 1, hint=str(state))
        assert_true("mode stored", state["watched_repos"][0]["mode"] == "autonomous")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cs.action_repo_mode(str(repo))
        assert_true("repo-mode prints autonomous", buf.getvalue().strip() == "autonomous", hint=buf.getvalue())


def test_enqueue_and_surface():
    with tempfile.TemporaryDirectory() as tmp:
        point_at(tmp)
        repo = make_repo(tmp)
        cs.action_register(str(repo), "in-session")
        cs.action_enqueue(str(repo), head(repo))
        rows = cs.read_queue()
        assert_true("one queued entry", len(rows) == 1, hint=str(rows))
        assert_true("entry pending", rows[0]["status"] == "pending")
        assert_true("changed_paths captured", "app/main.py" in rows[0]["changed_paths"], hint=str(rows[0]))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cs.action_surface()
        out = buf.getvalue()
        assert_true("surface mentions code-sync", "[code-sync]" in out, hint=out)
        assert_true("surface lists changed path", "app/main.py" in out, hint=out)


def test_surface_silent_when_empty():
    with tempfile.TemporaryDirectory() as tmp:
        point_at(tmp)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cs.action_surface()
        assert_true("no output when queue empty", buf.getvalue() == "", hint=repr(buf.getvalue()))


def test_mark_synced():
    with tempfile.TemporaryDirectory() as tmp:
        point_at(tmp)
        repo = make_repo(tmp)
        cs.action_register(str(repo), "in-session")
        h = head(repo)
        cs.action_enqueue(str(repo), h)
        cs.action_mark_synced(str(repo), h)
        rows = cs.read_queue()
        assert_true("entry marked synced", all(r["status"] == "synced" for r in rows), hint=str(rows))
        state = json.loads(cs.STATE_PATH.read_text())
        assert_true("last_synced_commit set", state["watched_repos"][0]["last_synced_commit"] == h)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cs.action_surface()
        assert_true("surface silent after sync", buf.getvalue() == "", hint=repr(buf.getvalue()))


def test_unregister():
    with tempfile.TemporaryDirectory() as tmp:
        point_at(tmp)
        repo = make_repo(tmp)
        cs.action_register(str(repo), "in-session")
        cs.action_unregister(str(repo))
        state = json.loads(cs.STATE_PATH.read_text())
        assert_true("repo removed", state["watched_repos"] == [], hint=str(state))


def main():
    print("=== test_code_sync_check.py ===")
    test_register_and_repo_mode()
    test_enqueue_and_surface()
    test_surface_silent_when_empty()
    test_mark_synced()
    test_unregister()
    print("\nAll code-sync-check tests passed.")


if __name__ == "__main__":
    main()
