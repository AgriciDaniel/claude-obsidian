---
type: meta
title: "Operation Log"
updated: 2026-04-08
tags:
  - meta
  - log
status: evergreen
related:
  - "[[index]]"
  - "[[hot]]"
  - "[[overview]]"
  - "[[sources/_index]]"
---

# Operation Log

Navigation: [[index]] | [[hot]] | [[overview]]

Append-only. New entries go at the TOP. Never edit past entries.

Entry format: `## [YYYY-MM-DD] operation | Title`

Parse recent entries: `grep "^## \[" wiki/log.md | head -10`

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 10: takeovers / Williams Act + lint)
- Rounds: 1 (2 search angles + SEC primary fetch via scripts/sec-fetch.sh)
- Sources found: 3 (SEC.gov tender-offer CDI fetched DIRECTLY + verified, Ropes & Gray, US Law Explained)
- Pages created: [[Williams Act]], [[Tender Offer]] + 3 source pages (5 total)
- Lint: full-vault (163 pages); 0 dead links / 0 orphans across 39 loop pages
- Tooling: improved scripts/sec-fetch.sh to follow redirects (-L) after diagnosing sec.gov 301s (principle: fix access, don't work around it)
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 10 section)
- Key finding: Williams Act (1968) = takeover rules via Sections 13(d)/14(d)/14(e). Tender offers run on Schedule TO (SC TO-T/TO-I/TO-C) with a 14D-9 board response in 10 business days; 20-business-day minimum period, all-holders + best-price rules, withdrawal rights; Rule 13e-4 (issuer self-tender) and 13e-3 (going private). Notable: April 16 2026 SEC exemptive order halves the minimum period to 10 business days for negotiated all-cash equity offers.

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 9: proxy solicitation)
- Rounds: 1 (2 search angles + 2 SEC primary fetches via scripts/sec-fetch.sh)
- Sources found: 4 (2 SEC.gov fetched DIRECTLY + verified, Cornell LII, Debevoise)
- Pages created: [[Proxy Statement]], [[Universal Proxy]], [[Rule 14a-8 Shareholder Proposals]] + 4 source pages (7 total)
- Method note: FIRST pass to apply the new operating principle - pulled SEC primary sources directly with the compliant-User-Agent wrapper instead of relying on search excerpts. Captured exact rule cites (14a-19(e), 67% solicitation threshold, 60/50/25-day deadlines, release 34-93596) verbatim.
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 9 section)
- Key finding: Proxy statements (DEF 14A / Schedule 14A) are governed by Section 14(a); "solicitation" is defined broadly. Say-on-pay is an advisory Dodd-Frank vote. Universal proxy (Rule 14a-19, effective 2022) forces one card listing all sides' nominees in contests, lowering the bar for activists. Rule 14a-8 is the separate shareholder-proposal path.

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 8: practical EDGAR data access)
- Rounds: 1 (3 search angles)
- Sources found: 3 (all SEC.gov: Accessing EDGAR Data, Financial Statement Data Sets, New Rate Control Limits)
- Pages created: [[EDGAR Data Access]], [[EDGAR Bulk Data]] + 3 source pages (5 total); also resolved the rate-limit gap in [[EDGAR APIs]]
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 8 section; planned backlog complete)
- Key finding: CIK = permanent 10-digit filer ID; accession number = submitterCIK-YY-sequential. Fair access = 10 req/s per IP + required User-Agent header; violations return HTTP 403 + ~10-min block (this is exactly why sec.gov 403'd this vault's WebFetches). Bulk analysis via Financial Statement Data Sets (SUB/NUM/TAG/PRE, since Apr 2009, monthly from Apr 2023), full-index, and DERA Data Library.

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 7: structure & enforcement + lint)
- Rounds: 1 (3 search angles)
- Sources found: 3 (SEC.gov org chart, Winston & Strawn, Wikipedia)
- Pages created: [[SEC Divisions and Structure]], [[SEC Enforcement Process]], [[SEC Whistleblower Program]] + 3 source pages (6 total)
- Lint: full-vault (146 pages); 0 dead links / 0 orphans across 32 loop pages
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 7 section added)
- Key finding: SEC = 5 divisions (Corp Fin, Enforcement, Trading & Markets, IM, DERA). Enforcement runs investigation -> Wells notice -> submission -> charge (administrative proceeding or federal court) or close; most settle. Dodd-Frank whistleblower program pays 10-30% of sanctions over $1M from the Investor Protection Fund with anti-retaliation protection.

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 6: disclosure rulebooks S-K / S-X)
- Rounds: 1 (3 search angles)
- Sources found: 3 (Cornell LII x2, CFO Bridge)
- Pages created: [[Regulation S-K]], [[Regulation S-X]], [[Integrated Disclosure System]] + 3 source pages (6 total)
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 6 section added)
- Key finding: The 1982 integrated disclosure system splits content into two rulebooks: Reg S-K (narrative - business, risk factors, MD&A Item 303, exec comp) and Reg S-X (financial-statement form/content, 17 CFR Part 210, auditor independence, Rule 3-05 acquired-business financials, Rule 1-02(w) significance tests). The same S-K + S-X items populate both registration statements and periodic reports.

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 5: private-offering exemptions)
- Rounds: 1 (4 search angles, detailed SEC/law excerpts)
- Sources found: 5 (4 SEC.gov, Carta)
- Pages created: [[Exempt Offerings]], [[Regulation D]], [[Regulation A]], [[Accredited Investor]], [[Rule 144]] + 5 source pages (11 total)
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 5 section added)
- Key finding: Reg D Rule 506 is the dominant private exemption (506(b) no-solicitation/35 non-accredited vs 506(c) accredited-only-with-verification, both Form D). Reg A is a public mini-IPO ($20M Tier 1 / $75M Tier 2, Form 1-A). Accredited status = $200k income or $1M net worth, plus Series 7/65/82 since 2020. Rule 144 governs resale (6mo/1yr holding; affiliate volume caps).

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 4: recent rulemaking + lint)
- Rounds: 1 (4 search angles, detailed law-firm/SEC excerpts; no extra fetch needed)
- Sources found: 5 (2 SEC.gov, DLA Piper, Orrick, Davis Polk)
- Pages created: [[SEC Cybersecurity Disclosure Rules]], [[SEC Climate Disclosure Rule]], [[T+1 Settlement Cycle]], [[Recent SEC Rulemaking and Litigation 2023-2026]] + 5 source pages (9 total)
- Lint: full-vault wiki-lint run; 0 orphans among loop pages, fixed 3 self-introduced dead links (table-escaped pipes), pre-existing dead links flagged for human review in [[Lint Report 2026-06-29]]
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 4 section added)
- Key finding: 2023-26 SEC rules split by type. Operational rules stuck (T+1 settlement May 2024; cyber 8-K Item 1.05). Disclosure-expansion rules failed: the buyback rule was vacated by the Fifth Circuit (Dec 2023) and the climate rule was stayed then proposed for rescission (2026).

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 3: XBRL & structured data)
- Rounds: 2 (4 search angles + 2 depth fetches)
- Sources found: 5 (2 SEC.gov, Covington, Cooley, IRIS Carbon)
- Pages created: [[XBRL]], [[Financial Data Transparency Act]], [[Financial Accounting Standards Board]] + 5 source pages (8 total)
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 3 section added)
- Key finding: SEC has required XBRL since 2009 and inline XBRL since 2018 (phased 2019-2021); financial data is tagged against FASB's ~17k-tag US GAAP taxonomy and powers the EDGAR APIs. The 2022 FDTA extends machine-readable standards across nine federal regulators with a common LEI; final joint rule in 2026.

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 2: Reg CF funding portals)
- Rounds: 2 (4 search angles + 2 depth fetches)
- Sources found: 7 (3 SEC.gov, 1 FINRA, 3 secondary/market)
- Pages created: [[Regulation Crowdfunding]], [[Funding Portal]], [[Form C]], [[Financial Industry Regulatory Authority]], [[Wefunder]], [[StartEngine]], [[Republic (crowdfunding)]] + 7 source pages (14 total)
- Synthesis: [[Research - SEC regulations and EDGAR]] (Pass 2 section added)
- Key finding: Reg CF (Title III JOBS Act) allows $5M/yr public raises only through a FINRA-member funding portal or broker-dealer; portals register via Form Funding Portal on EDGAR and cannot advise, solicit, or hold funds. 83 portals registered end-2024; Wefunder leads (~33% of 2025 dollars).

