# MAZos v3 — Deep Spec Addendum (2026-07-19)

> Extends `2026-07-18-mazos-v3-close-the-loop-plan.md`. Same phases A–D, now at file level with exact prompt texts, commands, and acceptance drills — plus new Phases E (measurement) and F (v4 portfolio horizon), a failure-drill suite, and per-phase kill criteria. Everything here obeys v2 constraints: PR-only, propose-only automation, allowlisted exec, no LLM calls from MAZos.

---

## PHASE A DEEP — Evaluator

### A1. `buildEvalPrompt(def)` — exact template (loopEngine.ts)

```
{OTHER_AGENT}: EVAL pass for loop "{name}" ({id}), reviewing commit {lastReceipt.commitRange.to}.

ROLE: adversarial reviewer. ASSUME this iteration is BROKEN until proven otherwise. DO NOT praise. Find what fails.
You must NOT be the agent that wrote it (generator: {lastReceipt.generatorAgent}). If you are, stop and say so.

CHECK, in order — ACT, don't read:
1. Run the verify command(s): {verifyActionIds → display commands}. Paste real exit codes and tails.
2. Execute the changed behavior itself: run the app/route/function the diff touches. UI work → drive it with Playwright/webapp-testing, screenshot proof.
3. Diff review: git show {commit}. Edge cases the author skipped. Placeholder/stub code. Criteria items claimed but not truly met.
4. Does behavior match the plan item named in the receipt note: "{lastReceipt.note}"?

WRITE .loops/{id}/eval.md EXACTLY:
  line 1: VERDICT: PASS   (or VERDICT: REJECT)
  line 2: AGENT: <your name — must differ from generator>
  line 3: COMMIT: {commit}
  then: numbered reasons; for REJECT, each reason = one concrete failing check with pasted output.

FORBIDDEN: editing any file except .loops/{id}/eval.md; fixing the code yourself (that's the generator's next iteration); PASS without pasted execution output.
```

### A2. Receipt schema delta (loopReceipts.ts)

- `LoopRunReceipt.generatorAgent: string` — from `def.agent` at capture time (maker identity for the checker rule).
- `LoopRunReceipt.evaluator: { verdict: 'PASS'|'REJECT'; agent: string; commit: string; fresh: boolean } | null` — parsed from `.loops/<id>/eval.md` lines 1–3. `fresh` = eval COMMIT === current HEAD short-SHA. Parse failures → null (never guess).
- Guard rails: eval `agent` case-insensitive-equal to `generatorAgent` ⇒ treat as null + `evalSelfReview: true` flag surfaced in UI ("generator graded own homework — ignored").
- Edge case, docs-only iteration: verify still runs; evaluator judgment still applies. No special path — simplest thing.

### A3. Completion matrix (loops route)

| autonomy | complete requires |
|---|---|
| suggest | v2 rules (receipt pass + criteria) |
| diff | v2 rules + eval PASS *if* eval.md exists (advisory-strict) |
| branch | v2 rules + **fresh** eval PASS from agent ≠ generator (hard) |

Refusal messages must name the missing thing exactly ("eval.md stale: reviewed 49019e2, HEAD is a3f11c2").

### A4. Acceptance drill
1. Dogfood loop: BUILD iteration → receipt pass.
2. Write eval.md REJECT by hand → complete refused, reason shown.
3. Eval PASS but AGENT = generator → refused, self-review flag.
4. Eval PASS by second agent → completes.
5. New commit after eval → stale → refused.

