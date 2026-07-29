---
type: source
title: "Find a Tender OCDS API"
source_type: official-government-documentation
author: UK Cabinet Office
date_accessed: 2026-06-18
url: "https://www.find-tender.service.gov.uk/Developer/Documentation"
confidence: high
key_claims:
  - "Find a Tender exposes public OCDS release and record package endpoints."
  - "The search API supports time windows, stages, page limits up to 100, and cursor pagination."
  - "From 24 February 2025, Find a Tender is the central platform for new procurements under the Procurement Act."
---

# Find a Tender OCDS API

## Retrieval API

`GET https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages`

Parameters include `updatedFrom`, `updatedTo`, `stages`, `limit` from 1 to 100, and `cursor`. The response is an OCDS release package with `links.next` for cursor pagination. The service documents HTTP 429 handling through the `Retry-After` header. Record package endpoints provide the compiled lifecycle for an `ocid`.

An unauthenticated request returned HTTP 200 and JSON on 2026-06-18. Authentication and API keys apply to the notice submission API, not ordinary public retrieval.

## Sources

- https://www.find-tender.service.gov.uk/Developer/Documentation
- https://www.find-tender.service.gov.uk/apidocumentation/1.0/GET-ocdsReleasePackages
- https://www.gov.uk/government/publications/procurement-act-2023-short-guides/the-procurement-act-2023-a-short-guide-for-suppliers-html
- https://www.find-tender.service.gov.uk/Developer/NoticeTypes

