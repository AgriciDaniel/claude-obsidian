# Vault Resolution

The plugin and the vault are separate directories. The plugin (skills, scripts, hooks) lives at a fixed install location. The vault (wiki/, .raw/, .vault-meta/, .obsidian/) can be anywhere on the filesystem.

Before using any vault paths, resolve two roots:

## VAULT_ROOT — where vault data lives

Resolution order (first match wins):

1. `$CLAUDE_OBSIDIAN_VAULT` env var (set in `.claude/settings.json`)
2. `Path:` line inside `## Wiki Knowledge Base` block in `$CLAUDE_PROJECT_DIR/CLAUDE.md`
3. `Path:` line inside `## Wiki Knowledge Base` block in `./CLAUDE.md`
4. Walk up from cwd looking for a directory containing `.obsidian/`
5. `~/.claude/claude-obsidian.json` → `"vault"` key

In practice, step 1 covers most cases. Check it first:

```bash
VAULT_ROOT="${CLAUDE_OBSIDIAN_VAULT}"
# If empty, fall back to cwd (only valid if cwd IS the vault)
if [ -z "$VAULT_ROOT" ]; then
  if [ -d ".obsidian" ]; then
    VAULT_ROOT="$(pwd)"
  else
    echo "Cannot resolve vault. Set CLAUDE_OBSIDIAN_VAULT." >&2
  fi
fi
```

These paths live inside the vault:
- `$VAULT_ROOT/wiki/` — all wiki pages
- `$VAULT_ROOT/.raw/` — source documents
- `$VAULT_ROOT/.vault-meta/` — DragonScale metadata, tiling cache
- `$VAULT_ROOT/.obsidian/` — Obsidian config

## PLUGIN_ROOT — where scripts and skills live

Claude Code sets `$CLAUDE_PLUGIN_ROOT` to the plugin install directory when loading the plugin. This is where `scripts/`, `skills/`, and `hooks/` live. The Python scripts read this env var via `_vault.py` automatically.

When a skill tells you to run a script, use `$CLAUDE_PLUGIN_ROOT`:

```bash
python "$CLAUDE_PLUGIN_ROOT/scripts/tiling-check.py" --peek
"$CLAUDE_PLUGIN_ROOT/scripts/allocate-address.sh" --peek
python "$CLAUDE_PLUGIN_ROOT/scripts/boundary-score.py" --json
```

## The two-variable pattern

Every bash snippet in skills that touches both scripts and vault data needs both variables:

```bash
# Script path — from plugin
python "$CLAUDE_PLUGIN_ROOT/scripts/tiling-check.py" --peek

# Data path — from vault
cat "$VAULT_ROOT/wiki/hot.md"
ls "$VAULT_ROOT/.vault-meta/"
```

## Backward compatibility

If `$CLAUDE_OBSIDIAN_VAULT` is not set AND the plugin directory IS the vault (it contains `.obsidian/`), then `VAULT_ROOT = $CLAUDE_PLUGIN_ROOT`. This is the "clone-as-vault" setup. Everything works as before — paths just happen to be the same.
