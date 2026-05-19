# Frontmatter Schema

Every wiki page starts with flat YAML frontmatter. No nested objects. Obsidian's Properties UI requires flat structure.

---

## Universal Fields

Every page, no exceptions:

```yaml
---
type: <source|entity|concept|domain|comparison|question|overview|meta>
title: "Human-Readable Title"
created: 2026-04-07
updated: 2026-04-07
tags:
  - <domain-tag>
  - <type-tag>
status: <seed|developing|mature|evergreen>
related:
  - "[[Other Page]]"
sources:
  - "[[raw/articles/source-file.md]]"
---
```

**status values:**
- `seed`: exists, barely populated
- `developing`: has real content, not yet complete
- `mature`: comprehensive, well-linked
- `evergreen`: unlikely to need updates

---

## Type-Specific Additions

### source

Add these fields after the universal fields:

```yaml
source_type: article    # article | video | podcast | paper | book | transcript | data
author: ""
date_published: YYYY-MM-DD
url: ""
confidence: high        # high | medium | low
key_claims:
  - "First key claim from this source"
  - "Second key claim"
```

### entity

```yaml
entity_type: person     # person | organization | product | repository | place
role: ""
first_mentioned: "[[Source Title]]"
```

### concept

```yaml
complexity: intermediate  # basic | intermediate | advanced
domain: ""
aliases:
  - "alternative name"
  - "abbreviation"
```

### comparison

```yaml
subjects:
  - "[[Thing A]]"
  - "[[Thing B]]"
dimensions:
  - "performance"
  - "cost"
  - "ease of use"
verdict: "One-line conclusion."
```

### question

```yaml
question: "The original query as asked."
answer_quality: solid   # draft | solid | definitive
```

### domain

```yaml
subdomain_of: ""        # leave empty for top-level domains
page_count: 0
```

---

## Rules

1. Use flat YAML only. Never nest objects.
2. Dates as `YYYY-MM-DD` strings, not ISO datetime.
3. Lists always use the `- item` format, not inline `[a, b, c]`.
4. Wikilinks in YAML fields must be quoted: `"[[Page Name]]"`.
5. Keep `related` and `sources` as wikilinks, not plain URLs.
6. Update `updated` every time you edit the page content.
