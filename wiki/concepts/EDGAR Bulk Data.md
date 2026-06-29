---
type: concept
title: "EDGAR Bulk Data"
complexity: advanced
domain: securities-regulation
aliases:
  - "Financial Statement Data Sets"
  - "EDGAR Full-Index"
  - "DERA Data Library"
created: 2026-06-29
updated: 2026-06-29
tags:
  - concept
  - securities
  - sec
  - edgar
  - data
status: developing
related:
  - "[[EDGAR Data Access]]"
  - "[[EDGAR APIs]]"
  - "[[XBRL]]"
  - "[[SEC Divisions and Structure]]"
  - "[[concepts/_index]]"
  - "[[index]]"
sources:
  - "[[SEC.gov - Financial Statement Data Sets]]"
  - "[[SEC.gov - Accessing EDGAR Data]]"
---

# EDGAR Bulk Data

Beyond per-company [[EDGAR APIs|APIs]], the SEC publishes **bulk datasets** for mass analysis of filings from 1993 to present. (Source: [[SEC.gov - Accessing EDGAR Data]])

---

## Financial Statement Data Sets

Structured extracts of the [[XBRL]] financial data from **10-K / 10-Q** family forms (submitted since **April 15, 2009**). Originally **quarterly**, then **monthly beginning April 2023**. (Source: [[SEC.gov - Financial Statement Data Sets]])

Four linked tables per dataset:
- **SUB** - submission metadata (filer, form, period).
- **NUM** - the numeric values reported.
- **TAG** - the XBRL tag definitions / taxonomy version.
- **PRE** - presentation (how tags map into the primary statements).

## Other bulk resources

- **Full-index files** - daily/quarterly indexes of all accepted filings (by company, form, and date).
- **FTP / bulk download** from the SEC for filings and exhibits.
- **DERA Data Library** ([[SEC Divisions and Structure|Division of Economic and Risk Analysis]]) - Financial Statements, Financial Statements and Notes, and EDGAR Logfile datasets.

## When to use which

- **Per-company question** -> `data.sec.gov` [[EDGAR APIs]].
- **Cross-company / time-series analysis** -> Financial Statement Data Sets or full-index bulk files.

## Confidence

**high** on the SUB/NUM/TAG/PRE structure, the 2009 start, and the 2023 monthly cadence; **medium** on current FTP endpoint specifics (the SEC has migrated some bulk access over time).
