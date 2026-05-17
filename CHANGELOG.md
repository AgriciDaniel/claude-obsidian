# Changelog

All notable changes to claude-obsidian. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [1.7.1] - 2026-05-17 (audit-driven patch)

Patch release closing the 1 BLOCKER + 6 HIGH findings from the v1.7.0 audit ([`docs/audits/v1.7.0-audit-2026-05-17.md`](docs/audits/v1.7.0-audit-2026-05-17.md)). All v1.7.0 features remain available; the changes are guard-rails and one new agent.

### Fixed

- **BLOCKER B1 — Data egress without consent** (`ca68bb6`). `scripts/contextual-prefix.py` now requires an explicit `--allow-egress` flag (default off) before selecting tier-1 (Anthropic API) or tier-2 (claude CLI subprocess). Without the flag, `pick_prefix_tier()` returns `"synthetic"` regardless of `ANTHROPIC_API_KEY` or `claude` binary presence. `bin/setup-retrieve.sh` adds a y/N consent prompt before any non-synthetic Stage 1 run. `skills/wiki-retrieve/SKILL.md` adds a Data Privacy callout (also closes H6). Mirror of the existing `scripts/tiling-check.py:351` `--allow-remote-ollama` precedent.
- **H1 — Stage 1 failure had no rollback path** (`4837d4f`). `bin/setup-retrieve.sh` now captures Stage 1's exit code, exits 5 on non-zero, and prints a 3-option recovery hint (incremental resume, full wipe, single-page re-process). Stage 2 only runs after Stage 1 success.
- **H2 — `make clean-test-state` didn't remove v1.7 artifacts** (`7e1f187`). Extended the target to remove `.vault-meta/chunks/`, `.vault-meta/bm25/`, `.vault-meta/locks/`, `.vault-meta/transport.json`, `.vault-meta/.wiki-lock.meta`, and the related `.tmp` files. The Makefile target now matches the v1.7 `.gitignore` set.
- **H3 — PostToolUse hook swallowed lock-check errors** (`7120970`). Restructured `hooks/hooks.json` to capture the wiki-lock script's exit code directly (not via a pipeline), defer the auto-commit on any non-zero rc, and only run `git add` after both the rc check and the non-empty-list check pass.
- **H4 — No verifier-agent pass at workstream gates** (`3ea443f`). Added `agents/verifier.md` — a read-only (`Read`/`Grep`/`Glob`/`Bash` only; no `Write`/`Edit`) pre-commit specialist that reads the staged diff, applies the /best-practices six-cut + agent kernel, and returns findings in four tiers (BLOCKER/HIGH/MEDIUM/LOW). CLAUDE.md "Pre-commit verifier (v1.7.1+)" section references it as the recommended pre-commit step.
- **H5 — `detect-transport.sh` JSON escaping was shell-only** (`722ac97`). Added a `json_escape()` helper that pipes through `python3 -c json.dumps`, applied to `CLI_VERSION` (both `obsidian-cli` and `obsidian`-binary paths). The heredoc now emits `${CLI_VERSION}` without surrounding quotes since the helper produces a pre-quoted JSON string. Defense in depth against pathological upstream version output (backslashes, tabs, newlines, control chars).
- **H6 — `skills/wiki-retrieve/SKILL.md` had no Data Privacy section** (bundled with B1 in `ca68bb6`). New section at the top of the skill body documents the two-layer egress guard (`--allow-egress` flag + setup-retrieve prompt) and points back to the `tiling-check.py` precedent.

### Added

- `agents/verifier.md` — pre-commit specialist; see H4 above.
- `scripts/baseline-v16.py` + `scripts/benchmark-runner.py` — audit instrumentation that ran the 50-query retrieval benchmark documented in `wiki/meta/retrieval-benchmark-v1.7.md`. Result: v1.7 top-1 54.0% vs v1.6 baseline 24.0% (+30pp); error reduction +39.5% vs the ≥30% gate. Future audits can re-run with `python3 scripts/benchmark-runner.py`.
- `docs/audits/v1.7.0-audit-2026-05-17.md` (481 lines) — the full audit report.
- `docs/audits/v1.7.1-fixes-plan.md` — the sequenced 6-commit roadmap this release executes.

### Changed

