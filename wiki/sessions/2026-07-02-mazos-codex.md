---
date: 2026-07-02
project: mazos
agent: codex
status: completed
---
## What I did
- Created a new Vercel project for MAZos:
  - site/project name: `mazos-command-centre`
  - production URL: `https://mazos-command-centre.vercel.app`
  - Vercel project: `manazir-s-projects1/mazos-command-centre`
- Linked local repo `C:\Users\manaz\Projects\mazos-ui` to Vercel.
- Connected Vercel project to GitHub repo `https://github.com/manazoid4/mazos-ui`.
- Added `.vercelignore` so deployment does not upload local runtime data, vault scans, or huge external-source worktrees.
- Let Vercel add `.vercel` to `.gitignore` so local project-link metadata stays out of git.
- Deployed MAZos to Vercel production.
- Opened and merged PR #6 for deploy hygiene:
  - `https://github.com/manazoid4/mazos-ui/pull/6`
- Confirmed PR #5 had already merged the command-centre work into main:
  - `https://github.com/manazoid4/mazos-ui/pull/5`

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\.gitignore`
- `C:\Users\manaz\Projects\mazos-ui\.vercelignore`
- `C:\Users\manaz\claude-obsidian\wiki\sessions\2026-07-02-mazos-codex.md`

## Decisions made
- Did not commit `.vercel/project.json`; it remains local metadata.
- Excluded `data/`, `research/`, `external/`, `.ralph/`, loop files, `.next/`, and `node_modules/` from Vercel uploads.
- Kept remaining local runtime/generated MAZos files out of git.
- Left the dirty Penpot submodule checkout untouched because resetting it would be destructive inside the submodule.

## Verification
- `npm run lint` passed before deployment.
- `npm run build` passed before deployment.
- Vercel production deployment completed with status `READY`.
- Deployment id: `dpl_AzS6eysZ2qRVgri3eFwczq4iDXb2`.
- `vercel inspect mazos-command-centre-1zsur9uti-manazir-s-projects1.vercel.app` reported status `Ready`.
- Live production checks returned HTTP 200 for:
  - `https://mazos-command-centre.vercel.app`
  - `https://mazos-command-centre.vercel.app/api/mazos`
  - `https://mazos-command-centre.vercel.app/api/mazos/health`
  - `https://mazos-command-centre.vercel.app/api/mazos/tool-router?q=browser%20automation`
- PR #6 merged into main as `9078107 chore: prepare MAZos for Vercel deployment`.

## Next steps
- Review the hosted site visually at `https://mazos-command-centre.vercel.app`.
- Decide whether MAZos should show a hosted/cloud-safe banner because Vercel cannot access Windows-local repos and vault paths the same way local MAZos can.
- If needed, clean local generated files separately: `data/`, `research/mazos/latest-vault-scan.md`, `tsconfig.tsbuildinfo`, and dirty Penpot submodule checkout.
