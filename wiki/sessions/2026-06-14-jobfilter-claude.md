# JobFilter — 2026-06-14 (Claude)

## Context
User fired the giant "founder-level 7-agent audit" mega-prompt at JobFilterV1.
Repo already has multiple recent audit docs (AUDIT-REPORT.md, JOBFILTER-APPLE-LEVEL-AUDIT-REPORT.md,
PROJECT_STATUS.md, COMPETITOR_STRATEGY_PLAYBOOK.md) — mostly redundant with the ask.
Also note: mega-prompt template assumes "AI job search platform" but JobFilter is
actually a UK trade-leads gen platform (plumbers/electricians/etc). Mismatch flagged.

Scoped down per user choice: "Just implement TODO" — skip the 7-agent audit/research
sprawl, pick highest-value unimplemented item from TODO.md / code TODOs and ship it.

## What shipped
- PR: https://github.com/manazoid4/JobFilterV1/pull/258 (branch `feat/lead-alert-email-delivery`)
- `app/api/alerts/route.ts` had a doc comment: "Email delivery is NOT implemented here".
- Implemented:
  - `server/lib/resend.ts` — new `sendLeadAlertEmail(to, opts)` (alongside existing
    `sendWelcomeEmail`, `sendPaidConfirmationEmail`, `sendAdminAlert`, `sendLeadChaseEmail`)
  - `app/api/alerts/send/route.ts` — new cron route. Reads active `lead_alerts`,
    checks `last_sent_at` vs frequency interval (instant=1h, daily=24h, weekly=7d),
    runs `scan({ postcode: postcode_outward, trade, tier })`, emails up to 5 leads
    via Resend if found, updates `last_sent_at`. Optional `CRON_SECRET` auth.
  - `vercel.json` — added hourly cron entry for `/api/alerts/send`.
  - `TODO.md` — documented optional `CRON_SECRET` env var, marked item done.

## Notes / gotchas
- Stash-pop during branch switch produced a merge conflict in `server/lib/resend.ts`
  because `origin/main` had already grown a `sendLeadChaseEmail` function (different
  feature, lead-chase emails) in the same file. Resolved by keeping both functions.
- Repo has lots of pre-existing uncommitted local changes (CLAUDE.md, .claude/settings.local.json,
  Obsidian .obsidian/graph.json & workspace.json, several `agents/codex-*-audit-2026-06-06.md`
  files, `.claude/scheduled_tasks.lock`) — left untouched, not part of this task. PR #258
  only touches the 5 files listed above.
- `.next/types/validator.ts` has a stale reference to a non-existent
  `app/api/cron/daily-scan/route.ts` — pre-existing tsc error, unrelated, regenerates on `next build`.

## Round 2 — "do 5 most impact things" from mega-prompt
- PR: https://github.com/manazoid4/JobFilterV1/pull/259 (branch `fix/security-seo-quickwins`)
- 5 shipped:
  1. `app/robots.ts` — was missing entirely (no robots.txt at all)
  2. `app/sitemap.ts` — `BASE_URL` was `jobfilter.co.uk`, everywhere else in
     codebase uses `jobfilter.uk` — sitemap pointed search engines at wrong domain
  3. `next.config.ts` — added security headers (X-Frame-Options, nosniff,
     Referrer-Policy, Permissions-Policy)
  4. `server/routes/leadsSearch.ts` `sanitizeRadius()` — threw 422 if
     `radiusMiles` omitted; now defaults to 25
  5. New `server/lib/nextRateLimit.ts` (in-memory, Next route handler compatible)
     applied to `/api/stripe/checkout` (10/min) and `/api/waitlist` (5/min) —
     both previously unprotected
- Tried `npm audit fix` for react-router DoS CVE first — it bumped next
  16.2.7→16.2.9 and made total vuln count WORSE (7→14, new undici issue).
  Reverted package-lock.json + re-ran `npm install`. Dep vuln fixes left as
  known issue, not safe to auto-fix without testing.
- Verified `/api/leads/search` IS reachable in prod (curled jobfilter.uk,
  got expected 422 for missing radiusMiles before the fix) — so the
  api/index.ts + app/api/* coexistence on Vercel works fine, no
  "Frankenstein stack" routing crisis as apple-audit implied.

## Remaining for next session
- The 20-deliverable mega-audit was NOT done (deliberately, user chose narrow path).
  If user wants the full audit later, start from existing AUDIT-REPORT.md /
  JOBFILTER-APPLE-LEVEL-AUDIT-REPORT.md / COMPETITOR_STRATEGY_PLAYBOOK.md rather than
  redoing research from scratch — most of agents 1/2/5's scope is already covered there.
- Other implementable code TODOs found but not done (lower priority, mock data fetchers):
  - `leadEngine/fetchers/charityCommissionFetcher.ts` — TODO: real Charity Commission API
  - `leadEngine/fetchers/forestryCommissionFetcher.ts` — TODO: real Forestry Commission register
  - `leadEngine/fetchers/landRegistryFetcher.ts` — TODO: real Land Registry CSV parsing
