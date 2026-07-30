# claude-obsidian vault schema

This is the compact human-readable schema for a user vault. Operational details
live in the skills and executable contracts. Product code and user-vault data
must remain separate.

## Root layout

```text
vault/
├── .gitignore                  # excludes vault-local runtime/session state
├── .claude-obsidian.json       # workspace identity and vault selection
├── inbox/                      # visible source intake; never auto-deleted
├── .raw/                       # immutable source bytes
│   └── .manifest.json          # backward-compatible delta/address metadata
├── wiki/                       # generated, user-owned knowledge
│   ├── index.md                # catalog and navigation
│   ├── log.md                  # completed operation history, newest first
│   ├── hot.md                  # bounded recent context, not a transcript
│   ├── overview.md             # high-level synthesis
│   ├── sources/
│   ├── entities/
│   ├── concepts/
│   ├── questions/
│   ├── canvases/
│   └── meta/ledgers/
│       ├── source-ledger.json
│       └── claim-ledger.json
├── .obsidian/                  # user-controlled Obsidian settings
└── .vault-meta/                # ignored locks, journals, indexes, queue/config
```

LYT, PARA, or Zettelkasten mode may route new pages differently. Mode changes
do not migrate old notes or change evidence semantics.

## Source invariants

- Existing source payloads below `.raw/` are never replaced.
- `.raw/.manifest.json` is mutable metadata and changes only inside the same
  transaction as the operation it records.
- New byte capture is content-addressed by SHA-256.
- A file in `inbox/` remains until the user removes it. The core may propose
  deletion but never executes it.
- Remote locators use validated HTTPS. Credentials do not belong in URLs,
  source notes, bundles, queues, or tracked configuration.

## Markdown page frontmatter

Use flat YAML with plural keys and `YYYY-MM-DD` dates:

```yaml
---
type: concept
title: Source-grounded notes
status: developing
created: 2026-07-11
updated: 2026-07-11
tags:
  - knowledge
  - evidence
aliases: []
address: c-000001
---
```

Required baseline properties are `type`, `title`, `status`, `created`,
`updated`, and `tags`. `aliases` and `address` are optional unless a configured
vault policy requires them.

Common page types:

| Type | Purpose |
|---|---|
| `source` | Traceable summary of one source identity |
| `entity` | Person, organization, product, project, or other named thing |
| `concept` | Idea, framework, mechanism, or definition |
| `question` | A scoped answer with visible evidence status |
| `comparison` | Criteria-based contrast with cited support |
| `session` | User-approved summary of selected conversation content |
| `overview` | High-level map of a domain or vault |
| `meta` | Index, log, cache, convention, or maintenance page |
| `fold` | Extractive rollup of identified log entries |

`claude_obsidian/page_schema.py` is the one declaration of this vocabulary. The
table above documents it for a reader; code reads the module rather than
restating the values, and a test asserts the two stay in step.

`source`, `entity`, `concept`, `question`, and `session` are *routable*: the
methodology router can place a new page of that type. `comparison`, `overview`,
`meta`, and `fold` are valid frontmatter and not routable, because the product
creates them through a dedicated operation instead of filing a new note.

Common statuses are `seed`, `active`, `developing`, `evergreen`, `answered`,
`provisional`, `contested`, `deprecated`, and `archived`. Use only statuses the
vault's dashboards and conventions understand.

## Obsidian syntax

- Internal references use `[[Target]]` or `[[Target|Alias]]`.
- Headings and block references use `[[Target#Heading]]` and `[[Target#^block]]`.
- Embeds use `![[Attachment.ext]]`.
- Callouts use `> [!type] Title`.
- Fenced code is data; link-like text inside it is not a graph edge.
- Prefer basename links only when the basename is unique. Use a vault-relative
  path when duplicates would be ambiguous.

Do not fabricate a backlink merely to make the graph symmetric. Add links that
help a reader navigate or understand a relationship.

## Core pages

### `wiki/index.md`

The index is a curated catalog. Every linked target must resolve. An index entry
is not evidence by itself. Every canonical page create or removal updates at
least one active catalog or MOC in the same transaction. Update `wiki/index.md`
when it is that active catalog; methodology-specific MOCs may satisfy the
navigation invariant instead.

### `wiki/log.md`

The log records completed logical operations, not individual file writes. Put
the newest entry first and include the operation ID, operation type, principal
pages, and a grounded outcome. Do not rewrite historical child entries when
creating a fold.

