# Bilingual Terminology Policy

Schema-level policy for an English-primary, Karpathy-style LLM wiki that preserves native-language terms of art. Operational document for `wiki-ingest`, `wiki-lint`, `wiki-query`, and `save` skills.

This document specifies **what is preserved, what is translated, and which guarantees the wiki upholds across its lifecycle.** It does not prescribe file layout, syntax, or tooling beyond what is necessary to make the policy auditable.

---

## 1 · Purpose

The wiki is written in English to maximize token efficiency and proximity to the largest body of training data, while preserving native-language terms (initially: German) whenever translation would distort meaning, lose a defined legal or cultural frame, or break recall against domain-original sources.

This is the **default policy** for vaults that opt in. To opt in, add to the vault's `CLAUDE.md`:

```markdown
## Bilingual terminology
Policy: docs/bilingual-terminology-policy.md (from claude-obsidian plugin)
Native language: de
```

---

## 2 · Why English-Primary

- **Token efficiency** in narrative prose, not in identifiers. Eigennamen (`IHK`, `GmbH`, `AGB`) tokenize cheaply in both languages — the gain comes from the surrounding English text.
- **Training-data proximity** for general concepts and cross-domain reasoning.
- **Caveat**: for *domain-native* topics (German law, German institutions, German business practice), the primary training data lives in German sources. Translating these moves the wiki *away* from its strongest signal. Native preservation is therefore not stylistic — it is a retrieval and fidelity requirement.

---

## 3 · What Stays Native (Do-Not-Translate)

A term stays in the source language when **any** of the following holds:

1. **Term of art** with a defined legal, regulatory, or institutional meaning (e.g. AGB under §§ 305 ff. BGB; Vorstand vs. Aufsichtsrat in the German two-tier board system).
2. **Eigenname** for an institution, statute, or scheme with no equivalent (e.g. IHK, BGB, GmbH, Mitbestimmung).
3. **Coined** — the wiki's own internal vocabulary, project names, conventions. Stable identifiers across languages.
4. **Hybrid** — bilingual compounds in active use (e.g. `KI-Berater`, `AI-Engineer-Rolle-DE`). Treated as native because the compound itself is the unit of meaning.

When in doubt, keep native and gloss on first use. **Native preservation is the safe default; translation is the active choice.**

A "near-synonym that loses the frame" is worse than the original. `AGB` is not `T&C`; `Geschäftsführer` is not `CEO`; `Vorstand` is not `board of directors`.

---

## 4 · What Gets Translated

Descriptive vocabulary, generic business and technical concepts, and anything without a defined frame in the source language. Translation is preferred where it improves clarity for an English-language reader and does not change the referent.

Industry-standard terms with clear cross-language usage (e.g. `Net Revenue Retention`, `Lean Canvas`, `Vertical SaaS`) stay English even when discussed in a German context. They are not DACH-bound.

---

## 5 · Core Components

The wiki maintains four artifacts. Physical representation is fixed below to match the plugin's existing structure.

