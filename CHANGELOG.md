# Changelog

Notable changes to claude-obsidian are recorded here using
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) categories and
[Semantic Versioning](https://semver.org/). Git history retains the detailed
implementation record for older releases.

## [Unreleased]

### Added

- Stop hook: an advisory-only line when `wiki/log.md` holds at least 85% of a
  wiki-fold batch (`2**k` entries, default `k=4`, override with
  `CLAUDE_OBSIDIAN_FOLD_BATCH_EXPONENT`) above its most recent `fold` marker.
  It reads at most the first 512 KiB of the log, is appended after any
  recovery warnings, never recommends `transaction recover`, and never runs
  wiki-fold or writes to the vault, since folding stays human-invoked per
  `skills/wiki-fold/SKILL.md`.

## [2.2.0] - 2026-09-10

Backlog triage: lint scoping, lock recovery, host validation, the `bin/`
to `scripts/` move for claude.ai plugin distribution, a single page-type
vocabulary, gitignore-aware link resolution, and a ZCode host adapter.

### Added

- `docs/windows-wsl.md`: a "Claude Code hooks and python3 on Windows" section
  and a platform-support-matrix row documenting that hooks require an
  interpreter reachable as `python3` on `PATH`, with native Windows setup
  notes for the python.org installer and the Microsoft Store alias stub.
- `hooks/README.md` and `README.md`: a stated minimum Claude Code
  requirement (a current release; the exec-form `args` command hook and the
  `compact` `SessionStart` matcher need it), linking to the Claude Code hooks
  contract.
- A repeatable `lint --exclude GLOB` CLI flag and a matching
  `lint_vault(..., exclude=...)` engine parameter scope specific paths (for
  example a `wiki/scratchpad/` folder) out of page, link-resolution, orphan,
  frontmatter, empty-section, and stale-index scanning. The same glob list
  may be set vault-side via an `exclude` (or `exclude_globs` /
  `excluded_paths`) array in `.vault-meta/lint.json`, `lint-allowlist.json`,
  or `wiki-lint.json`; CLI and vault-config patterns are combined. The
  report's new `summary.excluded_paths` count reports how many walked files
  were dropped.
- `claude_obsidian/page_schema.py` declares the page-type vocabulary once,
  separating every valid `type` value from the subset the methodology router can
  file. `wiki-mode.py` derives its accepted types from it instead of
  keeping a fifth hand-maintained copy.
- `question` is routable in all four modes, with a `questions_folder` generic
  setting that defaults to `wiki/questions/`. Note the asymmetry: only `generic`
  routes it through a configurable folder key; `para` places questions under
  `resources_folder + "questions/"`, matching how that mode treats its siblings.
- `wiki-mode.py route` now exits `6` for a valid-but-unroutable page type and
  keeps `4` for an unknown one. The two are different problems with different
  fixes, so a script branching on `$?` can tell them apart — not only a human
  reading stderr.

### Changed

- `ATTRIBUTION.md` now credits the contributor designs behind the reranker task
  prefixes (PR #77, maartengoet) and the BM25 fallback order fix (PR #62,
  vinsocci) that v2.0.0 adopted.
- The five setup shell scripts (`setup-dragonscale.sh`, `setup-mode.sh`,
  `setup-multi-agent.sh`, `setup-retrieve.sh`, `setup-vault.sh`) moved from
  the top-level `bin/` directory to `scripts/`. claude.ai rejects any plugin
  that ships a top-level `bin/` directory (it is reserved for the plugin's
  Bash `PATH`); this repository never relied on that PATH behavior, so the
  only change is the invocation path, for example `bash bin/setup-mode.sh`
  becomes `bash scripts/setup-mode.sh`. Update any local scripts, aliases, or
  CI that reference the old `bin/` paths. `RELEASE_MANIFEST.json` and
  `SHA256SUMS` are refreshed at release time.
- ZCode host adapter (`--host zcode`) for portable, user-level skill discovery
  into `~/.zcode/skills/`, with a `ZCODE.md` instruction pointer.

### Fixed

- `wiki-mode.py route` rejected `question`, `comparison`, `overview`, `meta`, and
  `fold` — five of the nine page types WIKI.md documents — and did so through a
  bare exit with no message, so a typo and a valid-but-unroutable type were
  indistinguishable. Rejections now explain which case applies.
- The frontmatter reference no longer restates a shorter type list that omitted
  `session` and `fold`, and the save skill no longer names `synthesis`/`decision`
  types that no other source declares.
- The scaffolded vault's `.obsidian/app.json` now pins Obsidian's "New link
  format" setting to `absolute`. It was previously left unset, defaulting to
  Obsidian's own "shortest path when possible" — links created through
  Obsidian's UI under that default resolve fine inside Obsidian but are
  unresolvable (or, once a second file shares a basename, silently wrong) to
  every other link-touching part of the product, which all resolve wikilinks
  by exact vault-relative path with no fuzzy resolution: resync scripts, the
  terminology linker, and lint's dead/ambiguous-link detection.
- The repository root `.gitignore` now ignores `.mcp.json`, matching the vault
  template and the install guide, which treat a project-scope MCP config as a
  potential credential carrier. Suggested by PR #44.
- `stop_status` now reads transaction journals up to the package's existing
  8 MiB runtime JSON bound, so large valid journals are not misreported as
  unreadable. Unsafe or unreadable journals now require manual inspection, and
  recovery advice is scoped to journals with a recognized recoverable state.
- `checkpoint` now honors Git's false values for `core.filemode`. Git ignores
  working-tree executable-bit differences in that mode, so checkpoint keeps
  strict content verification while skipping executable-mode comparison.
- Anthropic contextual-prefix responses now have a 256 KiB read cap in addition
  to the existing timeout, preventing an oversized response from consuming
  unbounded memory. Response-body read failures, invalid UTF-8, excessive JSON
  nesting, and malformed response shapes fail closed.
- `tests/test_contextual_prefix.py` and `tests/test_wiki_mode.py` no longer
  crash on native Windows before their assertions finish running. Both print
  `→` in test labels; Windows' default `cp1252` console encoding raised
  `UnicodeEncodeError` on the first such print. Both files now reconfigure
  stdout to UTF-8 on startup, guarded so a captured/redirected runner without
  a `reconfigure`-capable stdout still runs.
- `capture.py`'s public-host validator now rejects hex-dotted, octal-dotted,
  and short-form loopback spellings (`0x7f.0.0.1`, `0177.0.0.1`, `127.1`,
  `0x7f.0x0.0x0.0x1`) that `ipaddress.ip_address()` does not parse and that
  previously fell through to only a single-label check. Mirrors the existing
  numeric-label rejection in the source-ledger URL canonicalizer.
- Twelve `SKILL.md` files that link into `skills/wiki/references/` now state
  that a `../wiki/references/` link resolves relative to the skill's own
  directory under `$PRODUCT_ROOT`, never the selected vault's `wiki/`
  directory. Package validation now flags any such link missing that anchor
  sentence.
- Lint no longer walks dot-prefixed directories (`.raw/` ingest archives,
  `.claude/` agent worktrees, Obsidian's own `.trash/`, and similar) by
  default, matching Obsidian's own indexer. Previously a duplicated or
  archived page under a dot-prefixed folder became a real link-resolution
  candidate, turning a single healthy `[[Wikilink]]` into a spurious
  `ambiguous_targets` (and, on index pages, `stale_index_entries`) finding.
- `--force-stale-lock` can now reap a mutation lock or capture queue lock
  younger than `--stale-after` when the recorded owner PID is confirmed dead
  on the same host. It still never reaps a live same-host owner before
  `--stale-after` elapses and still keeps the age gate for a foreign-host or
  unresolvable owner. Both `recover` help texts now describe this precisely.
- Reading transaction runtime files now tolerates an external mtime-only
  touch (for example a sync client refreshing metadata) by re-reading once
  and accepting the content only if the bytes are identical to the first
  read. Any size, inode, device, or mode change, and any content change
  during the read, still fails closed with `CORRUPT_RUNTIME_STATE`.
- Lint link resolution no longer reports a wikilink as ambiguous when the
  extra candidates are gitignored files (for example a compiled binary whose
  name shadows a page, such as `bin/env8oy` next to `wiki/projects/env8oy.md`).
  A new pure-Python `.gitignore` evaluator (`claude_obsidian/gitignore.py`)
  reads only `.gitignore` files inside the vault root — never
  `.git/info/exclude`, global excludes, or a `git` subprocess — keeping
  reports deterministic and process-free. Gitignored files remain valid link
  targets when they are the only candidate, so no new dead links are
  introduced; ambiguity among only-gitignored candidates is still reported.
  This unblocks `checkpoint` runs that previously failed `LINT_FAILED`
  whenever a build artifact existed.

## [2.1.1] - 2026-08-26

Legacy migration safety and clearer Windows and WSL support guidance.

### Added

- `docs/windows-wsl.md`: platform support matrix and WSL troubleshooting for
  native Windows users, covering Microsoft's diagnostic flow for unconfirmed
  `wsl --status` hangs, approval-hash environment binding,
  and filesystem identity requirements. Linked from the README, install
  guide, compound vault guide, and the wiki skill's transaction reference.

### Changed

- The `UNSUPPORTED_PLATFORM` refusal message now points to
  `docs/windows-wsl.md` for users whose WSL setup is itself misbehaving.
- Windows and WSL troubleshooting now routes unconfirmed hangs through
  Microsoft's diagnostic flow without asserting an unsupported cause.

### Fixed

- Legacy migration and adoption no longer fail when a manifest source key is a
  valid batch label rather than a file. Unresolved labels are preserved as
  unreviewed manual sources without inventing payload mappings or hashes.
  Apply now rejects a reviewed migration if a legacy locator's file state
  changes or becomes unsafe before the transaction writes.
- Migration and adoption keep read-only source observations separate from the
  1,024-write recovery limit, preserving valid legacy manifests with larger
  source sets.
- Git-backed release and checkpoint fixtures now ignore machine-wide hooks and
  commit-signing settings, keeping the hermetic suite offline and deterministic.

## [2.1.0] - 2026-07-31

Native Windows compatibility.

### Fixed

- Native Windows no longer crashes with `AttributeError: os.O_DIRECTORY` on
  every vault command. Read-only inspection and dry-runs (`transaction
  inspect`, `migrate`/`init`/`adopt`/`capture` previews) now work natively
  with real equivalent safety checks: path-based casefold-alias auditing,
  lstat-based vault identity, and symlink/junction rejection.
- File reads in the transaction core now force binary mode (`O_BINARY`), so
  CRLF content is hashed byte-exactly on Windows instead of producing false
  `CONTENT_HASH_MISMATCH`/`EXPECTED_HASH_MISMATCH` failures.
- CLI output is always UTF-8, fixing `UnicodeEncodeError` crashes when
  redirecting output containing non-ASCII titles on Windows (cp1252 consoles).
- Retrieval no longer returns zero results for vaults with CRLF line endings:
  the chunker, index, and retriever now hash page bodies byte-identically
  (previously `read_text` newline normalization made every chunk look stale).
- Under a held mutation lock, a vault whose on-disk name differs only by case
  from the spelling used on the command line is no longer misreported as its
  own portable alias on case-insensitive filesystems (APFS; the lock layer
  never runs on native Windows); the descriptor-pinned vault object is
  recognized as itself. Inspect-time auditing keeps the stricter shipped
  behavior, since an absent init root on a case-insensitive volume cannot
  distinguish itself from an alien sibling.

### Changed

- Vault mutation on hosts without directory-descriptor confinement (native
  Windows) is refused before any side effect with a new
  `UNSUPPORTED_PLATFORM` validation error (exit 2, previously a generic
  `LOCK_FAILED` exit 1 or a traceback), and `init --apply` no longer creates
  an abandoned empty vault directory on refused platforms.
- New transaction write destinations are validated against
  portable-filesystem rules on every platform: Windows-reserved device names
  (`CON`, `NUL`, ...), `:<>|?*"` characters, and trailing dots/spaces are
  rejected with `UNPORTABLE_WRITE_PATH` so an approved plan means the same
  thing everywhere. Reads, retrieval indexing, and journal recovery of
  pre-existing files with such names are intentionally unaffected.
- Degraded-mode path walks now reject Windows directory junctions and mount
  points in addition to symlinks.
- File permission bits feeding plan hashes are normalized to `0o644` on
  Windows, keeping inspect output deterministic.
- Added a `.gitattributes` that disables line-ending translation so checkouts
  hash identically on every platform.
- CI gained a `windows-smoke` job exercising the portable Python surface and
  the new Windows compatibility suite on `windows-latest`.
- Replaced the animated README hero with the selected static PNG cover while
  preserving the warm orbital style.

## [2.0.0] - 2026-07-30

Reliability and evidence refoundation.

### Added

- Standard-library `claude_obsidian` core with fail-closed vault selection,
  recoverable operation transactions, crash recovery, exact changed-path
  manifests, and explicit Git checkpoints.
- Deterministic Obsidian linting, product and capability contracts, portable
  package validation, source and claim ledgers, and additive legacy migration.
- Dry-run-first `init`, `adopt`, methodology configuration, source capture,
  extension setup, and public artifact build and audit commands.
- Offline-first content-addressed capture and durable queues. Image, PDF, and
  EPUB support is metadata-only unless a separately configured adapter is
  explicitly approved.
- Reproducible clean-Git ZIP builder with manifests, checksums, deterministic
  executable modes, and defenses for secrets, private paths, live-vault state,
  symlinks, traversal, collisions, unreviewed binaries, and hostile archives.
- Artifact-only marketplace generation: development source keeps a reviewed
  catalog template under `config/`; release build injects it only into the
  distribution-clean root and verifies that the promoted tree can rebuild.
- Deterministic templates and sample vault, Linux and macOS CI, root-isolation
  tests, concurrency and failure-injection coverage, and automatic test
  discovery.
- Adversarial regression coverage for symlink and parent-swap escapes, stale
  approvals, signed credential URLs, provenance violations, staged Git state,
  checkpoint interruption, and transaction finalization windows.

### Changed

- Rebuilt the README around the product promise, compounding loop, real vault
  examples, concise onboarding, trust architecture, and honest capability
  boundaries.
- Adopted the warm orbital cover system, added the selected metadata-stripped
  static PNG cover, preserved the Obsidian screenshots, and aligned the
  self-contained SVG architecture diagrams to the new style.
- All 15 skills now use canonical two-field Agent Skills frontmatter and one
  host-neutral operation contract.
- Parallel ingestion and research workers are draft-only. One orchestrator
  inspects and applies the complete knowledge operation.
- Query and lint are read-only. Persistence and repairs are separate reviewed
  operations.
- Claude hooks are bounded SessionStart and Stop adapters. Stop reports recovery
  state; SessionStart context injection requires the explicit
  `CLAUDE_OBSIDIAN_SESSION_CONTEXT=1` opt-in. Neither mutates knowledge or Git.
- Setup and installation helpers default to previews, use selected user vaults,
  avoid plugin-cache state, and preserve existing configuration.
- Portable installation creates directly discoverable per-skill links at each
  host's current skill root, and executable skills resolve product helpers by
  absolute installed paths rather than the user-vault working directory.
- Retrieval now removes stale chunks, invalidates derived indexes, deduplicates
  before top-K, confines paths, uses task-specific Nomic prefixes, and restores
  the complete BM25 result when reranking cannot be trusted. Query size and
  result counts are bounded; invalid limits and oversized queries fail with
  nonzero, actionable usage errors.
- CJK retrieval now normalizes Unicode input and indexes bounded character
  n-grams so Japanese, Chinese, Korean, Bopomofo, and mixed-width queries can
  overlap longer documents; legacy derived indexes fail closed with rebuild
  guidance.
- Optional semantic reranking defaults to the multilingual Nomic v2 MoE model,
  uses Ollama's current single-input embed API, supports explicit model
  selection with exact tag semantics, and retains deterministic BM25 order when
  the selected local model is unavailable.
- Public release scanning rejects recognizable personal email addresses while
  retaining only reserved example domains and GitHub-generated noreply
  identities for fixtures and provenance; SSH clone locators and numeric
  package-version specifiers are not misclassified as email addresses.
- Product source, user vaults, deterministic templates, and public artifacts
  are explicit separate roles.
- Distributable setup references now follow the same transaction, privacy,
  plugin-review, TLS, and evidence boundaries as the skills.
- Dry-run/apply workflows are bound to exact canonical, vault-specific plan
  hashes. Transaction targets use no-follow vault-relative writes and unlinks,
  reserve product/runtime namespaces, and enforce declared workflow scopes;
  provenance contracts are enforced during inspect, apply, lint, and checkpoint.
- Explicit checkpoints now construct and verify Git objects through a temporary
  index, update refs by compare-and-swap, and recover from a durable pending
  record without consuming unrelated staged or intent-to-add state. Content and
  executable modes must both match the transaction result.
- Capability readiness now distinguishes configured workflows from genuine
  behavioral verification; schema/self-checks cannot promote a capability.
- Provenance identities now collapse RFC-equivalent IPv6, IDN, Unicode/IRI,
  default-port, dot-segment, and percent-encoding URL spellings before source
  independence is counted; malformed/non-scalar forms fail closed.
- Zettelkasten routing now combines its UTC microsecond prefix with a UUIDv4
  nonce, preventing rapid or concurrent preview collisions without allocator
  writes. Legacy format metadata is normalized through reviewed mode changes,
  overlong UTF-8 components are hash-suffixed within the 255-byte portability
  floor, and existing timestamp-only filenames remain valid.

### Removed

- Duplicate command mirrors and generic PostToolUse or PostCompact behavior.
- Direct shared writes, automatic Git commits, and per-file locks from the
  supported mutation path.
- Unsupported comparative, performance, and capability claims from current
  product documentation.
- Root contributor-vault Obsidian snippets from the public artifact; the
  project-owned deterministic template snippet remains.

### Compatibility

- Existing vaults remain readable. Migration is additive, idempotent, and
  preserves the legacy raw manifest byte-for-byte.
- `scripts/wiki-lock.sh` remains a deprecated v1 compatibility helper only.
- Product tools never publish, push, tag, or mutate public collaboration state
  without owner approval.

## [1.9.2] - 2026-05-27

- Added bounded local prompt-cache statistics to explicitly approved
  contextual-prefix API calls.
- Hardened explicit path handling and expanded hermetic contextual-prefix tests.

## [1.9.1] - 2026-05-18

- Hardened legacy lock path confinement, transport probes, cache warnings, and
  remote Ollama consent.
- Added operator-facing single-tenant threat-model documentation.

## [1.9.0] - 2026-05-18

- Added the 10-stage OBSERVE, OBSERVE, LISTEN, THINK, CONNECT, CONNECT, FEEL,
  ACCEPT, CREATE, GROW reasoning skill.
- Added repository contribution, security, issue, pull-request, and CI
  foundations.

## [1.8.2] - 2026-05-18

- Preserved manual transport overrides and hardened mode routing, input
  sanitization, and local vault selection.
- Expanded verifier and retrieval tests.

## [1.8.0] - 2026-05-17

- Added optional Generic, LYT, PARA, and Zettelkasten methodology modes.
- Added deterministic path routing and non-destructive mode configuration.

## [1.7.2] - 2026-05-17

- Added Unicode-aware BM25 tokenization and retrieval failure hardening.
- Improved cache locking, progress reporting, and invalid-input diagnostics.

## [1.7.1] - 2026-05-17

- Made contextual-prefix egress explicit and added a read-only verifier role.
- Hardened transport JSON handling and legacy retrieval failure recovery.

## [1.7.0] - 2026-05-17

- Added optional contextual retrieval, BM25, local reranking, transport
  detection, and a legacy multi-writer compatibility layer.
- Added the `wiki-cli` and `wiki-retrieve` skills.

## [1.6.0] - 2026-04-24

- Added opt-in boundary-first autoresearch and its deterministic graph scorer.

## [1.5.1] - 2026-04-24

- Hardened vault path confinement and aligned DragonScale rollout metadata.

## [1.5.0] - 2026-04-24

- Added opt-in fold, deterministic-address, and semantic-tiling prototypes.
- Added the initial test harness and extension setup helpers.

## [1.4.3] - prior

- Earlier project history remains available in Git.
