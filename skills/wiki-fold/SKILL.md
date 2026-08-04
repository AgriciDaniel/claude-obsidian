---
name: wiki-fold
description: "Create a bounded, extractive, structurally idempotent rollup of recent Obsidian wiki log entries, with dry-run preview by default and one optional transaction apply. Use for manual log compression without modifying child pages. Triggers: fold the log, run a fold, run wiki-fold, log rollup, roll up log entries, commit the fold."
---

# Extractive log fold

Create an additive rollup of raw `wiki/log.md` entries. Never modify, move, or
delete child entries or their pages. Do not perform fold-of-folds or trigger a
fold automatically.

Resolve the portable core from this skill's installation. Resolve the user vault
by explicit `--vault`, `CLAUDE_OBSIDIAN_VAULT`, workspace config, then
current-directory discovery. Never treat the plugin/product root as a vault.

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

This skill needs no network egress. Do not call external services.

## Select a bounded range

Use batch exponent `k` with size `2^k`; default to `k=4`. An explicit entry range
may override it. If fewer entries exist than requested, report the shortfall and
stop rather than folding a partial batch.

Read the selected log entries completely. Read referenced child pages only when
the log lacks enough context: target 0-10 reads, hard ceiling 15. Missing pages
remain explicit `page_missing` records.

Derive the structural ID only from inputs:

```text
fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}
```

If `wiki/folds/{FOLD_ID}.md` already exists, return a no-op. Replacing it requires
an explicit force request and a separately reviewed `replace` proposal.

## Draft extractively

Follow [fold-template.md](references/fold-template.md). Every child log entry must
have one deterministic `child_key` in frontmatter and exactly one matching row
in the Child Entries table. Do not deduplicate children by page, although the
final Child Pages link list may be deduplicated.

Every outcome must name its source entry. Every number must be verifiable in the
selected entry. A cross-entry theme must name at least two contributing entries.
Prefer `ambiguous in source` or `source missing` to invention. When a child page
and log entry disagree, preserve both and identify the mismatch; the log entry is
the fold's primary source.

Run these checks before proposing any write:

- deterministic ID and exact entry count;
- frontmatter/table bijection;
- numeric traceability;
- source citation for every outcome and theme;
- no change to a child, source, source ledger, or claim ledger.

A fold adds no new factual evidence, so it does not upgrade claim assessments or
create source records. Report discovered contradictions for later review instead
of editing canonical claims.

## Preview by default

Return the complete fold draft, ID, child range, read budget, and proposed changed
paths without modifying the vault. Parallel agents may check child entries and
return extracts, but only the orchestrator assembles the fold; workers never
write.

When the user explicitly says to apply or commit the fold, build one
`claude-obsidian.transaction.v1` bundle with `operation_type: fold`. Read
[the transaction contract](../wiki/references/operation-transactions.md). Couple:

- `wiki/folds/{FOLD_ID}.md` in `create` mode by default;
- the fold catalog entry in `wiki/index.md`;
- one new top-of-file fold entry in `wiki/log.md`, using the literal op token
  `fold` (`## [DATE] fold | ...`). That token is reserved for this marker: the
  Stop hook's fold-backlog check identifies already-covered log history by
  scanning for it, so no other skill or manual entry should reuse it.

Do not update `wiki/hot.md`. Record SHA-256 preconditions for all three targets.
Do not use host Write/Edit, Obsidian transport writes, deprecated locks, automatic
commits, or one apply per file.

Inspect before the single apply:

```bash
python3 "$CORE" transaction inspect /path/to/fold-bundle.json --vault /path/to/vault
# Set APPROVAL_SHA256 to the inspect result's approval_sha256 after review.
python3 "$CORE" transaction apply /path/to/fold-bundle.json --vault /path/to/vault \
  --approved-plan-sha256 "$APPROVAL_SHA256"
```

Report the operation ID and exact changed paths. The identical bundle and ID are
idempotent. On exit 75, re-read and rebuild; after interruption, use
`transaction recover`.

Git history is a separate optional action:

```bash
python3 "$CORE" checkpoint OPERATION_ID --vault /path/to/vault
```

Observe all selected entries, verify traceability and counts, then grow the
rollup only from what its children actually say.
