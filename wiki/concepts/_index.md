---
type: meta
title: "Concepts Index"
updated: 2026-04-07
tags:
  - meta
  - index
  - concept
domain: knowledge-management
status: evergreen
related:
  - "[[index]]"
  - "[[dashboard]]"
  - "[[Wiki Map]]"
  - "[[Hot Cache]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Hot Cache]]"
  - "[[Compounding Knowledge]]"
---

# Concepts Index

Navigation: [[index]] | [[entities/_index|Entities]] | [[sources/_index|Sources]]

All concept pages — ideas, patterns, and frameworks extracted from sources.

---

## Knowledge Management

- [[LLM Wiki Pattern]] — the core architecture for persistent, compounding knowledge bases
- [[Hot Cache]] — ~500-word session context file, updated after every ingest
- [[Compounding Knowledge]] — why the wiki grows more valuable over time, unlike RAG
- [[DragonScale Memory]] — memory-layer spec: fold operator, deterministic page addresses, semantic tiling, boundary-first autoresearch (status: shipped v0.4, all four mechanisms opt-in)
- [[Persistent Wiki Artifact]]: durable Markdown page as the LLM's memory object (developing)
- [[Source-First Synthesis]]: provenance discipline for LLM wiki layers (developing)
- [[Query-Time Retrieval]]: query synthesis with citations, complementary to Obsidian search (developing)

---

## Agent Architecture

- [[Agent Harness Engineering]] — 98.4% infrastructure / 1.6% AI; the harness (not the model loop) is the differentiator (developing)
- [[queryLoop Architecture]] — Claude Code's single AsyncGenerator while-loop; 9-step turn pipeline; 5 stop conditions (developing)
- [[5-Layer Compaction]] — graduated context degradation: Budget Reduction → Snip → Microcompact → Context Collapse → Auto-Compact; feature-gated stages (developing)
- [[Deny-First Permission Model]] — 7 permission modes, 7 safety layers, 4-stage authorization pipeline, never restore on resume (developing)
- [[Claude Code Extensibility]] — 4 mechanisms (hooks/skills/plugins/MCP) × 3 injection points (assemble/model/execute); graduated context cost (developing)
- [[Subagent Delegation Architecture]] — SkillTool vs AgentTool; 3 isolation modes; sidechain transcripts; flock() coordination (developing)
- [[CLAUDE.md Hierarchy]] — 4 levels; user context (probabilistic) not system prompt (deterministic); 9 ordered context sources (developing)
- [[Agent Design Space Decisions]] — 6 decisions with alternatives and trade-offs (LangGraph/Devin/SWE-Agent/Aider vs Claude Code); 3 meta-pattern commitments (developing)

---

## Add new concepts here as they are extracted from sources.
