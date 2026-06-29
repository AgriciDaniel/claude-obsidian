---
address: c-000017
type: reference
title: "Claude Code Ecosystem Reference"
created: 2026-06-05
updated: 2026-06-05
tags:
  - reference
  - claude-code
  - agent-architecture
  - ecosystem
status: current
related:
  - "[[Dive into Claude Code]]"
  - "[[Agent Harness Engineering]]"
  - "[[Dive-into-Claude-Code-Related-Resources]]"
---

# Claude Code Ecosystem Reference

Structured map of community analysis, reimplementations, guides, and academic papers around Claude Code's architecture. Source: [[Dive-into-Claude-Code-Related-Resources]] (arXiv 2604.14228 appendix).

---

## Architecture Analysis Repos

| Repo | Focus |
|:-----|:------|
| [ComeOnOliver/claude-code-analysis](https://github.com/ComeOnOliver/claude-code-analysis) | Comprehensive reverse-engineering: source tree, module boundaries, tool inventories |
| [alejandrobalderas/claude-code-from-source](https://github.com/alejandrobalderas/claude-code-from-source) | 18-chapter ~400-page technical book; original pseudocode, no proprietary source |
| [liuup/claude-code-analysis](https://github.com/liuup/claude-code-analysis) | Chinese: startup flow, query main loop, MCP integration, multi-agent |
| [sanbuphy/claude-code-source-code](https://github.com/sanbuphy/claude-code-source-code) | Quadrilingual (EN/JA/KO/ZH); 10 domains, 75 reports; telemetry, KAIROS, unreleased tools |
| [Yuyz0112/claude-code-reverse](https://github.com/Yuyz0112/claude-code-reverse) | Visual LLM interaction tracer; log parser for prompts, tool calls, compaction |
| [AgiFlow/claude-code-prompt-analysis](https://github.com/AgiFlow/claude-code-prompt-analysis) | Empirical API logs across 5 sessions; Skills two-step semantic matching discovery |

---

## Open-Source Reimplementations

| Repo | Notable |
|:-----|:--------|
| [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) | **Rust. 179K stars in 9 days — fastest to 100K in GitHub history.** 512K LoC → ~20K lines. |
| [chauncygu/collection-claude-code-source-code](https://github.com/chauncygu/collection-claude-code-source-code) | Meta-collection: claw-code, nano-claude-code (Python ~5K lines), original source archive |
| [777genius/claude-code-working](https://github.com/777genius/claude-code-working) | Working reverse-engineered CLI; Bun runtime; 450+ chunks; 30 feature flags polyfilled |
| [ruvnet/open-claude-code](https://github.com/ruvnet/open-claude-code) | Nightly auto-decompile; 903+ tests, 25 tools, 4 MCP transports, 6 permission modes |
| [T-Lab-CUHKSZ/claude-code](https://github.com/T-Lab-CUHKSZ/claude-code) | CUHK-SZ buildable research fork; reconstructed build system |

---

## Guides & Learning

| Repo | Focus |
|:-----|:------|
| [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | "Bash is all you need" — 19-chapter 0-to-1 course; runnable Python agents; ZH/EN/JA |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | Agent harness optimization — skills, instincts, memory, security; 50K+ stars |
| [nblintao/awesome-claude-code-postleak-insights](https://github.com/nblintao/awesome-claude-code-postleak-insights) | Best post-leak curation: BUDDY, KAIROS, ULTRAPLAN, Undercover Mode, AutoDream |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Skills, hooks, slash-commands, orchestrators, plugins |
| [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 135 agents, 35 skills, 42 commands, 176+ plugins, 20 hooks, 15 rules |

---

## Key Blog Posts

### Pre-Leak (2025 – early 2026)

| Article | Signal |
|:--------|:-------|
| [Marco Kotrotsos — "Claude Code Internals" (15-part)](https://kotrotsos.medium.com/claude-code-internals-part-1-high-level-architecture-9881c68c799f) | Most systematic pre-leak analysis; architecture, loop, permissions, sub-agents, MCP, telemetry |
| [George Sung — "Tracing Claude Code's LLM Traffic"](https://medium.com/@georgesung/tracing-claude-codes-llm-traffic-agentic-loop-sub-agents-tool-use-prompts-7796941806f5) | Complete system prompts + API logs; discovered dual-model usage (Opus main loop, Haiku metadata) |
| [Sabrina Ramonov — "Reverse-Engineering Using Sub Agents"](https://www.sabrina.dev/p/reverse-engineering-claude-code-using) | Custom sub-agents to reverse-engineer minified JS: File Splitter + Structure Analyzer |

### Post-Leak (March–April 2026)

| Article | Signal |
|:--------|:-------|
| [Alex Kim — "The Claude Code Source Leak"](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) | Definitive first-responder: anti-distillation, frustration regexes, Undercover Mode, ~250K wasted API calls/day |
| [Han HELOIR YAN — "Nobody Analyzed Its Architecture"](https://medium.com/data-science-collective/everyone-analyzed-claude-codes-features-nobody-analyzed-its-architecture-1173470ab622) | **"The moat is the harness, not the model."** Independent validation of the 98.4/1.6 thesis |
| [Haseeb Qureshi — Cross-agent comparison](https://gist.github.com/Haseeb-Qureshi/2213cc0487ea71d62572a645d7582518) | Claude Code vs Codex vs Cline vs OpenCode architectural comparison |
| [Agiflow — "Prompt Augmentation"](https://agiflow.io/blog/claude-code-internals-reverse-engineering-prompt-augmentation/) | 5 augmentation mechanisms via network traces; Skills two-step semantic matching |

### Specialized

| Topic | Resource |
|:------|:---------|
| Memory architecture | [MindStudio — "Three-Layer Memory"](https://www.mindstudio.ai/blog/claude-code-source-leak-memory-architecture): in-context + MEMORY.md + CLAUDE.md |
| Permission system | [Marco Kotrotsos Part 8](https://kotrotsos.medium.com/claude-code-internals-part-8-the-permission-system-624bd7bb66b7) |
| Prompt caching | [ClaudeCodeCamp — "How Prompt Caching Actually Works"](https://www.claudecodecamp.com/p/how-prompt-caching-actually-works-in-claude-code) |
| MCP integration | [Gigi Sayfan — "MCP Unleashed"](https://medium.com/@the.gigi/claude-code-deep-dive-mcp-unleashed-0c7692f9c2c2) |

---

## Academic Papers

| Paper | Venue | Focus |
|:------|:------|:------|
| [Architectural Design Decisions in AI Agent Harnesses](https://arxiv.org/abs/2604.18071) | arXiv | Source-grounded study of 70 agent-system projects; design-space framing closest peer to the VILA-Lab paper |
| [Decoding the Configuration of AI Coding Agents](https://arxiv.org/abs/2511.09268) | arXiv | 328 Claude Code config files; SE concerns and co-occurrence patterns |
| [On the Use of Agentic Coding Manifests](https://arxiv.org/abs/2509.14744) | arXiv | 253 CLAUDE.md files from 242 repos; structural patterns in operational commands |
| [Context Engineering for Multi-Agent Code Assistants](https://arxiv.org/abs/2508.08322) | arXiv | Multi-agent workflow combining multiple LLMs for code generation |
| [A Survey on Code Generation with LLM-based Agents](https://arxiv.org/abs/2508.00083) | arXiv | Best survey of the AI coding agent field |
| [OpenHands: An Open Platform for AI Software Developers](https://arxiv.org/abs/2407.16741) | ICLR 2025 | Primary academic reference for open-source AI coding agents |
| [SWE-Agent: Agent-Computer Interfaces](https://arxiv.org/abs/2405.15793) | NeurIPS 2024 | Docker-based coding agent; custom ACI |
| [AI Agent Systems: Architectures, Applications, and Evaluation](https://arxiv.org/html/2601.01743v1) | arXiv 2026 | Broad agent system taxonomy |

---

## Related

- [[Agent Harness Engineering]] — the "moat is the harness" thesis validated across multiple independent analysts
- [[Dive into Claude Code]] — the paper this reference list accompanies
- [[Agent Design Space Decisions]] — the design decisions these resources illuminate from different angles
