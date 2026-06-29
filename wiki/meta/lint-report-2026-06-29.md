---
type: meta
title: "Lint Report 2026-06-29"
created: 2026-06-29
updated: 2026-06-29
tags: [meta, lint]
status: developing
---

# Lint Report: 2026-06-29

Scope: the SEC/EDGAR autoresearch pages (passes 1-2, 30 pages). Run as part of the autoresearch loop.

## Summary

| Check | Result |
|-------|--------|
| Dead wikilinks (new pages) | **0** |
| Orphan pages (new pages with no inbound link) | **0** |
| Pages scanned | 30 |

## Detail

- **Dead links:** none. Every `[[wikilink]]` in the SEC/EDGAR/Reg-CF pages resolves to an existing page (stem resolution).
- **Orphans:** none. All 30 new pages have at least one inbound link (from the synthesis page, the index, or sibling pages).
- **Frontmatter:** all new pages carry type/title/created/updated/tags/status.

## Needs human review

- **Confidence flags (by design, not errors):** several `> [!gap]` / `> [!note]` callouts mark facts captured via WebSearch excerpts because SEC.gov blocks automated WebFetch (HTTP 403). Items to verify in a browser: exact EDGAR API rate limit; EDGAR Next December 2025 sub-deadlines; Reg CF financial-statement tier thresholds (Rule 201(t)); 2025 Reg CF platform dollar/share figures (single market-analysis source, confidence low).
- No destructive fixes were applied (no deletions, no edits to pre-existing non-loop pages).

## Next

Open research clusters remaining (see synthesis Open Questions): Reg S-K/S-X, remaining exemptions (Reg D/A+/144), SEC enforcement & structure, practical EDGAR data access.

---

# Pass 4 re-lint (full vault, after passes 3-4)

Scope: entire vault (124 pages) for dead links; all SEC/EDGAR loop pages for orphans.

## Summary

| Check | Result |
|-------|--------|
| Orphan pages (loop concept/entity/question pages) | **0** |
| Dead links introduced by THIS loop | **3, all fixed** |
| Pre-existing dead links (not from this loop) | 20 distinct targets - flagged below, not modified |

## Fixed (this loop's own pages)

- `Recent SEC Rulemaking and Litigation 2023-2026.md`: three wikilinks used table-escaped pipes (`[[Page\|alias]]`) which render in Obsidian but tripped strict link resolution. Rewrote as plain `[[Page]]` links. Now resolve cleanly.

## Needs human review (pre-existing, NOT touched by this loop)

These dead links predate the SEC/EDGAR autoresearch and were left untouched:

- `[[How does the LLM Wiki pattern work?]]` (trailing `?`) referenced from hot.md/log.md/Query-Time Retrieval.md, while the actual file is `How does the LLM Wiki pattern work.md` (no `?`). Likely a rename-drift; an alias or link fix would resolve it.
- `[[Wiki Map]]` (6 refs) - target is `Wiki Map.canvas`, not a `.md`; expected for canvas links.
- `[[Foo]]` - illustrative example text in DragonScale Memory.md / log.md.
- Doc/skill stubs: `[[mcp-setup]]`, `[[wiki-cli]]`, `[[wiki-fold]]`, `[[wiki-mode]]`, `[[methodology-modes-guide]]`, `[[fold-template]]`, `[[dashboard.base]]`, `[[claude-obsidian-presentation]]`, `[[AI Marketing Hub Cover Images Canvas]]`, `[[Claude Canvas]]`, `[[Claude Obsidian]]`, `[[Karpathy LLM Wiki Pattern]]`, `[[Rankenstein]]`, `[[E-commerce SEO]]`, `[[Three laws of motion]]`, `[[wikilinks]]`.
- `[[wikilink]]` in this report (pass 2 section) is illustrative prose, not a real link.

No destructive fixes applied. Pre-existing items are surfaced for the maintainer to decide.

---

# Pass 7 re-lint (after passes 5-7)

Scope: 32 SEC/EDGAR loop concept/entity/question pages (vault now 146 pages total).

## Summary

| Check | Result |
|-------|--------|
| Dead links in loop pages | **0** |
| Orphan loop pages | **0** |
| Loop concept/entity/question pages | 32 |

All exemptions (Reg D/A/144/Accredited/Exempt Offerings), disclosure-rulebook (S-K/S-X/Integrated Disclosure), and enforcement (Divisions/Enforcement Process/Whistleblower) pages link cleanly and have inbound references. No self-introduced dead links this round (table-escaped-pipe pattern avoided per the pass-4 lesson). Pre-existing vault dead links from the pass-4 section remain for human review; not re-listed.

---

# Pass 10 re-lint (after passes 9-10)

Scope: 39 SEC/EDGAR loop concept/entity/question pages (vault now 163 pages).

| Check | Result |
|-------|--------|
| Dead links in loop pages | **0** |
| Orphan loop pages | **0** |

New proxy (Proxy Statement / Universal Proxy / Rule 14a-8) and takeover (Williams Act / Tender Offer) pages all link cleanly and have inbound references. Passes 9-10 fetched SEC primary sources directly via `scripts/sec-fetch.sh` (compliant User-Agent + redirect-following), so those source pages are marked "verified" rather than "search excerpt."