| Component | Representation | Why |
|---|---|---|
| **Termbase** | A single index page at `wiki/meta/termbase.md` listing every page with a `dnt_class` frontmatter field. Optionally backed by an Obsidian Base (`wiki/meta/termbase.base`) for live filtering. | Single source of truth, lives next to the content. No separate JSON to drift. |
| **DNT classification** | Frontmatter field `dnt_class: term-of-art \| eigenname \| coined \| hybrid` on every native-preserved page. Translatable pages omit the field. | Auditable per-page; lint can act on it deterministically. |
| **First-use gloss** | On a page's *first* mention of a native term, the English meaning appears once in-line: `IHK (Industrie- und Handelskammer, Germany's chamber of commerce)`. Subsequent mentions on the same page use the native term alone. | Reader onboarding without token bloat. |
| **Dual-form retrieval surface** | The `aliases:` frontmatter field on every DNT page MUST contain both the native form and the English gloss. Obsidian resolves `[[english gloss]]` to the native page via alias. | English query hits native pages; German query hits the same pages. No parallel mirror needed. |

---

## 6 · Touchpoints in the Wiki Lifecycle

### Ingest (`wiki-ingest`)

When new sources or notes enter the wiki:

- **Detect native-language term candidates** during entity/concept extraction: unknown capitalized nouns, acronyms, legal references (§, Art., Abs., BGB, EStG…), recurring domain terms.
- **Classify per candidate**: term-of-art, eigenname, coined, hybrid, or translatable. Apply Section 3.
- **Propose termbase additions or updates** to the user before writing them. Claude Code does not silently extend the termbase.
- **Ensure dual-form retrievability**: every new DNT page must have at least one English-gloss alias in `aliases:`.
- **Record the source** for any classification that involved judgment in the page's `sources:` field, so audits can revisit it.

See `skills/wiki-ingest/SKILL.md` § *Bilingual term detection*.

### Lint (`wiki-lint`)

Periodic health checks surface — never silently fix — at minimum:

| Check | Severity | Source |
|---|---|---|
| `dnt_class` page has fewer than 2 entries in `aliases:` | error | deterministic, `scripts/lint-terminology.py` |
| `dnt_class` page is not listed in `wiki/meta/termbase.md` | warn | deterministic |
| Termbase entry has no inbound backlink | info | deterministic |
| Inconsistent surface forms of the same concept across pages | warn | LLM judgment in `wiki-lint` skill body |
| Native term used without first-use gloss on a page that does not have `dnt_class` for it | info | LLM judgment |
| Suspect translation: a native term-of-art rendered as an English near-synonym that may have changed the referent | warn | LLM judgment |

The lint report classifies findings by severity and proposes concrete fixes. It does not auto-apply changes that involve judgment.

See `skills/wiki-lint/SKILL.md` § *Bilingual terminology checks*.

### Update / Audit

A termbase entry is re-evaluated when:

- The scope of usage expands beyond the original frame (a term originally classified as domain-specific now appears in unrelated contexts).
- A source is added that contradicts the current English gloss.
- The user flags a term as miscategorized.

Re-evaluation propagates: changing a gloss requires sweeping pages for stale wording, exactly as the standard wiki-update flow does for factual claims.

---

## 7 · Decision Authority

Claude Code is authorized to **decide autonomously**:

- Whether a term meets Section 3 criteria, when the case is unambiguous.
- Where in the wiki a per-page glossing convention lives.
- How to make pages dual-form retrievable using `aliases:`.
- Lint severity assignments and fix proposals.

Claude Code must **escalate to the user**:

- Borderline classifications (translatable vs. term of art) — present the trade-off, recommend, let the user choose.
- Any change that would silently rewrite an existing gloss across multiple pages.
- Conflicts between this policy and other active policies (e.g. a project-specific style guide that mandates full translation).

Claude Code must **never**:

- Translate a term-of-art into a near-synonym to make prose flow.
- Add or remove termbase entries without surfacing the change.
- Fabricate a legal or institutional equivalent that does not exist. *"I don't know the English equivalent"* is the correct answer.

---

## 8 · Conflict and Improvement Mandate

This policy is a working hypothesis, not a fixed rule set.

- **Surface contradictions** — between this policy and observed wiki reality, between this policy and other project policies, or internal to the policy itself. Do not silently pick a side.
- **Flag uncertainty explicitly** on classification calls; do not project false confidence.
- **Propose improvements** when patterns in the wiki suggest a better rule. Improvement proposals come with: the observation that motivated them, the trade-off against the current rule, and an explicit recommendation. The user decides.

---

## 9 · Out of Scope

- Wikis with more than two languages. This policy assumes one English target and one source language; extension is possible but not specified here.
- Translation-memory or full bilingual mirroring of content. The wiki is English-primary with native anchors, not parallel-bilingual.
- Style and formatting choices unrelated to terminology.
