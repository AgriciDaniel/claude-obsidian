---
type: meta
title: "Hot Cache"
updated: 2026-04-24T12:40:00
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

- **Version**: 1.6.0 (Phase 4 shipped; plugin.json + marketplace.json synced; 1.5.1 was the Phase 3.6 hardening point release)
- **Install ID**: `claude-obsidian@claude-obsidian-marketplace`
- **Skills**: 11 (wiki, wiki-ingest, wiki-query, wiki-lint, wiki-fold, save, autoresearch, canvas, defuddle, obsidian-bases, obsidian-markdown)
- **Scripts**: `scripts/allocate-address.sh`, `scripts/tiling-check.py`, `scripts/boundary-score.py` (all opt-in; feature-detected by skills)
- **Setup**: `bin/setup-vault.sh` (base vault), `bin/setup-dragonscale.sh` (opt-in DragonScale), `bin/setup-multi-agent.sh` (multi-agent bootstrap)
- **Tests**: `make test` runs `tests/test_allocate_address.sh`, `tests/test_tiling_check.py`, `tests/test_boundary_score.py`. Zero ollama dependency for core tests.
- **Hooks**: 4 (SessionStart, PostCompact, PostToolUse [stages wiki/, .raw/, .vault-meta/], Stop)

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
- v1.6.0 not yet pushed to GitHub (local commits only, no git tag created). User controls push and tag timing.
- CLAUDE.md has one pre-existing uncommitted change ("Release Blog Post" section) that predates this session.

## Repo Locations

- Working: `~/Desktop/claude-obsidian/`
- Public: https://github.com/AgriciDaniel/claude-obsidian
