# Grading — case-001-german-query

Requires a live `wiki-query` run.

## Prompt for the LLM judge

You are evaluating whether `wiki-query` reached the correct page in both
language variants. The vault contains a single relevant page:
`wiki/entities/IHK.md` with bilingual aliases.

Score each variant 0-1:

### Variant A (German query)

- 1.0 — answer cites `[[IHK]]` and the answer is grounded in its content
- 0.5 — page cited but answer is generic / does not use page content
- 0.0 — page not cited or hallucinated content

### Variant B (English query)

Same scoring. Critical: this is the *retrieval* test. If the agent fails
to find `[[IHK]]` because it searched for "chamber of commerce" only, the
dual-form retrieval surface is broken.

## Output format

```json
{
  "case": "case-001-german-query",
  "scores": {
    "variant_a_de": 0.0,
    "variant_b_en": 0.0
  },
  "notes": "1-3 sentences. Especially note any retrieval failures in variant B."
}
```
