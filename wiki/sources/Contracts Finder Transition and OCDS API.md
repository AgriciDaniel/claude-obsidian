---
type: source
title: "Contracts Finder Transition and OCDS API"
source_type: official-government-documentation
author: Crown Commercial Service and UK Cabinet Office
date_accessed: 2026-06-18
url: "https://www.contractsfinder.service.gov.uk/apidocumentation/home"
confidence: high
key_claims:
  - "Contracts Finder exposes OCDS search, record, release, and bulk CSV access."
  - "New procurement notices moved to Find a Tender on 24 February 2025."
  - "Contracts Finder remains useful for historical notices and later updates to processes that began there."
---

# Contracts Finder Transition and OCDS API

## Retrieval API

`GET https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search`

Parameters include `publishedFrom`, `publishedTo`, `stages`, `limit` from 1 to 100, and `cursor`. The API also exposes release and record lookups plus daily and dated CSV files.

Public retrieval returned HTTP 200 without credentials on 2026-06-18. The documentation warns that excessive request rates can cause a temporary HTTP 403 cooldown. OAuth and Sid4Gov are required for publishing notices through the inbound API, not for public data retrieval.

## Transition

Official guidance states that new procurements must be published on Find a Tender from 24 February 2025. Existing Contracts Finder notices can still be managed there. The API returned a 2026 award release in testing, consistent with later-stage updates for legacy procurement processes.

## Sources

- https://www.contractsfinder.service.gov.uk/apidocumentation/home
- https://www.contractsfinder.service.gov.uk/apidocumentation/notices
- https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-Notices-OCDS-Search
- https://www.gov.uk/government/publications/procurement-act-2023-guidance-documents-manage-transition/converting-pipeline-notices-and-existing-opportunities

