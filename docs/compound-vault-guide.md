# Compound Vault architecture

The Compound Vault is claude-obsidian's operational model for a local,
source-cited knowledge base. The v1.10 foundation replaces historical
per-file-lock and lifecycle-write behavior with explicit vault selection and
recoverable operation transactions.

## Roles

| Role | Contains | Mutation policy |
|---|---|---|
| Product package | Skills, Python core, scripts, hooks, templates | Changed by product development only |
| User vault | Notes, sources, ledgers, Obsidian settings | Changed by reviewed vault operations |
| Derived runtime | Locks, journals, retrieval indexes, capture queue | Vault-local, ignored, recoverable/regenerable |
| Public artifact | Allowlisted product files and synthetic samples | Rebuilt from a clean Git snapshot |

An installed plugin cache is always product code. It never becomes the user
vault. Resolve vault state through `--vault`, `CLAUDE_OBSIDIAN_VAULT`, workspace
config, or current-directory discovery.

The development checkout and public marketplace root are distinct roles even
when they share history. Development source stores the reviewed marketplace
template under `config/`; the release builder injects it at
`.claude-plugin/marketplace.json` only after selecting and auditing the clean
artifact. Public default-branch promotion uses the extracted artifact and
requires owner approval.

## Knowledge layers

- `inbox/` is visible, user-controlled intake. Capture never deletes it.
- `.raw/` stores immutable payloads and the legacy ingestion manifest.
- `wiki/` stores generated pages, index, log, hot cache, and evidence ledgers.
- `.vault-meta/` stores runtime locks, transaction journals, queues, indexes,
  and optional configuration.

New vaults include a `.gitignore` that excludes `.vault-meta/` in full because
journals, queues, and derived chunks may contain note text, local paths, or
source URLs. Existing vaults should adopt the same default deliberately without
overwriting their current ignore policy.

`wiki/hot.md` is a bounded context cache, not a transcript. `wiki/log.md`
records completed operations. Source and claim ledgers keep provenance separate
from legacy delta tracking.

## One operation, one transaction

A save, ingest, fold, canvas update, research merge, or approved lint repair is
one `claude-obsidian.transaction.v1` bundle:

1. Read every target and record its current SHA-256 or expected absence.
2. Let parallel workers produce drafts and evidence without shared writes.
3. Merge the full logical change into one bundle.
4. Inspect it without mutation.
5. Obtain consent for destructive, external, or canonical-merge consequences.
6. Apply once under the vault-wide process-lifetime lock.
7. Report the operation ID and exact changed paths.

The engine journals originals, verifies content hashes, uses fsync and atomic
replacement, and restores prior state after a failed or interrupted apply.
Concurrent target changes return conflict exit 75. Re-read and build a new
operation; never force an old plan through.

One transaction content or predecessor file is limited to 64 MiB; aggregate
new content and aggregate recovery backups are each limited to 128 MiB. A
transaction has at most 1,024 writes and preflights its journal/result against
recovery's 8 MiB reader cap. The capture queue uses the same limit for reads and
writes (8 MiB canonical JSON, at most 4,096 entries), preserving recoverability
under bounded resources.

Mutation safety is bound to open directory descriptors, not later pathname
lookups. The vault root, metadata runtime, transaction operation, backups,
capture queue, checkpoint state, and retrieval publications remain pinned for
their complete mutation window. Concurrent alias replacement therefore fails
closed or rolls back without touching a replacement tree. These guarantees
require WSL/Linux or supported macOS; native Windows and Git Bash are not
supported mutation hosts and are refused with `UNSUPPORTED_PLATFORM` before
any side effect. Read-only inspection and dry-runs run natively on Windows
using point-in-time lstat validation (symlink and junction rejection) instead
of descriptor pinning. Platform specifics and WSL troubleshooting live in the
[Windows and WSL guide](windows-wsl.md).

Raw source bytes can be supplied through hash-checked binary `content_file`
writes, but their destination mode is create-only. Address allocation, page
frontmatter, address map, source manifest, index, log, and hot cache can move in
the same journaled operation.

Read [the transaction reference](../skills/wiki/references/operation-transactions.md).

## Read paths and transport

Filesystem reads are the portable baseline. `scripts/detect-transport.sh`
reports the official Obsidian CLI as ready only when the command, application,
and required capability work. Detection defaults to read-only `--peek`.

