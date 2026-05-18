---
type: question
title: "How does the LLM Wiki pattern work?"
question: "How does the LLM Wiki pattern work and why is it better than RAG?"
answer_quality: definitive
created: 2026-04-07
updated: 2026-04-07
tags:
  - question
  - llm-wiki
  - knowledge-management
status: developing
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Hot Cache]]"
  - "[[index]]"
  - "[[Wiki vs RAG]]"
sources: []
---

# How does the LLM Wiki pattern work?

**Question:** How does the LLM Wiki pattern work and why is it better than RAG?

## Answer

The [[LLM Wiki Pattern]] turns an LLM into a knowledge architect rather than a search engine.

**Standard RAG** (Retrieval-Augmented Generation): every query searches raw documents, retrieves chunks, and assembles an answer from scratch. Nothing is built up. Ask the same question twice — it does the same work twice.

**The wiki pattern** is different. When a source arrives, the LLM reads it and integrates it: updating entity pages, noting contradictions, adding cross-references. The synthesis is done once and persists. Every query benefits from all previous ingests.

### The three layers

1. **`.raw/`** — your source documents. Immutable. Claude reads, never modifies.
2. **`wiki/`** — Claude-generated knowledge. Summaries, entities, concepts, synthesis.
3. **`CLAUDE.md`** — the schema. Tells Claude how the wiki is structured and what to do.

### Why it compounds

See [[Compounding Knowledge]] for the full argument. The short version: each new source doesn't just add one page — it enriches 8-15 existing pages. The connections between pages are where the value lives, not the raw content itself.

### The hot cache shortcut

[[Hot Cache]] (wiki/hot.md) is a ~500-word summary of recent context. New sessions read it first. Cross-project references read it first. It prevents re-reading the whole wiki just to answer "where were we?"

(Source: [[LLM Wiki Pattern]])

## Confidence

definitive — this is the core concept the entire vault demonstrates.
