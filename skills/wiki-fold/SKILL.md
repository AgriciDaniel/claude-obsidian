---
name: wiki-fold
description: "Rollup of wiki log entries into meta-pages. Reads the last 2^k entries from wiki/log.md, writes a structurally-idempotent fold page to wiki/folds/ that links back to children. Extractive summarization (no invention). Dry-run by default, stdout-only; commit mode writes and accepts that the PostToolUse hook auto-commits. Triggers on: fold the log, run a fold, run wiki-fold, log rollup, roll up log entries."
---

# wiki-fold: Extractive Log Rollup

> **Vault resolution**: The vault and plugin are separate directories. Before using any paths, read `skills/wiki/references/vault-resolution.md` to resolve `VAULT_ROOT` (where `wiki/` lives). All `wiki/` paths below are relative to `VAULT_ROOT`.

Implements a bounded subset of Mechanism 1 from [[DragonScale Memory]]: flat fold over raw `wiki/log.md` entries. Fold-of-folds (hierarchical level-stacking) is **out of scope for this skill**; see "Scope boundary" below.

A fold is **additive**: child log entries and their referenced pages are never modified, moved, or deleted. A fold is **extractive**: every outcome and theme in the output must be traceable to a specific child log entry. No invented facts, no synthesis beyond what the child entries support.

---

## Scope boundary (explicit)

This skill does **not** implement:
- Fold-of-folds / hierarchical level stacking (DragonScale spec calls for it; deferred to a future skill).
- Automatic triggering (folds are always human-invoked in Phase 1).
- Semantic-tiling dedup (Mechanism 3; separate skill).

It **does** implement:
- Flat fold over raw log.md entries at a chosen batch exponent `k`.
- Structural idempotency via a deterministic fold ID.
- Extractive summarization with count-checking.

When referring to level in frontmatter, use `batch_exponent: k` (not `level: k`), because this skill does not produce hierarchical levels.

---

## Modes

| Mode | Writes? | Invocation |
|---|---|---|
| **dry-run (default)** | **No Write tool calls.** Emit fold content via Bash `cat`/`heredoc` to stdout only. | `fold the log, dry-run k=3` |
| **commit** | Uses Write/Edit tools. Each Write fires the repo PostToolUse hook which auto-commits wiki changes. Accept this. Compose full content first, then sequence writes. | `fold the log, commit k=3` (only after a clean dry-run) |

**Why stdout-only in dry-run**: the repo's `hooks/hooks.json` PostToolUse hook fires on any `Write|Edit` and runs `git add wiki/ .raw/`. Writing to `/tmp` does not stage /tmp, but it still triggers the hook, which will commit *any pending wiki changes* under a generic message. Dry-run must leave zero residue. Bash stdout does not fire the hook.

---

## Deterministic fold ID

Every fold has an ID derived from its inputs:

```
fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}
```

Example: `fold-k3-from-2026-04-10-to-2026-04-23-n8`.

The filename in commit mode is `wiki/folds/{FOLD-ID}.md`. No date-of-creation in the filename. No timestamp in the title.

**Duplicate detection (required)**: before emitting any output, check if `wiki/folds/{FOLD-ID}.md` already exists. If so, report "Fold already exists at wiki/folds/{FOLD-ID}.md. Use --force to overwrite, or pick a different range." and stop. This is the no-op idempotency guarantee; byte-identical content is NOT guaranteed (LLM prose varies) but the filename and scope are.

---

## Parameters

- `k` (default 4): batch exponent. Batch size = `2^k`. Typical values: k=3 (8), k=4 (16), k=5 (32).
- `range` (optional): explicit entry range `entries 1-16`. Overrides k.
- `--force`: overwrite an existing fold with the same ID. Default no.
- `--commit`: write to wiki/. Without it, dry-run stdout-only.

If fewer than `2^k` log entries exist, report the shortfall and stop. Do not silently fold a partial batch.

---

## Procedure

### 1. Parse log entries

```
grep -n "^## \[" wiki/log.md | head -{2^k}
```

Record for each entry: line number, date, operation, title, and the following bullet lines until the next `## [` or end-of-section.

### 2. Extract child page identifiers

From each entry's bullet list, extract:
- `Location: wiki/path/to/page.md` (the primary page)
- `[[Wikilinks]]` inline
- `Pages created:` and `Pages updated:` lists

Build a structured children list:
```yaml
children:
  - date: "2026-04-23"
    op: "save"
    title: "DragonScale Memory v0.2 — post-adversarial-review"
    page: "[[DragonScale Memory]]"
  - ...
```

