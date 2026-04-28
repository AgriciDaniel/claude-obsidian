"""_vault.py — shared vault resolution for all claude-obsidian scripts.

Extracted from wiki-hooks.py so that every script in scripts/ can resolve
the vault with a single import instead of duplicating the logic.

Usage from any sibling script:

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _vault import resolve_vault, resolve_vault_or_die, PLUGIN_ROOT

PLUGIN_ROOT is always the plugin install directory (parent of scripts/).
resolve_vault() returns the vault Path or None.
resolve_vault_or_die() returns the vault Path or calls sys.exit().
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

ENV_VAR = "CLAUDE_OBSIDIAN_VAULT"
PLUGIN_ENV = "CLAUDE_PLUGIN_ROOT"
PROJECT_ENV = "CLAUDE_PROJECT_DIR"
USER_CONFIG = Path.home() / ".claude" / "claude-obsidian.json"
WALK_LIMIT = 6

_SCRIPT_DIR = Path(__file__).resolve().parent
# PLUGIN_ROOT: prefer $CLAUDE_PLUGIN_ROOT (set by Claude Code when loading
# the plugin), fall back to script's parent directory for standalone use.
_plugin_env = os.environ.get(PLUGIN_ENV, "")
PLUGIN_ROOT = Path(_plugin_env).resolve() if _plugin_env else _SCRIPT_DIR.parent

PATH_LINE_RE = re.compile(r"^\s*Path:\s*(\S.*?)\s*$", re.MULTILINE)
WIKI_BLOCK_RE = re.compile(
    r"^##\s+Wiki Knowledge Base\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_vault(path: Path, trace: Optional[list] = None) -> bool:
    """A directory is a vault iff it contains .obsidian/."""
    def _t(msg: str) -> None:
        if trace is not None:
            trace.append(msg)
    try:
        exists = path.exists()
        is_dir = path.is_dir() if exists else False
        has_obsidian = (path / ".obsidian").is_dir() if is_dir else False
        _t(f"_is_vault({path}): exists={exists} is_dir={is_dir} .obsidian/={has_obsidian}")
        return has_obsidian
    except OSError as e:
        _t(f"_is_vault({path}): OSError: {e}")
        return False


def _normalize(path_str: str, base: Optional[Path] = None,
               trace: Optional[list] = None) -> Optional[Path]:
    """Resolve *path_str* to an absolute Path and validate it as a vault."""
    def _t(msg: str) -> None:
        if trace is not None:
            trace.append(msg)
    if not path_str:
        _t("_normalize: empty path_str, returning None")
        return None
    try:
        expanded = os.path.expandvars(os.path.expanduser(path_str))
        raw = Path(expanded)
        _t(f"_normalize: input={path_str!r} expanded={expanded!r} is_absolute={raw.is_absolute()} base={base}")
        if not raw.is_absolute() and base is not None:
            raw = base / raw
            _t(f"_normalize: joined with base -> {raw}")
        p = raw.resolve()
        _t(f"_normalize: resolved -> {p}")
    except (OSError, RuntimeError) as e:
        _t(f"_normalize: resolve error: {e}")
        return None
    if _is_vault(p, trace=trace):
        return p
    return None


def _path_from_claude_md(claude_md: Path,
                         trace: Optional[list] = None) -> Optional[Path]:
    try:
        text = claude_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    block = WIKI_BLOCK_RE.search(text)
    if not block:
        return None
    m = PATH_LINE_RE.search(block.group("body"))
    if not m:
        return None
    return _normalize(m.group(1), base=claude_md.parent, trace=trace)


def _walk_up(start: Path) -> Optional[Path]:
    home = Path.home().resolve()
    try:
        cur = start.resolve()
    except (OSError, RuntimeError):
        return None
    for _ in range(WALK_LIMIT + 1):
        if _is_vault(cur):
            return cur
        if cur == home or cur.parent == cur:
            return None
        cur = cur.parent
    return None


def _from_user_config(trace: Optional[list] = None) -> Optional[Path]:
    try:
        data = json.loads(USER_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return _normalize(data.get("vault", "") or "", trace=trace)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_vault(trace: Optional[list] = None) -> Optional[Path]:
    """Five-step resolution chain. Each step returns None on any failure
    so the next step gets a turn. Never raises.

    If *trace* is a list, diagnostic strings are appended for each step
    so callers can log the full resolution attempt."""
    def _trace(msg: str) -> None:
        if trace is not None:
            trace.append(msg)

    project = os.environ.get(PROJECT_ENV, "")
    project_base = Path(project) if project else None
    cwd = Path.cwd()
    _trace(f"cwd={cwd}")
    _trace(f"{PROJECT_ENV}={project!r}")

    # Step 1: env var
    env = os.environ.get(ENV_VAR, "")
    _trace(f"{ENV_VAR}={env!r}")
    base = project_base or cwd
    _trace(f"step1-env: base={base}")
    p = _normalize(env, base=base, trace=trace)
    if p:
        _trace(f"step1-env: resolved to {p}")
        return p
    if env:
        _trace("step1-env: set but did not resolve (see _normalize/_is_vault above)")
    else:
        _trace("step1-env: not set, skipped")

    # Step 2: CLAUDE.md in project dir
    if project_base:
        _trace(f"step2-project-claude-md: checking {project_base / 'CLAUDE.md'}")
        p = _path_from_claude_md(project_base / "CLAUDE.md", trace=trace)
        if p:
            _trace(f"step2-project-claude-md: resolved to {p}")
            return p
        _trace(f"step2-project-claude-md: no match")
    else:
        _trace("step2-project-claude-md: CLAUDE_PROJECT_DIR not set, skipped")

    # Step 3: CLAUDE.md in cwd
    _trace(f"step3-cwd-claude-md: checking {cwd / 'CLAUDE.md'}")
    p = _path_from_claude_md(cwd / "CLAUDE.md", trace=trace)
    if p:
        _trace(f"step3-cwd-claude-md: resolved to {p}")
        return p
    _trace(f"step3-cwd-claude-md: no match")

    # Step 4: walk up
    p = _walk_up(cwd)
    if p:
        _trace(f"step4-walk-up: resolved to {p}")
        return p
    _trace(f"step4-walk-up: no vault found walking up from {cwd}")

    # Step 5: user config
    _trace(f"step5-user-config: checking {USER_CONFIG}")
    p = _from_user_config(trace=trace)
    if p:
        _trace(f"step5-user-config: resolved to {p}")
        return p
    config_exists = USER_CONFIG.exists()
    _trace(f"step5-user-config: exists={config_exists}, no vault resolved")

    _trace("FAILED: no vault found after all 5 steps")
    return None


def resolve_vault_or_die(exit_code: int = 1,
                         trace: Optional[list] = None) -> Path:
    """Like resolve_vault() but sys.exit() if no vault is found."""
    vault = resolve_vault(trace=trace)
    if vault is None:
        print("error: could not resolve vault. Set $CLAUDE_OBSIDIAN_VAULT "
              "or run from inside a vault directory.", file=sys.stderr)
        sys.exit(exit_code)
    return vault
