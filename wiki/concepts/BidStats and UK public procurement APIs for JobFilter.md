---
type: synthesis
title: "BidStats and UK public procurement APIs for JobFilter"
created: 2026-06-18
updated: 2026-06-18
tags: [research, jobfilter, procurement, ocds]
status: current
related:
  - "[[BidStats Pricing and Insights API]]"
  - "[[Find a Tender OCDS API]]"
  - "[[Contracts Finder Transition and OCDS API]]"
  - "[[UK Procurement OCDS Bulk and Regional Feeds]]"
sources:
  - "[[BidStats Pricing and Insights API]]"
  - "[[Find a Tender OCDS API]]"
  - "[[Contracts Finder Transition and OCDS API]]"
  - "[[UK Procurement OCDS Bulk and Regional Feeds]]"
---

# BidStats and UK public procurement APIs for JobFilter

## Recommendation

Do not buy BidStats Insights yet. Build JobFilter's first tender ingestion layer on the free Find a Tender OCDS API, add Public Contracts Scotland for Scottish below-threshold coverage, and use Contracts Finder only for legacy and backfill continuity.

BidStats Insights starts at £5,000 per year, about £417 per month. At JobFilter's £39 monthly price, roughly 11 active subscriptions are needed only to cover that minimum data cost before tax, hosting, support, or acquisition costs. Reconsider BidStats when its pre-procurement signals, spend intelligence, contact enrichment, or reduced data-cleaning work have a measured effect on conversion.

## Current pricing

| BidStats plan | Price | Relevant access |
|---|---:|---|
| Free | £0 | 5 tender views per day, 3 portals, 90 days |
| Standard | £35 monthly or £350 yearly | Unlimited tenders from top 3 portals, 12 months, no API |
| Pro | £80 monthly or £800 yearly | 3 seats, 3,000+ buyers, 5 years, exports, no API |
| Insights | From £5,000 yearly | 10 years, API/CRM integration, pre-procurement, spend, frameworks, contacts |

The official site does not expose public API documentation, endpoint details, authentication method, quotas, or a self-serve API signup. Access appears to be sales-led and contract-specific. (Source: [[BidStats Pricing and Insights API]])

## Recommended source stack

### Find a Tender: primary live feed

- Endpoint: `GET https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages`
- Query with `updatedFrom`, `updatedTo`, optional `stages`, and `limit` from 1 to 100.
- Follow `links.next` cursor URLs until exhausted.
- Public retrieval worked without credentials on 2026-06-18.
- Handle HTTP 429 using `Retry-After`.
- Use record packages to reconstruct the full lifecycle for an `ocid`.

From 24 February 2025, Find a Tender became the central platform for new UK procurement notices under the Procurement Act. It includes planning, tender, award, contract, and implementation notices, including below-threshold notices where the Act applies. (Source: [[Find a Tender OCDS API]])

### Public Contracts Scotland: Scottish supplement

- Endpoint: `GET https://api.publiccontractsscotland.gov.uk/v1/Notices`
- Required parameter: `dateFrom=MM-YYYY`
- Optional: `noticeType`, `outputType`, `locale`
- No API key is documented. An unauthenticated request returned HTTP 200 on 2026-06-18.

This closes an important gap because the Procurement Act does not apply to devolved Scottish procurement and Find a Tender excludes Scottish below-threshold contracts. (Source: [[UK Procurement OCDS Bulk and Regional Feeds]])

### Contracts Finder: legacy and backfill only

- Endpoint: `GET https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search`
- Query with `publishedFrom`, `publishedTo`, optional `stages`, `limit` from 1 to 100, and cursor pagination.
- Public retrieval worked without credentials on 2026-06-18.
- Also offers daily and dated CSV downloads.

New procurements moved to Find a Tender on 24 February 2025. Contracts Finder still exposes historical processes and later-stage updates for notices that originated there, so it is useful for continuity but not as JobFilter's primary discovery feed. (Source: [[Contracts Finder Transition and OCDS API]])

### Bulk and analytics sources

- The Open Contracting Partnership Data Registry provides free yearly JSON, CSV, and Excel downloads for Find a Tender and Contracts Finder.
- `data.gov.uk/api/action` is a free CKAN metadata API with no authentication or documented rate limit. It helps discover datasets and bulk resources, but it is not a live tender query API.
- Sell2Wales publishes an OCDS API using the same monthly notice pattern as Public Contracts Scotland. Its TLS certificate was expired when tested on 2026-06-18, so it should not be a production dependency until repaired.

(Source: [[UK Procurement OCDS Bulk and Regional Feeds]])

## Suitability for JobFilter

The free OCDS feeds contain the fields needed for a useful first scoring pass: title, description, CPV classifications, value, location, buyer, tender deadline, procurement method, SME suitability, and source documents.

The main engineering cost is normalization rather than access. JobFilter should expect:

- Amendments and lifecycle notices that need deduplication by `ocid`.
- Missing or inconsistent buyer and supplier identifiers.
- Some procurement processes split across multiple identifiers.
- Submission documents hosted on external portals, sometimes behind registration.
- Regional gaps, especially Scottish below-threshold procurement.

Start with construction CPV filters, geographic matching, value bands, deadline freshness, and notice-stage weighting. Add BidStats only if the free-feed pipeline proves demand and curated intelligence materially improves lead quality.

## Confidence

- High: BidStats pricing and plan boundaries, Find a Tender transition, public OCDS endpoints, cursor pagination, and free public retrieval.
- Medium: BidStats API authentication and quota constraints, because the official site does not publish technical documentation.
- High: Sell2Wales certificate failure as observed on 2026-06-18. Recheck before making a long-term decision.

