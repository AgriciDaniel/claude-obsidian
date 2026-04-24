---
type: meta
title: "Boundary Frontier Snapshot (2026-04-24)"
updated: 2026-04-24
tags:
  - meta
  - dragonscale
  - mechanism-4
status: snapshot
related:
  - "[[DragonScale Memory]]"
  - "[[log]]"
  - "[[hot]]"
---

# Boundary Frontier Snapshot (2026-04-24)

Navigation: [[index]] | [[log]] | [[DragonScale Memory]]

First end-to-end run of DragonScale Mechanism 4 (`scripts/boundary-score.py`) against this vault. Generated from `./scripts/boundary-score.py --json --top 7` at 2026-04-24T08:49:16Z.

## What this is

This is a scoring snapshot, not a prescription. The boundary score heuristic surfaces pages that are outward-pointing and recently-touched as candidates for `/autoresearch` to extend. It is explicitly agenda-control per the [[DragonScale Memory]] spec, v0.4, Mechanism 4: the ranking shapes what the agent researches next, and a user should accept, override, or decline any candidate.

Formula: `boundary_score(p) = (out_degree(p) - in_degree(p)) * exp(-age_days / 30)`.

No recency floor. Pages older than ~90 days approach zero weight by design, so a stale hub does not dominate the frontier.

## Frontier (top 7, score > 0)

| # | score | out | in | age_d | title | path |
|---|---|---|---|---|---|---|
| 1 | 4.693 | 8 | 0 | 16 | Claude + Obsidian Ecosystem Research | wiki/sources/claude-obsidian-ecosystem-research.md |
| 2 | 4.000 | 4 | 0 | 0 | DragonScale Memory | wiki/concepts/DragonScale Memory.md |
| 3 | 1.702 | 3 | 0 | 17 | How does the LLM Wiki pattern work? | wiki/questions/How does the LLM Wiki pattern work.md |
| 4 | 1.135 | 2 | 0 | 17 | Wiki vs RAG | wiki/comparisons/Wiki vs RAG.md |
| 5 | 0.717 | 1 | 0 | 10 | SEO Drift Monitoring | wiki/concepts/SEO Drift Monitoring.md |
| 6 | 0.717 | 1 | 0 | 10 | Search Experience Optimization (SXO) | wiki/concepts/Search Experience Optimization.md |
| 7 | 0.717 | 1 | 0 | 10 | Semantic Topic Clustering | wiki/concepts/Semantic Topic Clustering.md |

22 scoreable pages total (meta, fold, and index pages excluded).

## Reading the result

- Row 1 is the ecosystem research source. It links out to eight entity pages and is not linked back, which is expected for a raw source: it seeds the graph rather than being referenced by it. The score is correct; following this candidate would extend one of its eight entities rather than re-examining the source itself.
- Row 2 (DragonScale Memory) has age_days=0 and zero in-degree. This is a fresh concept page not yet linked back by any discussion. A legitimate frontier signal.
- Rows 3-7 are older pages (~10 to 17 days) with modest out-degree. The recency decay correctly damps them relative to fresh pages.
- No page ranks on pure recency with zero out-degree, because the formula multiplies degree-delta by recency.

## Calibration note

The halflife of 30 days was chosen as a default, not a tuned value. If this vault grows past ~100 pages and out-degree patterns change, the halflife should be reviewed alongside the weighting between degree and recency. The [[DragonScale Memory]] spec explicitly tags these as seed values, not literature-backed.

## Reproduce

```
./scripts/boundary-score.py --json --top 7
```

Read-only. Requires python3 only. No DragonScale setup needed to run the scorer itself.

## Connections

- [[DragonScale Memory]] — spec, Mechanism 4
- [[log]] — operation log
- [[hot]] — recent context
