---
date: 2026-06-18
project: jobfilter
agent: codex
status: completed
---

## What I did

Researched current BidStats pricing and API availability plus free official UK procurement data sources. Verified live unauthenticated responses from Find a Tender, Contracts Finder, and Public Contracts Scotland. Compared current coverage after the 24 February 2025 Procurement Act transition and documented the recommended ingestion stack.

## Files changed

- `wiki/concepts/BidStats and UK public procurement APIs for JobFilter.md`
- `wiki/sources/BidStats Pricing and Insights API.md`
- `wiki/sources/Find a Tender OCDS API.md`
- `wiki/sources/Contracts Finder Transition and OCDS API.md`
- `wiki/sources/UK Procurement OCDS Bulk and Regional Feeds.md`
- `wiki/projects/jobfilter/index.md`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`
- `wiki/sessions/2026-06-18-jobfilter-codex.md`

No JobFilter code was edited.

## Decisions made

- Use Find a Tender OCDS as the primary live tender source.
- Add Public Contracts Scotland for Scottish below-threshold coverage.
- Use Contracts Finder for historical and legacy lifecycle continuity.
- Defer BidStats Insights at its current starting price of £5,000 per year.
- Do not rely on Sell2Wales until its expired TLS certificate is repaired.

## Next steps

- If implementation is approved later, design an OCDS normalization and deduplication model keyed by `ocid`.
- Recheck Sell2Wales TLS status before adding a Welsh regional connector.
- Reassess BidStats after JobFilter has enough paid users and evidence that enriched signals improve lead conversion.
