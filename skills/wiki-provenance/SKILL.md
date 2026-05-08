---
name: wiki-provenance
description: "Add and validate claim-level provenance pointers in the Obsidian wiki: every synthesized claim links back to the raw-source paragraph that justifies it. Use this skill whenever the user wants to know where a wiki claim came from, asks to add citations / sources / provenance to a page, asks to validate that a page's claims are properly sourced, runs a lint pass that needs source-checking, or wants a vault-wide audit of how well-sourced the wiki is. Also use during wiki-ingest synthesis to emit Provenance Blocks alongside every extracted claim. Triggers on: provenance, add citations, where does this claim come from, validate sources, source check, audit provenance, wiki-provenance, check this page's sources, prove this claim, citation chain, where's the receipt for this, this needs sources."
---

# wiki-provenance: Claim-Level Source Pointers

A wiki page synthesizes claims from raw sources in `.raw/`. Without provenance, every claim has the same epistemic weight: "the LLM said so." This skill adds a layer of audit. Each claim in a non-meta wiki page either points back to the raw-source paragraph that justifies it, or carries an explicit tag explaining why no source applies.

This is DragonScale Mechanism 5, specified at [[Provenance Chains]].

## When to use this skill

Three modes. Run on demand or as part of larger workflows.

| Mode | Trigger | Output |
|---|---|---|
| **Emit** | While writing or ingesting a wiki page from `.raw/` sources. | Provenance Blocks added beneath each claim. |
| **Validate** | When the user asks to check a page's sourcing, or when wiki-lint runs. | A structured list of broken pointers, missing provenance, or successful sourcing. |
| **Audit** | When the user wants a vault-wide rollup. | Per-page coverage totals. |

If `scripts/provenance-check.py` is present, prefer it for validation and audit; the skill will produce identical results parsing inline if not. The script is the canonical reference for parsing semantics.

---

## The canonical Provenance Block format

Every Provenance Block uses an Obsidian callout of type `provenance`. Place it on the line directly following the paragraph it justifies. List multiple sources as multiple bullet items inside one block.

```markdown
The ecosystem has 16+ active projects combining Claude with Obsidian.

> [!provenance]
> - [[claude-obsidian-ecosystem-research]] paragraph 17:
>   "16+ active projects found combining Claude/AI with Obsidian."
```

Format rules:

- Callout type is `provenance` (lowercase). Other callout types are ignored.
- First-level bullets inside the callout are pointers. One pointer per source.
- A pointer has the structure: `[[source-page]] paragraph <N>: "<verbatim quote>"`
  - `[[source-page]]` is the wiki page that summarizes the raw source (typically lives in `wiki/sources/`).
  - `paragraph <N>` is the 0-based index of the source paragraph inside the underlying `.raw/` file. Paragraphs are blank-line-separated text blocks.
  - The verbatim quote is a short excerpt (target ≤30 words) of the actual source text. The quote makes the citation visible without a tool round-trip and is checked by the validator for drift.

If the source file declares Obsidian block IDs (`^id`), prefer `[[source-page#^id]]` over a paragraph index. Block IDs are stable across reformatting; paragraph indices are not.

---

## When provenance is NOT required

If a paragraph genuinely cannot point at a source, follow it with one of these inline tags **on its own line, right after the paragraph**:

| Tag | Meaning | When to use |
|---|---|---|
| `[derived]` | Logically follows from already-provenanced claims elsewhere in this vault. | Synthesis paragraphs that combine prior provenanced material. |
| `[conjecture]` | Author-asserted; no source. | Speculation, predictions, proposed mechanisms. |
| `[editorial]` | Framing, transition, scope statement, rhetorical glue. | Section openers, topic sentences, "Why this matters" lines. |

The validator accepts any of these in place of a Provenance Block. Prefer tags over fabricated citations: a confident `[conjecture]` is more honest than a hallucinated source quote, and easier for a reviewer to challenge later.

---

## Mode 1: Emit (during ingest or page-authoring)

