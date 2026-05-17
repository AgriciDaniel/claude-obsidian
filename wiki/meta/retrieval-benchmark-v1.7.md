---
type: meta
title: "v1.7 Retrieval Benchmark Corpus"
status: evergreen
updated: 2026-05-17
---

# v1.7 Retrieval Benchmark — 50 Queries

Used by the v1.7.0 audit (`docs/audits/v1.7.0-audit-2026-05-17.md`) to score
top-1 / top-5 accuracy of the hybrid retrieval pipeline (`scripts/retrieve.py`)
vs. the simulated v1.6 baseline (`scripts/baseline-v16.py`).

## Schema

Each query: `id`, `query`, `correct` (canonical page paths), `relevant`
(supporting paths), `category`, `rationale`. For negative queries, `correct`
is `null` and success is defined as "returns nothing OR returns only pages
in `relevant`."

Machine-parsable: every query block is bracketed by `### <id>` and ends
before the next `### ` or `## `. The scoring runner at
`scripts/benchmark-runner.py` reads this file directly.

## Scoring rules

- **top-1 success**: top result's `page_path` equals one of `correct[]`
- **top-5 success**: any of top-5 results' `page_path` is in `correct[]`
- For negative queries (correct=null): top-1 success if top result in `relevant[]` or no results; top-5 success if any top-5 in `relevant[]` or no results

Final scores reported as (top-1%, top-5%) per pipeline, broken down by category.

---

## Derived Queries (25)

### D1
- query: How does knowledge compound differently in a wiki versus traditional RAG?
- correct: wiki/concepts/Compounding Knowledge.md
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/comparisons/Wiki vs RAG.md
- category: derived
- rationale: Canonical treatment of why wiki accumulation produces more value over time vs. query-time re-derivation.

### D2
- query: What is the Hot Cache and why would a user enable it in their session?
- correct: wiki/concepts/Hot Cache.md
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/getting-started.md
- category: derived
- rationale: Direct explanation of the session context mechanism and its token-cost benefits.

### D3
- query: Tell me the three-layer architecture behind the LLM Wiki pattern.
- correct: wiki/concepts/LLM Wiki Pattern.md
- relevant: wiki/overview.md, wiki/index.md
- category: derived
- rationale: Explicit description of .raw, wiki, and CLAUDE.md layers.

### D4
- query: What does the wiki fold operator do and why use exponential batch sizes?
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md, wiki/hot.md
- category: derived
- rationale: Mechanism 1 detailed explanation with 2^k justification and LSM analogy.

### D5
- query: How are deterministic page addresses assigned and what format do they use?
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md
- category: derived
- rationale: Mechanism 2 spec with c-NNNNNN format and counter recovery rules.

### D6
- query: Explain semantic tiling lint and what cosine similarity threshold it uses.
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md, wiki/hot.md
- category: derived
- rationale: Mechanism 3 detailed treatment including banded thresholds and embeddings.

### D7
- query: What are the cherry-picked features claude-obsidian should implement next?
- correct: wiki/concepts/cherry-picks.md
- relevant: wiki/index.md, wiki/comparisons/claude-obsidian-ecosystem.md
- category: derived
- rationale: Explicit prioritized backlog from ecosystem research across tiers.

### D8
- query: What is the relationship between SVG diagrams and brand tokens in claude-obsidian assets?
- correct: wiki/concepts/SVG Diagram Style Guide.md
- relevant: wiki/log.md
- category: derived
- rationale: Canonical style reference with color palette, typography, and layout tokens.

### D9
- query: How does a user ingest a source document into claude-obsidian and what happens next?
- correct: wiki/getting-started.md
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/overview.md
- category: derived
- rationale: Three-step quick start walkthrough with expected output pages.

### D10
- query: What does the Pro Hub Challenge reward and what was the first winner?
- correct: wiki/concepts/Pro Hub Challenge.md
- relevant: wiki/entities/Claude SEO.md, wiki/log.md
- category: derived
- rationale: Community challenge structure and integration pattern with historical results.

### D11
- query: What is Search Experience Optimization and how does it read SERPs backwards?
- correct: wiki/concepts/Search Experience Optimization.md
- relevant: wiki/entities/Claude SEO.md, wiki/concepts/Semantic Topic Clustering.md
- category: derived
- rationale: Direct explanation of SXO methodology and its page-type mismatch detection.

### D12
- query: How does semantic topic clustering use overlapping URLs to detect content relationships?
- correct: wiki/concepts/Semantic Topic Clustering.md
- relevant: wiki/entities/Claude SEO.md, wiki/log.md
- category: derived
- rationale: Overlap scoring rules and hub-spoke architecture.

