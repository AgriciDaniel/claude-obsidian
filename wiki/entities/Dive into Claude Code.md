---
address: c-000005
type: entity
title: "Dive into Claude Code"
arxiv: "2604.14228"
authors:
  - "Jiacheng Liu"
  - "Xiaohan Zhao"
  - "Xinyi Shang"
  - "Zhiqiang Shen"
affiliation: "VILA-Lab"
subject: "Claude Code v2.1.88"
license: "CC BY-NC-SA 4.0"
created: 2026-06-05
updated: 2026-06-05
tags:
  - entity
  - paper
  - agent-architecture
  - claude-code
status: current
related:
  - "[[VILA-Lab]]"
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[5-Layer Compaction]]"
  - "[[Deny-First Permission Model]]"
---

# Dive into Claude Code

arXiv 2604.14228 | [[VILA-Lab]] | CC BY-NC-SA 4.0

> A comprehensive source-level architectural analysis of Claude Code (v2.1.88, ~1,900 TypeScript files, ~512K lines of code), combined with a curated collection of community analyses, a design-space guide for agent builders, and cross-system comparisons.

## What It Is

A research paper and companion repository that dissects Claude Code's architecture at source level and distills it into actionable design guidance. Primary contribution: framing [[Agent Harness Engineering]] as a discipline with named primitives, tracing 5 human values through 13 design principles to specific implementation choices.

## Key Stats Analyzed

`1,884 files` · `~512K lines` · `v2.1.88` · `7 safety layers` · `5 compaction stages` · `54 tools` · `27 hook events` · `4 extension mechanisms` · `7 permission modes`

## Core Finding

98.4% of Claude Code is deterministic infrastructure. 1.6% is AI decision logic. The `queryLoop` is a simple while-loop; the real complexity lives in the harness around it. See [[Agent Harness Engineering]].

## Documents (Ingested into Wiki)

| File | Status | Wiki Page |
|:-----|:-------|:----------|
| `doc_README.md` | ingested | [[Dive-into-Claude-Code-README]] |
| `doc_architecture.md` | ingested | [[Dive-into-Claude-Code-Architecture]] |
| `doc_build-your-own-agent.md` | ingested | [[Dive-into-Claude-Code-Build-Agent]] |
| `doc_related-resources.md` | ingested | [[Dive-into-Claude-Code-Related-Resources]] |
| `doc_agent-design-space-source-notes_zh.md` | pending | — |

## Design Space Coverage

The paper covers 6 agent builder decisions: reasoning placement, safety posture, context management, extensibility, subagent architecture, session persistence.

## Cross-System Comparison

Claude Code vs OpenClaw vs Hermes-Agent across 6 dimensions. Key insight: deployment context (per-user coding CLI vs multi-channel gateway vs multi-deployment agent) drives the entire architectural shape.

## Related

- [[VILA-Lab]] — research group
- [[Agent Harness Engineering]] — overarching concept the paper codifies
- [[queryLoop Architecture]] — the agent loop itself
- [[5-Layer Compaction]] — context architecture
- [[Deny-First Permission Model]] — safety architecture
- [[Andrej Karpathy]] — cited for karpathy/autoresearch
