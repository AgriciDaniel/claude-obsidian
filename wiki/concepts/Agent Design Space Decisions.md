---
address: c-000015
type: concept
title: "Agent Design Space Decisions"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - harness-engineering
  - builder-guide
status: developing
related:
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[5-Layer Compaction]]"
  - "[[Deny-First Permission Model]]"
  - "[[Claude Code Extensibility]]"
  - "[[Subagent Delegation Architecture]]"
  - "[[Dive into Claude Code]]"
---

# Agent Design Space Decisions

Six recurring design decisions every production AI agent must answer, with trade-off alternatives derived from Claude Code's architecture. Claude Code's answers are one point in each space — not the only valid point.

> [!key-insight] The SWE-bench Convergence Argument
> Top 3 frontier models are within 1% of each other on SWE-bench. As model capability converges, the **operational harness** becomes the differentiator — not the model, not the scaffolding. This is the strongest current argument for investing in deterministic infrastructure over model-side improvements.

---

## Decision 1: Where Does Reasoning Live?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Minimal scaffolding** | Claude Code (~1.6% AI logic) | Max model latitude; bets on improving model capability. Harness enforces boundaries. |
| **Explicit state graphs** | LangGraph | Developer controls flow; easier to debug. But constrains the model and requires updates as capabilities improve. |
| **Heavy planning scaffolding** | Devin | Reliable for complex workflows. But scaffolding becomes maintenance burden as models improve. |

**Questions:** How capable is the model? How predictable do workflows need to be? How fast is model capability improving?

---

## Decision 2: What Is Your Safety Posture?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Deny-first + layered enforcement** | Claude Code (7 layers) | Very safe; requires graduated trust to avoid approval fatigue. |
| **Container isolation** | SWE-Agent, OpenHands (Docker) | Strong boundary but coarse-grained — everything inside is allowed; nothing outside is reachable. |
| **VCS rollback** | Aider (git-based) | Lightweight but only protects file changes. Doesn't prevent network requests or data exfiltration. |
| **Approval-only** | Basic chatbots | Simple but behaviorally unreliable at scale — users stop reading prompts. |

**Key:** Layers only provide true defense-in-depth if they have **independent failure modes**. Layers that share an economic constraint (e.g., all depend on token budget) degrade together. See [[Deny-First Permission Model]].

**Questions:** What's the worst the agent could do? Can sandboxing create safe zones to reduce approval friction? Do your safety layers share failure modes?

---

## Decision 3: How Do You Manage Context?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Graduated compaction pipeline** | Claude Code (5 layers) | Preserves most information longest. Complex to implement; compression invisible to users. |
| **Simple truncation** | Many basic agents | Easy to implement. Loses potentially critical early context. |
| **Sliding window** | Some chat apps | Predictable. No semantic awareness of importance. |
| **RAG** | Some IDE integrations | Can access entire codebase. Retrieval quality is the bottleneck; chunks lack surrounding context. |
| **Single summarization** | Some agents | One-pass compression. Can lose critical details. |

**Graduated approach:** Budget reduction (cheap) → history trimming → cache-aware compression → virtual projection → full summarization (last resort). See [[5-Layer Compaction]].

**Questions:** What's your context window size? Do you need long sessions? Can you separate "guidance" context from "working" context?

---

## Decision 4: How Do You Handle Extensibility?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Graduated context-cost mechanisms** | Claude Code (hooks=0, skills=low, plugins=medium, MCP=high) | Different extensions at different costs. Complex but scales. |
| **Single unified API** | Many tool-use frameworks | Simple to understand. Every extension consumes context — limits scale. |
| **Plugin marketplace** | IDE extensions | Rich ecosystem potential. Quality control and security review become bottlenecks. |

**Key:** Not all extensions need to consume context tokens. Hooks (zero cost) handle lifecycle events without touching the context window. See [[Claude Code Extensibility]].

**3 injection points in any agent loop:**
1. `assemble()` — what the model sees (instructions, tool schemas)
2. `model()` — what the model can reach (available tools)
3. `execute()` — whether/how actions run (permission gates, pre/post hooks)

**Questions:** How many tools? Do you need third-party extensions? Can you defer tool schema loading until needed?

---

## Decision 5: How Do Subagents Work?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Isolated context + summary return** | Claude Code (sidechain transcripts) | Prevents context explosion (~7x token cost). Subagents can't share fine-grained state. |
| **Shared context** | Some multi-agent frameworks | Full information sharing. Context fills up fast with N agents. |
| **Message passing** | Actor model systems | Clean boundaries. Requires explicit protocol design. |

**Key:** Subagent sessions cost ~7x tokens of standard sessions. Summary-only returns to parent are essential for context conservation. See [[Subagent Delegation Architecture]].

**Questions:** Do sub-tasks need to see each other's work? How do you prevent N * context_window token consumption? Do subagents inherit parent permissions?

---

## Decision 6: How Do Sessions Persist?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Append-only JSONL** | Claude Code | Auditable, reconstructable, simple. Poor query power. |
| **Database** | Some enterprise agents | Rich queries, fast lookups. Adds infrastructure dependency; reduces transparency. |
| **Stateless** | Most chat APIs | Simplest. No resume, no fork, no audit trail. |

**Key:** Never restore permissions on resume. Trust is always re-established in the current session — security state must not persist implicitly across session boundaries.

---

## The 3 Meta-Pattern Commitments

Across all 6 decisions, three patterns recur:

1. **Graduated layering over monolithic mechanisms** — safety, context, and extensibility all use stacked independent stages
2. **Append-only designs favoring auditability over query power** — everything reconstructable; nothing destructively edited
3. **Model judgment within a deterministic harness** — model decides freely; harness enforces. The 1.6%/98.4% split is not accidental

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228)
- [[Dive-into-Claude-Code-Build-Agent]]

## Related

- [[Agent Harness Engineering]] — the theoretical framing; meta-pattern summary
- [[queryLoop Architecture]] — Decision 1 answer
- [[Deny-First Permission Model]] — Decision 2 answer
- [[5-Layer Compaction]] — Decision 3 answer
- [[Claude Code Extensibility]] — Decision 4 answer
- [[Subagent Delegation Architecture]] — Decision 5 answer
