---
date: 2026-06-19
project: vault
agent: codex
status: completed
---

## What I did

- Created the canonical vault at `C:\Users\manaz\Desktop\Obsidian Main Vault`.
- Merged the former Documents main vault into `Personal/`.
- Preserved the Claude Obsidian wiki and tooling at the canonical root.
- Merged the local SwarmVault workspace into `Local Knowledge/`.
- Imported the current JobFilter vault into `Projects/JobFilter/`.
- Preserved the older JobFilter vault under `Archive/Legacy JobFilter Vault/`.
- Replaced old general-vault paths with junctions to the canonical vault.
- Repointed Claude, Codex, OpenCode, MCP, the desktop launcher, and the inbox watcher.
- Registered and opened the canonical vault in Obsidian.

## Files changed

- Canonical vault: `C:\Users\manaz\Desktop\Obsidian Main Vault`
- Backup: `C:\Users\manaz\Desktop\Vault Consolidation Backup\20260619-225220`
- Obsidian registry: `%APPDATA%\obsidian\obsidian.json`
- Agent skills and MCP configuration for Claude, Codex, and OpenCode.

## Decisions made

- Namespace imports instead of flattening files, because the source vaults contain many duplicate filenames.
- Keep imported personal and project folders out of the Claude Obsidian Git remote by default.
- Keep Zawiya outside the merged vault because its private spiritual-content boundary must remain isolated.
- Preserve compatibility junctions so older scripts continue working while all physical general knowledge lives in one place.

## Next steps

- Use `HOME.md` as the human entry point.
- Review the imported `Archive/Legacy JobFilter Vault/` later and delete redundant notes only after manual confirmation.
