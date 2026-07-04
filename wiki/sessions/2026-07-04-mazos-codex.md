---
date: 2026-07-04
project: mazos
agent: codex
status: completed
---

## What I did

- Verified MAZos is accessible locally at `http://127.0.0.1:3046`.
- Verified the hosted-to-local bridge is healthy at `http://127.0.0.1:3047/health`.
- Verified bridge repo access responds at `http://127.0.0.1:3047/api/mazos/repos`.
- Verified hosted MAZos responds at `https://mazos-command-centre.vercel.app`.
- Confirmed the Windows scheduled task `MAZos Local Stack` exists and was previously returning success, with the local app and bridge listening on ports `3046` and `3047`.
- Spawned planning agent Avicenna (`019f2cb9-8f45-7e73-8a8d-1be68bf7d07f`) to plan the next MAZos market-breaker stage.
- Saved agent access instructions for Codex, Claude/Hermes, and OpenCode in repo docs and live Hermes context.
- Saved Avicenna's roadmap into the repo, Hermes export, live Hermes folder, and Local Knowledge memory.
- Merged MAZos PR #9: `https://github.com/manazoid4/mazos-ui/pull/9`.

## Files changed

- `C:\Users\manaz\Projects\mazos-ui\AGENTS.md`
- `C:\Users\manaz\Projects\mazos-ui\config\hermes_export\MAZOS_ACCESS.md`
- `C:\Users\manaz\Projects\mazos-ui\config\hermes_export\MAZOS_MARKET_BREAKER_ROADMAP.md`
- `C:\Users\manaz\Projects\mazos-ui\docs\MAZOS_MARKET_BREAKER_ROADMAP.md`
- `C:\Users\manaz\.hermes\mazos\MAZOS_ACCESS.md`
- `C:\Users\manaz\.hermes\mazos\MAZOS_MARKET_BREAKER_ROADMAP.md`

## Decisions made

- MAZos should be positioned as a local-first, hosted-accessible AI operating cockpit for shipping Maz's products.
- The current moat is hosted convenience plus private Windows-local repo/vault truth through a narrow localhost bridge.
- The next build should be Shipping Spine v1, not more generic dashboard panels.
- MAZos should prioritize JobFilter and Recall revenue work over MAZos polish unless MAZos infrastructure is directly blocking product velocity.

## Next steps

- Build Shipping Spine v1:
  - Add product playbooks for JobFilter, Recall, OpenFlowKit, and MAZos.
  - Add `/api/mazos/shipping-spine`.
  - Combine project status, ship log, stale radar, decisions, and playbooks.
  - Put the Shipping Spine first on the NOW view.
  - Show product, objective, next action, evidence, blocker, safety, owner, and done criteria.
- Verify with `npm run lint` and `npm run build`.

## Verification

- `npm run lint` passed in `C:\Users\manaz\Projects\mazos-ui`.
- `GET http://127.0.0.1:3047/health` returned 200.
- `GET http://127.0.0.1:3047/api/mazos/repos` returned 200.
- `GET https://mazos-command-centre.vercel.app` returned 200.

## Notes

- Left unrelated/generated local dirty paths untouched:
  - `C:\Users\manaz\Projects\mazos-ui\external\agent-sources\penpot`
  - `C:\Users\manaz\Projects\mazos-ui\research\mazos\latest-vault-scan.md`
  - `C:\Users\manaz\Projects\mazos-ui\data\`
  - `C:\Users\manaz\Projects\mazos-ui\tsconfig.tsbuildinfo`

## OpenWiki Install and Agent Access

Completed on 2026-07-04:

- Installed `kdsz001/OpenWiki` v0.3.17 on Windows.
- Verified the Windows installer SHA-256 against the GitHub release digest:
  `4c0fef09009f2a59c1a29270bd69864fa98fef469b528f7005af53aea944d22d`.
- App path: `C:\Users\manaz\AppData\Local\OpenWiki\OpenWiki.exe`.
- Database path: `C:\Users\manaz\AppData\Roaming\com.openwiki.app\openwiki.db`.
- Source clone: `C:\Users\manaz\Projects\openwiki`.
- Hermes clone: `C:\Users\manaz\.hermes\external-sources\openwiki`.
- MAZos docs PR merged: `https://github.com/manazoid4/mazos-ui/pull/10`.
- Merge commit: `5da40a0b23518e47afffc394c2dc2c798558b3f3`.
- Added Windows scheduled task: `OpenWiki Local Knowledge App`.
- Scheduled-task starter script: `C:\Users\manaz\.hermes\openwiki\start-openwiki.ps1`.
- Verified the scheduled task returns result `0` when OpenWiki is already running.
- Configured MCP server name `openwiki` in:
  - `C:\Users\manaz\AppData\Roaming\Claude\claude_desktop_config.json`
  - `C:\Users\manaz\.openclaw\openclaw.json`
  - `C:\Users\manaz\.codex\config.toml`
- Seeded OpenWiki with three wiki pages:
  - `OpenWiki Local Install and Agent Access`
  - `MAZos Agent Access and Market-Breaker Roadmap`
  - `OpenWiki GitHub Capability Summary`
- Follow-up docs PR merged: `https://github.com/manazoid4/mazos-ui/pull/12`.
- Follow-up merge commit: `d5240e0fd178ea8696c84b9d662f5b7cce142d1d`.

Manual next step:

- Open OpenWiki and configure Settings -> AI with the preferred provider if in-app wiki compilation, reports, or Q&A should use Claude/OpenAI/Gemini/Ollama/LM Studio.

## Agent Task Gate and Mission Planner

Completed on 2026-07-04:

- Added MAZos Agent Task Gate at `/sessions`.
- Added `GET /api/mazos/task-gate`.
- Added `POST /api/mazos/task-gate`.
- Added `POST /api/mazos/mission-plan`.
- Added scoring from 0 to 100 with risk levels `safe`, `caution`, and `danger`.
- Added prompt repair, default forbidden actions, Research First toggle, Make Smaller 3-session split, validation command suggestions, and saved mission plans.
- Added docs in `README.md`.
- Added report `MAZOS_TASK_GATE_REPORT.md`.
- Merged MAZos PR #14: `https://github.com/manazoid4/mazos-ui/pull/14`.
- Merge commit: `aca06d02f082048c76c7b0e84ac7c066687c3b72`.

Validation:

- `npm run lint` passed.
- `npm run build` passed.
- `GET http://127.0.0.1:3046/sessions` returned 200.
- `POST http://127.0.0.1:3046/api/mazos/task-gate` returned a scored gate result.
- `POST http://127.0.0.1:3046/api/mazos/mission-plan` generated a saved markdown mission plan.
