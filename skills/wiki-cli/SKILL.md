---
name: wiki-cli
description: "Default vault-mutation transport for claude-obsidian v1.7+. Wraps the Obsidian CLI (Obsidian 1.12+) as the preferred way to read, write, search, and modify vault notes from Claude — no MCP server, no REST API plugin, no TLS workarounds. Falls back to direct filesystem Read/Write/Edit when the CLI is unavailable. Triggers on: wiki-cli, obsidian cli, obsidian read, obsidian write, obsidian search, daily note, obsidian create, obsidian append, vault transport, which transport, transport detection, obsidian command line."
allowed-tools: Read Bash
---

# wiki-cli: Default Transport Layer

claude-obsidian v1.7+ standardizes on the **Obsidian CLI** (shipped with Obsidian 1.12) as the preferred transport for all vault mutations on desktop. This skill is the recipe reference for using it.

**Substrate preference (v1.7+)**: This skill is a self-contained fallback. **Prefer `kepano/obsidian-skills`** (by Steph Ango, Obsidian CEO) as the authoritative substrate — its `obsidian-cli` skill is the canonical CLI reference for any Agent-Skills runtime. If you see an `obsidian-cli` skill available without the `claude-obsidian:` namespace, that is kepano's version: use it. The recipes below are provided so claude-obsidian remains functional when kepano's marketplace is not installed. Install kepano: `claude plugin marketplace add kepano/obsidian-skills`.

---

## Why CLI over MCP

| Concern | MCP (Options A/B) | Obsidian CLI |
|---|---|---|
| Install | Local REST API plugin + MCP server config | Built into Obsidian 1.12+ |
| Auth | API key + TLS bypass (`NODE_TLS_REJECT_UNAUTHORIZED=0`) | None — direct subprocess |
| Latency | HTTP round-trip per call | In-process binary |
| Failure mode | Plugin disabled → silent breakage | Binary missing → loud `command -v` failure |
| Reentrancy | Self-MCP-calls inside Claude session can deadlock | Pure subprocess, safe |
| Mobile / headless | Limited | Limited (CLI is desktop-only too) |

CLI loses to MCP on exactly one axis: it only works on machines where Obsidian itself is installed. For headless servers and mobile, fall through to the next transport in the chain.

---

## Detection

At session start (or vault setup), run:

```bash
bash scripts/detect-transport.sh
```

This writes `.vault-meta/transport.json` with the schema:

```json
{
  "preferred": "cli",
  "fallback_chain": ["cli", "filesystem"],
  "available": {
    "cli": {"present": true, "binary": "obsidian-cli", "version_string": "..."},
    "filesystem": {"present": true},
    "mcp_obsidian": {"present": null, "detection": "deferred"},
    "mcpvault": {"present": null, "detection": "deferred"}
  }
}
```

**Read this file before any non-trivial vault mutation.** Skills that need to read or write should consult `preferred` and pick the corresponding transport. The decision tree lives at `wiki/references/transport-fallback.md`.

Refresh detection with `--force` after installing/removing the Obsidian CLI:
```bash
bash scripts/detect-transport.sh --force
```

---

## Invocation contract

The CLI takes a subcommand followed by `key=value` options. It does **not** take positional
arguments, and it does **not** read content from stdin.

```
obsidian-cli <command> [vault=<name>] [key=value ...]
```

Three things to get right before writing any recipe:

- **`vault=` takes the vault NAME, not a path** — and the name is resolved against
  Obsidian's own registry, never against your working directory. This is a footgun:
  see the warning below. Omit it entirely to target the active vault.
- **`file=` resolves by name (like a wikilink); `path=` is exact** (`wiki/concepts/Foo.md`).
  Prefer `path=` in scripts — `file=` is ambiguous when two notes share a basename.
- **The CLI drives the running Obsidian app.** It is not a standalone vault parser. If
  Obsidian is not running, expect failure — check `available.cli.obsidian_app_running` in
  the detection snapshot.

> [!danger] `vault=<name>` can silently target a DIFFERENT directory.
> Because the name is resolved through Obsidian's registry, `vault=claude-obsidian` does
> **not** mean "the vault I am standing in." If Obsidian has some other folder registered
> under that name — a stray copy in `~/Downloads`, say — every read and write goes there
> instead, and the CLI reports success either way. This is not hypothetical: it swallowed
> an entire session's writes while the real working tree sat untouched.
>
> Never hardcode the vault name and never derive it from the directory basename.

