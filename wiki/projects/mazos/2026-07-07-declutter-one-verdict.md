---
type: project-log
project: mazos
date: 2026-07-07
tags: [mazos, declutter, shipping-spine, loops, pr]
source: Claude Code session
pr: https://github.com/manazoid4/mazos-ui/pull/40
---

# MAZos Declutter — One Verdict (PR #40)

Ruthless declutter after PRs #31–36 (Research Console, Loop Doctor, Product Loop Packs, Loop Receipts, Competitor Radar, pattern-first Loop Factory). Spec: `specs/declutter-one-verdict.md` (merged as #38). Implementation: PR #40, branch `agents/declutter-one-verdict`.

## Declutter report verdicts

- **Keep:** Shipping Spine (NOW), pattern-first Loop Factory + Loop Doctor scoring, Loop Engineering Deck, Decision Inbox, Research Console reports, Source Intake, Command Palette, Loop Receipts plumbing.
- **Merged:** Morning Brief + feed verdict → Shipping Spine verdict (one "what do I do today" answer). Handoff + Context Map + Tool Router + Runtime Safety → single Agent Prep panel. Ship Log + Stale Radar → feed/spine.
- **Removed:** `/focus` pomodoro page (orphan), Vault Intelligence panel, Loop Doctor aggregate panel, Repo Command Centre, 10 root `MAZOS_*.md` reports (→ `docs/reports/`).
- **Fixed:** feed lanes 9→4, watch capped at 3 and born `seen` (unread 19→3), loop `complete` requires evidence-bearing iteration (400 otherwise), receiptless loops >3 days lose `keep` verdict, custom loop `pattern` backfilled.

## Main daily command centre

`/` NOW tab — Shipping Spine only. It carries verdict, why, owner, safety, needs-you list, avoid-today, handoff prompt, brief copy, publishable update.

## Best next build (queued, not built)

Nothing new until PR #40 lands. After that: competitor-radar-driven loop packs are the strongest candidate — radar already has 8 live snapshots (n8n, Dify, Activepieces, LangGraph, OpenHands, opencode…), each with a `suggestedLoopPack`.

## Session hazards worth remembering

- Two agent sessions shared the same checkout; branches switched mid-work and one commit landed on local `main` (repaired, main reset to origin). Isolated into `git worktree` at `.claude/worktrees/declutter` — do this from the start next time.
- Earlier "Competitor Radar is empty" finding was wrong — read the wrong JSON key (`competitors` vs `snapshots`).
