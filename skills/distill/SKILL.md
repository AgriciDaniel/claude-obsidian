---
name: distill
description: >
  Post-ingest knowledge distillation. Analyzes connections between newly
  ingested content and existing wiki. Finds contradictions, concept
  co-occurrences, red links, updates cross-references. Runs automatically
  after each ingest. Also supports /distill <file>.
allowed-tools: Read Write Edit Glob Grep Bash
---

# distill: Knowledge Distillation Engine

Runs after every wiki ingest (or via `/distill <file>`).
Finds connections between new content and existing wiki, detects
contradictions, tracks concept co-occurrences, identifies expansion opportunities.

## Two Trigger Modes

### Mode A: Post-ingest (default)
Runs automatically after ingest completes. New source + concept/entity pages
are the input.

### Mode B: Manual (`/distill <path>`)
Human invokes with any file path. Same pipeline applies.

## Distillation Pipeline (4 Lenses)

### Lens 1: Nexus — Connection Scan
For each new concept page, scan existing wiki for same-topic references.
Update wikilinks on both new and existing pages. Note cross-domain connections.

### Lens 2: Prism — Contradiction & Gap Detection
Compare claims in new source against existing wiki pages.
Flag direct contradictions, temporal shifts, perspective differences.
Add [!contradiction] callouts to affected pages.

### Lens 3: Ember — Co-occurrence Tracking
Extract concept pairs from new source.
Update wiki/books/density-tracker.md.
Flag any pair where count >= 5 (Phase 4 crystalization threshold).

### Lens 4: Vector — Red Link Identification
Find named concepts/entities without pages yet.
Rank by frequency across wiki: >=2 mentions = HIGH priority.

## Final Report
Appended to wiki/log.md with sections:
- Connections Found
- Contradictions
- Co-occurrence Updates
- Red Links (missing pages)

## Phase 3 Collection Toggle
When Phase 3 collection layer is activated, this distill skill also processes
auto-collected .raw/aihot/*.md briefings through the same 4-lens pipeline.
