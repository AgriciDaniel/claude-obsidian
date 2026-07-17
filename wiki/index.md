---
type: meta
title: "Wiki Index"
updated: 2026-07-17
tags:
  - meta
  - index
status: evergreen
related:
  - "[[overview]]"
  - "[[log]]"
  - "[[hot]]"
  - "[[dashboard]]"
  - "[[Wiki Map]]"
  - "[[concepts/_index]]"
  - "[[entities/_index]]"
  - "[[sources/_index]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Hot Cache]]"
  - "[[Compounding Knowledge]]"
  - "[[Andrej Karpathy]]"
  - "[[AI大模型知识点全景图-home]]"
---

# Wiki Index

Last updated: 2026-07-17 | Total pages: 56 | Sources ingested: 3

Navigation: [[overview]] | [[log]] | [[hot]] | [[dashboard]] | [[Wiki Map]] | [[getting-started]]

---

## Concepts

- [[LLM Wiki Pattern]] — the pattern for building persistent, compounding knowledge bases using LLMs (status: mature)
- [[Hot Cache]] — ~500-word session context file, updated after every ingest and session (status: mature)
- [[Compounding Knowledge]] — why wiki knowledge grows more valuable over time, unlike RAG (status: mature)
- [[cherry-picks]] — prioritized feature backlog from ecosystem research; 13 features to add to claude-obsidian (status: current)
- [[SVG Diagram Style Guide]] — canonical visual style for all diagrams: Space Grotesk, #0A0A0A dark theme, #E07850 accent, full design tokens (status: evergreen)
- [[Pro Hub Challenge]] — community challenge pattern for building claude-seo/claude-blog extensions; first challenge produced 6 submissions, 5 integrated in v1.9.0 (status: evergreen)
- [[Semantic Topic Clustering]] — SERP-based keyword grouping replacing paid tools; hub-spoke architecture with interactive visualization (status: evergreen)
- [[Search Experience Optimization]] — "read SERPs backwards" methodology for page-type mismatch detection and persona scoring (status: evergreen)
- [[SEO Drift Monitoring]] — "git for SEO" baseline/diff/track with 17 comparison rules and SQLite persistence (status: evergreen)
- [[DragonScale Memory]] — memory-layer spec inspired by the Heighway dragon curve; fold operator, deterministic page addresses, semantic tiling, boundary-first autoresearch (status: shipped v0.4, all four mechanisms opt-in)
- [[Persistent Wiki Artifact]]: durable Markdown page as the LLM's memory object, distinct from ephemeral chat turns (status: developing)
- [[Source-First Synthesis]]: provenance discipline; raw sources stay immutable while the wiki layer is synthesized and cited (status: developing)
- [[Query-Time Retrieval]]: wiki query path synthesizes with citations; complementary to Obsidian's in-vault search (status: developing)
- [[AI Large Model Architecture]] — Transformer 架构详解与变体（MHA/GQA/MQA、MoE）（status: seed）
- [[LLM Training Methods]] — 预训练、SFT、RLHF、DPO、GRPO（status: seed）
- [[Model Alignment and Safety]] — 对齐技术、红队测试、Jailbreak 防御、Constitutional AI（status: seed）
- [[LLM Reasoning Methods]] — CoT、ToT、ReAct、Reflexion、o1/o3、test-time compute（status: seed）
- [[Multimodal AI]] — VLM、T2I、T2V、TTS、语音（status: seed）
- [[Chinese AI Model Ecosystem]] — 国内大模型生态全景（DeepSeek、Qwen、GLM 等）（status: seed）
- [[AI Agent Systems]] — Agent 框架、Function Calling、MoA、MCP 协议（status: seed）
- [[LLM Evaluation]] — 评测基准体系（MMLU、GSM8K、HumanEval、C-Eval 等）（status: seed）
- [[Model Scaling and Emergence]] — Scaling Laws、涌现能力、上下文窗口演进（status: seed）
- [[RAG and Retrieval]] — RAG 流水线、Embedding、检索策略、Chunking（status: seed）
- [[Model Optimization]] — 量化、蒸馏、LoRA/QLoRA、KV-cache 优化（status: seed）
- [[Prompt Engineering]] — 提示词工程方法体系（status: seed）

