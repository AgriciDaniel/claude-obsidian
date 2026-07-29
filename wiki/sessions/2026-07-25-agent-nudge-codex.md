---
date: 2026-07-25
project: agent-nudge
agent: codex
status: completed
---
## What I did
Replaced the earlier compiler-only dogfood plan with a commercial transition plan focused on pricing, licensing hooks, onboarding, changelog generation, DeWalt-style polish, context dashboard design, direct agent handoffs, and a 4-batch delivery sequence.

Added two minimal `AGENTS.md` bullets covering where Brief Compiler dogfood artifacts live and which existing compiler workflows/commands are already present in the repo.

## Files changed
`C:\Users\manaz\Projects\agent-nudge\docs\dogfood\MAZ-MODE-BUILD-PLAN.md`

`C:\Users\manaz\Projects\agent-nudge\AGENTS.md`

## Decisions made
Kept the proposed commercial hook local-first: free core compiler, paid convenience and scale features.

Did not rewrite `PRODUCT.md`; instead documented the explicit conflict between current anti-reference guidance and the requested JobFilter-style commercial direction.

## Next steps
If adopting the plan, start Batch 1 by adding `license` and `bootstrap` command branches in `src/cli/index.ts`, then wire a minimal local license status endpoint in `src/daemon/server.ts`.
