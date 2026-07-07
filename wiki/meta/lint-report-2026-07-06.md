---
type: meta
title: "Lint Report 2026-07-06"
created: 2026-07-06
updated: 2026-07-06
tags: [meta, lint]
status: developing
---

# Lint Report: 2026-07-06

## Summary
- Pages scanned: 47 (wiki/**/*.md)
- Issues found: 21
- Auto-fixed: 0
- Needs review: 21

## Dead Links

- [[AI Marketing Hub Cover Images Canvas]] — referenced in `wiki/overview.md:60`, no matching page or canvas exists. Suggest: create the canvas or remove the line.
- [[Claude Obsidian]], [[Claude Canvas]], [[Rankenstein]], [[Karpathy LLM Wiki Pattern]] — all four in the `related:` frontmatter of `wiki/meta/2026-04-10-backlink-empire-session.md:15-18`, none exist as pages. Suggest: create stubs or drop from `related:`.
- [[E-commerce SEO]] — referenced in `wiki/meta/2026-04-14-claude-seo-v190-session.md:19` and `wiki/entities/Claude SEO.md:18`, page does not exist. Suggest: create a concept stub or remove the link.
- [[How does the LLM Wiki pattern work?]] (trailing `?`) — used in `wiki/log.md:53`, `wiki/hot.md:35`, `wiki/concepts/Query-Time Retrieval.md:12`, `wiki/concepts/Source-First Synthesis.md:12`, `wiki/concepts/Persistent Wiki Artifact.md:12`. The actual page is `wiki/questions/How does the LLM Wiki pattern work.md` (no `?`). These links do not resolve. Suggest: strip the trailing `?` in all five locations.
- [[wiki-cli]], [[wiki-fold]], [[wiki-mode]] — referenced in `wiki/references/transport-fallback.md:6`, `wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md:49,78,108`, and `wiki/references/methodology-modes.md:11,69`. These name skill folders (`skills/wiki-cli/`, etc.) which have no note file at that stem, so the wikilink is unresolvable. Suggest: link to the `SKILL.md` file directly or leave as plain text since these aren't vault pages.

Not flagged (checked and resolve correctly): `[[claude-obsidian-presentation]]` → `wiki/canvases/claude-obsidian-presentation.canvas`, `[[mcp-setup]]` → `skills/wiki/references/mcp-setup.md`, `[[dashboard.base]]` → `wiki/meta/dashboard.base`, `[[Wiki Map]]` → `wiki/Wiki Map.canvas`. Also not flagged: `[[Three laws of motion]]`, `[[wikilinks]]`, `[[Foo]]`, `[[notes/Foo]]` — these appear inside inline code spans as syntax examples, not real links.

## Orphan Pages

- [[transport-fallback]] (`wiki/references/transport-fallback.md`) — no inbound links found.
- [[methodology-modes]] (`wiki/references/methodology-modes.md`) — no inbound links found.
- [[retrieval-benchmark-v1.7]] (`wiki/meta/retrieval-benchmark-v1.7.md`) — no inbound links found.
- [[tiling-report-2026-04-24]] (`wiki/meta/tiling-report-2026-04-24.md`) — no inbound links found; also has no frontmatter at all (see below).
- [[2026-04-10-backlink-empire-session]] (`wiki/meta/2026-04-10-backlink-empire-session.md`) — no inbound links found.
- [[fold-k3-from-2026-04-23-to-2026-04-24-n8]] (`wiki/folds/…`) — no inbound links found (folds are typically referenced from `log.md` rollup markers only).

## Frontmatter Gaps

- [[2026-04-15-release-report-session]]: missing `created`
- [[2026-04-15-slides-and-release-session]]: missing `created`
- [[boundary-frontier-2026-04-24]]: missing `created`
- [[retrieval-benchmark-v1.7]]: missing `created`, `tags`
- [[methodology-modes]] (`wiki/references/methodology-modes.md`): missing `created`, `updated`
- [[transport-fallback]] (`wiki/references/transport-fallback.md`): missing `created`, `tags`
- `wiki/meta/tiling-report-2026-04-24.md`: **no frontmatter block at all** — starts directly with `# Semantic Tiling Report`. This is a generated report (`scripts/tiling-check.py --report`); consider having the generator emit a minimal `type: meta` block, or exclude it from the frontmatter check explicitly.

## Empty Sections

None found. (Initial heuristic pass flagged ~30 headings immediately followed by a subheading — e.g. `wiki/concepts/cherry-picks.md` Tier headings, `wiki/entities/*.md` "Key Innovations" — but manual inspection showed real content under each subheading. No genuine empty sections.)

## Stale Index Entries

None found in `wiki/index.md`. (Initial diff flagged `concepts/_index`, `entities/_index`, `sources/_index`, `Wiki Map` as unresolved, but these are folder-qualified links and a canvas file respectively — all resolve correctly.)

## Address Validation (DragonScale Mechanism 2)