Obsidian CLI may accelerate reads and search. It is not a second mutation path:
all writes still go through the transaction core. This avoids races between
Obsidian, agent tools, and parallel workers.

## Retrieval

The optional retrieval pipeline stores contextual chunks and BM25 state below
`.vault-meta/`. Provisioning is preview-first:

```bash
bash bin/setup-retrieve.sh --vault <vault> --no-llm
bash bin/setup-retrieve.sh --vault <vault> --no-llm --apply
```

BM25 is deterministic and local. Optional cosine reranking defaults to the
multilingual `nomic-embed-text-v2-moe` Ollama model, which is approximately
958 MB and is never downloaded automatically. Nomic embeddings use distinct
`search_query:` and `search_document:` task prefixes. Users who already have
the smaller English-oriented v1.5 model can select it explicitly with
`--model nomic-embed-text`; multilingual vaults should retain the v2 default.
Nomic v2 has a 512-token input context, and Ollama truncates longer embedding
inputs by default; BM25 still scores the complete chunk. If the selected model
is missing or an embedding stage fails, results fall back completely to BM25
order and scores. Deleted, changed, or escaping chunk records are rejected, and
page deduplication happens before the final top-K.

Retrieval queries are bounded at 8,000 normalized characters and result counts
at 1 through 1,000. Oversized queries and invalid limits fail explicitly. An
untagged Ollama model request matches only the corresponding untagged name or
its `:latest` alias; other installed tags must be selected by their exact name.

Contextual-prefix model calls require `--allow-egress`. Remote Ollama requires
`--allow-remote-ollama`. Neither is inferred from an environment variable
alone.

## Evidence

The source ledger records content identity, authority, independence, freshness,
review state, and linked pages. The claim ledger records falsifiable claims,
support, contradictions, confidence, risk, and assessment.

- Accepted claims need current active non-synthetic support.
- High-risk accepted claims need two independent sources.
- Sources with one independence key count as one line of evidence.
- RFC-equivalent URL spellings count as one origin, including normalized IPv6,
  IDN, Unicode/UTF-8 percent encoding, and default ports.
- Contradictions remain visible.
- Unsupported is a valid state; invented citations are not.

Read [the provenance reference](../skills/wiki/references/provenance.md).

## Hooks

Claude's SessionStart hook is silent by default. It emits bounded, sanitized hot
context only when a user vault resolves and the user has explicitly exported
`CLAUDE_OBSIDIAN_SESSION_CONTEXT=1`; hook stdout becomes model context, so this
opt-in is an egress decision. The Stop hook reports incomplete transactions and,
advisory-only, a `wiki/log.md` backlog nearing the wiki-fold batch size. It
never runs a fold itself, since wiki-fold stays human-invoked.
Hooks do not update notes, capture conversations, stage files, or commit Git.
Hosts without hooks use the same core workflows.

## Capture

Filesystem byte capture is the only internally implemented adapter. It performs
a full read-only preflight, then the CLI applies all new content-addressed raw
copies as one binary-capable transaction. Image, PDF, and EPUB format metadata
is local; semantic extraction is not built in. URL, YouTube, and OCR actions are
inert consent plans for a separately configured runner.

## Maintenance and recovery

```bash
python3 scripts/claude-obsidian.py doctor --vault <vault>
python3 scripts/claude-obsidian.py lint --vault <vault> --as-of YYYY-MM-DD
python3 scripts/claude-obsidian.py transaction recover --vault <vault>
```

Lint is deterministic for its declared UTC audit date and read-only. Any fix is a separate reviewed
transaction. Git checkpointing is also separate and explicit; it verifies exact
blob bytes, refuses pre-existing staged content, advances history by
compare-and-swap, and excludes raw bytes unless the user opts in.
If a stale lock remains after a crash, first verify no writer is alive; only
then use `transaction recover --force-stale-lock`. Never automate the override.

## Upgrade path

Existing layouts stay readable. Preview the additive migration before applying:

```bash
python3 scripts/claude-obsidian.py migrate --vault <vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed
python3 scripts/claude-obsidian.py migrate --vault <vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Migration adds missing workspace/provenance state, preserves the legacy manifest
byte-for-byte, and does not infer claims from prose. The deprecated
`scripts/wiki-lock.sh` remains for v1 compatibility only and must not be used by
new workflows.
