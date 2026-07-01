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
- Do not touch unrelated dirty files such as `data/` or `research/mazos/latest-vault-scan.md`.

## Verification
- JSON parse passed for MAZos config and Hermes buttons.
- YAML parse passed for MAZos and Hermes control panels.
- `git submodule status` resolved all six pointers.
- `npm run lint` passed.
- `npm run build` passed with existing workspace-root/CSS warnings only.

## Next steps
- Consider documenting submodule update procedure for future refreshes.
- Consider adding a small validator script for external-source registry consistency.
