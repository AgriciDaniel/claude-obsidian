---
date: 2026-07-05
project: recall-mazos
agent: codex
status: completed
---

## What I did
- Reviewed Recall vault context, Recall repo shape, and MAZos integration surfaces.
- Confirmed Recall has moved from generic saved-brain/personal memory toward agency creative intelligence, Instagram Inbox, and Signal OS.
- Confirmed MAZos already has partial Recall wiring through Source Intake, project status, repo scanner, build command, product playbook, Shipping Spine, AI Feed, and human decision gates.
- Identified the main integration gap: MAZos points Recall paths at `C:/Users/manaz/Projects/recall`, while the actual local repo and vault metadata point at `C:/Users/manaz/saved-brain`.

## Files changed
- `wiki/sessions/2026-07-05-recall-mazos-codex.md`

## Decisions made
- Treat Recall inside MAZos as a revenue/signal workstream, not a standalone generic knowledge-base panel.
- First integration layer should be read-only/status-oriented: path correction, project status, feed signals, capture queue health, and pilot evidence prompts.
- Deeper integration should focus on the validated Recall chain: source -> why it mattered -> client/project -> recommendation -> delivered work -> outcome.

## Next steps
- Fix Recall path references in MAZos config and code.
- Add Recall-specific health/metrics to MAZos: capture queue count, enriched item count, recent captures, failed ingestion, and pilot-evidence completeness.
- Add a Recall cockpit page or section in MAZos that turns the pre-mortem into an operating checklist for the 30-90 day validation sprint.
