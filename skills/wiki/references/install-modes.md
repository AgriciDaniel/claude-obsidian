# Supported installation modes

Resolve the installed product root from the invoking skill's own location, not
from the user-vault working directory:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

## Claude marketplace plugin

Install the plugin through its marketplace and invoke namespaced skills such as
`/claude-obsidian:wiki`. Plugin assets live in an ephemeral cache. Mutable vault
state must resolve from the project, `--vault`, or workspace configuration,
never `${CLAUDE_PLUGIN_ROOT}`.

## Local Claude plugin development

```bash
claude --plugin-dir /path/to/claude-obsidian
```

Skills remain namespaced. Run Claude from the user vault, not the plugin source
directory, or configure the vault explicitly.

## Portable Agent Skills

Use `scripts/setup-multi-agent.sh` or link each `skills/<name>/` directory at the
host's direct `<skill-root>/<name>/SKILL.md` discovery path. Codex, OpenCode,
and other Agent Skills hosts consume the same `SKILL.md` files. Claude-only
hooks are adapters, not core workflow logic.

## Product clone

A source clone is product/development code, not an automatically installed
plugin and not the recommended user vault. Create a separate vault:

```bash
python3 "$CORE" init /path/to/vault \
  --generated-at <ISO-UTC> --operation-id init-reviewed
python3 "$CORE" init /path/to/vault \
  --generated-at <ISO-UTC> --operation-id init-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Adopt an existing Obsidian vault non-destructively:

```bash
python3 "$CORE" adopt /path/to/vault \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed
python3 "$CORE" adopt /path/to/vault \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Both commands default to dry-run. New user vaults receive no upstream product
remote.
