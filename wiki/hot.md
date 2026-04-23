---
type: meta
title: "Hot Cache"
updated: 2026-04-24T00:45:00
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

2026-04-24: Phase 3.5 hardening pass. Cross-phase audit ran (codex rated original Phase 1-3 output cross-phase risk as "high" with 10 hold-ship items). All 10 resolved: doc-lint contradiction fixed, Mechanism 4 labeled NOT IMPLEMENTED, DragonScale Memory.md assigned `address: c-000001`, agents/wiki-ingest.md + agents/wiki-lint.md updated to reflect Phase 2+3, hooks.json extended to stage `.vault-meta/`, `bin/setup-dragonscale.sh` created as opt-in installer, `tests/` + `Makefile` added (all tests pass), versions synced to 1.5.0 across plugin.json + marketplace.json, CHANGELOG.md created.

2026-04-23 (3): Phase 3 complete. Semantic tiling lint shipped as opt-in. `scripts/tiling-check.py` (485 lines) with flock-guarded atomic cache, localhost-locked OLLAMA_URL default, symlink rejection, model-drift invalidation, and banded thresholds (error>=0.90, review>=0.80, conservative seeds). 4 codex review rounds, 10/10 accept.

2026-04-23 (2): Phase 2 complete. Deterministic page addresses MVP via `scripts/allocate-address.sh` (flock-guarded, recovers counter from max observed). New frontmatter `address: c-NNNNNN`. `wiki-ingest` and `wiki-lint` updated with opt-in Address Assignment and Validation sections. 3 codex rounds, 8/8 accept.

2026-04-23 (1): Phase 0-1 complete. DragonScale Memory spec (`wiki/concepts/DragonScale Memory.md` v0.3) plus `skills/wiki-fold/` for Mechanism 1 (log rollups, dry-run verified). Survived multi-round codex review.

## Plugin State

- **Version**: 1.6.0 (Phase 4 shipped; plugin.json + marketplace.json synced; 1.5.1 was the Phase 3.6 hardening point release)
- **Install ID**: `claude-obsidian@claude-obsidian-marketplace`
- **Skills**: 11 (wiki, wiki-ingest, wiki-query, wiki-lint, wiki-fold, save, autoresearch, canvas, defuddle, obsidian-bases, obsidian-markdown)
- **Scripts**: `scripts/allocate-address.sh`, `scripts/tiling-check.py` (both opt-in; feature-detected by skills)
- **Setup**: `bin/setup-vault.sh` (base vault), `bin/setup-dragonscale.sh` (opt-in DragonScale), `bin/setup-multi-agent.sh` (multi-agent bootstrap)
- **Tests**: `make test` runs `tests/test_allocate_address.sh` + `tests/test_tiling_check.py`. Zero ollama dependency for core tests.
- **Hooks**: 4 (SessionStart, PostCompact, PostToolUse [stages wiki/, .raw/, .vault-meta/], Stop)

## DragonScale Mechanisms

1. **Fold operator** (Mechanism 1): `skills/wiki-fold/`, dry-run verified. No fold committed yet in this vault.
2. **Deterministic addresses** (Mechanism 2): shipped; vault counter at 2 (DragonScale Memory.md holds c-000001).
3. **Semantic tiling lint** (Mechanism 3): shipped; awaiting `ollama pull nomic-embed-text` to activate in this vault.
4. **Boundary-first autoresearch** (Mechanism 4): shipped (Phase 4, opt-in). `scripts/boundary-score.py` + `tests/test_boundary_score.py`. `/autoresearch` without a topic surfaces top-5 frontier pages as candidates; user picks, overrides, or declines. Explicitly labeled "agenda control" in both spec and skill.

## Key Lessons from This Release Cycle

1. Cross-phase audits are essential. Individual phase reviews miss drift between phases.
2. Opt-in feature detection (`[ -x script ] && [ -f state ]`) preserves default plugin behavior for adopters and non-adopters alike.
3. PostToolUse hook matcher is `Write|Edit` — Bash writes don't fire it. Scripts that mutate tracked state must be Bash-only to avoid side-effect commits.
4. Seed-vault self-consistency matters: if the spec says post-rollout pages need addresses, the concept page itself has to have one.
5. Codex adversarial review rounds stop when the punch list is empty, not when the author feels done.

## Style Preferences

- No em dashes (U+2014) or `--` as punctuation. Periods, commas, colons, or parentheses. Hyphens in compound words are fine.
- Short and direct responses. No trailing summaries.
- Parallel tool calls when independent.

## Active Threads

- DragonScale Mechanism 4 shipped in Phase 4 as an opt-in Topic Selection mode in `skills/autoresearch/`. All four DragonScale mechanisms are now shipped and feature-gated.
- v1.5.0 not yet pushed to GitHub. User controls the push timing.
- CLAUDE.md has one pre-existing uncommitted change ("Release Blog Post" section) that predates this session.

## Repo Locations

- Working: `~/Desktop/claude-obsidian/`
- Public: https://github.com/AgriciDaniel/claude-obsidian
