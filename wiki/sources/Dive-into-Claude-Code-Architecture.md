---
address: c-000010
type: source
title: "Dive into Claude Code — Architecture"
source_file: ".raw/architechtai/doc_architecture.md"
authors:
  - "Jiacheng Liu"
  - "Xiaohan Zhao"
  - "Xinyi Shang"
  - "Zhiqiang Shen"
affiliation: "VILA-Lab"
arxiv: "2604.14228"
version: "Claude Code v2.1.88"
created: 2026-06-05
updated: 2026-06-05
tags:
  - source
  - agent-architecture
  - claude-code
  - harness-engineering
status: ingested
related:
  - "[[Dive into Claude Code]]"
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[5-Layer Compaction]]"
  - "[[Deny-First Permission Model]]"
  - "[[Claude Code Extensibility]]"
  - "[[Subagent Delegation Architecture]]"
  - "[[CLAUDE.md Hierarchy]]"
---

# Dive into Claude Code — Architecture

Source: `.raw/architechtai/doc_architecture.md` | arXiv: 2604.14228 | [[VILA-Lab]]

Technical deep dive companion to [[Dive-into-Claude-Code-README]]. Covers the 7-component system structure, 5-layer subsystem decomposition, 7 safety layers, 9-step turn pipeline, extensibility mechanisms, context/memory architecture, subagent delegation, and session persistence.

## 7-Component System Structure

1. **User** — submits prompts, approves permissions, reviews output
2. **Interfaces** — Interactive CLI, headless CLI (`claude -p`), Agent SDK, IDE/Desktop/Browser
3. **Agent Loop** — `queryLoop` async generator in `query.ts`
4. **Permission System** — deny-first rules + auto-mode ML classifier + hook interception
5. **Tools** — up to 54 built-in + MCP-provided, assembled via `assembleToolPool`
6. **State & Persistence** — append-only JSONL transcripts, prompt history, subagent sidechains
7. **Execution Environment** — shell (with sandbox), filesystem, web fetching, MCP connections

All interfaces (interactive CLI, headless, SDK, IDE) converge on the same `queryLoop`. `QueryEngine` is a conversation wrapper, not the execution engine.

## 5-Layer Subsystem Decomposition (21 Subsystems)

| Layer | Responsibility | Key Components |
|:------|:---------------|:---------------|
| Surface | Entry points & rendering | CLI, headless, SDK, IDE (React + Ink terminal UI) |
| Core | Context assembly & agent loop | `queryLoop`, 5-stage compaction pipeline, subagent spawning |
| Safety/Action | Permissions & tools | 7 permission modes, auto-mode classifier, 27 hook events, tool pool, shell sandbox |
| State | Runtime state & persistence | JSONL transcripts, CLAUDE.md hierarchy, auto-memory, sidechain files |
| Backend | Execution environments | Shell execution, MCP connections (7 transport types), 42 tool subdirectories |

## Key Architectural Decisions

**CLAUDE.md is user context, not system prompt.** This is the critical design choice for compliance: user context = probabilistic compliance; system prompt = deterministic enforcement. Permission rules provide the deterministic layer. See [[CLAUDE.md Hierarchy]].

**File-based memory with no embeddings.** LLM scans memory-file headers and selects up to 5 relevant files. Fully inspectable and version-controllable.

**Sidechain transcripts.** Each subagent writes its own `.jsonl`. Only summaries return to parent. Multi-instance coordination via POSIX `flock()` — zero external dependencies. See [[Subagent Delegation Architecture]].

**Append-only JSONL favors auditability over query power.** Every event is human-readable and reconstructable without specialized tooling.

## Compaction Stage Feature Gates

| Stage | Feature Gate |
|:------|:------------|
| Budget Reduction | Always active |
| Snip | `HISTORY_SNIP` |
| Microcompact | Always (time-based); optional cache-aware path |
| Context Collapse | `CONTEXT_COLLAPSE` |
| Auto-Compact | When all else fails |

See [[5-Layer Compaction]] for full detail.

## Related Concept Pages

- [[Agent Harness Engineering]] — the 98.4/1.6 framing
- [[queryLoop Architecture]] — 9-step pipeline, 2 execution paths, 5 stop conditions
- [[5-Layer Compaction]] — graduated context degradation
- [[Deny-First Permission Model]] — 7 modes, 7 layers, authorization pipeline
- [[Claude Code Extensibility]] — 4 mechanisms × 3 injection points
- [[Subagent Delegation Architecture]] — SkillTool vs AgentTool, isolation modes, sidechains
- [[CLAUDE.md Hierarchy]] — 4 levels, user context vs system prompt
