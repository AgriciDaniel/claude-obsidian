---
type: meta
title: "Wiki Index"
updated: 2026-04-07
tags:
  - meta
  - index
status: evergreen
related:
  - "[[overview]]"
  - "[[log]]"
  - "[[hot]]"
  - "[[dashboard]]"
  - "[[Wiki Map]]"
  - "[[concepts/_index]]"
  - "[[entities/_index]]"
  - "[[sources/_index]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Hot Cache]]"
  - "[[Compounding Knowledge]]"
  - "[[Andrej Karpathy]]"
---

# Wiki Index

Last updated: 2026-06-29 | Total pages: 52 + 13 (Mode D scaffold) + 87 (SEC/EDGAR autoresearch, 10 passes) | Sources ingested: 8

Navigation: [[overview]] | [[log]] | [[hot]] | [[dashboard]] | [[Wiki Map]] | [[getting-started]]

---

## Concepts

- [[LLM Wiki Pattern]] — the pattern for building persistent, compounding knowledge bases using LLMs (status: mature)
- [[Hot Cache]] — ~500-word session context file, updated after every ingest and session (status: mature)
- [[Compounding Knowledge]] — why wiki knowledge grows more valuable over time, unlike RAG (status: mature)
- [[Agent Harness Engineering]] — 98.4% infrastructure / 1.6% AI; the harness is the differentiator; 6 production agent design decisions (status: developing)
- [[queryLoop Architecture]] — Claude Code's single AsyncGenerator while-loop; 9-step turn pipeline; 5 stop conditions (status: developing)
- [[5-Layer Compaction]] — graduated context degradation pipeline; Budget Reduction → Snip → Microcompact → Context Collapse → Auto-Compact (status: developing)
- [[Deny-First Permission Model]] — 7 permission modes, 7 safety layers, broad deny always wins, never restore on resume (status: developing)
- [[Claude Code Extensibility]] — 4 mechanisms × 3 injection points; graduated context cost from zero (hooks) to high (MCP) (status: developing)
- [[Subagent Delegation Architecture]] — SkillTool vs AgentTool; 3 isolation modes; sidechain transcripts via flock() (status: developing)
- [[CLAUDE.md Hierarchy]] — 4 levels; user context not system prompt; 9 ordered context sources (status: developing)
- [[Agent Design Space Decisions]] — 6 decisions with alternatives; SWE-bench convergence argument; 3 meta-pattern commitments (status: developing)
- [[Claude Code Ecosystem Reference]] — community repos, blog posts, 8 academic papers; "moat is the harness" independent validation (status: current)
- [[cherry-picks]] — prioritized feature backlog from ecosystem research; 13 features to add to claude-obsidian (status: current)
- [[SVG Diagram Style Guide]] — canonical visual style for all diagrams: Space Grotesk, #0A0A0A dark theme, #E07850 accent, full design tokens (status: evergreen)
- [[Pro Hub Challenge]] — community challenge pattern for building claude-seo/claude-blog extensions; first challenge produced 6 submissions, 5 integrated in v1.9.0 (status: evergreen)
- [[Semantic Topic Clustering]] — SERP-based keyword grouping replacing paid tools; hub-spoke architecture with interactive visualization (status: evergreen)
- [[Search Experience Optimization]] — "read SERPs backwards" methodology for page-type mismatch detection and persona scoring (status: evergreen)
- [[SEO Drift Monitoring]] — "git for SEO" baseline/diff/track with 17 comparison rules and SQLite persistence (status: evergreen)
- [[DragonScale Memory]] — memory-layer spec inspired by the Heighway dragon curve; fold operator, deterministic page addresses, semantic tiling, boundary-first autoresearch (status: shipped v0.4, all four mechanisms opt-in)
- [[Persistent Wiki Artifact]]: durable Markdown page as the LLM's memory object, distinct from ephemeral chat turns (status: developing)
- [[Source-First Synthesis]]: provenance discipline; raw sources stay immutable while the wiki layer is synthesized and cited (status: developing)
- [[Query-Time Retrieval]]: wiki query path synthesizes with citations; complementary to Obsidian's in-vault search (status: developing)
- [[EDGAR]] - the SEC's electronic system for collecting and publishing mandatory corporate filings (status: developing)
- [[EDGAR Next]] - 2024-25 modernization of EDGAR filer access: Login.gov + MFA, role-based admins (status: developing)
- [[SEC Filing Types]] - the standardized forms (10-K, 10-Q, 8-K, S-1, 13D/G, Forms 3/4/5) (status: developing)
- [[EDGAR APIs]] - public data.sec.gov JSON endpoints + full-text search; no API key required (status: developing)
- [[Federal Securities Laws]] - the statutes the SEC administers (1933 Act through JOBS Act 2012) (status: developing)
- [[Regulation Crowdfunding]] - Reg CF: $5M public raises via registered intermediaries; Title III JOBS Act (status: developing)
- [[Funding Portal]] - FINRA-member Reg CF intermediary; lighter-weight than a broker-dealer (status: developing)
- [[Form C]] - the Reg CF offering statement + C-AR annual report, filed on EDGAR (status: developing)
- [[XBRL]] - structured-data tagging standard (inline XBRL) for EDGAR financial filings; FASB US GAAP taxonomy (status: developing)
- [[Financial Data Transparency Act]] - 2022 law mandating uniform machine-readable data across nine financial regulators (status: developing)
- [[SEC Cybersecurity Disclosure Rules]] - 8-K Item 1.05 (4-business-day incident disclosure) + Reg S-K Item 106 (status: developing)
- [[SEC Climate Disclosure Rule]] - adopted 2024, stayed, rescission proposed 2026 (status: developing)
- [[T+1 Settlement Cycle]] - one-business-day settlement (Rule 15c6-1), effective May 2024 (status: developing)
- [[Recent SEC Rulemaking and Litigation 2023-2026]] - roundup: which rules took effect vs were vacated/stayed (status: developing)
- [[Exempt Offerings]] - the menu of Securities Act registration exemptions (Reg D / A / CF / 4(a)(2)) (status: developing)
- [[Regulation D]] - Rule 506(b)/506(c) private placements; the most-used exemption; Form D (status: developing)
- [[Regulation A]] - "mini-IPO"; Tier 1 ($20M) / Tier 2 ($75M); Form 1-A (status: developing)
- [[Accredited Investor]] - income/net-worth thresholds + Series 7/65/82 credential path (2020) (status: developing)
- [[Rule 144]] - resale of restricted/control securities; holding periods + affiliate limits (status: developing)
- [[Regulation S-K]] - narrative/non-financial disclosure rulebook (business, risk factors, MD&A Item 303) (status: developing)
- [[Regulation S-X]] - financial-statement form and content (17 CFR Part 210) (status: developing)
- [[Integrated Disclosure System]] - 1982 architecture unifying S-K, S-X, and the forms (status: developing)
- [[SEC Divisions and Structure]] - the five divisions (Corp Fin, Enforcement, Trading & Markets, IM, DERA) (status: developing)
- [[SEC Enforcement Process]] - investigation, Wells notice/submission, admin vs federal-court action (status: developing)
- [[SEC Whistleblower Program]] - Dodd-Frank bounty: 10-30% of >$1M sanctions (status: developing)
- [[EDGAR Data Access]] - CIK, accession-number format, and the 10 req/s + User-Agent fair-access rules (status: developing)
- [[EDGAR Bulk Data]] - Financial Statement Data Sets (SUB/NUM/TAG/PRE), full-index, DERA library (status: developing)
- [[Proxy Statement]] - DEF 14A / Schedule 14A under Section 14(a); director elections, auditor, say-on-pay (status: developing)
- [[Universal Proxy]] - Rule 14a-19; one card lists all sides' nominees in a contested election (status: developing)
- [[Rule 14a-8 Shareholder Proposals]] - getting a shareholder proposal into the company proxy (status: developing)
- [[Williams Act]] - 1968 takeover law; Sections 13(d)/14(d)/14(e) (status: developing)
- [[Tender Offer]] - Schedule TO / 14D-9; 20-day rule, all-holders/best-price; 2026 10-day order (status: developing)

