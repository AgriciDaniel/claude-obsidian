---
date: 2026-07-01
project: mazos
agent: codex
status: completed
---
## What I did
- Located MAZos at `C:\Users\manaz\Projects\mazos-ui` and Hermes at `C:\Users\manaz\AppData\Local\Programs\hermes-desktop` with local runtime/config under `C:\Users\manaz\.hermes`.
- Installed local Hermes external source clones under `C:\Users\manaz\.hermes\external-sources`:
  - `headroomlabs-ai/headroom`
  - `Panniantong/agent-reach`
  - `nvidia/skills`
  - `alirezarezvani/claude-skills`
  - `getmaxun/maxun`
  - `cobusgreyling/loop-engineering`
- Downloaded the linked `CLAUDE.md` from `alirezarezvani/claude-skills`.
- Added MAZos Git submodule pointers for the six accessible external repos.
- Added MAZos registry docs/config so Hermes and the cockpit can route tasks to the right external source.
- Added live Hermes registry and `external-agent-sources` skill.
- Added local knowledge vault note `03-MEMORY/HERMES_EXTERNAL_AGENT_SOURCES.md` and updated memory indexes.
- Opened MAZos PR #1: `https://github.com/manazoid4/mazos-ui/pull/1`.
- Audited Hermes external agent source integration across MAZos, Hermes local files, local external clones, and the Obsidian memory note.
- Validated JSON/YAML syntax and checked submodule gitlinks against local clone remotes/revisions.
- Tightened routing prompt wording so private scraping, auth bypass, and unbounded loops are refused rather than merely confirmation-gated.
- Added `enescingoz/awesome-n8n-templates` after follow-up request, pinned at `2d78bc6`, and routed it as the n8n/no-code workflow template source.
- Kept the MAZos n8n submodule sparse because the full repo contains Windows long-path template filenames; the full clone is available under `C:\Users\manaz\.hermes\external-sources\awesome-n8n-templates`.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\config\buttons.json`
- `C:\Users\manaz\Projects\mazos-ui\.gitmodules`
- `C:\Users\manaz\Projects\mazos-ui\README.md`
- `C:\Users\manaz\Projects\mazos-ui\config\control-panel.yaml`
- `C:\Users\manaz\Projects\mazos-ui\config\external-agent-sources.json`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\commandRegistry.ts`
- `C:\Users\manaz\Projects\mazos-ui\config\hermes_export\EXTERNAL_SOURCES.md`
- `C:\Users\manaz\Projects\mazos-ui\research\mazos\HERMES_EXTERNAL_SOURCES.md`
- `C:\Users\manaz\Projects\mazos-ui\tsconfig.json`
- `C:\Users\manaz\Projects\mazos-ui\external\agent-sources\*` gitlinks
- `C:\Users\manaz\.hermes\mazos\ADVANCED_SKILLS.md`
- `C:\Users\manaz\.hermes\mazos\EXTERNAL_SOURCES.md`
- `C:\Users\manaz\.hermes\mazos\control-panel.yaml`
- `C:\Users\manaz\.hermes\mazos\buttons.json`
- `C:\Users\manaz\.hermes\skills\external-agent-sources\SKILL.md`
- `C:\Users\manaz\Desktop\Obsidian Main Vault\03-MEMORY\HERMES_EXTERNAL_AGENT_SOURCES.md`
- `C:\Users\manaz\Desktop\Obsidian Main Vault\03-MEMORY\PROJECT_INDEX.md`
- `C:\Users\manaz\Desktop\Obsidian Main Vault\03-MEMORY\CURRENT_TASKS.md`
- `C:\Users\manaz\claude-obsidian\wiki\sessions\2026-07-01-mazos-codex.md`

## Decisions made
- Treat the MAZos submodule approach as coherent because `.gitmodules`, gitlinks, and local Hermes clone commits/remotes line up.
- Keep `alirezarezvani/claude` documented as inaccessible and route to `alirezarezvani/claude-skills` plus the installed `CLAUDE.md`.
- Keep external repos out of MAZos TypeScript/build scope because they are reference repos, not app source.
- Use the full local Hermes clone for n8n template files and use the MAZos sparse submodule as a pinned repository pointer.
- Do not touch unrelated dirty files such as `data/` or `research/mazos/latest-vault-scan.md`.

## Verification
- JSON parse passed for MAZos config and Hermes buttons.
- YAML parse passed for MAZos and Hermes control panels.
- `git submodule status` resolved all seven pointers.
- `npm run lint` passed.
- `npm run build` passed with existing workspace-root/CSS warnings only.

## Next steps
- Consider documenting submodule update procedure for future refreshes.
- Consider adding a small validator script for external-source registry consistency.

## Addendum: project status lookup

## What I did
- Added MAZos read-only project status lookup for questions like "what's the latest work done on JobFilter in the last 24h?"
- Resolver checks `03-MEMORY/PROJECT_INDEX.md`, `02-PROJECTS/<project>/CURRENT.md`, git commits from the last 24h, `git status --short`, and loop state files where present.
- Added dashboard panel with one project input, one `LATEST 24H` button, and a concise output summary.
- Scoped Tailwind v4 source detection to `src/app` and `src/components` so external markdown tables do not generate invalid CSS in dev mode.
- Opened MAZos PR #3: `https://github.com/manazoid4/mazos-ui/pull/3`.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\projectStatus.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\api\mazos\project-status\route.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\app\page.tsx`
- `C:\Users\manaz\Projects\mazos-ui\src\app\globals.css`

