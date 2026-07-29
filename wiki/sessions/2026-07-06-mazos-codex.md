---
date: 2026-07-06
project: mazos
agent: codex
status: completed
---
## What I did
- Started a Codex loop for the MAZos next-stage prompt pack after Claude merged PR #22.
- Confirmed latest MAZos main included Feed Operator Inbox, Flight Recorder, score breakdowns, and premium UI.
- Created isolated worktree branch `agents/next-stage-loop`.
- Added the next missing operating layer: server-side Morning Brief, Source Receipts / Context Map, and Agent Runtime Registry / Safety Console.
- Opened PR #23: https://github.com/manazoid4/mazos-ui/pull/23
- Continued loop iteration 2 after PR #23 merged: connected Context Map Source Receipts into Task Gate mission plans.
- Opened PR #24: https://github.com/manazoid4/mazos-ui/pull/24

## Files changed
- `src/lib/mazos/morningBrief.ts`
- `src/lib/mazos/sourceReceipts.ts`
- `src/lib/mazos/agentRuntimes.ts`
- `src/app/api/mazos/morning-brief/route.ts`
- `src/app/api/mazos/context-map/route.ts`
- `src/app/api/mazos/agent-runtimes/route.ts`
- `src/app/page.tsx`
- `src/app/globals.css`
- `README.md`
- `MAZOS_NEXT_STAGE_LOOP_REPORT.md`
- `src/lib/mazos/missionPlanner.ts`
- `src/app/sessions/page.tsx`

## Decisions made
- Did not rebuild features Claude already shipped in PR #22.
- Kept all new surfaces prompt/context/safety only: no shell launch, no LLM calls, no autonomous agent starts.
- Put server Morning Brief and Context Map in `NOW`; put Runtime Safety Console in `SYSTEM`.
- Kept Context Map receipts sensitive-aware so Windows-local vault/repo paths are clearly treated as local/private evidence.
- Mission plans should now carry receipt-backed context into Hermes prompts instead of relying on vague task text alone.

## Validation
- `npm run lint`: passed.
- `npm run build`: passed with existing non-fatal Next/Turbopack root/tracing warnings.
- `GET http://127.0.0.1:3052/api/mazos/morning-brief?project=MAZos`: 200.
- `GET http://127.0.0.1:3052/api/mazos/context-map?project=MAZos`: 200.
- `GET http://127.0.0.1:3052/api/mazos/agent-runtimes?task=improve%20mazos%20context`: 200.
- `GET http://127.0.0.1:3052/`: 200.
- Iteration 2: `npm run lint`: passed.
- Iteration 2: `npm run build`: passed.
- Iteration 2: `POST http://127.0.0.1:3053/api/mazos/mission-plan`: 200, returned 10 source receipts, and the Hermes prompt included `SOURCE RECEIPTS`.

## Next steps
- Wait for PR #24 CI/automerge.
- Vercel production deploy for PR #23 was still building after local/GitHub success; recheck hosted alias later.
- Add a dedicated `/context` page with saved project views and missing-knowledge cleanup.
- Link Flight Recorder sessions to runtime recommendations and context receipts.

---

## Loop Factory Product Line Research

## What I did
- Confirmed MAZos local readiness fix from PR #28 and explained how `/api/mazos/system` reads local system info.
- Researched current loop-engineering practice using latest GitHub metadata, primary docs, and current public loop-engineering writing.
- Checked live GitHub repo signals for `n8n`, `opencode`, `OpenHands`, `AutoGen`, `CrewAI`, `LangGraph`, `OpenAI Agents SDK`, `Mastra`, `loop-engineering`, and `ospec`.
- Added a MAZos product-line research brief and opened PR #29: https://github.com/manazoid4/mazos-ui/pull/29

## Files changed
- `research/mazos/LOOP_FACTORY_PRODUCT_LINE_RESEARCH_2026-07-06.md`

## Decisions made
- Treat Loop Factory as the first product in a broader loop product line, not a one-off prompt generator.
- Default MAZos loops to report-only/read-only unless the user explicitly graduates them to assisted writes or PR-only operation.
- Make latest GitHub metadata, source freshness, evidence receipts, safety levels, and verifier roles core loop fields.
- Prioritize the next MAZos PRs around Loop Doctor, Loop Pattern Library, Loop Receipts, Product Loop Packs, and Loop Simulator.

## Validation
- `npm run build`: passed in `C:\Users\manaz\Projects\mazos-ui`.
- Build still shows pre-existing non-fatal Next/Turbopack warnings around workspace root inference and dynamic `openWiki.ts` tracing.

## Next steps
- Merge PR #29 after review.
- Implement Loop Doctor first so MAZos can grade useless vs useful loops before adding more automation.
- Add curated Product Loop Packs for Competitor Intelligence, GitHub Pulse, and Useless Feature Reaper.