`scripts/detect-transport.sh` closes this. It asks the CLI which vaults it can reach,
matches one against the vault root, and **refuses to prefer `cli` at all** unless a vault
is genuinely addressable (`preferred` falls back to `filesystem`). It publishes the
verified name for you to use. So take both the binary and the vault name from the snapshot:

```bash
SNAP=.vault-meta/transport.json
CLI="$(python3 -c "import json;print(json.load(open('$SNAP'))['available']['cli']['binary'])")"
VAULT="$(python3 -c "import json;print(json.load(open('$SNAP'))['available']['cli']['vault_name'])")"
```

And honor `preferred` before you use them. If it is not `cli`, use the filesystem
fallbacks below — the CLI either is not installed or cannot reach this vault:

```bash
PREFERRED="$(python3 -c "import json;print(json.load(open('$SNAP'))['preferred'])")"
[ "$PREFERRED" = cli ] || echo "CLI not usable here; use the filesystem fallback."
```

## Recipes (CLI-first; fallback noted inline)

Each recipe shows the CLI form first. If the CLI is unavailable per the detection snapshot,
fall through to the noted fallback. `$NOTE` is a vault-relative path like `wiki/concepts/Foo.md`;
`$VAULT_ROOT` is the absolute vault root (used only by the filesystem fallbacks).

### Read a note
```bash
# CLI
"$CLI" read vault="$VAULT" path="$NOTE"

# Fallback: Claude's Read tool with absolute path
# Read $VAULT_ROOT/$NOTE
```

### Create or overwrite a note
```bash
# CLI — there is no `write` command; `create` + `overwrite` is the upsert.
"$CLI" create vault="$VAULT" path="$NOTE" content="# Title\n\nBody text." overwrite

# Fallback: Claude's Write tool with absolute path
# Write $VAULT_ROOT/$NOTE with the desired content string
```

> [!warning] `content=` is a shell argument, not stdin.
> Newlines must be escaped as `\n` (and tabs as `\t`). There is no `< file.md` redirect form.
> For anything longer than a few lines — i.e. most real wiki pages — **prefer the filesystem
> Write tool**: it avoids a fragile escaping round-trip through the shell. Reserve `create`
> for short notes and for the case where you want Obsidian's own template/link handling.

### Append to a note
```bash
# CLI
"$CLI" append vault="$VAULT" path="$NOTE" content="additional content"

# Fallback: Read $VAULT_ROOT/$NOTE, append manually, Write back
```

`prepend` takes the same options. Both add a leading/trailing newline unless you pass `inline`.

### Search note content (CLI uses Obsidian's own search ranking)
```bash
# CLI — returns ranked file paths
"$CLI" search vault="$VAULT" query="<query>"

# Narrow, cap, or get structured output:
"$CLI" search vault="$VAULT" query="<query>" path=wiki/ limit=10 format=json

# With matching lines for context (closer to a grep hit list):
"$CLI" search:context vault="$VAULT" query="<query>" path=wiki/

# Fallback: ripgrep
rg --type=md "<query>" "$VAULT_ROOT/wiki/"
```

### Daily note (if Daily Notes plugin is enabled)
```bash
# CLI — there is no `daily:today`.
"$CLI" daily:path vault="$VAULT"      # resolve today's path
"$CLI" daily:read vault="$VAULT"      # read today's contents
"$CLI" daily:append vault="$VAULT" content="captured at $(date)"

# Fallback: compute path manually
NOTE="$VAULT_ROOT/wiki/daily/$(date +%Y-%m-%d).md"
```

### Patch a frontmatter property
```bash
# CLI — name= and value= are both required, and are named options, not positionals.
"$CLI" property:set vault="$VAULT" path="$NOTE" name=status value=evergreen

# Typed properties (text|list|number|checkbox|date|datetime):
"$CLI" property:set vault="$VAULT" path="$NOTE" name=updated value=2026-07-12 type=date

# Read one back, or remove it:
"$CLI" property:read vault="$VAULT" path="$NOTE" name=status
"$CLI" property:remove vault="$VAULT" path="$NOTE" name=status

# Fallback: read frontmatter, parse, mutate, rewrite
```

