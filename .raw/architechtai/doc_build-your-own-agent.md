[Back to Main README](../README.md)

# Build Your Own AI Agent: A Design Space Guide

> This is not a coding tutorial. This is a guide to the **design decisions** you must make when building a production AI agent system, derived from the architectural analysis of Claude Code.

Every production coding agent must answer the same recurring design questions. Claude Code is one set of answers. This guide maps the decision space so you can make your own informed choices.

---

## Decision 1: Where Does Reasoning Live?

**The question:** How much decision-making do you put in the model vs. in your harness code?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Minimal scaffolding** | Claude Code (~1.6% AI logic) | Model has maximum latitude; harness enforces boundaries. Bets on model capability improving over time. |
| **Explicit state graphs** | LangGraph | Developer controls flow; easier to debug and predict. But constrains the model and requires updating as capabilities improve. |
| **Heavy planning scaffolding** | Devin | Multi-step planners + task trackers. More reliable for complex workflows, but the scaffolding itself becomes maintenance burden. |

**Key insight from Claude Code:** As frontier models converge in capability (top 3 within 1% on SWE-bench), the **operational harness becomes the differentiator**, not the model or the scaffolding. Investing in deterministic infrastructure (context management, safety, recovery) may yield greater reliability than adding planning constraints.

**Questions to ask yourself:**
- How capable is the model you're targeting? More capable models need less scaffolding.
- How predictable do your workflows need to be? Regulated domains may need explicit graphs.
- How fast is the model capability improving? Heavy scaffolding becomes tech debt if models outgrow it.

---

## Decision 2: What Is Your Safety Posture?

**The question:** How do you prevent the agent from doing harmful things?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Deny-first with layered enforcement** | Claude Code (7 independent layers) | Very safe, but can create approval fatigue (93% of prompts approved without review). Requires graduated trust mechanisms. |
| **Container isolation** | SWE-Agent, OpenHands (Docker) | Strong boundary, but coarse-grained. Everything inside the container is allowed; nothing outside is reachable. |
| **VCS rollback** | Aider (git-based) | Lightweight, but only protects against file changes. Doesn't prevent network requests, data exfiltration, or shell side effects. |
| **Approval-only** | Basic chatbots | Simple but behaviorally unreliable at scale. Users stop reading prompts. |

**Key insight from Claude Code:** Defense-in-depth only works when safety layers have **independent failure modes**. Claude Code's layers share an economic constraint (token costs) -- commands exceeding 50 subcommands bypass security analysis entirely. Design your layers to fail independently.

**Key insight on approval fatigue:** Users approve 93% of permission prompts. The solution is not more warnings but **restructured boundaries** -- sandboxing and classifiers that create safe zones for autonomous operation.

**Questions to ask yourself:**
- What's the worst thing your agent could do? (Delete production data? Send emails? Exfiltrate code?)
- Can you use sandboxing to reduce the number of decisions users must make?
- Do your safety layers share failure modes (e.g., all depend on token budget)?

---

## Decision 3: How Do You Manage Context?

**The question:** The context window is finite. How do you decide what the model sees?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Graduated compaction pipeline** | Claude Code (5 layers) | Preserves the most information for the longest time. Complex to implement and debug. Compression is invisible to users. |
| **Simple truncation** | Many basic agents | Easy to implement. But loses potentially critical early context. |
| **Sliding window** | Some chat applications | Predictable behavior. But no semantic awareness of what's important. |
| **RAG (retrieval-augmented)** | Some IDE integrations | Can access entire codebase. But retrieval quality is a bottleneck, and retrieved chunks may lack surrounding context. |
| **Single summarization** | Some agents | One summary pass. But a single compression can lose critical details. |

**Key insight from Claude Code:** Context is the **binding constraint** that shapes nearly every other architectural decision. Lazy loading, deferred tool schemas, summary-only subagent returns, and per-tool-result budgets all exist because context is scarce. Design for context scarcity from day one.

**The graduated approach:** Apply the least disruptive compression first. Budget reduction (cheap) → History trimming (cheap) → Cache-aware compression (medium) → Virtual projection (medium) → Full summarization (expensive, last resort).

**Questions to ask yourself:**
- What's your context window size? This determines how aggressive your compression needs to be.
- Do you need to support long sessions (hours of work)? Single-pass truncation won't survive.
- Can you separate "guidance" context (instructions) from "working" context (conversation)?

---

