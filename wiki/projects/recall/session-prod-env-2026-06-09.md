---
title: Recall — Production Environment + Voice Capture
project: recall
type: session-log
created: 2026-06-09
tags: [recall, session, production, shipped]
---

# Session: Production Environment + Voice Capture

Commits: `cd1b867` → https://github.com/manazoid4/recall

## Shipped

### Infrastructure
- Clerk app "Recall" created — app_3EuOr3cocpxjRhljbOgUYe10Z46
- Supabase project "recall" created — ref: tcfwhkqxirdrqolkygqd, eu-central-1
- Supabase migrations pushed (PostgreSQL schema with Clerk JWT RLS)
- Vercel project renamed: saved-brain → recall
- All env vars set in Vercel (Production + Preview + Development)

### Vercel env vars now set
- NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY (pk_test_)
- CLERK_SECRET_KEY (sk_test_)
- NEXT_PUBLIC_SUPABASE_URL = https://tcfwhkqxirdrqolkygqd.supabase.co
- NEXT_PUBLIC_SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY
- DATABASE_URL (Supabase pooler port 6543)
- RESEND_API_KEY
- CRON_SECRET
- DIGEST_EMAIL = digest@userecall.app
- DEFAULT_LLM_PROVIDER = openai
- DEFAULT_LLM_MODEL = gpt-4o-mini
- NEXT_PUBLIC_CLERK_SIGN_IN_URL / SIGN_UP_URL
- KEY_ENCRYPTION_SECRET, NEXT_PUBLIC_APP_URL (pre-existing)

### Voice Capture feature
- `components/VoiceCapture.tsx` — Web Speech API, continuous recognition, refine on stop
- `app/api/refine/route.ts` — LLM cleans transcript, returns {title, refined}
- `app/(app)/capture/page.tsx` — /capture route with success toast
- `components/Sidebar.tsx` — Capture nav item added (Mic icon)

## Manual steps remaining

| Item | Where |
|------|-------|
| LemonSqueezy keys | app.lemonsqueezy.com (domain blocked) |
| Clerk production instance | dashboard.clerk.com (currently test keys) |
| userecall.app domain DNS | Vercel + registrar |
| LLM API key | User configures in-app at /settings |

## Technical notes
- Voice note URL: `https://userecall.app/voice/{timestamp}` (passes z.string().url() validation)
- Supabase RLS uses `auth.jwt() ->> 'sub'` for Clerk user ID (TEXT)
- Service role key bypasses RLS on all server-side queries
- SQLite fallback still active for local dev
