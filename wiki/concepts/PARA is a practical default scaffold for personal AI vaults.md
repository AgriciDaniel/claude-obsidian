---
type: concept
title: "PARA is a practical default scaffold for personal AI vaults"
created: 2026-05-09
updated: 2026-05-09
tags:
  - concept
  - obsidian
  - pkm
  - para
status: developing
related:
  - "[[Mode D Personal Second Brain]]"
  - "[[Vault adoption should be non-destructive]]"
  - "[[ballred-obsidian-claude-pkm]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# PARA is a practical default scaffold for personal AI vaults

PARA works well as a default Obsidian scaffold for AI-assisted personal knowledge management because it gives agents simple routing categories: inbox, active projects, maintained areas, reusable resources, and archive.

## Extracted Claim

The ecosystem research identifies `heyitsnoah/claudesidian` as using a PARA folder structure:

- `00_Inbox`
- `01_Projects`
- `02_Areas`
- `03_Resources`
- `04_Archive`

It also notes that [[ballred-obsidian-claude-pkm]] can detect PARA during vault adoption.

## Why It Matters

PARA gives an agent a low-friction filing policy without requiring a fully custom ontology upfront. It is especially useful for personal second-brain vaults where notes mix goals, projects, reference material, and archived context.

## Relationship to Mode D

[[Mode D Personal Second Brain]] already uses goals, learning, people, areas, and resources. PARA is not a replacement for that mode, but it is a useful compatibility target when adopting an existing personal vault or designing a starter scaffold that users already recognize.

## Design Implication

AI vault tools should treat PARA as a common detected structure, not as the only valid structure. During adoption, the agent should map PARA folders to wiki responsibilities instead of forcing a new directory tree.
