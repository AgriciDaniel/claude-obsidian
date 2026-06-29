---
type: concept
title: "EDGAR APIs"
complexity: advanced
domain: securities-regulation
aliases:
  - "data.sec.gov"
  - "EDGAR Full-Text Search API"
  - "SEC Submissions API"
created: 2026-06-29
updated: 2026-06-29
tags:
  - concept
  - securities
  - sec
  - api
  - data
status: developing
related:
  - "[[EDGAR]]"
  - "[[SEC Filing Types]]"
  - "[[EDGAR Next]]"
  - "[[concepts/_index]]"
  - "[[index]]"
sources:
  - "[[SEC.gov - EDGAR APIs]]"
  - "[[sec-api.io - Full-Text Search API Docs]]"
---

# EDGAR APIs

The SEC exposes [[EDGAR]] filing data through public REST APIs on `data.sec.gov`, returning JSON. **No authentication or API key is required** for read access. (Source: [[SEC.gov - EDGAR APIs]])

---

## Core endpoints (`data.sec.gov`)

- **Submissions API** - returns all filing metadata for a company by CIK (form type, filing date, accession number, document index), covering recent and historical filings. (Source: [[SEC.gov - EDGAR APIs]])
- **Company Facts API** - all XBRL-tagged financial facts for a company in one JSON document.
- **Company Concept API** - a single XBRL concept (e.g., one financial line item) for a company across periods.
- **Frames API** - one concept across many companies for a given period.

CIK numbers are zero-padded to 10 digits in API paths.

## Full-text search (EFTS)

- Searches the full text of all EDGAR filings **and exhibits since 2001 to present**, including delisted companies (no survivorship bias). (Source: [[sec-api.io - Full-Text Search API Docs]])
- New filings are indexed and searchable in **under 60 seconds** of publication.
- Boolean operators: implicit `AND`, capitalized `OR`, `NOT`/hyphen exclusion, `*` wildcards (term-end), and `"exact phrase"` matching.
- Filterable by date range (`startDate`/`endDate`), `formTypes`, and `ciks`.
- Returns up to 100 documents per response; capped at 10,000 results per query - narrow by date window or CIK to page beyond that.

## Fair access

The SEC requires automated clients to declare a descriptive **User-Agent header** (organization name + contact email) and observe a fair-access rate limit.

- **Rate limit: 10 requests/second** per user/IP, regardless of machine count. Exceeding it returns **HTTP 403** and blocks the IP for ~10 minutes. (Resolved in Pass 8 - see [[EDGAR Data Access]].)
- Requests without a User-Agent header are blocked.

> [!note] This is the same rate-control/User-Agent mechanism that returned 403 to this vault's automated `WebFetch` against sec.gov throughout this research. See [[EDGAR Data Access]] for CIK / accession-number detail.

## Confidence

**high** for endpoint structure, JSON output, no-auth access, and full-text search behavior; **medium** on the precise rate-limit number pending SEC.gov re-verification.
