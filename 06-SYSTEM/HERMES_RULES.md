# Hermes Rules

---
## 2026-06-29 Hermes memory/context update
# Hermes ↔ Obsidian rules

1. Session start: read hot/index + memory index files if relevant.
2. Search-first: before saying "I remember/we did", search/read vault or session DB.
3. Context budget: never load whole vault. Read indexes → search → open top relevant notes only.
4. Session summaries: serious sessions write `04-SESSIONS/YYYY-MM-DD-project-session.md`.
5. Durable changes: append dated sections to `CURRENT_TASKS.md` / `DECISIONS.md` / project `CURRENT.md`.
6. Backups: before overwriting important memory files, append instead or create `.bak-YYYYMMDD-HHMMSS`.
7. Scope: Obsidian tooling should target only `C:/Users/manaz/Desktop/Obsidian Main Vault`, not whole `C:/`.
8. GitHub handoff: show direct repo URLs for touched repos.
9. oh-my-hermes: use as reference for state-file/plugin patterns; verify before adopting.
