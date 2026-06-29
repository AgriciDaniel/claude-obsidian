---
type: synthesis
title: "Research: SEC regulations and EDGAR"
created: 2026-06-29
updated: 2026-06-29
tags:
  - research
  - securities
  - sec
  - edgar
  - regulation
status: developing
related:
  - "[[U.S. Securities and Exchange Commission]]"
  - "[[EDGAR]]"
  - "[[EDGAR Next]]"
  - "[[SEC Filing Types]]"
  - "[[EDGAR APIs]]"
  - "[[Federal Securities Laws]]"
  - "[[index]]"
sources:
  - "[[SEC.gov - About EDGAR]]"
  - "[[SEC.gov - Transition to EDGAR Next]]"
  - "[[SEC.gov - EDGAR APIs]]"
  - "[[investor.gov - Laws That Govern the Securities Industry]]"
  - "[[Wikipedia - EDGAR]]"
  - "[[Wikipedia - Securities Exchange Act of 1934]]"
  - "[[sec-api.io - Full-Text Search API Docs]]"
  - "[[edgar.tools - SEC Filing Types Explained]]"
  - "[[Nuvo Group - EDGAR Next Transition]]"
---

# Research: SEC regulations and EDGAR

## Overview

U.S. securities regulation rests on a **mandatory-disclosure** model: the [[U.S. Securities and Exchange Commission|SEC]] requires public companies to file standardized information, and [[EDGAR]] is the electronic pipe through which those filings are submitted and published. The legal obligations come from the [[Federal Securities Laws]] (1933 Act onward); [[SEC Filing Types]] are the instruments; [[EDGAR APIs]] expose the data; and [[EDGAR Next]] is the 2025 modernization of how filers authenticate.

## Key Findings

- The system splits cleanly by market stage: the **Securities Act of 1933** governs primary-market offerings (register before you sell), while the **Securities Exchange Act of 1934** created the SEC and governs ongoing secondary-market reporting. (Source: [[Federal Securities Laws]])
- **EDGAR** automates collection, validation, indexing, and public dissemination of filings; it accepts HTML, ASCII, XML, and XBRL, runs 6am–10pm ET on weekdays, and is free to the public. It holds 17M+ filings and processes thousands per day. (Source: [[EDGAR]])
- The principal periodic forms are the **10-K** (audited annual), **10-Q** (unaudited quarterly), and **8-K** (material events within 4 business days); **S-1** registers a public offering. (Source: [[SEC Filing Types]])
- **EDGAR Next** (final rule Dec 27, 2024) is the biggest filer-access overhaul in 20+ years: Login.gov + multi-factor authentication, no shared credentials, and at least two account administrators per filer. Compliance was required by **Sept 15, 2025**. (Source: [[EDGAR Next]])
- EDGAR data is programmatically accessible via `data.sec.gov` JSON APIs (submissions, company facts/concept/frames) and a full-text search covering filings since 2001, indexed in under 60 seconds - **no API key required**, but a declared User-Agent and rate limits apply. (Source: [[EDGAR APIs]])

## Reg CF / Crowdfunding Funding Portals (Pass 2)

- **[[Regulation Crowdfunding]]** (Title III of the JOBS Act, effective 2016) lets private companies raise up to **$5M/12 months** from the public, including non-accredited investors. (Source: [[SEC.gov - Regulation Crowdfunding]])
- Every Reg CF raise must run through a registered **[[Funding Portal]]** or broker-dealer. A funding portal is a FINRA-member intermediary that **cannot** give advice, solicit, hold investor funds, or take transaction-based pay - a lighter-weight model than a broker-dealer. (Source: [[Funding Portal]])
- Portals register on **Form Funding Portal via [[EDGAR]]** and join **[[Financial Industry Regulatory Authority|FINRA]]**; FINRA runs the Funding Portal Registration Depository and the Funding Portal Rules. **83 portals** were registered as of end-2024. (Source: [[FINRA - Funding Portals]])
- Issuers file **[[Form C]]** before the raise and **Form C-AR** annually (within 120 days of FY-end) on EDGAR. (Source: [[Form C]])
- Market is concentrated: 2025 Reg CF dollars led by **[[Wefunder]]** (~$109M, ~33%), **[[StartEngine]]** (~$89M, ~24%), DealMaker (~$66M), **[[Republic (crowdfunding)|Republic]]** (~$20M). (Source: [[Angel Investors Network - Reg CF Platform Comparison]])

