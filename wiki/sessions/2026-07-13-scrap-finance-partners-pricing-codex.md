---
date: 2026-07-13
project: scrap-finance-partners
agent: codex
status: completed
---
## What I did
- Raised Scrap Finance Partners pricing to a more premium offer ladder.
- Rebuilt the pricing page around outcome-based retainers, fixed sprints, and scaffolded feature modules.
- Updated the Health Check page to anchor at £2,500.
- Updated the offer ladder documentation to match the new pricing and module scaffold.
- Fixed a lint issue in Growth Hub while validating the build.
- Opened PR #4 on the project repo.

## Files changed
- `app/pricing/page.tsx`
- `data/pricing.ts`
- `app/health-check/page.tsx`
- `docs/OFFER_LADDER.md`
- `app/growth-hub/page.tsx`

## Decisions made
- Replaced Bronze/Silver/Gold with Control, Margin, and Board.
- Set retainers at £1,500/mo, £3,000/mo, and £6,000+/mo.
- Set the Health Check at £2,500 fixed.
- Repriced sprints into £3,500-£15,000 ranges depending on scope.
- Framed new capabilities as scaffolded modules rather than finished product functionality.

## Next steps
- Review PR #4.
- Decide whether the live deployed branch is newer than local source, because the audited Vercel site had routes and styling not present in this source tree.
- After merging, deploy and verify the Vercel production page.
