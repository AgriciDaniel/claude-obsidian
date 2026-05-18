---
type: entity
title: "Nexus (ProfSynapse/claudesidian-mcp)"
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - obsidian-plugin
  - mcp-server
  - native-plugin
status: current
related:
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Nexus (formerly Claudesidian MCP)

**Type**: Native Obsidian plugin + MCP bridge
**URL**: https://github.com/ProfSynapse/claudesidian-mcp
**Current name**: Nexus MCP for Obsidian
**Install**: `.obsidian/plugins/nexus/`

## What It Does

Full Obsidian plugin with two modes:
1. **Native chat inside Obsidian** — connect any AI provider
2. **MCP bridge** — expose vault to Claude Desktop, Claude Code, Codex CLI, Gemini CLI, Cursor, Cline

## Key Features

- **Workspace memory** — persistent context across sessions stored as JSONL, automatically included in Obsidian Sync
- **Task management** — projects, tasks, blockers, dependencies tracked within vault
- **Semantic search** — search notes + past conversations by meaning
- **Inline editing** — edit selected text in notes
- **PDF + audio → Markdown** — conversion on right-click or auto-on-add
- **Web page capture** — open URL in Obsidian, save as Markdown/PNG/PDF
- **Mobile support** — native chat works on iOS/Android
- **Two-tool architecture** — dedicated tools for read vs write actions

## Storage Architecture

Data stored as JSONL files in `.obsidian/plugins/nexus/data/`. This is included in Obsidian Sync automatically (unlike the `.nexus/` folder of v1). SQLite cache is local-only, rebuilt from JSONL on each device.

## Relevance to claude-obsidian

Nexus is in a different category — it's a native TypeScript Obsidian plugin, not a Claude Code skill plugin. The two don't compete directly, but its workspace memory and task management patterns are cherry-pickable.

## Cherry-Picks for claude-obsidian

- [[cherry-picks#11. obsidian-memory-mcp Integration]] (different implementation, same concept)
