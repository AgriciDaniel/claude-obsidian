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

## Recipes (CLI-first; fallback noted inline)

Each recipe shows the CLI form first. If the CLI is unavailable per the detection snapshot, fall through to the noted fallback.

The CLI uses `key=value` arguments — there is no positional vault root argument. The CLI infers the active vault automatically. Use `vault=<name>` only when targeting a non-active vault.

### Read a note
```bash
# CLI
obsidian-cli read path=wiki/concepts/Foo.md

# Fallback: Claude's Read tool with absolute path
# Read $VAULT/wiki/concepts/Foo.md
```

### Create or overwrite a note
```bash
# CLI
obsidian-cli create path=wiki/concepts/Foo.md content="# Foo\n\ncontent here" overwrite

# Fallback: Claude's Write tool with absolute path
# Write $VAULT/wiki/concepts/Foo.md with the desired content string
```

### Append to a note
```bash
# CLI
obsidian-cli append path=wiki/concepts/Foo.md content="additional content"

# Fallback: Read $VAULT/wiki/concepts/Foo.md, append manually, Write back
```

### Search note content (CLI uses Obsidian's own search ranking)
```bash
# CLI
obsidian-cli search query="<query>"
obsidian-cli search query="<query>" path=wiki/   # limit to subfolder

# Fallback: ripgrep
rg --type=md "<query>" "$VAULT/wiki/"
```

### Today's daily note (if Daily Notes plugin is enabled)
```bash
# CLI
obsidian-cli daily:read
obsidian-cli daily:append content="captured at $(date)"

# Fallback: compute path manually
NOTE="$VAULT/wiki/daily/$(date +%Y-%m-%d).md"
```

### Patch a frontmatter property
```bash
# CLI
obsidian-cli property:set name=status value=evergreen path=wiki/concepts/Foo.md

# Fallback: read frontmatter, parse, mutate, rewrite (use mcp__obsidian-vault__update_frontmatter if MCP is configured)
```

### List backlinks for a page
```bash
# CLI
obsidian-cli backlinks path=wiki/concepts/Foo.md

# Fallback: ripgrep for wikilink references
rg --type=md "\[\[Foo" "$VAULT/wiki/"
```

### Open a Bases (.base) file's resolved view
```bash
# CLI
obsidian-cli bases
obsidian-cli base:query file=mybase view="All items" format=json
# (supplements obsidian-bases skill which handles the .base file's YAML)

# Fallback: read the .base file directly; no resolved-view available without Obsidian itself
```

### Tags + bookmarks
```bash
obsidian-cli tags counts sort=count
obsidian-cli bookmarks
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
