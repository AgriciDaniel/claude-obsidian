# Grading prompt — case-001-bilingual-de-source

Use this as the LLM-as-judge prompt when this case is run manually.
Pass the agent's output (created pages + their frontmatter) as input.

## Prompt

You are evaluating a `wiki-ingest` run against a synthetic German-domain
source. The source is in `input.md`. The expected pages are listed in
`expected-pages.txt`. The expected frontmatter fragments are in
`expected-frontmatter.yaml`.

Score the run on three dimensions, each 0-1:

### 1. Page coverage (recall)

Did the agent create all expected pages?
- 1.0 — all expected pages exist
- 0.5 — at least half exist
- 0.0 — fewer than half exist

### 2. DNT classification correctness

For each DNT page (IHK, Gewerbesteuer, Gewerbeanmeldung):
- `dnt_class` is set to one of the four valid values
- `dnt_class` value matches expected (see expected-frontmatter.yaml)
- `lang: de` is set
- `aliases:` contains both the native form and at least one English gloss

Score: fraction of pages that satisfy all four criteria.

### 3. No fabricated equivalents

The agent must not invent a non-existent English term for an institutional
concept. If a clean English equivalent does not exist, the alias should
preserve the native form or use a descriptive phrase, not invent one.

Penalize:
- "IHK Chamber" (not idiomatic English)
- "Trade Tax Germany" as a non-existent canonical term
- Any "official" English name that the agent could not have sourced

Score: 1.0 if no fabricated terms; 0.5 if one or two borderline; 0.0 if any clear fabrication.

## Output format

```json
{
  "case": "case-001-bilingual-de-source",
  "scores": {
    "recall": 0.0,
    "dnt_classification": 0.0,
    "no_fabrication": 0.0
  },
  "notes": "1-3 sentences on what stood out."
}
```
