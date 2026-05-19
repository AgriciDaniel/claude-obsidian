# Eval Suite

Regression and quality harness for the three primary skills:
`wiki-ingest`, `wiki-lint`, `wiki-query`.

The goal is modest: detect skill regressions after refactors, upstream
merges, or cherry-picks. Not a benchmark — there is no leaderboard, no
training signal, no automated optimization. The eval is a **guardrail**.

---

## Layout

```
evals/
├── README.md
├── run.sh                          # entry point — iterates cases, writes one JSON
├── score-summary.py                # converts JSON to a Markdown summary
├── results/                        # one JSON file per run, timestamped
│
├── ingest/                         # cases for wiki-ingest
│   └── case-001-bilingual-de-source/
│       ├── case.json               # metadata: title, what it tests
│       ├── input.md                # the synthetic source to ingest
│       ├── expected-pages.txt      # one expected wiki page path per line
│       ├── expected-frontmatter.yaml  # required frontmatter fragments
│       └── grading.md              # LLM-as-judge prompt
│
├── lint/                           # cases for wiki-lint
│   └── case-001-dnt-missing-alias/
│       ├── case.json
│       ├── vault/                  # synthetic wiki to lint
│       ├── expected-findings.json  # checks that MUST appear
│       └── grading.md
│
└── query/                          # cases for wiki-query
    └── case-001-german-query/
        ├── case.json
        ├── vault/
        ├── question.md
        ├── expected-citations.txt
        └── grading.md
```

---

## How to add a case

1. Pick the skill the case belongs to: `ingest`, `lint`, or `query`.
2. Create a folder `case-NNN-short-slug/` under it.
3. Add `case.json` with at minimum:
   ```json
   {
     "title": "Short human-readable label",
     "tests": "What behavior this case exercises",
     "created": "YYYY-MM-DD"
   }
   ```
4. Add the inputs and the expected-* files per the layout above.
5. Run `./evals/run.sh` and verify the new case appears in the output.

Keep cases small. One case = one specific behavior. If a case needs
> 20 lines of input or > 5 expected outputs, split it.

---

## Running

```bash
./evals/run.sh                     # all cases, default
./evals/run.sh ingest              # only ingest cases
./evals/run.sh lint case-001-*     # specific case
```

Outputs:
- `evals/results/<timestamp>.json` — machine-readable
- `evals/results/<timestamp>.md` — human summary via `score-summary.py`

Append a row to `docs/eval-results-trend.md` after each run with the
top-level metrics.

---

## Metrics

Per skill, the runner computes:

| Skill | Metric | Definition |
|---|---|---|
| `wiki-ingest` | recall | |created pages ∩ expected| / |expected| |
|  | precision | |created pages ∩ expected| / |created| |
|  | frontmatter compliance | per case: all expected-frontmatter fragments matched |
| `wiki-lint` | recall | |found findings ∩ expected| / |expected| |
|  | false-positive rate | 1 − |found ∩ real| / |found| |
| `wiki-query` | citation accuracy | LLM-as-judge 0-1 over expected-citations |

Lower-bound watermark: any metric dropping > 0.10 between two consecutive
runs on the same case set is a regression. Investigate before merging.

---

## Limits

- This harness does **not** run the skill end-to-end against a live
  Claude session. It runs the deterministic parts (lint scripts) and
  provides scaffolding for manual LLM-judge passes on the rest.
- Full skill-execution evals (spawning Claude sub-agents on each case)
  are a deferred upgrade — see `docs/influence-log.md` for the cookbook
  patterns we are tracking.
- Case-set drift: cases capture today's expectations. Refresh them when
  the skill evolves. Outdated cases give false confidence.
