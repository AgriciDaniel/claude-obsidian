---
title: Project Locations
type: index
created: 2026-06-15
updated: 2026-08-08
tags: [projects, github, locations]
---

# Project Locations

Clean map of active projects, local PC folders, and GitHub repositories.

| Project | PC location | GitHub |
|---|---|---|
| JobFilter | `C:\Users\manaz\JobFilterV1` | https://github.com/manazoid4/JobFilterV1 |
| InkWeave | `C:\Users\manaz\Desktop\inkweave` | https://github.com/manazoid4/inkweave |
| OpenFlowKit | `C:\Users\manaz\openflowkit` | https://github.com/manazoid4/openflowkit |
| FlipSignal | `C:\Users\manaz\Desktop\flipsignal` | https://github.com/manazoid4/flipsignal |
| khutba.io | `C:\Users\manaz\Desktop\khutba-io` | https://github.com/manazoid4/khutba-io |
| Recall | `C:\Users\manaz\saved-brain` | https://github.com/manazoid4/recall |
| Zawiya Growth Hub | `C:\Users\manaz\zawiya-growth-hub` | https://github.com/manazoid4/zawiya-growth-hub |
| Vault | `C:\Users\manaz\claude-obsidian` junction to `C:\Users\manaz\Desktop\Obsidian Main Vault` | https://github.com/manazoid4/claude-obsidian |

## Agent Operating Memory

- Codex should use both the local Obsidian vault and the online GitHub vault remote for durable project context.
- Local vault commands may need the resolved path `C:\Users\manaz\Desktop\Obsidian Main Vault` because `git -C C:\Users\manaz\claude-obsidian` can fail on the junction.
- Local Codex skills are installed under `C:\Users\manaz\.codex\skills`; 236 skill directories were present on 2026-08-08.
- Before project work, pull the vault from `fork main`, read the relevant `wiki/projects/{project}/` files, use applicable local skills by reading their `SKILL.md`, and write a session note before pushing the vault.

## Project Notes

- [[jobfilter/index|JobFilter]]
- [[inkweave/overview|InkWeave]]
- [[openflowkit/overview|OpenFlowKit]]
- [[flipsignal/index|FlipSignal]]
- [[khutba.io/overview|khutba.io]]
- [[recall/index|Recall]]