- Versions bumped to 1.7.1 in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (description fields refreshed to mention the verifier agent and the egress-consent guard).
- `CLAUDE.md` "Pre-commit verifier (v1.7.1+)" section added; "Concurrency (v1.7+)" section retained verbatim.

### Polish (post-fix self-audit refinements)

After the 7 v1.7.1 commits landed, a re-pass with `agents/verifier.md` against the slice surfaced 2 MEDIUM + 3 LOW polish items. All closed in one follow-up commit:

- `scripts/detect-transport.sh` — split `CLI_VERSION_RAW` (human log line) from `CLI_VERSION` (pre-quoted JSON for the heredoc). The JSON-escape fix from H5 made the log line `CLI: obsidian-cli ("1.12.0")` carry visible quotes; the split keeps both paths clean.
- `agents/verifier.md` — converted `tools:` from CSV to YAML list. Both forms are valid per Anthropic's spec; the list form is more explicit.
- `bin/setup-retrieve.sh` — refreshed the header docstring (lines 13-26) to mention `--allow-egress` and the consent gate. Inline comments at line 121 were already correct; the file-top doc was the stale one.
- `scripts/contextual-prefix.py` — docstring on `generate_prefix()` explaining the deliberate asymmetric fallback (api→cli→synthetic, but cli→synthetic only — climbing from cli to api would silently spend money the user did not authorize).
- `hooks/hooks.json` — breadcrumb log to `.vault-meta/hook.log` on the rare non-zero `LOCK_RC` defer path. Verified with concurrency (10 parallel hook fires → 10 atomic lines, no interleaving; line length < `PIPE_BUF`), no format-string injection (printf uses literal format with %s placeholders), filesystem-failure edge cases preserve `exit 0` (defer behavior intact).

### Migration notes

- v1.6 vaults: no action needed. The new components are opt-in or read-only.
- v1.7.0 adopters who provisioned `bin/setup-retrieve.sh` and had `ANTHROPIC_API_KEY` set: the next `bin/setup-retrieve.sh` run will prompt for consent before proceeding with the non-synthetic tier. Decline to keep all data on-machine (tier-3 synthetic), accept to preserve the prior behavior. Existing chunks/ data is unaffected either way.
- Test suite: `make test` continues to run 7 hermetic suites (~1162 assertions). Zero ollama, zero network dependency.

## [1.7.0] - 2026-05-17 (Compound Vault refoundation)

The v1.7 line, codenamed **Compound Vault**, refoundations the plugin around four pillars from the May 2026 gap analysis: substrate alignment with `kepano/obsidian-skills`, Obsidian-CLI-native transport, contextual + hybrid retrieval, and safe multi-writer ingest. v1.6 vaults that never install the new opt-in components see no behavior change. Full design rationale in `docs/compound-vault-guide.md`.

### Added

- **§3.2 Default transport** — `skills/wiki-cli/SKILL.md` (recipe reference for Obsidian CLI), `scripts/detect-transport.sh` (writes `.vault-meta/transport.json` snapshot; auto-stale at 7d), `wiki/references/transport-fallback.md` (canonical decision tree). 5 transport-aware skills (wiki-ingest, wiki-query, save, autoresearch, wiki-lint) gained "## Transport (v1.7+)" sections.
- **§3.3 Hybrid retrieval pipeline (wiki-retrieve, opt-in)** — implements Anthropic's Sept 2024 Contextual Retrieval pattern as agent-skill plumbing. 4 new scripts: `scripts/contextual-prefix.py` (3-tier auto: Anthropic API → claude CLI subprocess → synthetic), `scripts/bm25-index.py` (Okapi BM25, k1=1.5 b=0.75, pure stdlib, flock-guarded), `scripts/rerank.py` (cosine on nomic-embed-text via ollama, embed-cache), `scripts/retrieve.py` (orchestrator: BM25 top-20 → rerank top-5 → page dedupe). `bin/setup-retrieve.sh` opt-in bootstrap. `skills/wiki-retrieve/SKILL.md` documents the architecture and cost ceiling (~$12/1000 docs per Anthropic). Wired into `skills/wiki-query/SKILL.md` via "## Retrieval (v1.7+)" section with graceful exit-10 fallback to the v1.6 hot→index→drill read order.
- **§3.4 Multi-writer safety (wiki-lock, core)** — `scripts/wiki-lock.sh` per-file advisory locking. Age-based staleness (default `STALE_AFTER_SEC=60`), cross-process release allowed by design. 4 skills (wiki-ingest, wiki-fold, save, autoresearch) gained "## Concurrency (v1.7+)" sections with concrete acquire/release recipes. The latent corruption bug from v1.6 — documented but unenforced in `skills/wiki-ingest/SKILL.md:259-264` — is now closed.
- **New skills (2)**: `wiki-cli` (§3.2) and `wiki-retrieve` (§3.3). Total skill count is now 13.
- **New scripts (6)**: `detect-transport.sh`, `contextual-prefix.py`, `bm25-index.py`, `rerank.py`, `retrieve.py`, `wiki-lock.sh`.
- **New tests (4)**: `tests/test_bm25_index.py` (~30 hermetic assertions including BM25 monotonicity and IDF positivity), `tests/test_retrieve.py` (22 hermetic assertions including end-to-end subprocess test), `tests/test_wiki_lock.sh` (14 hermetic assertions including age-based stale reap), `tests/test_concurrent_write.sh` (6 hermetic assertions; the critical multi-writer correctness gate — 10 parallel workers, no losses, no garbled lines). `make test` now runs 7 suites with zero network and zero ollama dependency.
- **New docs**: `docs/compound-vault-guide.md` (omnibus v1.7 guide), `wiki/references/transport-fallback.md` (transport decision tree).
- **Makefile targets**: `test-bm25`, `test-retrieve`, `test-lock`, `test-concurrent`, `setup-retrieve`.