---

## Entities

- [[Andrej Karpathy]] — AI researcher, creator of the LLM Wiki pattern, former Tesla AI director (status: developing)
- [[VILA-Lab]] — research group behind "Dive into Claude Code" (arXiv 2604.14228) (status: developing)
- [[Dive into Claude Code]] — paper; source-level analysis of Claude Code v2.1.88; codifies Agent Harness Engineering as a discipline (status: current)
- [[Ar9av-obsidian-wiki]] — multi-agent compatible LLM Wiki plugin; delta tracking manifest (status: current)
- [[Nexus-claudesidian-mcp]] — native Obsidian plugin + MCP bridge; workspace memory, task management (status: current)
- [[ballred-obsidian-claude-pkm]] — goal cascade PKM; auto-commit hooks, /adopt command (status: current)
- [[rvk7895-llm-knowledge-bases]] — 3-depth query system, Marp slides, parallel deep research (status: current)
- [[kepano-obsidian-skills]] — official skills from Obsidian creator; defuddle, obsidian-bases (status: current)
- [[Claudian-YishenTu]] — native Obsidian plugin embedding Claude Code; plan mode, @mention (status: current)
- [[Claude SEO]] — Tier 4 Claude Code skill for SEO analysis; 23 skills, 17 agents, 30 scripts at v1.9.0 (status: evergreen)
- [[U.S. Securities and Exchange Commission]] - US federal securities regulator; operates EDGAR (status: developing)
- [[Financial Industry Regulatory Authority]] - FINRA; SRO overseeing broker-dealers and funding portals (status: developing)
- [[Wefunder]] - largest Reg CF funding portal (~33% of 2025 dollars) (status: developing)
- [[StartEngine]] - second-largest Reg CF portal; full-stack (primary + secondary + funds) (status: developing)
- [[Republic (crowdfunding)]] - accredited-leaning Reg CF platform; multi-asset private markets (status: developing)
- [[Financial Accounting Standards Board]] - FASB; sets US GAAP and maintains the XBRL US GAAP taxonomy (status: developing)

