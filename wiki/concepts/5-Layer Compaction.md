---
address: c-000008
type: concept
title: "5-Layer Compaction"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - context-management
  - claude-code
status: developing
related:
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[Dive into Claude Code]]"
  - "[[DragonScale Memory]]"
---

# 5-Layer Compaction

Claude Code's graduated context degradation pipeline: five shapers that run sequentially before every model call, cheapest first, last resort last.

## The Five Stages

| Stage | Cost | Feature Gate | Trigger |
|:------|:-----|:-------------|
| **Budget Reduction** | Cheapest | Always active | Per-message size caps |
| **Snip** | Low | `HISTORY_SNIP` | Trims older history |
| **Microcompact** | Medium | Always (time-based); optional cache-aware path | Fine-grained compression |
| **Context Collapse** | Medium | `CONTEXT_COLLAPSE` | Read-time virtual projection, non-destructive |
| **Auto-Compact** | Last resort | When all else fails | Full model-generated summary |

## Design Principle

> [!key-insight] Graduated Lazy Degradation
> Cheapest shaper runs first. Each stage invokes only if cheaper ones were insufficient. Auto-Compact (a full LLM call) fires only when all others fail.

This is proactive management, not reactive firefighting: all five shapers run before every model call, not just when context is full.

## Context as Scarce Resource

One of the 13 Claude Code design principles. The binding architectural constraint:
- ~200K tokens: older models
- ~1M tokens: Claude 4.6 series

The entire 5-layer pipeline exists to operate within this constraint across long sessions.

## Turn Pipeline Integration

Stage 4 of the 9-step [[queryLoop Architecture]] pipeline runs all five shapers before the model call at step 5.

## Session Persistence: Chain Patching

Compact boundaries record `headUuid`/`anchorUuid`/`tailUuid`. The session loader patches the message chain at read time. Nothing is destructively edited on disk — append-only JSONL throughout.

**Checkpoints**: file-history checkpoints at `~/.claude/file-history/<sessionId>/` support `--rewind-files`.

## Connection to DragonScale

[[DragonScale Memory]]'s fold operator is the wiki-layer analogue: periodic log rollups that compress history into durable fold artifacts, preserving structure while reducing retrieval cost. Both systems solve the same problem (growing state vs finite window) with graduated, non-destructive compression.

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228)
- [[Dive-into-Claude-Code-README]]

## Related

- [[queryLoop Architecture]] — the loop that runs this pipeline at step 4
- [[Agent Harness Engineering]] — compaction is a core harness component
- [[DragonScale Memory]] — wiki-layer fold/compaction analogue