## XBRL & Structured Data (Pass 3)

- **[[XBRL]]** (eXtensible Business Reporting Language) is the structured-data standard for financial info in EDGAR filings: each figure is tagged against the FASB **US GAAP taxonomy** (~17,000 tags) so filings are machine-readable. (Source: [[XBRL]])
- **Inline XBRL (iXBRL)** embeds tags directly in the HTML filing (one human- + machine-readable document). Adopted June 28, 2018; phased in by filer size FY-ends June 2019 -> June 2021. Required for cover page + financials in 10-K/10-Q and parts of 8-K/proxy. (Source: [[XBRL]])
- XBRL history: mandate began **2009** (large accelerated filers), all filers by **2012**; this XBRL data powers the [[EDGAR APIs]]. (Source: [[XBRL]])
- The **[[Financial Data Transparency Act]]** (FDTA, Dec 2022) extends machine-readable standards across **nine federal agencies** (incl. SEC, Treasury, Fed, FDIC, CFTC...). Adopts a common **LEI (ISO 17442)**; standardizes format without requiring new data collection. Proposed Aug 2024; final joint rule in 2026. (Source: [[Financial Data Transparency Act]])

## Recent Rulemaking 2023-2026 (Pass 4)

The era's rules split by type ([[Recent SEC Rulemaking and Litigation 2023-2026]]):

- **In effect:** [[SEC Cybersecurity Disclosure Rules]] (Jul 2023) - 8-K **Item 1.05** material-incident disclosure within **4 business days** + annual Reg S-K **Item 106** governance; and [[T+1 Settlement Cycle]] (Rule 15c6-1, effective **May 28, 2024**).
- **Vacated:** the share-repurchase ("buyback") disclosure rule (May 2023) was struck down by the **Fifth Circuit on Dec 19, 2023** as arbitrary and capricious under the APA. (Source: [[Orrick - Fifth Circuit Vacates Share Repurchase Rules]])
- **Stayed -> rescission proposed:** the [[SEC Climate Disclosure Rule]] (Mar 2024) was stayed Apr 2024, the SEC dropped its defense Mar 2025, and a **2026 rescission** is now proposed. (Source: [[SEC Climate Disclosure Rule]])
- Pattern: disclosure-expansion mandates drew successful APA / major-questions challenges; operational rules (T+1, cyber-incident) stuck.

## Private-Offering Exemptions (Pass 5)

The Securities Act requires registration unless an exemption applies ([[Exempt Offerings]]):

- **[[Regulation D]]** is the private workhorse. **Rule 506(b)**: no general solicitation, unlimited accredited + up to 35 sophisticated, self-verification. **Rule 506(c)**: general solicitation allowed but accredited-only with "reasonable steps to verify." Both file a **Form D** within 15 days of first sale. (Source: [[Regulation D]])
- **[[Regulation A]]** ("mini-IPO") is public-facing: **Tier 1 up to $20M**, **Tier 2 up to $75M** per 12 months, via **Form 1-A** qualified by the SEC; Tier 2 preempts state review. (Source: [[Regulation A]])
- **[[Accredited Investor]]**: income > $200k ($300k joint) or net worth > $1M (ex-residence); since Dec 2020, **Series 7/65/82** holders also qualify. (Source: [[Accredited Investor]])
- **[[Rule 144]]** is the resale exit: 6-month (reporting) / 1-year (non-reporting) holding period; affiliates also face a 1%-or-weekly-volume cap, manner-of-sale rules, and Form 144. (Source: [[Rule 144]])

## The Disclosure Rulebooks: S-K & S-X (Pass 6)

- The **[[Integrated Disclosure System]]** (1982) unified SEC disclosure: two content rulebooks feed standardized forms. (Source: [[Integrated Disclosure System]])
- **[[Regulation S-K]]** governs **narrative, non-financial** disclosure - business, risk factors, **MD&A (Item 303)**, executive compensation. (Source: [[Regulation S-K]])
- **[[Regulation S-X]]** (17 CFR Part 210) governs the **form and content of financial statements** - a technical rule working alongside US GAAP, including auditor independence, acquired-business financials (Rule 3-05), and significance tests (Rule 1-02(w)). (Source: [[Regulation S-X]])
- Mental model: **S-K = the words, S-X = the numbers, the forms = the containers.** The same S-K + S-X items populate both a registration statement (1933 Act) and periodic reports (1934 Act).