---

## Sources

- [[claude-obsidian-ecosystem-research]] — 2026-04-08 | web research across 16+ repos | 8 wiki pages created
- [[Dive-into-Claude-Code-README]] — 2026-06-05 | VILA-Lab arXiv 2604.14228 | Claude Code v2.1.88 architecture overview
- [[Dive-into-Claude-Code-Architecture]] — 2026-06-05 | VILA-Lab arXiv 2604.14228 | 7-component system, 5-layer subsystems, extensibility, subagents, session persistence
- [[Dive-into-Claude-Code-Build-Agent]] — 2026-06-05 | VILA-Lab arXiv 2604.14228 | 6 design decisions, alternatives, 3 meta-pattern commitments
- [[Dive-into-Claude-Code-Related-Resources]] — 2026-06-05 | VILA-Lab arXiv 2604.14228 | community analysis, reimplementations, blog posts, academic papers
- _SEC/EDGAR cluster (2026-06-29):_ [[SEC.gov - About EDGAR]], [[SEC.gov - Transition to EDGAR Next]], [[SEC.gov - EDGAR APIs]], [[investor.gov - Laws That Govern the Securities Industry]], [[Wikipedia - EDGAR]], [[Wikipedia - Securities Exchange Act of 1934]], [[sec-api.io - Full-Text Search API Docs]], [[edgar.tools - SEC Filing Types Explained]], [[Nuvo Group - EDGAR Next Transition]]
- _Reg CF / funding portals cluster (2026-06-29):_ [[SEC.gov - Regulation Crowdfunding]], [[SEC.gov - Registration of Funding Portals]], [[SEC.gov - Staff Guidance on EDGAR Filing of Form C]], [[FINRA - Funding Portals]], [[MicroVentures - Funding Portals vs Broker-Dealers]], [[crowdfundingattorney.com - 2026 Reg CF Guidance]], [[Angel Investors Network - Reg CF Platform Comparison]]
- _XBRL / structured data cluster (2026-06-29):_ [[SEC.gov - Inline XBRL]], [[SEC.gov - FDTA Joint Data Standards]], [[Covington - FDTA Implementation]], [[IRIS Carbon - 10 Years of SEC iXBRL Timeline]], [[Cooley - SEC Adopts Mandatory Inline XBRL]]
- _Recent rulemaking cluster (2026-06-29):_ [[SEC.gov - Cybersecurity Disclosure Rules Press Release]], [[SEC.gov - Proposes Rescission of Climate Rules]], [[DLA Piper - SEC Climate Rule Litigation Update]], [[Orrick - Fifth Circuit Vacates Share Repurchase Rules]], [[Davis Polk - SEC Adopts T+1 Settlement]]
- _Exemptions cluster (2026-06-29):_ [[SEC.gov - Private Placements Rule 506]], [[SEC.gov - Regulation A]], [[SEC.gov - Accredited Investor Definition Amendments]], [[SEC.gov - Rule 144]], [[Carta - 506(b) vs 506(c) Guide]]
- _Reg S-K / S-X cluster (2026-06-29):_ [[Cornell LII - Regulation S-K]], [[Cornell LII - Regulation S-X]], [[CFO Bridge - Regulation S-X vs S-K]]
- _Enforcement & structure cluster (2026-06-29):_ [[SEC.gov - Organizational Chart]], [[Winston & Strawn - SEC Investigations Primer]], [[Wikipedia - SEC Office of the Whistleblower]]
- _EDGAR data access cluster (2026-06-29):_ [[SEC.gov - Accessing EDGAR Data]], [[SEC.gov - Financial Statement Data Sets]], [[SEC.gov - New Rate Control Limits]]
- _Proxy cluster (2026-06-29, SEC primaries fetched directly):_ [[SEC.gov - Universal Proxy]], [[SEC.gov - Proxy Rules and Schedules 14A 14C]], [[Cornell LII - Schedule 14A (Rule 14a-101)]], [[Debevoise - Shareholder Proposals under Rule 14a-8]]
- _Takeovers cluster (2026-06-29, SEC primary fetched directly):_ [[SEC.gov - Tender Offer Rules and Schedules]], [[Ropes & Gray - SEC Cuts Minimum Tender Offer Period]], [[US Law Explained - The Williams Act]]

