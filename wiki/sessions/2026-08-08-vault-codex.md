---
date: 2026-08-08
project: vault
agent: codex
status: blocked
---

## What I did

- Set `mcp_servers.local-knowledge.startup_timeout_sec` to 120 in the active Codex config.
- Validated the TOML and confirmed a fresh Codex process recognizes the timeout.
- Health-checked every enabled MCP with harmless read-only calls.
- Cleared the expired Supabase MCP OAuth credential and opened a fresh interactive login.

## Files changed

- `C:\Users\manaz\.codex\config.toml`
- `wiki/sessions/2026-08-08-vault-codex.md`

## Decisions made

- Used 120 seconds for `local-knowledge`, matching the other slow local MCP configurations.
- Treated `codebase-memory-mcp`'s home-directory “project not found or not indexed” response as successful server execution rather than a transport failure.
- Left Notion disabled because it is explicitly disabled in the existing configuration.

## Next steps

- Complete the Supabase authorization in the interactive browser/login window, then rerun a read-only Supabase MCP probe.

---

date: 2026-08-08
project: Vault
agent: codex
status: completed

## What I did
- Installed Codex skills from `mattpocock/skills`.
- Installed Codex skills from `addyosmani/agent-skills`.
- Verified representative installed skill directories under `C:\Users\manaz\.codex\skills`.

## Files changed
- `C:\Users\manaz\.codex\skills\*` skill directories from the two GitHub repositories.
- `wiki/sessions/2026-08-08-vault-codex.md`

## Decisions made
- Installed concrete directories containing `SKILL.md`; repo roots were not valid installer targets.
- Used the real vault target path because `C:\Users\manaz\claude-obsidian` is a junction.

## Next steps
- New skills should be available from the next Codex turn/session.

---

date: 2026-08-08
project: Vault
agent: codex
status: completed

## What I did
- Installed Codex skills from `zhaoxuya520/reverse-skill`.
- Added persistent skill routing instructions to consider Matt Pocock, Addy Osmani, and reverse-skill packs task-by-task.
- Verified representative reverse/security skill directories under `C:\Users\manaz\.codex\skills`.

## Files changed
- `C:\Users\manaz\.codex\skills\*` skill directories from `zhaoxuya520/reverse-skill`.
- `C:\Users\manaz\.codex\AGENTS.md`
- `wiki/sessions/2026-08-08-vault-codex.md`

## Decisions made
- Installed concrete directories containing `SKILL.md`.
- Added a routing pointer instead of listing every installed skill in AGENTS.md, so future agents reference the packs without loading irrelevant instructions.

## Next steps
- Reverse/security skills should be available from the next Codex turn/session.

---

date: 2026-08-08
project: Vault
agent: codex
status: completed

## What I did
- Installed the Codex `clone-website` skill from `JCodesMore/ai-website-cloner-template`.
- Installed canonical Agent Native skills from `BuilderIO/agent-native`.
- Updated persistent skill routing instructions to include website cloning and Agent Native task families.
- Verified representative installed directories under `C:\Users\manaz\.codex\skills`.

## Files changed
- `C:\Users\manaz\.codex\skills\clone-website`
- `C:\Users\manaz\.codex\skills\*` Agent Native skill directories
- `C:\Users\manaz\.codex\AGENTS.md`
- `wiki/sessions/2026-08-08-vault-codex.md`

## Decisions made
- Installed the `.codex/skills/clone-website` copy from the website cloner repo because the repo includes duplicate Claude/Codex/GitHub skill copies.
- Installed Agent Native canonical source skills and plugin/root skills, while skipping app/template duplicate copies.
- Kept AGENTS.md as a compact routing pointer so future sessions consider all installed packs without loading irrelevant skill bodies.

## Next steps
- Website cloning and Agent Native skills should be available from the next Codex turn/session.

---

date: 2026-08-08
project: vault
agent: codex
status: completed
session_id: 019fe272-7b91-7220-bc12-60298909a4b9

## What I did

- Pulled the online Obsidian vault from `fork main`.
- Verified the local Obsidian vault path and GitHub remotes.
- Confirmed local Codex skills are available under `C:\Users\manaz\.codex\skills`.
- Updated project location records so Codex can use the verified local paths rather than stale Desktop paths.
- Updated persistent Codex standing orders with the same verified vault and repo paths.

## Files changed

- `wiki/projects/project-locations.md`
- `wiki/sessions/2026-08-08-vault-codex.md`
- `C:\Users\manaz\.codex\AGENTS.md`

## Decisions made

- Use `C:\Users\manaz\Desktop\Obsidian Main Vault` for Git commands against the vault because the `C:\Users\manaz\claude-obsidian` junction can fail with `git -C`.
- Treat the Obsidian vault plus `fork main` remote as durable operating memory.
- Use relevant local skills only after reading their `SKILL.md`.

## Next steps

- For each future project task, pull the vault first, read relevant project context, inspect the actual repo worktree, use codebase-memory MCP when available, and push a session note at the end.
