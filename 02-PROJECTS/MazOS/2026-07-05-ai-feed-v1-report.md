# MAZos AI Feed Report

Date: 2026-07-05

## Research Used

The v1 feed design follows the research/spec in `specs/mazos-ai-feed.md`:

- Linear Inbox: activity should behave like a triage inbox, not a noisy timeline.
- GitHub Notifications: filters and attention state are useful for developer workflows.
- Slack Activity: one consolidated catch-up surface reduces tab switching.
- Devin and OpenHands: agent systems need event/trajectory continuity and easy handoff.

MAZos-specific doctrine from `docs/MAZOS_MARKET_BREAKER_ROADMAP.md` won: every panel must reduce decision load and answer what should ship next.

## What Shipped

- Added `GET /api/mazos/feed`.
- Added `src/lib/mazos/feed.ts` deterministic aggregator.
- Added `FEED` tab to the main MAZos cockpit.
- Feed sources:
  - Shipping Spine
  - Decision Inbox
  - Run history
  - Stale Work Radar
  - Ship Log
  - Intake queue
  - OpenWiki status
- Added compact feed verdict, filters, attention-only mode, evidence modal, copyable prompt per item, and safety badges.
- Updated README.

## Safety

- No shell execution.
- No LLM calls.
- No external RSS/web crawling.
- No cron.
- No database or JSONL writes.
- No agent launch.
- All item actions are read-only links, evidence modals, or copyable prompts.

## API

`GET /api/mazos/feed`

Query params:

- `limit`, default `12`, max `30`
- `product`
- `type`
- `attentionOnly=true`

Response includes `verdict`, `filters`, `items`, `degraded`, and `warnings`.

## Validation

- `npm run lint`: passed.
- `npm run build`: passed. Build emitted the existing non-fatal Turbopack warnings for OpenWiki local Windows/Python tracing and root lockfile inference.
- Local `GET http://127.0.0.1:3046/api/mazos/feed`: passed.
- Local root page smoke check returned 200. Existing dev server on `3046` held the Next project lock, so a second branch-specific dev server could not start on `3051`.
- PR #17 merged.
- Production deployment `dpl_obMah8Nezzf6WgyDrGwfLMV7uoB7`: Ready.
- Hosted `GET https://mazos-command-centre.vercel.app/api/mazos/feed`: passed.
- Hosted `https://mazos-command-centre.vercel.app/`: returned 200.

## Next Improvements

1. Add read/mute state in `data/mazos/feed-state.json` only after v1 proves useful.
2. Add Proof Receipts as first-class feed items.
3. Add a prompt-only "summarize this feed" action before any automatic LLM integration.
