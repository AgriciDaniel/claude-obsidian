# Frontmatter Schema

Every wiki page starts with flat YAML frontmatter. No nested objects. Obsidian's Properties UI requires flat structure.

---

## Universal Fields

Every page, no exceptions:

```yaml
---
type: <source|entity|concept|domain|comparison|question|overview|meta|module|component|dependency|flow|decision>
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
  - "[[.raw/articles/source-file.md]]"
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
source_type: article    # article | video | podcast | paper | book | transcript | data | code
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

### module / component / dependency / flow / decision (Mode B code pages)

Code pages document a slice of a codebase. They are created and kept in sync by
`/wiki-code-ingest`. Add these after the universal fields:

```yaml
source_type: code       # marks this as a code-derived page
status: active          # active | deprecated | experimental | planned
language: ""            # primary language; "" when mixed/unknown
purpose: ""             # one-line "what this is for"
source_paths:           # repo-relative file/dir paths this page documents
  - "src/auth/"
code_anchors:           # FLAT list, one "path@sha" per source_path (git blob/tree SHA at ingest)
  - "src/auth/@<tree-or-blob-sha>"
ingest_commit: ""       # repo HEAD (full 40-char SHA) when anchors were captured
ingested_at: YYYY-MM-DD # date the anchors were captured
depends_on:             # intra-repo modules this one imports (wikilinks)
  - "[[Other Module]]"
used_by:                # reverse edges (wikilinks)
  - "[[Caller Module]]"
```

The drift lint (`wiki-lint`) compares each `code_anchors` entry against the current
`git rev-parse HEAD:<path>` to flag pages whose source changed since ingest. Anchors are
encoded as flat `path@sha` strings (split on the LAST `@`) to honor the flat-YAML rule (#1) —
never a nested map. `git rev-parse HEAD:<path>` returns a *blob* SHA for files and a *tree*
SHA for directories; the lint compares whichever git returns, so directory anchors are stable.

---

## Rules

1. Use flat YAML only. Never nest objects.
2. Dates as `YYYY-MM-DD` strings, not ISO datetime.
3. Lists always use the `- item` format, not inline `[a, b, c]`.
4. Wikilinks in YAML fields must be quoted: `"[[Page Name]]"`.
5. Keep `related` and `sources` as wikilinks, not plain URLs.
6. Update `updated` every time you edit the page content.