One record per log entry. Do not dedupe by page: if two entries both point to `[[DragonScale Memory]]`, both records appear, distinguishable by date and title.

### 3. Read referenced pages (bounded)

Read only the pages that are not already captured fully in the log entry's bullets. Budget: 0-10 page reads. Hard ceiling: 15. If an entry's referenced page is missing, record `page_missing: true` and proceed.

### 4. Extractive summarization with count checks

Write the fold body per `references/fold-template.md`. **Rules**:

- **Extractive only.** Every outcome bullet and theme bullet must cite a specific child entry (e.g., `(from 2026-04-14 session)`) or a quoted line from that entry. Do not introduce events, counts, or interpretations not present in a child entry.
- **Log entry is the primary source.** If the log entry's bullets and the referenced meta-page disagree on a fact (e.g., a count), prefer the log-entry bullets and flag the mismatch as "source mismatch: log says X, meta says Y."
- **Count checks.** If you write "N concept pages" or "M repos updated," grep the source entries for the number and verify. Numeric mismatches are dry-run blockers.
- **No merging across entries without naming them.** A theme that spans multiple entries must name each contributing entry inline.
- **Uncertainty is a feature.** If an entry is ambiguous, say "ambiguous in source: [[Entry]]" rather than picking one interpretation.

### 5. Self-check before emitting

Before printing output, verify:
- Every child in `children:` frontmatter appears exactly once in the Child Entries table.
- Every entry in the table appears in the `children:` frontmatter.
- Every numeric claim in Key Outcomes is grep-verifiable against a child entry.
- The fold ID is deterministic and the file does not already exist (or `--force` is set).

If any check fails, abort and report the specific failure.

### 6. Emit

**Dry-run**: use Bash `cat <<'EOF' ... EOF` to stdout. Do not use Write. Print the fold ID and a one-line summary of what the commit step would do.

**Commit** (only after user says "commit the fold"):
1. `Write` the fold page to `wiki/folds/{FOLD-ID}.md`. (PostToolUse hook will auto-commit this.)
2. `Edit` `wiki/index.md` to add the fold link under a `## Folds` section (create section if missing). (Hook auto-commits.)
3. `Edit` `wiki/log.md` to prepend one entry:
   ```
   ## [YYYY-MM-DD] fold | batch-exponent-k{K} rollup of N entries
   - Location: wiki/folds/{FOLD-ID}.md
   - Range: {EARLIEST-DATE} to {LATEST-DATE}
   - Children: N log entries
   ```
   (Hook auto-commits.)

Three auto-commits result. The user sees three separate `wiki: auto-commit` entries in git log. This is expected; do not attempt to suppress the hook.

---

## Output schema

See `references/fold-template.md` for the canonical frontmatter and body layout.

---

## Invariants

1. **Structural idempotency**: same range + same k → same fold ID → duplicate detection prevents double-writes. LLM prose may vary across runs; the *location and scope* are fixed.
2. **Additive**: children are never modified.
3. **Bounded reads**: 0-15 child-page reads per fold.
4. **Extractive**: zero invented facts. Count checks enforced.
5. **No chaining**: wiki-fold does not invoke wiki-lint, wiki-ingest, autoresearch, or save.

---

## What NOT to do

- Do not use Write/Edit during dry-run. Bash stdout only.
- Do not include the current date in the fold filename or title. Use the child entry range.
- Do not silently dedupe children by page title. One record per log entry.
- Do not write "emergent themes" that span entries without naming which entries contribute.
- Do not claim byte-identical idempotency. Structural idempotency is the actual guarantee.
- Do not suppress or bypass the PostToolUse auto-commit hook.
- Do not update `wiki/hot.md`. Ownership stays with save/ingest skills.

---

## Reversal

Committed fold reversal (three commits, land in this order):
1. Remove the log.md fold entry.
2. Remove the index.md entry.
3. Delete the fold page file.

Or: `git revert` the three auto-commits. Child pages are untouched in either path.

---

## Example dry-run sequence

User: "fold the log, dry-run k=3"

1. Parse `wiki/log.md` top 8 entries.
2. Build structured children list (8 records).
3. Read 0-10 referenced pages as needed.
4. Produce fold ID: `fold-k3-from-2026-04-10-to-2026-04-23-n8`.
5. Check `wiki/folds/fold-k3-from-2026-04-10-to-2026-04-23-n8.md` does not exist.
6. Write fold body following the template.
7. Run self-check (frontmatter/table consistency, count verification).
8. Emit via `cat <<'EOF' ... EOF` to stdout.
9. Report: "Dry-run complete. Fold ID: {FOLD-ID}. To commit: 'commit the fold'."
