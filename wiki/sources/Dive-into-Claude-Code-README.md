---
address: c-000003
type: source
title: "Dive into Claude Code — README"
source_file: ".raw/architechtai/doc_README.md"
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
  - "[[VILA-Lab]]"
  - "[[Dive into Claude Code]]"
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[5-Layer Compaction]]"
  - "[[Deny-First Permission Model]]"
---

# Dive into Claude Code — README

Source: `.raw/architechtai/doc_README.md` | arXiv: 2604.14228 | [[VILA-Lab]] | v2.1.88

## TL;DR

Only 1.6% of Claude Code's codebase is AI decision logic. The other 98.4% is deterministic infrastructure: permission gates, context management, tool routing, and recovery logic. The agent loop is a simple while-loop; the real engineering complexity lives in the systems around it.

## Key Findings

> [!key-insight] Core Thesis
> Agent capability is not a model property. It emerges from the runtime, context layer, execution boundary, tool supply chain, human control surface, and evaluation loop around the model.

- **98.4% infrastructure, 1.6% AI** — the `queryLoop` is a simple AsyncGenerator while-loop
- **5 values → 13 design principles → implementation** — every architectural choice traces back to human authority, safety, reliability, capability, adaptability
- **Defense in depth with shared failure modes** — 7 safety layers, but all share performance constraints; 50+ subcommands bypass security analysis
- **4 CVEs reveal a pre-trust window** — extensions execute before the trust dialog appears
- **The cross-cutting harness resists reimplementation** — the loop is easy to copy; hooks, classifier, compaction, and isolation are not

## Architecture Summary

Claude Code answers four design questions every production coding agent must face:

| Question | Answer |
|:---------|:-------|
| Where does reasoning live? | Model reasons; harness enforces. ~1.6% AI, 98.4% infrastructure. |
| How many execution engines? | One `queryLoop` for all interfaces (CLI, SDK, IDE). |
| Default safety posture? | Deny-first: deny > ask > allow. Strictest rule wins. |
| Binding resource constraint? | ~200K / 1M context window. 5 compaction layers before every model call. |

7 components across 5 architectural layers: User → Interfaces → Agent Loop → Permission System → Tools → State & Persistence → Execution Environment.

## 5 Values → 13 Principles

| Value | Core Idea |
|:------|:----------|
| Human Decision Authority | Principal hierarchy; approval fatigue solved by restructuring boundaries, not more warnings |
| Safety, Security, Privacy | 7 independent safety layers; protects even when human vigilance lapses |
| Reliable Execution | Gather-act-verify loop; graceful recovery |
| Capability Amplification | "A Unix utility, not a product." 98.4% deterministic infrastructure enables the model |
| Contextual Adaptability | CLAUDE.md hierarchy, graduated extensibility, trust trajectories |

The 13 principles: deny-first with human escalation, graduated trust spectrum, defense in depth, externalized programmable policy, context as scarce resource, append-only durable state, minimal scaffolding/maximal harness, values over rules, composable multi-mechanism extensibility, reversibility-weighted risk assessment, transparent file-based config and memory, isolated subagent boundaries, graceful recovery and resilience.

## Key Components

- **[[queryLoop Architecture]]** — AsyncGenerator ReAct while-loop; 9-step pipeline per turn; 5 stop conditions
- **[[5-Layer Compaction]]** — Budget Reduction → Snip → Microcompact → Context Collapse → Auto-Compact; runs before every model call
- **[[Deny-First Permission Model]]** — 7 permission modes; deny always overrides allow; permissions never restored on resume
- **Extensibility** — 4 mechanisms (hooks/skills/plugins/MCP) at graduated context cost; 27 hook events; 10 plugin component types
- **Subagent delegation** — 6 built-in types; sidechain transcripts; only summaries return to parent
- **Session persistence** — append-only JSONL transcripts; chain patching via headUuid/anchorUuid/tailUuid

## Cross-System Comparison

Paper compares Claude Code vs OpenClaw vs Hermes-Agent across 6 design dimensions. Key observation: deployment context (per-user coding CLI vs multi-channel gateway vs multi-deployment messaging agent) drives the rest of the design.

Memory architecture spectrum: file-based Markdown (Claude Code) → file-based + optional vector + dreaming (OpenClaw) → FTS5-indexed + 8 swappable plugin backends (Hermes-Agent).

## New Signals in the Agent Design Space

Six implications for agent builders:
1. Runtime and control plane are first-class design surfaces, not hidden deployment plumbing
2. Context is managed infrastructure: lifecycle, provenance, review, rollback
3. Execution boundary is the safety boundary (permissions, sandbox, credential custody)
4. Tools and skills are a supply chain: registries, allowlists, identity, revocation
5. Humans become managers and verifiers: goals, plans, approvals, interrupts, reviewable diffs
6. Observability must close the improvement loop: traces → evals → prompt/tool repair

## Community Resources Referenced

- [ComeOnOliver/claude-code-analysis](https://github.com/ComeOnOliver/claude-code-analysis) — comprehensive reverse-engineering
- [alejandrobalderas/claude-code-from-source](https://github.com/alejandrobalderas/claude-code-from-source) — 18-chapter ~400-page technical book
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch) — [[Andrej Karpathy]]'s autonomous AI-agent loop on a single GPU
- arXiv 2604.18071 — 70 agent-system projects, recurring design dimensions
- arXiv 2511.09268 — empirical study of 328 Claude Code config files

## Related

- [[VILA-Lab]] — research group behind the paper
- [[Dive into Claude Code]] — paper entity
- [[Agent Harness Engineering]] — overarching concept the paper codifies
- [[queryLoop Architecture]] — the 1.6% AI loop
- [[5-Layer Compaction]] — context management architecture
- [[Deny-First Permission Model]] — safety and permission design
- [[Andrej Karpathy]] — cited for autoresearch project
