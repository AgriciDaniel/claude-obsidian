#!/usr/bin/env python
"""test_wiki_hooks.py — unit tests for scripts/wiki-hooks.py.

Covers:
  - Each step of the resolve_vault() chain in isolation.
  - The two-marker check (a parent dir with only one marker must NOT match).
  - Malformed stdin -> ctx is {} -> subcommands still exit 0.
  - PostToolUse per-file commit scoping (file inside vault vs. outside).
  - Silent fallback when no vault resolves.
  - Stop's WIKI_CHANGED stdout marker.
  - init writes the user-config atomically and rejects non-vault paths.

Usage:
  python tests/test_wiki_hooks.py
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "wiki-hooks.py"

spec = importlib.util.spec_from_file_location("wiki_hooks", HELPER)
wh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wh)


class Fail(SystemExit):
    pass


def assert_eq(label, expected, actual):
    if expected != actual:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"OK   {label}")


def assert_true(label, cond):
    if not cond:
        raise Fail(f"FAIL {label}")
    print(f"OK   {label}")


def make_vault(parent: Path, name: str = "vault") -> Path:
    v = parent / name
    (v / "wiki").mkdir(parents=True)
    (v / ".vault-meta").mkdir(parents=True)
    return v


def half_vault(parent: Path, name: str, marker: str) -> Path:
    v = parent / name
    (v / marker).mkdir(parents=True)
    return v


# ---------------------------------------------------------------------------
# Resolution chain
# ---------------------------------------------------------------------------

def _clean_env(extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items()
           if k not in (wh.ENV_VAR, wh.PROJECT_ENV)}
    if extra:
        env.update(extra)
    return env


def test_env_var_wins():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "no-config.json"):
                got = wh.resolve_vault()
        assert_eq("env var resolves", v.resolve(), got)


def test_env_var_invalid_falls_through():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        bogus = tmp / "does-not-exist"
        # No CWD vault, no user config -> invalid env var should fall through to None.
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(bogus)}), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "no-config.json"):
                with mock.patch.object(Path, "cwd", staticmethod(lambda: tmp)):
                    got = wh.resolve_vault()
        assert_eq("invalid env var -> None (fall through)", None, got)


def test_project_claude_md_path_line():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp, "actual-vault")
        project = tmp / "some-project"
        project.mkdir()
        (project / "CLAUDE.md").write_text(
            "# Project\n\n"
            "## Wiki Knowledge Base\n"
            f"Path: {v}\n"
            "Registry key: foo/bar\n\n"
            "## Other section\n"
        )
        env = _clean_env({wh.PROJECT_ENV: str(project)})
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "no-config.json"):
                with mock.patch.object(Path, "cwd", staticmethod(lambda: tmp)):
                    got = wh.resolve_vault()
        assert_eq("project CLAUDE.md Path: line resolves", v.resolve(), got)


def test_cwd_claude_md_path_line():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp, "actual-vault")
        cwd = tmp / "consumer"
        cwd.mkdir()
        (cwd / "CLAUDE.md").write_text(
            f"## Wiki Knowledge Base\nPath: {v}\n"
        )
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "no-config.json"):
                with mock.patch.object(Path, "cwd", staticmethod(lambda: cwd)):
                    got = wh.resolve_vault()
        assert_eq("cwd CLAUDE.md Path: line resolves", v.resolve(), got)


def test_walk_up_finds_vault():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        deep = v / "a" / "b" / "c"
        deep.mkdir(parents=True)
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "no-config.json"):
                with mock.patch.object(Path, "cwd", staticmethod(lambda: deep)):
                    # Force HOME above tmp so the walk doesn't terminate early.
                    with mock.patch.object(Path, "home",
                                           staticmethod(lambda: Path("/"))):
                        got = wh.resolve_vault()
        assert_eq("walk-up resolves to vault", v.resolve(), got)


def test_walk_up_two_marker_check():
    """A parent dir that has only wiki/ (not .vault-meta/) MUST NOT match."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Outer dir has wiki/ only -> looks vault-ish, but isn't.
        outer = half_vault(tmp, "false-positive", "wiki")
        # Real vault nested deeper, but cwd is BETWEEN outer and the real one
        # to make sure the walker stops at the false-positive if the check
        # were sloppy. Construct: outer/wiki/, outer/sub/cwd/  -- no real vault
        # at all to confirm the false-positive parent is rejected.
        cwd = outer / "sub" / "cwd"
        cwd.mkdir(parents=True)
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "no-config.json"):
                with mock.patch.object(Path, "cwd", staticmethod(lambda: cwd)):
                    with mock.patch.object(Path, "home",
                                           staticmethod(lambda: Path("/"))):
                        got = wh.resolve_vault()
        assert_eq("two-marker check rejects wiki/-only parent", None, got)


