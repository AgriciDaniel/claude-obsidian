---
date: 2026-07-03
project: mazos
agent: codex
status: completed
---
## What I did
- Fixed the hosted MAZos limitation where Vercel could not read Windows-local repo/vault paths directly.
- Added a local Windows bridge:
  - script: `scripts/mazos-local-bridge.mjs`
  - command: `npm run bridge`
  - listens on `http://127.0.0.1:3047`
  - proxies only `/api/mazos/*` to local MAZos at `http://127.0.0.1:3046`
- Updated the hosted React app so, when opened from `*.vercel.app`, it tries the local bridge first for MAZos API calls and falls back to hosted APIs if the bridge is offline.
- Added a visible bridge status banner showing whether local Windows access is connected.
- Documented the hosted + local bridge flow in `README.md`.
- Opened and merged PR #7:
  - `https://github.com/manazoid4/mazos-ui/pull/7`
- Deployed the bridge-enabled version to production:
  - `https://mazos-command-centre.vercel.app`
- Started the bridge as a hidden background PowerShell process on this PC.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\README.md`
- `C:\Users\manaz\Projects\mazos-ui\package.json`
- `C:\Users\manaz\Projects\mazos-ui\scripts\mazos-local-bridge.mjs`
- `C:\Users\manaz\Projects\mazos-ui\src\app\page.tsx`
- `C:\Users\manaz\Projects\mazos-ui\src\app\globals.css`
- `C:\Users\manaz\claude-obsidian\wiki\sessions\2026-07-03-mazos-codex.md`

## Decisions made
- Did not attempt to make Vercel servers read `C:\Users\manaz` directly, because cloud functions cannot access a private Windows filesystem.
- Used browser-to-localhost bridge access instead: hosted page -> `127.0.0.1:3047` -> local MAZos -> Windows paths.
- Kept bridge scope narrow: `/api/mazos/*` only.
- Left generated/runtime local files out of git: `data/`, `research/mazos/latest-vault-scan.md`, `tsconfig.tsbuildinfo`.
- Left the dirty Penpot submodule checkout untouched.

## Verification
- `npm run build` passed.
- `npm run lint` passed after build regenerated `.next/types`.
- Bridge health returned 200:
  - `http://127.0.0.1:3047/health`
- Bridge proxied local Windows repo data:
  - `http://127.0.0.1:3047/api/mazos/repos`
  - `http://127.0.0.1:3047/api/mazos/project-status?project=MAZos`
- Live production checks returned 200:
  - `https://mazos-command-centre.vercel.app`
  - `https://mazos-command-centre.vercel.app/api/mazos`
- Live client bundle contains the bridge code (`127.0.0.1:3047`).
- Production deployment ready:
  - `dpl_2FrrPXUTaXGhEAdWJ72oNkqazADd`
- PR #7 merged into main:
  - `8f1fc07 feat: add hosted local bridge for Windows paths`

## Next steps
- When using the hosted site, keep both local processes running:
  - `npm run dev -- -p 3046`
  - `npm run bridge`
- Consider adding a Windows startup shortcut or scheduled task for the bridge if this becomes daily workflow.
- Consider adding token auth to the bridge if it ever listens beyond `127.0.0.1`.

## Addendum: automatic local stack startup

## What I did
- Added `C:\Users\manaz\Projects\mazos-ui\scripts\start-mazos-local-stack.ps1`.
- Registered Windows Scheduled Task `MAZos Local Stack`.
- Configured it to run at user logon.
- The launcher starts:
  - MAZos local app on `3046` with `npm run dev -- -p 3046`
  - MAZos local bridge on `3047` with `npm run bridge`
- The launcher checks ports first and does not start duplicate processes if the app or bridge is already listening.
- Updated `README.md` with the scheduled task name and behavior.
- Opened and merged PR #8:
  - `https://github.com/manazoid4/mazos-ui/pull/8`

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\README.md`
- `C:\Users\manaz\Projects\mazos-ui\scripts\start-mazos-local-stack.ps1`
- `C:\Users\manaz\claude-obsidian\wiki\sessions\2026-07-03-mazos-codex.md`

## Verification
- Ran the launcher manually. It detected existing listeners and skipped duplicates.
- Ran the scheduled task manually with `Start-ScheduledTask`.
- Scheduled task last result: `0`.
- Ports verified listening:
  - `3046`
  - `3047`
- `npm run lint` passed.
- `npm run build` passed.
- PR #8 merged into main as:
  - `ff58eb0 chore: auto-start MAZos local stack`

## Next steps
- After next Windows login, MAZos local app and bridge should start automatically.
- If it ever fails, check logs under `C:\Users\manaz\Projects\mazos-ui\data\mazos\logs`.
