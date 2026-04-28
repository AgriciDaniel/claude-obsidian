#!/usr/bin/env python
"""wiki-hooks.py — unified dispatcher for claude-obsidian plugin hooks.

One executable handles every hook event the plugin registers. The dispatcher
resolves the vault on its own so the hooks work whether the plugin lives
inside the vault (clone-as-vault), is installed globally (install-as-plugin),
or is added to a separate Obsidian vault (add-to-existing-vault).

Subcommands map to hook events:
  session-start       Print wiki/hot.md if the vault has one. Read-only.
  post-compact        Same as session-start. Restores the hot cache after
                      Claude Code compacts the conversation.
  post-tool-use       Auto-commit wiki/.raw/.vault-meta changes. If stdin
                      gives a tool_input.file_path inside the vault, commit
                      only that file; otherwise fall back to the bulk add.
  stop                Detect uncommitted wiki/ edits and print the
                      WIKI_CHANGED stdout marker that asks Claude to refresh
                      the hot cache.
  init --vault PATH   Write ~/.claude/claude-obsidian.json so the dispatcher
                      can find the vault from any working directory.

Vault resolution (priority order, first hit wins):
  1. $CLAUDE_OBSIDIAN_VAULT
  2. Path: line in $CLAUDE_PROJECT_DIR/CLAUDE.md (Claude Code sets this env)
  3. Path: line in ./CLAUDE.md
  4. Walk up from cwd (capped at $HOME, max 6 levels) for a directory
     containing both wiki/ and .vault-meta/.
  5. ~/.claude/claude-obsidian.json -> "vault" key

If nothing resolves, the dispatcher exits 0 silently. A hook MUST NEVER
break a Claude Code session, so every subcommand returns 0 (or prints to
stdout for the cases Claude reads back).

Failures (missing vault, git errors, malformed stdin) are logged to
<plugin-root>/logs/wiki-hooks.log. The log rotates by truncating to
roughly the last 500 KB once it exceeds 1 MB.

Exit codes:
  0  always, except for `init` usage errors (2)
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

# Vault resolution lives in _vault.py (shared with sibling scripts).
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from _vault import (  # noqa: E402
    resolve_vault, PLUGIN_ROOT, ENV_VAR, PROJECT_ENV, USER_CONFIG,
)

PLUGIN_LOG_DIR = PLUGIN_ROOT / "logs"
FALLBACK_LOG = PLUGIN_LOG_DIR / "wiki-hooks.log"
LOG_MAX_BYTES = 1_000_000
LOG_KEEP_BYTES = 500_000
HOT_CACHE_REL = Path("wiki") / "hot.md"

WIKI_CHANGED_MSG = (
    "WIKI_CHANGED: Wiki pages were modified this session. Please update "
    "wiki/hot.md with a brief summary of what changed (under 500 words). "
    "Use the hot cache format: Last Updated, Key Recent Facts, Recent "
    "Changes, Active Threads. Keep it factual. Overwrite the file "
    "completely. It is a cache, not a journal."
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _rotate_log(log_path: Path) -> None:
    try:
        if log_path.stat().st_size <= LOG_MAX_BYTES:
            return
    except OSError:
        return
    try:
        with open(log_path, "rb") as f:
            f.seek(-LOG_KEEP_BYTES, os.SEEK_END)
            tail = f.read()
        # Drop the partial first line so the file always starts on a
        # complete record.
        nl = tail.find(b"\n")
        if nl >= 0:
            tail = tail[nl + 1:]
        with open(log_path, "wb") as f:
            f.write(tail)
    except OSError:
        pass


def _write_log_line(log_path: Path, line: str) -> None:
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        _rotate_log(log_path)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def log(vault: Optional[Path], subcommand: str, message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{stamp} [{subcommand}] {message}\n"
    _write_log_line(FALLBACK_LOG, line)


# ---------------------------------------------------------------------------
# Stdin context
# ---------------------------------------------------------------------------

def read_stdin_json() -> dict:
    """Claude Code does not always send a body on stdin, so an empty or
    malformed payload must not raise."""
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(vault: Path, *args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(vault), *args],
        capture_output=capture,
        text=True,
        check=False,
    )


def _git_dir_ok(vault: Path) -> bool:
    """Works for plain repos, worktrees, and detached HEAD. Replaces the
    old `[ -d .git ]` check that fails on git worktrees."""
    return _git(vault, "rev-parse", "--git-dir", capture=True).returncode == 0


def _file_in_vault(vault: Path, file_path: str) -> Optional[str]:
    if not file_path:
        return None
    candidate = Path(file_path)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate)
    try:
        candidate = candidate.resolve()
        rel = candidate.relative_to(vault.resolve())
    except (OSError, RuntimeError, ValueError):
        return None
    return str(rel)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def _log_trace(vault: Optional[Path], subcmd: str, trace: list[str],
               result: Optional[Path]) -> None:
    """Write the full resolution trace to the log, one step per line."""
    header = f"vault resolution {'OK' if result else 'FAILED'}: result={result}"
    log(vault, subcmd, header)
    for line in trace:
        log(vault, subcmd, f"  {line}")


def cmd_session_start(_ctx: dict) -> int:
    trace: list[str] = []
    vault = resolve_vault(trace=trace)
    if vault is None:
        _log_trace(None, "session-start", trace, None)
        return 0
    _log_trace(vault, "session-start", trace, vault)
    hot = vault / HOT_CACHE_REL
    if not hot.is_file():
        log(vault, "session-start", f"hot.md not found at {hot}")
        return 0
    try:
        content = hot.read_text(encoding="utf-8", errors="replace")
        sys.stdout.buffer.write(content.encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    except OSError as e:
        log(vault, "session-start", f"hot.md read failed: {e}")
    return 0


def cmd_post_compact(ctx: dict) -> int:
    # Same logic as session-start but logged under its own name.
    trace: list[str] = []
    vault = resolve_vault(trace=trace)
    if vault is None:
        _log_trace(None, "post-compact", trace, None)
        return 0
    _log_trace(vault, "post-compact", trace, vault)
    hot = vault / HOT_CACHE_REL
    if not hot.is_file():
        log(vault, "post-compact", f"hot.md not found at {hot}")
        return 0
    try:
        content = hot.read_text(encoding="utf-8", errors="replace")
        sys.stdout.buffer.write(content.encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    except OSError as e:
        log(vault, "post-compact", f"hot.md read failed: {e}")
    return 0


def cmd_post_tool_use(ctx: dict) -> int:
    vault = resolve_vault()
    if vault is None:
        return 0
    if not _git_dir_ok(vault):
        log(vault, "post-tool-use", "no git repo")
        return 0

    file_path = ""
    tool_input = ctx.get("tool_input")
    if isinstance(tool_input, dict):
        fp = tool_input.get("file_path")
        if isinstance(fp, str):
            file_path = fp

    rel = _file_in_vault(vault, file_path) if file_path else None
    if rel:
        add = _git(vault, "add", "--", rel, capture=True)
        scope = rel
    else:
        # Filter to existing dirs so an incomplete vault layout (missing .raw/
        # for example) does not turn into a git pathspec error.
        targets = [d for d in ("wiki", ".raw", ".vault-meta") if (vault / d).is_dir()]
        if not targets:
            return 0
        add = _git(vault, "add", *[f"{t}/" for t in targets], capture=True)
        scope = " ".join(f"{t}/" for t in targets)

    if add.returncode != 0:
        log(vault, "post-tool-use", f"git add failed ({scope}): {add.stderr.strip()}")
        return 0

    diff = _git(vault, "diff", "--cached", "--quiet")
    if diff.returncode == 0:
        return 0  # nothing staged, no commit

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit = _git(vault, "commit", "-m", f"wiki: auto-commit {stamp}", capture=True)
    if commit.returncode != 0:
        log(vault, "post-tool-use", f"commit failed: {commit.stderr.strip()}")
    return 0


def cmd_stop(_ctx: dict) -> int:
    vault = resolve_vault()
    if vault is None:
        return 0
    if not _git_dir_ok(vault):
        return 0
    diff = _git(vault, "diff", "--name-only", "HEAD", capture=True)
    if diff.returncode != 0:
        log(vault, "stop", f"git diff failed: {diff.stderr.strip()}")
        return 0
    for line in diff.stdout.splitlines():
        if line.startswith("wiki/"):
            print(WIKI_CHANGED_MSG)
            return 0
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    raw = args.vault
    try:
        target = Path(os.path.expandvars(os.path.expanduser(raw))).resolve()
    except (OSError, RuntimeError) as e:
        print(f"wiki-hooks init: invalid path: {e}", file=sys.stderr)
        return 2
    if not _is_vault(target):
        print(
            f"wiki-hooks init: not a vault (missing wiki/ or .vault-meta/): {target}",
            file=sys.stderr,
        )
        return 2

    USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "vault": str(target)}
    fd, tmp = tempfile.mkstemp(
        prefix="claude-obsidian.", suffix=".tmp", dir=str(USER_CONFIG.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        os.replace(tmp, USER_CONFIG)
    except OSError as e:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        print(f"wiki-hooks init: write failed: {e}", file=sys.stderr)
        return 2
    print(f"wrote {USER_CONFIG} -> {target}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

HOOK_COMMANDS = {
    "session-start": cmd_session_start,
    "post-compact": cmd_post_compact,
    "post-tool-use": cmd_post_tool_use,
    "stop": cmd_stop,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wiki-hooks",
        description="Unified hook dispatcher for the claude-obsidian plugin.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in HOOK_COMMANDS:
        sub.add_parser(name, help=f"hook handler: {name}")
    init = sub.add_parser("init", help="write ~/.claude/claude-obsidian.json")
    init.add_argument("--vault", required=True, help="absolute path to the vault")
    return p


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "init":
        return cmd_init(args)
    handler = HOOK_COMMANDS[args.cmd]
    try:
        ctx = read_stdin_json()
    except Exception as e:  # belt-and-suspenders; read_stdin_json is already defensive
        log(None, args.cmd, f"stdin parse blew up: {e}")
        ctx = {}
    try:
        return handler(ctx)
    except Exception as e:
        # Last resort: never propagate to Claude Code.
        import traceback
        tb = traceback.format_exc()
        log(None, args.cmd, f"unhandled exception: {e!r}\n{tb}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
