# Operation transactions

Use this reference whenever a skill will change vault state.

## Contract

One logical operation produces one versioned transaction bundle and one
recoverable apply. Parallel workers may read and draft, but only the
orchestrator applies vault mutations.

Resolve the installed product root from the invoking skill's own location, not
from the user-vault working directory:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Never use the deprecated per-file `wiki-lock.sh` helper for new work. Never
commit from a generic lifecycle hook.

## Workflow

1. Resolve a user vault. Prefer `--vault`, then `CLAUDE_OBSIDIAN_VAULT`, then
   `.claude-obsidian.json`, then unambiguous current-directory discovery.
2. Read every expected target and record its SHA-256, or `null` when it must be
   absent.
3. Have workers return drafts and evidence. Workers do not edit shared vault
   state.
4. Build one `claude-obsidian.transaction.v1` JSON bundle.
5. Run `python3 "$CORE" transaction inspect BUNDLE --vault VAULT`.
6. Show destructive, external, or canonical-merge proposals to the user before
   applying them.
7. Pass the inspect result's exact `approval_sha256`, which binds the expanded
   plan to the canonical resolved vault root and cannot be reused for another
   vault:
   `python3 "$CORE" transaction apply BUNDLE --vault VAULT --approved-plan-sha256 HASH`.
8. Report the resulting operation ID and changed paths.
9. If the user wants Git history, run the separate explicit checkpoint command.

## Bundle shape

```json
{
  "schema": "claude-obsidian.transaction.v1",
  "operation_id": "save-20260711-example",
  "operation_type": "save",
  "expected_hashes": {
    "wiki/concepts/Example.md": null
  },
  "writes": [
    {
      "path": "wiki/concepts/Example.md",
      "mode": "create",
      "content_file": "drafts/example.md",
      "sha256": "<sha256>"
    }
  ],
  "address_requests": [],
  "source_manifest_updates": {}
}
```

`content` may replace `content_file` for small drafts. Use exactly one. Raw
source payloads are create-only. `.raw/.manifest.json` and the address counter
are expanded and journaled by the transaction engine when managed requests are
present. Only `ingest` and `autoresearch` own non-empty managed requests;
`setup` and `migration` may initialize the managed files directly. Other
operation types cannot target them.

Operation types are enforced authorities, not labels: `base` writes only
`wiki/**/*.base`; `canvas` writes canvases under `wiki/canvases/` and its
optional `_index.md` catalog; `fold` writes exactly one `wiki/folds/*.md` page plus
`wiki/index.md` and `wiki/log.md`; `configuration` writes only
`.vault-meta/mode.json`; and `capture` creates only `.raw/captured/*` payloads.
Save, Markdown, lint repair, and generic extension bundles remain confined to
`wiki/`. `setup` and `migration` accept only the exact tracked vault-template,
ledger, and DragonScale bootstrap paths declared by the product contract; they
are not escape hatches for arbitrary root, plugin, snippet, metadata, or wiki
files. Paths that collide by case are rejected for macOS portability.

One content or predecessor file may be at most 64 MiB, and one operation's new
content or recovery backups may total at most 128 MiB. Split larger work at a
logical boundary before inspection; the engine rejects an operation it could
not roll back under the same limits.

One operation may contain at most 1,024 writes. Each canonical vault-relative
path may use at most 1,024 UTF-8 bytes. File-backed transaction bundles must be
no-follow regular files and may use at most 136 MiB; journals and completed
results are preflighted against the same 8 MiB cap used by recovery. These
limits ensure that every accepted operation remains readable and recoverable.

The lock retains the selected vault and `.vault-meta` directory descriptors
for the whole operation. Targets, journals, results, backups, capture queues,
checkpoints, and derived retrieval publications use no-follow descriptor-based
I/O, so replacing a public root, metadata, transaction, operation, or backup
entry cannot redirect reads, writes, rollback, or cleanup outside the selected
vault. This confinement requires POSIX directory descriptors and
`fcntl.flock`; Windows users must run the skill under WSL rather than native
Windows or Git Bash (setup and troubleshooting: `docs/windows-wsl.md`).

## Required coupled writes

- Save: note, index, log, hot cache.
- Ingest: source capture when applicable, pages, ingestion/evidence records,
  indexes or MOCs, log, hot cache, and optional overview.
- Autoresearch: cited research pages and evidence records. Canonical merge is a
  separate approved transaction.
- Fold: fold page, index, log.
- Canvas: canvas plus catalog metadata only when that metadata changes.
- Lint repair: approved fixes plus regenerated report/index.
- Query: read-only. Delegate persistence to Save.

## Failure behavior

- Exit 75 means the vault changed or another operation holds the mutation lock.
  Re-read, rebuild, and inspect a new bundle.
- Validation failure means no vault write occurred.
- An interrupted apply is recovered or rolled back by the next apply, or by
  `transaction recover`.
- Recovery never steals an old lock merely because its age elapsed. After
  independently confirming that no writer is active, an operator may use
  `transaction recover --force-stale-lock`; the same explicit override exists
  for `capture queue recover`. Do not automate either override.
- Never paper over a transaction failure with `|| true`.

## Explicit checkpoint

```bash
python3 "$CORE" checkpoint OPERATION_ID --vault VAULT \
  --as-of YYYY-MM-DD
```

Checkpointing is never automatic. It refuses all pre-existing staged state,
verifies the candidate tree's blob bytes against transaction hashes, runs
deterministic lint by default, and excludes raw source payloads unless the user
explicitly opts in. `--as-of` pins and records the UTC provenance audit date; a
pending record resumes the same commit and pinned date after interruption.
