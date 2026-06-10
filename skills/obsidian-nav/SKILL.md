---
name: obsidian-nav
description: "Add navigable structure to wiki pages: folded table-of-contents callout, per-section return links, and cross-page navigation footers. Use when creating or editing wiki/concept or wiki/source pages that have multiple ## sections. Triggers on: add navigation, add nav, add toc, table of contents, return links, navigation footer, obsidian navigation, wiki navigation, page navigation, nav links."
allowed-tools: Read Write Edit
---

# obsidian-nav: Wiki Page Navigation

Wiki pages without navigation are dead ends. This skill adds three navigation primitives that make long wiki pages scannable, traversable, and connected to the vault graph:

1. **Folded TOC callout** — clickable section index at the top
2. **Return links** — `[[#目录|↑ 返回目录]]` at the end of every section
3. **Cross-page footer** — `📚 导航` block linking sibling pages

Apply this skill after `wiki-ingest` creates or updates a page with multiple `##` sections. Also apply when `wiki-lint` reports pages missing navigation.

---

## Prerequisite: obsidian-markdown

This skill builds on the Obsidian Flavored Markdown syntax defined in [`skills/obsidian-markdown/SKILL.md`](../obsidian-markdown/SKILL.md). It uses wikilinks, callouts, and frontmatter from that skill. Read that skill first if you are unsure about syntax.

---

## 1. Folded TOC Callout

For pages with 3+ `##` sections, add a table-of-contents callout at the top.

### Anchor pattern

Use a **real heading** as the anchor target, plus a **callout** for visual display:

```markdown
## 目录

> [!note]+ 📑 目录
> [[index|← 返回知识库]]
> **相关文档**: [[other-file|显示名]] · [[another-file|另一篇]]
>
> - [[#1. Main Section]]
>   - [[#1.1 Subsection]]
>   - [[#1.2 Subsection]]
> - [[#2. Another Section]]
>   - [[#2.1 Sub A]]
>   - [[#2.2 Sub B]]
```

**Why `## 目录` + callout?** Callout titles (`[!note]+ 📑 目录`) do NOT generate anchor targets in Obsidian. The `## 目录` heading is the actual anchor that `[[#目录]]` resolves to. The callout provides the visual folded TOC.

### Multi-level nesting

Indent with 2 spaces per level. `###` subsections go under their `##` parent:

```markdown
> - [[#3. 隔离技术栈详解]]
>   - [[#3.1 容器沙箱]]
>   - [[#3.2 MicroVM 沙箱]]
```

### Anchor text rules

- Use the **heading text verbatim** as the anchor. NOT a slug.
- `[[#1. Model Selection]]` — correct
- `[[#1-model-selection]]` — wrong, will not resolve

---

## 2. Return Links

Put `[[#目录|↑ 返回目录]]` at the end of **every** `##` section AND **every** `###` subsection:

```markdown
## 1. Main Section

正文...

[[#目录|↑ 返回目录]]

---

### 1.1 Subsection

正文...

[[#目录|↑ 返回目录]]
```

**No emoji in the anchor.** The anchor target is `## 目录`, so return links use `[[#目录|↑ 返回目录]]`. NOT `[[#📑 目录]]` — that will not resolve.

### Batch injection

For documents with many subsections, generate return links programmatically:

1. Find all `## ` and `### ` headings and their end positions (next `##`/`###` or `---` footer or EOF)
2. Check each section for existing `[[#目录|↑ 返回目录]]`
3. Insert before the section end if missing
4. Insert in **reverse order** to preserve positions

```python
import re
with open(filepath) as f:
    content = f.read()
# Find heading positions, work backwards to insert
headings = [(m.start(), m.group(1)) for m in re.finditer(r'^(##+ .+)$', content, re.MULTILINE)]
```

---

## 3. Cross-Page Navigation Footer

Add a `📚 导航` footer at the bottom of every wiki page, linking sibling pages in the same domain:

```markdown
---

> 📚 导航: [[index|📑 知识库]] · [[concept-a|概念A]] · [[concept-b|概念B]] · [[concept-c|概念C]]
```

The footer goes after the last content section, before any `---` horizontal rule that precedes metadata. Every page in the same `wiki/concepts/` or `wiki/sources/` group should appear in the footer so readers can traverse the full cluster without returning to index.

---

## Integration with wiki-ingest

When `wiki-ingest` creates a page with 3+ `##` sections, apply this skill immediately after:

1. Read the newly created page
2. Insert `## 目录` + folded TOC callout after the frontmatter
3. Add `[[#目录|↑ 返回目录]]` at the end of every section
4. Add `📚 导航` footer with sibling page links
5. Verify all wikilinks resolve (no broken anchors)

This can be done as a post-ingest step in the same session, or as a separate `obsidian-nav` invocation.

---

## Integration with wiki-lint

Add a navigation check to `wiki-lint`:

- **WARN**: page has 3+ `##` sections but no `## 目录` heading
- **WARN**: page has `## 目录` but sections are missing `[[#目录|↑ 返回目录]]`
- **WARN**: page has no `📚 导航` footer and sibling pages exist

---

## What NOT to Do

| Wrong | Correct | Why |
|-------|---------|-----|
| `[[#1-model-selection]]` | `[[#1. Model Selection]]` | Use heading text, not slug |
| `{#custom-id}` after heading | Remove `{#}` entirely | Heading text IS the anchor |
| `[[#📑 目录\|↑ 返回目录]]` | `[[#目录\|↑ 返回目录]]` | Anchor targets `## 目录`, no emoji |
| Callout as anchor target | Use real `##` heading | Callout titles don't generate anchors |
| Return links only on `##` | Add on EVERY `##` AND `###` | Subsections need navigation too |
| Callout lines without `>` | Every line inside callout needs `>` | Blockquote syntax |
| Manual link insertion for 50+ sections | Use script to batch-inject | Faster, fewer errors |
| Skip navigation on new pages | Apply after every wiki-ingest | Navigation is not optional |

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read the page structure: how many `##` sections? What are the heading texts? What sibling pages exist? |
| 2 | OBSERVE (int) | Am I adding navigation that matches the page's actual structure, or imposing a generic template? |
| 3 | LISTEN | Which sections do users actually jump between? The TOC should reflect real navigation paths. |
| 4 | THINK | Three primitives (TOC, return links, footer) compose into a complete navigation system. Each is independent. |
| 5 | CONNECT (lat) | How does this page relate to its siblings? The footer should mirror the vault graph, not invent connections. |
| 6 | CONNECT (sys) | Integrates with wiki-ingest (post-create) and wiki-lint (health check). Part of the vault lifecycle. |
| 7 | FEEL | A page without navigation is a dead end. Navigation turns a document into a traversable node in the knowledge graph. |
| 8 | ACCEPT | Not every page needs all three primitives. Short pages (1-2 sections) may only need a footer. |
| 9 | CREATE | TOC callout + return links + cross-page footer. Verify all wikilinks resolve before writing. |
| 10 | GROW | As the vault grows, navigation footers may need pruning. Large clusters may need sub-index pages instead of flat footers. |