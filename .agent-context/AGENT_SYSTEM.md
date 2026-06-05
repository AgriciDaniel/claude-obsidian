# Agent Standing Orders

## Source of Truth
Vault at `C:\Users\manaz\claude-obsidian` is the single source of truth for ALL projects.
Read it before starting work. Write back to it when done.

## On Session Start — MANDATORY
1. Pull latest vault:
   ```
   git -C C:\Users\manaz\claude-obsidian pull origin main
   ```
2. Read relevant project context:
   - InkWeave    → wiki/projects/inkweave/
   - OpenFlowKit → wiki/projects/openflowkit/
   - Zawiya      → wiki/projects/zawiya/
   - JobFilter   → wiki/projects/jobfilter/

## On Session End — MANDATORY
1. Write session note to `wiki/sessions/YYYY-MM-DD-{project}-{agent}.md`:
```markdown
---
date: YYYY-MM-DD
project: {project}
agent: {claude|codex|opencode}
status: {completed|blocked|in-progress}
---
## What I did
## Files changed
## Decisions made
## Next steps
```
2. Push vault:
```
git -C C:\Users\manaz\claude-obsidian add -A
git -C C:\Users\manaz\claude-obsidian commit -m "session: {project} {YYYY-MM-DD}"
git -C C:\Users\manaz\claude-obsidian push origin main
```

## Project Paths
- InkWeave:    C:\Users\manaz\Desktop\inkweave
- OpenFlowKit: C:\Users\manaz\Desktop\openflowkit
- JobFilter:   C:\Users\manaz\Desktop\jobfilter\jobfilterv1
- Zawiya:      C:\Users\manaz\Desktop\zawiya-growth-hub
- Vault:       C:\Users\manaz\claude-obsidian

## Stack Reference
- InkWeave:    Next.js, tRPC, Claude API, Supabase, Stripe, Vercel
- OpenFlowKit: Vite + React 19 + TypeScript 5.9, hash routing
- JobFilter:   JavaScript
- Zawiya:      Notion (12 DBs), Obsidian, GitHub ops

## Rules
- Never push directly to main on project repos — always create a PR
- Update wiki/projects/{project}/ when architecture or key decisions change
- Push vault after EVERY session, no exceptions
- Zawiya: never put private spiritual content anywhere digital
