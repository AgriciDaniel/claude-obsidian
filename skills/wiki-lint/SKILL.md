---
name: wiki-lint
description: >
  Health check the Obsidian wiki vault. Finds orphan pages, dead wikilinks, stale claims,
  missing cross-references, frontmatter gaps, and empty sections. Creates or updates
  Dataview dashboards. Generates canvas maps. Triggers on: "lint", "health check",
  "clean up wiki", "check the wiki", "wiki maintenance", "find orphans", "wiki audit".
---

# wiki-lint: Wiki Health Check

Run lint after every 10-15 ingests, or weekly. Ask before auto-fixing anything. Output a lint report to `wiki/meta/lint-report-YYYY-MM-DD.md`.

---

## Lint Checks

Work through these in order:

1. **Orphan pages**. Wiki pages with no inbound wikilinks. They exist but nothing points to them.
2. **Dead links**. Wikilinks that reference a page that does not exist.
3. **Stale claims**. Assertions on older pages that newer sources have contradicted or updated.
4. **Missing pages**. Concepts or entities mentioned in multiple pages but lacking their own page.
5. **Missing cross-references**. Entities mentioned in a page but not linked.
6. **Frontmatter gaps**. Pages missing required fields (type, status, created, updated, tags).
7. **Empty sections**. Headings with no content underneath.
8. **Stale index entries**. Items in `wiki/index.md` pointing to renamed or deleted pages.
9. **Address validity** (DragonScale Mechanism 2). For every page that has an `address:` frontmatter field, validate the format. See the **Address Validation** section below.
10. **Semantic tiling** (DragonScale Mechanism 3, opt-in). Flag candidate duplicate pages (across all scanned types, not just concepts) via embedding cosine similarity. See the **Semantic Tiling** section below.

---

## Lint Report Format

Create at `wiki/meta/lint-report-YYYY-MM-DD.md`:

```markdown
---
type: meta
title: "Lint Report YYYY-MM-DD"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [meta, lint]
status: developing
---

# Lint Report: YYYY-MM-DD

## Summary
- Pages scanned: N
- Issues found: N
- Auto-fixed: N
- Needs review: N

## Orphan Pages
- [[Page Name]]: no inbound links. Suggest: link from [[Related Page]] or delete.

## Dead Links
- [[Missing Page]]: referenced in [[Source Page]] but does not exist. Suggest: create stub or remove link.

## Missing Pages
- "concept name": mentioned in [[Page A]], [[Page B]], [[Page C]]. Suggest: create a concept page.

## Frontmatter Gaps
- [[Page Name]]: missing fields: status, tags

## Stale Claims
- [[Page Name]]: claim "X" may conflict with newer source [[Newer Source]].

## Cross-Reference Gaps
- [[Entity Name]] mentioned in [[Page A]] without a wikilink.
```

---

## Naming Conventions

Enforce these during lint:

| Element | Convention | Example |
|---------|-----------|---------|
| Filenames | Title Case with spaces | `Machine Learning.md` |
| Folders | lowercase with dashes | `wiki/data-models/` |
| Tags | lowercase, hierarchical | `#domain/architecture` |
| Wikilinks | match filename exactly | `[[Machine Learning]]` |

Filenames must be unique across the vault. Wikilinks work without paths only if filenames are unique.

---

## Writing Style Check

During lint, flag pages that violate the style guide:

- Not declarative present tense ("X basically does Y" instead of "X does Y")
- Missing source citations where claims are made
- Uncertainty not flagged with `> [!gap]`
- Contradictions not flagged with `> [!contradiction]`

---

## Dataview Dashboard

Create or update `wiki/meta/dashboard.md` with these queries:

````markdown
---
type: meta
title: "Dashboard"
updated: YYYY-MM-DD
---
# Wiki Dashboard

## Recent Activity
```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15
```

## Seed Pages (Need Development)
```dataview
LIST FROM "wiki" WHERE status = "seed" SORT updated ASC
```

## Entities Missing Sources
```dataview
LIST FROM "wiki/entities" WHERE !sources OR length(sources) = 0
```

## Open Questions
```dataview
LIST FROM "wiki/questions" WHERE answer_quality = "draft" SORT created DESC
```
````

