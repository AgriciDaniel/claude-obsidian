---
type: entity
title: "ballred/obsidian-claude-pkm"
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - llm-wiki-pattern
  - pkm
  - productivity
status: current
related:
  - "[[LLM Wiki Pattern]]"
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# ballred/obsidian-claude-pkm

**Type**: Claude Code plugin (skill-based PKM system)
**URL**: https://github.com/ballred/obsidian-claude-pkm
**Version**: 3.1
**Tagline**: "Not another PKM starter kit. An execution system."

## What It Does

Connects a 3-year vision cascade to daily task execution, using Claude as an accountability partner. Every layer is linked — daily notes surface the weekly ONE Big Thing, which links to active projects, which link to yearly goals.

## Goal Cascade

```
3-Year Vision → Yearly Goals → Projects → Monthly Goals → Weekly Review → Daily Tasks
```

Each layer has a dedicated skill: `/goal-tracking`, `/project`, `/monthly`, `/weekly`, `/daily`, `/review`.

## Key Innovations

### Auto-Commit via PostToolUse Hook
Every Write/Edit tool call triggers `git add -A && git commit` automatically. Vault is always versioned.

### /adopt Command
Scans an existing Obsidian vault, detects its organization method (PARA, Zettelkasten, LYT, plain folders), maps folders interactively to the PKM layers, generates config files. Non-destructive.

### 4 Specialized Agents with Memory
- `goal-aligner` — audits activity vs. stated goals, flags misalignment
- `weekly-reviewer` — facilitates 3-phase weekly review, learns reflection style
- `note-organizer` — fixes broken links, consolidates duplicates
- `inbox-processor` — GTD-style inbox processing

Uses `memory: project` so agents remember patterns across sessions.

### Productivity Coach Output Style
`/output-style coach` transforms Claude into an accountability partner — challenges assumptions, asks powerful questions, points out goal-action misalignment.

## Architecture

Zero dependencies (bash + markdown only). Path-specific rules loaded contextually. Session init surfaces ONE Big Thing, active project count, days since last review.

## Cherry-Picks for claude-obsidian

- [[cherry-picks#2. Auto-Commit PostToolUse Hook]]
- [[cherry-picks#7. /adopt — Import Existing Vault]]
- [[cherry-picks#8. Productivity Wrapper (Daily/Weekly Reviews)]]
