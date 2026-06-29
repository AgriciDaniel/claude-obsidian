---
type: concept
title: "EDGAR Data Access"
complexity: advanced
domain: securities-regulation
aliases:
  - "CIK"
  - "Central Index Key"
  - "Accession Number"
  - "EDGAR Identifiers"
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
  - "[[EDGAR]]"
  - "[[EDGAR APIs]]"
  - "[[EDGAR Bulk Data]]"
  - "[[XBRL]]"
  - "[[concepts/_index]]"
  - "[[index]]"
sources:
  - "[[SEC.gov - Accessing EDGAR Data]]"
  - "[[SEC.gov - New Rate Control Limits]]"
---

# EDGAR Data Access

The practical identifiers and rules for retrieving filings from [[EDGAR]] programmatically. (Source: [[SEC.gov - Accessing EDGAR Data]])

---

## CIK (Central Index Key)

- A unique **10-digit** number the SEC assigns to each registrant/filer.
- **Never changes** even if the company renames or changes ticker - the most reliable long-term identifier. (Source: [[SEC.gov - Accessing EDGAR Data]])
- Find a CIK by searching EDGAR by company name or ticker (e.g., IBM -> CIK `0000051143`). Leading zeros are often dropped in some access paths.
- In `data.sec.gov` API paths, CIK is **zero-padded to 10 digits**.

## Accession number

The unique ID of an accepted submission, format `XXXXXXXXXX-YY-NNNNNN`: (Source: [[SEC.gov - Accessing EDGAR Data]])

- First block = the **CIK of the submitter** (company or filer agent).
- `YY` = the **year**.
- `NNNNNN` = a **sequential count** of that filer's submissions, reset each calendar year.
- Example: IBM's Oct 2013 10-Q = `0000051143-13-000007`.

## Fair-access rules (important)

- **10 requests/second** hard cap **per user/IP**, regardless of machine count. (Source: [[SEC.gov - New Rate Control Limits]]; verified verbatim from sec.gov Developer Resources and "Accessing EDGAR Data," 2026-06-29.)
- A descriptive **User-Agent header** is **required**. SEC's own sample format: `User-Agent: Sample Company Name AdminContact@<company domain>`. Requests without it are blocked.
- Exceeding the limit returns **HTTP 403** and throttles the IP.

> [!note] **Confirmed in practice (2026-06-29):** plain `WebFetch` returned 403 against sec.gov because it sends no compliant User-Agent. A `curl`/HTTP request **with** the SEC-format User-Agent returns **HTTP 200** (verified against both `data.sec.gov` JSON APIs and sec.gov HTML pages). This resolves the earlier open question on [[EDGAR APIs]] and is the supported way to read SEC primary sources.

## Confidence

**high** - CIK/accession format and the 10 req/s + User-Agent rule are documented by the SEC and corroborated across multiple developer sources.
