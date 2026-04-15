---
type: entity
title: "kepano/obsidian-skills"
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - official
  - agent-skills
  - obsidian-creator
status: current
related:
  - "[[LLM Wiki Pattern]]"
sources:
---

# kepano/obsidian-skills

**Type**: Agent Skills (Agent Skills standard)
**URL**: https://github.com/kepano/obsidian-skills
**Author**: **Linus Kepano** — creator of Obsidian + Minimal theme
**Install**: `/plugin marketplace add kepano/obsidian-skills`

## Why This Matters

This repo is from the creator of Obsidian. It:
1. Validates that the Agent Skills standard is the right format for Obsidian AI tools
2. Provides the canonical reference for how to teach Claude about Obsidian-specific syntax
3. Covers Obsidian Bases — a new core Obsidian feature that no other AI project supports yet

## Skills

| Skill | What It Teaches Claude |
|-------|----------------------|
| `obsidian-markdown` | Full Obsidian Flavored Markdown: wikilinks, embeds, callouts, properties, tags |
| `obsidian-bases` | Obsidian Bases (.base files): views, filters, formulas, summaries |
| `json-canvas` | JSON Canvas spec: nodes, edges, groups, connections |
| `obsidian-cli` | Vault management, plugin/theme dev via Obsidian CLI |
| `defuddle` | Extract clean Markdown from web pages — removes ads, nav, clutter |

## defuddle

The `defuddle` skill wraps `defuddle-cli`. When ingesting web content, running defuddle first:
- Strips ads, navigation, footers
- Reduces token usage ~40-60% on typical web pages
- Produces cleaner Markdown that fits better in context window

This is a direct cherry-pick for claude-obsidian's ingest pipeline.

## Multi-Platform

Works with Claude Code, Codex CLI, and OpenCode out of the box.

## Relevance to claude-obsidian

claude-obsidian adopted skills directly from this repo: `defuddle`, `obsidian-markdown`, and `obsidian-bases`.
