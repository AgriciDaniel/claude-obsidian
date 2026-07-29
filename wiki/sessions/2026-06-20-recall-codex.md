---
date: 2026-06-20
project: recall
agent: codex
status: completed
---

## What I did

- Earlier today, reviewed commit `3d4e109` for spec compliance, security, owner isolation, duplicate handling, provenance validation, URL canonicalization, extension collection boundaries, and partial-sync queue preservation.
- Ran root and extension checks for that review and reported correctness/data-boundary defects without editing project source.
- Repositioned the landing page around Recall Signals and agency creative intelligence.
- Added the capture → patterns → cited briefs workflow and explicit social-listening distinction.
- Replaced lifetime consumer pricing with Trial, Studio £149/mo, Agency £349/mo, and Agency Plus £749/mo.
- Labelled unshipped team collaboration and automated brief capabilities as pilot/upcoming.
- Added a current competitor matrix and concrete 90-day agency revenue roadmap.
- Ran the unit tests and production build successfully.

## Files changed

- Earlier review: vault session note only.
- `app/(marketing)/page.tsx`
- `app/(marketing)/pricing/page.tsx`
- `docs/strategy/competitor-matrix.md`
- `docs/strategy/90-day-revenue-roadmap.md`

## Decisions made

- Earlier review: commit `3d4e109` was not approved; unrelated project changes were left untouched.
- Position Recall as a high-intent, human-curated signal layer that complements social listening.
- Keep paid team plans in pilot status until shared workspaces, roles, collaboration, and cited brief automation ship.
- Use a four-week £500 credited founding-agency pilot to validate pricing and workflow value.
- Record MagicBrief's announced July 31, 2026 shutdown as a dated market event.

## Next steps

- Resolve the previously reported secure-ingestion review findings before merging that work.
- Recruit the first 40 agency targets and run five workflow discovery calls.
- Create a short demo using a real client topic.
- Implement a dedicated pilot lead-capture flow when product scope permits.
