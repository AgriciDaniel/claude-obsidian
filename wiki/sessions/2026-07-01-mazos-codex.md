---
date: 2026-07-01
project: mazos
agent: codex
status: completed
---
## What I did
- Audited Hermes external agent source integration across MAZos, Hermes local files, local external clones, and the Obsidian memory note.
- Validated JSON/YAML syntax and checked submodule gitlinks against local clone remotes/revisions.
- Tightened routing prompt wording so private scraping, auth bypass, and unbounded loops are refused rather than merely confirmation-gated.

## Files changed
- `C:\Users\manaz\Projects\mazos-ui\config\buttons.json`
- `C:\Users\manaz\Projects\mazos-ui\src\lib\mazos\commandRegistry.ts`
- `C:\Users\manaz\Projects\mazos-ui\config\hermes_export\EXTERNAL_SOURCES.md`
- `C:\Users\manaz\.hermes\mazos\ADVANCED_SKILLS.md`
- `C:\Users\manaz\Desktop\Obsidian Main Vault\03-MEMORY\HERMES_EXTERNAL_AGENT_SOURCES.md`
- `C:\Users\manaz\claude-obsidian\wiki\sessions\2026-07-01-mazos-codex.md`

## Decisions made
- Treat the MAZos submodule approach as coherent because `.gitmodules`, gitlinks, and local Hermes clone commits/remotes line up.
- Keep `alirezarezvani/claude` documented as inaccessible and route to `alirezarezvani/claude-skills` plus the installed `CLAUDE.md`.
- Do not touch unrelated dirty files such as `data/` or `research/mazos/latest-vault-scan.md`.

## Next steps
- Consider documenting submodule update procedure for future refreshes.
- Consider adding a small validator script for external-source registry consistency.
