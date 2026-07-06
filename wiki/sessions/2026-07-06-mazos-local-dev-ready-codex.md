---
date: 2026-07-06
project: mazos
agent: codex
status: completed
---
## What I did
- Investigated Maz's report that Loop Factory was not really ready locally.
- Confirmed GitHub `origin/main` had advanced to `3324fc6` / PR #27.
- Updated local `main` to track `origin/main` while preserving unrelated dirty runtime/generated files.
- Confirmed `/api/mazos/loop-factory` drafts and saves locally.
- Confirmed `/api/mazos/loops` includes the saved `JobFilter Competitor Intelligence` loop.
- Found the local UI-level issue in `.next/dev/logs/next-development.log`: Next dev was blocking HMR resources when the app was opened at `127.0.0.1`.
- Added `allowedDevOrigins: ['127.0.0.1']` in `next.config.js`.
- Restarted the local dev server on port `3046`.
- Opened PR #28: https://github.com/manazoid4/mazos-ui/pull/28

## Files changed
- `next.config.js`
- Vault session note: `wiki/sessions/2026-07-06-mazos-local-dev-ready-codex.md`

## Decisions made
- Keep the fix minimal: allow the existing local bridge/API origin instead of changing app URLs or bridge behavior.
- Leave unrelated local dirt untouched: `data/`, `tsconfig.tsbuildinfo`, `research/mazos/latest-vault-scan.md`, and `external/agent-sources/penpot`.

## Next steps
- Watch PR #28 CI/automerge.
- Use `http://127.0.0.1:3046` or `http://localhost:3046`; both should now serve the local Loop Factory route cleanly after restart.

## Validation
- `npm run lint`: passed.
- `npm run build`: passed with existing workspace-root/openWiki tracing warnings.
- Fresh local dev server on `3046`: ready.
- `GET http://127.0.0.1:3046/`: 200.
- `GET http://127.0.0.1:3046/api/mazos/loop-factory`: 200, `customLoopCount=1`.
- Fresh dev log no longer showed the 127.0.0.1 cross-origin block.
