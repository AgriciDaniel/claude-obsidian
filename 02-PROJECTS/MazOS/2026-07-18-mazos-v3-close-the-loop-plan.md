# MAZos v3 — Close the Loop (Ultra Plan, 2026-07-18)

> Built from the three canon sources saved to memory: Greyling's Loop Engineering Playbook, AI Builder Club's Anthropic Playbook, and the asixiv Orange Book (Osmani/Steinberger/Cherny, June 2026). Copy-paste this whole document into a fresh Claude Code session in `C:\Users\manaz\Projects\mazos-ui` after PR #50 (v2 Loop Cockpit) is merged. Self-contained.

---

## THE AUDIT — MAZos v2 scored against the Five Moves

The Orange Book: one loop turn = **discovery → handoff → verification → persistence → scheduling**. Skip a move, get a named anti-pattern. Verdict on v2:

| Move | v2 state | Anti-pattern we are today |
|---|---|---|
| Discovery | ❌ Maz hand-writes every loop goal | **Blind Loop** — "the human still spends their morning deciding what the loop should do" |
| Handoff | ⚠️ single agent, no worktree isolation | Tangled Loop *waiting to happen* at parallelism |
| Verification | ⚠️ mechanical verify (build) ✓, but **no independent evaluator** | **Nodding Loop** for every quality a build can't catch |
| Persistence | ✅ `.loops/<id>/` files, receipts JSONL, git | — |
| Scheduling | ❌ v2 deliberately dropped `trigger` ("nothing schedules anything") | **Manual Loop** — "a script the human runs by hand and then forgets" |

v2 built the skeleton (receipts, criteria, gates) — the canon says the remaining two missing moves are exactly what makes a loop a loop: *"automations are what make a loop an actual loop and not just one run you did once."* Also: the four silent costs (verification debt, comprehension rot, cognitive surrender, token blowout) get guards.

Build order follows Anthropic principle #3 — **verifier before scaling generator**. Evaluator first, then discovery, then scheduling, then parallelism last (*"a loop earns the right to run more agents by first demonstrating it can stop a single bad one"*).

---

## PHASE A — EVALUATOR (kill the Nodding Loop)

Canon: generator grading its own work praises it; tune a skeptic, don't fix a modest author; evaluator must **act, not read**; completion judged maker–checker style by someone who didn't write the code.

MAZos never calls LLMs, so the evaluator is a third copy-paste prompt whose output is machine-checked:

1. **EVAL prompt** — third renderer in `loopEngine.ts` (`buildEvalPrompt(def)`), alongside PLAN/BUILD:
   - "ROLE: adversarial reviewer. ASSUME the last iteration of loop `<id>` is BROKEN until proven otherwise. DO NOT praise."
   - Must ACT: run the verify command(s), execute the changed code path, use Playwright/webapp-testing on UI work, paste real output.
   - Must be a DIFFERENT agent/model than the generator recorded in the last receipt (maker–checker).
   - Writes verdict to `.loops/<id>/eval.md`: first line `VERDICT: PASS` or `VERDICT: REJECT`, then reasons, then `AGENT: <name>` + the commit SHA reviewed.
