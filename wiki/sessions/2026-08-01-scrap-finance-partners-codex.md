---
date: 2026-08-01
project: scrap-finance-partners
agent: codex
status: completed
---

## What I did

- Reviewed the current industrial evidence-room design and its desktop homepage capture.
- Located the client-preferred Bloomberg-terminal redesign at commit `0c3cc5e` and compared its visual language with the current site.
- Planned a Bloomberg-dominant blend that preserves the current evidence structure, approval gating, pricing, routes, mobile navigation, forms, and accessibility work.
- Refreshed the codebase knowledge graph for the current repository structure.
- Developed a four-year managed website and launch package with a larger Year 1 delivery and lower managed-service fees in Years 2–4.
- Costed the current Vercel, Resend and business-email service levels and defined fair-use limits for third-party costs, updates, advertising and new feature work.
- Applied client feedback that the terminal redesign was too loud.
- Researched plain-English and low-friction content patterns, then restored the quieter light consultancy design.
- Shortened homepage, Health Check and form copy; moved optional qualification fields behind a disclosure.
- Merged PR #24 and verified the corrected production deployment.

## Files changed

- Rebuilt app/globals.css around a dark graphite, copper and compact information-display system.
- Updated app/page.tsx, components/site-header.tsx and components/site-footer.tsx with the blended Bloomberg/evidence-room treatment.
- Added the legacy /insights redirect to next.config.ts.
- Updated and pushed this vault session note.
- Restored the pre-PR-23 versions of app/globals.css, app/page.tsx and the shared site shell, then refined the homepage and Health Check journey.
- Updated components/lead-form.tsx, data/health-check.ts, tests/e2e/forms.spec.ts and the footer/legacy route handling.

## Decisions made

- Use the old Bloomberg version as an art-direction reference, not a commit to cherry-pick: the current route and data model are safer and more mature.
- Make the global canvas dark graphite with copper and restrained semantic colours; use the current light evidence-document treatment only as a deliberate contrast island.
- Restore data density, terminal labels, compact status strips, tabular layouts, and a split hero while retaining the current pain-led copy and real conversion path.
- Do not restore fake live claims, unverified savings figures, glass/glow, decorative grid/noise textures, or old inaccessible motion.
- Prototype the shared shell and homepage first, obtain visual approval, then roll the system across all secondary routes.
- Recommended commercial position: £8,500 total over four years — £4,750 in Year 1 and £1,250 in each of Years 2–4 — against an indicative standard value of £12,600.
- Year 1 includes the redesign, launch infrastructure, one business mailbox, virtual-address setup/allowance, LinkedIn Company Page launch, three sales one-pagers, up to three ad creatives and £500 media spend.
- Years 2–4 include managed commercial hosting, transactional email, one business mailbox, virtual-address renewal allowance, monitoring, backups, dependency/security maintenance and up to 12 hours or four planned production releases per year.
- Larger features, extra advertising, extra mailboxes and usage overages require a written variation; recommended loyalty development rate is £55/hour or a fixed quote.
- Client should own the domain and third-party accounts, retain super-admin access and complete any required identity/KYC checks.
- Implemented the redesign on agents/scrap-finance-bloomberg-blend, passed lint, typecheck, production build and all 123 Playwright tests.
- Opened and merged PR #23; Vercel production deployment dpl_BjwbZUFUnQAzqRtCCQsfcyqQziqB reached Ready and the public domain returned HTTP 200.
- Revised commercial position to a two-year £10,800 agreement: £1,200/month for months 1–6 and £200/month for months 7–24, subject to confirming that “£1,200 for the next six months” means per month.
- Client feedback superseded the Bloomberg-dominant direction: retain the first quiet consultancy design and use the later work only for content and service clarity.
- Remove the ticker and commercial-control status language entirely.
- Show only name, company and work email in the initial form; keep phone, priority and timing available but optional.
- PR #24 passed lint, typecheck, production build, design detection and all 123 Playwright tests; production deployment dpl_61Ck7Au8kPUAfZNxz1y53EFdVUzC reached Ready.

## Next steps

- Send the copy-ready two-year estimate and confirm whether the £1,200 target is monthly or total across the first six months.
- Confirm VAT status, client billing details, commencement date and the virtual-office/mailbox provider before issuing the first invoice.
- Create client-owned third-party accounts and complete KYC only after the agreement is signed.
- Scope any additional feature requests through a written variation before implementation.
- Confirm the client accepts the quieter production direction before starting another visual expansion.

## Planning intake continuation

- Audited the current `master` branch before the next requested major feature batch; no application code was changed.
- Confirmed the production direction is now the quieter light editorial/evidence-led design, while root `DESIGN.md` still describes an older dark graphite system and needs reconciliation during the next batch.
- Confirmed no client images, image guidelines, or photographic assets exist in the repository or its remote branches.
- Deferred the implementation brief and formal recurring invoice pending the client's visual reference, the batch's primary commercial objective, and seller/VAT/payment details.

### Next decision gate

- Obtain the client's image/design reference or explicit permission to infer from the current live site.
- Choose the first-order goal: enquiries, premium credibility, or YardLedger growth.
- Confirm whether the recurring charge is GBP 150, whether VAT applies, the first billing date, and the supplier/client legal and payment details.

## Client acquisition system

- Reprioritised the next batch around winning suitable UK scrap and recycling clients for Scrap Finance Partners.
- Built a private-by-default outreach workflow with corporate-recipient eligibility, consent gating for sole traders, suppression and duplicate handling, source recording, four-touch message generation and human approval before delivery.
- Added a Resend delivery runner that is dry-run by default, requires `--confirm`, caps batches, rechecks suppression at send time and allows only one due message per prospect per run.
- Added paid-revenue attribution and configurable commission reporting, defaulting to 15% of net collected revenue.
- Added an operating guide, invented-data templates, environment template, changelog entry and an itemised GBP 150/month acquisition invoice with a separate success-fee section.
- Kept all real prospect, send-log, queue and revenue data under Git-ignored `private/outreach/`.

### Verification

- Acquisition tests: 4/4 passed.
- ESLint, TypeScript and production build passed.
- Existing Playwright suite: 123/123 passed.
- Production dependency audit: zero known vulnerabilities.

### Deferred

- Supabase login, signup, password recovery and protected client portal remain the next clean batch. The mandatory Probity hook could not evaluate TS/TSX edits until the updated Codex desktop runtime is restarted, so no untested authentication code or unused auth dependencies were committed.
