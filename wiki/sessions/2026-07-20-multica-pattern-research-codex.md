---
date: 2026-07-20
project: portfolio
agent: codex
status: completed
---

## What I did

- Audited Multica's landing page, changelog, docs, download flow, use-case story, about page, GitHub repository, and public release pipeline.
- Compared its approach with Keep a Changelog, GitHub-generated release notes, and Linear's product changelog.
- Reviewed current JobFilter vault context and its internal engineering changelogs.
- Produced a reusable research-and-ship prompt for transferring the strongest mechanics to JobFilter or another portfolio project without copying Multica's identity.

## Files changed

- `wiki/sessions/2026-07-20-multica-pattern-research-codex.md`

## Decisions made

- JobFilter should use a customer-facing “What's new” surface rather than exposing internal audit logs.
- Changelog content, the current-version badge, GitHub releases, in-app update indicators, and announcement copy should derive from one validated release record.
- Copy Multica's mechanics—visible shipping cadence, user-language notes, deep links, onboarding, proof-rich use cases, trust documentation—not its agent-teammate positioning or visual identity.
- Avoid Multica's observed content drift: its changelog showed v0.4.5 while its download page showed v0.4.6, and runtime counts differed between public surfaces.

## Next steps

- Run the generated prompt against the live JobFilter repository after resolving its current local path.
- Ship the first verified customer-facing release entry only after founder blockers and production behavior are reconciled.
