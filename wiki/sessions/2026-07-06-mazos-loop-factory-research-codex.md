---
date: 2026-07-06
project: mazos
agent: codex
status: completed
---
## What I did
- Pulled the vault from `fork main`.
- Fetched latest MazOS GitHub state and confirmed `origin/main` is `b8de927` / PR #25.
- Researched a Loop Factory direction for MazOS: generate reusable loop templates from plain-English goals.
- Read existing MazOS loop implementation, prior specs, roadmap constraints, and the local Loop Engineering source.
- Cross-checked external workflow/agent patterns: Loop Engineering, LangGraph, Temporal, GitHub Actions, n8n, Prefect, and Airflow.

## Files changed
- Vault session note only: `wiki/sessions/2026-07-06-mazos-loop-factory-research-codex.md`.
- No MazOS project repo files changed.

## Decisions made
- Loop Factory v1 should generate reusable loop specs, not one-off prompts.
- Generated loops should remain prompt-first and review-only: no autonomous execution, cron, crawling, or new database.
- Each loop spec should include trigger/cadence, sources, repeat task, success condition, evidence receipts, human gates, stop conditions, cost budget, run-log shape, and proof/verification requirements.
- MazOS should score loop readiness before saving a loop to avoid low-quality loops becoming permanent noise.

## Next steps
- Ask Maz whether Loop Factory should start as a guided form, a plain-English generator, or pattern-picker-first.
- After approval, write a design spec before implementation.
