---
date: 2026-07-07
project: mazos
agent: codex
status: completed
---
## What I did
- Implemented PR #37, "feat: add remote MAZos data layer", and merged it into `main`.
- Added and merged PR #38, "docs: add declutter one verdict spec", preserving the minimalist audit as an implementation spec.
- Added a remote-safe MAZos snapshot endpoint for Codex Mobile / hosted usage.
- Added token-gated snapshot publishing plus a remote intent queue so mobile can request work without directly executing local system actions.
- Added recursive redaction for local paths, env files, bearer tokens, API-key shaped secrets, and private spiritual terms.
- Added `npm run remote:publish` to publish a local snapshot to a remote push endpoint.
- Added `.gitignore` entries for generated `data/` and `tsconfig.tsbuildinfo`.
- Spawned specialized audit agents:
  - Minimalist UI audit: consolidate WORK clutter into a smaller Today / Loop Ops / Research shape.
  - Remote data architect: recommended local source of truth -> redacted snapshot -> hosted/mobile read model, with local-only execution.
  - Loop product strategist: recommended Run Inspector, Loop Inbox, and Cadence Controller as the next loop product line.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\.gitignore`
- `C:\Users\manaz\Projects\mazos-ui\package.json`
- `C:\Users\manaz\Projects\mazos-ui\scripts\mazos-publish-remote-snapshot.mjs`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\remote\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\remote\push\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\remote\intents\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\research\page.tsx`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\paths.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\remoteAuth.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\remoteSanitize.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\remoteSnapshot.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\remoteStore.ts`
- `C:\Users\manaz\Projects\mazos-ui\specs\declutter-one-verdict.md`

## Decisions made
- Mobile/hosted MAZos gets a sanitized read model, not raw localhost access.
- Mobile writes become queued intents only: `task_gate_request`, `mission_plan_request`, `research_request`, or `note_to_local_operator`.
- Hosted runtime requires remote tokens when configured; local development may run without them.
- V1 uses local file persistence for snapshots/intents and reports no persistent hosted store unless configured later.
- Next product direction should prioritize Run Inspector before broader loop automation.

## Verification
- `npm run lint` passed.
- `npm run build` passed.
- `GET http://127.0.0.1:3046/research` returned 200 and contained `Remote Snapshot`.
- `GET http://127.0.0.1:3046/api/mazos/remote` returned 4 prompts, 8 competitors, 6 loops, 3 mobile next items, and 0 redactions.
- `npm run remote:publish` stored a local snapshot.
- `POST http://127.0.0.1:3046/api/mazos/remote/intents` redacted a test Windows path and fake API key.
- GitHub Actions checks for PR #37 passed. Vercel status context remained pending after merge.
- GitHub Actions checks for PR #38 passed. Vercel status context remained pending after merge.

## Next steps
- Configure hosted secrets: `MAZOS_REMOTE_SYNC_TOKEN`, `MAZOS_REMOTE_READ_TOKEN`, and a persistent store if hosted snapshots should survive serverless restarts.
- Build Run Inspector as the main loop surface by grouping loop receipts into run timelines with evidence freshness, blockers, retries, and next actions.
- Add Loop Inbox for accept/defer/dismiss decisions across radar, research, and loops.
- Add Cadence Controller for due/stale/useful/retired loop scheduling.
- Continue decluttering the main WORK tab into a minimal Today / Loop Ops / Research structure.

