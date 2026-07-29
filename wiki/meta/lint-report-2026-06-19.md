---
type: meta
title: "Lint Report 2026-06-19"
created: 2026-06-19
updated: 2026-06-19
tags: [meta, lint, vault-consolidation]
status: developing
---

# Lint Report: 2026-06-19

## Summary

- Wiki pages scanned: 111
- Orphan candidates: 42
- Dead-link references: 109
- Frontmatter gaps: 48
- Empty-section candidates: 88
- Consolidation blockers: 0

The unified vault is structurally operational. Most findings predate consolidation and include documentation examples, archived sessions, intentional project leaves, and generated references. They were not auto-fixed because bulk stubs, links, or deletions would create misleading knowledge.

## Highest-priority review

### Dead links used by navigation

- `[[Wiki Map]]` is referenced by `getting-started.md`, `hot.md`, `index.md`, and sub-indexes.
- `[[How does the LLM Wiki pattern work?]]` is referenced by the hot cache, log, and several concept pages.

### Frontmatter gaps

- `wiki/projects/jobfilter/STICKY-TODO.md`: no frontmatter.
- Several historical audit and session notes lack `created` or `updated`.
- `wiki/meta/tiling-report-2026-04-24.md`: no frontmatter.

### Orphan candidates

Most orphan candidates are dated audits, changelogs, release sessions, or project leaf pages. These require human judgment before linking or archiving.

## Consolidation-specific checks

- Personal notes are isolated under `Personal/`, preventing filename collisions with the generated wiki.
- SwarmVault files are isolated under `Local Knowledge/`.
- JobFilter notes are isolated under `Projects/JobFilter/`.
- Legacy JobFilter content is isolated under `Archive/Legacy JobFilter Vault/`.
- Zawiya was not merged because its private-content boundary requires separate handling.

## Recommended follow-up

1. Create or restore the two missing navigation pages after confirming their intended content.
2. Review orphan project logs in batches rather than linking every historical page.
3. Add frontmatter only when a page is next edited, avoiding a large low-value metadata rewrite.
4. Review SwarmVault candidate pages from `Local Knowledge/` before promotion.
