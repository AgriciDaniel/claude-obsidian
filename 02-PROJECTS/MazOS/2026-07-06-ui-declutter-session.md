# MazOS UI Declutter — 2026-07-06

Session: Maz asked for "whole UI overhaul, massive declutter" + approved research-prompt PR.

## Shipped (both merged to main)

- **PR #25** — `MAZOS_PROOF_RECEIPTS_RESEARCH_PROMPT.md` (research brief for Proof Receipts / Safe Action Capsules / Revenue Radar). See [[2026-07-06-proof-receipts-research-prompt]].
- **PR #26** — UI declutter per `specs/mazos-ui-declutter.md` (spec → build → review loop):
  - Nav 8 destinations → 5 tabs: NOW / INBOX (was FEED) / WORK (PROJECTS+LOOPS merged) / INTAKE / SYSTEM. TASK GATE + OPENWIKI → mono header links + palette entries.
  - NOW = Shipping Spine + Morning Brief only. Deleted: mini Stale Radar, Loop Status strip, Last Signal panel (dupes), "Latest Project Work" query panel, JARVIS eyebrow, always-on local bridge banner.
  - localStorage tab migration (FEED→INBOX, LOOPS/PROJECTS→WORK, unknown→NOW); feed.ts hrefs updated; INBOX unread badge; orphan CSS removed.
  - Review: 11/11 spec requirements pass. tsc + build + CI green.

## Caveats

- Vercel deploy rate-limited 24h (free tier) — hosted mirror updates late; local cockpit has new UI immediately.
- Browser tab-switch smoke not run locally (Playwright MCP bridge extension missing); covered by CI build + type check, visual check pending on next Vercel deploy.

Related: [[2026-07-06-operator-inbox-session]]