### Changed

- **§3.1 Substrate hard-prefer on `kepano/obsidian-skills`** — `skills/obsidian-markdown/SKILL.md`, `skills/obsidian-bases/SKILL.md`, and `skills/canvas/SKILL.md` upgraded from soft-defer ("if kepano installed, prefer it") to hard-prefer ("this is a fallback; prefer kepano"). Architectural behavior unchanged; signal sharpened. `skills/defuddle/SKILL.md` documented as canonical (kepano does not ship a defuddle skill). `.claude-plugin/marketplace.json` declares `recommendedCompanions: [kepano/obsidian-skills]` with install hint.
- **`hooks/hooks.json` PostToolUse** — added a lock-in-flight check before `git add`. When `bash scripts/wiki-lock.sh list` returns non-zero count, the auto-commit defers. Prevents torn commits during multi-agent ingest. Falls through gracefully if `wiki-lock.sh` is absent.
- **`agents/wiki-ingest.md`** — rewrote the "Sub-agents MUST NOT" section. The prohibition on calling `allocate-address.sh` from sub-agents is preserved (counter monotonicity). A NEW rule is added: sub-agents MAY now write pages, but MUST acquire locks first.
- **Versions** synced to 1.7.0 across `plugin.json` and `marketplace.json`.

### Migration notes

- v1.6 vaults need no action. The new components are opt-in (`bash bin/setup-retrieve.sh` for hybrid retrieval) or universally beneficial (wiki-lock is core; no setup needed). The plugin remains MIT-licensed; no paid tier introduced.
- To install the recommended companion: `claude plugin marketplace add kepano/obsidian-skills`. Existing local fallbacks remain functional without it.
- Estimated upgrade time: 5 minutes (substrate auto-detected; transport auto-detected on first session; retrieval requires explicit `bash bin/setup-retrieve.sh`).

### Out of scope for v1.7 (deferred to v1.8+)

- Methodology modes (LYT / PARA / Zettelkasten / Generic via `wiki-mode` skill) — planned for v1.8.
- NotebookLM-class derivative outputs (audio, quiz, flashcards, study guide via `wiki-derive`) — planned for v1.9 or v2.0.
- Multimodal ingest adapters (YouTube, PDF, EPUB, image OCR via `wiki-ingest-multimodal`) — planned for v1.9.
- Periodic review artifacts (`wiki-review`) — planned for v1.8.

## [1.6.0] - 2026-04-24

### Added (DragonScale Mechanism 4, opt-in)

- **Boundary-first autoresearch**: `scripts/boundary-score.py` computes `(out_degree - in_degree) * recency_weight` across the wikilink graph and emits top-K frontier pages. `/autoresearch` invoked without a topic now offers the top-5 frontier pages as research candidates when the vault has adopted DragonScale.
- `tests/test_boundary_score.py` — 35 unit tests covering frontmatter parsing, recency weight, wikilink extraction (with code-block guard), graph construction, scoring, CLI interface.
- `make test-boundary` target + integration into `make test`.

