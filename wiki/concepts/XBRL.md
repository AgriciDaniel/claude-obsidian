---
type: concept
title: "XBRL"
complexity: advanced
domain: securities-regulation
aliases:
  - "eXtensible Business Reporting Language"
  - "Inline XBRL"
  - "iXBRL"
  - "Interactive Data"
created: 2026-06-29
updated: 2026-06-29
tags:
  - concept
  - securities
  - sec
  - xbrl
  - structured-data
status: developing
related:
  - "[[EDGAR]]"
  - "[[EDGAR APIs]]"
  - "[[SEC Filing Types]]"
  - "[[Financial Data Transparency Act]]"
  - "[[Financial Accounting Standards Board]]"
  - "[[concepts/_index]]"
  - "[[index]]"
sources:
  - "[[SEC.gov - Inline XBRL]]"
  - "[[IRIS Carbon - 10 Years of SEC iXBRL Timeline]]"
  - "[[Cooley - SEC Adopts Mandatory Inline XBRL]]"
---

# XBRL

**XBRL** (eXtensible Business Reporting Language) is the structured-data standard the SEC requires for financial information in [[EDGAR]] filings. It tags each reported figure with machine-readable metadata so computers can search, assemble, and analyze filings automatically. (Source: [[SEC.gov - Inline XBRL]])

---

## How tagging works

- Each financial item is tagged against the **US GAAP Financial Reporting Taxonomy** - a library of ~17,000 standard tags maintained by the **[[Financial Accounting Standards Board|FASB]]** that defines concepts (Revenue, Net Income, Assets) and their relationships. (Source: [[SEC.gov - Inline XBRL]])
- If no standard tag fits, filers may create a custom **extension** tag.
- This XBRL data feeds the [[EDGAR APIs]] (company facts / concept / frames endpoints).

## Inline XBRL (iXBRL)

**Inline XBRL** embeds the tags directly into the human-readable HTML filing, so one document is both human- and machine-readable - eliminating the separate XBRL exhibit. (Source: [[Cooley - SEC Adopts Mandatory Inline XBRL]])

What must be in iXBRL: cover-page and financial-statement data (including footnotes and schedules) in **10-K, 10-Q**, certain non-IPO registration statements; cover pages and certain data in **8-K**, proxy, and information statements; and fund risk/return summaries.

## Timeline

| Date | Milestone |
|------|-----------|
| 2008 | SEC unveils IDEA (Interactive Data); XBRL US publishes first US GAAP taxonomy |
| 2009 | XBRL mandatory for large accelerated filers (public float > $700M) |
| 2011 | Smaller reporting companies (< $75M float) phased in |
| 2012 | All filers filing complete financials in XBRL |
| Jun 28, 2018 | SEC adopts mandatory **Inline** XBRL (phased over 2018-2021) |
| FY ending >= Jun 15, 2019 | Large accelerated filers (US GAAP) on iXBRL |
| FY ending >= Jun 15, 2020 | Accelerated filers on iXBRL |
| FY ending >= Jun 15, 2021 | All other filers on iXBRL |

(Source: [[IRIS Carbon - 10 Years of SEC iXBRL Timeline]])

## Confidence

**high** on the standard, inline XBRL mechanics, and phase-in dates (corroborated across SEC, law-firm, and vendor sources); **medium** on the exact ~17,000 tag count (single vendor figure, varies by taxonomy year).
