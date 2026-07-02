# Multi-Source Consolidation Guide

How to merge several vaults (or one vault plus a pile of external sources)
into a single compounding wiki without losing data, leaking data, or breaking
the link graph. These patterns were battle-tested consolidating four live
vaults (~10,000 files) into one, and they generalize to any migration where
the sources contain anything you would not publish.

Three tools in this repo back the guide:

| Tool | Role |
|---|---|
| `bin/setup-perimeter.sh` | deny-by-default privacy boundary (git hooks) |
| `scripts/graph-lint.py` | link-graph health check after every merge wave |
| `scripts/wiki-lock.sh` | per-file locks when several writers ingest at once |

## The consolidation loop

Each source (a vault, an export, a folder of documents) goes through the same
loop. Run it per source, never "all sources at once" — a failed wave should be
one revert, not an archaeology project.

```
import (copy-forward) → dedup → weave → lint → commit
```

1. **Import, copy-forward only.** The source is read, never modified. Before
   copying, hash the whole source tree (`find ... | sha256sum`) and hash it
   again after: byte-identical manifests are your proof the source survived.
   Keep sources intact until the migration is verified end to end — they are
   your rollback anchor.

2. **Dedup by normalized name, not by identifier.** Two vaults describing the
   same thing rarely share an ID, but they usually share a title. Normalize
   (lowercase, strip diacritics/punctuation) and compare. For candidate pairs,
   diff the content — and normalize line endings first: CRLF/LF noise routinely
   shows up as ">1% divergence" between files that are actually identical
   (`diff <(tr -d '\r' < a) <(tr -d '\r' < b)`).

3. **Weave, don't just copy.** A page that lands without inbound links is
   invisible to future retrieval. Every imported page gets: a link from the
   relevant MOC or `_index.md`, and (if your vault uses hierarchy frontmatter)
   an `up:` pointing at an existing note — never at a folder name.

4. **Lint the graph after every wave.** `python3 scripts/graph-lint.py --root wiki`
   reports broken links, broken `up:`, and orphans. Classify before you fix:
   calendar dates and planned-but-unwritten pages are *legitimate* dangling
   links — whitelist them (`.vault-meta/graph-lint-whitelist.txt`) instead of
   editing the files that mention them. What remains is either genuinely
   broken (fix it) or a creation backlog (document it).

5. **Commit per wave, with a reversible map.** One commit per source/wave,
   and a machine-readable map (CSV of `old-path,new-path`) committed alongside.
   Reversibility is what makes an aggressive migration safe.

## Hardened migration (for sensitive sources)

When a source contains anything private — personal notes, client data,
identifiers — the import step needs teeth. The pattern, in order of the
guarantees it gives you:

- **Dry-run by default.** The migration script copies nothing unless invoked
  with an explicit `--apply`. The default run prints what *would* happen.
- **Scan before add.** After copying, scan every copied file (secrets baseline
  plus your own identifier patterns) *before* any `git add`. A file that fails
  the scan is deleted from the destination, not committed "to fix later".
- **Index-only tier.** Version taxonomy/index files; leave verbatim sensitive
  content untracked (or in a gitignored band). Most retrieval value lives in
  the index layer anyway.
- **Manifest proof.** Source hashed before and after (see loop step 1).
- **Anti-operator brakes.** The failure mode is not the script — it is the
  operator approving zone after zone in one sitting. Two deterministic brakes:
  (a) *retype confirmation*: committing a sensitive zone requires re-typing the
  zone name exactly (no blind re-runs); (b) *cooldown*: refuse to commit a
  second sensitive zone within N hours of the previous one.

And the lesson that motivates all of it: **pattern-based PII scanning is not
sufficient.** Regexes catch well-formed identifiers; they miss hyphenated
variants, names, addresses, and — worst of all — real data disguised as
"examples" inside templates and course material. For anything you publish or
back up off-machine, exclude the entire example/case layer wholesale rather
than trusting a scrub. The perimeter (below) is the last line of defense, not
the only one.

## The privacy perimeter

`bash bin/setup-perimeter.sh` installs two git hooks (opt-in, local-only,
nothing leaves your machine):

- **pre-commit** blocks the commit if a staged path matches a sensitive band
  glob (`.vault-meta/perimeter-paths.txt`) or an added line matches an
  identifier/secret regex (`.vault-meta/perimeter-patterns.txt`), minus a
  whitelist of known false positives (`.vault-meta/perimeter-whitelist.txt`).
- **pre-push** (with `--air-gap`) blocks *every* push, for vaults that must
  never leave the machine.

Overrides exist and are single-shot on purpose (`PERIMETER_ALLOW=1`,
`PERIMETER_ALLOW_PUSH=1`): a human types them per incident, scripts don't.
Run `bash bin/setup-perimeter.sh --check` for a status readout and
`--uninstall` to remove the hooks (pre-existing hooks are backed up and
restored automatically).

Two operational notes, both learned the hard way:

- gitignore a *future* sensitive directory with both forms (`x` and `x/`):
  directory-only patterns don't match `git check-ignore x` while the
  directory doesn't exist yet.
- third-party installers and CLIs can run `git init` or add remotes over the
  current directory — never run them from inside an air-gapped vault.

## Merge governance

Interpretive decisions (which duplicate wins, what gets renamed, what gets
quarantined) need provenance, or the second migration relitigates the first.
Two small documents, kept in the vault and committed with each wave:

- **A dedup ledger.** One line per merge decision: the pair, the winner, the
  tie-break rule applied, the date. When sources conflict, declare the
  precedence order *once* at the top (`source A > source B > source C`) and
  mark canonical pages with `ssot: true` frontmatter so later ingests defer
  to them.
- **A pending-decisions quarantine.** Anything requiring human judgment
  (ambiguous PII, conflicting versions of the same reference, bulk moves of
  sensitive records) gets parked in a `decisions-pending.md` with enough
  context to decide later. The loop continues; the human decides on their own
  schedule; each resolved item records who decided and why. An empty
  quarantine is the definition of "consolidation done".

If multiple agents write during a merge wave, guard every page write with
`scripts/wiki-lock.sh acquire`/`release` (see the concurrency section in
`CLAUDE.md`) — the loop above is safe for parallel ingest as long as writers
lock per file.