## Decisions made
- Keep status lookup read-only; it does not mutate vault scan files or repo state.
- Leave unrelated dirty MAZos files unstaged: `.gitmodules`, `external/agent-sources/penpot`, `research/mazos/latest-vault-scan.md`, `data/`, `tsconfig.tsbuildinfo`.
- Preserve the Ralph conflict as evidence in status output instead of resolving it silently.

## Verification
- `npm run lint` passed.
- `npm run build` passed. Remaining warning: Next workspace-root inference and Turbopack dynamic filesystem tracing for the read-only status helper.
- `GET /api/mazos/project-status?project=MAZos` returned commits, dirty files, CURRENT entries, Ralph conflict, blocker, next action, and evidence paths.
- `GET /api/mazos/project-status?project=JobFilter` returned repo/vault summary and evidence paths.
- `GET /` returned HTTP 200 from the running local MAZos dev server on port 3046.

## Next steps
- Merge PR #3 if the status lookup output looks useful.
- Clean or finish the unrelated platform-source dirty files separately before more MAZos source work.

## Addendum: daily cockpit sharpening

## What I did
- Added a `What Now` daily cockpit panel above the main dashboard so MAZos surfaces the current priority, warning, next action, last-24h commit count, dirty repo count, and dirty-file split immediately.
- Grouped project dirty files into app work, generated/runtime noise, submodule/source leftovers, docs, and unknown.
- Surfaced Ralph loop conflicts as warnings and promoted them into the next best action when `.ralph/STATE.md` and `.ralph/prd.json` disagree.
- Added `Daily Triage L1` as a report-only prompt action with explicit no-edit/no-push/no-deploy/no-credential limits.
- Clarified action button modes so MAZos distinguishes manual prompts, repo reads, command runs, and vault scan writes.
- Pushed MAZos PR #3 update at `42c47f9`: `https://github.com/manazoid4/mazos-ui/pull/3`.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\src\app\page.tsx`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\commandRegistry.ts`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\projectStatus.ts`

## Decisions made
- Keep the status and cockpit layer read-only; it reports state and gives prompts rather than mutating repos.
- Leave unrelated dirty MAZos files unstaged: `.gitmodules`, `external/agent-sources/penpot`, `research/mazos/latest-vault-scan.md`, `data/`, `tsconfig.tsbuildinfo`.
- Do not hide generated or external-source leftovers; classify them so Hermes/Codex can decide what to finish or clean next.

## Verification
- `npm run lint` passed.
- `npm run build` passed. Remaining warning: Next workspace-root inference from multiple lockfiles.
- `GET /api/mazos/project-status?project=MAZos` returned the Ralph conflict warning, source/submodule warning, and correct dirty groups.
- `GET /api/mazos/project-status?project=JobFilter` returned a clean repo/vault status.
- `GET /api/mazos/project-status?project=Recall` returned a repo/vault status with one recent commit.
- `GET /api/mazos/project-status?project=doesnotexist` returned a clear missing-project warning.
- `GET /` returned HTTP 200 from the running MAZos dev server on port 3046.
- Browser visual automation was not completed because the local Playwright Chromium binary is missing.

## Next steps
- Refresh `http://localhost:3046/` and review the `What Now` panel.
- Resolve the MAZos Ralph state conflict before trusting loop progress.
- Clean or finish the unrelated platform-source dirty files in a separate task.

## Addendum: next stage prompt sheet

## What I did
- Read the attached Hermes MAZos usefulness brief.
- Reviewed current MAZos context, external-source registry, control panel config, and lightweight README snippets from the installed GitHub source folders.
- Created `C:\Users\manaz\Projects\mazos-ui\MAZOS_NEXT_STAGE_BUILD_PROMPT_SHEET.txt`.
- Included a concise implementation prompt for Hermes/Codex covering Hermes Context Pack, Light Hermes Prompt, real Next Best Move, button audit, intake queue, focus evidence, repo command centre, Ship Board, safety levels, and performance.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\MAZOS_NEXT_STAGE_BUILD_PROMPT_SHEET.txt`
- `C:\Users\manaz\claude-obsidian\wiki\sessions\2026-07-01-mazos-codex.md`

## Decisions made
- Kept this as a prompt-sheet artifact only, not an app implementation.
- Did not push MAZos because the attached brief explicitly says not to push unless Maz asks.
- Left unrelated/background MAZos changes untouched.

## Verification
- Confirmed the prompt sheet exists and is readable.
- Confirmed the prompt sheet includes MAZos repo reference, PR #3 reference, installed GitHub source references, safety rules, validation commands, and final response format.

## Next steps
- Paste the implementation prompt from `MAZOS_NEXT_STAGE_BUILD_PROMPT_SHEET.txt` into Hermes/Codex when ready.
- If the sheet looks right, commit it on an `agents/` branch and open/update a PR.