**Kill criterion**: if after 2 real iterations the eval step feels like ceremony (evaluator never catches anything verify didn't), demote eval to `branch`-only and log why in LOOP.md — don't let the loop grow ritual.

---

## PHASE B DEEP — Discovery skill

### B1. Full `.claude/skills/mazos-triage/SKILL.md`

```markdown
---
name: mazos-triage
description: Morning triage — read spine + GitHub + repos, write triage.md, propose loops. Report-only.
---

## READ (bounded, in order)
1. GET http://127.0.0.1:3046/api/mazos/shipping-spine (fallback: data/mazos/shipping-spine.md)
2. For each repo in src/lib/mazos/paths.ts PATHS (skip _alt/openwiki keys):
   gh pr list --state open · gh issue list --state open --limit 10 · gh run list --limit 5 (failed only)
   git log --oneline --since=yesterday
3. Previous data/mazos/triage.md (carry unresolved rows forward)
4. data/mazos/loop-receipts.jsonl tail — which loops moved yesterday

## JUDGE — score each candidate 0–10, keep max 5
+3 blocks revenue (FlowLens/JobFilter path) · +2 failing CI on main · +2 spine names it as next action
+1 open PR waiting >48h · +1 carried unresolved ≥2 days (escalating)
−5 already an active loop · −5 noise/cosmetic · −10 requires credentials/scraping/destructive anything

## WRITE
1. data/mazos/triage.md:
   | finding | source | score | proposed loop (goal · repo · verify) | status |
   Plus one SAMPLE row: yesterday's most substantive merged commit + "explain this change" prompt.
2. For each finding ≥6: POST /api/mazos/loop-factory {goal, repo, verifyActionId, action:'draft'} — draft ONLY.
3. Append one line to data/mazos/loop-runs.jsonl: {"loopId":"mazos_triage","at":ISO,"type":"iteration","summary":"triage: N findings, M proposed"}

## STOP — the boundary
Never save a loop. Never edit code. Never merge/close/comment on GitHub. Anything credential-shaped,
destructive, or uncertain → POST /api/mazos/decisions {type:'open', source:'mazos_triage', question}.
If MAZos app unreachable: write triage.md anyway from files, note "app offline".
```

### B2. Proposed Loops strip (page.tsx)
- New GET param `/api/mazos/loop-factory?proposed=1` → parses triage.md proposed-loop column → returns drafts with gate scores (re-runs generateLoopDraft server-side; triage's own drafts are not trusted state).
- Strip renders between Loop Deck cards and New Loop drawer: goal · repo · verify · gate score · `[Save]` `[Dismiss]`. Dismiss writes status=dismissed back to triage.md.
- Sample-review card in Shipped zone: commit subject + `[Explain it]` (marks explained in triage.md) + `[Show diff]` (copies `git show <sha>` command). Streak counter = comprehension-rot metric (E).

**Kill criterion**: 5 mornings where <50% of proposals are worth saving ⇒ triage JUDGE rubric miscalibrated; tighten scoring before adding any scheduling frequency.

---

## PHASE C DEEP — Scheduling

### C1. Local task — exact registration (one-time, scripts/register-triage-task.ps1)

```powershell
$Action = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument '-NoProfile -ExecutionPolicy Bypass -File "C:\Users\manaz\Projects\mazos-ui\scripts\run-morning-triage.ps1"'
$Trigger = New-ScheduledTaskTrigger -Daily -At 06:30
Register-ScheduledTask -TaskName 'MAZos Morning Triage' -Action $Action -Trigger $Trigger -Description 'L1 report-only loop discovery'
```

`run-morning-triage.ps1`: ensure stack up (reuse start-mazos-local-stack.ps1) → headless Claude Code: `claude -p "Run the mazos-triage skill. Report-only. Obey its STOP section." --max-turns 40` in mazos-ui; tee output to `data/mazos/logs/triage-YYYY-MM-DD.log`; on nonzero exit append a `stop` event with reason to loop-runs.jsonl (failure is also a receipt).

Token-blowout guard (Orange Book cost #4): `--max-turns 40` hard cap + wrapper timeout 20 min then kill. A hung triage costs one bounded run, never a night.

### C2. Cloud workflow — `.github/workflows/triage.yml`

```yaml
on:
  schedule: [{cron: '0 6 * * *'}]
  workflow_dispatch:
permissions: {contents: write, issues: write}   # NO pull-requests:write — cannot touch PRs
concurrency: {group: triage, cancel-in-progress: false}
```
Steps: checkout `triage` branch (create if absent) → `gh` scans (GITHUB_TOKEN, this-repo only; cross-repo needs a PAT — defer, start single-repo) → write `data/mazos/triage-cloud.md` → commit to `triage` branch → update rolling issue "Morning Triage". Local triage skill READs that issue next morning — cloud feeds local; the two schedulers compose instead of colliding.

### C3. Collision rule
Both fire ~06:30: fine — cloud writes triage-cloud.md + issue only; local writes triage.md and consumes cloud output. Single writer per file. Never let both write triage.md.

**Kill criterion**: 3 consecutive silent scheduler failures (no receipt line) ⇒ scheduler health row in Ops footer before anything else ships. A dead automation that looks alive is worse than the Manual Loop.

---

## PHASE D DEEP — lint + caps

### D1. Loop lint — evidence rules (computed in loops route, shown on card)

| Move | PASS evidence | else badge |
|---|---|---|
| Discovery | loop id appears in a triage.md "proposed" row, or def has `discoveredBy` | ⚠ Blind |
| Handoff | last receipt commitRange on branch `loop/<id>` or worktree path | ⚠ Tangled-risk |
| Verification | verifyActionIds present AND (autonomy≠branch OR fresh eval) | ⚠ Nodding |
| Persistence | ≥1 machine receipt | ⚠ Amnesiac |
| Scheduling | trigger.kind ≠ manual AND a scheduled receipt in last 48h | ⚠ Manual |

Card shows worst badge only. All five green ⇒ `● closed loop` mark. Replaces the keyword Doctor with observed behavior.

### D2. Attempt cap
`captureLoopRunReceipt`: normalize note → item key; 3 consecutive fail-receipts with same item key ⇒ append Decision `escalate: "<item>" failed 3×, circuit open` + fold sets circuitOpen. Human resolution from Decisions strip re-arms the circuit (new `rearm` POST action).

---

## PHASE E — MEASUREMENT (new; economics of judgment)

Canon: loops make generation free, judgment scarce — measure judgment throughput, not output volume. Tiny, derived, no new stores:

`GET /api/mazos/loop-metrics` (reads receipts + triage.md + shiplog):
- **time-to-verify**: median seconds of verify runs (falling = principle #1 working)
- **receipts/week** + pass rate (the nines, portfolio-wide)
- **proposal hit-rate**: triage proposals saved ÷ proposed (discovery quality; feeds B kill criterion)
- **eval catch-rate**: eval REJECTs ÷ evals (evaluator earning its keep; ~0 over weeks ⇒ A kill criterion)
- **sample-explained streak**: consecutive days sample card marked explained (comprehension-rot dial)
- **unattended ratio**: scheduled receipts ÷ all receipts (Manual → autonomous progress)

Surface: one-line strip under Ship Next. No charts (design direction: no metrics chrome) — six numbers, each clickable to its evidence. Ship AFTER C (needs scheduled data to mean anything).

## PHASE F — v4 HORIZON: portfolio loops + deterministic gates (plan-only; do not build in v3)

1. **Standing product loops** (one per revenue product, from playbooks): FlowLens Revenue Loop (goal from playbook currentBet, verify_flowlens + a real user-flow check), JobFilter Conversion Loop. Each: triage-fed plan items, weekly cadence, criteria.json seeded from playbook doneCriteria.
2. **Stripe lesson — deterministic gates in TARGET repos**: pre-commit/CI hooks the agent cannot skip (lint+typecheck+test) in flowlens/JobFilterV1, so MAZos receipts verify what CI already enforced. "Anything deterministic logic can solve never goes to a probabilistic model." Repo work, not MAZos work.
3. **Cattle worktrees**: `wt-<loopId>` dirs created/destroyed per iteration via registered actions (`worktree_open`/`worktree_reap` in commandRegistry — still allowlisted).
4. **Cross-repo cloud triage**: read-only PAT → cloud triage covers all product repos.
5. **Entry condition for ANY of F**: v3 dogfood gate passed. A loop earns parallelism by first stopping a bad run.

---

## FAILURE DRILLS (run once after C lands — ~1 hour; each outcome logged to loop-runs.jsonl. Drills ARE receipts.)

1. **Evaluator down**: delete eval.md mid-loop → branch complete refused with exact message.
2. **Triage hallucination**: plant a fake failing-CI signal → proposal appears but nothing auto-saves; dismiss works.
3. **Broken-build morning**: break mazos build, let scheduled triage fire → skill still writes triage.md ("app offline" path), receipt logged.
4. **Token blowout sim**: set --max-turns 3 on triage wrapper → bounded exit + failure receipt, no runaway.
5. **Tamper**: edit a criteria desc in the dogfood loop → next receipt criteriaTampered:true renders FAIL.

## RISK REGISTER

| Risk | Guard |
|---|---|
| Headless claude at 06:30 hangs on a permission prompt | --max-turns + 20-min wrapper kill + failure receipt; drill 4 |
| Cloud cron commits garbage | triage branch only; permissions block PR/merge; rolling issue reviewable |
| Evaluator theatre (rubber-stamp PASS) | eval requires pasted execution output; catch-rate metric; A kill criterion |
| Triage floods the deck | max 5 findings, score ≥6 to propose, dismiss persists |
| Two loop systems drifting again (triage.md vs Deck) | proposals exist only as drafts until human saves; single store custom-loops.json |
| Scheduled-task rot (the old .ralph lie) | lint Scheduling rule demands a receipt <48h — stale schedule self-reports as Manual |

## SESSION MAP (updated)

1. Phase A (evaluator) — 1 session
2. Phase B (triage skill + proposed strip + sample card) — 1 session
3. Phase C (both schedulers + drills 1–5) — 1 session
4. Phase D (lint + caps + worktree prompt) — 1 session
5. Phase E (metrics strip) — half session, after ≥3 scheduled mornings of data
6. Dogfood gate v3 → then, and only then, open Phase F planning.
