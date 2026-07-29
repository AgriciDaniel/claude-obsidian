---
date: 2026-06-30
project: recall
agent: codex
status: completed
---
## What I did
- Wrote a detailed Recall post-mortem covering what the reset fixed, what remained weak, and where the future moat should be.
- Added the Instagram Inbox moat: message-first capture that feels like DMing a trusted person, backed by a compliant shared Recall inbox and private routing codes.
- Added `/instagram-inbox`, webhook verification at `/api/instagram/inbox/webhook`, demo inbox data, typed models, agent helpers, tests, and documentation updates.
- Added the Signal OS paid wedge so Recall now scores captures as GOLD/SILVER/BRONZE and turns the best signals into daily actions and agent context packs.
- Added `/signal-os`, dashboard Signal OS CTA, deterministic signal scoring helpers, daily brief generation, paid moat copy, tests, and repo documentation updates.
- Opened GitHub PR #6: https://github.com/manazoid4/recall/pull/6
- Pushed commit `2984a2e` to PR #6.

## Files changed
- `POSTMORTEM.md`
- `.env.example`
- `README.md`
- `PRODUCT_MAP.md`
- `ROADMAP.md`
- `app/instagram-inbox/page.tsx`
- `app/signal-os/page.tsx`
- `app/api/instagram/inbox/webhook/route.ts`
- `app/components/RecallShell.tsx`
- `app/components/RouteViews.tsx`
- `app/globals.css`
- `lib/types.ts`
- `lib/agents.ts`
- `lib/mockData.ts`
- `middleware.ts`
- `tests/unit/recall-agents.test.ts`

## Decisions made
- The literal "every user gets an Instagram bot" idea was translated into a compliant product shape: shared Recall-owned Instagram professional inbox with user routing codes first, connected professional accounts later.
- JobFilter inspiration should be the scoring discipline, not the niche: Recall should charge for ranked personal signal, not storage.
- GOLD means act today or generate a prompt, SILVER means watch/ask for context, BRONZE means archive without polluting the active profile.
- Webhook verification is public, while the rest of `/api/instagram/*` remains protected by Clerk.
- The moat language now centers capture habit, signal scoring, evidence graph, taste/intent graph, agent context, privacy/trust, and workflow distribution.

## Verification
- `npm test` passed: 46 tests across 7 files.
- `npm run lint` passed with existing unused-argument warnings in `components/VoiceCapture.tsx` and `lib/db.ts`.
- `npm run build` passed with dummy Clerk publishable key and placeholder DATABASE_URL; the known DB health warning appeared during static generation.
- Build output includes `/signal-os`.

## Next steps
- Add durable routing records for Instagram sender/thread -> Recall user.
- Persist inbound DM captures as real `MemoryItem` records.
- Persist `SignalScore` and `DailyBrief` records instead of generating them from demo data.
- Add paid daily brief delivery by email/DM and connect GOLD signals to project-specific agent prompts.
- Add assistant replies asking for reason saved, sensitivity, project link, and prompt generation.
- Complete Meta app setup, webhook subscriptions, permissions, and app review for production Instagram Messaging.
- Build mobile share sheet and MCP context pack after the Instagram inbox loop is proven.
