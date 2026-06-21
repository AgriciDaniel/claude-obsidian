---
date: 2026-06-21
project: recall
agent: codex
status: completed
---

## What I did

- Built and shipped Recall's first Execution Router.
- Added deterministic task routing for Claude, Codex, and OpenCode.
- Added ordered dependencies, assignment rationale, verification requirements, and copy-ready agent prompts.
- Kept objectives and tasks device-local with no model call or new database table.
- Added the Router to the authenticated sidebar.
- Added a working product-led Router section to the landing page.
- Added the Router to Trial pricing and positioned shared templates, routing history, approvals, and outcome tracking as upcoming monthly-plan value.
- Replaced dead pilot conversion paths with a pre-addressed £500 founding-pilot enquiry.
- Simplified Recall and JobFilterV1 GitHub descriptions.
- Simplified Recall repository metadata and README.
- Fixed CI builds that lacked Clerk configuration and failed on Windows native SQLite installation.

## Files changed

- `app/(app)/router/page.tsx`
- `lib/execution-router.ts`
- `tests/unit/execution-router.test.ts`
- `components/Sidebar.tsx`
- `middleware.ts`
- `app/(marketing)/page.tsx`
- `app/(marketing)/pricing/page.tsx`
- `app/layout.tsx`
- `.github/workflows/ci.yml`
- `.gitignore`
- `README.md`
- `package.json`
- `package-lock.json`
- Execution Router design and implementation-plan documents

## Decisions made

- Use deterministic routing rather than an LLM so the feature works without credentials and does not transmit confidential client objectives.
- Use browser storage for the first release instead of adding speculative persistence.
- Default ambiguous implementation/integration work to Codex.
- Order discovery and design before build, then verification and shipping.
- Monetize the collaborative layer: shared templates, history, permissions, approvals, and outcome tracking.
- Use a £500 four-week pilot credited against the first three paid months after conversion.
- Keep unfinished collaboration capabilities explicitly marked as pilot or upcoming.

## Verification

- Unit tests: 27 passed, including 4 Execution Router tests.
- Extension tests: 4 passed.
- Extension build: passed.
- TypeScript and lint: passed with existing unused-parameter warnings.
- Production build with Vercel preview variables: passed.
- GitHub CI: Linux, Windows, macOS, and standalone type-check jobs passed.
- HTTP verification:
  - `/` → 200
  - `/pricing` → 200
  - `/router` unauthenticated → 307 to `/sign-in?redirect_url=%2Frouter`
  - `/api/health` → 200
- No secrets were added to the diff.
- Interactive browser automation was unavailable in the session, so no authenticated visual-browser claim was made.

## Deployment

- Preview: https://recall-5vck6rbi5-manazir-s-projects1.vercel.app
- Draft PR: https://github.com/manazoid4/recall/pull/1
- Branch: `agents/execution-router`
- Latest commit: `afabd88`

## Remaining manual actions

- Replace the preview `DATABASE_URL` with the correct pooled Supabase connection string; the current adapter reports that the configured URL is a direct connection.
- Perform an authenticated desktop/mobile visual pass of `/router`.
- Plan a separately scoped dependency upgrade: `npm audit` reports 10 existing findings, including one critical development-tool finding.
- Confirm `hello@userecall.app` receives pilot enquiries.
- Do not promote the preview to production until the database URL and authenticated visual pass are complete.

## Next steps

- Add persisted, tenant-scoped routing templates and history.
- Connect routed work to evidence boards and cited briefs.
- Add client-scoped permissions and approval states.
- Track delivered work and outcomes to strengthen Recall's learning moat.