### Changed

- `skills/autoresearch/SKILL.md` — new Topic Selection section with three paths: explicit (A), boundary-first (B, opt-in), user-ask (C, default without DragonScale).
- `commands/autoresearch.md` — no-topic usage documented for both modes.
- `wiki/concepts/DragonScale Memory.md` — Mechanism 4 flipped from NOT IMPLEMENTED to shipped; exact scoring formula and "what is NOT included" callout added. Version bumped to v0.4.
- Version synced to 1.6.0 across plugin.json and marketplace.json.

## [1.5.1] - 2026-04-24 (Phase 3.6 hardening)

### Fixed

- `scripts/tiling-check.py`: `--report PATH` now resolved against VAULT_ROOT and rejected if it escapes (security: prevents hostile or accidental writes outside the vault).
- `.vault-meta/legacy-pages.txt`: rollout baseline corrected from 2026-04-24 to 2026-04-23 (matches earliest addressed page in the seed vault).
- `AGENTS.md`: wiki-fold listed in the skills table; stale claim that "all skills use only name/description" narrowed to newer skills (older skills still carry allowed-tools for Claude Code compatibility).
- `skills/wiki-ingest/SKILL.md`: resolves the internal contradiction between "immutable .raw/" and "maintain .raw/.manifest.json" — user-dropped source documents remain immutable; only the manifest is wiki-ingest-maintained.
- `docs/install-guide.md`: version 1.2.0 -> 1.5.0 with a DragonScale optional-install callout.

## [1.5.0] - 2026-04-24

### Added (DragonScale Memory extension, opt-in)

- **Mechanism 1 — Fold operator** (`skills/wiki-fold/`): extractive, structurally-idempotent rollups of `wiki/log.md` entries into per-batch meta-pages under `wiki/folds/`. Dry-run via stdout by default (does not trigger PostToolUse auto-commit hook); commit mode explicit.
- **Mechanism 2 — Deterministic page addresses** (opt-in): `scripts/allocate-address.sh` flock-guarded atomic allocator; new `address: c-NNNNNN` frontmatter convention; re-ingest idempotency via `.raw/.manifest.json address_map`. `wiki-ingest` and `wiki-lint` skills feature-detect DragonScale setup.
- **Mechanism 3 — Semantic tiling lint** (opt-in): `scripts/tiling-check.py` uses local `nomic-embed-text` via ollama to flag candidate duplicate pages by cosine similarity. Banded thresholds (error/review/pass) documented as conservative seeds with manual calibration procedure.
- `wiki/concepts/DragonScale Memory.md` — full design spec (v0.3) with four mechanisms, scope boundary, and primary-source citations.
- `bin/setup-dragonscale.sh` — idempotent installer that provisions `.vault-meta/` counter, thresholds, and legacy-pages manifest.
- `tests/` — shell + python test suite for the allocator and tiling-check. Run via `make test`.
- `Makefile` — developer targets (`test`, `setup-dragonscale`, `clean-test-state`).

### Changed

- `hooks/hooks.json` PostToolUse now stages `.vault-meta/` in addition to `wiki/` and `.raw/` so DragonScale runtime state is captured by the auto-commit hook.
- `skills/wiki-ingest/SKILL.md` and `skills/wiki-lint/SKILL.md` gained opt-in DragonScale sections behind feature-detection guards; original behavior unchanged for vaults that have not run `setup-dragonscale.sh`.
- `agents/wiki-ingest.md` explicitly forbids parallel sub-agents from calling the allocator (single-writer rule for address assignment).
- `agents/wiki-lint.md` extended to describe Address Validation and Semantic Tiling checks.
- Stale `allowed-tools` frontmatter removed from `wiki-ingest` and `wiki-lint` SKILL.md (kepano convention: only `name` and `description`).
- Version strings synced across `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and documentation.

### Security

- `scripts/tiling-check.py` locks `OLLAMA_URL` to localhost by default. Remote endpoints require `--allow-remote-ollama`. Symlinks and vault-root escapes are rejected before any read.

### Not in this release

- **Mechanism 4 — Boundary-first autoresearch**: documented in the spec as a future proposal; no code shipped. `skills/autoresearch/SKILL.md` unchanged.

## [1.4.3] - prior

Previous state. See git log for details.