---

## Multiple Deep Research Tracks

## What I did
- Ran multiple MAZos research tracks after the Loop Factory product-line brief.
- Confirmed the Gemini-backed `deep-research` skill could not run because `GEMINI_API_KEY` is not configured, then completed the work manually with live web/GitHub research.
- Checked latest GitHub metadata for workflow automation, agent runtime, loop-engineering, and coding-agent repos.
- Audited MAZos current surfaces against usefulness criteria: clear next action, source freshness, evidence receipts, human gates, product value, and loop fit.
- Opened PR #30: https://github.com/manazoid4/mazos-ui/pull/30

## Files changed
- `research/mazos/MULTI_DEEP_RESEARCH_INDEX_2026-07-06.md`
- `research/mazos/DEEP_RESEARCH_WORKFLOW_AUTOMATION_2026-07-06.md`
- `research/mazos/DEEP_RESEARCH_AGENT_RUNTIME_LOOP_ENGINEERING_2026-07-06.md`
- `research/mazos/DEEP_RESEARCH_CODING_AGENT_PRODUCTS_2026-07-06.md`
- `research/mazos/DEEP_RESEARCH_MAZOS_USEFULNESS_AUDIT_2026-07-06.md`

## Decisions made
- MAZos should not become a generic workflow canvas, generic coding IDE, or hidden autonomous deployer.
- The strongest wedge is a local-first cockpit that turns project state, competitor research, GitHub activity, vault memory, and agent work into safe receipt-backed loops.
- Keep and strengthen Loop Factory, Feed/Loop Inbox, Flight Recorder, Context Map, Shipping Spine, Task Gate, and Morning Brief.
- Demote or merge Action Matrix, raw Ship Log, standalone Tool Router, and broad dashboard surfaces unless they feed loop receipts.
- Build Loop Doctor next before adding more automation.

## Validation
- `npm run build`: passed in `C:\Users\manaz\Projects\mazos-ui`.
- Build still shows pre-existing non-fatal Next/Turbopack warnings around workspace root inference and dynamic `openWiki.ts` tracing.

## Next steps
- Wait for PR #30 checks/automerge.
- Implement `loopPatterns.ts` and Loop Doctor as the next code PR.
- Use the new research reports as the source of truth for Product Loop Packs and Loop Receipts.

---

## Research Console And Loop Doctor

## What I did
- Continued after the multi-track research pass and turned the reports into a usable MAZos surface.
- Added `/research`, a sleek local-first Research Console that reads saved markdown reports, extracts sources, next actions, usefulness tags, and a copy-ready automation prompt.
- Added `/api/mazos/research` so future agents/scripts can consume research reports instead of scraping chat history.
- Opened and merged PR #31: https://github.com/manazoid4/mazos-ui/pull/31
- Continued into the next research-backed feature: Loop Doctor.
- Added deterministic loop usefulness audits across built-in, custom, and drafted loops.
- Opened PR #32: https://github.com/manazoid4/mazos-ui/pull/32

## Files changed
- `src/lib/mazos/research.ts`
- `src/app/api/mazos/research/route.ts`
- `src/app/research/page.tsx`
- `src/lib/mazos/loopFactory.ts`
- `src/app/api/mazos/loops/route.ts`
- `src/app/page.tsx`
- `src/app/globals.css`

## Decisions made
- Research is now a product surface and API, not just saved docs.
- Loop Doctor scores loops on trigger clarity, source policy, latest GitHub/source freshness, evidence, verifier, safety, stop conditions, and product impact.
- WORK tab should show a compact keep/revise/merge/remove audit before adding more loops.
- Screenshot automation was attempted but blocked by missing/incomplete local Playwright packages; kept build, API, and HTML checks as verification.

## Validation
- Research Console PR #31: `npm run lint`, `npm run build`, `/research` 200, `/api/mazos/research` returned 6 reports, 24 sources, and 10 queued next actions.
- Loop Doctor PR #32: `npm run lint`, `npm run build`, `/api/mazos/loops` returned 6 audited loops; first loop scored `83 keep`.
- Builds still show pre-existing non-fatal Next/Turbopack warnings around workspace root inference and dynamic `openWiki.ts` tracing.

## Next steps
- Wait for PR #32 checks/automerge.
- After Loop Doctor lands, build typed Product Loop Packs: Competitor Intelligence, GitHub Pulse, and Useless Feature Reaper.
- Add Loop Receipts so Research Console and Loop Doctor can attach evidence to every recommendation.

---

## Product Loop Packs