def test_user_config_resolves():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        cfg = tmp / "claude-obsidian.json"
        cfg.write_text(json.dumps({"version": 1, "vault": str(v)}))
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", cfg):
                # cwd points outside any vault.
                outside = tmp / "outside"
                outside.mkdir()
                with mock.patch.object(Path, "cwd", staticmethod(lambda: outside)):
                    with mock.patch.object(Path, "home",
                                           staticmethod(lambda: outside)):
                        got = wh.resolve_vault()
        assert_eq("user config resolves", v.resolve(), got)


def test_no_resolve_returns_none():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "missing.json"):
                with mock.patch.object(Path, "cwd", staticmethod(lambda: tmp)):
                    with mock.patch.object(Path, "home",
                                           staticmethod(lambda: tmp)):
                        got = wh.resolve_vault()
        assert_eq("no-resolve returns None", None, got)


def test_priority_env_beats_user_config():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        env_vault = make_vault(tmp, "env-vault")
        cfg_vault = make_vault(tmp, "cfg-vault")
        cfg = tmp / "claude-obsidian.json"
        cfg.write_text(json.dumps({"version": 1, "vault": str(cfg_vault)}))
        with mock.patch.dict(
            os.environ, _clean_env({wh.ENV_VAR: str(env_vault)}), clear=True
        ):
            with mock.patch.object(wh, "USER_CONFIG", cfg):
                got = wh.resolve_vault()
        assert_eq("env var beats user config", env_vault.resolve(), got)


# ---------------------------------------------------------------------------
# Stdin parsing
# ---------------------------------------------------------------------------

def test_read_stdin_empty():
    with mock.patch.object(sys, "stdin", io.StringIO("")):
        # isatty() on StringIO returns False; pipe-like.
        ctx = wh.read_stdin_json()
    assert_eq("empty stdin -> {}", {}, ctx)


def test_read_stdin_garbage():
    with mock.patch.object(sys, "stdin", io.StringIO("not json {")):
        ctx = wh.read_stdin_json()
    assert_eq("garbage stdin -> {}", {}, ctx)


def test_read_stdin_non_object():
    with mock.patch.object(sys, "stdin", io.StringIO('"a string"')):
        ctx = wh.read_stdin_json()
    assert_eq("non-object stdin -> {}", {}, ctx)


def test_read_stdin_valid():
    payload = {"tool_input": {"file_path": "wiki/foo.md"}}
    with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
        ctx = wh.read_stdin_json()
    assert_eq("valid stdin parsed", payload, ctx)


# ---------------------------------------------------------------------------
# PostToolUse per-file commit scoping
# ---------------------------------------------------------------------------

def _git_init(vault: Path) -> None:
    subprocess.run(["git", "-C", str(vault), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(vault), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(vault), "config", "user.name", "test"], check=True
    )
    subprocess.run(
        ["git", "-C", str(vault), "config", "commit.gpgsign", "false"], check=True
    )
    # Initial commit so HEAD exists.
    (vault / ".gitkeep").write_text("")
    subprocess.run(["git", "-C", str(vault), "add", ".gitkeep"], check=True)
    subprocess.run(
        ["git", "-C", str(vault), "commit", "-q", "-m", "init"], check=True
    )


def _commit_subject_count(vault: Path) -> int:
    out = subprocess.run(
        ["git", "-C", str(vault), "log", "--format=%s"],
        capture_output=True, text=True, check=True,
    )
    return len([l for l in out.stdout.splitlines() if l.startswith("wiki: auto-commit")])


