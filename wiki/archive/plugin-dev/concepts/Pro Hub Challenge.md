---
type: concept
title: "Pro Hub Challenge"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - community
  - ai-marketing-hub
  - claude-seo
  - open-source
status: evergreen
related:
  - "[[Claude SEO]]"
  - "[[2026-04-14-claude-seo-v190-session]]"
  - "[[Semantic Topic Clustering]]"
  - "[[Search Experience Optimization]]"
---

# Pro Hub Challenge

A community challenge hosted in the [AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro) Skool community where members build extensions for Claude SEO or Claude Blog, competing for $600 in Claude Credits.

## First Challenge (v1.9.0, April 2026)

**6 submissions, 5 scored Proficient or above**

| Contributor | Submission | Score | Integrated? |
|------------|------------|-------|-------------|
| Lutfiya Miller | Semantic Cluster Engine | Winner | Yes — `seo-cluster` |
| Florian Schmitz | SXO Skill | Proficient | Yes — `seo-sxo` |
| Dan Colta | SEO Drift Monitor | Proficient | Yes — `seo-drift` |
| Chris Muller | Multi-lingual Blog | Proficient | Partial — SEO parts into `seo-hreflang` |
| Matej Marjanovic | E-commerce + Cost Config | Proficient | Yes — `seo-ecommerce` + cost guardrails |
| Benjamin Samar | SEO Dungeon | Reviewed | No — not integrated in v1.9.0 |

## Integration Pattern

Community submissions go through:
1. **Full code review** — architecture, quality, security
2. **Security audit** — SSRF, injection, credential handling
3. **Cherry-pick** — only SEO-relevant parts for claude-seo, blog parts stay for claude-blog
4. **De-brand** — remove contributor-specific branding (e.g., ScienceExperts.ai)
5. **Attribution** — `original_author` in SKILL.md frontmatter, HTML comments in agents, CONTRIBUTORS.md

## Submission Guidelines (from CONTRIBUTING.md)

1. SKILL.md under 500 lines, references under 200 lines
2. All scripts must import `validate_url()` for SSRF protection
3. Include `original_author` in SKILL.md frontmatter metadata
4. Submit via PR or post in AI Marketing Hub community

## Second Challenge (April 2026)

**Keyword**: LEADS
**Prize pool**: $600 ($400 first place, $200 second place) in Claude Credits
**Deadline**: April 28, 2026
**Scope**: Anything touching lead generation — Claude Code skills, n8n workflows, MCP servers, scrapers, dashboards, pipelines. If it helps someone capture, qualify, nurture, or convert leads, it counts.
**Rules**: GitHub repo or .zip file + 1-2 minute demo video. Must be functional (not a concept). Solo or team both welcome.
**Previous winner**: Lutfiya Miller (seo-cluster, integrated in v1.9.0)