---

## Questions

- [[How does the LLM Wiki pattern work]] — how the pattern works and why it outperforms RAG at human scale (status: developing)
- [[Research - SEC regulations and EDGAR]] - autoresearch synthesis: laws, EDGAR, filing types, EDGAR Next, APIs (status: developing)

---

## Comparisons

- [[Wiki vs RAG]] — when to use a wiki knowledge base versus RAG; verdict: wiki wins at <1000 pages
- [[claude-obsidian-ecosystem]] — feature matrix of 16+ Claude+Obsidian projects; where claude-obsidian wins and gaps

---

## Decisions

- [[2026-04-14-community-cta-rollout]] - Skool community CTA footer added to 6 skill repos with per-tool frequency rules (status: active)
- [[2026-04-15-slides-and-release-session]] - Claude SEO v1.9.0 slides (15-slide HTML deck) + GitHub release v1.9.0 with PDF asset (status: complete)
- [[2026-04-15-release-report-session]] - Claude SEO v1.9.0 Release Report PDF: dark theme, 13 pages, WeasyPrint layout fixes, Challenge v2 added (status: complete)
- [[2026-04-14-claude-seo-v190-session]] - Claude SEO v1.9.0 Pro Hub Challenge integration: 5 submissions, 4 new skills, 4 review rounds, cybersecurity audit (status: complete)

---

## Domains

<!-- Add domain entries here after scaffold -->

---

## Second Brain (Mode D)

_Added 2026-06-04. Personal life OS layer — goals, learning, people, areas, resources._

### Goals
- [[North Star]] — one-sentence direction; anchor for everything else
- [[Annual Goals]] — 2026 goals table with quarterly focus
- [[Weekly Review Template]] — copy and fill each week

### Areas
- [[areas/_index]] → [[Health]] | [[Career]] | [[Finances]] | [[Creative]]

### Learning
- [[learning/_index]] — concepts being mastered; skills in development

### People
- [[people/_index]] — relationships, shared context, follow-ups

### Resources
- [[resources/_index]] — books, courses, tools, articles worth keeping
