---
date: 2026-07-05
project: mazos
agent: codex
status: completed
---

## What I did
- Implemented the MAZos OpenWiki Cockpit Integration.
- Added a first-class `/openwiki` page and dashboard `OPENWIKI` nav link.
- Added `GET /api/mazos/openwiki` and safe `POST /api/mazos/openwiki` prompt actions.
- Added OpenWiki health scoring, process/task/path checks, SQLite counts, latest wiki pages, knowledge gaps, MCP reminders, copyable Hermes/Codex prompts, and launch-command prompt.
- Added OpenWiki to Ops Radar/service health and Tool Router routing.
- Added docs, implementation report, and a concise next-agent build prompt.
- Opened PR #15, merged it, removed a stale stuck Vercel preview deployment, and verified production.

## Files changed
- `README.md`
- `docs/OPENWIKI_LOCAL_INSTALL.md`
- `MAZOS_OPENWIKI_INTEGRATION_REPORT.md`
- `MAZOS_OPENWIKI_NEXT_AGENT_PROMPT.txt`
- `src/app/page.tsx`
- `src/app/openwiki/page.tsx`
- `src/app/api/mazos/openwiki/route.ts`
- `src/app/globals.css`
- `src/lib/mazos/openWiki.ts`
- `src/lib/mazos/paths.ts`
- `src/lib/mazos/serviceHealth.ts`
- `src/lib/mazos/toolRouter.ts`

## Decisions made
- Scoped the work to MAZos integration, not editing upstream `kdsz001/OpenWiki`.
- Kept OpenWiki actions prompt-only because `config/control-panel.yaml` has `allow_shell: false`.
- Kept OpenWiki database access read-only; no SQLite mutation from MAZos.
- Used the existing MAZos hosted/local bridge pattern so Vercel can call `/api/mazos/openwiki` through the local bridge when Windows-local data is needed.
- Left unrelated dirty state alone: `external/agent-sources/penpot`, `research/mazos/latest-vault-scan.md`, `data/`, and `tsconfig.tsbuildinfo`.

## Validation
- `npm run lint`: passed.
- `npm run build`: passed with non-fatal Turbopack warnings about local Windows/Python tracing and root lockfile inference.
- Local `GET http://127.0.0.1:3046/api/mazos/openwiki`: passed.
- Local `http://127.0.0.1:3046/openwiki`: returned 200.
- Hosted `https://mazos-command-centre.vercel.app/openwiki`: returned 200.
- Hosted `https://mazos-command-centre.vercel.app/api/mazos/openwiki`: returned 200.

## GitHub / Vercel
- PR: `https://github.com/manazoid4/mazos-ui/pull/15`
- Merge commit: `bf830e2a570263f4867eaf84c264fc466ade33dd`
- Production deployment: `dpl_Fmf5opWMWaqe3ThdqiUY2C9iqRDb`
- Production URL: `https://mazos-command-centre.vercel.app/openwiki`

## Next steps
- Seed OpenWiki with project-specific pages for MAZos, Recall, JobFilter, OpenFlowKit, and Hermes.
- Add OpenWiki-to-Obsidian export/handoff flow while preserving prompt-first safety.
- Add agent memory diff across OpenWiki, Obsidian, GitHub, and MAZos session state before launching tasks.

## Addendum — AI Feed Spec
- Read the attached `MazOS AI Feed — Research-Further Prompt`.
- Completed the requested build-ready spec at `specs/mazos-ai-feed.md`.
- The spec recommends a deterministic v1 `FEED` tab plus `GET /api/mazos/feed`, aggregating Shipping Spine, decisions, runs, ship log, stale radar, intake queue, and OpenWiki status.
- The spec rejects LLM calls, external RSS/web crawling, Supabase/KV, cron, and autonomous execution for v1.
- Added ranking rules, item schema, API contract, storage/ingestion/placement options, safety notes, done criteria, and a concise next-agent build prompt.
- PR #16 merged: `https://github.com/manazoid4/mazos-ui/pull/16`
- Merge commit: `746c355c2f1f8b9d2ac21d3426a5e8ba0b69b0e3`
- Validation: `npm run lint` passed locally.
- Vercel preview passed. Production deployment `dpl_AcibPDkMNvmdLQKefAjsq8Fzn3xJ` reached Ready and is aliased to `https://mazos-command-centre.vercel.app`.

## Addendum — AI Feed Implementation
- Implemented the deterministic MAZos AI Feed v1 from `specs/mazos-ai-feed.md`.
- Added `GET /api/mazos/feed`.
- Added `src/lib/mazos/feed.ts` to aggregate Shipping Spine, Decision Inbox, run history, Stale Work Radar, Ship Log, intake queue, and OpenWiki status.
- Added the cockpit `FEED` tab with verdict, attention/product/type filters, evidence modal, copyable prompts, score, source, and safety badges.
- Updated `README.md` and `MAZOS_AI_FEED_REPORT.md`.
- PR #17 merged: `https://github.com/manazoid4/mazos-ui/pull/17`
- Merge commit: `e2880cd9bdeed6d35440046ea5b70baae6c64a0d`
- Follow-up report PR #18 merged: `https://github.com/manazoid4/mazos-ui/pull/18`
- Follow-up merge commit: `778b82e0edd059ff35516295dc127f92a71ad064`
- Validation: `npm run lint` passed, `npm run build` passed, local `GET http://127.0.0.1:3046/api/mazos/feed` passed, hosted `GET https://mazos-command-centre.vercel.app/api/mazos/feed` passed.
- Production deployment for PR #17: `dpl_obMah8Nezzf6WgyDrGwfLMV7uoB7`, Ready and aliased to `https://mazos-command-centre.vercel.app`.
- Final report deployment for PR #18: `dpl_2DYo3f3MY46zGYpfd2DEmCTJhCCP`, Ready and aliased to `https://mazos-command-centre.vercel.app`.

## Addendum — GitHub Inspiration Research Lane 1
- Researched GitHub inspiration for local-first AI dashboards, agent cockpits, LLM observability feeds, homelab dashboards, and personal knowledge OS patterns relevant to MAZos.
- Prioritized patterns that fit MAZos current direction: deterministic feed, local/private state, hosted-to-local bridge, agent task gate, OpenWiki/Obsidian evidence, and prompt-first safety.
- Strongest external patterns found:
  - TMA1-style agent-readable observability context.
  - AgentLens-style append-only flight recorder/audit trail.
  - OpenClaw Command Center-style unified state endpoint with SSE and read-only default.
  - Mission Control/LiteLLM-style runtime registry and task/agent control plane.
  - PersonalOS/Life-OS-style plain-text local operating memory.
- Recommended MAZos build ideas:
  - AI Feed as flight recorder plus action inbox.
  - Cockpit unified state endpoint with live local bridge updates.
  - Agent preflight/diff view across Obsidian, OpenWiki, GitHub, runs, decisions, and ship log before task launch.