---

## Canvas Map

Create or update `wiki/meta/overview.canvas` for a visual domain map:

```json
{
  "nodes": [
    {
      "id": "1",
      "type": "file",
      "file": "wiki/overview.md",
      "x": 0, "y": 0,
      "width": 300, "height": 140,
      "color": "1"
    }
  ],
  "edges": []
}
```

Add one node per domain page. Connect domains that have significant cross-references. Colors map to the CSS scheme: 1=blue, 2=purple, 3=yellow, 4=orange, 5=green, 6=red.

---

## Address Validation (DragonScale Mechanism 2 MVP)

**Opt-in feature.** Address Validation runs only if the vault is using DragonScale, detected by:

```bash
if [ -f ./scripts/allocate-address.py ] && [ -f ./.vault-meta/address-counter.txt ]; then
  DRAGONSCALE_ADDRESSES=1
else
  DRAGONSCALE_ADDRESSES=0
fi
```

When `DRAGONSCALE_ADDRESSES=0`, skip this entire section. Missing `address:` fields are not flagged, not even informationally. Pages that happen to have an `address:` field are passed through unvalidated (treat as user-managed metadata).

When `DRAGONSCALE_ADDRESSES=1`, proceed with the rollout baseline and checks below.

Rollout baseline: **2026-04-23** (Phase 2 ship date in vaults that adopted DragonScale on that day). Vaults that adopted DragonScale later should override this baseline by setting the earliest `created:` date of any addressed page as their personal rollout date. Record the chosen baseline at the top of `.vault-meta/legacy-pages.txt` as a commented line: `# rollout: YYYY-MM-DD`.

### Classification rule (applied per page)

Before validating anything, classify the page:

| Classification | Criteria |
|---|---|
| **Meta / fold / excluded** | File is in `wiki/folds/` OR filename in `{_index.md, index.md, log.md, hot.md, overview.md, dashboard.md, dashboard.base, Wiki Map.md, getting-started.md}`. Address not required. |
| **Post-rollout (must have address)** | `type` is not meta/fold AND frontmatter `created:` date is >= 2026-04-23 AND file path is NOT in the legacy baseline manifest. |
| **Legacy (backfill-eligible)** | `type` is not meta/fold AND frontmatter `created:` date is < 2026-04-23 OR file path IS in the legacy baseline manifest. Address not required until backfill. |

**Legacy baseline manifest**: optional file at `.vault-meta/legacy-pages.txt`, one relative path per line. Pages listed there are treated as legacy regardless of `created:` date. Use this to grandfather pages whose `created:` metadata is wrong or missing.

### Validation checks (run in order)

1. **Format check**: any page with `address:` set must match one of:
   - `^c-[0-9]{6}$` — post-rollout creation address.
   - `^l-[0-9]{6}$` — legacy-backfill address.
   - Pages under `wiki/folds/` use `fold_id`, not `address`; do not apply the `c-`/`l-` regex there.

2. **Uniqueness check**: no two pages share the same address value. Report both paths.

3. **Counter consistency**: `./scripts/allocate-address.py --peek` returns the next counter value. Every observed `c-NNNNNN` must satisfy `NNNNNN < peek_value`. Violation = counter drift.

4. **Post-rollout enforcement**: every page classified as "post-rollout (must have address)" that LACKS the `address:` field is a lint **error**, not informational. This prevents the silent-regression path where a new page skips address assignment.

5. **Legacy identification**: every page classified as "legacy" that LACKS an address is informational. The lint report lists them under "Pending backfill" with total count.

6. **Address-map consistency** (`.raw/.manifest.json`): for every page path in `address_map`, the page must exist and its frontmatter `address` must match the mapping. Mismatches are errors (either a rename dropped the map update, or a manual edit diverged).

### Lint posture summary

- Pages that HAVE an address with bad format: **error**.
- Pages that HAVE colliding addresses: **error**.
- Pages classified **post-rollout** WITHOUT an address: **error**.
- Pages classified **legacy** WITHOUT an address: **informational** (expected).
- Meta and fold pages without `address`: **ignored** (not applicable).
- Counter drift (observed counter >= peek): **error**.
- Address-map mismatch: **error**.

