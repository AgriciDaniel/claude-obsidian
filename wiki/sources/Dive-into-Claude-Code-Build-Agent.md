---
address: c-000014
type: source
title: "Dive into Claude Code — Build Your Own Agent"
source_file: ".raw/architechtai/doc_build-your-own-agent.md"
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
  - harness-engineering
  - builder-guide
status: ingested
related:
  - "[[Dive into Claude Code]]"
  - "[[Agent Harness Engineering]]"
  - "[[Agent Design Space Decisions]]"
---

# Dive into Claude Code — Build Your Own Agent

Source: `.raw/architechtai/doc_build-your-own-agent.md` | arXiv: 2604.14228 | [[VILA-Lab]]

Not a coding tutorial. A guide to the **design decisions** required when building a production AI agent, derived from Claude Code's architecture. Companion to [[Dive-into-Claude-Code-Architecture]].

## Core Framing

Every production coding agent must answer the same 6 recurring design questions. Claude Code is one set of answers. The guide maps the full decision space so builders can make informed choices for their own context.

The 6 decisions → [[Agent Design Space Decisions]]

## The 3 Meta-Pattern Commitments

Across all 6 decisions, three patterns recur throughout Claude Code's architecture:

1. **Graduated layering over monolithic mechanisms** — safety, context, and extensibility all use stacked independent stages rather than single solutions
2. **Append-only designs favoring auditability over query power** — everything can be reconstructed; nothing is destructively edited
3. **Model judgment within a deterministic harness** — the model decides freely; the harness enforces boundaries. The 1.6%/98.4% split is not accidental

## Key Synthesized Insights

**On reasoning placement:** As frontier models converge in capability (top 3 within 1% on SWE-bench), the operational harness becomes the differentiator, not the model or scaffolding. Heavy scaffolding becomes tech debt if models outgrow it.

**On safety posture:** Defense-in-depth only works when safety layers have *independent* failure modes. Claude Code's layers share an economic constraint (token costs) — commands >50 subcommands bypass security analysis to prevent REPL freeze. Design layers to fail independently.

**On approval fatigue:** Users approve 93% of permission prompts. The solution is not more warnings but restructured boundaries — sandboxing and classifiers that create safe zones for autonomous operation.

**On context:** Context is the binding constraint that shapes nearly every other architectural decision. Lazy loading, deferred tool schemas, summary-only subagent returns — all exist because context is scarce. Design for scarcity from day one.

**On session persistence:** Never restore permissions on resume. Trust is always re-established in the current session. Security state should not persist implicitly across session boundaries.

## Related

- [[Agent Design Space Decisions]] — the 6 decisions with alternatives and trade-offs
- [[Agent Harness Engineering]] — theoretical framing; meta-pattern lives here
- [[queryLoop Architecture]], [[5-Layer Compaction]], [[Deny-First Permission Model]], [[Claude Code Extensibility]], [[Subagent Delegation Architecture]] — the specific answers Claude Code chose
