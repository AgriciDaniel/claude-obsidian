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
- Performed privileged read-only counts confirming every workspace table contains zero records.

## Files changed

- No application source files changed.
- External Supabase and Vercel production configuration only.

## Decisions made

- Use a dedicated Scrap Finance Partners project, not the existing JobFilter or Recall projects.
- Keep live email in draft-only mode until `SEND_EMAILS_ENABLED=true` is deliberately configured.
- Do not create temporary users or leads because the user prohibited all fake data.
- The personal access token shared in chat should be rotated after setup.

## Next steps

- The user can create the first real account at `https://scrap-finance-partners.vercel.app/sign-up`.
- Confirm the Supabase confirmation email arrives and the first real lead persists.
- Rotate the supplied Supabase personal access token from the Supabase account settings.
