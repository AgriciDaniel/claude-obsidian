---
type: session
project: mazos
date: 2026-07-07
tags: [mazos, loop-factory, loop-engineering]
---

# MazOS Loop Factory — pattern-picker-first shipped

## State found
- Loop Factory already fully on `main` (c6a61c4, PR #35): `loopFactory.ts` with 10 patterns, readiness scoring, usefulness audit (Loop Doctor dimensions), Competitor Intelligence draft, custom-loop save merged into Loop Engineering Deck, runner-prompt generation.
- Old `agents/loop-factory` branch is stale (main superseded it) — ignore/delete.
- Local site already running: Next dev on **http://localhost:3046** (bridge on 3047).

## Shipped this session — PR #36
https://github.com/manazoid4/mazos-ui/pull/36 (`agents/loop-factory-pattern-first`)

Design decision implemented: **pattern picker first**, plain-English goal inside it.
- Pattern select moved above goal field, default `research-intelligence`, hint line per pattern.
- `Auto-pick` demoted to "last resort" at bottom of list.
- Bugfix: duplicate React key warning in Morning Brief needs-you list (`${lane}: ${title}` collided for two open PR Babysitter decisions) → indexed key.

## Verification
- `tsc --noEmit` clean.
- Playwright against live localhost:3046 WORK tab: pattern-first layout renders, Draft Loop generates "JobFilter Competitor Intelligence" card with readiness score, gates, evidence; console errors zero after key fix.

## Open next
- Merge PR #36.
- First real run: save Competitor Intelligence loop, copy runner prompt, feed results into Operator Inbox.
- Cleanup: delete stale `agents/loop-factory` + `agents/loop-factory-product-line` branches.

Related: [[2026-07-06-mazos-loop-factory-research-codex]]
