# Frontmatter conventions

Preserve an existing vault's valid property vocabulary. For a new generic
claude-obsidian page, use flat YAML properties, block lists, and explicit
evidence fields where they apply.

## Common properties

```yaml
---
type: concept
title: "Human-readable title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: developing
tags:
  - concept
related:
  - "[[Related page]]"
sources:
  - "[[Source page]]"
claim_ids:
  - claim-example
---
```

Page types are declared once in `claude_obsidian/page_schema.py` and documented in
[WIKI.md](../../../WIKI.md). This file previously restated a shorter list that
omitted `session` and `fold`, which is how a vault ends up carrying values one
document calls invalid. Statuses are still described in prose in both places and
are out of this change's scope. A custom scaffold may add types when
its schema is documented. `status` commonly progresses through `seed`,
`developing`, `mature`, and `evergreen`; preserve other established values in an
adopted vault.

## Source properties

```yaml
source_type: article
author: ""
date_published: YYYY-MM-DD
url: ""
source_id: ""
sha256: ""
authority: unknown
independence_key: ""
review_state: unreviewed
key_claims:
  - "No claims extracted yet."
```

Allowed authority values and evidence semantics are defined in
[provenance.md](provenance.md). A missing value remains empty or `unknown`; do
not manufacture metadata to complete a form.

## Other type-specific properties

```yaml
# entity
entity_type: organization
role: ""
first_mentioned: "[[Source page]]"

# concept
complexity: intermediate
domain: ""
aliases:
  - Alternative name

# comparison
subjects:
  - "[[Thing A]]"
  - "[[Thing B]]"
dimensions:
  - cost
  - reliability
assessment: provisional
risk: low

# question
question: "What is being asked?"
assessment: unsupported
risk: low
```

## Rules

1. Keep generated properties flat; do not introduce nested mappings.
2. Write dates as `YYYY-MM-DD` unless an existing schema requires a timestamp.
3. Use block lists for generated multi-value properties.
4. Quote wikilinks in YAML.
5. Keep external locators on source records; use wikilinks for internal
   `related` and `sources` relationships.
6. Update `updated` only when the page content or assessed state changes.
7. Preserve unknown valid properties during an edit.
8. Do not treat a frontmatter confidence label as evidence; the claim ledger
   and linked active sources determine support.
9. Quote numeric-only tag values, for example `- "2026"`, so their YAML type
   remains text.
