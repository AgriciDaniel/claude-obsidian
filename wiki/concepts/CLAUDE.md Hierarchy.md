---
address: c-000013
type: concept
title: "CLAUDE.md Hierarchy"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - claude-code
  - context-management
status: developing
related:
  - "[[Agent Harness Engineering]]"
  - "[[5-Layer Compaction]]"
  - "[[Deny-First Permission Model]]"
  - "[[Dive into Claude Code]]"
---

# CLAUDE.md Hierarchy

Claude Code's 4-level instruction hierarchy — and the critical design choice that CLAUDE.md delivers user context (probabilistic compliance), not system prompt (deterministic enforcement).

## The 4 Levels

| Level | Path | Scope |
|:------|:-----|:------|
| Managed | `/etc/claude-code/CLAUDE.md` | System-wide (enterprise deployments) |
| User | `~/.claude/CLAUDE.md` | Per-user global |
| Project | `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md` | Per-project |
| Local | `CLAUDE.local.md` | Personal, gitignored |

Higher levels set the baseline. Lower levels specialize. Local is the escape hatch for personal preferences that shouldn't be committed.

## The Critical Design Choice

> [!key-insight] User Context, Not System Prompt
> CLAUDE.md instructions land in the **user context turn**, not the system prompt. This means compliance is probabilistic, not deterministic. Permission rules (deny-first, mode constraints, hooks) provide the deterministic enforcement layer.

Implications:
- You cannot rely on CLAUDE.md alone for safety-critical constraints — use permission rules
- Instructions in CLAUDE.md *can* be overridden by the model in edge cases
- System-level enforcement lives in the [[Deny-First Permission Model]], not in text instructions

## 9 Ordered Context Sources

The full context assembly order (CLAUDE.md hierarchy is source 3):

1. System prompt
2. Environment info
3. CLAUDE.md hierarchy (all 4 levels, outer to inner)
4. Path-scoped rules
5. Auto-memory (LLM-selected from memory files, up to 5)
6. Tool metadata
7. Conversation history
8. Tool results
9. Compact summaries

## File-Based Memory (No Embeddings)

Auto-memory selection: LLM scans memory-file headers and selects up to 5 relevant files per session. No vector DB, no cosine similarity. Fully inspectable and version-controllable.

This is the same pattern as the [[LLM Wiki Pattern]]: file-based, human-readable, LLM-navigated.

## Relevance to claude-obsidian

This vault's `CLAUDE.md` and `wiki/hot.md` operate exactly on this design: CLAUDE.md for project-scope instructions, hot.md as the manual auto-memory equivalent (the 500-word hot cache the model reads first). The 4-level hierarchy maps cleanly onto: managed (N/A), user (`~/.claude/CLAUDE.md`), project (`claude-obsidian/CLAUDE.md`), local (`CLAUDE.local.md`).

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228)
- [[Dive-into-Claude-Code-Architecture]]

## Related

- [[Agent Harness Engineering]] — CLAUDE.md hierarchy is the "contextual adaptability" value in action
- [[Deny-First Permission Model]] — deterministic enforcement layer that CLAUDE.md cannot replace
- [[5-Layer Compaction]] — compact summaries (source 9) are the output of this pipeline
- [[LLM Wiki Pattern]] — analogous: file-based, LLM-navigated, no embeddings
