# 2026-07-04 — MAZos Shipping Spine v1 session

Agent: Claude (Fable 5) · Repo: `C:/Users/manaz/Projects/mazos-ui` · PR: https://github.com/manazoid4/mazos-ui/pull/11 (merged → main `9077ec9`)

## What shipped

**Shipping Spine v1** — MAZos now opens on an evidence-ranked operating table answering "what should be shipped next" across JobFilter, Recall, OpenFlowKit, MAZos.

- `src/lib/mazos/playbooks.ts` — product playbooks: audience, paid outcome, moat, current wedge, current bet, forbidden bloat, top metrics, done criteria. Grounded in real repo READMEs.
- `src/lib/mazos/shippingSpine.ts` — combines project status + repo scan + ship log + stale radar + open decisions + playbooks into ranked rows, each with a ready-to-paste scoped handoff prompt (owner, safety L1-L5, verify commands, forbidden actions). Writes snapshot to `data/mazos/shipping-spine.md`.
- `GET /api/mazos/shipping-spine` — works locally (3046) and through the hosted bridge (3047). Agents: read this before asking what to work on.
- NOW view: first-viewport Shipping Spine panel replaced the softer What Now. Ship-next verdict + per-product rows (objective / next / why it pays / evidence / blocker / safety / owner / done-when).

## Key fixes and findings

- **OpenFlowKit path was wrong**: `Projects/openflowkit` doesn't exist; real repo at `Desktop/openflowkit`. Fixed with fallback — spine/ship log/repo scan now see it. OpenFlowKit is privacy-first **voice dictation**, not "workflow templates" (roadmap corrected).
- **Spine logic proved itself first run**: MAZos scored highest (dirty tree + Ralph state conflict `.ralph/STATE.md` vs `.ralph/prd.json`) but was flagged BLOCKED → verdict routed to revenue work instead of cockpit polish.
- Concurrent local agent committed OpenWiki docs to both my branch and main → trivial AGENTS.md conflict, resolved keeping both lines.
- Stale Turbopack dev server crashed on CSS change (0xc0000142 worker spawn); restart via `start-mazos-local-stack.ps1` fixed it.

## Validation evidence

- `npm run lint` (tsc --noEmit): pass
- `npm run build`: pass; `/api/mazos/shipping-spine` in route table
- `GET 127.0.0.1:3047/health` → 200 · `GET 127.0.0.1:3047/api/mazos/shipping-spine` → 200 (bridge path verified)
- Current spine verdict at session end: land OpenFlowKit's fresh dirty work first, then JobFilter lead-to-paid conversion.

## Follow-up fix (same session)

Hosted `/api/mazos/shipping-spine` 500'd: snapshot write hits EROFS on Vercel's read-only filesystem. Fixed in PR #13 (merged, `005975e`): write wrapped in try/catch, hosted serves spine as bridge-less fallback with empty `savedTo`; UI hides snapshot name. Lesson: any `data/mazos/*` write must be optional on hosted.

## Open items / next session

- MAZos Ralph state conflict still open — resolve `.ralph/STATE.md` vs `.ralph/prd.json` before trusting loop progress.
- Roadmap next candidates: Proof Receipts or Safe Action Capsules — decide after a week of spine use.
- Playbook `currentBet` lines are code constants; revisit them as products move (they are the fallback when repo evidence is silent).
