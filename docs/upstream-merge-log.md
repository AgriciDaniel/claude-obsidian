# Upstream Merge Log

Audit trail for every change pulled from the upstream `AgriciDaniel/claude-obsidian` repo. Each entry records *what* was merged, *when*, and *why*. This file is append-only — newest entries at the top.

## How to add an entry

After running `git cherry-pick <hash>` or `git merge upstream/<ref>`:

```bash
git fetch upstream
git log upstream/main --oneline ^main      # list new commits
git cherry-pick <hash>                      # or a range
# resolve conflicts, run evals, then:
./evals/run.sh
# Append a new entry here with the commit hash, range, and 1-2 sentences why
```

Entries below use this format:

```markdown
## YYYY-MM-DD — <short title>
- Source: upstream/<branch> @ <hash> (or range `<from>..<to>`)
- Action: cherry-pick | merge | re-implement
- Skills touched: wiki-ingest, wiki-lint, ...
- Eval delta: <baseline-run-id> → <new-run-id> (regression: yes/no)
- Why: 1-2 sentences.
- Why-not (skipped commits in the same range): bulleted list with hashes.
```

---

## 2026-05-19 — Fork bootstrap

- Source: upstream/main @ 75d3b6f (v1.6.0)
- Action: initial fork; no upstream merges yet
- Skills touched: none (clean baseline)
- Eval delta: n/a — eval suite scaffolded in this same PR
- Why: starting point for DACH/Bilingual customization layer; upstream remains read-only for selective backports.
