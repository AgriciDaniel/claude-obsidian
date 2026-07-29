# FlowLens

## Purpose
Screen recording + annotation + workflow intelligence tool.

## Audience
Corporate teams, support teams, QA, ops, training, documentation.

## Current Status
Product definition / early build. Desktop markdown archives merged into this project folder.

## Goal
- Auto-clipping of key moments
- Annotations and comments
- AI summaries
- Auto-generated process docs
- Vercel-ready product

## Key Decisions
- Keep imported historical markdown under `Archive/` to avoid cluttering active project memory.
- Do not copy code/build artifacts into Obsidian memory.

## Active Tasks
- [ ] Review imported archive summaries
- [ ] Define MVP feature set
- [ ] Plan architecture
- [ ] Build Vercel-ready version

## Useful Prompts

## Technical Notes
- Imported source folders: `flowlens`, `hermes-support-flowlens`
- Imported only `.md` and `.txt`

## Session Receipts
<!-- Newest first -->

### 2026-07-09 — GitHub Sync
- Pulled latest markdown/text files from cloud GitHub repos to ensure Obsidian has the cloud source of truth.
- Repos synced: `flowlens`.
- Saved under `Archive/GitHub_<repo>/`.

### 2026-07-09 — Desktop Vault Merge
- Merged historical FlowLens markdown/text files into `10_Projects/FlowLens/Archive/`
- Skipped code, binaries, `.git`, `node_modules`, `dist`, `.next`, build artifacts
