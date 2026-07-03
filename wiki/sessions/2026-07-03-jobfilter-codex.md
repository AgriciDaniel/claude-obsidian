---
date: 2026-07-03
project: jobfilter
agent: codex
status: completed
---
## What I did
- Updated `AGENTS.md` with repo-backed regression commands for lead-engine/source-config, unified find-jobs, package-copy, and WhatsApp env checks.
- Added the current `/api/alerts` -> `/api/alerts/send` email-delivery workflow note with `RESEND_API_KEY` and optional `RESEND_FROM_EMAIL`.
- Verified the repo gates after installing local dependencies.

## Files changed
- `C:\Users\manaz\.codex\worktrees\8d8f\JobFilterV1\AGENTS.md`

## Decisions made
- Kept the edit scoped to existing command/workflow sections only.
- Did not add stale docs-only checks like `free-access-daily-tools-regression.mjs` because that script is retired and absent in this repo snapshot.

## Next steps
- If someone updates lead, pricing, WhatsApp, or alerts flows again, use the added regressions instead of rediscovering them from changelogs.
