---
type: plan
project: jobfilter
date: 2026-06-11
---

# 13 Split Batches — Codex vs Claude

Source: [[06 Bugs Risks and Blockers]] + [[09 Next Build Plan]]. Split logic: Codex gets self-contained single-file fixes (no cross-system context needed). Claude gets git-history recovery, multi-system integration, external services (Twilio/Supabase/cron), and founder coordination.

## Batch A — CODEX (mechanical, isolated)
1. Harden Stripe checkout — `app/api/stripe/checkout/route.ts` (server auth, ignore client priceId)
2. Unify GOLD/SILVER thresholds — new `leadEngine/thresholds.ts`, GOLD=80
3. Gate `/test` + `/dev-portal` behind owner auth
4. Rate limiting on scan/intake/waitlist routes
5. Webhook: return 500 on DB failure paths so Stripe retries
6. `npm audit fix` (2 high, 2 moderate)
7. Root debris cleanup + .gitignore (logs, tsbuildinfo, fix-*.cjs, zips)

Full prompt: see "CODEX BATCH PROMPT" section below — copy-paste verbatim.

## Batch B — CLAUDE (integration, recovery, delivery)
1. Recover intake pipeline from git history (`git log --all -- app/api/intake/score/route.ts`) or re-implement: username capture, Supabase `intake_submissions` persistence, GOLD WhatsApp trigger
2. Auto GOLD→WhatsApp delivery: trigger on persist, dedupe via `delivery_events`, daily 7am Vercel cron digest
3. Server-backed leads: leadStore/winStore → Supabase, cross-device dashboard
4. Onboarding capture: trade + postcode districts → profiles
5. Branch hygiene: merge `fix/mobile-nav-rebuild` → main via PR
6. Founder coordination: STICKY-TODO (Twilio, Stripe dashboard, migrations, Vercel envs), verify prod after deploy

Rule: Codex works on a NEW branch `codex/launch-blockers-batch-a` cut from `fix/mobile-nav-rebuild`. Claude works after Codex PR lands (or on separate branch touching disjoint files). Disjoint file sets — no conflicts expected except `package.json` (audit fix) — Codex owns it.

---

## CODEX BATCH PROMPT (copy-paste)

You are fixing launch blockers in JobFilter, a UK construction lead intelligence platform (Next.js 16 App Router + React 19 + Supabase + Stripe). Repo: `C:\Users\manaz\Desktop\jobfilter\jobfilterv1`. Current branch `fix/mobile-nav-rebuild` — cut a new branch `codex/launch-blockers-batch-a` from it.

RULES: Read each file before editing. Surgical changes only — do not refactor beyond the listed tasks, do not touch `app/api/intake/score/route.ts` (another agent owns it), do not delete `server/` or `src/` directories. Run `npx tsc --noEmit` and `npm run build` after changes — both must pass. Never commit secrets. Commit per-task, open a PR to `fix/mobile-nav-rebuild` — never push to main.

TASK 1 — Harden Stripe checkout (`app/api/stripe/checkout/route.ts`).
Evidence: lines 22–28 currently accept `priceId`, `userId`, `email` from the request body with no auth. A client can POST `tier: "business"` plus a cheaper `priceId` and the webhook then upgrades plan from metadata tier. Fix: (a) ignore any client-supplied `priceId` — always resolve via `resolvePriceId(tier, billing)` from `src/lib/stripe.ts`; (b) derive the user server-side via the Supabase auth session (`createAuthServerClient` from `src/lib/supabase/auth-server.ts` — see `app/api/leads/whatsapp/route.ts` lines 20–47 for the working pattern); reject unauthenticated requests with 401; use session user id + email, never body values. Keep `app/api/create-checkout-session/route.ts` re-export working. Acceptance: forged body cannot change price or user; tsc green.

TASK 2 — Unify lead tier thresholds.
Evidence: `leadEngine/scorer.ts:239` uses `finalScore >= 90` for GOLD; `server/services/decisionScoring.ts:60` uses `finalScore >= 80 ? 'GOLD' : finalScore >= 50 ? 'SILVER' : 'BIN'`. Marketing promise is GOLD = 80+. Fix: create `leadEngine/thresholds.ts` exporting `export const GOLD_THRESHOLD = 80; export const SILVER_THRESHOLD = 50;`. Import and use in `leadEngine/scorer.ts`, `server/services/decisionScoring.ts`, `server/services/leadScoring.ts`, and any UI file comparing score literals (grep `>= 90`, `>= 80`, `>= 75`, `>= 50` across `src/` and fix tier comparisons only — leave unrelated numerics alone). Acceptance: `grep -rn ">= 90\|>= 80" leadEngine server src` shows only the constants file or imports; tsc green.