### D13
- query: What tracking rules does SEO Drift Monitoring enforce and where is the baseline stored?
- correct: wiki/concepts/SEO Drift Monitoring.md
- relevant: wiki/entities/Claude SEO.md
- category: derived
- rationale: 17 comparison rules across severity levels and SQLite persistence location.

### D14
- query: Who is Andrej Karpathy and why does he matter to this wiki project?
- correct: wiki/entities/Andrej Karpathy.md
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/index.md
- category: derived
- rationale: Founder attribution and origination of the pattern with notable quote.

### D15
- query: What version of Claude SEO shipped in April 2026 and how many skills does it have?
- correct: wiki/entities/Claude SEO.md
- relevant: wiki/log.md, wiki/meta/2026-04-14-claude-seo-v190-session.md
- category: derived
- rationale: v1.9.0 state with skill counts and Pro Hub Challenge integration.

### D16
- query: Does Ar9av's obsidian-wiki support multi-agent deployment and how?
- correct: wiki/entities/Ar9av-obsidian-wiki.md
- relevant: wiki/comparisons/claude-obsidian-ecosystem.md, wiki/concepts/cherry-picks.md
- category: derived
- rationale: setup.sh bootstrap matrix across multiple agents and delta tracking manifest.

### D17
- query: What does the /adopt command in ballred's PKM system do?
- correct: wiki/entities/ballred-obsidian-claude-pkm.md
- relevant: wiki/concepts/cherry-picks.md, wiki/comparisons/claude-obsidian-ecosystem.md
- category: derived
- rationale: Vault analysis and pattern detection for PARA, Zettelkasten, LYT migration.

### D18
- query: What official Obsidian skills does kepano publish and which is most token-efficient?
- correct: wiki/entities/kepano-obsidian-skills.md
- relevant: wiki/concepts/cherry-picks.md, wiki/entities/Claudian-YishenTu.md
- category: derived
- rationale: obsidian-markdown, obsidian-bases, defuddle, and defuddle's 40-60% token reduction.

### D19
- query: What are the three query depths in rvk7895's LLM knowledge base system?
- correct: wiki/entities/rvk7895-llm-knowledge-bases.md
- relevant: wiki/concepts/cherry-picks.md, wiki/comparisons/claude-obsidian-ecosystem.md
- category: derived
- rationale: Quick, Standard, Deep modes with output formats.

### D20
- query: How does Nexus MCP for Obsidian store workspace memory and is it Obsidian Sync compatible?
- correct: wiki/entities/Nexus-claudesidian-mcp.md
- relevant: wiki/comparisons/claude-obsidian-ecosystem.md
- category: derived
- rationale: JSONL storage and Sync auto-inclusion.

### D21
- query: What makes Claudian's inline edit feature best-in-class compared to other Obsidian AI plugins?
- correct: wiki/entities/Claudian-YishenTu.md
- relevant: wiki/comparisons/claude-obsidian-ecosystem.md
- category: derived
- rationale: Word-level diff preview and one-click apply with Plan Mode support.

### D22
- query: Between claude-obsidian and other projects, who has the hot cache mechanism?
- correct: wiki/comparisons/claude-obsidian-ecosystem.md
- relevant: wiki/concepts/Hot Cache.md, wiki/index.md
- category: derived
- rationale: Feature matrix shows claude-obsidian is unique in session context caching.

### D23
- query: When was the first real fold committed to the vault and what was its fold_id?
- correct: wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md
- relevant: wiki/log.md, wiki/hot.md, wiki/concepts/DragonScale Memory.md
- category: derived
- rationale: Fold metadata with exact creation date and 8-entry batch documentation.

### D24
- query: What pages were created after the boundary-first autoresearch frontier pass?
- correct: wiki/log.md
- relevant: wiki/concepts/Persistent Wiki Artifact.md, wiki/concepts/Source-First Synthesis.md, wiki/concepts/Query-Time Retrieval.md
- category: derived
- rationale: Log entry for 2026-04-24 M4 run explicitly lists the three new concept pages filed.

### D25
- query: What is a Persistent Wiki Artifact and how does it differ from ephemeral chat turns?
- correct: wiki/concepts/Persistent Wiki Artifact.md
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/concepts/Source-First Synthesis.md
- category: derived
- rationale: Explicit definition of durable memory object with frontmatter, title, wikilinks, and provenance.

---

## Hard Queries (25)

