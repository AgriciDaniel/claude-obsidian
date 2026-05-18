---
type: concept
title: "Persistent Wiki Artifact"
created: 2026-04-24
updated: 2026-04-24
tags:
  - llm-wiki
  - knowledge-management
  - agent-memory
status: developing
related:
  - "[[How does the LLM Wiki pattern work?]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Source-First Synthesis]]"
  - "[[Query-Time Retrieval]]"
---

# Persistent Wiki Artifact

A persistent wiki artifact is the maintained Markdown layer between raw sources and future questions. In Karpathy's LLM Wiki description, the agent reads source material, extracts key information, and integrates it into an interlinked wiki instead of only retrieving chunks at answer time: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## Boundary Filled

The selected question explains that an LLM Wiki compounds knowledge, but it does not isolate the artifact as the unit of memory. This page makes that boundary explicit: memory is stored in files that can be browsed, linked, reviewed, and revised.

## Extracted Claims

- The LLM Wiki pattern defines raw sources, the generated wiki, and a schema document as separate layers: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- In that pattern, the raw source collection is treated as immutable, while the wiki layer is owned and maintained by the LLM: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- The pattern frames the wiki as a compounding artifact whose cross-references, contradiction flags, and synthesis persist across later questions: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Obsidian supports Wikilinks such as `[[Three laws of motion]]`, which lets Markdown files form an internal network of notes: https://obsidian.md/help/links
- Obsidian can automatically update internal links when a file is renamed, depending on the vault setting: https://obsidian.md/help/links

## Implications for This Vault

- The durable memory object is the page, not the chat turn.
- The page needs frontmatter, stable title, wikilinks, and source URLs so later agents can inspect provenance.
- The page should remain small enough to revise directly, because the LLM Wiki pattern depends on updating existing synthesis when new sources arrive: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## Primary Sources

- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://obsidian.md/help/links
