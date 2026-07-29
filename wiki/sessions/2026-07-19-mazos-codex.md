---
date: 2026-07-19
project: mazos
agent: codex
status: completed
---
## What I did
- Audited the local MAZos v2 loop implementation and the new `v3-auto-loops` morning-triage wrapper.
- Audited the separate `portfolio-deck` public-terminal branch and incorporated the operator-deck-to-public-terminal pivot.
- Researched production loop mechanisms in OpenHands, Aider, SWE-agent, LangGraph, Vercel Ralph Loop Agent, Hermes Agent, and related GitHub implementations.
- Reviewed current Reddit practitioner reports for recurring successes, failure modes, cost controls, sandboxing, fresh-context patterns, and human gates.
- Produced an evidence-backed architecture and phased implementation plan; no project source files were changed.

## Files changed
- `wiki/sessions/2026-07-19-mazos-codex.md`

## Decisions made
- Keep MAZos as the private loop control plane and `portfolio-deck` as a separate public, read-only projection.
- Implement loops as persisted state machines with deterministic verification and stop predicates, not prompt-only repetition.
- Start automation with report-only triage; earn higher autonomy per loop through passing receipts.
- Do not expose private repository names, MAZos receipts, local paths, internal blockers, or authenticated `/user/repos` results in the public portfolio.
- Treat Reddit evidence as practitioner signals; use GitHub source code and local validation as implementation authority.

## Next steps
- Repair and dogfood the morning-triage loop contract before registering its schedule.
- Harden budgets, typed stop reasons, repetition detection, idempotent approvals, and structured receipts in the MAZos kernel.
- Implement the curated public-terminal portfolio only after its public-data boundary and truthful project metadata are fixed.
- Run build and targeted tests in each repo on implementation branches, then open PRs rather than pushing to main.
