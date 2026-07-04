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
