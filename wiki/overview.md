---
type: overview
title: "Wiki Overview"
created: 2026-04-07
updated: 2026-04-07
tags:
  - meta
  - overview
status: developing
related:
  - "[[index]]"
  - "[[hot]]"
  - "[[log]]"
  - "[[dashboard]]"
  - "[[LLM Wiki Pattern]]"
sources:
---

# Wiki Overview

Navigation: [[index]] | [[hot]] | [[log]] | [[dashboard]]

---

## Purpose

This is the claude-obsidian demo vault. It demonstrates the [[LLM Wiki Pattern]] — a system for building persistent, compounding knowledge bases using Claude and Obsidian.

Run `/wiki` to scaffold this vault for your own domain and replace this overview.

---

## Current Seed Content


**Concepts seeded:**
- [[LLM Wiki Pattern]] — the core architecture
- [[Hot Cache]] — session context mechanism
- [[Compounding Knowledge]] — why the pattern works

**Entities seeded:**
- [[Andrej Karpathy]] — originated the pattern

**Sources seeded:**
- [[claude-obsidian-ecosystem-research]] — 16+ projects, 13 cherry-picks identified (2026-04-08)

---

## Current State

- Sources ingested: 2
- Wiki pages: 26
- Last activity: 2026-04-08 (v1.4.1 shipped, release session filed)

---

## Canvases

- [[claude-obsidian-presentation]] — Full presentation: hero, overview, skills, architecture, Wiki vs RAG, visual demos (2026-04-07)

---

## Key Themes

**Knowledge compounds.** Unlike RAG, the wiki pre-compiles synthesis. Cross-references are already there. Contradictions are flagged. Every ingest enriches existing pages rather than adding isolated chunks.

**The hot cache is the force multiplier.** A ~500-word file captures recent context. New sessions start with full context at minimal token cost.

**Obsidian is the IDE, Claude is the programmer.** The graph view shows what's connected. The human curates sources and asks questions. Claude writes and maintains everything else.