### H1
- query: How does the exponential compaction operator summarize batch entries?
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md
- category: synonym
- rationale: "Fold operator" and "rollup" are interchangeable; query uses LSM terminology instead of dragon-curve naming.

### H2
- query: What stable identifiers help page references survive renames in prompt-cache workloads?
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md, wiki/hot.md
- category: synonym
- rationale: Deterministic addresses (c-NNNNNN format) are the answer; query uses prompt-cache context instead.

### H3
- query: How does the semantic tiling mechanism detect and flag duplicate or near-duplicate pages?
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md, wiki/hot.md
- category: synonym
- rationale: Mechanism 3 performs dedup via cosine similarity; query uses "near-duplicate" instead of "semantic tiling."

### H4
- query: When user asks /autoresearch without a topic, which pages are candidates and how are they scored?
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md, wiki/hot.md
- category: synonym
- rationale: Boundary-first autoresearch (Mechanism 4) surfaces frontier pages; query uses "autoresearch no-topic" instead.

### H5
- query: How should the wiki layer stay connected to raw source material without replacing source content?
- correct: wiki/concepts/Source-First Synthesis.md
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/concepts/Persistent Wiki Artifact.md
- category: synonym
- rationale: Source-first synthesis is the provenance rule; query asks for the principle without using the term.

### H6
- query: When building a wiki versus RAG, how does the cost structure differ in maintenance, infrastructure, and long-term knowledge value?
- correct: wiki/concepts/LLM Wiki Pattern.md, wiki/comparisons/Wiki vs RAG.md, wiki/concepts/Compounding Knowledge.md
- relevant: wiki/overview.md
- category: cross-page
- rationale: Spans three concepts: architecture table, comparison table, and compounding mechanics.

### H7
- query: What does the wiki-fold skill output in dry-run mode and how does it create child references?
- correct: wiki/concepts/DragonScale Memory.md, wiki/log.md
- relevant: wiki/hot.md
- category: cross-page
- rationale: Mechanism 1 spec + dry-run artifact from 2026-04-24 Phase 1 log entry cross-reference.

### H8
- query: How would adding URL ingestion and web cleaning together reduce token usage during ingest?
- correct: wiki/concepts/cherry-picks.md, wiki/entities/kepano-obsidian-skills.md
- relevant: wiki/getting-started.md
- category: cross-page
- rationale: Combining cherry-pick #1 (URL ingest) and defuddle (40-60% token reduction) from two sources.

### H9
- query: Which project has the best auto-commit hook and how did that feature get integrated into Claude SEO?
- correct: wiki/entities/ballred-obsidian-claude-pkm.md, wiki/entities/Claude SEO.md, wiki/log.md
- relevant: wiki/comparisons/claude-obsidian-ecosystem.md
- category: cross-page
- rationale: ballred has PostToolUse auto-commit; Claude SEO v1.9.0 release cites integration patterns.

### H10
- query: How would you audit a page for SERP alignment, topic cannibalization risk, and performance regressions together?
- correct: wiki/concepts/Search Experience Optimization.md, wiki/concepts/Semantic Topic Clustering.md, wiki/concepts/SEO Drift Monitoring.md
- relevant: wiki/entities/Claude SEO.md, wiki/log.md
- category: cross-page
- rationale: Three separate v1.9.0 features; query asks for integrated workflow across all three.

### H11
- query: What were the six test stages and did all mechanisms pass validation before v1.6.0 shipped?
- correct: wiki/log.md, wiki/hot.md
- relevant: wiki/concepts/DragonScale Memory.md
- category: cross-page
- rationale: 2026-04-24 end-to-end validation pass entry lists T0-T6; hot.md confirms all four mechanisms validated.

### H12
- query: Why does the LLM Wiki pattern avoid re-querying and re-assembling the same sources every time?
- correct: wiki/concepts/Query-Time Retrieval.md, wiki/concepts/Persistent Wiki Artifact.md, wiki/concepts/Source-First Synthesis.md
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/concepts/Compounding Knowledge.md
- category: cross-page
- rationale: Spans three pages: RAG baseline definition + durable memory object + synthesis discipline.

### H13
- query: What are two independent ways to embed the LLM Wiki pattern in different editor environments?
- correct: wiki/entities/Ar9av-obsidian-wiki.md, wiki/entities/Claudian-YishenTu.md
- relevant: wiki/comparisons/claude-obsidian-ecosystem.md
- category: cross-page
- rationale: Ar9av setup.sh for multiple agents; Claudian native TypeScript plugin; both different deployment models.

