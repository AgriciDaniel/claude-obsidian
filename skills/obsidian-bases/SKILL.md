---
name: obsidian-bases
description: "Create and edit Obsidian Bases (.base files): Obsidian's native database layer for dynamic tables, card views, list views, filters, formulas, and summaries over vault notes. Triggers on: create a base, add a base file, obsidian bases, base view, filter notes, formula, database view, dynamic table, task tracker base, reading list base."
allowed-tools: Read Write
---

# obsidian-bases: Obsidian's Database Layer

Obsidian Bases (launched 2025) turns vault notes into queryable, dynamic views. Tables, cards, lists, maps. Defined in `.base` files. No plugin required; it is a core Obsidian feature.

**Substrate preference (v1.7+)**: This skill is a self-contained fallback. **Prefer `kepano/obsidian-skills`** as the authoritative substrate — its `obsidian-bases` skill is the canonical reference for Bases YAML, formulas, and view definitions. If you see an `obsidian-bases` skill available without the `claude-obsidian:` namespace, that is kepano's version: use it. The reference below is provided so the plugin remains functional when kepano's marketplace is not installed. Install: `claude plugin marketplace add kepano/obsidian-skills`. Official Bases docs: https://help.obsidian.md/bases/syntax

---

## File Format

`.base` files contain valid YAML. The root keys are `filters`, `formulas`, `properties`, `summaries`, and `views`.

```yaml
# Global filters: apply to ALL views
filters:
  and:
    - file.hasTag("wiki")
    - 'status != "archived"'

# Computed properties
formulas:
  age_days: '(now() - file.ctime).days.round(0)'
  status_icon: 'if(status == "mature", "✅", "🔄")'

# Display name overrides for properties panel
properties:
  status:
    displayName: "Status"
  formula.age_days:
    displayName: "Age (days)"

# One or more views
views:
  - type: table
    name: "All Pages"
    order:
      - file.name
      - type
      - status
      - updated
      - formula.age_days
```

---

## Filters

Filters select which notes appear. Applied globally or per-view.

```yaml
# Single string filter
filters: 'status == "current"'

# AND: all must be true
filters:
  and:
    - 'status != "archived"'
    - file.hasTag("wiki")

# OR: any can be true
filters:
  or:
    - file.hasTag("concept")
    - file.hasTag("entity")

# NOT: exclude matches
filters:
  not:
    - file.inFolder("wiki/meta")

# Nested
filters:
  and:
    - file.inFolder("wiki/")
    - or:
        - 'type == "concept"'
        - 'type == "entity"'
```

### Filter operators

`==` `!=` `>` `<` `>=` `<=`

### Useful filter functions

| Function | Example |
|----------|---------|
| `file.hasTag("x")` | Notes with tag `x` |
| `file.inFolder("path/")` | Notes in folder |
| `file.hasLink("Note")` | Notes linking to Note |

---

## Properties

Three types:
- **Note properties**: from frontmatter: `status`, `type`, `updated`
- **File properties**: metadata: `file.name`, `file.mtime`, `file.size`, `file.ctime`, `file.tags`, `file.folder`
- **Formula properties**: computed: `formula.age_days`

---

## Formulas

Defined in `formulas:`. Referenced as `formula.name` in `order:` and `properties:`.

```yaml
formulas:
  # Days since created
  age_days: '(now() - file.ctime).days.round(0)'

  # Days until a date property
  days_until: 'if(due_date, (date(due_date) - today()).days, "")'

  # Conditional label
  status_icon: 'if(status == "mature", "✅", if(status == "developing", "🔄", "🌱"))'

  # Word count estimate
  word_est: '(file.size / 5).round(0)'
```

**Key rule**: Subtracting two dates returns a `Duration`. Not a number. Always access `.days` first:
```yaml
# CORRECT
age: '(now() - file.ctime).days'

# WRONG: crashes
age: '(now() - file.ctime).round(0)'
```

**Always guard nullable properties with `if()`**:
```yaml
# CORRECT
days_left: 'if(due_date, (date(due_date) - today()).days, "")'
```

---

## View Types

### Table
```yaml
views:
  - type: table
    name: "Wiki Index"
    limit: 100
    order:
      - file.name
      - type
      - status
      - updated
    groupBy:
      property: type
      direction: ASC
```

### Cards
```yaml
views:
  - type: cards
    name: "Gallery"
    order:
      - file.name
      - tags
      - status
```

### List
```yaml
views:
  - type: list
    name: "Quick List"
    order:
      - file.name
      - status
```

---

## Wiki Vault Templates

### Wiki content dashboard (all non-meta pages)

```yaml
filters:
  and:
    - file.inFolder("wiki/")
    - not:
        - file.inFolder("wiki/meta")

formulas:
  age: '(now() - file.ctime).days.round(0)'

properties:
  formula.age:
    displayName: "Age (days)"

views:
  - type: table
    name: "All Wiki Pages"
    order:
      - file.name
      - type
      - status
      - updated
      - formula.age
    groupBy:
      property: type
      direction: ASC
```

### Entity index (people, orgs, repos)

```yaml
filters:
  and:
    - file.inFolder("wiki/entities/")
    - 'file.ext == "md"'

views:
  - type: table
    name: "Entities"
    order:
      - file.name
      - entity_type
      - status
      - updated
    groupBy:
      property: entity_type
      direction: ASC
```

### Recent ingests

```yaml
filters:
  and:
    - file.inFolder("wiki/sources/")

views:
  - type: table
    name: "Sources"
    order:
      - file.name
      - source_type
      - created
      - status
    groupBy:
      property: source_type
      direction: ASC
```

---

## Embedding in Notes

```markdown
![[MyBase.base]]

![[MyBase.base#View Name]]
```

---

## Where to Save

Store `.base` files in `wiki/meta/` for vault dashboards:
- `wiki/meta/dashboard.base`: main content view
- `wiki/meta/entities.base`: entity tracker
- `wiki/meta/sources.base`: ingestion log

---

## YAML Quoting Rules

- Formulas with double quotes → wrap in single quotes: `'if(done, "Yes", "No")'`
- Strings with colons or special chars → wrap in double quotes: `"Status: Active"`
- Unquoted strings with `:` break YAML parsing

---

## What Not to Do

- Do not use `from:` or `where:`: those are Dataview syntax, not Obsidian Bases
- Do not use `sort:` at the root level: sorting is per-view via `order:` and `groupBy:`
- Do not put `.base` files outside the vault: they only render inside Obsidian
- Do not reference `formula.X` in `order:` without defining `X` in `formulas:`

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | The `.base` YAML the user is composing — read it carefully before suggesting changes. |
| 2 | OBSERVE (int) | Am I documenting yesterday's spec or today's? Bases evolves fast post-GA. |
| 3 | LISTEN | The user's specific Bases use-case (dashboard, filter chain, computed property). |
| 4 | THINK | Which filter operators, formula syntax, view types apply? Validate against the current spec. |
| 5 | CONNECT (lat) | How do Bases relate to Dataview queries? Properties? Canvas overlays? Map the deltas. |
| 6 | CONNECT (sys) | Obsidian Bases is post-1.10 GA; substrate-defer to kepano/obsidian-skills when present. |
| 7 | FEEL | Examples that actually parse and render. Pseudo-syntax wastes the user. |
| 8 | ACCEPT | Bases spec evolves; some features in this doc may have changed. Keep the version note current. |
| 9 | CREATE | Schema docs + worked examples that render in the user's actual Obsidian version. |
| 10 | GROW | As Bases features ship, refresh the reference. Track upstream releases. |