When you write claims into a wiki page, emit a Provenance Block for each claim that comes from a source.

Procedure:

1. Identify each top-level claim in the paragraph you are about to write.
2. For each claim, locate the supporting paragraph in the source file. Note the 0-based paragraph index and a verbatim quote (target ≤30 words).
3. Write the paragraph, then on the next line write the Provenance Block following the canonical format.
4. If no source paragraph supports the claim, decide which exemption tag applies. If none cleanly applies, the claim probably should not be written. Either drop it, soften it, or surface it as a question to the user.

Example with multiple sources:

```markdown
ballred's auto-commit hook and ekadetov's manifest tracking both target the same goal: the wiki stays in version control without manual effort.

> [!provenance]
> - [[ballred-obsidian-claude-pkm]] paragraph 6:
>   "Auto-commit via PostToolUse hook on every file write/edit."
> - [[ekadetov-llm-wiki]] paragraph 4:
>   "Auto-commit on every ingest via git."
```

Why this matters: a reviewer reading the synthesized claim can immediately see which raw quotes back it. If the synthesis is wrong, the receipts make the failure visible without a deep search through `.raw/`.

---

## Mode 2: Validate

Read a wiki page (or a directory). For each paragraph in body text (not YAML, code blocks, or callout bodies), verify one of:

- The paragraph is immediately followed by a Provenance Block.
- The paragraph is immediately followed by `[derived]`, `[conjecture]`, or `[editorial]`.
- The page is exempt by type or location (see exclusions below).

If `scripts/provenance-check.py` is present, prefer it:

```bash
./scripts/provenance-check.py wiki/concepts/SomePage.md
./scripts/provenance-check.py --missing wiki/        # paragraphs lacking provenance
./scripts/provenance-check.py --broken wiki/         # dangling pointers
./scripts/provenance-check.py --json wiki/           # machine-readable
```

### Severity model

Mirrors the [[DragonScale Memory]] Mechanism 2 lint pattern.

| Issue | Severity |
|---|---|
| Provenance Block whose target source page does not exist | **Error** |
| Provenance Block whose paragraph index is out of range for the cited source | **Error** |
| Paragraph in a `type: source` page with no provenance and no exemption tag | **Error** |
| Paragraph in a `type: concept` / `type: comparison` / `type: question` page lacking both | **Warning** |
| Provenance Block whose verbatim quote does not appear in the cited paragraph | **Warning** (drift) |
| Paragraph in a legacy page (`created` < 2026-04-23) without provenance | **Informational** |
| Paragraph in a meta page (`type: meta` or `type: fold`) | Excluded |
| Paragraph inside a fenced code block, callout body, or YAML frontmatter | Excluded |
| File path under `wiki/folds/` or `wiki/meta/` | Excluded |

Output format (plain run): a table with columns `path | line | issue | severity`, ending with a one-line summary `X errors, Y warnings, Z informational across N pages`. JSON mode emits the same data structurally.

### Exclusions in detail

- **Page exemption** by frontmatter `provenance: exempt` overrides type-based defaults. Use sparingly; record why in a frontmatter `exempt_reason:` field.
- **Filename exclusions**: `_index.md`, `index.md`, `log.md`, `hot.md`, `overview.md`, `dashboard.md`, `Wiki Map.md`, `getting-started.md` are always excluded regardless of type.
- **Symlink rejection**: a symlinked file whose target escapes the vault root is rejected at scan time (not silently followed).

---

## Mode 3: Audit

Produce a vault-wide coverage report. Useful for dashboards or release-readiness checks.

```bash
./scripts/provenance-check.py --audit wiki/
```

Output structure:

```
provenance audit: wiki/
  pages scanned:                  34
  pages requiring coverage:       22  (concept + source + comparison + question)
  paragraphs requiring coverage: 412
  paragraphs covered:            287  (69.7%)
    via provenance block:        180
    via [derived]:                42
    via [conjecture]:             34
    via [editorial]:              31
  paragraphs uncovered:          125  (30.3%)
  broken pointers:                 3
```

