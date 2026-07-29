---
type: project-log
project: mazos
date: 2026-07-07
tags: [mazos, declutter, shipping-spine, loops, pr]
source: Claude Code session
pr: https://github.com/manazoid4/mazos-ui/pull/40
---

# MAZos Declutter — One Verdict (PR #40)

Ruthless declutter after PRs #31–36 (Research Console, Loop Doctor, Product Loop Packs, Loop Receipts, Competitor Radar, pattern-first Loop Factory). Spec: `specs/declutter-one-verdict.md` (merged as #38). Implementation: PR #40, branch `agents/declutter-one-verdict`.

## Declutter report verdicts

- **Keep:** Shipping Spine (NOW), pattern-first Loop Factory + Loop Doctor scoring, Loop Engineering Deck, Decision Inbox, Research Console reports, Source Intake, Command Palette, Loop Receipts plumbing.
- **Merged:** Morning Brief + feed verdict → Shipping Spine verdict (one "what do I do today" answer). Handoff + Context Map + Tool Router + Runtime Safety → single Agent Prep panel. Ship Log + Stale Radar → feed/spine.
- **Removed:** `/focus` pomodoro page (orphan), Vault Intelligence panel, Loop Doctor aggregate panel, Repo Command Centre, 10 root `MAZOS_*.md` reports (→ `docs/reports/`).
- **Fixed:** feed lanes 9→4, watch capped at 3 and born `seen` (unread 19→3), loop `complete` requires evidence-bearing iteration (400 otherwise), receiptless loops >3 days lose `keep` verdict, custom loop `pattern` backfilled.

## Main daily command centre

`/` NOW tab — Shipping Spine only. It carries verdict, why, owner, safety, needs-you list, avoid-today, handoff prompt, brief copy, publishable update.

## Best next build — SHIPPED same session

PR #40 merged (auto-merge on green checks), then radar→loop shipped as [PR #42](https://github.com/manazoid4/mazos-ui/pull/42) (also merged): every Competitor Radar snapshot and Mass Competitor card (61 buttons, incl. #39's mass catalog) now has `→ Loop Factory`, landing in the cockpit WORK tab with a prefilled pattern-picked draft via `mazos-loopfactory-draft` localStorage handoff. One manual check outstanding: click a button once in the browser to see the form fill.

## AI Intelligence Engine — [PR #43](https://github.com/manazoid4/mazos-ui/pull/43) merged, tests added in [PR #45](https://github.com/manazoid4/mazos-ui/pull/45)

Big joined research+build task: turn scattered AI links/notes (GitHub, Instagram AI Feed, YouTube, docs, prompts, MCPs) into a decision, not more clutter. Spec: `specs/ai-intelligence-engine.md`.

Shipped (already on main by the time I resumed — a parallel session had completed and merged #43 while I was mid-build on the same branch name):
- **Trust layer** (`src/lib/mazos/trust.ts`): `computeTrust` (source clarity, usefulness, testability, evidence, safety risk, duplication, setup complexity, staleness, human gate) → score/level/gaps; `buildEvalChecklist`; approval floor (`approvalGaps`) requiring note + test evidence + source + risk-accepted before anything reaches "approved".
- **AI Source Inbox** (`aiSourceInbox.ts` + `/api/mazos/ai-source-inbox`): paste messy text → URL extraction, github/instagram/youtube/x/docs/website platform detection, github sub-typing (issue/pull/file/repo), keyword-driven type/usefulness scoring, dedupe by normalised URL, suggested action (research/make_skill/add_to_loop_factory/add_to_competitor_radar/save_for_later/ignore). Instagram is classify-only — never fetched, no login.
- **Skill Factory** (`skillFactory.ts` + `/api/mazos/skill-factory`): deterministic rule-based spec generation from a source item or raw text (no external API calls), copyable spec markdown + eval checklist, approval gated by the trust floor.
- **Loop Store** (`loopStore.ts` + `/api/mazos/loop-store`): pack registry with 4 idempotently-seeded starter packs (Founder Command, AI Research, Hermes Clean Context, JobFilter Growth), pack README generator.
- **UI**: one compact "AI Intelligence Engine" panel on the INTAKE tab (paste box, counts, recommended next action, latest items; skill/pack sub-views collapsed) — not a new dashboard. Instagram helper text present verbatim. Morning Brief got compact `aiInbox` + `trust` sections.
- **My contribution this loop**: PR #43 landed with zero test coverage. Added `tests/aiIntelligence.test.ts` (14 cases: URL extraction, platform/type classification incl. github subtypes and Instagram, usefulness scoring, suggested-action + loop-pattern mapping, dedupe via parsePaste/isDuplicate, trust scoring, skill-spec generation, starter-pack seeding idempotency, pack README sections). All green, `npm run lint`/`npm run build` clean, live API smoke-tested on port 3057.

### Session hazard (recurring)
Multiple agent sessions are actively working this same repo/branch namespace in parallel — a second session merged `agents/ai-intelligence-engine` as PR #43 while I was independently building the identical feature on a branch with the same name. Discovered via `git rebase origin/main` reporting "skipped previously applied commit" (content-identical commit already on main). Resolution: verified no drift, added only the missing test file, rebased, force-pushed the now-stale remote branch (`--force-with-lease`, own feature branch only, not main), confirmed PR diff shrank to just the test file before merging.
**Takeaway:** before starting a build with a `git log` check showing an unfamiliar branch name already exists remotely, fetch and diff against origin/main first — don't assume a branch you just created is actually new.

## Session hazards worth remembering

- Two agent sessions shared the same checkout; branches switched mid-work and one commit landed on local `main` (repaired, main reset to origin). Isolated into `git worktree` at `.claude/worktrees/declutter` — do this from the start next time.
- Earlier "Competitor Radar is empty" finding was wrong — read the wrong JSON key (`competitors` vs `snapshots`).