## Decision 4: How Do You Handle Extensibility?

**The question:** How do external tools, custom instructions, and user customizations plug into your system?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Graduated context-cost mechanisms** | Claude Code (hooks=0, skills=low, plugins=medium, MCP=high) | Different extensions at different costs. Complex to manage, but scales. |
| **Single unified API** | Many tool-use frameworks | Simple to understand. But every extension consumes context, limiting scalability. |
| **Plugin marketplace** | IDE extensions | Rich ecosystem potential. But quality control and security review become bottlenecks. |

**Key insight from Claude Code:** Not all extensions need to consume context tokens. Hooks (zero cost) handle lifecycle events without touching the context window. Skills (low cost) inject only when relevant. Reserve high-context-cost mechanisms (MCP) for genuinely new tool surfaces.

**The three injection points:** Every agent loop has three places where extensions can intervene:
1. **assemble()** -- What the model sees (instructions, tool schemas)
2. **model()** -- What the model can reach (available tools)
3. **execute()** -- Whether/how an action runs (permission gates, pre/post hooks)

**Questions to ask yourself:**
- How many tools will your agent need to support? More tools = more context pressure.
- Do you need third-party extensions? Plan for security and quality control.
- Can you defer tool schema loading until the model actually needs a tool?

---

## Decision 5: How Do Subagents Work?

**The question:** When the agent spawns sub-tasks, do they share context or run in isolation?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Isolated context + summary return** | Claude Code (sidechain transcripts) | Prevents context explosion (~7x token cost). But subagents can't share fine-grained state. |
| **Shared context** | Some multi-agent frameworks | Full information sharing. But context fills up fast with N agents. |
| **Message passing** | Actor model systems | Clean boundaries. But requires explicit protocol design. |

**Key insight from Claude Code:** Subagent sessions cost ~7x tokens of standard sessions. Only summaries return to the parent -- full history never enters the parent context. This is essential for context conservation.

**Questions to ask yourself:**
- Do your sub-tasks need to see each other's work?
- How do you prevent N subagents from consuming N * context_window tokens?
- Do subagents inherit parent permissions, or establish their own?

---

## Decision 6: How Do Sessions Persist?

**The question:** What happens when a session ends? What carries over?

| Approach | Example | Trade-off |
|:---------|:--------|:----------|
| **Append-only JSONL** | Claude Code | Auditable, reconstructable, simple. But poor query power. |
| **Database** | Some enterprise agents | Rich queries, fast lookups. But adds infrastructure dependency and reduces transparency. |
| **Stateless** | Most chat APIs | Simplest. But no resume, no fork, no audit trail. |

**Key insight from Claude Code:** **Never restore permissions on resume.** Trust is always re-established in the current session. Security state should not persist implicitly across session boundaries.

**Key insight on auditability:** Append-only JSONL means every event is human-readable, version-controllable, and reconstructable without specialized tooling. The slight loss in query power is worth the transparency.

---

## The Meta-Pattern: Three Recurring Design Commitments

Across all six decisions, three patterns recur in Claude Code's architecture:

1. **Graduated layering over monolithic mechanisms** -- Safety, context, and extensibility all use stacked independent stages rather than single solutions.

2. **Append-only designs favoring auditability over query power** -- Everything can be reconstructed; nothing is destructively edited.

3. **Model judgment within a deterministic harness** -- The model decides freely; the harness enforces boundaries. The 1.6%/98.4% ratio is not accidental.

---

## Resources for Builders

- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) -- "Bash is all you need." Build a nano Claude Code from scratch, session by session.
- [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) -- Rust reimplementation. Reduced 512K lines of TypeScript to ~20K lines while preserving core functionality.
- [Yuyz0112/claude-code-reverse](https://github.com/Yuyz0112/claude-code-reverse) -- Visualize Claude Code's LLM interactions. See exactly what API requests are made for different task scenarios.
- [Haseeb Qureshi's architecture comparison](https://gist.github.com/Haseeb-Qureshi/2213cc0487ea71d62572a645d7582518) -- Claude Code vs Codex vs Cline vs OpenCode, compared architecturally.
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) -- Open-source AI coding agent platform (ICLR 2025). Container-isolation approach.
- [SWE-Agent](https://github.com/SWE-agent/SWE-agent) -- NeurIPS 2024. Docker-based coding agent.
- [Aider](https://github.com/Aider-AI/aider) -- Git-as-safety-net approach to AI coding.
