---
type: meta
title: "Hot Cache"
updated: 2026-07-20T00:00:00
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[Wiki Map]]"
  - "[[getting-started]]"
  - "[[DragonScale Memory]]"
---

# Recent Context

Navigation: [[index]] | [[log]] | [[overview]]

## Last Updated

2026-07-20: **Hot cache refreshed after 6 releases of drift (v1.7.1 → v1.9.2) + plugin marketplace install**. This cache had gone stale: it still described the local-only `v1.7.0-compound-vault` branch pre-push, but `git log` showed 5 more releases had shipped and pushed since. Catching up from CHANGELOG.md: **v1.7.2** (Unicode-aware BM25 tokenizer, defensive-input fixes, dead-code prune per kernel). **v1.8.0** (methodology modes — LYT/PARA/Zettelkasten/Generic via `scripts/wiki-mode.py`, closes compass priority gap 5; `.vault-meta/mode.json`, currently absent here so this vault runs generic/v1.7 default). **v1.8.2** (pre-push audit closure: `manual_override` in `detect-transport.sh` actually honored, `wiki-ingest` agent got `Bash` tool + mode awareness, `autoresearch` got web-egress hygiene (URL validation, content sanitization, cost/failure-mode docs), `save` got explicit destination-root routing). **v1.9.0** (10-principle thinking framework shipped as skill #15 `/think`, every other SKILL.md got a "How to think" appendix; first-public-release repo hygiene: CONTRIBUTING/CODE_OF_CONDUCT/SECURITY/CI workflow/issue templates). **v1.9.1** (6 HIGH/MEDIUM hardening: SessionStart now runs `wiki-lock.sh clear-stale` on every session start, PostToolUse auto-commit gets a `.vault-meta/auto-commit.disabled` opt-out, `wiki-lock.sh` canonicalizes symlinks before path-validation to close an escape vector, `setup-retrieve.sh` refuses non-localhost `OLLAMA_URL` without `--allow-remote-ollama`, new `SECURITY.md` single-tenant threat model). **v1.9.2** (prompt-cache hardening in `scripts/contextual-prefix.py`: `cache_control` only attached above the ~16KB Haiku-4.5 cacheable floor via new `cache_control_for()`, cache hit/write telemetry logged, explicit missing/out-of-vault page paths now fail with clean exit codes instead of silent-0 or raw traceback; new `test_contextual_prefix.py`, `make test` now **9** hermetic suites / ~1240 assertions). Repo was then promoted to **public canonical** at `github.com/AgriciDaniel/claude-obsidian` (`00213b7`) plus a social-preview-card commit (`cb93ff6`, `2026-05-28`) — no commits since. **This session**: user asked why `commands/wiki.md` wasn't runnable; root cause was the plugin never being registered (no `.claude/commands/`, no `commands` key in the manifest, and the plugin itself wasn't installed — only cloned as a vault via `bin/setup-vault.sh`, which is vault-config only and doesn't touch Claude Code's skill/command registry). Fixed by running `claude plugin marketplace add AgriciDaniel/claude-obsidian` then `claude plugin install claude-obsidian@agricidaniel-claude-obsidian` (user scope). User restarted Claude Code; `claude-obsidian:wiki` and all 15 skills now resolve via the `Skill` tool. **Deferred items still open** (none of v1.9.2's changes touched these; carried forward from the v1.9.1 CHANGELOG "Deferred to v1.9.2" list since nothing since has closed them): Data M2 (embed-cache + chunk-orphan GC subcommand for `bm25-index.py`/`contextual-prefix.py`), W1 (12 files' worth of `wiki/meta/` release-session notes need relocation + wikilink graph update, bundle with References M1+M2's 17 dead wikilink targets), Security S1 (pin Excalidraw release-asset checksum in `setup-vault.sh`'s `curl` download).

2026-05-17 (very late, post-polish): **v1.7.1 patch + polish slice shipped locally** (branch `v1.7.0-compound-vault`, still NOT pushed). All 1 BLOCKER + 6 HIGH findings closed; then verifier agent re-pass surfaced 2 MEDIUM + 3 LOW polish items, all closed in `c2d7575`. Final verifier verdict: 0/0/0/0 SHIP. Score: 100/100 on the v1.7.1 patch dimensions (plan fidelity, behavioral correctness, test health, internal consistency, constraint honor, defect introduction, kernel application). 8 commits landed in this resumption session: `ca68bb6` (Fix 1+6 BLOCKER B1 + H6 — contextual-prefix `--allow-egress` flag default-off + `bin/setup-retrieve.sh` consent prompt + `skills/wiki-retrieve/SKILL.md` Data Privacy callout, mirror of `tiling-check.py:351` `--allow-remote-ollama` precedent), `4837d4f` (Fix 2 H1 — setup-retrieve exit 5 + 3-option recovery hint on Stage 1 failure), `7e1f187` (Fix 3 H2 — `make clean-test-state` extended to v1.7 artifacts), `7120970` (Fix 4 H3 — PostToolUse hook captures LOCK_RC directly, not via pipeline; defers commit on script error OR locks held), `722ac97` (Fix 5 H5 — `detect-transport.sh` `json_escape()` helper via `python3 json.dumps`), `3ea443f` (Fix 7 H4 — new `agents/verifier.md` read-only pre-commit specialist + CLAUDE.md reference), and the cross-cutting closeout `822c80a` (version bump 1.7.0 → 1.7.1, CHANGELOG entry, audit doc updated with §10.2 SHAs + v1.7.1 closeout block, audit benchmark scripts promoted to tracked files). `make test` ran 7/7 green after every fix. End-to-end verifications: `python3 scripts/contextual-prefix.py --peek` returns `tier=synthetic` even with `ANTHROPIC_API_KEY` set (default-deny works); `--allow-egress` correctly flips it; `echo "" | bash bin/setup-retrieve.sh` aborts at the consent prompt; `bash scripts/wiki-lock.sh acquire ...` then hook trigger correctly defers auto-commit. **Next step**: ask user whether to push + tag `v1.7.1`. Do NOT push without explicit go.

2026-05-17 (late): **v1.7.0 full audit complete; v1.7.1 fixes plan ready**. Branch `v1.7.0-compound-vault` still local-only (no push, no tag). The audit was demanded as "THROUGH and FULL on AUDIT following /best-practices" with EVERYTHING scope. Result: **31 findings (1 BLOCKER + 6 HIGH + 14 MEDIUM + 10 LOW)** in `docs/audits/v1.7.0-audit-2026-05-17.md` (481 lines). **BLOCKER**: `scripts/contextual-prefix.py:252-258` data-egress consent gap — `pick_prefix_tier()` silently sends wiki page bodies to Anthropic API whenever `ANTHROPIC_API_KEY` is set; mirror `scripts/tiling-check.py:351-352` `--allow-remote-ollama` precedent to fix (~1h). **Retrieval benchmark PASS**: 50 queries × 2 pipelines via `scripts/benchmark-runner.py`; v1.7 top-1 54.0% vs v1.6 baseline 24.0% (+30pp); error-reduction +39.5% vs ≥30% gate. Per-category breakdown in audit §6.2. **Competitor recheck (24h after compass May 16)**: kepano +1.1k★ to 31.6k, Copilot CLI integration issue still stale 3mo (genuine moat for us), NotebookLM May 2026 shipped Video Overviews + 4-tile Studio (widens derivative-outputs gap — filed M13 for v2.0 derive spec). **7-axis #1 verdict**: YES on 4 axes (compounding wiki, multi-writer safety, retrieval architecture free-tier, license openness), TIE on methodology (v1.8 closes), NO on GUI ergonomics (v2.5+) + derivative outputs (v2.0). Honest answer: #1 today on power-user-control axes, not in mainstream adoption without v2.0+v2.5.

**For post-compact resumption**: read `docs/audits/v1.7.1-fixes-plan.md` (this is your roadmap — 6 commits, ~2.5h, sequenced top-to-bottom with file paths + exact edits + verification steps + commit messages per fix). The plan starts with the BLOCKER (Fix 1) + Data Privacy callout (Fix 6) bundled. Working tree state on resume: 4 untracked files (audit doc, fixes plan, `scripts/baseline-v16.py`, `scripts/benchmark-runner.py`); `96a5505` wiki auto-commit landed the benchmark corpus at `wiki/meta/retrieval-benchmark-v1.7.md`; `make test` is 7/7 green; `bash bin/setup-retrieve.sh --no-llm` is provisioned (chunks/, bm25/, embed-cache.json exist — gitignored). User wants to "proceed" with the fixes after compact; do NOT push or tag without explicit go.

**Session record** (full prose, ~600 lines) in personal vault: `~/Documents/Obsidian Vault/sessions/2026-05-17 claude-obsidian v1.7 audit + fixes plan.md`. Ingest-log entry prepended at top of `~/Documents/Obsidian Vault/log/ingest-log.md` per global save convention.

2026-05-17: **v1.7.0 "Compound Vault" refoundation shipped locally** (branch `v1.7.0-compound-vault`, NOT pushed). Four workstreams committed as 4 separate feat commits: §3.1 substrate hard-prefer on `kepano/obsidian-skills` (9c8e510), §3.2 default transport with new `wiki-cli` skill + `scripts/detect-transport.sh` (6c7671e), §3.3 hybrid retrieval pipeline as opt-in `wiki-retrieve` skill with 4 new scripts + 2 hermetic test suites (45a5bd3), §3.4 multi-writer safety closing the latent corruption bug from v1.6 via `scripts/wiki-lock.sh` (66c11f9). Cross-cutting commit pending: version bump 1.6.0→1.7.0, README/CLAUDE.md updates, CHANGELOG entry, new `docs/compound-vault-guide.md` omnibus, this hot.md update. `make test` runs 7 suites green (was 3) — zero ollama / network dependency preserved. Plan file at `~/.claude/plans/read-in-full-the-hidden-sun.md`. User-paused at "full on review on all work done"; no push or tag until explicit go.

2026-04-24 (late night): v1.6.0 public release notes shipped. `docs/releases/v1.6.0.md` (Karpathy-style, 346 lines) establishes the release-notes convention. Three original SVGs at `wiki/meta/dragonscale-{mechanism-overview,6-test-flow,frontier-graph}.svg` carry the visual load; Wikipedia dragon curve referenced by text link only (no binary vendoring). R4 codex verifier ACCEPT WITH FIXES, 3 wording fixes applied. User runs `gh release create v1.6.0 --notes-file docs/releases/v1.6.0.md` when ready. Commits `85515bb` (docs), plus wiki/meta/ auto-commits for SVGs.

2026-04-24 (night): DragonScale end-to-end validation pass. Six-test menu run via Teams orchestration (codex gpt-5.4 for M1 dry-run, M1 commit, M4 autoresearch; chair for ollama pull, M2 allocate, M3 full tiling). All six green. First real fold committed (`wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md`, 115 lines, 8 children). First real tiling report at `wiki/meta/tiling-report-2026-04-24.md` (0 errors, 15 review pairs). M2 counter advanced 2 to 3, `c-000002` reserved-unassigned. M4 autoresearch filed 3 new concept pages (`Persistent Wiki Artifact`, `Source-First Synthesis`, `Query-Time Retrieval`) extending `[[How does the LLM Wiki pattern work?]]` with Karpathy gist + RAG + MemGPT + Obsidian docs as sources. v1.6.0 validated.

2026-04-24 (evening): v1.6.0 closeout via Teams approach (chair-led, codex gpt-5.4 for sub-agents). 2 explorers (closeout gaps + doc surface). 6 bounded writes (non-overlapping scope): `docs/dragonscale-guide.md` (new, 563 lines), `wiki/meta/2026-04-24-v1.6.0-release-session.md` (new, 346 lines), `wiki/meta/boundary-frontier-2026-04-24.md` (first real M4 run artifact, new), `docs/install-guide.md` (1.5.0 to 1.6.0 + M4 callout + flat-extractive correction), `README.md` (parenthetical + guide link), `wiki/hot.md` (drift fixes). 1 adversarial verifier returned ACCEPT WITH FIXES; all 11 fixes applied in place. Docs commit `eb1562f`. `make test` green (74+ assertions). Still no git tags for v1.5.0 / v1.5.1 / v1.6.0. User requested gpt-5.5; API rejects it on this codex CLI; gpt-5.4 used throughout.

2026-04-24 (late): Phase 4 shipped. Mechanism 4 (boundary-first autoresearch) implemented as `scripts/boundary-score.py` with expanded test coverage. `/autoresearch` without a topic now offers frontier candidates (opt-in, agenda-control labeled). Cross-file status updated. Version bumped to 1.6.0 in `plugin.json` + `marketplace.json`; no git tag created locally (only pre-DragonScale tags `v1.1` - `v1.4.3` exist).

2026-04-24 (afternoon): Phase 3.6 hardening, five surgical fixes (tiling --report path confinement, rollout baseline, AGENTS.md consistency, wiki-ingest .raw contradiction, install-guide version). v1.5.1.

2026-04-24 (morning): Phase 3.5 hardening pass. Cross-phase audit resolved 10 hold-ship items. At that point Mechanism 4 was marked NOT IMPLEMENTED (later reversed in Phase 4 the same day). `bin/setup-dragonscale.sh` + tests + Makefile added, CHANGELOG created, versions synced to 1.5.0.

2026-04-23 (3): Phase 3 complete. Semantic tiling lint shipped as opt-in. `scripts/tiling-check.py` with flock-guarded atomic cache, localhost-locked OLLAMA_URL default, symlink rejection, model-drift invalidation, and banded thresholds (error>=0.90, review>=0.80, conservative seeds). 4 codex review rounds, 10/10 accept.

2026-04-23 (2): Phase 2 complete. Deterministic page addresses MVP via `scripts/allocate-address.sh` (flock-guarded, recovers counter from max observed). New frontmatter `address: c-NNNNNN`. `wiki-ingest` and `wiki-lint` updated with opt-in Address Assignment and Validation sections. 3 codex rounds, 8/8 accept.

2026-04-23 (1): Phase 0-1 complete. DragonScale Memory spec (`wiki/concepts/DragonScale Memory.md` v0.3) plus `skills/wiki-fold/` for Mechanism 1 (log rollups, dry-run verified). Survived multi-round codex review.

## Plugin State

- **Version**: 1.9.2, public canonical release (`plugin.json` + `marketplace.json` synced; pushed and promoted, `github.com/AgriciDaniel/claude-obsidian`)
- **Install ID (this machine)**: `claude-obsidian@agricidaniel-claude-obsidian`, user scope, added 2026-07-20 via `claude plugin marketplace add` + `claude plugin install`. Earlier hot-cache entries below reference `claude-obsidian@ai-marketing-hub-claude-obsidian` from a different operator/machine/context — do not assume they're the same registry entry.
- **Skills**: 15 — `wiki`, `wiki-ingest`, `wiki-query`, `wiki-lint`, `wiki-fold`, `wiki-mode` (v1.8), `wiki-cli` (v1.7), `wiki-retrieve` (v1.7, opt-in), `save`, `autoresearch`, `canvas`, `defuddle`, `obsidian-bases`, `obsidian-markdown`, `think` (v1.9, skill #15). Every skill now carries a "How to think" 10-principle appendix.
- **Scripts (v1.6, DragonScale, opt-in)**: `scripts/allocate-address.sh`, `scripts/tiling-check.py`, `scripts/boundary-score.py`
- **Scripts (v1.7+)**: `scripts/detect-transport.sh` (v1.8.2: honors `manual_override`), `scripts/contextual-prefix.py` (v1.9.1: egress consent gate; v1.9.2: `cache_control_for()` Haiku-floor caching + telemetry + clean exit codes), `scripts/bm25-index.py` (v1.7.2: Unicode-aware tokenizer), `scripts/rerank.py` (v1.9.1: lock-contention warnings route to `hook.log`), `scripts/retrieve.py`, `scripts/wiki-lock.sh` (v1.9.1: symlink canonicalization before path-validation), `scripts/wiki-mode.py` (v1.8, methodology routing)
- **Setup**: `bin/setup-vault.sh`, `bin/setup-dragonscale.sh` (opt-in), `bin/setup-multi-agent.sh`, `bin/setup-retrieve.sh` (opt-in; v1.9.1: refuses non-localhost `OLLAMA_URL` without `--allow-remote-ollama`), `bin/setup-mode.sh` (v1.8, methodology mode)
- **Tests**: `make test` runs **9** hermetic suites (~1240 assertions): `test_allocate_address.sh`, `test_tiling_check.py`, `test_boundary_score.py`, `test_bm25_index.py`, `test_retrieve.py`, `test_wiki_lock.sh`, `test_concurrent_write.sh`, `test_wiki_mode.py` (v1.8), `test_contextual_prefix.py` (v1.9.2). Zero ollama and zero network dependency for all core tests; CI (`.github/workflows/test.yml`, v1.9.0) runs the same suite plus SKILL.md/agent-manifest/plugin-manifest validation.
- **Hooks**: SessionStart (v1.9.1: also runs `wiki-lock.sh clear-stale --max-age 3600`), PostCompact, PostToolUse (stages `wiki/ .raw/ .vault-meta/`; defers `git add` while wiki-lock locks are held; v1.9.1: exits early if `.vault-meta/auto-commit.disabled` exists), Stop
- **Methodology mode**: no `.vault-meta/mode.json` present in this vault → defaults to `generic` (v1.7 behavior, no organizational opinion imposed)

## DragonScale Mechanisms

1. **Fold operator** (Mechanism 1): `skills/wiki-fold/`, dry-run verified AND first real fold committed at `wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md`.
2. **Deterministic addresses** (Mechanism 2): shipped and exercised; vault counter at 3. `c-000001` on DragonScale Memory.md. `c-000002` reserved-unassigned from validation pass (gap acceptable per spec).
3. **Semantic tiling lint** (Mechanism 3): shipped and activated. `nomic-embed-text` pulled; first tiling report at `wiki/meta/tiling-report-2026-04-24.md` (0 errors, 15 review-band pairs).
4. **Boundary-first autoresearch** (Mechanism 4): shipped (Phase 4, opt-in). `scripts/boundary-score.py` + `tests/test_boundary_score.py`. `/autoresearch` without a topic surfaces top-5 frontier pages as candidates; user picks, overrides, or declines. Explicitly labeled "agenda control" in both spec and skill.

## Key Lessons from This Release Cycle

1. Cross-phase audits are essential. Individual phase reviews miss drift between phases.
2. Opt-in feature detection (`[ -x script ] && [ -f state ]`) preserves default plugin behavior for adopters and non-adopters alike.
3. PostToolUse hook matcher is `Write|Edit`, so Bash writes don't fire it. Scripts that mutate tracked state must be Bash-only to avoid side-effect commits.
4. Seed-vault self-consistency matters: if the spec says post-rollout pages need addresses, the concept page itself has to have one.
5. Codex adversarial review rounds stop when the punch list is empty, not when the author feels done.

## Style Preferences

- No em dashes (U+2014) or `--` as punctuation. Periods, commas, colons, or parentheses. Hyphens in compound words are fine.
- Short and direct responses. No trailing summaries.
- Parallel tool calls when independent.

## Active Threads

- DragonScale Mechanism 4 shipped in Phase 4 as an opt-in Topic Selection mode in `skills/autoresearch/`. All four DragonScale mechanisms are now shipped and feature-gated.
- v1.9.2 is pushed and public-canonical; nothing local-only or unpushed as of this refresh.
- Deferred, still open: Data M2 (embed-cache/chunk-orphan GC for `bm25-index.py`/`contextual-prefix.py`), W1 (12-file `wiki/meta/` release-note relocation + wikilink graph fix, bundle with References M1+M2's 17 dead wikilink targets), Security S1 (pin Excalidraw release checksum in `setup-vault.sh`).
- Only 1 source in `.raw/` (`claude-obsidian-ecosystem-research.md`) — most of this vault's content was filed directly as dev/release documentation rather than via `/wiki-ingest`, which is expected for a vault that dogfoods its own plugin.
- No Obsidian MCP server configured (`claude mcp list` shows only Google Drive/Gmail/Calendar connectors); filesystem transport works fine, MCP is optional.
- `git status` shows several uncommitted `.obsidian/*` files (app.json, appearance.json, graph.json, community-plugins.json, core-plugins.json, workspace.json, a few plugin data/manifest files) plus untracked `.obsidian/plugins/{dataview,obsidian-git,obsidian-memos,templater-obsidian}/` and modified `CLAUDE.md`/`CODE_OF_CONDUCT.md` — routine local Obsidian usage state, not flagged as a problem, just noted so a future session doesn't mistake it for in-progress work to finish.

## Repo Locations

- Working: this vault's actual path is user-specific (OneDrive-synced); don't assume `~/Desktop/claude-obsidian/` from older entries above — check `git rev-parse --show-toplevel` if it matters.
- Public canonical: https://github.com/AgriciDaniel/claude-obsidian (flipped from mirror to canonical at v1.9.2's `00213b7`)
- Pro early-access mirror: https://github.com/AI-Marketing-Hub/claude-obsidian (same MIT core, earlier access to in-development features)
