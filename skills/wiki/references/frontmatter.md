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
  - "[[.raw/articles/source-file.md]]"
---
```

**status values:**
- `seed`: exists, barely populated
- `developing`: has real content, not yet complete
- `mature`: comprehensive, well-linked
- `evergreen`: unlikely to need updates

---

## Bilingual Terminology Fields (opt-in)

When the vault opts into the Bilingual Terminology Policy (see `docs/bilingual-terminology-policy.md`), pages that preserve a native-language term carry two additional fields:

```yaml
dnt_class: term-of-art   # term-of-art | eigenname | coined | hybrid
lang: de                 # ISO 639-1 code for the native language; default "en" (and field can be omitted)
```

**dnt_class values:**
- `term-of-art`: defined legal, regulatory, or institutional meaning (`AGB`, `Geschäftsführer`, `Gewerbesteuer`).
- `eigenname`: institution, statute, or scheme without equivalent (`IHK`, `BGB`, `Mittelstand-Digital-Zentrum`).
- `coined`: the wiki's internal vocabulary (project names, conventions).
- `hybrid`: bilingual compound where the compound itself is the unit of meaning (`KI-Berater`, `AI-Engineer-Rolle-DE`).

When `dnt_class` is set, the `aliases:` field **must** contain both the native form and the English gloss. Lint enforces this deterministically (`scripts/lint-terminology.py`).

Translatable pages omit both fields. Default = translatable.

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
aliases:                # required when dnt_class is set; otherwise optional
  - "alternative name"
  - "english gloss"
```

### concept

```yaml
complexity: intermediate  # basic | intermediate | advanced
domain: ""
aliases:                # required when dnt_class is set; otherwise optional
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
