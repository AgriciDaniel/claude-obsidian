---
type: reference
title: "Transport Fallback Decision Tree"
status: evergreen
related:
  - "[[wiki-cli]]"
  - "[[mcp-setup]]"
updated: 2026-05-17
---

# Transport Fallback Decision Tree

claude-obsidian v1.7+ supports four ways to read and mutate vault notes. This document is the canonical decision tree skills consult when picking one.

## Quick reference

```
                  ┌─────────────────────────┐
                  │ I need to read/write    │
                  │ a wiki note             │
                  └────────────┬────────────┘
                               │
                               ▼
         ┌─────────────────────────────────────────────┐
         │ Read .vault-meta/transport.json             │
         │ (if missing, run scripts/detect-transport.sh)│
         └─────────────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
   preferred = "cli"               preferred = "filesystem"
              │                                 │
              ▼                                 ▼
   ┌──────────────────┐              ┌────────────────────┐
   │ obsidian-cli <op>│              │ Read/Write/Edit    │
   │                  │              │ tools with absolute│
   │ Falls through on │              │ vault paths        │
   │ binary error to  │              │                    │
   │ filesystem.      │              │ Final floor.       │
   └──────────────────┘              └────────────────────┘
```

## The fallback chain (highest to lowest precedence)

| # | Transport | When preferred | Strengths | Weaknesses |
|---|-----------|----------------|-----------|------------|
| 1 | **`cli`** | Desktop with Obsidian 1.12+ installed. Auto-detected by `scripts/detect-transport.sh`. | No MCP, no TLS, no plugins. Subprocess speed. Loud failure on missing binary. | Desktop-only. Single-vault per invocation. |
| 2 | **`mcp-obsidian`** | When the user has the Local REST API plugin + an MCP server configured. Not auto-detected in v1.7 — user must edit `transport.json` by hand or override per call. | Persistent connection; rich tools (`mcp__obsidian-vault__*`); patch_note primitives. | Requires plugin install + TLS bypass for self-signed cert; reentrancy risk in self-MCP-calls. |
| 3 | **`mcpvault`** | When user has `@bitbonsai/mcpvault` configured. Not auto-detected in v1.7. | No Obsidian plugin needed; BM25 search built in. | Filesystem-based — no Obsidian-native features (live render, hot reload). |
| 4 | **`filesystem`** | Always available. Final floor. Used when nothing above is. | Zero setup. Works on any machine with the repo. | No Obsidian-aware features (no resolved Bases, no daily-note logic, no backlink graph). |

## When skills should consult this tree

Any skill that mutates a vault file should follow this pattern at the top:

```python
# Pseudocode for any vault-mutating skill
transport = read_json(".vault-meta/transport.json")  # auto-created on first run
match transport["preferred"]:
    case "cli":
        result = bash(f'obsidian-cli {operation} "{vault_root}" "{path}"')
    case "mcp-obsidian" | "mcpvault":
        result = mcp_call(operation, path)
    case "filesystem" | _:
        result = read_or_write_tool(absolute_path)
```

Skills covered by this policy in v1.7:
- `wiki-ingest` — page creation, frontmatter mutation, manifest updates
- `wiki-query` — page reads (when standard or deep mode pulls full text)
- `wiki-lint` — bulk reads for orphan/link analysis
- `wiki-fold` — fold-page writes
- `save` — session-note writes
- `autoresearch` — source + concept page writes during the research loop

Skills that explicitly bypass the tree (always use direct filesystem):
- `wiki-cli` — this skill IS the CLI wrapper; recursion is meaningless
- `defuddle` — operates on HTTP-fetched content, not vault state
- `obsidian-markdown` / `obsidian-bases` / `canvas` — reference skills, do not mutate the vault

## Refresh policy

`scripts/detect-transport.sh` rewrites `.vault-meta/transport.json` only if the existing snapshot is older than 7 days (`STALE_AFTER_DAYS=7`). To force a refresh after installing/uninstalling the Obsidian CLI:

```bash
bash scripts/detect-transport.sh --force
```

## Manual override

If you have an MCP transport configured (or any other transport not in the auto-detected set) and want claude-obsidian to use it as preferred:

1. Open `.vault-meta/transport.json` in any editor.
2. Set `"preferred": "mcp-obsidian"` (or `"mcpvault"`, or any custom value).
3. Set `"fallback_chain": ["mcp-obsidian", "filesystem"]` (or your preferred order).
4. Add a `"manual_override": true` field at the top level so the detection script knows not to clobber your `preferred` + `fallback_chain` on next run.

The detection script (`scripts/detect-transport.sh`, v1.8.2+) parses the existing transport.json BEFORE running auto-detection. When `manual_override` is `true`, the script re-runs auto-detection only to refresh `available.cli.*` and `available.cli.obsidian_app_running` (so the human log line stays accurate), but preserves the user's `preferred` and `fallback_chain` choices across every cycle — including `--force` runs and post-staleness refreshes. The `manual_override` field itself round-trips through the snapshot, so the override survives indefinitely.

To disable the override later, edit the file and either set `"manual_override": false` or delete the field; the next detection pass will recompute `preferred` from auto-detection.

## See also

- Detection script: [`scripts/detect-transport.sh`](../../scripts/detect-transport.sh)
- CLI recipe reference: [`skills/wiki-cli/SKILL.md`](../../skills/wiki-cli/SKILL.md)
- Legacy 4-option MCP setup: [`skills/wiki/references/mcp-setup.md`](../../skills/wiki/references/mcp-setup.md) (still authoritative for MCP configuration steps)
