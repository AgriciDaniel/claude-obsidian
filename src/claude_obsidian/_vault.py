"""Shared vault-root resolution so every tool runs against any vault dir.

Precedence:
  1. CO_VAULT_ROOT env var  (explicit override)
  2. cwd, if it looks like a vault (has .vault-meta/ or wiki/)
  3. repo root (fallback, for in-tree/dev use)

This is the one shared library the scripts genuinely duplicated. Modules keep
their own local `log()` because logging targets differ (e.g. rerank also routes
to .vault-meta/hook.log).
"""
import os
from pathlib import Path


def resolve_vault_root() -> Path:
    env = os.environ.get("CO_VAULT_ROOT")
    if env:
        return Path(env).resolve()
    cwd = Path.cwd()
    if (cwd / ".vault-meta").is_dir() or (cwd / "wiki").is_dir():
        return cwd.resolve()
    # src/claude_obsidian/_vault.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]