Lint only observes. Do NOT auto-assign missing addresses during lint. Assignment is `wiki-ingest`'s responsibility only.

### Output section in the lint report

```markdown
## Address Validation

- Counter state: `$(./scripts/allocate-address.py --peek)`
- Highest c- address observed: c-XXXXXX
- Post-rollout pages checked: N (X passing, Y errors)
- Legacy pages pending backfill: M

### Errors
- [[Page Name]]: invalid address format `{value}`. Expected `c-NNNNNN` or `l-NNNNNN`.
- [[Page A]] and [[Page B]] share address `c-000042`.
- [[Post-Rollout Page]]: missing address. Page created 2026-04-25 (post-rollout); address required. Run wiki-ingest or manually run `./scripts/allocate-address.py` and add to frontmatter.
- [[Page Name]] has address `c-000100` but counter peek is `50`. Counter drift; run `./scripts/allocate-address.py --rebuild`.
- `.raw/.manifest.json` maps `wiki/foo.md` -> `c-000010` but page frontmatter has `c-000012`. Resolve mismatch.

### Pending backfill (informational)
- M legacy pages without addresses. See `.vault-meta/legacy-pages.txt` for the canonical legacy set, or filter by `created:` < 2026-04-23.
```

---

## Semantic Tiling (DragonScale Mechanism 3 MVP, opt-in)

**Opt-in feature.** Semantic tiling flags candidate duplicate *pages* (not just concept pages — see Scope below) using embedding cosine similarity. Local ollama only by default; remote endpoints require an explicit override flag.

### Detection and delegation

```bash
if [ -x ./scripts/tiling-check.py ] && command -v python3 >/dev/null 2>&1; then
  ./scripts/tiling-check.py --peek > /tmp/tiling-peek.json 2>/dev/null
  PEEK_EXIT=$?
  case $PEEK_EXIT in
    0)  TILING_READY=1 ;;                                  # ready
    2)  TILING_READY=0 ; echo "tiling ERROR: usage error (exit 2); inspect /tmp/tiling-peek.json" ;;
    3)  TILING_READY=0 ; echo "tiling ERROR: cache corrupt (exit 3); inspect .vault-meta/tiling-cache.json" ;;
    4)  TILING_READY=0 ; echo "tiling ERROR: vault exceeds scale hard-fail (exit 4); batching required" ;;
    10) TILING_READY=0 ; echo "tiling skipped: ollama not reachable (exit 10)" ;;
    11) TILING_READY=0 ; echo "tiling skipped: run 'ollama pull nomic-embed-text' to enable (exit 11)" ;;
    *)  TILING_READY=0 ; echo "tiling ERROR: unexpected exit code $PEEK_EXIT from tiling-check.py --peek" ;;
  esac
else
  TILING_READY=0
  echo "tiling skipped: scripts/tiling-check.py or python3 not available"
fi
```

Inspect `/tmp/tiling-peek.json` (structured diagnostics: script path, python interpreter, ollama URL, cache state, thresholds state) whenever the status is ambiguous. Never collapse unknown exits into "unknown status" silently.

When `TILING_READY=1`:

```bash
./scripts/tiling-check.py --report wiki/meta/tiling-report-YYYY-MM-DD.md
REPORT_EXIT=$?
case $REPORT_EXIT in
  0)  echo "tiling report written" ;;
  2)  echo "tiling ERROR: usage error during --report" ;;
  3)  echo "tiling ERROR: cache corrupt during --report" ;;
  4)  echo "tiling ERROR: scale hard-fail during --report" ;;
  10) echo "tiling ERROR: ollama became unreachable between --peek and --report" ;;
  11) echo "tiling ERROR: model became unavailable between --peek and --report" ;;
  *)  echo "tiling ERROR: unexpected exit code $REPORT_EXIT from tiling-check.py --report" ;;
esac
```

### Scope (what the helper scans)

