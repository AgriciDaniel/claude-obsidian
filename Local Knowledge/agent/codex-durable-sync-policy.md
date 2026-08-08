---
title: Codex Durable Sync Policy
created: 2026-08-08
updated: 2026-08-08
session_id: 019fe272-7b91-7220-bc12-60298909a4b9
tags: [codex, agents, vault, local-knowledge, skills, repos]
---

# Codex Durable Sync Policy

Codex must always persist changes about repos, skills, instructions, project memory, and agent operating rules to both durable stores:

- Local knowledge vault: `C:\Users\manaz\LocalKnowledgeVault`
- Obsidian vault GitHub repo: `C:\Users\manaz\Desktop\Obsidian Main Vault`, pushed to `fork main`

`C:\Users\manaz\LocalKnowledgeVault` is a junction to `C:\Users\manaz\Desktop\Obsidian Main Vault\Local Knowledge`, so updates written inside Local Knowledge are included in the Obsidian vault commit.

## Required Workflow

1. Pull the Obsidian vault from `fork main`.
2. Make the requested repo, skill, or instruction change.
3. Update local knowledge/Obsidian notes with the durable memory.
4. Write or append the session note in `wiki/sessions/`.
5. Commit and push the Obsidian vault to `fork main`.

## Current Session

- Session ID: `019fe272-7b91-7220-bc12-60298909a4b9`
- User requested this rule be remembered every time.
- A low-cost worker agent was spawned to inspect local previous-conversation/session artifacts for missing skills and GitHub repos that may need to be uploaded or installed.
