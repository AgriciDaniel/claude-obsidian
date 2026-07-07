# 2026-07-08 — MAZos Light Redesign (YouMind-inspired) session

Agent: Claude (Sonnet 5) · Repo: `C:/Users/manaz/Projects/mazos-ui` · PR: https://github.com/manazoid4/mazos-ui/pull/47 (merged → main via CI auto-merge)

## What shipped

**Full replace of MAZos's dark cockpit theme with a light theme**, taking design cues from youmind.com — soft off-white ground, restrained violet+coral gradient wash, bold headline type — while keeping the operator-cockpit identity (dense, evidence-first, no marketing chrome). No toggle: dark theme removed entirely, not coexisting.

- `src/app/globals.css` — full token replace (`--bg:#fbfaf9`, `--ink:#15161b`, `--muted:#6b6f78`, `--soft:#33363f`, `--violet` retuned, new ambient-only `--coral:#ff7a59`), `.shell`/`.gridGlow` retinted for light, systematic retint of every dark-literal in the file.
- `src/app/page.tsx` — 3 new real-data strips on NOW view (below Shipping Spine): **Stats strip** (products tracked, oldest stale touch, open blockers, commits/7d — wired to `/api/mazos/shipping-spine` + `/api/mazos/shiplog`), **Evidence → Rank → Ship** 3-card operating-loop strip (static copy, MAZos's real loop condensed), **Recently Shipped** strip (last 5 real commits, linked to GitHub). Restrained `<em>` emphasis on the Spine verdict product name.
- `docs/MAZOS_DESIGN_DIRECTION.md` — rewritten: light palette, gradient-wash rule (≤10% opacity, violet+coral, coral ambient-only never state), new-strip patterns, updated banned list (no template gallery, no marketing CTAs, dark theme banned instead of light).

## Process (spec → build → review loop)

1. `/spec mazos-light-redesign` — interviewed user (full replace vs toggle → full replace; which YouMind features → user said "figure it out, stick to product context"), wrote 10 numbered requirements + edge cases + DoD to `specs/mazos-light-redesign.md`.
2. `/build` — delegated to a worktree-isolated agent (full context in prompt, no back-reference to conversation). Agent implemented all 10 reqs, self-verified via Playwright (screenshots, console errors, computed contrast on `--muted`/`--soft`), caught and fixed 2 real bugs during its own self-check (a retint-script chained-substitution bug that had turned some cards near-black, and a `.massMoves` column-width collision). Opened PR #47.
3. `/review` — checked build against spec line-by-line directly against the diff (not the agent's self-report). Found **1 real gap the agent's own check missed**: `--violet:#6a63f2` measured 4.30:1 against `--bg` (needs 4.5:1 AA) in its actual text-color usages (`.eyebrow`, `a{}`, `b{}`, `span{}`, `.boot`) — agent had flagged it as "marginal" but it's an outright fail for normal-size text. Also found a second, compounding instance: `.primary`/`.researchPrimary` CTA buttons inherited `color:var(--ink)` (near-black in light theme) over an unchanged violet gradient (`#7b7aff → #5550d8`) — near-black text on that gradient only hit ~3.0–3.5:1, well under AA.
4. Fixed directly (didn't loop back through another `/build` round — single CSS-token change): retuned `--violet` to `#4f46e5` (6.03:1), narrowed/darkened the two CTA-button gradients to `#5b52e0 → #3f37c9` with forced white text (5.64:1 / 8.07:1 at the two stops). Re-ran `npm run lint` + `npm run build` (both pass), committed, pushed to the PR branch — repo's existing CI auto-merge pipeline (from an earlier merged PR, `agents/ci-automerge`) merged it to `main` automatically once checks went green.

## Key findings

- **All 25+ locally-stale "unfinished" agent branches were actually already merged** (squash-merged, just not pruned). Checked every one against `gh pr list --state merged` before assuming any backlog existed — zero real orphan work. Corrected the user's premise before doing anything with the branches.
- **Real problem surfaced mid-session**: 44+ merged PRs in MAZos itself (loop-factory, loop-doctor, loop-receipts, clutter-reaper, AI feed, research console, task-gate, openwiki-cockpit, skill-factory...) vs. the tracked revenue products (JobFilter, Recall, OpenFlowKit) sitting stale — 0 commits/7d on OpenFlowKit, parked branches on JobFilter/Recall. MAZos has been building itself, not shipping the products it exists to accelerate. User acknowledged this and chose to continue MAZos work anyway (this redesign) — noted as an explicit, informed tradeoff, not something that was missed.
- Contrast bugs in this PR are a good example of why `/review` needs to check the actual rendered CSS math, not just trust a build agent's self-report: the agent's own Playwright check computed `--muted`/`--soft` contrast correctly and passed, but didn't catch `--violet`'s text uses or the CTA-button gradient interaction — both required grepping actual `color:var(--violet)` call sites and computing WCAG contrast by hand.

## Validation evidence

- `npm run lint` (tsc --noEmit): pass (both build round and fix round)
- `npm run build`: pass (both rounds)
- Contrast computed by hand (WCAG relative-luminance formula) for every text/bg pairing using `--violet`, `--green`, `--red`, `--yellow`, plus the `.primary`/`.researchPrimary` gradient at both stops — all ≥4.5:1 after the fix.
- PR #47: 4 files in original build commit + 1 file in fix commit, base `main`, all CI checks SUCCESS, auto-merged.

## Open items / next session

- Roadmap items #3 (Proof Receipts), #4 (Safe Action Capsules), #5 (Founder Revenue Radar) from `MAZOS_MARKET_BREAKER_ROADMAP.md` still not built — only #1 (Shipping Spine) and #2 (Product Playbooks, partially) exist.
- Sprawl audit (kill-list vs keep-list for the 12+ non-roadmap `/api/mazos/*` routes) was proposed but not run this session — still open.
- Bigger open question, not resolved: should MAZos work continue at all before JobFilter/Recall/OpenFlowKit get real shipped work? User chose "keep going on MAZos" this session; worth revisiting.
