# JobFilter

## Purpose
Construction and trade lead intelligence product.

## Audience
Builders, plumbers, electricians, roofers, heat pump installers.

## Current Status
Planning / early development. Desktop markdown archives merged into this project folder.

## Goal
- Surface relevant planning applications, EPCs, tenders, Companies House data
- Lead scoring engine
- WhatsApp/email alerts for tradespeople

## Key Decisions
- Keep imported historical markdown under `Archive/` to avoid cluttering active project memory.
- Do not copy code/build artifacts into Obsidian memory.

## Active Tasks
- [ ] Review imported archive summaries
- [ ] Define data sources (planning apps, EPCs, tenders)
- [ ] Lead scoring logic
- [ ] Alert delivery (WhatsApp/email)

## Useful Prompts

## Technical Notes
- Imported source folders: `JobFilter`, `JobFilterV1`, `JobFilterV1-github`
- Imported only `.md` and `.txt`

## Session Receipts
<!-- Newest first -->

### 2026-07-09 — GitHub Sync
- Pulled latest markdown/text files from cloud GitHub repos to ensure Obsidian has the cloud source of truth.
- Repos synced: `JobFilterV1`, `JobFilter-Obsidian-Vault`.
- Saved under `Archive/GitHub_<repo>/`.

### 2026-07-09 — Desktop Vault Merge
- Merged historical JobFilter markdown/text files into `10_Projects/JobFilter/Archive/`
- Skipped code, binaries, `.git`, `node_modules`, `dist`, `.next`, build artifacts
