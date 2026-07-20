---
date: 2026-07-21
project: portfolio
agent: codex
status: completed
type: session
title: "GitHub History Hygiene Cleanup"
tags:
  - github
  - repository-hygiene
  - agent-nudge
  - portfolio
related:
  - "[[2026-07-20-jobfilter-codex]]"
  - "[[2026-07-20-jobfilter-whats-new-codex]]"
  - "[[2026-07-20-live-agent-bridge]]"
---

# GitHub History Hygiene Cleanup

## What I did

- Audited all 20 repositories for default branches, branch counts, open PRs/issues, releases, archive state, descriptions, homepages, and recent commit history.
- Read the commit and PR history of Agent Nudge, JobFilter, the shared vault, FlipSignal, and InkWeave before changing refs.
- Migrated Agent Nudge's default from `agents/agent-nudge-mvp` to protected `main` at the same released merge commit (`6382113`).
- Retargeted the v0.4.0 GitHub Release to `main`, preserved both Windows assets and SHA-256 digests, added the live homepage and six useful repository topics.
- Enabled enforced PRs, conversation resolution, no force pushes, and no branch deletion on Agent Nudge `main`.
- Removed 10 obsolete GitHub branch refs: the old Agent Nudge default, four already-merged vault branches, three already-merged FlipSignal branches, the merged Scrap Finance Partners session branch, and one duplicate Saved Brain session branch.
- Merged vault PR #8 because it was a clean, single-file launch receipt. Closed vault PR #2 because its commit and file are fully contained in PR #3.
- Reduced the vault from six open PRs to four. The remaining PRs contain unique material and are labelled `knowledge-backlog` plus `stale-review` instead of being deleted.
- Set JobFilter, Agent Nudge, FlipSignal, and the shared vault to squash-only PR merges with automatic branch deletion and PR-title commit subjects.
- Pruned local Agent Nudge branches and fixed local `origin/HEAD` to track `main`.

## History findings

- JobFilter's noisy July history came from many tiny copy PRs and vault/digest commits. The public-repository cleanup removed the obsolete automation paths; current open PR #376 remains active and was not touched.
- Agent Nudge has a compact, valid ten-commit history. Its problem was naming and policy, not commit content. Rewriting it would have broken the released tag for no gain.
- Vault PR #3 includes the entire PR #2 commit, making #2 the only proven duplicate.
- Vault PRs #1, #3, #4, and #5 add unique audits, strategy, or redacted memory material. They require human content decisions, not automated deletion.
- FlipSignal's three removed branches all belong to merged PRs. Its open TypeScript-hygiene PR #5 remains intact.
- InkWeave is archived. GitHub blocks ref deletion while archived; its five merged feature branches were deliberately left untouched rather than generating unarchive/rearchive churn.
- Seven active legacy repositories still use `master`. They each have a single default branch and no open PR clutter. They were left unchanged because a bulk rename could disturb Vercel, vault scripts, or local clones without improving history.

## Files changed

- No product source files changed.
- GitHub repository refs, settings, labels, PR states, default branch, release target, homepage, and topics changed through the GitHub API.
- This vault session note plus `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md` record the cleanup.

## Decisions made

- Never rewrite published history merely to make the graph prettier.
- Delete a branch only when its PR is merged or its content is provably contained elsewhere.
- Preserve unique stale work as labelled backlog until a human decides merge versus archive.
- Use squash-only PRs on active code/history-heavy repositories so one product change creates one mainline commit.
- Treat archived repositories and legacy `master` defaults as explicit exceptions, not automatic cleanup targets.

## Current clean state

| Repository | Default | Branches | Open PRs | Notes |
|---|---:|---:|---:|---|
| Agent Nudge | `main` | 1 | 0 | Protected; v0.4.0 release targets main |
| JobFilter | `main` | 2 | 1 | Main + active nightly copy PR |
| Claude Obsidian | `main` | 5 | 4 | Main + four unique labelled backlogs |
| FlipSignal | `main` | 2 | 1 | Main + active TypeScript hygiene PR |
| InkWeave | `main` | 6 | 0 | Archived; branch cleanup intentionally skipped |

## Next steps

1. Review vault PRs #1, #3, #4, and #5 individually; merge useful knowledge or close with an explicit archive reason.
2. Review JobFilter PR #376 and FlipSignal PR #5 through their normal build/CI gates.
3. Only rename the seven legacy `master` defaults during project-specific sessions that can verify deployment and local tooling.
4. If InkWeave is revived, delete its five merged feature branches during the unarchive session.

## Verification

- Agent Nudge `main` points to released commit `6382113`, is protected, and is the GitHub/local default.
- Agent Nudge v0.4.0 still exposes both verified Windows assets and targets `main`.
- Post-cleanup branch/PR counts were re-read through GraphQL.
- No open or unmerged branch was deleted.
