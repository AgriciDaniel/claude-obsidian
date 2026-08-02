---
date: 2026-08-02
project: scrap-finance-partners
agent: codex
status: completed
---

## What I did

- Used the supplied Supabase personal access token ephemerally; it was not written to the repository or Vercel.
- Created a dedicated Supabase project named Scrap Finance Partners in the London region.
- Linked the local project and applied the lead-workspace migrations.
- Configured production Supabase Auth, URL and publishable key for the canonical Vercel domain.
- Created a real admin identity for the account email associated with the supplied credentials.
- Created the real Scrap Finance Partners organisation and assigned that account the `owner` role.
- Added three genuine reusable email templates: Finance Health Check introduction, Polite follow-up, and Meeting confirmation.
- Added a mobile-friendly Start here guide inside the client workspace.
- Connected every valid website enquiry directly to the workspace lead table.
- Preserved source, campaign and qualification context, deduplicated repeat email enquiries, and assigned a next-day action.
- Made notification delivery secondary so a Resend failure cannot discard a captured lead.
- Added a mobile Today’s pipeline summary for due, new, meeting and won records.
- Applied `20260802120000_add_direct_enquiry_basis.sql` and added three server-only production intake variables.
- Merged PR #27 for onboarding and PR #28 for the website-to-pipeline flow.
- Verified the canonical production deployment `dpl_Gmb1iTw7LmgERzRWyKqS5FTHspkX` is Ready.
- Verified the health-check page returns 200, the protected workspace redirects anonymous users to login, and production still has zero leads.

## Files changed

- `app/account/guide/page.jsx`
- `app/account/layout.jsx`
- `app/account/leads/page.jsx`
- `app/api/lead/route.ts`
- `lib/inbound-lead.mjs`
- `tests/account/inbound-lead.test.mjs`
- `tests/e2e/account.spec.ts`
- `.env.example`
- `supabase/migrations/20260802120000_add_direct_enquiry_basis.sql`
- `docs/BUILD_LOG.md`
- `docs/releases/client-workspace-onboarding.md`

## Decisions made

- Maximise genuine, qualified client acquisition without fake data, spam or unsafe automation.
- Give the initial account the `owner` role, which includes full administrative access.
- Website form submissions are `direct_enquiry` records and receive a next-day action.
- Repeat submissions from the same organisation/email update the existing record instead of inflating lead count.
- Persist a lead before attempting an email notification.
- Keep outbound prospecting in draft-only mode until `SEND_EMAILS_ENABLED=true` is deliberately configured.
- Do not submit synthetic production enquiries during verification.
- Rotate the personal access token shared in chat after setup.

## Verification

- Account unit tests: 7 passed.
- ESLint: passed.
- TypeScript: passed.
- Production build: passed.
- Playwright account tests: 2 passed.
- Impeccable detector: no findings.
- Vercel production check: passed.
- Production lead count after deployment: 0.

## Next steps

- Set the admin password through `https://scrap-finance-partners.vercel.app/forgot-password`.
- Sign in and use `/account/leads` as the daily action queue.
- Begin driving real traffic to the Health Check form with source-tagged links.
- Configure and verify the Resend notification domain if immediate inbox alerts are required.
- Rotate the supplied Supabase personal access token.