### H14
- query: How could you avoid re-processing unchanged sources when integrating community submissions?
- correct: wiki/concepts/cherry-picks.md, wiki/concepts/Pro Hub Challenge.md
- relevant: wiki/log.md
- category: cross-page
- rationale: Delta tracking manifest solves re-ingest problem; integration pattern in Pro Hub workflow.

### H15
- query: What is the most direct way to add defuddle to claude-obsidian's current ingest pipeline?
- correct: wiki/entities/kepano-obsidian-skills.md, wiki/concepts/cherry-picks.md
- relevant: wiki/getting-started.md
- category: cross-page
- rationale: Cherry-pick #3 + getting-started ingest flow both discussed; requires both for full picture.

### H16
- query: Where can I find Karpathy's original description of the wiki pattern?
- correct: wiki/concepts/Persistent Wiki Artifact.md, wiki/concepts/Source-First Synthesis.md, wiki/entities/Andrej Karpathy.md
- relevant: wiki/concepts/LLM Wiki Pattern.md
- category: partial-recall
- rationale: Multiple pages cite Karpathy gist; user remembers "gist" + "Karpathy."

### H17
- query: What was inspired by dragon curves and what problem does it solve?
- correct: wiki/concepts/DragonScale Memory.md
- relevant: wiki/log.md
- category: partial-recall
- rationale: User recalls dragon analogy but not "DragonScale"; wants to understand fold operator.

### H18
- query: What is the ~500-word file that gets updated at the end of every session?
- correct: wiki/concepts/Hot Cache.md
- relevant: wiki/getting-started.md, wiki/overview.md, wiki/hot.md
- category: partial-recall
- rationale: Exact description matches; user remembers fragment but not exact terminology.

### H19
- query: Which community competition paid out Claude Credits and who won first?
- correct: wiki/concepts/Pro Hub Challenge.md
- relevant: wiki/entities/Claude SEO.md
- category: partial-recall
- rationale: User remembers community challenge and winners but not the name.

### H20
- query: How many projects does the wiki track as competitors or adjacent to claude-obsidian?
- correct: wiki/comparisons/claude-obsidian-ecosystem.md
- relevant: wiki/concepts/cherry-picks.md
- category: partial-recall
- rationale: User remembers ecosystem matrix but not exact page; queries for count of projects.

### H21
- query: How does the wiki pattern use blockchain or distributed ledger technology for vault consensus?
- correct: null
- relevant: wiki/concepts/DragonScale Memory.md
- category: negative
- rationale: Wiki does not discuss blockchain; DragonScale addresses are creation-order counter, not DLT.

### H22
- query: What CRDT algorithm does the vault use for simultaneous multi-user editing?
- correct: null
- relevant: wiki/hot.md, wiki/concepts/DragonScale Memory.md
- category: negative
- rationale: No CRDT discussion; v1.7 mentions wiki-lock.sh for multi-writer safety (locking, not CRDTs).

### H23
- query: Can I build an LLM wiki without installing Obsidian as a desktop application?
- correct: null
- relevant: wiki/concepts/LLM Wiki Pattern.md, wiki/getting-started.md
- category: negative
- rationale: Pattern is agnostic but this vault uses Obsidian. No Obsidian-free mode documented.

### H24
- query: How do you customize the semantic embedding model weights for better tiling accuracy on your domain?
- correct: null
- relevant: wiki/concepts/DragonScale Memory.md, wiki/log.md
- category: negative
- rationale: Mechanism 3 uses locked ollama nomic-embed-text; no fine-tuning support documented.

### H25
- query: Does the vault have CI/CD pipeline to automatically ingest new .raw files on every push?
- correct: null
- relevant: wiki/log.md, wiki/hot.md
- category: negative
- rationale: No GitHub Actions / CI-CD / automated ingest documented. Auto-commit hook exists but not scheduled CI.

---

## Benchmark Notes

**Coverage**: 47 wiki pages, ~50 queries → roughly 1 query per page on average; spread covers concepts, entities, comparisons, meta, folds, sources.

**Balance**: 25 derived (natural questions) + 5 synonym + 10 cross-page + 5 partial-recall + 5 negative.

**Targets** (rough expectation, not a gate):
- v1.6 baseline top-1: ~50-65% on derived, much lower on hard
- v1.7 hybrid top-1: ~75-90% on derived, ~50-70% on hard
- Plan §7 ship gate (from v1.7 implementation plan): ≥30% reduction in "wrong page cited" errors. Verify by comparing the percentage-points improvement on top-1 across all 50 queries.
