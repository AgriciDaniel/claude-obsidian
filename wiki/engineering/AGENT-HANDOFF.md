---
title: Agent Handoff
created: 2026-07-05
updated: 2026-07-05
type: summary
tags: [engineering, agents, handoff]
---

# Agent Handoff

Links: [[wiki/projects/INDEX]] · [[wiki/engineering/REPO-MAP]]

## Start every repo session

1. Pull latest remote first.
2. Check `git status --short` before edits.
3. Read repo `AGENTS.md` / `CLAUDE.md` if present.
4. Read this project wiki folder before broad code changes.
5. Never paste secrets or `.env` values into notes.

## Project-specific warnings

### JobFilter

- Highest priority / revenue pressure.
- Local tree is heavily divergent from `origin/main`; do not reset/checkout casually.
- Remote is `manazoid4/JobFilterV1.git`, not exact requested `jobfilter` slug.
- Preserve lead scoring reason-code simplicity.
- Verify Firebase rules + Stripe/WhatsApp before deploy.

### InkWeave

- Do not build a giant writing platform. Build one paid path: snippets → free chapter → paid full book.
- Generation pipeline currently types only. Keep implementation minimal.
- Run `npm run build` + `npm run lint` after changes.

### OpenFlowKit

- Core must stay provider-neutral/open.
- Browser MVP and terminal bridge exist; desktop/global hotkeys next.
- Local bridge is not equivalent to hosted deploy.
- Run `npm run test` + `npm run build`.

### Zawiya Growth Hub

- GitHub docs are source of truth; Notion is live ops.
- Do not digitize/summarize private spiritual content, awrad, wirds, teacher instructions, private screenshots, or unapproved recordings.
- Work only with public-safe operational/funding/project docs unless explicitly cleared.

## Wiki maintenance rules

- Keep notes concise; no file dumps.
- Update canonical pages instead of creating duplicates.
- Use wikilinks between project and engineering notes.
- Mark uncertainty as `Unknown` / `Needs verification`.
- Commands in docs must come from `package.json` or repo docs.

## Verified local paths

| Project | Path |
|---|---|
| JobFilter | `C:\Users\manaz\Desktop\JobFilter` |
| InkWeave | `C:\Users\manaz\Desktop\inkweave` |
| OpenFlowKit | `C:\Users\manaz\Desktop\openflowkit` |
| Zawiya | `C:\Users\manaz\Desktop\zawiya-growth-hub` |
| Vault | `C:\Users\manaz\Desktop\Obsidian Main Vault` (also surfaced as `C:\Users\manaz\claude-obsidian`) |
