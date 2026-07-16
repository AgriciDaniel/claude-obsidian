# Article Home — Ingest Workflow

> Referenced by `SKILL.md`. This file defines the Article Home output step in the ingest pipeline.
> Canonical structure spec: `CLAUDE.md §Article Home`.

---

## When to create

An Article Home is created for **every source ingested** (files, URLs, images). There is one Article Home per source; re-ingest updates the existing page rather than creating a new one.

## Placement

```
wiki/articles/<slug>-home.md
```

Resolve `<slug>` from the source filename or URL: lowercased, spaces→hyphens, strip query strings and file extension. Append `-home` suffix to distinguish from other wiki page types.

## Pipeline location (Step 3 + Step 7)

Article Home creation spans **two** pipeline steps:

### Step 3 — Create (initial)

Immediately after reading and discussing the source, **before** creating source summary (Step 4), entity pages (Step 5), and concept pages (Step 6).

At Step 3, concept/entity pages don't exist yet. Write wikilinks as planned red links — they render as red in Obsidian, which is intentional (they populate the "待补知识 / 红链候选" section).

### Step 7 — Finalize

After source summary, entity pages, and concept pages are created (Steps 4–6):

1. Update "值得沉淀的 wiki 页面" section: replace planned wikilinks with actual page titles (e.g. `[[Planned Concept]]` → `[[Actual Concept Page]]`)
2. Confirm all backlinks from Steps 4–6 point correctly to the Article Home
3. Update "红链候选" — demote links that now have real pages, keep only genuine red links

This two-phase approach ensures the Article Home is both created early (as an entry point) and accurate after downstream pages exist.

## Mandatory output fields

Every Article Home MUST include all 10 sections defined in `CLAUDE.md §Article Home`:

1. 先说结论
2. 目录地图
3. 像人讲一遍
4. 上游与下游
5. 关键概念怎么连起来
6. 值得沉淀的 wiki 页面
7. 待补知识 / 红链候选
8. 后续可问的问题
9. 以后怎么查回来
10. 人类判断区

See `_templates/article-home.md` for the exact reference structure.

## YAML frontmatter

```yaml
---
type: article-home
title: "<slug>-home"
source_title: ""
source_url: ""
author: ""
date_published: ""
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - article-home
status: seed
reading_priority: medium
related: []
sources:
  - "[[.raw/articles/<source-file>.md]]"
---
```

## Backlinks from downstream pages

Pages created in subsequent steps MUST backlink to the Article Home:

| Step | Page type | Backlink requirement |
|------|-----------|---------------------|
| 4 | Source summary `wiki/sources/` | MUST include `[[<slug>-home]]` |
| 5 | Entity pages `wiki/entities/` | MUST include `[[<slug>-home]]` |
| 6 | Concept pages `wiki/concepts/` | MUST include `[[<slug>-home]]` |

This ensures the Article Home is discoverable from both directions.

## log.md entry

Append an Article Home line to every ingest log entry:

```markdown
## [YYYY-MM-DD] ingest | Source Title
- Source: `.raw/articles/filename.md`
- Article Home: [[<slug>-home]]
- Summary: [[Source Title]]
- Pages created: [[Page 1]], [[Page 2]]
- Pages updated: [[Page 3]], [[Page 4]]
- Key insight: One sentence on what is new.
```

## Batch ingest

When processing multiple sources, defer Article Home cross-linking to the cross-reference pass (Step 3 in batch flow). Cross-link Article Homes where topics overlap.

## Reference

- Structure: `CLAUDE.md §Article Home`
- Template: `_templates/article-home.md`
- Insights layer: `WIKI.md §Conventions`
