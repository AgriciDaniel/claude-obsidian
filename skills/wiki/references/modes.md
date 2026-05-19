# Wiki Modes

Six modes cover the most common use cases. Pick the one that fits, or combine them.

---

## Mode A: Website / Sitemap

Use when: "build a sitemap wiki for my website", "map content gaps", "SEO audit wiki"

```
vault/
├── raw/              # crawl exports, analytics, scraped pages, GSC data
├── wiki/
│   ├── pages/         # one note per URL: status, meta, content summary
│   ├── structure/     # site architecture, nav hierarchy, internal link map
│   ├── audits/        # content gaps, redirect needs, thin content flags
│   ├── keywords/      # keyword clusters, target page assignments
│   └── entities/      # brand, authors, topic hubs
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

Frontmatter for `wiki/pages/` notes:
```yaml
---
type: page
url: "https://example.com/page-slug"
status: live          # live | redirect | 404 | stub | no-index
title: ""
h1: ""
meta_description: ""
word_count: 0
has_schema: false
indexed: true
canonical: ""
internal_links_in: 0
internal_links_out: 0
last_crawled: YYYY-MM-DD
tags: [page]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Key wiki pages to create: `[[Site Overview]]`, `[[Navigation Structure]]`, `[[Content Gaps]]`, `[[Redirect Map]]`, `[[Keyword Clusters]]`

---

## Mode B: GitHub / Repository

Use when: "map my codebase", "architecture wiki for my repo", "understand this project"

```
vault/
├── raw/              # README, git log exports, code dumps, issue exports
├── wiki/
│   ├── modules/       # one note per major module / package / service
│   ├── components/    # reusable UI or functional components
│   ├── decisions/     # Architecture Decision Records (ADRs)
│   ├── dependencies/  # external deps, versions, risk assessment
│   └── flows/         # data flows, request paths, auth flows
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

Frontmatter for `wiki/modules/` notes:
```yaml
---
type: module           # module | component | decision | dependency | flow
path: "src/auth/"
status: active         # active | deprecated | experimental | planned
language: typescript
purpose: ""
maintainer: ""
last_updated: YYYY-MM-DD
linked_issues: []
depends_on: []
used_by: []
tags: [module]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Key wiki pages to create: `[[Architecture Overview]]`, `[[Data Flow]]`, `[[Tech Stack]]`, `[[Dependency Graph]]`, `[[Key Decisions]]`

---

## Mode C: Business / Project

Use when: "project wiki", "competitive intelligence", "team knowledge base", "meeting notes"

```
vault/
├── raw/              # meeting transcripts, Slack exports, docs, emails
├── wiki/
│   ├── stakeholders/  # people, companies, decision-makers
│   ├── decisions/     # key decisions with rationale and date
│   ├── deliverables/  # milestones, outputs, status tracking
│   ├── intel/         # competitor analysis, market research
│   └── comms/         # synthesized meeting notes, key threads
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

Frontmatter for `wiki/decisions/` notes:
```yaml
---
type: decision         # stakeholder | decision | deliverable | intel | meeting | competitor
status: active         # active | pending | done | blocked | superseded
priority: 3            # 1 (highest) to 5 (lowest)
date: YYYY-MM-DD
owner: ""
due_date: ""
context: ""
tags: [decision]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Key wiki pages to create: `[[Project Overview]]`, `[[Stakeholder Map]]`, `[[Decision Log]]`, `[[Competitor Landscape]]`

---

## Mode D: Personal / Second Brain

Use when: "personal second brain", "track my goals", "journal synthesis", "life wiki"

```
vault/
├── raw/              # journal entries, articles, podcast notes, voice transcripts
├── wiki/
│   ├── goals/         # personal and professional goals with progress tracking
│   ├── learning/      # concepts being mastered, skill development
│   ├── people/        # relationships, shared context, follow-ups
│   ├── areas/         # life areas: health, finances, career, creative
│   └── resources/     # books, courses, tools worth referencing
├── _meta/
│   ├── index.md
│   ├── log.md
│   └── hot-cache.md   # ~500-word summary of most active context
└── CLAUDE.md
```

Frontmatter for `wiki/goals/` notes:
```yaml
---
type: goal             # goal | concept | person | area | resource | reflection
status: active         # active | paused | completed | abandoned
area: career           # health | career | finance | creative | relationships | growth
priority: 1
target_date: YYYY-MM-DD
progress: 0            # 0-100 percent
tags: [goal]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Hot cache note: `_meta/hot-cache.md` is a ~500-word file Claude updates at the end of each session. It captures current focus areas, recent wins, and open threads. This prevents Claude from having to crawl the whole wiki to answer "where were we?".

Key wiki pages to create: `[[North Star]]`, `[[Weekly Review Template]]`, `[[Annual Goals]]`

---

## Mode E: Research

Use when: "research wiki on [topic]", "track papers I'm reading", "build a thesis"

```
vault/
├── raw/              # PDFs, web clips, data files, raw notes
├── wiki/
│   ├── papers/        # paper summaries with key claims and methodology
│   ├── concepts/      # extracted concepts, models, frameworks
│   ├── entities/      # people, organizations, methods, datasets
│   ├── thesis/        # evolving synthesis: the "state of the field" pages
│   └── gaps/          # open questions, contradictions, research needed
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

Frontmatter for `wiki/papers/` notes:
```yaml
---
type: paper            # paper | concept | entity | thesis | gap
status: summarized     # raw | summarized | synthesized | superseded
year: 2024
authors: []
venue: ""
key_claim: ""
methodology: ""
contradicts: []
supports: []
tags: [paper]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Key wiki pages to create: `[[Research Overview]]`, `[[Key Claims Map]]`, `[[Open Questions]]`, `[[Methodology Comparison]]`

---

## Mode F: Book / Course

Use when: "companion wiki for a book", "course notes wiki", "as I read [title]"

```
vault/
├── raw/              # chapter notes, highlights, exercises
├── wiki/
│   ├── characters/    # characters, personas, agents, experts (adapt to content)
│   ├── themes/        # major themes with supporting evidence
│   ├── concepts/      # domain-specific terms and frameworks
│   ├── timeline/      # plot structure, curriculum sequence, chapter map
│   └── synthesis/     # your own takeaways, questions, applications
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

Frontmatter for `wiki/concepts/` notes:
```yaml
---
type: concept          # concept | character | theme | chapter | synthesis
status: developing     # stub | developing | mature
source_chapters: []
first_appearance: ""
tags: [concept]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Key wiki pages to create: `[[Book Overview]]`, `[[Theme Map]]`, `[[Character / Expert Index]]`, `[[My Takeaways]]`

---

## Combining Modes

You can combine modes. Examples:

- "GitHub repo + research on the AI approach used" -> Mode B folders + Mode E papers/ folder
- "My SaaS business + second brain" -> Mode C intel/ + Mode D goals/
- "YouTube channel" -> Mode F (content as "book") + Mode E (research on topics covered)

When combining, keep folder names distinct. Don't merge `decisions/` from Mode B and Mode C into one folder.
