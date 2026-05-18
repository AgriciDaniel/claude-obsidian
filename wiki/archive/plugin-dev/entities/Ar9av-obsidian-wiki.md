---
type: entity
title: "Ar9av/obsidian-wiki"
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - llm-wiki-pattern
  - multi-agent
status: current
related:
  - "[[LLM Wiki Pattern]]"
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Ar9av/obsidian-wiki

**Type**: Claude Code plugin (skill-based)
**URL**: https://github.com/Ar9av/obsidian-wiki
**Pattern**: Karpathy LLM Wiki
**Unique claim**: Works with any AI coding agent via `setup.sh`

## What It Does

Framework for AI agents to build and maintain an Obsidian wiki using the Karpathy LLM Wiki pattern. The key differentiator: a single `setup.sh` deploys the skills to 7 different agents simultaneously.

## Agent Compatibility Matrix

| Agent | Bootstrap | Skills Dir |
|-------|-----------|-----------|
| Claude Code | CLAUDE.md | `.claude/skills/` |
| Cursor | `.cursor/rules/obsidian-wiki.mdc` | `.cursor/skills/` |
| Windsurf | `.windsurf/rules/` | `.windsurf/skills/` |
| Codex (OpenAI) | AGENTS.md | `~/.codex/skills/` |
| Gemini/Antigravity | GEMINI.md | `~/.gemini/antigravity/skills/` |
| OpenClaw | AGENTS.md | `.agents/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` | — |

## Key Innovations

### Delta Tracking Manifest
`.manifest.json` tracks every ingested source: path, hash, timestamp, which wiki pages produced. Only processes new/changed files. Solves the "re-ingest everything" problem.

### 4-Stage Pipeline
1. **Ingest** — reads source (PDF, JSONL, text, conversation exports, images)
2. **Extract** — pulls concepts, entities, claims, relationships, open questions
3. **Resolve** — merges new knowledge against existing wiki (no duplication)
4. **Schema** — structure emerges from sources, not predefined

### Vision Support
Images, screenshots, whiteboard photos ingestable with vision-capable model. Each page gets 1-2 sentence `summary:` in frontmatter for preview without opening.

## Cherry-Picks for claude-obsidian

- [[cherry-picks#4. Delta Tracking Manifest]]
- [[cherry-picks#6. /wiki-ingest Vision Support]]
- [[cherry-picks#9. Multi-Agent Compatibility (Cursor, Windsurf, Codex)]]
- [[cherry-picks#13. Schema-Emergent Vault Mode]]
