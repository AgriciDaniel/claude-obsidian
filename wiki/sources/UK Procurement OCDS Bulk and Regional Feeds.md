---
type: source
title: "UK Procurement OCDS Bulk and Regional Feeds"
source_type: official-data-documentation
author: Open Contracting Partnership and UK regional procurement services
date_accessed: 2026-06-18
url: "https://data.open-contracting.org/en/publication/41"
confidence: high
key_claims:
  - "The Open Contracting Data Registry offers free bulk JSON, CSV, and Excel downloads."
  - "Public Contracts Scotland exposes a free OCDS notice endpoint."
  - "Sell2Wales exposes an OCDS endpoint, but its TLS certificate was expired when tested."
---

# UK Procurement OCDS Bulk and Regional Feeds

## Open Contracting Data Registry

The registry publishes processed yearly JSON, CSV, and Excel downloads for Find a Tender and Contracts Finder. It is suitable for backfills and analytics, not low-latency alerts. Its data quality notes flag missing organisation identifiers, malformed dates, and procurement processes split across multiple identifiers.

## Public Contracts Scotland

`GET https://api.publiccontractsscotland.gov.uk/v1/Notices`

The required parameter is `dateFrom=MM-YYYY`. Optional parameters are `noticeType`, `outputType`, and `locale`. No API key is documented. An unauthenticated request returned HTTP 200 on 2026-06-18.

Scotland follows devolved procurement legislation rather than the Procurement Act 2023. Find a Tender excludes Scottish below-threshold contracts, so this feed is a useful supplement.

## Sell2Wales

`GET https://api.sell2wales.gov.wales/v1/Notices`

The endpoint uses the same monthly parameter pattern. No API key is documented. The TLS certificate was expired when tested with Windows curl and Node.js on 2026-06-18. Do not make it a production dependency until the certificate is repaired.

## data.gov.uk

`GET https://data.gov.uk/api/action`

This CKAN API requires no authentication and documents no rate limit. It searches dataset metadata and discovers download resources. It is not a substitute for Find a Tender's live notice API.

## Sources

- https://data.open-contracting.org/en/publication/41
- https://data.open-contracting.org/en/publication/14
- https://api.publiccontractsscotland.gov.uk/
- https://www.publiccontractsscotland.gov.uk/Notice/Download/Download.aspx
- https://api.sell2wales.gov.wales/
- https://www.sell2wales.gov.wales/Notice/Download/Download.aspx
- https://www.find-tender.service.gov.uk/Developer/NoticeTypes
- https://www.gov.scot/publications/public-procurement-regulations-thresholds-changes-1-january-2026/
- https://guidance.data.gov.uk/publish_and_manage_data/harvest_or_add_data/api_documentation/

