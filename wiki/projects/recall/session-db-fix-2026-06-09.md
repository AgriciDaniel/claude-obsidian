# Recall: DB Layer Fix Session — 2026-06-09

## Summary

Full production DB layer overhaul. App was silently broken — all Supabase queries returned empty data.

## Root Causes Fixed

### 1. Middleware 401 → Redirect
- `auth.protect()` rewrites to 404 with Clerk test keys on non-localhost
- Fix: manual `NextResponse.redirect('/sign-in?redirect_url=...')`

### 2. Database Layer Broken in Production
- SQLite db interface: synchronous
- Supabase adapter: async, but callers never awaited
- All db calls returned Promises treated as data → empty results

### 3. @vercel/postgres Wrong Export
- `db` export from `@vercel/postgres` uses `POSTGRES_URL` not `DATABASE_URL`
- Fix: `createPool({ connectionString: DATABASE_URL })`

### 4. SQL Dialect Differences
- `?` placeholders → `$1, $2` (handled in `toPostgresSQL()`)
- `datetime('now')` → `NOW()` (handled in `toPostgresSQL()`)
- `COUNT(*)` → `COUNT(*)::int` to avoid BigInt string return

### 5. Settings Table Schema Mismatch
- Supabase: `id TEXT PRIMARY KEY`, SQLite: `key TEXT PRIMARY KEY`
- Migration 20260609000002: changed to `(key, owner_id)` composite PK
- owner_id defaults to `''` (not NULL) for proper ON CONFLICT support

### 6. better-sqlite3 Native Module
- Static import at module level could fail in Vercel Lambda
- Fix: `require('better-sqlite3')` inside `getSQLite()` (only called in local dev)

## Commits

- dbedcd7 fix: manual redirect to /sign-in for protected routes
- 08c32c7 fix: checkIsPro queries purchases table not settings
- 11640de fix: lazy-load better-sqlite3 via require() to avoid native module import on Vercel
- 90a519b fix: use createPool(DATABASE_URL) instead of db export from @vercel/postgres
- 2b451fe fix: settings table schema + SQL alignment for Postgres
- e79399b fix: Postgres COUNT(*) → COUNT(*)::int, null-safe total in items route
- 680a60b fix: production database layer now works with @vercel/postgres
- 91ae26d feat: add Chrome Extension card to settings + fix settings API key names
- 388fea1 fix: redirect to sign-in instead of 401 for protected routes

## Remaining Todos

| Task | Status | Blocker |
|------|--------|---------|
| Clerk production keys | Manual | User must upgrade at dashboard.clerk.com |
| OPENAI_API_KEY in Vercel | Manual | Need API key value |
| LemonSqueezy keys | Manual | Need LemonSqueezy account |
| userecall.app custom domain | Manual | DNS setup at registrar |

## Architecture Notes

**DB Layer (lib/db.ts):**
- `isProduction = !!(DATABASE_URL || (SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY))`
- Production: `@vercel/postgres` createPool with `DATABASE_URL`
- Local dev: `better-sqlite3` (lazy-loaded via require)
- SQL conversion: `toPostgresSQL()` handles `?` → `$N`, `datetime('now')` → `NOW()`, `COUNT(*) → COUNT(*)::int`

**Settings table schema:**
- `(key TEXT, owner_id TEXT DEFAULT '') PRIMARY KEY (key, owner_id)`
- `getSetting('llm_api_key')` → DB → `LLM_API_KEY` env → provider-specific env fallthrough
