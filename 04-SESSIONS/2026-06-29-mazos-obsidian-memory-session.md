# 2026-06-29 MazOS + Obsidian memory session

- Verified vault access: `C:/Users/manaz/Desktop/Obsidian Main Vault`.
- Created/updated Obsidian memory structure: `00-INBOX`, `01-DAILY`, `02-PROJECTS`, `03-MEMORY`, `04-SESSIONS`, `05-HERMES-OUTPUTS`, `06-SYSTEM`.
- Added core memory files: project index, current tasks, decisions, prompt library, user profile, Hermes rules.
- Added project CURRENT files for JobFilter, Recall, MazOS, Hermes.
- Smoke-tested vault write/read/delete.
- Added MazOS repo `AGENTS.md` with vault/search/context rules.
- Added MazOS buttons: Update GitHub, Obsidian immersion.
- Reviewed `https://github.com/witt3rd/oh-my-hermes` as reference; useful pattern: state-file/plugin approach, not blindly installed.
- Built MazOS: `npm run build` passed.
- Pushed MazOS: `https://github.com/manazoid4/mazos-ui` commit `ce536c8`.
- Pushed Obsidian memory: `https://github.com/manazoid4/claude-obsidian` commits `b1cbd9f`, `53bae1a`.

Starter prompt:
Read `C:/Users/manaz/Desktop/Obsidian Main Vault/wiki/hot.md`, `wiki/index.md`, `03-MEMORY/PROJECT_INDEX.md`, `03-MEMORY/CURRENT_TASKS.md`, and `06-SYSTEM/HERMES_RULES.md`. Search the vault before claiming memory. Keep context small. Update tasks/decisions/session summary when durable. Then continue with: <task>.
