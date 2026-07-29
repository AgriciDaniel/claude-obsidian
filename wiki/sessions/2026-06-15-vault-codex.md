---
date: 2026-06-15
project: vault
agent: codex
status: completed
---

## What I did

- Pulled the vault from `fork main`.
- Added GitHub and local PC location metadata to active project notes.
- Added a missing JobFilter project index.
- Added a central project locations index.
- Updated the top-level wiki index to link to active project notes.
- Cleaned the project metadata layout so repeated GitHub/location blocks are only kept where useful.

## Files changed

- `wiki/index.md`
- `wiki/projects/project-locations.md`
- `wiki/projects/jobfilter/index.md`
- `wiki/projects/flipsignal/index.md`
- `wiki/projects/inkweave/overview.md`
- `wiki/projects/inkweave/project-outline.md`
- `wiki/projects/khutba.io/overview.md`
- `wiki/projects/khutba.io/project-outline.md`
- `wiki/projects/openflowkit/overview.md`
- `wiki/projects/openflowkit/next-steps.md`
- `wiki/projects/recall/index.md`
- `wiki/sessions/2026-06-15-vault-codex.md`

## Decisions made

- Used verified local git remotes where available.
- Kept `wiki/projects/project-locations.md` as the clean central project map.
- Noted Recall's on-disk git remote still points to `saved-brain` while the project note uses the current Recall GitHub URL.

## Next steps

- Optionally add missing dedicated project folders for Zawiya and Vault if they should have their own long-form wiki pages.