- Includes: every `.md` under `wiki/` **except** the exclusion set below. The scope is "candidate tileable pages," not just `type: concept`.
- Excludes (path): anything under `wiki/folds/` or `wiki/meta/`.
- Excludes (filename): `_index.md`, `index.md`, `log.md`, `hot.md`, `overview.md`, `dashboard.md`, `Wiki Map.md`, `getting-started.md`.
- Excludes (frontmatter): `type: meta` or `type: fold`.
- Excludes (security): symlinks. Any page file that is a symlink, or whose resolved path escapes the vault root, is skipped.

If you place a real concept under `wiki/meta/` it will be excluded by path regardless of content. Keep concepts in their canonical folders.

### How the helper works

- Computes one embedding per included page via the ollama `nomic-embed-text` model by default.
- Caches embeddings at `.vault-meta/tiling-cache.json`, keyed on `sha256(model + body)` so model drift auto-invalidates. Frontmatter is not part of the hash or the embedding input — pure frontmatter edits (tag changes, status bumps) do not trigger recomputation.
- Orphans are GC'd: when a cached page path no longer exists on disk, its entry is dropped on save.
- Concurrent-safe: exclusive file lock on `.vault-meta/.tiling.lock` around cache I/O; per-PID temp file for atomic writes.

### Security posture

- Defaults to `http://127.0.0.1:11434`. `OLLAMA_URL` env override is accepted **only** with `--allow-remote-ollama` because page bodies are POSTed as embedding input.
- Symlinks and vault-root escapes are rejected.

### Default bands (conservative seeds, NOT calibrated)

| Band | Similarity | Report section |
|---|---|---|
| Error | `>= 0.90` | **Errors** — strong near-duplicate, likely the same concept |
| Review | `0.80 - 0.90` | **Review** — possible tile overlap; human judgement needed |
| Pass | `< 0.80` | not emitted |

**These values are conservative seeds, not literature-backed interpolation.** Published reference points: Sentence Transformers `community_detection` defaults to 0.75; Quora-duplicate calibrations land around 0.7715-0.8352 depending on objective. The 0.80 review floor is already stricter than at least one cited Quora optimum, so expect **false negatives** against those baselines. Reduce the review floor during calibration if you want more sensitivity.

### Calibration procedure (manual, one-time per vault)

1. Run the helper with defaults. Capture the **Review** band pairs.
2. Temporarily lower `bands.review` to `0.70` in `.vault-meta/tiling-thresholds.json` to surface a wider sample. Aim for >=50 pairs spanning 0.70-0.95.
3. Label each pair: `duplicate`, `similar`, `distinct`.
4. Pick bands such that: (a) the `error` band contains >= 95% true duplicates; (b) the `review` band captures `similar` pairs without swamping the report with `distinct` ones.
5. Edit `.vault-meta/tiling-thresholds.json`: set new `bands.error` and `bands.review`, set `calibrated: true`, set `calibration_pairs_labeled` to the label count.
6. Re-run lint. Report footer now says `calibrated: true`.

### Scale

- Cold-cache cost is O(N) POSTs to ollama. Warm-cache cost is O(N^2) cosines in pure Python.
- Helper prints a warning at > 500 pages and hard-fails (exit 4) at > 5000. Revisit the implementation (batching, vectorized cosine, or external tooling) before exceeding either limit.

### Lint report embed

```markdown
## Semantic Tiling
See [[tiling-report-YYYY-MM-DD]] for the full pair listing.
- Errors (>=0.90): N pairs
- Review (0.80-0.90): M pairs
- Calibrated: true|false
```

### Invariants

- Read-only. `tiling-check.py` never modifies wiki pages.
- No auto-merge. Duplicates are listed, never resolved.
- Cache is incremental and model-scoped. Unchanged pages are not re-embedded.
- Exit codes: `0` ok, `2` usage error, `3` cache corrupt, `4` scale hard-fail, `10` ollama unreachable, `11` model missing. Surface all of them; do not collapse into a single "unknown" bucket.

---

## Before Auto-Fixing

Always show the lint report first. Ask: "Should I fix these automatically, or do you want to review each one?"

Safe to auto-fix:
- Adding missing frontmatter fields with placeholder values
- Creating stub pages for missing entities
- Adding wikilinks for unlinked mentions

Needs review before fixing:
- Deleting orphan pages (they might be intentionally isolated)
- Resolving contradictions (requires human judgment)
- Merging duplicate pages