## Proxy Solicitation (Pass 9 — first pass using SEC primary sources directly)

- A **[[Proxy Statement]]** (DEF 14A, Schedule 14A) is required under **Section 14(a)** of the Exchange Act whenever a company solicits shareholder votes. The SEC defines a "solicitation" broadly: **any communication reasonably calculated to procure, withhold, or revoke a proxy**. (Source: [[SEC.gov - Proxy Rules and Schedules 14A 14C]], fetched directly)
- **Say-on-pay** is a Dodd-Frank **advisory** (non-binding) vote on executive compensation; the materials are still a Section 14(a) solicitation.
- **[[Universal Proxy]]** (Rule 14a-19, adopted Nov 2021, effective Jan 31 2022, applies to elections after Aug 31 2022): contested director elections must use one card listing **all nominees of all sides**. Dissidents must solicit **>=67%** of voting power and meet 60/50/25-day deadlines. (Source: [[SEC.gov - Universal Proxy]], fetched directly)
- **[[Rule 14a-8 Shareholder Proposals]]** is the separate path for putting a shareholder *proposal* (not a nominee) into the company proxy, subject to enumerated exclusion grounds and SEC no-action letters.

## Takeovers: The Williams Act & Tender Offers (Pass 10)

- The **[[Williams Act]]** (1968) regulates takeovers via three Exchange Act sections: **13(d)** (>5% ownership disclosure on Schedule 13D), **14(d)** (tender-offer procedure, Reg 14D), and **14(e)** (broad anti-fraud for "any tender offer," Reg 14E). Its four guarantees: adequate info, adequate time, equal treatment, withdrawal rights. (Source: [[Williams Act]])
- A **[[Tender Offer]]** runs through a **Schedule TO** (EDGAR tags SC TO-T / TO-I / TO-C); the target board responds on **Schedule 14D-9** within **10 business days**. Core rules: **20-business-day** minimum period, **withdrawal rights**, **all-holders** and **best-price** rules; **Rule 13e-4** covers issuer self-tenders and **Rule 13e-3** going-private deals. (Source: [[SEC.gov - Tender Offer Rules and Schedules]], fetched directly)
- **2026 change:** an April 16, 2026 SEC exemptive order **halves the minimum period to 10 business days** for negotiated all-cash equity offers. (Source: [[Tender Offer]])

## Key Entities

- [[U.S. Securities and Exchange Commission]]: the federal regulator that administers securities law and operates EDGAR.
- [[Financial Industry Regulatory Authority]]: SRO overseeing broker-dealers and funding portals under SEC supervision.
- [[Wefunder]], [[StartEngine]], [[Republic (crowdfunding)]]: the leading Reg CF funding portals.

## How the SEC Is Built & Enforces (Pass 7)

- The SEC has **five divisions**: Corporation Finance (disclosure review), Enforcement, Trading & Markets, Investment Management, and **DERA** (economics/risk, est. 2009). ([[SEC Divisions and Structure]])
- **[[SEC Enforcement Process]]:** investigation -> **Wells notice** -> Wells submission -> charge or close; actions run as **SEC administrative proceedings** or **federal-court civil suits**; most settle (recent reforms separate settlement from the Wells submission).
- **[[SEC Whistleblower Program]]** (Dodd-Frank 2010): pays **10-30%** of sanctions when collections exceed **$1M**, from the Investor Protection Fund, with anti-retaliation protection.

## Practical EDGAR Data Access (Pass 8)

- **[[EDGAR Data Access|CIK]]** (Central Index Key) is a permanent **10-digit** filer ID that never changes; it is the reliable key for tracking an entity across renames/ticker changes. **Accession numbers** encode `submitterCIK-YY-sequential`. (Source: [[EDGAR Data Access]])
- **Fair access:** a hard **10 requests/second** cap per IP and a required descriptive **User-Agent header**; violations return **HTTP 403** + ~10-minute block. **This is exactly why sec.gov returned 403 to this vault's automated fetches** - the standing "Open Question" on API limits is now closed. (Source: [[EDGAR Data Access]])
- **[[EDGAR Bulk Data]]:** for cross-company analysis, the SEC publishes **Financial Statement Data Sets** (XBRL extracts, tables SUB/NUM/TAG/PRE, since Apr 2009, monthly from Apr 2023), full-index files, and the DERA Data Library. (Source: [[EDGAR Bulk Data]])

