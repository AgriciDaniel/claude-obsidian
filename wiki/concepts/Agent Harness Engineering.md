---
address: c-000006
type: concept
title: "Agent Harness Engineering"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - harness
  - infrastructure
status: developing
related:
  - "[[Dive into Claude Code]]"
  - "[[queryLoop Architecture]]"
  - "[[5-Layer Compaction]]"
  - "[[Deny-First Permission Model]]"
  - "[[LLM Wiki Pattern]]"
---

# Agent Harness Engineering

The discipline of designing the deterministic infrastructure layer around an AI model: permissions, context management, tool routing, recovery logic, hooks, and observability — as opposed to the model loop itself.

> [!key-insight] Core Claim
> Agent capability is not a model property. It emerges from the runtime, context layer, execution boundary, tool supply chain, human control surface, and evaluation loop around the model.

## The 98.4 / 1.6 Split

From Claude Code v2.1.88 source analysis (~512K lines):
- 1.6% is AI decision logic (the `queryLoop` while-loop)
- 98.4% is deterministic infrastructure

As models converge in raw capability, the harness becomes the differentiator. The loop is easy to copy; the cross-cutting harness is not.

> "The moat is the harness, not the model." — Han HELOIR YAN (Medium, post-leak analysis, Apr 2026)

Independent validation: claw-code (Rust reimplementation) reached 179K stars in 9 days — fastest repo in GitHub history to 100K. Multiple independent post-leak analysts arrived at the same 98.4/1.6 framing from different directions.

## What Makes the Harness Hard to Reimplement

- **Hooks** — 27 events, 4 execution types; programmable policy externalization
- **Auto-mode classifier** — separate LLM sidecar with two-stage fast-filter + chain-of-thought
- **5-layer compaction** — graduated context degradation before every model call
- **Process isolation** — worktree + sidechain transcript architecture for subagents
- **Permission system** — deny-first with 7 modes, session-scoped state, never-restore-on-resume

## The SWE-bench Convergence Argument

Top 3 frontier models are within 1% of each other on SWE-bench. As model capability converges, the operational harness becomes the differentiator — not the model, not the scaffolding. Heavy scaffolding added today becomes tech debt when models outgrow it. The investment case for deterministic infrastructure over model-side improvements has never been stronger.

## Three Meta-Pattern Commitments

Across all design decisions, three patterns recur throughout Claude Code's architecture:

1. **Graduated layering over monolithic mechanisms** — safety, context, and extensibility all use stacked independent stages rather than single solutions
2. **Append-only designs favoring auditability over query power** — everything reconstructable; nothing destructively edited
3. **Model judgment within a deterministic harness** — model decides freely; harness enforces boundaries. The 1.6%/98.4% split is not accidental

## Six Design Decisions Every Production Agent Must Make

| Decision | The Core Question | Claude Code's Answer |
|:---------|:------------------|:--------------------|
| Reasoning placement | How much logic in the model vs. harness? | Minimal scaffolding; harness enforces |
| Safety posture | How do you prevent harmful actions? | Deny-first, 7 independent layers |
| Context management | What does the model see? | 5-layer graduated compaction |
| Extensibility | How do extensions plug in? | 4 mechanisms × 3 injection points |
| Subagent architecture | Shared or isolated context? | Isolated + summary-only return |
| Session persistence | What carries over? | Append-only JSONL; never restore permissions |

Full alternatives and trade-offs for each decision: [[Agent Design Space Decisions]]

## Six Design Implications (2026 Agent Ecosystem)

1. Runtime and control plane are first-class design surfaces, not hidden deployment plumbing
2. Context is managed infrastructure: lifecycle, provenance, review, rollback
3. Execution boundary is the safety boundary (permissions, sandbox, credential custody)
4. Tools and skills are a supply chain: registries, allowlists, identity, revocation
5. Humans become managers and verifiers: goals, plans, approvals, interrupts, reviewable diffs
6. Observability must close the improvement loop: traces → evals → prompt/tool repair

## Named Primitives

Addy Osmani (citing Claude Code as the canonical mature example) names: filesystem/git state, sandboxes, AGENTS.md memory, compaction, planning loops, hooks.

## Connection to LLM Wiki Pattern

The [[LLM Wiki Pattern]] is itself a harness: the wiki (file-based memory, ingest pipeline, index, hot cache, log) is infrastructure around the LLM, not a property of the LLM. The same 98.4/1.6 framing applies.

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228) — primary source codifying this as a discipline
- [[Dive-into-Claude-Code-README]] — overview and design-space scan
- [[Dive-into-Claude-Code-Build-Agent]] — practitioner guide; source of the 3 meta-pattern and SWE-bench convergence framing

## Related

- [[Agent Design Space Decisions]] — the 6 decisions with alternative approaches and trade-offs
- [[queryLoop Architecture]] — the 1.6% loop that the harness wraps
- [[5-Layer Compaction]] — harness component: context management
- [[Deny-First Permission Model]] — harness component: safety posture
- [[Claude Code Extensibility]] — harness component: extensibility
- [[Subagent Delegation Architecture]] — harness component: multi-agent architecture
- [[LLM Wiki Pattern]] — analogous pattern: wiki as infrastructure around LLM
