---
type: entity
title: "Claudian (YishenTu/claudian)"
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - native-obsidian-plugin
  - embedded-ai
status: current
related:
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Claudian (YishenTu/claudian)

**Type**: Native Obsidian plugin (TypeScript, embedded Claude Code/Codex)
**URL**: https://github.com/YishenTu/claudian
**Install**: BRAT or manual (not yet in community store)

## What It Does

Embeds Claude Code (or Codex CLI) directly inside Obsidian as a sidebar chat. The vault becomes the agent's working directory — all Claude Code tools work natively inside Obsidian.

## Key Features

### Inline Edit with Word-Level Diff
Select text in a note + hotkey → Claude proposes edit with word-level diff preview → one-click apply. Best-in-class inline editing in the Obsidian AI ecosystem.

### Plan Mode (Shift+Tab)
Agent explores and designs before implementing. Presents a plan for approval before any file changes. Mirrors Claude Code's own plan mode.

### @mention System
Type `@` to reference:
- Vault files
- Sub-agents
- MCP servers
- Files in external directories (outside vault)

### Instruction Mode (#)
Add refined custom instructions directly from chat input — persisted for the session.

### MCP Server Integration
Connect external tools via stdio, SSE, or HTTP. Claude manages vault MCP in-app; Codex uses CLI-managed config.

### Multi-Tab Conversations
Multiple chat tabs, conversation history, fork, resume, compact mode.

## Privacy
- No telemetry
- Settings stored in `vault/.claudian/`
- Claude files in `vault/.claude/`
- Transcripts in `~/.claude/projects/`

## Relevance to claude-obsidian
Claudian is a native plugin (different category) but its Plan Mode, @mention, and inline edit patterns could inspire new features in claude-obsidian skills — particularly for the canvas and wiki-query workflows.
