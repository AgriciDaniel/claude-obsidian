---
type: concept
title: "How does the LLM Wiki pattern work?"
aliases:
  - "How does the LLM Wiki pattern work?"
created: 2026-06-19
updated: 2026-06-19
tags: [concept, llm-wiki, knowledge-management]
status: evergreen
---

# How does the LLM Wiki pattern work?

The LLM Wiki pattern compiles source material into a persistent Markdown knowledge base instead of recreating answers from retrieved chunks on every query.

## Layers

1. Immutable source material is retained for provenance.
2. Agent-generated wiki pages synthesize concepts, entities, projects, and connections.
3. Rules and schemas define naming, frontmatter, linking, and maintenance behavior.

## Operating loop

- Ingest sources.
- Create or update linked pages.
- Record changes in the log and hot cache.
- Query the durable wiki.
- Lint for contradictions, dead links, orphans, and stale claims.

Related: [[Persistent Wiki Artifact]], [[Source-First Synthesis]], [[Query-Time Retrieval]], and [[Wiki vs RAG]].