## [2026-06-29] autoresearch | SEC regulations and EDGAR (pass 1)
- Rounds: 2 (broad sweep + targeted gap fetches)
- Sources found: 9 (4 SEC/investor.gov primary, 2 Wikipedia, 3 secondary/vendor)
- Pages created: [[U.S. Securities and Exchange Commission]], [[EDGAR]], [[EDGAR Next]], [[SEC Filing Types]], [[EDGAR APIs]], [[Federal Securities Laws]] + 9 source pages + synthesis
- Synthesis: [[Research - SEC regulations and EDGAR]]
- Key finding: US securities regulation is a mandatory-disclosure regime (1933 Act = offerings, 1934 Act = ongoing reporting); EDGAR is the filing pipe, now mid-modernization via EDGAR Next (Login.gov + MFA, compliance required Sept 15 2025).
- Note: running on a 2-hour loop; subsequent passes fill Open Questions (XBRL/FDTA, recent rulemaking, Reg S-K/S-X, exemptions, API rate limits).

---

## [2026-04-24] save | v1.6.0 public release notes (Teams, Karpathy-style)
- Type: release doc + visual assets
- Locations (new): `docs/releases/v1.6.0.md` (346 lines, 6 sections, Karpathy-style prose), `wiki/meta/dragonscale-mechanism-overview.svg` (4-mechanism diagram with shared .vault-meta/ gate), `wiki/meta/dragonscale-6-test-flow.svg` (validation timeline), `wiki/meta/dragonscale-frontier-graph.svg` (M4 candidate + 3 filed pages)
- Locations (modified): `wiki/meta/2026-04-24-v1.6.0-release-session.md` (cross-reference added pointing to public release notes)
- Scope: Teams approach. R1 (chair) wrote 3 original SVGs per SVG Diagram Style Guide. R2 (codex worker) drafted Karpathy-style release prose. R3 (chair) stitched SVGs, pivoted Wikipedia imagery to text links only (no binary vendoring per permission). R4 (codex verifier) returned ACCEPT WITH FIXES, 3 wording fixes on version narrative. R5 (chair) applied fixes, committed.
- Style: direct, short, signal-dense, lists over prose, no em dashes, no marketing terms. Verifier confirmed zero em-dashes and zero banned marketing language ('revolutionary', 'seamless', 'world-class', 'game-changing', 'unlock', 'transform').
- Distribution (all three destinations covered): (1) `docs/releases/v1.6.0.md` public-facing file (commit `85515bb`), (2) `wiki/meta/2026-04-24-v1.6.0-release-session.md` internal engineering record (cross-linked), (3) GitHub Release body (user to paste from docs/releases/v1.6.0.md when ready to `gh release create v1.6.0`).
- Wikipedia imagery: referenced as text link to `https://en.wikipedia.org/wiki/Dragon_curve` rather than hotlinked or vendored. Cleaner license-wise (no CC-BY-SA attribution needed) and no external dependency. The 3 original SVGs carry the visual load instead.
- PII scan post-write: `docs/releases/v1.6.0.md` + all three SVGs are clean. No `/home/` paths, no real emails, no tokens.
- Next recommended: user runs `gh release create v1.6.0 --notes-file docs/releases/v1.6.0.md` when ready to cut the public release. This also creates the annotated tag.

