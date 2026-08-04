# Changelog

Notable changes to claude-obsidian are recorded here using
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) categories and
[Semantic Versioning](https://semver.org/). Git history retains the detailed
implementation record for older releases.

## [Unreleased]

### Added

- `docs/windows-wsl.md`: platform support matrix and WSL troubleshooting for
  native Windows users, covering the virtualization-conflict hang class
  (`wsl --status` hanging after install), approval-hash environment binding,
  and filesystem identity requirements. Linked from the README, install
  guide, compound vault guide, and the wiki skill's transaction reference.
- Stop hook: an advisory-only warning when `wiki/log.md` has accumulated at
  or above 85% of the wiki-fold batch size (`2**k` entries, default `k=4`)
  worth of entries since the last fold marker, so a growing log doesn't go
  unnoticed between sessions. Configurable via
  `CLAUDE_OBSIDIAN_FOLD_BATCH_EXPONENT`. It never runs wiki-fold or mutates
  the vault itself, since folding stays human-invoked per
  `skills/wiki-fold/SKILL.md`.

### Changed

- The `UNSUPPORTED_PLATFORM` refusal message now points to
  `docs/windows-wsl.md` for users whose WSL setup is itself misbehaving.

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
