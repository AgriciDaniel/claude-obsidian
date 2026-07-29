# Agent Standing Orders — manazoid4

## Squad
Three agents work in parallel across all projects:
- **Claude** (`claude`) — primary reasoning, architecture, complex tasks
- **Codex** (`codex`) — execution, build tasks, code-heavy work (OpenAI Codex CLI, gpt-5.5)
- **OpenCode** (`opencode`) — fast iteration, UI/frontend, exploratory work

All three share the same vault, branch prefix, and PR workflow.

---

## Source of Truth
Two vaults. Read both:
1. **Squad vault** — `C:\Users\manaz\claude-obsidian` (github.com/manazoid4/claude-obsidian)
   Projects, sessions, architecture notes, wiki
2. **Ops vault** — `C:\Users\manaz\JobFilter-Obsidian-Vault`
   JobFilter agent runs, daily brief, revenue, territory, competitor intel

---

## On Session Start — MANDATORY

1. Pull squad vault:
   ```
   git -C "C:\Users\manaz\claude-obsidian" pull fork main
   ```
2. Read relevant project context:
   - JobFilter → `wiki/projects/jobfilter/` + `JobFilter-Obsidian-Vault/JobFilter/Daily Brief.md`
   - InkWeave → `wiki/projects/inkweave/`
   - OpenFlowKit → `wiki/projects/openflowkit/`
   - Zawiya → `wiki/projects/zawiya/`

---

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
2. Push squad vault:
```
git -C "C:\Users\manaz\claude-obsidian" add -A
git -C "C:\Users\manaz\claude-obsidian" commit -m "session: {project} {YYYY-MM-DD} {agent}"
git -C "C:\Users\manaz\claude-obsidian" push fork main
```

---

## Project Paths & Stack

| Project | Local | Repo | Stack |
|---|---|---|---|
| JobFilter | `C:\Users\manaz\Desktop\jobfilter\jobfilterv1` | manazoid4/jobfilter | Next.js 15, Supabase, Stripe, Tailwind, Vercel, jobfilter.uk |
| InkWeave | `C:\Users\manaz\Desktop\inkweave` | manazoid4/inkweave | Next.js, tRPC, Claude API, Supabase, Stripe, Vercel, inkweave.co.uk |
| OpenFlowKit | `C:\Users\manaz\Desktop\openflowkit` | manazoid4/openflowkit | Vite + React 19 + TS, hash routing, Vercel |
| Zawiya | `C:\Users\manaz\Desktop\zawiya-growth-hub` | manazoid4/zawiya-growth-hub | Notion (12 DBs), Obsidian, GitHub ops |
| Squad Vault | `C:\Users\manaz\claude-obsidian` | manazoid4/claude-obsidian | Obsidian + Git |
| Ops Vault | `C:\Users\manaz\JobFilter-Obsidian-Vault` | local only | Obsidian |

---

## Git / PR Rules

- NEVER push directly to `main` on any project repo
- Branch prefix: `agents/` — all work in `agents/{task-slug}`
- Push squad vault after EVERY session, no exceptions
- Zawiya: never put private spiritual content anywhere digital
- Update `wiki/projects/{project}/` when architecture or decisions change

---

## JobFilter — Key Facts

Design: Brutalist-Yellow (white/black/yellow, `border-2`, hard shadows `shadow-[3px_3px_0_var(--line)]`)
Lead tiers: GOLD ≥80, SILVER ≥50, BRONZE 30-49, BIN <30
Founder blockers (see `wiki/projects/jobfilter/STICKY-TODO.md`): WhatsApp env vars, Supabase tables, Stripe setup
