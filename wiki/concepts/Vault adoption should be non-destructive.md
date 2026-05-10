---
type: concept
title: "Vault adoption should be non-destructive"
created: 2026-05-09
updated: 2026-05-09
tags:
  - concept
  - obsidian
  - migration
  - adoption
status: developing
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Source-First Synthesis]]"
  - "[[ballred-obsidian-claude-pkm]]"
  - "[[cherry-picks]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Vault adoption should be non-destructive

Existing Obsidian users are unlikely to accept an LLM wiki tool that requires them to start over. A stronger adoption pattern scans the current vault, preserves its original structure, then layers agent instructions and generated wiki artifacts around it.

## Extracted Claim

The ecosystem research identifies two comparable adoption approaches:

- `heyitsnoah/claudesidian` safely imports an existing vault into `OLD_VAULT/` before bootstrapping its configured workflow.
- [[ballred-obsidian-claude-pkm]] provides an `/adopt` command that detects PARA, Zettelkasten, LYT, or plain-folder organization and maps the existing structure non-destructively.

## Why It Matters

Non-destructive adoption changes the product question from "Will users migrate to this vault?" to "Can this agent layer improve the vault users already trust?" That matters for mature vaults because folder structure, links, daily notes, plugins, and personal conventions are already part of the knowledge system.

## Design Implication

A vault adoption workflow should:

- inventory folders, note types, attachments, templates, and plugin files before writing
- classify the organizing method without assuming a fresh scaffold
- propose mappings from existing folders to wiki roles
- create agent-owned generated areas without moving private source material unexpectedly
- preserve a reversible path such as `OLD_VAULT/`, an adoption manifest, or a dry-run report

## Boundaries

This is different from [[Source-First Synthesis]]. Source-first synthesis protects raw evidence during ingest; non-destructive adoption protects a user's existing vault during setup and migration.
