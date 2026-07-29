---
project: flipsignal
status: phase-1-scaffolded
repo: manazoid4/flipsignal
local_path: C:\Users\manaz\Desktop\flipsignal
vercel: manazir-s-projects1/flipsignal
created: 2026-06-15
---

# FlipSignal

AI-powered marketplace arbitrage engine. Finds undervalued listings (Facebook
Marketplace, eBay, Gumtree), models resale value/risk, ranks opportunity by
expected ROI, and tracks flips from discovery to sold.

## Status
- GitHub: https://github.com/manazoid4/flipsignal
- Local PC location: `C:\Users\manaz\Desktop\flipsignal`
- Repo created and pushed
- Vercel project linked + GitHub auto-deploy connected (main branch)
- Phase 1 scaffold complete: Clerk auth, Prisma schema (17 models), dashboard
  shell (deal feed, deal detail, portfolio, copilot, reports, alerts,
  billing, market), AI pipeline stubs (feature extraction, valuation, deal
  scoring, Flip Copilot, listing generator), scraper adapter stubs
  (Facebook/eBay/Gumtree), cron job stubs (ingest/score/daily-report/obsidian-export),
  Obsidian export module wired to this vault.

## Tiers
- FREE: limited searches, basic alerts, manual scoring
- PRO: AI deal discovery, profit engine, daily feed, portfolio, listing
  generator, negotiation assistant
- ELITE: full automation, predictive sourcing, category intelligence,
  Telegram/Discord alerts, AI flipping copilot, batch analysis

## Build phases (see repo README for detail)
1. Foundation (done) — auth, schema, dashboard shell, mock ingestion
2. Deal scoring engine + real scraper adapters + UI feed
3. Profit engine + portfolio CRUD
4. AI Flip Copilot (vision input)
5. Automation + alerts (Telegram/Discord, Stripe tier gating)
6. Learning loop (UserActionLog → CategoryStats feedback)

## Folders in this vault
- `Deals/` — per-flip markdown exported by `/api/cron/obsidian-export`
- `Daily Reports/` — daily top-10 flip reports
- `Portfolio/` — lifecycle notes per tracked item
- `Market Research/` — category/price anomaly signals
- `User Performance/` — learning loop outcome tracking

## Env vars needed before Phase 2
DATABASE_URL, DIRECT_URL, Clerk keys, OPENAI_API_KEY, CRON_SECRET, Stripe
keys, GITHUB_TOKEN (for this export), Telegram/Discord webhook for ELITE
alerts. Full list in repo `.env.example`.