TASK 3 — Gate dev pages.
Evidence: `app/test/page.tsx` and `app/dev-portal/page.tsx` are publicly reachable and `/test` is in the sitemap. Fix: in both pages, if `process.env.NODE_ENV === 'production'`, call `notFound()` from `next/navigation` before rendering (server-side check in the page wrapper, not inside the client component). Remove both routes from `app/sitemap.ts` if listed. Acceptance: production build serves 404 for both; dev still works.

TASK 4 — Rate limiting.
Evidence: no rate limiting on any Next API route (`server/middleware/rateLimit.ts` belongs to the dead Express app). Fix: create `src/lib/rateLimit.ts` with a simple in-memory sliding-window limiter keyed by IP (`request.headers.get('x-forwarded-for')` first value, fallback 'unknown'): max 20 requests/minute. Apply at the top of: `app/api/leads/whatsapp/route.ts`, `app/api/waitlist/route.ts`, `app/api/ai/score-lead/route.ts`, and any `app/api/leads/*` scan/search routes present. Return 429 JSON `{ ok: false, error: 'Too many requests' }` when exceeded. Note in a comment that in-memory state is per-serverless-instance — acceptable stopgap. Do NOT touch the intake route. Acceptance: hammering an endpoint in dev returns 429 after 20 hits.

TASK 5 — Webhook retry semantics (`app/api/stripe/webhook/route.ts`).
Evidence: lines 59–62 catch handler errors and still return 200 ("Still return 200 so Stripe does not retry"), so failed plan upgrades are lost. Fix: in the catch block, return `Response.json({ received: false, error: '...' }, { status: 500 })` so Stripe retries. Keep signature-failure 400 and unconfigured 503 as-is. Acceptance: thrown error inside handlers yields 500.

TASK 6 — Dependency vulnerabilities.
Run `npm audit --omit=dev` (currently 2 high, 2 moderate). Run `npm audit fix` (NOT `--force`). Re-run `npx tsc --noEmit` and `npm run build`. If fix requires breaking changes, document in PR body instead of forcing. Acceptance: high count reduced or rationale documented; build green.

TASK 7 — Root debris cleanup.
Delete from repo root: `fix-client-lib.cjs`, `fix-client.cjs`, `fix-env.cjs`, `fix-imports.cjs`, `fix-links.cjs`, `fix-localstorage-all.cjs`, `fix-localstorage.cjs`, `fix-router-imports.cjs`, `replace-router.cjs`, `use-client.cjs`, `migrate-pages.js`, `migrate-router.js`, `dev-server.log`, `next-dev.err.log`, `next-dev.out.log`, `server-dev.err.log`, `server-dev.out.log`, `FinalDesignJobFilter.zip`, `JobFilterStich.zip`. Add to `.gitignore`: `*.log`, `tsconfig.tsbuildinfo`, `*.zip` and `git rm --cached tsconfig.tsbuildinfo`. Do NOT delete `index.html`, `vite.config.ts`, `server.ts`, `server/`, or any directory. Acceptance: build green after deletions; `git status` clean of junk.

FINAL: run `npx tsc --noEmit` + `npm run build`, write a summary table (| # | Task | Status | Files |) to `CODEX-BATCH-A-2026-06-11.md` in repo root, open PR titled "fix: launch blockers batch A (checkout, thresholds, gating, ratelimit, webhook, audit, cleanup)".

---

## CLAUDE BATCH B — execution checklist (this agent, next session)
- [ ] B1: `git log --all -- app/api/intake/score/route.ts` → recover or re-implement intake persistence + username + WhatsApp trigger (graceful no-op without env)
- [ ] B2: GOLD auto-delivery — trigger on persist, `delivery_events` dedupe, `app/api/cron/daily-scan/route.ts` + `CRON_SECRET` + vercel.json cron
- [ ] B3: leadStore/winStore → Supabase server-first, localStorage fallback
- [ ] B4: post-signup trade + postcode capture → profiles
- [ ] B5: merge `fix/mobile-nav-rebuild` → main via PR after Batch A lands
- [ ] B6: walk founder through STICKY-TODO (Twilio, Stripe product/webhook, 20260531 migrations, Vercel envs), verify `/api/subscription/status` in prod