Use the audit number to decide whether the vault is ready for a "provenance-clean" milestone (target: ≥95% covered, 0 broken pointers). The number is not a release blocker by default; making it one is the user's call.

---

## Page-type schema

Add `provenance:` to a page's frontmatter to override the type-based default:

```yaml
provenance: required   # warnings stay warnings, errors stay errors
provenance: optional   # warnings demote to informational; errors stay errors
provenance: exempt     # all checks skipped; record exempt_reason: why
```

If `provenance:` is absent, the default is derived from `type:`:

| `type:` | Default `provenance:` |
|---|---|
| `source`, `concept`, `comparison`, `question` | `required` |
| `entity` | `required` (entities make factual claims about people/orgs/products) |
| `meta`, `fold` | `exempt` |
| anything else | `optional` |

---

## Edge cases

**Defuddle-cleaned web sources.** If a source was cleaned by `defuddle` before ingest, paragraph indices reference the cleaned output, not the original HTML. Re-running defuddle with a different version may shift indices. Mitigation: persist the defuddle output verbatim in `.raw/` and treat that file as immutable. Provenance pointers stay stable as long as `.raw/` files are immutable, which is already a wiki-ingest invariant.

**Fold inheritance.** When `wiki-fold` rolls up a batch of pages into a meta-page, the meta-page should carry the union of its children's Provenance Blocks for any synthesized claim it makes. The fold author (the LLM running wiki-fold) is responsible for emitting these unions; the validator checks them. Super-folds inherit the union recursively.

**Missing source page.** If a Provenance Block points at `[[source]]` that no longer exists in `wiki/sources/`, the validator emits an error. Resolution: restore the source page from git history, point the block at a different source that supports the same claim, or drop the claim entirely. Do not "fix" the error by inventing a quote.

**Quote drift.** If the verbatim quote in the Provenance Block does not appear in the cited source paragraph, the validator emits a warning. This catches cases where a source was edited after a claim was provenanced. (`.raw/` should be immutable, but human edits sometimes happen.) The fix is usually to update the quote, not to delete the block.

**Block-ID resolution.** A Provenance Block using `[[source#^id]]` syntax is resolved by looking up the block ID in the source's underlying `.raw/` file. If the ID is not present in `.raw/`, the validator falls back to interpreting the suffix as a paragraph index hint, then errors if neither resolves.

**Multi-paragraph claims.** A claim that spans two consecutive paragraphs gets one Provenance Block placed after the second paragraph. Don't duplicate the same block after each paragraph; one block per claim, no matter how many paragraphs the claim takes.

---

## Composition with other DragonScale mechanisms

| Mechanism | Interaction |
|---|---|
| 1. Fold | Folds inherit the union of their children's provenance. Validator enforces this on `type: fold` pages with `provenance: required` overrides. |
| 2. Address | Pointers may use `(c-NNNNNN, paragraph-N)` for additional stability across page renames. The `address_map` in `.raw/.manifest.json` resolves either form. |
| 3. Tiling | Independent. Tiling deduplicates pages; provenance addresses claim-level sourcing. They run as separate lint passes. |
| 4. Boundary | Independent. `boundary_score` does not read provenance state. |

---

## What this skill does NOT do

- It does not LLM-judge whether a source actually supports the claim semantically. That is a deferred Phase 6 mechanism (semantic provenance verification).
- It does not auto-emit Provenance Blocks during edits to existing pages. Authors must add them; the validator only checks.
- It does not enforce provenance on legacy pages (`created` < 2026-04-23). Those are informational only.
- It does not provide a UI for resolving broken pointers. Resolution is manual.
- It does not call wiki-ingest or wiki-lint. Those skills decide independently whether to delegate to this one.

---

## Connections

- [[Provenance Chains]] for the full Mechanism 5 spec, design rationale, open questions.
- [[DragonScale Memory]] for the four prior mechanisms and the framework this extends.
- [[Source-First Synthesis]] for the principle this operationalizes (raw stays raw; the wiki cites it).