### List backlinks for a page
```bash
# CLI
"$CLI" backlinks vault="$VAULT" path="$NOTE"
"$CLI" backlinks vault="$VAULT" path="$NOTE" format=json counts

# Outgoing links are the mirror command:
"$CLI" links vault="$VAULT" path="$NOTE"

# Fallback: ripgrep for wikilink references
rg --type=md "\[\[$(basename "$NOTE" .md)" "$VAULT_ROOT/wiki/"
```

### Query a Bases (.base) file's resolved view
```bash
# CLI — `bases` LISTS base files; `base:query` resolves one to rows.
"$CLI" bases vault="$VAULT"
"$CLI" base:query vault="$VAULT" path="$NOTE" view="<view-name>" format=json

# Omitting `view=` does NOT return all views — it silently resolves the FIRST view
# defined in the file. Always pass `view=` explicitly in scripts.

# `base:views` takes NO file/path option — it reads whatever file is ACTIVE in the GUI and
# errors otherwise ("Active file is not a base file"). It is not scriptable. To enumerate
# view names without depending on GUI state, parse the .base YAML directly — note `name:`
# is nested under each `views:` list item, not on the `- ` line:
grep -E '^[[:space:]]+name:' "$VAULT_ROOT/$NOTE" | sed 's/^ *name: *//'

# Fallback: read the .base file directly; no resolved-view available without Obsidian itself
```

### Vault health primitives (native — prefer these over reimplementing in wiki-lint)
```bash
"$CLI" orphans vault="$VAULT"           # files with no incoming links
"$CLI" unresolved vault="$VAULT"        # dead wikilinks (add verbose for source files)
"$CLI" deadends vault="$VAULT"          # files with no outgoing links
# Append `total` to any of them for a bare count.
```

### Tags + bookmarks
```bash
"$CLI" tags vault="$VAULT"
"$CLI" tags vault="$VAULT" counts sort=count format=json
"$CLI" bookmarks vault="$VAULT"
```

---

## When CLI is NOT the right choice

- **Mobile (iOS Share extension)**: filesystem write into `.raw/` is the only path; CLI is desktop-only.
- **CI / headless ingest jobs**: filesystem with manual frontmatter parsing.
- **Cross-vault operations**: CLI binds to one vault root per invocation; for federation, fall back to filesystem walks.
- **Live edits while Obsidian is mid-save**: rare race; CLI handles it correctly but in pathological cases the v1.7 `wiki-lock.sh` advisory locks (see [skills/wiki-fold/](../wiki-fold/SKILL.md) and `agents/wiki-ingest.md`) should be acquired first.

---

## Cross-reference

- Decision tree: [`wiki/references/transport-fallback.md`](../../wiki/references/transport-fallback.md)
- Legacy MCP options (A/B/C/D): [`skills/wiki/references/mcp-setup.md`](../wiki/references/mcp-setup.md)
- Concurrency policy (v1.7+): [`skills/wiki-ingest/SKILL.md`](../wiki-ingest/SKILL.md) §Concurrency
- Detection script: [`scripts/detect-transport.sh`](../../scripts/detect-transport.sh)

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Detect which Obsidian CLI binaries are installed; check if Obsidian app is running. Read `.vault-meta/transport.json` if it exists. |
| 2 | OBSERVE (int) | Don't be biased toward filesystem fallback when CLI is actually available — verify auto-detection caught what's installed. |
| 3 | LISTEN | If `manual_override: true` is set in transport.json, the user has spoken — preserve their `preferred` and `fallback_chain`. |
| 4 | THINK | Compute the right fallback chain for this environment. CLI > MCP > filesystem; freshness check before recomputing. |
| 5 | CONNECT (lat) | How does this transport choice affect every other skill's write? Six downstream skills depend on this snapshot. |
| 6 | CONNECT (sys) | Schema stability of transport.json matters more than feature richness — consumers parse the JSON via simple shell idioms. |
| 7 | FEEL | Error message when no transport works should tell the user EXACTLY what to do (install CLI, configure MCP, etc.). |
| 8 | ACCEPT | Filesystem fallback is fine. Admit when CLI doesn't exist; don't fabricate a binary that isn't there. |
| 9 | CREATE | Write transport.json atomically (temp + rename). Round-trip `manual_override` every cycle. |
| 10 | GROW | As MCP support matures, auto-detection should cover the deferred tiers. Track that as v1.7.x scope. |
