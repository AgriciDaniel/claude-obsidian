---
address: c-000007
type: concept
title: "queryLoop Architecture"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - claude-code
status: developing
related:
  - "[[Agent Harness Engineering]]"
  - "[[Dive into Claude Code]]"
  - "[[5-Layer Compaction]]"
  - "[[Deny-First Permission Model]]"
---

# queryLoop Architecture

The single `queryLoop` AsyncGenerator at the core of Claude Code — a ReAct-pattern while-loop that serves all interfaces (CLI, SDK, IDE) from one execution engine.

## Design Choice

One loop, all interfaces. Not separate implementations per entry point. The harness around the loop (not the loop itself) is the differentiator. See [[Agent Harness Engineering]].

## The Loop Pattern

```
assemble context → call model → dispatch tools → check permissions → execute → repeat
```

Implemented as an `AsyncGenerator` yielding streaming events.

## 9-Step Pipeline Per Turn

1. Settings resolution
2. State init
3. Context assembly
4. Five pre-model compaction shapers (see [[5-Layer Compaction]])
5. Model call
6. Tool dispatch
7. Permission gate (see [[Deny-First Permission Model]])
8. Tool execution
9. Stop condition check

## 5-Layer Subsystem Decomposition

The queryLoop sits in the **Core** layer of a 5-layer, 21-subsystem stack:

| Layer | Key Components |
|:------|:---------------|
| Surface | CLI, headless, SDK, IDE (React + Ink) |
| **Core** | **`queryLoop`, compaction pipeline, subagent spawning** |
| Safety/Action | 7 permission modes, auto-mode classifier, 27 hook events, tool pool |
| State | JSONL transcripts, CLAUDE.md hierarchy, auto-memory, sidechain files |
| Backend | Shell execution, MCP connections (7 transport types), 42 tool subdirectories |

## Two Execution Paths

- **StreamingToolExecutor** — begins executing tools as they stream in (latency optimization)
- **Fallback `runTools`** — classifies tools as concurrent-safe vs exclusive before executing

## Recovery Mechanisms

- Max output token escalation (3 retries)
- Reactive compaction (once per turn)
- Prompt-too-long handling
- Streaming fallback
- Fallback model

## 5 Stop Conditions

1. No tool use
2. Max turns reached
3. Context overflow
4. Hook intervention
5. Explicit abort

## Scale (v2.1.88)

`54 tools` in the registry · `27 hook events` across 5 categories · `4 extension mechanisms`

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228)
- [[Dive-into-Claude-Code-README]]

## Related

- [[Agent Harness Engineering]] — the 98.4% infrastructure wrapping this loop
- [[5-Layer Compaction]] — runs at step 4 before every model call
- [[Deny-First Permission Model]] — applied at step 7 (permission gate)
