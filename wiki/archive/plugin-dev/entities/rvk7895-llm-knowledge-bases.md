---
type: entity
title: "rvk7895/llm-knowledge-bases"
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - llm-wiki-pattern
  - deep-research
status: current
related:
  - "[[LLM Wiki Pattern]]"
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
  - "[[Andrej Karpathy]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# rvk7895/llm-knowledge-bases

**Type**: Claude Code plugin (Marketplace)
**URL**: https://github.com/rvk7895/llm-knowledge-bases
**Install**: `/plugin marketplace add rvk7895/llm-knowledge-bases`

## What It Does

Turns raw research material into an LLM-maintained Obsidian wiki with multi-depth querying and rich output formats. Adds a deep research pipeline with parallel agents on top of the Karpathy pattern.

## Key Innovations

### 3-Depth Query System
- **Quick** — answers from wiki indexes and summaries only (minimal reads)
- **Standard** — cross-references full wiki, supplements with web search
- **Deep** — multi-agent parallel web search pipeline

### Output Formats
Beyond Markdown: Marp slides, matplotlib charts. All outputs saved to `output/` and optionally filed back into wiki.

### Skills Set
| Skill | Purpose |
|-------|---------|
| `/kb-init` | One-time setup |
| `/kb compile` | Raw → wiki |
| `/kb query` | Query with depth |
| `/kb lint` | Health check |
| `/kb evolve` | Maintenance pass |
| `/research <topic>` | Structured research outline |
| `/research-deep` | Parallel agents per outline item |
| `/research-report` | Compile deep results → Markdown |

### X/Twitter Integration
Via Smaug tool (`npm install -g @steipete/bird`). Ingests tweets, threads, bookmarks from X/Twitter by pasting URL. Uses session cookies (read-only, personal use).

## Attribution
Built on Karpathy pattern + Weizhena's Deep Research skills adapted for the research pipeline.

## Cherry-Picks for claude-obsidian

- [[cherry-picks#5. Multi-Depth Query Modes]]
- [[cherry-picks#10. Marp Presentation Output]]