## What I did
- Continued after Loop Doctor and added first-class Product Loop Packs to Loop Factory.
- Added GitHub Pulse, Useless Feature Reaper, Revenue Radar, and Founder Inbox patterns.
- Kept existing Competitor Intelligence as the research-intelligence pack.
- Added auto-classification terms so goals route into the right loop pack.
- Opened PR #33: https://github.com/manazoid4/mazos-ui/pull/33

## Files changed
- `src/lib/mazos/loopFactory.ts`
- `src/app/page.tsx`

## Decisions made
- Product Loop Packs should be typed Loop Factory patterns, not one-off UI cards.
- Every pack must include source policy, safety ceiling, evidence requirements, stop conditions, and human gates.
- New packs default to L1 report-only because receipts and simulator are not yet fully built.

## Validation
- `npm run lint`: passed.
- `npm run build`: passed.
- Local loop-factory API drafted all four new packs successfully:
  - `github-pulse`: `89 keep`, `100 ready`
  - `useless-feature-reaper`: `100 keep`, `100 ready`
  - `revenue-radar`: `100 keep`, `100 ready`
  - `founder-inbox`: `89 keep`, `100 ready`

## Next steps
- Wait for PR #33 checks/automerge.
- Build Loop Receipts next so Research Console, Loop Doctor, and Product Loop Packs can preserve evidence across runs.

---

## Competitor Emulation: Loop Receipts

## What I did
- Treated competitor "copy" as product-pattern emulation, not code copying.
- Refreshed latest GitHub metadata for n8n, Dify, Activepieces, LangGraph, AutoGen, CrewAI, OpenHands, opencode, Codex, Cline, Continue, Aider, loop-engineering, and OSpec.
- Implemented Loop Receipts as the shared MAZos equivalent of execution history, workflow artifacts, durable state, and agent traces.
- Opened PR #34: https://github.com/manazoid4/mazos-ui/pull/34

## Files changed
- `src/lib/mazos/loopReceipts.ts`
- `src/app/api/mazos/loop-receipts/route.ts`
- `src/app/api/mazos/loops/route.ts`
- `src/lib/mazos/flightRecorder.ts`
- `src/lib/mazos/paths.ts`
- `src/app/page.tsx`

## Decisions made
- Emulate n8n/GitHub Actions execution history through append-only loop receipts.
- Emulate LangGraph/Temporal durable state by making every loop event replayable.
- Emulate OpenAI Agents tracing/OpenHands/opencode by preserving actions, evidence, risk flags, and next-run suggestions.
- Keep receipts local-first and report-only; no new autonomous execution.

## Validation
- `npm run lint`: passed.
- `npm run build`: passed.
- `POST /api/mazos/loops` start event created a `started` receipt for `daily_triage_l1`.
- `GET /api/mazos/loop-receipts?loopId=daily_triage_l1` returned the receipt.
- `GET /api/mazos/loops` included receipt summaries.
- Verification created local runtime files under `data/mazos`; these stayed untracked.

## Next steps
- Wait for PR #34 checks/automerge.
- Continue competitor emulation with a GitHub Pulse snapshot API and competitor feature matrix.

---

## Research Roadmap And Competitor Radar

## What I did
- Spawned a specialized research strategist subagent, Lovelace, to define four big research prompts and a next-step roadmap.
- Added those four prompts to the MAZos Research Console:
  - Execution Observability
  - Durable Human-Gated Loop Runtime
  - Agent Workbench / Mission Control UX
  - Competitor Pattern Library + Loop Marketplace
- Implemented the subagent's top recommendation: Competitor Radar / Feature Matrix.
- Added live GitHub-backed competitor snapshots for n8n, Dify, Activepieces, LangGraph, OpenHands, opencode, Codex, and OSpec.
- Opened PR #35: https://github.com/manazoid4/mazos-ui/pull/35

## Files changed
- `src/lib/mazos/competitorRadar.ts`
- `src/app/api/mazos/competitor-radar/route.ts`
- `src/lib/mazos/research.ts`
- `src/app/research/page.tsx`
- `src/app/globals.css`

## Decisions made
- Research prompts should be first-class app data, not only chat output.
- Competitor emulation should be copy/adapt/ignore guidance backed by latest GitHub metadata and official docs links.
- Next implementation focus after this PR should be a Run Inspector that upgrades Loop Receipts from JSON logs into a usable timeline.

## Validation
- `npm run lint`: passed.
- `npm run build`: passed.
- `GET /api/mazos/competitor-radar`: returned 8 snapshots with live GitHub stars/pushed metadata.
- `GET /api/mazos/research`: returned 4 research prompts and 4 roadmap steps.
- `GET /research`: rendered Competitor Radar and Four Big Research Prompts.

## Next steps
- Wait for PR #35 checks/automerge.
- Build Run Inspector next: step timeline, evidence diffs, input/output summaries, retry/failure state, and next-run suggestions.