def _last_commit_files(vault: Path) -> list:
    out = subprocess.run(
        ["git", "-C", str(vault), "show", "--name-only", "--format=", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return [l for l in out.stdout.splitlines() if l.strip()]


def test_post_tool_use_per_file_commit():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        _git_init(v)
        target = v / "wiki" / "concepts.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("hello\n")
        # Touch an OTHER file that should NOT be in the commit.
        other = v / "wiki" / "other.md"
        other.write_text("other\n")

        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            rc = wh.cmd_post_tool_use({"tool_input": {"file_path": str(target)}})
        assert_eq("per-file rc 0", 0, rc)
        files = _last_commit_files(v)
        assert_eq("only target staged", ["wiki/concepts.md"], files)
        # `other.md` is still untracked.
        status = subprocess.run(
            ["git", "-C", str(v), "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        )
        assert_true("other still untracked", "wiki/other.md" in status.stdout)


def test_post_tool_use_falls_back_to_bulk_when_path_outside():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        _git_init(v)
        # Add a wiki file so the bulk add has something to stage.
        page = v / "wiki" / "page.md"
        page.write_text("body\n")
        outside = tmp / "elsewhere.md"
        outside.write_text("outside\n")

        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            rc = wh.cmd_post_tool_use({"tool_input": {"file_path": str(outside)}})
        assert_eq("fallback rc 0", 0, rc)
        # Bulk add picks up wiki/ contents, but never touches outside files.
        files = _last_commit_files(v)
        assert_true("page.md committed via bulk add", "wiki/page.md" in files)
        assert_true("outside file not committed",
                    not any("elsewhere" in f for f in files))


def test_post_tool_use_no_change_no_commit():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        _git_init(v)
        before = _commit_subject_count(v)
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            wh.cmd_post_tool_use({})
        after = _commit_subject_count(v)
        assert_eq("no-op when nothing staged", before, after)


def test_post_tool_use_no_git_silent():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)  # no git init
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            rc = wh.cmd_post_tool_use({"tool_input": {"file_path": "wiki/x.md"}})
        assert_eq("no git -> 0 silently", 0, rc)


# ---------------------------------------------------------------------------
# Stop hook
# ---------------------------------------------------------------------------

def test_stop_emits_marker_on_wiki_change(capsys=None):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        _git_init(v)
        # Commit a wiki file, then edit it without committing.
        page = v / "wiki" / "page.md"
        page.write_text("v1\n")
        subprocess.run(["git", "-C", str(v), "add", "wiki/page.md"], check=True)
        subprocess.run(["git", "-C", str(v), "commit", "-q", "-m", "p"], check=True)
        page.write_text("v2\n")

        buf = io.StringIO()
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            with mock.patch.object(sys, "stdout", buf):
                rc = wh.cmd_stop({})
        assert_eq("stop rc 0", 0, rc)
        assert_true("WIKI_CHANGED printed", "WIKI_CHANGED:" in buf.getvalue())


def test_stop_silent_when_no_wiki_change():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        _git_init(v)
        buf = io.StringIO()
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            with mock.patch.object(sys, "stdout", buf):
                rc = wh.cmd_stop({})
        assert_eq("stop rc 0 (no change)", 0, rc)
        assert_eq("no WIKI_CHANGED on clean repo", "", buf.getvalue())


def test_stop_silent_when_no_vault():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with mock.patch.dict(os.environ, _clean_env(), clear=True):
            with mock.patch.object(wh, "USER_CONFIG", tmp / "no-config.json"):
                with mock.patch.object(Path, "cwd", staticmethod(lambda: tmp)):
                    with mock.patch.object(Path, "home",
                                           staticmethod(lambda: tmp)):
                        buf = io.StringIO()
                        with mock.patch.object(sys, "stdout", buf):
                            rc = wh.cmd_stop({})
        assert_eq("stop rc 0 (no vault)", 0, rc)
        assert_eq("no output without vault", "", buf.getvalue())


# ---------------------------------------------------------------------------
# session-start
# ---------------------------------------------------------------------------

def test_session_start_emits_hot():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        (v / "wiki" / "hot.md").write_text("HOTCACHE\n")
        buf = io.StringIO()
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            with mock.patch.object(sys, "stdout", buf):
                rc = wh.cmd_session_start({})
        assert_eq("rc 0", 0, rc)
        assert_eq("hot.md piped to stdout", "HOTCACHE\n", buf.getvalue())


def test_session_start_silent_when_no_hot():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        buf = io.StringIO()
        with mock.patch.dict(os.environ, _clean_env({wh.ENV_VAR: str(v)}), clear=True):
            with mock.patch.object(sys, "stdout", buf):
                rc = wh.cmd_session_start({})
        assert_eq("rc 0 no hot", 0, rc)
        assert_eq("no output without hot.md", "", buf.getvalue())


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def test_init_writes_config():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        cfg = tmp / "claude-obsidian.json"
        with mock.patch.object(wh, "USER_CONFIG", cfg):
            rc = wh.cmd_init(type("A", (), {"vault": str(v)})())
        assert_eq("init rc 0", 0, rc)
        data = json.loads(cfg.read_text())
        assert_eq("config version", 1, data.get("version"))
        assert_eq("config vault", str(v.resolve()), data.get("vault"))


def test_init_rejects_non_vault():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        not_vault = tmp / "no-markers"
        not_vault.mkdir()
        cfg = tmp / "claude-obsidian.json"
        with mock.patch.object(wh, "USER_CONFIG", cfg):
            with mock.patch.object(sys, "stderr", io.StringIO()):
                rc = wh.cmd_init(type("A", (), {"vault": str(not_vault)})())
        assert_eq("init rejects non-vault", 2, rc)
        assert_true("no config written on rejection", not cfg.exists())


# ---------------------------------------------------------------------------
# CLI integration (subprocess) — confirms shebang + argparse + exit codes.
# ---------------------------------------------------------------------------

def test_cli_no_vault_exits_zero():
    with tempfile.TemporaryDirectory() as tmp:
        env = {k: v for k, v in os.environ.items() if k != wh.ENV_VAR}
        env["HOME"] = tmp
        # Drop CLAUDE_PROJECT_DIR too so the chain has nothing to grab.
        env.pop(wh.PROJECT_ENV, None)
        for sub in ("session-start", "post-compact", "post-tool-use", "stop"):
            r = subprocess.run(
                [sys.executable, str(HELPER), sub],
                cwd=tmp, env=env, input="", capture_output=True, text=True, timeout=5,
            )
            assert_eq(f"cli {sub} rc 0 with no vault", 0, r.returncode)
            assert_eq(f"cli {sub} no stdout", "", r.stdout)


def test_cli_init_then_resolve():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        (v / "wiki" / "hot.md").write_text("HC\n")

        fake_home = tmp / "home"
        fake_home.mkdir()
        env = {k: vv for k, vv in os.environ.items() if k != wh.ENV_VAR}
        env["HOME"] = str(fake_home)
        env.pop(wh.PROJECT_ENV, None)

        # init
        r = subprocess.run(
            [sys.executable, str(HELPER), "init", "--vault", str(v)],
            env=env, capture_output=True, text=True, timeout=5,
        )
        assert_eq("cli init rc 0", 0, r.returncode)
        assert_true("config file exists",
                    (fake_home / ".claude" / "claude-obsidian.json").is_file())

        # session-start now finds the vault from a faraway cwd
        away = tmp / "away"
        away.mkdir()
        r = subprocess.run(
            [sys.executable, str(HELPER), "session-start"],
            cwd=str(away), env=env, input="", capture_output=True, text=True, timeout=5,
        )
        assert_eq("cli session-start rc 0", 0, r.returncode)
        assert_eq("hot.md emitted via user config", "HC\n", r.stdout)


# ---------------------------------------------------------------------------
# Logging rotation
# ---------------------------------------------------------------------------

def test_log_rotation():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        v = make_vault(tmp)
        log_path = v / ".vault-meta" / "hooks.log"
        # Pre-populate above LOG_MAX_BYTES.
        big = "x" * 1200  # 1.2 KB lines
        with open(log_path, "w") as f:
            for _ in range(1100):  # ~1.32 MB
                f.write(big + "\n")
        size_before = log_path.stat().st_size
        assert_true("log oversized before rotation", size_before > wh.LOG_MAX_BYTES)
        wh.log(v, "test", "trigger rotation")
        size_after = log_path.stat().st_size
        assert_true("log shrunk after rotation", size_after < size_before)
        assert_true("log under the keep size + slack",
                    size_after <= wh.LOG_KEEP_BYTES + 4096)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    tests = [
        test_env_var_wins,
        test_env_var_invalid_falls_through,
        test_project_claude_md_path_line,
        test_cwd_claude_md_path_line,
        test_walk_up_finds_vault,
        test_walk_up_two_marker_check,
        test_user_config_resolves,
        test_no_resolve_returns_none,
        test_priority_env_beats_user_config,
        test_read_stdin_empty,
        test_read_stdin_garbage,
        test_read_stdin_non_object,
        test_read_stdin_valid,
        test_post_tool_use_per_file_commit,
        test_post_tool_use_falls_back_to_bulk_when_path_outside,
        test_post_tool_use_no_change_no_commit,
        test_post_tool_use_no_git_silent,
        test_stop_emits_marker_on_wiki_change,
        test_stop_silent_when_no_wiki_change,
        test_stop_silent_when_no_vault,
        test_session_start_emits_hot,
        test_session_start_silent_when_no_hot,
        test_init_writes_config,
        test_init_rejects_non_vault,
        test_cli_no_vault_exits_zero,
        test_cli_init_then_resolve,
        test_log_rotation,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except Fail as e:
            print(e)
            failures += 1
    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    print(f"\nall {len(tests)} tests passed")


if __name__ == "__main__":
    main()
