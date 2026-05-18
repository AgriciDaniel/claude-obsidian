---
type: concept
title: "Compounding Knowledge"
complexity: basic
domain: knowledge-management
aliases:
  - "Knowledge Compounding"
  - "Persistent Synthesis"
created: 2026-04-07
updated: 2026-04-07
tags:
  - concept
  - knowledge-management
status: mature
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Hot Cache]]"
  - "[[Andrej Karpathy]]"
  - "[[concepts/_index]]"
sources:
---

# Compounding Knowledge

The central insight behind the [[LLM Wiki Pattern]]: knowledge in a wiki compounds like interest in a bank. Every source added, every question answered, every analysis filed makes the wiki more valuable — not just by adding pages, but by enriching the connections between existing pages.

---

## Why Normal AI Chats Don't Compound

In a standard chat, knowledge is ephemeral. Each session starts fresh. Even if you upload the same documents repeatedly, the LLM re-derives the same insights from scratch. Nothing accumulates.

The same is true of most RAG systems: they index raw documents and retrieve chunks at query time. The retrieval gets the right fragments, but no synthesis is built up. Nothing is compiled. Ask the same complex question twice and you get the same assembly process twice.

---

## How Wiki Knowledge Compounds

When a new source arrives, the LLM doesn't just index it. It integrates it:
- Updates entity pages with new information
- Flags contradictions with existing claims
- Strengthens or challenges the evolving synthesis
- Adds cross-references from the new source to existing pages and back

The cross-references are already there next time. The contradictions have already been flagged. The synthesis already reflects everything that was read.

**The wiki is pre-compiled knowledge.** RAG re-compiles on every query.

---

## The Maintenance Problem

Wikis maintained by humans decay. The maintenance burden grows faster than the value — updating cross-references, keeping summaries current, noting when new data contradicts old claims. Humans abandon wikis because no one wants to do the bookkeeping.

LLMs don't get bored. They don't forget to update a cross-reference. The cost of maintenance is near zero. This is the practical reason the wiki pattern works: the entity that's best at the tedious maintenance work is the same entity that reads and writes the wiki.

---

## In Practice

One X user turned 383 scattered files and over 100 meeting transcripts into a compact wiki and dropped token usage by 95% when querying with Claude. The drop came from two sources: better navigation (index + hot cache vs. full document search) and pre-compiled synthesis (no re-deriving the same insights from scratch).

---

## Connections

See [[LLM Wiki Pattern]] for the full architecture.
See [[Hot Cache]] for the session context mechanism.
See [[Andrej Karpathy]] for the origin of this framing.
