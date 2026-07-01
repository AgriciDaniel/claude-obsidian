---
date: 2026-07-01
project: MazOS
branch: agents/mazos-command-centre-next
pr: https://github.com/manazoid4/mazos-ui/pull/4
base_pr: https://github.com/manazoid4/mazos-ui/pull/3
safety: L3 (branch/PR — no push to main)
type: session
---

# MAZos Command Centre — Next Stage

## Mission
Turn MAZos from a daily cockpit into a practical AI operating command centre: tell the
user what matters now, why, what evidence supports it, and which tool/agent should handle it.

## Shipped
1. **Ranked "What Now"** — `src/lib/mazos/commandCentre.ts`. Ranks JobFilter, Recall,
   MAZos, and vault by urgency + blocker state + money impact + freshness. Priority stack
   with per-factor scores. Money weighting: JobFilter high, Recall/OpenFlowKit medium, MAZos/vault low.
2. **Tool Router** — `src/lib/mazos/toolRouter.ts` + `src/app/api/mazos/tool-router/route.ts`.
   Task → best installed source with one-line why. Registry mirrors `external/agent-sources`
   submodules. Each source carries a safety ceiling + read-first file.
3. **Safety levels L1–L5** — `src/lib/mazos/safety.ts`. Every action mapped; default report-only (L1).
   Badges on action matrix, tool router, handoff. prompt/repo→L1, vault→L2, caution→L3, danger→L5.
4. **Project command cards** — `ProjectCard` in `page.tsx`. Latest commit, branch, GitHub
   reference (link), dirty-file groups, blocker, next action, evidence paths, verify commands.
   `projectStatus.ts` extended: `latestCommit`, `currentBranch`, `githubRemote`, `verifyCommands`.
5. **Handoff generator** — `src/lib/mazos/handoff.ts`. Hermes/Codex scoped brief: repo path,
   branch, task, safety level, verify commands, forbidden actions (forbidden set expands as
   safety ceiling drops). Copy-paste output.

## Verification
- `npm run lint` (tsc --noEmit): clean
- `npm run build`: success; `/api/mazos/tool-router` route generated
- http://localhost:3046/ → 200; dev log clean
- project-status: MAZos (repo resolved, commits, new fields OK), JobFilter, Recall, and
  missing case (`?project=zzznope` → null match + guidance)
- tool-router `?task=build n8n outreach scraping automation` → n8n, Agent Reach, Maxun

## Constraints honoured
- Branch `agents/mazos-command-centre-next`; PR #4 based on PR #3 branch; no push to main.
- Unrelated dirty files left untouched: `data/`, `external/agent-sources/penpot/`,
  `.gitmodules`, `research/mazos/latest-vault-scan.md`, `tsconfig.tsbuildinfo`.
- Only 9 focused files committed.

## Next
- Wire handoff output into logStore so generated briefs are auditable.
- Consider persisting tool-router picks per task for a routing history.
- MAZos now runnable live locally: `npm run dev -- -p 3046`.