---
date: 2026-07-07
project: mazos
agent: codex
status: completed
---
## What I did
- Implemented and merged PR #39, "feat: add mass competitor catalog".
- Added a simple mass competitor list with 53 tools across workflow automation, agent builders, coding agents, research/knowledge, observability/evals, and product operations.
- Added clear plain-English fields for every competitor: what it is, why MAZos should care, what to copy, what to avoid, and the MAZos move.
- Added `GET /api/mazos/mass-competitors`.
- Added a `Mass Competitor List` section to `/research` with top moves, grouped expandable sections, priority labels, and GitHub repo links where available.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\massCompetitors.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\mass-competitors\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\research\page.tsx`
- `C:\Users\manaz\Projects\mazos-ui\src\app\globals.css`

## Decisions made
- Kept the existing live Competitor Radar small and metadata-focused.
- Added the mass list as a separate static catalog so it stays easy to scan and explain.
- Used "copy now / study / watch" instead of complex scoring.
- Kept the wording simple enough for a product planning surface, not an analyst report.

## Verification
- `npm run lint` passed.
- `npm run build` passed.
- `GET http://127.0.0.1:3046/api/mazos/mass-competitors` returned 53 competitors, 15 copy-now items, and 6 groups.
- `GET http://127.0.0.1:3046/research` returned 200 and rendered `Mass Competitor List`.
- GitHub Actions checks for PR #39 passed. Vercel status context remained pending after merge.

## Next steps
- Convert the top catalog moves into Loop Factory presets: Run Inspector, Operator Inbox, Cadence Controller, Agent Workbench, and Loop Evals.
- Add per-competitor "send to loop" actions after the declutter pass so the page does not become another noisy dashboard.
- Optionally add live GitHub metadata to the mass list for open-source competitors, using the existing Competitor Radar fetch pattern.

---
date: 2026-07-07
project: mazos
agent: codex
status: completed
---
## What I did
- Resumed the interrupted AI Intelligence Engine work from the `.claude/worktrees/declutter` handoff.
- Implemented and merged PR #43, "feat: add ai intelligence engine".
- Added a local-first AI Source Inbox for messy AI links, notes, GitHub repos, MCPs, prompts, workflow ideas, AI Feed captions, and docs.
- Added deterministic source classification, dedupe, usefulness scoring, trust scoring, and forced actions.
- Added Skill Factory drafts with copyable skill specs, eval checklists, risk levels, and approval floor.
- Added Loop Store starter packs and copyable pack README generation.
- Added a compact `AI Intelligence Engine` section to the existing INTAKE tab instead of creating another page.
- Added Morning Brief AI Inbox and trust/cleanup summaries.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\specs\ai-intelligence-engine.md`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\trust.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\aiSourceInbox.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\skillFactory.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\loopStore.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\ai-source-inbox\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\skill-factory\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\loop-store\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\morningBrief.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\page.tsx`
- `C:\Users\manaz\Projects\mazos-ui\src\app\globals.css`

## Decisions made
- No scraping, no Instagram login, no external API calls, no auto-installing unknown code.
- Storage stays local JSON under `data/mazos/`.
- The intelligence engine lives in INTAKE as one compact section to avoid more dashboard clutter.
- Source-to-loop only prefills Loop Factory and switches to WORK; it never auto-saves a loop.
- Starter packs are seeded idempotently by `GET /api/mazos/loop-store`.

## Verification
- `npm run lint` passed.
- `npm run build` passed with the existing Turbopack/OpenWiki NFT trace warning.
- Worktree smoke on port 3051: source inbox POST added 3 items and skipped 0 duplicates.
- Worktree smoke: Skill Factory drafted a `context_management` skill with markdown.
- Worktree smoke: Loop Store returned 4 starter packs and a README with safety limits.
- Worktree smoke: Morning Brief included AI Source Inbox and trust sections.
- Main localhost 3046 after merge: AI Source Inbox returned 0 items, Loop Store returned 4 starter packs, Morning Brief included AI Inbox fields.
- GitHub Actions checks for PR #43 passed. Vercel status context remained pending after merge.

## Next steps
- Add formal `node:test` or repo-native tests once the project has a test runner decision.
- Add a Clutter Reaper pass over AI Source Inbox, Skill Factory, and Loop Store records.
- Add "source to competitor decision" wiring so copied/adapted/ignored competitor findings become reusable records.
- Add remote-safe AI Inbox summary to the Codex Mobile snapshot.
