# Recall: Auth & Security Session — 2026-06-09 (Session 3)

## Summary

Continued production hardening. Fixed 13 bugs across security, auth enforcement, SQL compatibility, AI userId threading, and license flow.

## Bugs Fixed

### Security / Auth

| File | Bug | Fix |
|------|-----|-----|
| `app/api/boards/route.ts` | GET returned ALL users' boards unauthenticated | Require auth, always filter WHERE owner_id = userId |
| `app/api/boards/route.ts` | POST allowed unauthenticated board creation | Require auth |
| `app/api/boards/[slug]/route.ts` | GET returned private boards to unauthenticated callers | Enforce is_public = 1 when no userId |
| `app/api/boards/[slug]/items/route.ts` | POST/DELETE bypassed auth when board.owner_id = null | Require auth, filter by owner_id |
| `app/api/boards/[slug]/clone/route.ts` | Anyone could clone private boards | Require auth, restrict to public or own boards |
| `app/api/digest/route.ts` | GET/POST accessible unauthenticated - data leak + unsolicited email | Require userId |
| `app/api/stats/route.ts` | Returned aggregate counts without auth - info disclosure | Require auth, always scope to userId |

### SQL Compatibility

| File | Bug | Fix |
|------|-----|-----|
| `app/api/enrich/route.ts` | INSERT OR REPLACE - Postgres rejects silently | ON CONFLICT(id) DO UPDATE SET with deterministic ID enrichment-{itemId} |

### AI / Per-User Keys

| File | Bug | Fix |
|------|-----|-----|
| `lib/ai/providers.ts` | callLLM fetched API key with no userId - always read global key | Added userId? to CallLLMOptions, threaded to all getSetting calls |
| `lib/ai/enrich.ts` | enrichItem/enrichBatch ignored userId | Added userId? param, passed to getSetting and callLLM |
| `app/api/enrich/route.ts` | Didn't pass userId to enrichItem | Pass userId or undefined |
| `app/api/refine/route.ts` | await auth() result discarded | Destructure userId, pass to callLLM |

### Entitlements

| Bug | Fix |
|-----|-----|
| enrichment not in PRO_TIER.features - enrichment always 403 for Pro users | Added enrichment to PRO_TIER |
| graph_view in FREE_TIER (pricing says it's Pro) | Moved to PRO_TIER |
| getItemCount/getBoardCount used raw BigInt result | Wrapped with Number() |

### Settings / Onboarding

| Bug | Fix |
|-----|-----|
| onboarding_complete not in ALLOWED_KEYS - silently dropped | Added to ALLOWED_KEYS |
| No UI to activate license key after purchase | Added Pro License card to settings page with license key input + tier badge |

### Content / UX

| Bug | Fix |
|-----|-----|
| Pricing FAQ: "data stays local, SQLite" - wrong for cloud SaaS | Updated to: Supabase + RLS, encrypted keys |
| /b/[slug] 404 page back link goes to /boards (auth required) | Changed to / |
| /upgrade page missing (referenced in 7 API 403 responses) | Created as redirect to /pricing |

## Commits

```
47a26e3 fix: thread userId through AI layer, fix board privacy, onboarding_complete setting
9ef41e1 fix: auth checks, entitlement features, COUNT safety
8692928 feat: Pro license activation in settings + fix license/verify features list
631c7a9 fix: ingest route iterates validated.data not raw request body
ad0a0f3 fix: INSERT OR REPLACE -> ON CONFLICT(id) in enrichments (Postgres compat)
6078df5 fix: boards clone requires auth + only allows cloning public/own boards
37c4a49 fix: boards API auth hardening - scope all ops to authenticated owner
```

## Architecture: Entitlement Tiers (corrected)

FREE_TIER features: basic_search, manual_import (50 items, 1 board)

PRO_TIER features: everything in free + enrichment, semantic_search, graph_view,
auto_sync, api_access, export, webhooks, digest (unlimited items + boards)

## Architecture: Per-User AI Keys

Flow:
1. User enters API key in /onboarding or /settings -> POST /api/settings -> setSetting(key, value, userId) -> stored with owner_id = userId
2. API route calls enrichItem(item, userId) or callLLM(prompt, { ..., userId })
3. getSetting('llm_api_key', '', userId) -> fetches from settings WHERE key = ? AND owner_id = ?
4. If empty: fall through to LLM_API_KEY env var -> OPENAI_API_KEY env var

## Remaining Todos

| Task | Notes |
|------|-------|
| Clerk production keys | User must upgrade at dashboard.clerk.com |
| OPENAI_API_KEY in Vercel | Platform-level key for users who haven't configured their own |
| LemonSqueezy account setup | LEMONSQUEEZY_API_KEY, STORE_ID, PRODUCT_ID, WEBHOOK_SECRET |
| userecall.app custom domain | DNS + Vercel custom domain |
| Webhook -> Clerk user lookup | Link purchase email -> Clerk userId at webhook time for auto Pro activation |