- Rollout baseline: 2026-04-23 (from `.vault-meta/legacy-pages.txt`)
- Legacy-pages manifest: present but empty (no explicit grandfathered paths)
- Counter peek: **could not run** — `./scripts/allocate-address.sh --peek` fails with `line 36: flock: command not found`. `flock` is not installed on this macOS system (no Homebrew formula either). This is a tooling gap, not a vault-data error — worth fixing the script to fall back to `mkdir`-based locking or detect `flock` absence, or documenting a `brew install flock`/`util-linux` dependency.
- Counter file (`.vault-meta/address-counter.txt`): `3`
- Addresses observed in frontmatter: exactly one — `wiki/concepts/DragonScale Memory.md` → `c-000001` (format valid, no collisions). A second `address: c-000042` appears at line 91 of the same file but is inside a fenced code example illustrating the address format, not real frontmatter — correctly not counted.
- Address-map (`.raw/.manifest.json`) consistency: `wiki/concepts/DragonScale Memory.md` → `c-000001` matches frontmatter. No mismatch.

### Errors

- [[Persistent Wiki Artifact]] (`wiki/concepts/Persistent Wiki Artifact.md`): created 2026-04-24 (post-rollout), no `address` field. Missing address is a lint error for post-rollout pages.
- [[Query-Time Retrieval]] (`wiki/concepts/Query-Time Retrieval.md`): created 2026-04-24 (post-rollout), no `address` field.
- [[Source-First Synthesis]] (`wiki/concepts/Source-First Synthesis.md`): created 2026-04-24 (post-rollout), no `address` field.

All three were filed by the same autoresearch run (per `wiki/hot.md:35`) that shipped after DragonScale's rollout date but never ran through the address allocator. Suggest: run `./scripts/allocate-address.sh` for each (once the `flock` dependency is resolved) and backfill the frontmatter.

### Pending backfill (informational)

21 legacy pages (created before 2026-04-23) without an address — expected, not an error:
`wiki/comparisons/Wiki vs RAG.md`, `wiki/comparisons/claude-obsidian-ecosystem.md`, `wiki/concepts/Compounding Knowledge.md`, `wiki/concepts/Hot Cache.md`, `wiki/concepts/LLM Wiki Pattern.md`, `wiki/concepts/Pro Hub Challenge.md`, `wiki/concepts/SEO Drift Monitoring.md`, `wiki/concepts/SVG Diagram Style Guide.md`, `wiki/concepts/Search Experience Optimization.md`, `wiki/concepts/Semantic Topic Clustering.md`, `wiki/concepts/cherry-picks.md`, `wiki/entities/Andrej Karpathy.md`, `wiki/entities/Ar9av-obsidian-wiki.md`, `wiki/entities/Claude SEO.md`, `wiki/entities/Claudian-YishenTu.md`, `wiki/entities/Nexus-claudesidian-mcp.md`, `wiki/entities/ballred-obsidian-claude-pkm.md`, `wiki/entities/kepano-obsidian-skills.md`, `wiki/entities/rvk7895-llm-knowledge-bases.md`, `wiki/questions/How does the LLM Wiki pattern work.md`, `wiki/sources/claude-obsidian-ecosystem-research.md`.

`wiki/references/methodology-modes.md` and `wiki/references/transport-fallback.md` have `type: reference` and no `created` date at all, so they default to "legacy" by the classification rule — but they should get a `created` field regardless (see Frontmatter Gaps above).

## Semantic Tiling (DragonScale Mechanism 3)

- `./scripts/tiling-check.py --peek` succeeded (exit 0) but reports `ollama_reachable: false` and `model_present: false`.
- `./scripts/tiling-check.py --report` returned exit `10` (ollama unreachable) — tiling skipped this run, as documented behavior when Ollama isn't running locally.
- A prior report exists: [[tiling-report-2026-04-24]] — 0 errors, 15 review-band pairs, not yet calibrated. Worth a manual look since it's 2.5 months old and 11 more pages have been added since.
- To re-run: start Ollama (`ollama serve`) and ensure `nomic-embed-text` is pulled (`ollama pull nomic-embed-text`), then re-invoke lint.

## Naming Convention Check

No violations found — filenames are Title Case, folders are lowercase-with-dashes, tags are lowercase/hierarchical where present.

## Recommended Priority

1. **Fix the 3 post-rollout address errors** (Persistent Wiki Artifact, Query-Time Retrieval, Source-First Synthesis) — this is the one genuine DragonScale-enforcement gap.
2. **Fix the `?` typo** in 5 wikilinks to `[[How does the LLM Wiki pattern work]]` — quick, mechanical, closes 5 dead links at once.
3. **Resolve or stub** the 4 dangling `related:` links in `2026-04-10-backlink-empire-session.md` and the `E-commerce SEO` / `AI Marketing Hub Cover Images Canvas` dead links.
4. **Add missing `created`/`tags` fields** to the 6 pages flagged under Frontmatter Gaps.
5. **Investigate the `flock` gap** in `allocate-address.sh` — it silently blocks all address-counter operations on stock macOS.