2. **Receipt capture reads eval.md**: `captureLoopRunReceipt` gains `evaluator: {verdict, agent, commit, fresh} | null` — `fresh` = eval commit matches current HEAD. Stale or generator-authored eval = ignored.
3. **Completion tightens**: loops with `autonomy: 'branch'` cannot complete without a fresh `VERDICT: PASS` from an agent ≠ generator. `suggest`/`diff` loops keep v2 rules (don't over-gate small loops — simplest thing that works).
4. **UI**: LoopCard gains `[Eval prompt]` button + evaluator status line (`eval: PASS by Hermes @49019e2` / `no eval — branch loops can't complete`).

**Acceptance**: run the dogfood loop one iteration; evaluator REJECT blocks completion; PASS from second agent unblocks; stale eval (new commit after eval) blocks again.

## PHASE B — DISCOVERY (kill the Blind Loop)

Canon: "letting the agent find its own work rather than being handed a list… discovery sets the ceiling on the whole loop's quality." Discovery lives in a **skill, not a wall of cron text**.

1. **Triage skill** — `.claude/skills/mazos-triage/SKILL.md` in mazos-ui:
   - READ: `GET /api/mazos/shipping-spine`, `gh` open PRs/issues/failed checks across tracked repos (paths.ts list), commits since last run, previous `data/mazos/triage.md`.
   - JUDGE: actionable now or noise? blocks revenue (FlowLens/JobFilter weighted)? already tracked as a loop? (Greyling: triage cheap — one pass, no maker-checker at triage stage.)
   - WRITE: `data/mazos/triage.md` table `| finding | source | priority | proposed loop | status |` + POST draft loops to `/api/mazos/loop-factory` (`action:'draft'` only — never auto-save).
   - STOP: never merge, never edit code, anything uncertain → Decision strip. Max 5 findings/run.
2. **Proposed Loops strip** in the Loop Deck: renders drafts from triage.md with gate score; one click = gate + save. Human stays chooser (cognitive-surrender guard).
3. **Read-a-sample ritual** (comprehension-rot guard): triage output always includes one merged commit from yesterday with "explain this change" — surfaces in Shipped zone as a daily card.

**Acceptance**: run the skill manually once; triage.md written; ≥1 sensible proposed loop appears in UI; sample-review card renders.

## PHASE C — SCHEDULING (kill the Manual Loop)

Canon: local /loop buys frequency + local file access (machine on); cloud cron buys true autonomy (coarse interval). Mature loop uses both. Safety posture holds: automation only ever *reads and proposes* — no auto-merge, no auto-save of loops, human door stays open.

1. **Local**: register a second scheduled task **MAZos Morning Triage** (06:30 daily): headless Claude Code invoking the mazos-triage skill in mazos-ui, L1 report-only. Output = triage.md + drafts. Appends a `triage` receipt line so loop-lint sees scheduling evidence.
2. **Cloud**: `.github/workflows/triage.yml` cron `0 6 * * *` — repo-only triage (issues/PRs/CI via gh, no local paths), commits `data/mazos/triage-cloud.md` on a `triage` branch + updates one rolling issue. Never touches main. Runs when the laptop lid is shut — the "while you sleep" half.
3. **Trigger metadata returns, honestly**: `Loop.trigger?: {kind:'manual'|'local-task'|'cloud-cron', ref:string}` — pure metadata linking a loop to its automation; UI shows "last scheduled run" from receipts. (v2 dropped `trigger` as decorative; it returns only because the schedulers now exist.)

**Acceptance**: scheduled task fires next morning and triage.md timestamp updates with zero human input; cloud workflow green on manual dispatch.

## PHASE D — HANDOFF, CAPS, LOOP LINT

1. **Worktree handoff**: BUILD prompt template gains "work in an isolated worktree: `git worktree add ../wt-<loopId> -b loop/<loopId>`; commit there; PR from that branch." Parallelism last — only after A–C proven.
2. **Attempt cap** (Greyling: 3 attempts then escalate): receipt capture counts consecutive fails per plan item; 3rd identical fail auto-files a Decision ("escalate: <item> failed 3×") and opens the circuit. Token-blowout guard in iteration units.
3. **Loop lint** (the Doctor, resurrected honestly): per-card five-moves checklist computed from *evidence*, not keywords — discovery source? (proposed by triage vs hand-written), schedule? (trigger + scheduled receipts), evaluator? (fresh eval.md), persistence? (receipts exist), isolation? (worktree branch in commitRange). Card names the loop's current anti-pattern: `⚠ Manual Loop — no schedule`.
4. **Docs**: LOOP.md gains the five-moves table + four-costs guards; AGENTS.md gains evaluator rules.

**Acceptance**: dogfood loop card shows lint improving as A→C land (Nodding → Manual → clean).

---

## ORDER & SESSIONS

1. Session 1 — Phase A (evaluator). Verifier is load-bearing; nothing scales before it.
2. Session 2 — Phase B (discovery skill + proposed strip).
3. Session 3 — Phase C (both schedulers).
4. Session 4 — Phase D (worktrees, caps, lint).
5. Dogfood gate v3: **5 consecutive mornings where triage ran unattended, proposed ≥1 loop, and at least one loop iteration passed both verify AND evaluator.** Receipts prove it or the design gets chopped again.

## CONSTRAINTS (unchanged from v2)

Branch + PR, never main. No auto-merge anywhere, ever. Automation reads/proposes only. `commandRegistry` allowlist is the only exec surface. Local-first; bridge contract intact. Minimal diffs — extend `loopEngine`/`loopReceipts`/`loopFactory`, no new modules except the skill and workflow files.

## FORBIDDEN

No auto-save of proposed loops. No evaluator run by MAZos itself (it's a prompt, machine-checked). No schedule shorter than daily until the dogfood gate passes. No parallel worktree fan-out before Phase D. No editing `.loops/*/criteria.json` or `eval.md` from generator prompts.
