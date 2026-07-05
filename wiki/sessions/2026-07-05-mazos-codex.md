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
