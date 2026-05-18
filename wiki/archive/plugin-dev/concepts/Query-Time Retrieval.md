---
type: concept
title: "Query-Time Retrieval"
created: 2026-04-24
updated: 2026-04-24
tags:
  - rag
  - retrieval
  - llm-wiki
status: developing
related:
  - "[[How does the LLM Wiki pattern work?]]"
  - "[[Wiki vs RAG]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Persistent Wiki Artifact]]"
  - "[[Source-First Synthesis]]"
---

# Query-Time Retrieval

Query-time retrieval is the baseline memory pattern that LLM Wiki is contrasted against: relevant material is retrieved when the user asks a question, and the answer is generated from the retrieved context.

## Boundary Filled

The selected question contrasts wiki accumulation with RAG, but it does not define the retrieval side precisely. This page anchors the contrast in the original RAG paper and in the LLM Wiki gist.

## Extracted Claims

- The RAG paper defines retrieval-augmented generation as combining parametric memory with non-parametric memory for language generation: https://arxiv.org/abs/2005.11401
- The RAG paper describes the non-parametric memory as a dense vector index of Wikipedia accessed with a neural retriever: https://arxiv.org/abs/2005.11401
- The paper reports that RAG models generated more specific, diverse, and factual language than a parametric-only seq2seq baseline in its evaluated generation tasks: https://arxiv.org/abs/2005.11401
- Karpathy's LLM Wiki gist describes common document workflows as uploading files, retrieving relevant chunks at query time, and generating an answer: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Karpathy's LLM Wiki gist states that this query-time pattern makes the model rediscover and assemble knowledge on each question instead of accumulating synthesis: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- The MemGPT paper frames limited LLM context windows as a constraint for extended conversations and document analysis, then proposes virtual context management across memory tiers: https://arxiv.org/abs/2310.08560

## Contrast With Wiki Memory

Query-time retrieval can provide external evidence at answer time. The LLM Wiki pattern shifts part of the work earlier by compiling source material into maintained pages before later queries arrive: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## Primary Sources

- https://arxiv.org/abs/2005.11401
- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://arxiv.org/abs/2310.08560
