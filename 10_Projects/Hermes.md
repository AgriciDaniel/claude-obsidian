# Hermes

## Purpose
Maz's primary AI agent OS. Runs on Telegram, controls local machine, manages cron jobs, memory, and code tasks.

## Current Status
Active daily use. maz-lite profile on Windows. Connected to Telegram.

## Goal
Make Hermes faster, cleaner, better at memory, and easier to control — including from Telegram.

## Key Decisions
- Obsidian vault used as searchable long-term memory (not full-context)
- Session receipts written after major work
- Token streaming enabled (display.stream_responses: true)

## Active Tasks
- [ ] Refine Obsidian memory workflow
- [ ] Install and wire camofox browser toolset
- [ ] Explore awesome-hermes-usecases patterns

## Useful Prompts
- "Update RECENT_SUMMARY.md with today's session"
- "Write a session receipt for [task]"
- "Check MEMORY_INDEX.md and open the relevant project note"

## Technical Notes
- Profile: maz-lite
- Config: C:\Users\manaz\AppData\Local\hermes\profiles\maz-lite\config.yaml
- Obsidian vault: C:\Users\manaz\Desktop\Obsidian Main Vault
- Installed: @askjo/camofox-browser (npm global)
- Streaming: enabled

## Session Receipts
<!-- Newest first -->

### 2026-07-09 — Agent Frameworks Installed
- Installed `obra/superpowers` skills manually into `~/.hermes/profiles/maz-lite/skills/`.
- Configured rules to enforce Ponytail methodology (YAGNI, minimal diffs) and Superpowers SDLC (spec -> plan -> subagent execution).

### 2026-07-09 — GitHub Sync
- Pulled latest markdown/text files from cloud GitHub repos to ensure Obsidian has the cloud source of truth.
- Repos synced: `claude-obsidian`, `mazos-ui`, `dfrostar/neuralmind`.
- Saved under `Archive/GitHub_<repo>/`.

### 2026-07-09 — Compression + Vault Merge
- Tuned Hermes compression: threshold 0.90, target_ratio 0.30, protect_first_n 5, protect_last_n 30
- Merged Hermes-related desktop markdown/text files into `10_Projects/Hermes/Archive/`
- Kept compression enabled but delayed
- Codex native/app-server auto-raise disabled via `compression.codex_gpt55_autoraise: false`

### 2026-07-09 — Obsidian memory setup
- Created 00_Hermes/, 10_Projects/, 40_Decisions/, 50_Prompts/, 99_Inbox/ structure
- Populated all starter files
- Enabled token streaming
- Installed camofox-browser
