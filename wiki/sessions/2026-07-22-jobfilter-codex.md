---
date: 2026-07-22
project: jobfilter
agent: codex
status: completed
---

## What I did

- Ran a multi-agent JobFilter audit across engineering/security, product/market, and UX/conversion/QA perspectives.
- Audited the active `agents/jobfilter-find-a-tender` branch, production routes/API behaviour, open PR queue, branch protection, CI, dependencies and current Supabase drift.
- Verified a clean-install typecheck, FTS fixture regression, source-safety, postcode, redaction, lead-quality and Next.js production build.
- Researched the current UK procurement market, Find a Tender capabilities, SME policy and tender-intelligence competitors.
- Produced a dependency-aware 90-day execution plan with binary release, paid-pilot and beta gates.
- Secured Batch 1 API surfaces: tenant-bound outcome/flag mutations, authenticated self-only lead email, paid start-signal access, authenticated subscription lookup, HMAC-signed n8n ingress, and an explicit Express API 404.
- Made Resend lead-alert delivery return explicit provider success/failure and message IDs, with HTML escaping and safe URL handling.
- Added and ran a focused API security regression, full TypeScript check, and production build.

## Files changed

- `wiki/projects/jobfilter/2026-07-22-ultra-research-execution-plan.md`
- `wiki/sessions/2026-07-22-jobfilter-codex.md`
- JobFilter application security changes committed as `55ec673` (`fix: secure tenant API mutations and webhooks`).

## Decisions made

- JobFilter should target employing construction/maintenance SMEs and qualify public-works opportunities, not market itself as a domestic lead marketplace.
- Broad paid launch is no-go until security, tenant isolation, schema, Stripe, alert locality and lead-supply gates pass.
- Draft PR #383 is the release foundation; overlapping nightly copy PRs must be triaged against the new product contract.
- The paid value is BID/WATCH/SUBCONTRACT/SKIP decision quality and outcome learning, not access to free government notices or alerts.
- First recommended wedge is West Midlands electrical, M&E/maintenance and refurbishment firms.
- Express routes now derive tenant identity from verified Supabase bearer tokens or SSR auth cookies; callers cannot select another account through body/query identity fields.
- Inbound n8n events require a fresh timestamped HMAC-SHA256 signature using `N8N_INGRESS_SECRET`.

## Next steps

- Pause JobFilter nightly automation and triage PRs #381/#383–#386.
- Make #383 green against the current dependency audit and portable runtime tests.
- Configure `N8N_INGRESS_SECRET` and update n8n callers to sign `${timestamp}.${rawBody}` in `x-jobfilter-signature`, with Unix seconds in `x-jobfilter-timestamp`.
- Deploy the truthful FTS foundation.
- Reconcile Supabase in staging and prove two-user tenant isolation before payment testing.
