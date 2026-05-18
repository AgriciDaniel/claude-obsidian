---
type: entity
title: "Claude SEO"
created: 2026-04-14
updated: 2026-04-15
tags:
  - entity
  - project
  - claude-code
  - seo
status: evergreen
related:
  - "[[Pro Hub Challenge]]"
  - "[[2026-04-14-claude-seo-v190-session]]"
  - "[[Semantic Topic Clustering]]"
  - "[[Search Experience Optimization]]"
  - "[[SEO Drift Monitoring]]"
  - "[[E-commerce SEO]]"
  - "[[2026-04-15-slides-and-release-session]]"
  - "[[2026-04-15-release-report-session]]"
---

# Claude SEO

A Tier 4 Claude Code skill for comprehensive SEO analysis across all industries. Repository: [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)

## Current State (v1.9.0 — released April 15, 2026)

- **23 skills** (20 core + 3 extensions: DataForSEO, Firecrawl, Banana)
- **17 subagents** (15 core + 2 extension agents)
- **30 Python scripts** (28 tracked + 2 dev-only)
- **Architecture**: 3-layer (directive, orchestration, execution)
- **Entry point**: `/seo [command] [url]`
- **GitHub release**: [v1.9.0](https://github.com/AgriciDaniel/claude-seo/releases/tag/v1.9.0) — PDF report attached
- **Slides**: `claude-seo-slides/v190.html` — 15-slide community presentation deck
- **Contributors**: 6 submissions, 5 integrated (Lutfiya Miller, Florian Schmitz, Dan Colta, Matej Marjanovic, Chris Muller)

## Key Commands

| Category | Commands |
|----------|----------|
| Analysis | audit, page, technical, content, schema, images, geo |
| Planning | plan, cluster, sxo, programmatic, competitor-pages |
| Monitoring | drift baseline, drift compare, drift history |
| Local | local, maps |
| International | hreflang (with cultural profiles) |
| E-commerce | ecommerce |
| Data | google, backlinks, dataforseo |
| Generation | sitemap, image-gen |

## Version History

| Version | Date | Key Addition |
|---------|------|-------------|
| v1.9.0 | 2026-04-15 | Pro Hub Challenge: cluster, SXO, drift, ecommerce, cost guardrails, cultural profiles. GitHub release + PDF report + 15-slide deck. |
| v1.8.2 | 2026-04-10 | Ukrainian localization, CI fixes, version sync |
| v1.8.1 | 2026-04-06 | Google Images SERP, image optimization |
| v1.8.0 | 2026-03-31 | Free backlink data (Moz, Bing, Common Crawl) |
| v1.7.0 | 2026-03-28 | Google SEO APIs (GSC, PageSpeed, CrUX, GA4) |

## Ecosystem

- [[Claude SEO]] — SEO analysis (this project)
- Claude Blog — companion blog engine, consumes SEO findings
- Claude Banana — AI image generation, bundled as extension
- AI Marketing Claude — community marketing suite by Zubair Trabzada

## Security Posture (v1.9.0 audit)

- **Score**: 85/100 (Grade B+)
- **SSRF protection**: validate_url() + fetch_page.py DNS resolution
- **SQL**: all queries parameterized
- **Cost guardrails**: threshold approval, daily limits, file locking, audit trail
- **Pre-existing debt**: validate_url DNS rebinding gap, install script injection, OAuth file permissions
