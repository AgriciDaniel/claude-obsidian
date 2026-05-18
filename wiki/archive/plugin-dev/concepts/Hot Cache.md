---
type: concept
title: "Hot Cache"
complexity: basic
domain: knowledge-management
aliases:
  - "hot.md"
  - "Session Cache"
  - "Context Cache"
created: 2026-04-07
updated: 2026-04-07
tags:
  - concept
  - knowledge-management
  - context
status: mature
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[index]]"
  - "[[hot]]"
  - "[[concepts/_index]]"
sources:
---

# Hot Cache

A ~500-word summary of the most recent context in the wiki vault. Stored in `wiki/hot.md`. Updated at the end of every session and after every significant ingest or query.

The hot cache exists to answer one question: "where did we leave off?" A new session reads `hot.md` first. If the answer is there, it skips crawling the rest of the wiki.

---

## What It Stores

- What was most recently ingested or discussed
- Key recent facts and takeaways
- Pages recently created or updated
- Active threads and open questions
- What the user is currently focused on

---

## Format

```markdown
---
type: meta
title: "Hot Cache"
updated: YYYY-MM-DDTHH:MM:SS
---

# Recent Context

## Last Updated
YYYY-MM-DD — [what happened]

## Key Recent Facts
- [Most important recent takeaway]
- [Second]

## Recent Changes
- Created: new wiki pages from this ingest
- Updated: existing pages with new connections
- Flagged: contradictions between sources where found

## Active Threads
- User is researching [topic]
- Open question: [thing being investigated]
```

---

## Rules

- Keep it under 500 words. It is a cache, not a journal.
- Overwrite it completely each time. Not append-only.
- One file. Not split by date.
- Updated after every ingest, significant query, and at the end of each session.

---

## Why It Matters

Without the hot cache, every session starts cold: read the index (1000 tokens), read several domain sub-indexes, read several individual pages. With the hot cache, the first 500 tokens often have everything needed.

In practice, adding `hot.md` to an executive assistant vault dramatically reduces the token cost of session startup compared to crawling multiple wiki pages.

The hot cache is especially valuable in cross-project setups: another Claude Code project can point at this vault and read `hot.md` first to get recent context at minimal token cost.

---

## Connections

The hot cache is part of the [[LLM Wiki Pattern]] token discipline strategy. See [[index]] for how the broader navigation works.