---

## Entities

- [[Andrej Karpathy]] — AI researcher, creator of the LLM Wiki pattern, former Tesla AI director (status: developing)
- [[Ar9av-obsidian-wiki]] — multi-agent compatible LLM Wiki plugin; delta tracking manifest (status: current)
- [[Nexus-claudesidian-mcp]] — native Obsidian plugin + MCP bridge; workspace memory, task management (status: current)
- [[ballred-obsidian-claude-pkm]] — goal cascade PKM; auto-commit hooks, /adopt command (status: current)
- [[rvk7895-llm-knowledge-bases]] — 3-depth query system, Marp slides, parallel deep research (status: current)
- [[kepano-obsidian-skills]] — official skills from Obsidian creator; defuddle, obsidian-bases (status: current)
- [[Claudian-YishenTu]] — native Obsidian plugin embedding Claude Code; plan mode, @mention (status: current)
- [[Claude SEO]] — Tier 4 Claude Code skill for SEO analysis; 23 skills, 17 agents, 30 scripts at v1.9.0 (status: evergreen)
- [[OpenAI GPT Series]] — OpenAI 模型进化史：GPT-1 → GPT-4o → o1/o3（status: seed）
- [[Anthropic Claude Series]] — Anthropic 与 Claude 系列：Constitutional AI 安全对齐（status: seed）
- [[DeepSeek]] — DeepSeek 模型家族：MLA、MoE 架构、GRPO 训练、R1 推理模型（status: seed）
- [[Meta LLaMA Series]] — Meta LLaMA 开源模型生态（LLaMA 1 → 2 → 3）（status: seed）
- [[Google Gemini Series]] — Google Gemini 系列：原生多模态、1M 上下文（status: seed）
- [[Qwen (Alibaba)]] — 阿里通义 Qwen 系列：全面开源、Agent 生态（status: seed）
- [[GLM (Zhipu AI)]] — 智谱 GLM/ChatGLM 系列：学术渊源深厚（status: seed）
- [[Moonshot AI (Kimi)]] — 月之暗面 Kimi：超长上下文、k1.5 推理模型（status: seed）

---

## Sources

- [[claude-obsidian-ecosystem-research]] — 2026-04-08 | web research across 16+ repos | 8 wiki pages created
- [[AI大模型知识点全景图]] — 2026-07-17 | 73 页扫描版 AI 大模型知识全景图 | 22 wiki pages created (concepts: 12, entities: 8, source: 1, article home: 1)

---

## Questions

- [[How does the LLM Wiki pattern work]] — how the pattern works and why it outperforms RAG at human scale (status: developing)

---

## Comparisons

- [[Wiki vs RAG]] — when to use a wiki knowledge base versus RAG; verdict: wiki wins at <1000 pages
- [[claude-obsidian-ecosystem]] — feature matrix of 16+ Claude+Obsidian projects; where claude-obsidian wins and gaps

---

## Decisions

- [[2026-04-14-community-cta-rollout]] - Skool community CTA footer added to 6 skill repos with per-tool frequency rules (status: active)
- [[2026-04-15-slides-and-release-session]] - Claude SEO v1.9.0 slides (15-slide HTML deck) + GitHub release v1.9.0 with PDF asset (status: complete)
- [[2026-04-15-release-report-session]] - Claude SEO v1.9.0 Release Report PDF: dark theme, 13 pages, WeasyPrint layout fixes, Challenge v2 added (status: complete)
- [[2026-04-14-claude-seo-v190-session]] - Claude SEO v1.9.0 Pro Hub Challenge integration: 5 submissions, 4 new skills, 4 review rounds, cybersecurity audit (status: complete)

---

## Domains

<!-- Add domain entries here after scaffold -->
