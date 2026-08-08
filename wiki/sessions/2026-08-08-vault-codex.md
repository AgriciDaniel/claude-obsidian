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
