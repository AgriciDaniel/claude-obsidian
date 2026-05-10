---
type: concept
title: "AI vault tools need separate thinking and writing modes"
created: 2026-05-09
updated: 2026-05-09
tags:
  - concept
  - obsidian
  - agent-workflow
  - writing
status: developing
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Source-First Synthesis]]"
  - "[[cherry-picks]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# AI vault tools need separate thinking and writing modes

Claude + Obsidian tools serve two different jobs: private reasoning over the vault and durable writing into the vault. Treating both as one mode increases the risk that exploratory thoughts become permanent notes or that polished notes hide unresolved reasoning.

## Extracted Claim

The ecosystem research highlights `heyitsnoah/claudesidian` as distinguishing Thinking Mode from Writing Mode. That distinction is useful beyond that project because Obsidian vaults are both workspaces and archives.

## Thinking Mode

Thinking Mode is for exploration, synthesis, critique, planning, and comparison. It can read broadly, create temporary outlines, challenge assumptions, and surface uncertainty without committing every intermediate step to the wiki.

## Writing Mode

Writing Mode is for durable artifacts: source summaries, concept notes, entity pages, index updates, and dated logs. It should apply [[Source-First Synthesis]], use wikilinks, avoid duplicate pages, and make provenance explicit.

## Design Implication

Agent skills should make write boundaries explicit. A query or planning skill can reason freely, but ingest, save, and fold operations should declare which files are durable outputs and which notes are source-backed synthesis.