## Key Concepts

- [[EDGAR]]: the SEC's electronic filing and dissemination system.
- [[EDGAR Next]]: 2024–2025 modernization of filer access (Login.gov, MFA, role-based admin).
- [[Federal Securities Laws]]: the statutes the SEC enforces (1933 Act through JOBS Act 2012).
- [[SEC Filing Types]]: the standardized forms (10-K, 10-Q, 8-K, S-1, 13D/G, Forms 3/4/5, etc.).
- [[EDGAR APIs]]: the public `data.sec.gov` JSON endpoints and full-text search.
- [[Regulation Crowdfunding]]: the Reg CF exemption (Title III JOBS Act); $5M public raises via registered intermediaries.
- [[Funding Portal]]: FINRA-member Reg CF intermediary; lighter-weight than a broker-dealer.
- [[Form C]]: the Reg CF offering statement (plus C-AR annual report) filed on EDGAR.
- [[XBRL]]: structured-data tagging standard (inline XBRL) for EDGAR financial filings.
- [[Financial Data Transparency Act]]: 2022 law mandating uniform machine-readable data across nine financial regulators.
- [[SEC Cybersecurity Disclosure Rules]]: 8-K Item 1.05 + Reg S-K Item 106 (in effect, 2023).
- [[SEC Climate Disclosure Rule]]: adopted 2024, stayed, rescission proposed 2026.
- [[T+1 Settlement Cycle]]: one-day settlement, effective May 2024.
- [[Recent SEC Rulemaking and Litigation 2023-2026]]: roundup of the era's rules and their fates.
- [[Exempt Offerings]]: the menu of registration exemptions (Reg D / Reg A / Reg CF / 4(a)(2)).
- [[Regulation D]], [[Regulation A]], [[Accredited Investor]], [[Rule 144]]: the private-capital and resale exemptions.
- [[Regulation S-K]], [[Regulation S-X]], [[Integrated Disclosure System]]: the narrative and financial-statement disclosure rulebooks.
- [[SEC Divisions and Structure]], [[SEC Enforcement Process]], [[SEC Whistleblower Program]]: how the agency is organized and enforces the law.
- [[Proxy Statement]], [[Universal Proxy]], [[Rule 14a-8 Shareholder Proposals]]: shareholder-voting and proxy-solicitation rules.
- [[Williams Act]], [[Tender Offer]]: takeover and tender-offer regulation (Schedule TO / 14D-9).

## Contradictions

- Headline scale figures differ across sources: Wikipedia cites "17M filings (May 2025)" while older SEC material cites "36M documents." These measure different units (submissions vs. constituent documents) rather than truly conflicting. (Source: [[EDGAR]])
- December 2025 EDGAR Next sub-deadlines vary by a few days between law-firm summaries (Dec 19 vs Dec 22). The SEC final rule is authoritative. (Source: [[EDGAR Next]])

## Open Questions

