---
type: concept
title: "Search Experience Optimization (SXO)"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - seo
  - ux
  - serp-analysis
status: evergreen
related:
  - "[[Claude SEO]]"
  - "[[Pro Hub Challenge]]"
  - "[[Semantic Topic Clustering]]"
---

# Search Experience Optimization (SXO)

A methodology that reads SERPs backwards to detect page-type mismatches, derives user stories from search features, and scores pages from persona perspectives. Contributed to [[Claude SEO]] v1.9.0 by Florian Schmitz.

## Core Insight

> "Read SERPs backwards" — instead of optimizing content FOR the SERP, analyze WHAT the SERP tells you about user expectations, then check if your page meets them.

## Process

1. **Page-type detection** — classify the URL as one of 8 types (Landing, Blog, Product, Hybrid, Service, Comparison, Local, Tool)
2. **SERP pattern matching** — compare what Google shows (featured snippets, PAA, ads, related searches) against what the page provides
3. **Mismatch detection** — if SERP says "users want comparison" but page is "product page", that's a mismatch
4. **User story derivation** — from SERP features, derive 4-7 personas with emotional states, barriers, goals
5. **Persona scoring** — score the page from each persona's perspective (0-100 across 4 dimensions)
6. **Wireframe generation** — IST (current) vs SOLL (ideal) wireframes with ultra-concrete placeholders

## Key Innovation

Most SEO tools analyze pages in isolation. SXO uses the SERP as a proxy for user intent — the SERP IS the research that Google already did about what users want. This makes the analysis data-driven without needing user testing.

## Command

```
/seo sxo <url>
/seo sxo wireframe <url>
```
