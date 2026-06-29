[Back to Main README](../README.md)

# Related Resources: Community Analysis

> A curated map of the repos, reimplementations, blog posts, and academic papers surrounding Claude Code's architecture.

---

## Design-Space Source Notes

| Resource | Description |
|:---|:---|
| [Agent Systems Design Space Source Notes](./agent-design-space-source-notes_zh.md) | Chinese-language notes on high-signal agent-system design sources and new developments, with year-month metadata kept per source for ongoing extension. Covers OpenAI Codex, Anthropic/Claude, Google Antigravity, GitHub Copilot, LangChain, Cursor, AWS, Microsoft, standards/security guidance, and recent papers. Focuses on the emerging agent operating layer, sandboxes, context/memory, tool connectivity, human control surfaces, and trace/eval improvement loops. |

---

## Architecture Analysis

Deep dives into Claude Code's internal design.

| Repository | Description |
|:-----------|:------------|
| [**ComeOnOliver/claude-code-analysis**](https://github.com/ComeOnOliver/claude-code-analysis) | Comprehensive reverse-engineering: source tree structure, module boundaries, tool inventories, and architectural patterns. |
| [**alejandrobalderas/claude-code-from-source**](https://github.com/alejandrobalderas/claude-code-from-source) | 18-chapter technical book (~400 pages). All original pseudocode, no proprietary source. |
| [**liuup/claude-code-analysis**](https://github.com/liuup/claude-code-analysis) | Chinese-language deep-dive — startup flow, query main loop, MCP integration, multi-agent architecture. |
| [**sanbuphy/claude-code-source-code**](https://github.com/sanbuphy/claude-code-source-code) | Quadrilingual analysis (EN/JA/KO/ZH) — 10 domains, 75 reports. Covers telemetry, codenames, KAIROS, unreleased tools. |
| [**cablate/claude-code-research**](https://github.com/cablate/claude-code-research) | Independent research on internals, Agent SDK, and related tooling. |
| [**Yuyz0112/claude-code-reverse**](https://github.com/Yuyz0112/claude-code-reverse) | Visualize Claude Code's LLM interactions — log parser and visual tool to trace prompts, tool calls, and compaction. |
| [**AgiFlow/claude-code-prompt-analysis**](https://github.com/AgiFlow/claude-code-prompt-analysis) | API request/response logs across 5 conversation sessions. Unique empirical methodology with reproducible data. |

---

## Open-Source Reimplementations

Clean-room rewrites and buildable research forks.

| Repository | Description |
|:-----------|:------------|
| [**chauncygu/collection-claude-code-source-code**](https://github.com/chauncygu/collection-claude-code-source-code) | Meta-collection — claw-code (Rust, 30K+ stars), nano-claude-code (Python ~5K lines), and original source archive. |
| [**ultraworkers/claw-code**](https://github.com/ultraworkers/claw-code) | Clean-room Rust reimplementation. 179K stars in 9 days — fastest repo in GitHub history to 100K. Reduced 512K LoC TypeScript to ~20K lines. |
| [**777genius/claude-code-working**](https://github.com/777genius/claude-code-working) | Working reverse-engineered CLI. Runnable with Bun, 450+ chunk files, 30 feature flags polyfilled. |
| [**T-Lab-CUHKSZ/claude-code**](https://github.com/T-Lab-CUHKSZ/claude-code) | CUHK-Shenzhen buildable research fork — reconstructed build system from raw TypeScript snapshot. |
| [**ruvnet/open-claude-code**](https://github.com/ruvnet/open-claude-code) | Nightly auto-decompile rebuild — 903+ tests, 25 tools, 4 MCP transports, 6 permission modes. |
| [**Enderfga/openclaw-claude-code**](https://github.com/Enderfga/openclaw-claude-code) | OpenClaw plugin — unified ISession interface for Claude/Codex/Gemini/Cursor. Multi-agent council. |
| [**memaxo/claude_code_re**](https://github.com/memaxo/claude_code_re) | Reverse engineering from minified bundles — deobfuscation of the publicly distributed cli.js file. |
| [**agentforce314/clawcodex**](https://github.com/agentforce314/clawcodex) | Python rebuild with multi-provider LLM support. |

---

## Guides & Learning

Tutorials and hands-on learning paths.

| Repository | Description |
|:-----------|:------------|
| [**shareAI-lab/learn-claude-code**](https://github.com/shareAI-lab/learn-claude-code) | "Bash is all you need" — 19-chapter 0-to-1 course with runnable Python agents, web platform. ZH/EN/JA. |
| [**FlorianBruniaux/claude-code-ultimate-guide**](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Beginner-to-power-user guide with production-ready templates, agentic workflow guides, and cheatsheets. |
| [**affaan-m/everything-claude-code**](https://github.com/affaan-m/everything-claude-code) | Agent harness optimization — skills, instincts, memory, security, and research-first development. 50K+ stars. |
| [**nblintao/awesome-claude-code-postleak-insights**](https://github.com/nblintao/awesome-claude-code-postleak-insights) | Best curated post-leak resource. BUDDY, KAIROS, ULTRAPLAN, Undercover Mode, AutoDream memory consolidation. |
| [**hesreallyhim/awesome-claude-code**](https://github.com/hesreallyhim/awesome-claude-code) | Curated list of skills, hooks, slash-commands, agent orchestrators, and plugins. |
| [**rohitg00/awesome-claude-code-toolkit**](https://github.com/rohitg00/awesome-claude-code-toolkit) | 135 agents, 35 skills, 42 commands, 176+ plugins, 20 hooks, 15 rules, 7 templates, 14 MCP configs. |

---

## Blog Posts & Technical Articles

### Pre-Leak Reverse Engineering (2025 -- early 2026)

| Article | What Makes It Valuable |
|:--------|:----------------------|
| [Marco Kotrotsos — "Claude Code Internals" (15-part series)](https://kotrotsos.medium.com/claude-code-internals-part-1-high-level-architecture-9881c68c799f) | Most systematic pre-leak analysis. Architecture, agent loop, permissions, sub-agents, MCP, telemetry. Based on v2.0.76. |
| [George Sung — "Tracing Claude Code's LLM Traffic"](https://medium.com/@georgesung/tracing-claude-codes-llm-traffic-agentic-loop-sub-agents-tool-use-prompts-7796941806f5) | Complete system prompts and full API logs. Discovered dual-model usage (Opus for main loop, Haiku for metadata). |
| [Reid Barber — "Reverse Engineering Claude Code"](https://www.reidbarber.com/blog/reverse-engineering-claude-code) | One of the earliest analyses (mid-2025). REPL architecture and tool suite. |
| [Kir Shatrov — "Reverse Engineering Claude Code"](https://kirshatrov.com/posts/claude-code-internals) | Used mitmproxy to intercept API calls. Single experiment: 40 seconds LLM time, $0.11 cost. |
| [Sabrina Ramonov — "Reverse-Engineering Using Sub Agents"](https://www.sabrina.dev/p/reverse-engineering-claude-code-using) | Creative methodology: custom sub-agents (File Splitter, Structure Analyzer) to reverse-engineer minified JS. |

### Post-Leak Analysis (March--April 2026)

| Article | What Makes It Valuable |
|:--------|:----------------------|
| [Alex Kim — "The Claude Code Source Leak"](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) | Definitive first-responder analysis. Anti-distillation, frustration regexes, Undercover Mode, ~250K wasted API calls/day. Went viral on HN. |
| [Haseeb Qureshi — "Inside the Claude Code source"](https://gist.github.com/Haseeb-Qureshi/d0dc36844c19d26303ce09b42e7188c1) | Key module analysis. React/Ink UI, four compaction strategies, dynamic prompt boundary system. |
| [Haseeb Qureshi — Cross-agent architecture comparison](https://gist.github.com/Haseeb-Qureshi/2213cc0487ea71d62572a645d7582518) | Claude Code vs Codex vs Cline vs OpenCode — architecture-level comparison. |
| [Engineer's Codex — "Diving into the Source Code Leak"](https://read.engineerscodex.com/p/diving-into-claude-codes-source-code) | Modular system prompt, ~40 tools, 46K-line query engine, anti-distillation. Accessible to broad audience. |
| [Han HELOIR YAN — "Nobody Analyzed Its Architecture"](https://medium.com/data-science-collective/everyone-analyzed-claude-codes-features-nobody-analyzed-its-architecture-1173470ab622) | "The moat is the harness, not the model." Aligns with our report's thesis. |
| [Agiflow — "Reverse Engineering Prompt Augmentation"](https://agiflow.io/blog/claude-code-internals-reverse-engineering-prompt-augmentation/) | 5 prompt augmentation mechanisms backed by actual network traces. Shows Skills two-step semantic matching. |

### Specialized Deep Dives

| Topic | Resource |
|:------|:---------|
| **Memory Architecture** | [MindStudio — "Three-Layer Memory Architecture"](https://www.mindstudio.ai/blog/claude-code-source-leak-memory-architecture) — In-context, MEMORY.md pointer index, CLAUDE.md static config. Best single resource on memory. |
| **Permission System** | [Marco Kotrotsos — "Part 8: The Permission System"](https://kotrotsos.medium.com/claude-code-internals-part-8-the-permission-system-624bd7bb66b7) |
| **Prompt Caching** | [ClaudeCodeCamp — "How Prompt Caching Actually Works"](https://www.claudecodecamp.com/p/how-prompt-caching-actually-works-in-claude-code) |
| **MCP Integration** | [Gigi Sayfan — "MCP Unleashed"](https://medium.com/@the.gigi/claude-code-deep-dive-mcp-unleashed-0c7692f9c2c2) |
| **Compression & Telemetry** | [WaveSpeedAI — "Architecture Deep Dive"](https://wavespeed.ai/blog/posts/claude-code-architecture-leaked-source-deep-dive/) — Three-layer compression, frustration metrics. |
| **Rust Rewrite Analysis** | [DEV Community — "Architecture via Rust Rewrite"](https://dev.to/brooks_wilson_36fbefbbae4/claude-code-architecture-explained-agent-loop-tool-system-and-permission-model-rust-rewrite-41b2) — 18 tools in three-layer structure. |
| **Permissions Config** | [Vincent Qiao — "Permissions System Deep Dive"](https://blog.vincentqiao.com/en/posts/claude-code-settings-permissions/) |

---

## Related Academic Papers

| Paper | Venue | Relevance |
|:------|:------|:----------|
| [Decoding the Configuration of AI Coding Agents](https://arxiv.org/abs/2511.09268) | arXiv | Empirical study of 328 Claude Code config files — SE concerns and co-occurrence patterns. |
| [On the Use of Agentic Coding Manifests](https://arxiv.org/abs/2509.14744) | arXiv | Analyzed 253 CLAUDE.md files from 242 repos — structural patterns in operational commands. |
| [Context Engineering for Multi-Agent Code Assistants](https://arxiv.org/abs/2508.08322) | arXiv | Multi-agent workflow combining multiple LLMs for code generation. |
| [OpenHands: An Open Platform for AI Software Developers](https://arxiv.org/abs/2407.16741) | ICLR 2025 | Primary academic reference for open-source AI coding agents. |
| [SWE-Agent: Agent-Computer Interfaces](https://arxiv.org/abs/2405.15793) | NeurIPS 2024 | Docker-based coding agent with custom agent-computer interface. |
| [The OpenHands Software Agent SDK](https://arxiv.org/abs/2511.03690) | arXiv | Composable SDK foundation for production agents. |
| [A Survey on Code Generation with LLM-based Agents](https://arxiv.org/abs/2508.00083) | arXiv | Best survey of the AI coding agent field. |
| [AI Agent Systems: Architectures, Applications, and Evaluation](https://arxiv.org/html/2601.01743v1) | arXiv 2026 | Broad agent system taxonomy. |

---

## How This Paper Differs

While the projects above focus on **engineering reverse-engineering** or **practical reimplementation**, this paper provides a **systematic values → principles → implementation** analytical framework — tracing five human values through thirteen design principles to specific source-level choices, and using OpenClaw comparison to reveal that cross-cutting integrative mechanisms, not modular features, are the true locus of engineering complexity.

---

*Know a resource that should be listed here? Open an issue or PR.*