- ~~**EDGAR API rate limits:**~~ RESOLVED in Pass 8: 10 requests/second per IP + required User-Agent header; violations return HTTP 403 + ~10-min block. See [[EDGAR Data Access]].
- **EDGAR Next machine-to-machine filing:** how API tokens / technical-administrator roles work for automated filing under the new model needs a dedicated pass.
- **XBRL & structured-data mandate:** covered in Pass 3 (XBRL/iXBRL + FDTA). Remaining: exact FDTA 2026 final-rule effective date; per-agency SEC implementing rules.
- **Recent rulemaking (2023-2026):** covered in Pass 4 (cyber, climate, buybacks, T+1). Remaining: precise 2026 climate-rescission final text; any new 2026 disclosure proposals.
- **Regulation S-K / S-X:** covered in Pass 6. Remaining: specific S-K item numbers beyond 303/106; S-X article-by-article detail.
- **Exemptions:** covered in Pass 5 (Reg D, Reg A, Rule 144, accredited investor) and Pass 2 (Reg CF). Remaining: Section 4(a)(2) case law; intrastate (Rule 147/147A); pending accredited-investor expansion legislation.
- **SEC enforcement & structure:** covered in Pass 7 (divisions, Wells process, whistleblower). Remaining: examinations (Division of Examinations), the gag-rule/Rule 102(e) detail.
- **Practical EDGAR data access:** covered in Pass 8 (CIK, accession format, bulk datasets, rate limits). Planned backlog now complete.
- **Possible future clusters:** proxy solicitation (Section 14 / Schedule 14A), tender offers (Williams Act / Schedule TO), municipal securities & the MSRB, Investment Advisers Act detail (Form ADV), SPACs, Section 16 insider trading mechanics.
- **Reg CF financial-statement tiers:** exact dollar thresholds for self-certified vs reviewed vs audited financials (Rule 201(t)) still need verification.

## Sources

- [[SEC.gov - About EDGAR]]: SEC, official
- [[SEC.gov - Transition to EDGAR Next]]: SEC, 2025-03-24
- [[SEC.gov - EDGAR APIs]]: SEC, official
- [[investor.gov - Laws That Govern the Securities Industry]]: SEC, official
- [[Wikipedia - EDGAR]]: Wikipedia, 2026
- [[Wikipedia - Securities Exchange Act of 1934]]: Wikipedia, 2026
- [[sec-api.io - Full-Text Search API Docs]]: sec-api.io
- [[edgar.tools - SEC Filing Types Explained]]: edgar.tools
- [[Nuvo Group - EDGAR Next Transition]]: The Nuvo Group, 2025

---

## Research Log

- **Pass 1 (2026-06-29):** Broad sweep - laws, EDGAR system, filing types, EDGAR Next, APIs. 16 pages filed.
- **Pass 2 (2026-06-29):** Reg CF crowdfunding funding portals - Regulation Crowdfunding, Funding Portal, Form C, FINRA, and the three leading portals (Wefunder/StartEngine/Republic). 14 pages filed.
- **Pass 3 (2026-06-29):** XBRL & structured data - XBRL/inline XBRL, Financial Data Transparency Act, FASB. 8 pages filed.
- **Pass 4 (2026-06-29):** Recent rulemaking 2023-2026 - cybersecurity (8-K Item 1.05), climate disclosure, buyback vacatur, T+1, plus a litigation roundup. 9 pages filed. Wiki-lint run (full vault): 0 orphans, fixed 3 self-introduced dead links, flagged pre-existing ones for human review.
- **Pass 5 (2026-06-29):** Private-offering exemptions - Exempt Offerings umbrella, Regulation D (506b/506c), Regulation A (Tier 1/2), Accredited Investor, Rule 144. 11 pages filed.
- **Pass 6 (2026-06-29):** Disclosure rulebooks - Regulation S-K, Regulation S-X, Integrated Disclosure System. 6 pages filed.
- **Pass 7 (2026-06-29):** SEC structure & enforcement - Divisions/DERA, Enforcement Process (Wells), Whistleblower Program. 6 pages filed. Wiki-lint (full vault, 146 pages): 0 dead links / 0 orphans across 32 loop pages.
- **Pass 8 (2026-06-29):** Practical EDGAR data access - EDGAR Data Access (CIK/accession/rate limits), EDGAR Bulk Data. 5 pages filed; resolved the long-standing API rate-limit open question (10 req/s + User-Agent). Planned backlog complete.
- **Pass 9 (2026-06-29):** Proxy solicitation - Proxy Statement (Schedule 14A / say-on-pay), Universal Proxy (Rule 14a-19), Rule 14a-8 shareholder proposals. 7 pages filed. FIRST pass to pull SEC primary sources directly via scripts/sec-fetch.sh (verified verbatim), per the new operating principle.
- **Pass 10 (2026-06-29):** Takeovers - Williams Act (13(d)/14(d)/14(e)), Tender Offer (Schedule TO/14D-9, 20-day rule, all-holders/best-price, April 2026 10-day order). 5 pages + full-vault lint (0/0). SEC primaries fetched directly; also improved scripts/sec-fetch.sh to follow redirects.
