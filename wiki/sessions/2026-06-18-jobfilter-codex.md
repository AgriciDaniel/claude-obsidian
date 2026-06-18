---
date: 2026-06-18
project: jobfilter
agent: codex
status: completed
---

## What I did

- Pulled the squad vault from `fork/main`.
- Read JobFilter project context from the squad vault, ops vault, embedded repo vault, current repository state, audits, role prompts, changelogs, and launch checklists.
- Created a full autonomous Claude Code prompt that uses role-based review, a 90-day pre-mortem, evidence-based launch gates, iterative implementation, adversarial review, verification, founder-only blockers, and durable checkpoints.
- Added explicit protection for the current dirty JobFilter worktree and stale or contradictory vault notes.

## Files changed

- `wiki/projects/jobfilter/prompts/2026-06-18-claude-launch-readiness-loop.md`
- `wiki/projects/jobfilter/index.md`
- `wiki/sessions/2026-06-18-jobfilter-codex.md`

## Decisions made

- Current code and recent git evidence take precedence over older vault claims.
- Claude should loop on launch gates, not general feature generation.
- Lead truth, payment integrity, tenant isolation, delivery truth, and activation rank above UI polish or new features.
- Remaining dashboard, credential, legal approval, purchase, and real-message actions must be separated as founder-only tasks.
- Claude must continue after each green build until code-controllable launch gates are verified or genuinely blocked.

## Next steps

- Paste the prompt into Claude Code while opened in the JobFilter repository.
- Review Claude's durable launch-state file and PR rather than relying only on its chat summary.
