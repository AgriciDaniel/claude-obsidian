---
date: 2026-08-02
project: scrap-finance-partners
agent: codex
status: completed
---

## What I did

- Used the supplied Supabase personal access token ephemerally; it was not written to the repository or Vercel.
- Created a dedicated Supabase project named Scrap Finance Partners in the London region.
- Linked the local project and applied `20260801201911_create_lead_workspace.sql`.
- Configured production Supabase URL and publishable key as Vercel environment variables.
- Configured Supabase Auth site and redirect URLs for the canonical Vercel domain.
- Redeployed the existing production commit so the new environment variables are active.
- Verified login inputs are enabled, email signup is enabled, unauthenticated lead routes redirect to login, and anonymous database reads are denied.
- Created a real admin identity for the account email associated with the supplied Supabase credentials.
- Created the real Scrap Finance Partners organisation and assigned that account the `owner` role.
- Added three genuine reusable email templates: Finance Health Check introduction, Polite follow-up, and Meeting confirmation.
- Added a mobile-friendly Start here guide inside the client workspace, linked it from navigation and the leads page, and covered it with an end-to-end test.
- Merged PR #27 and verified the canonical production deployment is Ready.
- Verified live data remains clean: one organisation, one owner membership, three templates, and zero leads, messages, or revenue entries.

## Files changed

- `app/account/guide/page.jsx`
- `app/account/layout.jsx`
- `app/account/leads/page.jsx`
- `tests/e2e/account.spec.ts`
- `docs/releases/client-workspace-onboarding.md`

## Decisions made

- Use a dedicated Scrap Finance Partners project, not the existing JobFilter or Recall projects.
- Give the initial account the `owner` role, which includes full administrative access.
- Require password selection through the live Forgot Password flow rather than exposing or storing a temporary password.
- Keep live email in draft-only mode until `SEND_EMAILS_ENABLED=true` is deliberately configured.
- Populate instructions and reusable templates only; do not invent leads, contacts, messages, or revenue.
- The personal access token shared in chat should be rotated after setup.

## Next steps

- Open `https://scrap-finance-partners.vercel.app/forgot-password` and enter the account email associated with the Supabase credentials, then choose a password.
- Sign in and follow the workspace guide at `/account/guide`.
- Add the first genuine lead and confirm the intended client workflow.
- Rotate the supplied Supabase personal access token from the Supabase account settings.
