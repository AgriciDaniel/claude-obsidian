# Eval Results Trend

Snapshot of eval-suite results over time. Each row is one `evals/run.sh` invocation. Use this to spot regressions across skill iterations and after upstream merges. Append-only — newest entries at the top.

## How to add an entry

After `./evals/run.sh`:

```bash
./evals/run.sh
# Outputs evals/results/<timestamp>.json
python3 evals/score-summary.py evals/results/<latest>.json >> docs/eval-results-trend.md
```

Or fill in manually using the table format below.

## Trend table

| Date | Run ID | Branch | wiki-ingest recall | wiki-ingest precision | wiki-lint recall | wiki-lint false-pos | wiki-query citation acc. | Notes |
|---|---|---|---|---|---|---|---|---|
| _baseline pending_ | — | feat/bilingual-terminology-and-evals | — | — | — | — | — | First run after eval-suite scaffold lands; expected baseline ~2026-05-20 |

## Reading the columns

- **wiki-ingest recall**: (created pages ∩ expected pages) / expected pages. Higher is better.
- **wiki-ingest precision**: (created pages ∩ expected pages) / created pages. Higher is better; catches over-fragmentation.
- **wiki-lint recall**: (issues found ∩ injected issues) / injected issues.
- **wiki-lint false-pos**: 1 − (issues found ∩ real issues) / issues found.
- **wiki-query citation accuracy**: LLM-as-judge score 0-1 averaged across cases.

A red flag is any metric dropping > 0.10 between consecutive runs on the same case set. Investigate before merging.
