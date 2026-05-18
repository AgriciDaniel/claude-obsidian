---
type: concept
title: "Source-First Synthesis"
created: 2026-04-24
updated: 2026-04-24
tags:
  - llm-wiki
  - synthesis
  - provenance
status: developing
related:
  - "[[How does the LLM Wiki pattern work?]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Persistent Wiki Artifact]]"
  - "[[Query-Time Retrieval]]"
---

# Source-First Synthesis

Source-first synthesis is the LLM Wiki practice of keeping raw sources separate from the generated wiki while requiring the wiki to cite and integrate those sources. Karpathy's pattern describes raw sources as the source of truth and the generated wiki as the maintained synthesis layer: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## Boundary Filled

The selected question says the wiki pattern integrates sources, but it does not spell out the provenance discipline. This page records the rule: synthesis is allowed to be rewritten, but source material remains the cited anchor.

## Extracted Claims

- Karpathy's LLM Wiki pattern says raw sources can include articles, papers, images, and data files, and that the LLM reads them without modifying them: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- The same source describes the wiki as summaries, entity pages, concept pages, comparisons, overview, and synthesis maintained by the LLM: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- The ingest operation can create a source summary, update indexes, update relevant entity and concept pages, and append a log entry: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- The query operation reads relevant wiki pages and synthesizes answers with citations, and useful answers can be filed back into the wiki: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- The RAG paper identifies provenance and updating world knowledge as open problems for knowledge-intensive generation systems: https://arxiv.org/abs/2005.11401

## Operating Rule

Source-first synthesis is stricter than unsourced summarization. A new concept page should identify the sources it used, state what was extracted from them, and avoid treating the generated page as a replacement for the source document.

## Primary Sources

- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://arxiv.org/abs/2005.11401
