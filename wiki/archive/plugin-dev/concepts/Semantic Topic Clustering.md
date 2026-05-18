---
type: concept
title: "Semantic Topic Clustering"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - seo
  - content-strategy
  - clustering
status: evergreen
related:
  - "[[Claude SEO]]"
  - "[[Pro Hub Challenge]]"
  - "[[Search Experience Optimization]]"
---

# Semantic Topic Clustering

SERP-based keyword grouping that replaces paid tools ($50-200/month) with Claude's reasoning. Contributed to [[Claude SEO]] v1.9.0 by Lutfiya Miller (Pro Hub Challenge Winner).

## How It Works

1. **Seed keyword** provided by user
2. **SERP fetching** — get Google results for the seed and related terms (via WebSearch or DataForSEO)
3. **Overlap scoring** — compare top-10 results between keyword pairs:
   - 7-10 overlapping URLs = same post (keyword cannibalization)
   - 4-6 overlapping = same cluster (supporting content)
   - 2-3 overlapping = interlink opportunity
   - 0-1 overlapping = separate clusters
4. **Hub-spoke architecture** — 1 pillar page (2500-4000 words) + 2-5 clusters + 2-4 posts each
5. **Internal link matrix** — bidirectional linking plan with backward link injection
6. **Visualization** — interactive cluster-map.html (SVG, dark mode, keyboard accessible)

## Key Design Decisions

- **No Python scripts** — clustering is prompt-driven (Claude's reasoning + WebSearch)
- **Optional execution** — outputs content briefs when claude-blog isn't installed, full pipeline when it is
- **Resume capability** — for long multi-post execution runs
- **DataForSEO integration** — uses `serp_organic_live_advanced` for live SERP data when available (with cost check)

## Command

```
/seo cluster <seed-keyword>
```
