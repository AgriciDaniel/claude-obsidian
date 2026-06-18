---
date: 2026-06-18
project: jobfilter
agent: codex
status: blocked
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

---

## WhatsApp direct-chat investigation

### What I did

- Traced every WhatsApp action on `/leads`, `/leads/[id]`, `/dashboard`, and `/find-jobs`.
- Traced buyer-phone data from lead fetchers through normalization, the search API, local tracking storage, and `wa.me` URL construction.
- Inspected the requested dirty worktree without editing it, including the uncommitted Meta WhatsApp route rewrite.
- Inspected the separate `agents/whatsapp-direct-chat` worktree and its uncommitted regression test without modifying that agent's work.

### Files changed

- No JobFilter repository files changed.
- This session note only.

### Decisions made

- Root cause is missing buyer-phone propagation, not the existing `wa.me` links: normalized scan leads do not expose `rawContact.phone`, the frontend lead contract omits `buyerPhone`, and tracked leads are saved without `phone`.
- The only fetcher currently setting `rawContact.phone` uses the placeholder `available`, so any propagation fix must validate a real dialable number before storing it.
- The separate direct-chat worktree fixes frontend propagation and replaces the accidental SMS action, but it does not populate `buyerPhone` in the lead normalizer; by itself it cannot make scanned leads open a client chat.
- Existing direct-chat URL normalization is duplicated and mishandles `0044...`; a shared validated UK normalization helper is the smallest safe implementation boundary.

### Next steps

- Complete the in-progress `agents/whatsapp-direct-chat` work by adding validated backend phone propagation from `rawContact.phone`.
- Keep generic WhatsApp contact-picker behavior for leads without a verified number and label it honestly.
- Do not merge or overwrite the unrelated dirty changes in `agents/protect-dev-routes`.

---

## Uncommitted diff review

### What I did

- Pulled the squad vault and read current JobFilter project context.
- Confirmed the requested dirty worktree and review scope without editing JobFilter files.
- Installed CodeRabbit CLI 0.6.1 in WSL because it was not present.
- Started the required agent authentication flow and opened its browser login URL.

### Files changed

- No JobFilter repository files changed.
- This session note only.

### Decisions made

- The configured code-review workflow forbids substituting a manual review when CodeRabbit authentication or execution fails.
- The review could not run because CodeRabbit remained unauthenticated after the browser login window.

### Next steps

- Run `~/.local/bin/coderabbit auth login --agent` in WSL and complete the browser sign-in.
- Re-run the uncommitted JobFilter diff review after `~/.local/bin/coderabbit auth status --agent` reports authenticated.