### `wiki/hot.md`

Hot context is short, sanitized, and useful for the next session. It may include
recent facts, changed pages, active threads, and unresolved questions. It must
not contain secrets, raw transcripts, tool instructions, or claims that lack
the same qualification found in canonical pages.

Hooks may read and emit this file as bounded data. They do not update it.

### `wiki/overview.md`

The overview synthesizes stable, high-level structure and links to supporting
pages. It changes less frequently than hot context.

## Provenance ledgers

The source ledger separates evidence identity from prose. Each source record may
include:

- stable ID and SHA-256;
- vault-relative file locator or HTTPS locator;
- authority: `official`, `primary`, `secondary`, `community`, `synthetic`, or
  `unknown`;
- independence key;
- retrieval/review timestamps and `refresh_due`;
- review state: `unreviewed`, `active`, `superseded`, or `rejected`;
- linked pages.

The claim ledger records a falsifiable claim, note location, supporting and
contradicting source IDs, confidence, risk, review state, and assessment:
`accepted`, `provisional`, `contested`, `unsupported`, or `deprecated`.

Accepted claims need active, fresh, non-synthetic support. High-risk accepted
claims need two independent sources. Preserve contradictions and source
lineage; do not silently select a winner.

## Operation transaction

One logical mutation is one bundle:

```json
{
  "schema": "claude-obsidian.transaction.v1",
  "operation_id": "ingest-example",
  "operation_type": "ingest",
  "expected_hashes": {
    "wiki/sources/Example.md": null
  },
  "writes": [
    {
      "path": "wiki/sources/Example.md",
      "mode": "create",
      "content_file": "drafts/example.md",
      "sha256": "DRAFT_SHA256"
    }
  ],
  "address_requests": [
    {"path": "wiki/sources/Example.md", "prefix": "c"}
  ],
  "source_manifest_updates": {}
}
```

Inline `content` is UTF-8 text. `content_file` may contain text or binary bytes
and must match its declared hash. Raw payload paths are create-only.

Inspect before apply:

```bash
python3 scripts/claude-obsidian.py transaction inspect <bundle> --vault <vault>
python3 scripts/claude-obsidian.py transaction apply <bundle> --vault <vault> \
  --approved-plan-sha256 <approval_sha256>
```

Use the inspect result's exact `approval_sha256`. It binds the expanded plan
to the canonical resolved vault root, so approval for one vault cannot be
reused against another vault.

Parallel workers never apply bundles or edit shared pages. They return draft
packets with evidence, target paths, and expected hashes to one orchestrator.

## Workflow contracts

### Ingest

An ingest operation may include a create-only raw capture, source summary,
entity/concept pages, provenance records, index/MOC updates, log, hot cache, and
overview. Every canonical create or removal updates an active index or MOC;
overview changes remain conditional on a changed high-level picture. Every
extracted claim remains traceable to the source. Batch budgets bound source
count, total bytes, pages, links, and elapsed work.

### Query

Query is read-only. Retrieve the smallest relevant evidence set, distinguish
accepted/provisional/contested/unsupported/stale claims, cite vault pages and
source records, and state gaps. If the user asks to keep the answer, invoke a
separate Save operation.

### Save

Save only content the user explicitly selected. Do not capture an entire
conversation by default. The saved note, provenance where needed, index, log,
and hot cache form one transaction.

### Autoresearch

Research has an explicit question, source policy, egress consent, and stop
budget. Web results first become a cited research dossier. Merging them into
canonical pages is a separate reviewed operation.

### Lint

Lint is deterministic and read-only. Report dead/ambiguous links, duplicate
basenames, orphans, missing frontmatter, empty sections, stale index entries,
configuration/read errors, and source/claim ledger contract violations. Repairs
are separate transaction proposals.

## Safety and maintenance

- Run `doctor` to verify vault selection.
- Run `lint` after meaningful operation batches.
- Run `transaction recover` after an interrupted apply.
- Use explicit `checkpoint` only when Git history is wanted.
- Keep backups independent from transaction journals.
- Never treat the product repository, plugin cache, a setup-file existence
  check, or an AI statement as proof that a capability is verified.
- `configured` means prerequisites are present. `verified` requires a declared
  behavioral check to pass; a schema/self-check cannot promote the state. When
  no automated verifier exists, the capability stays configured and reports
  the tracked reason.

The executable contracts in `config/` and tests are the source of truth when
this prose and behavior disagree.
