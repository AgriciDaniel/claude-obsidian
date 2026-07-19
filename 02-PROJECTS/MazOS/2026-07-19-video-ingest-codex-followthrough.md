---
date: 2026-07-19
project: mazos
type: ingest
sources: [nQwJVHCtDDY, 4biXYSNkn9Y, 8wsM0euQOvc]
---

# Loop-engineering video ingest + Codex audit follow-through

## Videos

### 1. Matt Pocock's Agentic Engineering Workflow (David Ondrej, yt nQwJVHCtDDY) — the substantive one

- **Harness > model**: "everyone's obsessed with the model… they should be more interested in the harness." Optimize prompts/skills/environment — the part you control.
- **Grill me first**: adversarial alignment interview BEFORE planning — AI challenges your vision until shared understanding; flushes assumptions pre-code.
- **PRD → blocked-issue kanban**: destination-style PRD decomposed into granular markdown issues with blocking relationships; unblocked issues run in parallel across agents.
- **Vertical slices** (tracer bullets): each task crosses schema→service→API→frontend, thin but complete, with tests.
- **Review in fresh context**; video walkthroughs for richer review.
- **Queues over infinite loops**: prioritized backlog + deliberate human checkpoints, not while-true.
- **Ratchets**: every AI fix becomes a preventative measure (test, lint rule, doc) so the class of bug can't recur. Review the review process itself.
- **Context hygiene**: delete all skills/MCPs, observe blank-slate behavior, then layer *procedure* skills (human-invoked) intentionally.
- **Strategic vs tactical**: AI owns tactical (syntax, debugging); human owns strategic (architecture, scoping). Skills are the ceiling.

**MAZos mapping**: grill-me = gate preflight interview (future New Loop upgrade); blocked-issue kanban = .loops/<id>/plan.md could gain blocking deps; ratchets = when a loop fixes a bug, its criteria.json gains a permanent regression criterion; queues-not-loops validates the propose→human-save design.

### 2–3. "Loop Engineering explained in 8min" (Caleb Writes Code, 4biXYSNkn9Y) · "Loop Engineering Just 10x Claude Code" (AI LABS, 8wsM0euQOvc)

Standard explainers of the June-2026 loop-engineering wave: /goal evaluator-judged stop conditions, writer/checker split ("the model that wrote the code is way too nice grading its own homework"), state outside the model (files/git/CLAUDE.md), Cherny's "my job is to write loops." Consistent with the Orange Book canon; no novel mechanics.

## Codex audit — actions taken (2026-07-19)

| Codex next step | Status |
|---|---|
| Repair + dogfood triage before schedule | ✅ quoting bug fixed, 1 real dogfooded run (5 findings, 1 proposal, receipt); schedule live 06:33 |
| Harden budgets/typed stops/repetition/receipts | ✅ already in v2 kernel (iteration budgets, LoopStopReason, failureKey circuit breaker, machine receipts); idempotent approvals via event-fold |
| Public-data boundary before portfolio ships | ✅ getRepos now filters private at source (token made /user/repos leak-capable); page filter kept as second layer |
| Truthful project metadata | ✅ JobFilter description corrected to real product (UK trades lead filtering) + real repo link; ForgeOS status → "Concept" (no repo, no fake claims) |
| Build + PRs, never main | ✅ mazos PR #51, portfolio PR #1, both green |