## [2026-04-24] save | DragonScale end-to-end validation pass (Teams, 6 tests)
- Type: validation + first real fold + first real autoresearch
- Tests executed (all green):
  - T0 ollama pull `nomic-embed-text`: done (274MB, 15s wall)
  - T1 M1 dry-run k=3 via codex: DRY-RUN OK, 8 children, no em-dashes
  - T2 M2 real allocate: counter advanced 2 to 3, got `c-000002` (unassigned reservation; gap acceptable per spec)
  - T3 M3 full tiling with model present: 41 pages scanned, 21 embedded, 20 correctly skipped (meta/excluded/embed-error), 0 errors at >=0.9, 15 pairs in 0.8-0.9 review band (top 0.8822 Compounding Knowledge vs LLM Wiki Pattern, a legitimate semantic neighbor), report at `wiki/meta/tiling-report-2026-04-24.md`
  - T4 M1 commit via codex: first real fold committed, `wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md` (115 lines, 8 children, flat extractive). Flips the long-standing "no fold committed yet" status
  - T6 M4 autoresearch no-topic via codex: selected "How does the LLM Wiki pattern work?" as candidate (score 1.7022, #3 after skipping top-1 source + top-2 self-reference); 6 web fetches (Karpathy gist, RAG paper arXiv 2005.11401, MemGPT arXiv 2310.08560, Obsidian docs); 3 new concept pages filed, each with Primary Sources
- Locations (new): `wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md`, `wiki/meta/tiling-report-2026-04-24.md`, `wiki/concepts/Persistent Wiki Artifact.md`, `wiki/concepts/Source-First Synthesis.md`, `wiki/concepts/Query-Time Retrieval.md`
- Locations (modified): `.vault-meta/address-counter.txt` (2 to 3), `wiki/index.md` (3 concept links), `wiki/concepts/_index.md` (3 concept links)
- Scope: six-test menu the user approved. Codex gpt-5.4 for T1/T4/T6 (sub-agent delegation); chair for T0/T2/T3 (one-shot shell) and all integration (index, log, hot, commit).
- Style: all new content uses colons or parens instead of em-dashes. Pre-existing em-dashes in index entries and wiki/concepts/_index.md left as-is (clean-room boundary; deferred to F-slice style pass).
- Tests still green: `make test` passes (74+ assertions).
- Integration: chair added the 3 new concepts to `wiki/index.md` and `wiki/concepts/_index.md` with colon-style descriptions so the fresh pages are discoverable. The cluster extends `[[How does the LLM Wiki pattern work?]]` and cross-references `[[LLM Wiki Pattern]]`.
- Next recommended slice: either (G) commit this test batch and declare v1.6.0 validated, or (H) run a second fold k=3 now that 8 newer entries exist above this one and close the hierarchical-fold-not-yet-supported loop in a future phase.

## [2026-04-24] save | v1.6.0 closeout (Teams, chair-led)
- Type: docs + release hygiene
- Locations (new): wiki/meta/2026-04-24-v1.6.0-release-session.md (release session summary, 346 lines), wiki/meta/boundary-frontier-2026-04-24.md (first M4 run artifact against this vault), docs/dragonscale-guide.md (user-facing DragonScale guide, 563 lines)
- Locations (modified): wiki/hot.md (tag-claim fix, Scripts line adds boundary-score, tests line adds test_boundary_score, push-line drift, tiling line-count, one em-dash), docs/install-guide.md (version 1.5.0 to 1.6.0, DragonScale callout expanded to all four mechanisms, "hierarchical log folds" corrected to "flat extractive log folds", points to docs/dragonscale-guide.md), README.md (DragonScale parenthetical expanded to all four mechanisms plus guide link)
- Scope: Teams approach, chair-led. Slice A (2 codex read-only explorers: closeout punch list + doc-surface map). Slice B (6 bounded writes: 4 chair, 2 codex workers, non-overlapping write scopes). Slice C (codex adversarial verifier, ACCEPT WITH FIXES). Slice D (fix pass + log entry + manual commit of docs + README).
- Verifier: C1 found 11 items across 6 files. All 11 applied. Flag typos `--allow-remote-ollama` and `--report PATH` corrected in release-session; boundary-frontier provenance corrected to `--top 7` to match default vs explicit top; hot.md tiling line-count claim stripped to avoid drift; hot.md "local tag only" corrected to "local commits only, no git tag"; install-guide log-fold wording corrected from "hierarchical" to "flat extractive"; dragonscale-guide rollback wording corrected (`.vault-meta/` is a shared gate across M2+M3+M4, not per-mechanism).
- Model: codex gpt-5.4 used throughout. User requested gpt-5.5; not reachable via codex CLI 0.123.0 / this account at the time. models_cache lists max gpt-5.4, and the API rejects gpt-5.5 with "does not exist or you do not have access". Existing config already has `service_tier = "fast"` and `sandbox_mode = "workspace-write"`, matching the "fast for chatgpt with permission of full access" intent.
- Tests: `make test` passes. test_allocate_address.sh (shell, 12 assertions), test_tiling_check.py (python, 18 assertions), test_boundary_score.py (python, 44 assertions). Zero ollama dependency.
- Tags: still no local v1.5.0 / v1.5.1 / v1.6.0 tags. User controls tag creation and push. Pre-existing tags unchanged (v1.1, v1.4.0 through v1.4.3).
- Deliberately NOT done: no real M1 fold committed; no M3 end-to-end run (needs `ollama pull nomic-embed-text`); pre-existing em-dashes in install-guide.md and README.md left untouched (clean-room boundary, not in write scope this slice); CLAUDE.md pre-existing uncommitted change left untouched.
- Next recommended slice: either (E) push to origin/main and create annotated tags v1.5.0, v1.5.1, v1.6.0 in landing order, or (F) dedicated style pass to scrub pre-existing em-dashes across install-guide.md, README.md, and any other wiki files flagged by a grep scan.

## [2026-04-24] save | DragonScale Phase 4 — boundary-first autoresearch shipped (v1.6.0)
- Type: feature release
- Locations (new): scripts/boundary-score.py (with --top, --page, --json, stdout-only CLI), tests/test_boundary_score.py (40+ assertions)
- Locations (modified): skills/autoresearch/SKILL.md (new Topic Selection section A/B/C with helper-failure fallback), commands/autoresearch.md (no-topic candidate flow with agenda-control label), wiki/concepts/DragonScale Memory.md (v0.4: M4 flipped from NOT IMPLEMENTED to shipped; exact formula without recency floor; filename-stem disclosure; fence-handling qualifiers), CHANGELOG.md, .claude-plugin/{plugin,marketplace}.json (1.5.0 -> 1.6.0), Makefile (test-boundary target), wiki/hot.md, wiki/index.md, wiki/concepts/_index.md (status drift resolved).
- Scope: boundary-first autoresearch as opt-in Topic Selection mode. `/autoresearch` without a topic surfaces top-5 frontier pages; user picks/overrides/declines. Explicit helper-failure fallback to user-ask. Labeled "agenda control" throughout to match the spec's scope disclosure.
- Correctness: filename-stem resolution including folder-qualified `[[notes/Foo]]` -> Foo.md. Self-loops, unresolved targets, meta-targets, symlinks, and vault escapes all excluded. Code-fence parser handles backticks AND tildes with CommonMark length tracking (longer opening fence is not closed by shorter inner fence). Indented blocks intentionally not filtered (Obsidian bullet convention).
- Recency: exp(-days/30), no floor. Stale pages approach zero weight so they do not dominate frontier ranking.
- Review rounds: codex adversarial Phase 4 round 1 (10 items: 7 reject + 3 refine). Round 2 (7 accept + 3 still-reject: folder-qualified stem, docstring floor mention, hot.md historical drift). Round 3 (3 accept, PASS).
- Phase 3.6 (pre-Phase-4 hardening) already landed as v1.5.1: tiling --report VAULT_ROOT confinement, rollout baseline, AGENTS.md consistency, wiki-ingest .raw/ contradiction, install-guide version.
- All four DragonScale mechanisms now shipped and opt-in. 44 commits ahead of origin/main, no push.

## [2026-04-24] save | DragonScale Phase 3.5 — cross-phase hardening to v1.5.0
- Type: release hardening
- Locations (new): bin/setup-dragonscale.sh (opt-in installer), tests/test_allocate_address.sh, tests/test_tiling_check.py, Makefile, CHANGELOG.md
- Locations (modified): hooks/hooks.json (+.vault-meta/ staging), agents/wiki-ingest.md (single-writer rule for addresses), agents/wiki-lint.md (Mechanism 2+3 checks), skills/wiki-ingest/SKILL.md (aligned non-DragonScale wording), wiki/concepts/DragonScale Memory.md (M2 severity matches lint, M4 marked NOT IMPLEMENTED, seed page gets address c-000001), .claude-plugin/{plugin.json,marketplace.json} (1.4.2/1.4.3 → 1.5.0), README.md (11 skills + DragonScale callout), wiki/hot.md (refreshed for v1.5.0), .raw/.manifest.json (address_map now has DragonScale Memory.md → c-000001), .gitignore (.vault-meta/.tiling.lock + cache), .vault-meta/address-counter.txt (advanced to 2).
- Scope: resolve the 10 hold-ship items from the cross-phase audit. Add reproducible test harness (make test passes). Version-bump plugin.json and marketplace.json to 1.5.0. Create CHANGELOG.md. Refresh hot cache.
- Review rounds: codex 3.5a (5/5 accept on doc/agent fixes), codex final holistic (10/10 accept on audit items + 2 surgical regression fixes: wiki-ingest/wiki-lint non-DragonScale wording alignment, README skill count).
- Tests: `make test` runs 12 shell assertions (allocator) + 18 python assertions (tiling-check). All pass; no ollama dependency.
- Phase 3.5 complete. Repo state: 6 developer commits added this pass (f2e73c1, 2b49a0c, 8b28e48, 19ad7e4, 365f557, 2e7dd16). Total 39 commits ahead of origin/main. No push.

## [2026-04-24] save | DragonScale Phase 3 — semantic tiling MVP
- Type: skill update + new script + threshold state
- Locations: scripts/tiling-check.py (485 lines), .vault-meta/tiling-thresholds.json (seed defaults), skills/wiki-lint/SKILL.md (109-line Semantic Tiling section + item #10 in checks), wiki/concepts/DragonScale Memory.md (Mechanism 3 cost framing clarified)
- Scope: opt-in embedding-based duplicate detection via ollama nomic-embed-text. Default bands error>=0.90, review>=0.80, explicitly documented as conservative seeds (not literature-backed interpolation). Calibration procedure documented, not automated.
- Security: default OLLAMA_URL locked to 127.0.0.1; non-localhost requires --allow-remote-ollama flag. Symlinks and vault-root escapes rejected before file reads (prevents data exfil).
- Correctness: cache keyed on sha256(model+body); orphan GC on save; model-drift auto-invalidation on load.
- Concurrency: flock(LOCK_EX) on .vault-meta/.tiling.lock; per-PID temp file for atomic writes.
- Scale: warn >500 pages; hard-fail exit 4 at >5000 pages.
- Exit codes: 0/2/3/4/10/11 distinctly surfaced in wiki-lint wiring (not collapsed into "unknown").
- Review rounds: 4 codex exec adversarial passes covering security, cache correctness, feature gate, inclusion logic, scale, threshold honesty, concurrency, exit codes, model drift, terminology coupling.
  Round 1: 10 items -> 7 reject + 3 refine.
  Round 2: 6 accept + 4 still-reject (symlink ordering, prose sync, exit-code wiring, terminology in checklist + "no API cost" claim).
  Round 3: 3 accept + 1 still-reject (cost-framing phrasing).
  Round 4: accept.
- Final verdict: 10/10 accept.
- Phase 3 complete. All three DragonScale mechanisms that were in-scope for the initial spec are now shipped as opt-in features. Mechanism 4 (boundary-first autoresearch) was flagged as agenda-control out-of-scope per the v0.2 scope boundary; may or may not ship as a future phase.

## [2026-04-23] save | DragonScale Phase 2 — deterministic page addresses MVP
- Type: skill update + new script
- Locations: scripts/allocate-address.sh, skills/wiki-ingest/SKILL.md (Address Assignment section), skills/wiki-lint/SKILL.md (Address Validation section), wiki/concepts/DragonScale Memory.md (Mechanism 2 rewritten v0.2→v0.3), .vault-meta/address-counter.txt, .raw/.manifest.json (new)
- Scope: MVP address format `c-NNNNNN` (creation-order counter, zero-padded 6 digits). Rollout baseline 2026-04-23. Legacy pages exempt until deliberate backfill (future `l-` prefix). No content hash, no fold-ancestry encoding in the MVP (both deferred).
- Concurrency: atomic allocation via flock-guarded Bash helper. Counter recovery from max observed `c-` address, never silent reset to 1.
- Lint: post-rollout pages without address are errors; legacy pages without address are informational. Optional `.vault-meta/legacy-pages.txt` manifest grandfathers pages with missing/wrong `created:` metadata.
- Re-ingest idempotency: `.raw/.manifest.json` `address_map` preserves path→address mapping across re-ingests and renames.
- Naming: mechanism renamed from "content-addressable paths" to "deterministic page addresses" (the MVP is a counter, not a content hash; the old name was overclaim).
- Review rounds: 2 codex exec adversarial passes. Round 1: 8 rejects covering counter mutation, race conditions, uniqueness atomicity, missing-file recovery, terminology drift, silent regression path, legacy classification, re-ingest idempotency. Round 2: 7 accept + 1 reject (manifest.json absent). Round 3 (item 8 only): accept after creating `.raw/.manifest.json`.
- Final verdict: 8/8 accept.
- Phase 2 complete. Phase 3 (semantic tiling lint) gated on human approval.

## [2026-04-23] save | DragonScale Phase 1 — wiki-fold skill shipped
- Type: skill
- Location: skills/wiki-fold/SKILL.md, skills/wiki-fold/references/fold-template.md
- Scope: flat extractive fold over raw wiki/log.md entries. Dry-run default via Bash stdout (no Write tool, avoids PostToolUse hook residue). Structural idempotency via deterministic fold_id. Duplicate-range detection. Fold-of-folds explicitly out of scope.
- Review rounds: 3 codex exec adversarial passes. Round 1: 1 refine + 6 reject across 7 items (allowed-tools, hook-mutation risk, idempotency claim, dry-run faithfulness, children structure, Mechanism 1 coverage, auto-commit conflict). Round 2: 6 accept + 1 reject (25/26 count inversion). Round 3 (item 4 only): accept.
- Final verdict: 7/7 accept.
- Dry-run artifact: /tmp/wiki-fold-dry-run-v2.md (not committed). fold_id: fold-k3-from-2026-04-10-to-2026-04-23-n8.
- Phase 1 complete. Phase 2 (content-addressable paths) gated on human approval.

## [2026-04-23] save | DragonScale Memory v0.2 — post-adversarial-review
- Type: concept revision
- Location: wiki/concepts/DragonScale Memory.md
- Review: codex exec adversarial review rejected all 7 load-bearing claims in v0.1
- Changes: weakened LSM analogy, removed strong prompt-cache claim, replaced 0.85 threshold with calibration procedure, justified 2^k as MVP convenience, acknowledged scope-boundary leak for boundary-first autoresearch, added Operational Policies section (retention/tombstones/versioning/conflict/concurrency/provenance/ACL), tagged claims as [sourced]/[derived]/[conjecture], narrowed tagging scope per re-review
- Re-review result: 7/7 accepted (after one surgical fix on tagging-scope language)
- Phase 0 complete. Phase 1 (wiki-fold skill) gated on human approval.

## [2026-04-23] save | DragonScale Memory — Phase 0 design doc (proposed)
- Type: concept
- Location: wiki/concepts/DragonScale Memory.md
- From: brainstorming session on applying Heighway dragon curve properties to LLM wiki memory architecture
- Scope: memory-layer only, NOT agent reasoning. Four mechanisms: (1) fold operator (LSM-style exponential compaction at 2^k log entries), (2) content-addressable page paths for prompt-cache stability, (3) semantic tiling lint (embedding-based dedup, 0.85 cosine threshold), (4) boundary-first autoresearch scoring
- Status: proposed. Phase 0 pending codex adversarial review. Phase 1+ (fold skill, address anchors, tiling lint, boundary score) gated on review pass.
- Primary sources verified: Dragon curve (Wikipedia, boundary dim 1.523627086), Regular paperfolding sequence (OEIS A014577), LSM trees (arXiv 2504.17178, LevelDB 10x level ratio), MemGPT (arXiv 2310.08560), Anthropic prompt caching docs (5min/1hr TTL, 20-block lookback)
- Links updated: wiki/concepts/_index.md, wiki/index.md

## [2026-04-15] save | Claude SEO v1.9.0 Slides and GitHub Release
- Type: session
- Location: wiki/meta/2026-04-15-slides-and-release-session.md
- From: built 15-slide HTML presentation deck (v190.html), fixed hardcoded path in release_report.py, pushed 68 files to GitHub, tagged v1.9.0, created GitHub release with PDF asset
- Key lessons: Path.home() not hardcoded paths, git pull --rebase before big pushes, Chrome blocks file:// cross-origin images, .claude/ always in .gitignore
- Release: https://github.com/AgriciDaniel/claude-seo/releases/tag/v1.9.0

## [2026-04-15] save | Claude SEO v1.9.0 Release Report — PDF Complete
- Type: session
- Location: wiki/meta/2026-04-15-release-report-session.md
- From: full session completing the v1.9.0 PDF release report. Dark theme, 13 pages, 1.53 MB. Fixed logo (double-space filename), empty spaces, page-break orphans, file:// URL encoding.
- Key fixes: `urllib.parse.quote()` for file:// URIs; `display:table-cell` is atomic in WeasyPrint (no page-break); fixed `height:297mm` causes empty space; replaced orphan tables with paragraphs
- Challenge v2 added: keyword LEADS, $600 prize pool, deadline April 28
- Output: `~/Desktop/Claude-SEO-v1.9.0-Release-Report.pdf`

## [2026-04-14] save | Claude SEO v1.9.0 — Pro Hub Challenge Integration Session
- Type: session + 4 concept pages + 1 entity page
- Location: wiki/meta/2026-04-14-claude-seo-v190-session.md
- From: full v1.9.0 implementation session — reviewed 5 community submissions, integrated 4 new skills (seo-cluster, seo-sxo, seo-drift, seo-ecommerce), enhanced seo-hreflang, added DataForSEO cost guardrails
- Pages created: [[2026-04-14-claude-seo-v190-session]], [[Claude SEO]], [[Pro Hub Challenge]], [[Semantic Topic Clustering]], [[Search Experience Optimization]], [[SEO Drift Monitoring]]
- Review rounds: 4 (code review x3 + cybersecurity audit). Score: 87 → 93 → 97 → 85 security
- Key learnings: always verify subagent output (40-line count error caught), insertion-point bugs caught by max-effort plan review, pre-existing security debt identified (10 of 15 findings)

## [2026-04-14] save | SVG Diagram Style Guide
- Type: concept
- Location: wiki/concepts/SVG Diagram Style Guide.md
- From: extracted design tokens from 17 production SVGs in claude-ads/assets/diagrams/
- Covers: colors, typography, layout primitives, card patterns, arrow connectors, numbered circles, file naming

## [2026-04-14] save | Community CTA Footer Rollout
- Type: decision
- Location: wiki/meta/2026-04-14-community-cta-rollout.md
- From: session adding Skool community footer to 6 skill repos (claude-ads, claude-seo, claude-obsidian, claude-blog, banana-claude, claude-cybersecurity)
- Key insight: frequency calibration per tool type; single-point orchestrator instruction pattern

## [2026-04-10] save | Backlink Empire - Blog Posts, Karpathy Gist, GitHub Cross-Linking
- Type: session
- Location: wiki/meta/2026-04-10-backlink-empire-session.md
- From: full session covering blog creation (claude-obsidian + claude-canvas), Karpathy gist comment, 26 GitHub README updates with Author/community/backlink sections, homepage URLs on 10 repos, topics on 25 repos, rankenstein.pro backlinks on 5 SEO repos
- Blog posts: agricidaniel.com/blog/claude-obsidian-ai-second-brain, agricidaniel.com/blog/claude-canvas-ai-visual-production
- Impact: ~87 new backlinks from DA 96 github.com, 6 rankenstein.pro backlinks, 25 Skool community links

## [2026-04-08] save | claude-obsidian v1.4 Release Session
- Type: session
- Location: wiki/meta/claude-obsidian-v1.4-release-session.md
- From: full release cycle covering v1.1 (URL/vision/delta tracking, 3 new skills), v1.4.0 (audit response, multi-agent compat, Bases dashboard, em dash scrub, security history rewrite), and v1.4.1 (plugin install command hotfix)
- Key lessons: plugin install is 2-step (marketplace add then install), allowed-tools is not valid frontmatter, Bases uses filters/views/formulas not Dataview syntax, hook context does not survive compaction, git filter-repo needs 2 passes for full scrub

## [2026-04-08] ingest | Claude + Obsidian Ecosystem Research
- Type: research ingest
- Source: `.raw/claude-obsidian-ecosystem-research.md`
- Queries: 6 parallel web searches + 12 repo deep-reads
- Pages created: [[claude-obsidian-ecosystem]], [[cherry-picks]], [[claude-obsidian-ecosystem-research]], [[Ar9av-obsidian-wiki]], [[Nexus-claudesidian-mcp]], [[ballred-obsidian-claude-pkm]], [[rvk7895-llm-knowledge-bases]], [[kepano-obsidian-skills]], [[Claudian-YishenTu]]
- Key finding: 16+ active Claude+Obsidian projects; 13 cherry-pick features identified for v1.3.0+
- Top gap confirmed: no delta tracking, no URL ingestion, no auto-commit

## [2026-04-07] session | Full Audit, System Setup & Plugin Installation
- Type: session
- Location: wiki/meta/full-audit-and-system-setup-session.md
- From: 12-area repo audit, 3 fixes, plugin installed to local system, folder renamed

## [2026-04-07] session | claude-obsidian v1.2.0 Release Session
- Type: session
- Location: wiki/meta/claude-obsidian-v1.2.0-release-session.md
- From: full build session — v1.2.0 plan execution, cosmic-brain→claude-obsidian rename, legal/security audit, branded GIFs, PDF install guide, dual GitHub repos


- Source: `.raw/` (first ingest)
- Pages updated: [[index]], [[log]], [[hot]], [[overview]]
- Key insight: The wiki pattern turns ephemeral AI chat into compounding knowledge — one user dropped token usage by 95%.

## [2026-04-07] setup | Vault initialized

- Plugin: claude-obsidian v1.1.0
- Structure: seed files + first ingest complete
- Skills: wiki, wiki-ingest, wiki-query, wiki-lint, save, autoresearch

## [2026-06-05] ingest | Dive into Claude Code — README (arXiv 2604.14228)
- Source: `.raw/architechtai/doc_README.md`
- Summary: [[Dive-into-Claude-Code-README]]
- Pages created: [[Dive-into-Claude-Code-README]], [[VILA-Lab]], [[Dive into Claude Code]], [[Agent Harness Engineering]], [[queryLoop Architecture]], [[5-Layer Compaction]], [[Deny-First Permission Model]]
- Pages updated: [[Andrej Karpathy]], [[entities/_index]], [[sources/_index]], [[concepts/_index]], [[index]], [[hot]]
- Key insight: 98.4% of Claude Code is deterministic infrastructure; the harness (hooks, compaction, permissions) is the differentiator, not the model loop.


## [2026-06-05] ingest | Dive into Claude Code — Architecture (arXiv 2604.14228)
- Source: `.raw/architechtai/doc_architecture.md`
- Summary: [[Dive-into-Claude-Code-Architecture]]
- Pages created: [[Dive-into-Claude-Code-Architecture]], [[Claude Code Extensibility]], [[Subagent Delegation Architecture]], [[CLAUDE.md Hierarchy]]
- Pages updated: [[queryLoop Architecture]], [[5-Layer Compaction]], [[Deny-First Permission Model]], [[concepts/_index]], [[index]], [[hot]]
- Key insight: CLAUDE.md is user context (probabilistic), not system prompt (deterministic) — permission rules are the enforcement layer, not text instructions.


## [2026-06-05] ingest | Dive into Claude Code — Build Your Own Agent (arXiv 2604.14228)
- Source: `.raw/architechtai/doc_build-your-own-agent.md`
- Summary: [[Dive-into-Claude-Code-Build-Agent]]
- Pages created: [[Dive-into-Claude-Code-Build-Agent]], [[Agent Design Space Decisions]]
- Pages updated: [[Agent Harness Engineering]], [[Dive into Claude Code]], [[concepts/_index]], [[index]], [[hot]]
- Key insight: Top 3 frontier models are within 1% on SWE-bench — the harness is now the differentiator, not the model. Three meta-pattern commitments: graduated layering, append-only auditability, model-in-harness.


## [2026-06-05] ingest | Dive into Claude Code — Related Resources (arXiv 2604.14228)
- Source: `.raw/architechtai/doc_related-resources.md`
- Summary: [[Dive-into-Claude-Code-Related-Resources]]
- Pages created: [[Dive-into-Claude-Code-Related-Resources]], [[Claude Code Ecosystem Reference]]
- Pages updated: [[Agent Harness Engineering]], [[Dive into Claude Code]], [[index]], [[hot]]
- Key insight: claw-code hit 179K stars in 9 days (fastest to 100K in GitHub history) — the community appetite for harness-level understanding is real. "The moat is the harness, not the model" independently confirmed by post-leak analysts.

