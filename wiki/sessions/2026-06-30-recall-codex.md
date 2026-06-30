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
- Opened GitHub PR #6: https://github.com/manazoid4/recall/pull/6

## Files changed
- `POSTMORTEM.md`
- `.env.example`
- `README.md`
- `PRODUCT_MAP.md`
- `ROADMAP.md`
- `app/instagram-inbox/page.tsx`
- `app/api/instagram/inbox/webhook/route.ts`
- `app/components/RecallShell.tsx`
- `app/components/RouteViews.tsx`
- `lib/types.ts`
- `lib/agents.ts`
- `lib/mockData.ts`
- `middleware.ts`
- `tests/unit/recall-agents.test.ts`

## Decisions made
- The literal "every user gets an Instagram bot" idea was translated into a compliant product shape: shared Recall-owned Instagram professional inbox with user routing codes first, connected professional accounts later.
- Webhook verification is public, while the rest of `/api/instagram/*` remains protected by Clerk.
- The moat language now centers capture habit, evidence graph, taste/intent graph, agent context, privacy/trust, and workflow distribution.

## Next steps
- Add durable routing records for Instagram sender/thread -> Recall user.
- Persist inbound DM captures as real `MemoryItem` records.
- Add assistant replies asking for reason saved, sensitivity, project link, and prompt generation.
- Complete Meta app setup, webhook subscriptions, permissions, and app review for production Instagram Messaging.
- Build mobile share sheet and MCP context pack after the Instagram inbox loop is proven.
