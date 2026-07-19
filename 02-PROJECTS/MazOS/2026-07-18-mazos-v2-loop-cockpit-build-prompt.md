# MAZos v2 — Loop Cockpit Build Prompt

> Copy-paste this entire document into a fresh Claude Code session started in `C:\Users\manaz\Projects\mazos-ui`.
> Source of truth: `github.com/manazoid4/mazos-ui` `main` (synced 2026-07-18, HEAD `e323160`).
> Produced by a 6-agent workflow (repo audit → notes audit → Karpathy loop-engineering research → value audit → architect → adversarial critic). All critic fixes are already merged below — build exactly this, no scope creep.

---

## MISSION

Rebuild MAZos from a 39-route / 46-lib-module cluttered cockpit into a **loop cockpit**: one screen where every unit of work is a **Loop** — a versioned prompt + a machine-runnable verify command + an append-only receipt trail. MAZos never executes agent work; it defines loops, gates them before launch, hands the operator a copy-paste prompt, then captures hard evidence per iteration (commit SHA, diff range, verify pass/fail) and answers one question: **what ships next**.

If a panel does not (a) define a loop, (b) gate one, (c) show a receipt, or (d) answer "what ships next" — it does not exist.

**Evidence this rebuild is needed:** no file in `data/mazos/` written since 2026-07-08 (cockpit idle 10 days). Of 39 API routes, ~25 are orphaned. `massCompetitors.ts` (36KB, largest lib) never produced one artifact. Loop deck telemetry: 13 JSONL lines, mostly "smoke pass 1". One loop has claimed "running" since 07-06. `loop-receipts.jsonl`: 1 line ever. FlowLens — the revenue product — cannot appear in Shipping Spine because `playbooks.ts` doesn't know it exists.

---

## LOOP ENGINEERING PRINCIPLES (the design law — Karpathy / Ralph / Anthropic)

1. **Verification is the bottleneck** (Karpathy: "This latest round of LLMs can automate what you can verify"). Optimize time-to-verify before anything else.
2. **Short leash** (Karpathy: "it's not useful to me to get a diff of 1,000 lines"). Cap iteration size structurally.
3. **Autonomy slider per task**, ceiling set by verifier strength. Suggest → diff → branch. Never auto-merge.
4. **March of nines**: a loop that succeeded once is 10% done. Show success rate over N runs.
5. **One task per iteration** (Ralph). Multi-task passes cascade errors.
6. **Fresh context every iteration; filesystem is the memory** (Ralph: `while :; do cat PROMPT.md | claude-code; done`). State lives in files + git, never a session.
7. **Plan/build split — two prompts, one loop** (Ralph: 3 phases, 2 prompts, 1 loop). One prompt never both decides and does.
8. **Backpressure**: a loop without a hard mechanical gate is a slop machine.
9. **Machine-checkable, tamper-proof "done"** (Anthropic: criteria JSON with `passes` booleans; "unacceptable to remove or edit tests").
10. **Init once, iterate after**: setup phase scaffolds; iterations re-hydrate from disk.
11. **Every iteration ends with a receipt** (commit + log line). No receipt = didn't happen.
12. **Explicit stop conditions**: backlog-empty, max-iteration cap, repeated-failure circuit breaker.
13. **The prompt is a living artifact**: version it, add a rule after every misbehavior.
14. **Quality bar**: loops only aim at objectively checkable goals; open-ended goals decompose first.
15. **Human stays accountable**: specs in, diffs and receipts out. Operator = spec writer + diff inspector.

---

## PHASE 0 — FOUNDATION FIX (do FIRST, everything rests on it)

**BLOCKER found by adversarial review:** `src/lib/mazos/runCommand.ts` uses `spawn(command, args, { shell: false })`. On Windows, `npm` is `npm.cmd` → ENOENT. Run logs prove that across the app's entire life only ONE spawned command ever executed (`git log @{u}..`, twice). Every npm action has silently never run.

1. Fix `runCommand.ts`: resolve `.cmd` on win32 (wrap as `['cmd','/c', ...]` or resolve the executable extension). Keep the allowlist posture — no new exec surface.
2. Register `verify_mazos` in `commandRegistry.ts` (`npm run build` — single command; if a chain is needed, register multiple actionIds; `&&` doesn't exist without a shell).
3. **Acceptance:** execute `verify_mazos` end-to-end from the Action machinery and see a real exit code in the run log. Do not proceed to Phase 1 until this passes.

Also Phase 0, security:
4. Delete `data/mazos/remote-intents.jsonl` (contains a logged `OPENAI_API_KEY`) and `data/mazos/remote-snapshot.json`. `data/` is gitignored — no history scrub needed. **Tell Maz to rotate that OpenAI key at the provider** (it transited a Vercel-deployed endpoint); print this reminder loudly in your final report.
5. Grep `data/` for other secret-shaped strings (`sk-`, `key`, `token`) and report.

---

## PHASE 1 — DELETE (~6,000 LOC out)

Delete these routes under `src/app/api/mazos/` + their matching libs in `src/lib/mazos/`:

| Group | Delete | ~LOC |
|---|---|---|
| Orphaned aggregators | `feed` (+`feed.ts`,`feedState.ts`), `morning-brief` (+`morningBrief.ts`), `flight-recorder` (+`flightRecorder.ts`), `clutter-reaper` (+`clutterReaper.ts`), `agent-runtimes`+`agents` (+`agentRuntimes.ts`) | 1,850 |
| Never-used pipeline | `ai-source-inbox` (+`aiSourceInbox.ts`), `skill-factory` (+`skillFactory.ts`), `ingest`, `loop-store` (+`loopStore.ts`), `trust.ts` | 800 |
| Research surface | `src/app/research/` entire, `mass-competitors` (+`massCompetitors.ts`, 36KB), `competitor-radar` (+`competitorRadar.ts`), `research` (+`research.ts`), `ToLoopButton` | 1,570 |
| Remote + email | `remote/**` (+`remoteSnapshot.ts`,`remoteStore.ts`,`remoteAuth.ts`,`remoteSanitize.ts`), `email`, `email-digest`, `scripts/mazos-publish-remote-snapshot.mjs` | 560 |
| Secondary pages | `src/app/openwiki/` (+`openWiki.ts`+route), `src/app/sessions/` page + `task-gate` route (**keep libs `taskScoring.ts`, `taskGate.ts`**), `mission-plan` (+`missionPlanner.ts`), `context-map` (+`sourceReceipts.ts`), `tool-router` (+`toolRouter.ts`), `vault` route (+`vaultInsight.ts` — vault scan survives as one Action button) | 1,300 |
| Cockpit chrome | `system` route + `systemInfo.ts` + SystemStrip, Ops Radar orb grid (health → one topbar dot), duplicate ProjectCard deck, unused `src/components/ui/{button,input,select}.tsx`, the 11-pattern picker + Loop Doctor / `auditLoopUsefulness` ceremony inside `loopFactory.ts` (~300 of its 432 lines) | 250+ |

Also in Phase 1:
- Extract the 4x copy-pasted `mazosFetch`/`shouldUseLocalBridge` into `src/lib/mazos/client.ts`.
- Add a **FlowLens playbook entry** to `playbooks.ts` (critic: spine rows come from the hardcoded `PLAYBOOKS` array — FlowLens, the revenue product, can never rank without this). Better: derive rows from `config/tracked-repos.json` if cheap; otherwise add the entry.
- Fix the zombie loop at the correct layer: append a `stop` event to `data/mazos/loop-runs.jsonl` (`loops.json` is a derived snapshot — hand-editing gets clobbered).
- Trim `serviceHealth.ts`: remove OpenWiki desktop checks and dead-page copy; keep one red/green topbar dot.
- Fix stale in-app hint in `page.tsx` (references nonexistent `config/loops.json`; custom loops live in `data/mazos/custom-loops.json`).
- Delete or re-init `.ralph/` (STATE.md claims "All stories completed" while prd.json shows 4/5 pending — a lying harness file is worse than none).
- Rewrite `README.md`, `AGENTS.md`, `ARCHITECTURE.md` to ~1 page each describing v2 (they still advertise chopped features and the port-9999 era).

**Phase 1 acceptance (honest scope — spine UI re-add is Phase 2 work, not here):** `npm run build` green; ~14 routes remain (`root, loops, loop-factory, loop-receipts, decisions, shipping-spine, project-status, context-pack, shiplog, repos, action, runs, health, hermes-profile`); grep for imports of every deleted lib returns zero; grep `config/hermes_export/` + `scripts/` for killed-route references returns zero; app renders (current loop strip + decisions + shiplog fine — final layout lands in Phase 2).

---

## PHASE 2 — LOOP CORE (the build)

### Data model — extend `loopEngine.ts`, don't rewrite

```ts
type Loop = {
  id: string;                 // custom_<repo>_<slug>_<sha8>
  name: string;
  goal: string;               // one sentence, objectively checkable
  repo: string;               // key into configured repos
  planPrompt: string;         // PLAN pass: gap analysis → writes .loops/<id>/plan.md, NO commits
  buildPrompt: string;        // BUILD pass: exactly ONE plan item, implement, verify, commit
  promptVersion: number;      // bump on every rule added after a misbehavior
  verify: { actionIds: string[] };  // registered commandRegistry actions; REQUIRED — loop cannot save without one
  criteriaFile: string;       // .loops/<id>/criteria.json — [{id, desc, passes}], all false at start
  autonomy: 'suggest' | 'diff' | 'branch';   // ceiling from verifier strength; no verify → permanently 'suggest'
  budget: { maxIterations: number };          // iterations only — wall-clock is unobservable theatre
  stop: { noProgressAfter: number; sameFailureAfter: number };
  humanGates: string[];
  safetyCeiling: SafetyLevel; // existing L1–L5
  agent: 'Hermes' | 'Claude' | 'Codex';
};
// NOTE: no `trigger` field — nothing schedules anything; manual-only until a scheduler exists.

type LoopRunReceipt = {
  loopId: string; at: string; iteration: number;
  verify: { actionId: string; exitCode: number; passed: boolean; tail: string }[];
  commitRange: { from: string | null; to: string | null; count: number } | null;
      // prevReceiptCommit..HEAD — flag receipts spanning >1 commit; git log -1 alone
      // credits unrelated work to the loop
  diffStat: { files: number; insertions: number; deletions: number } | null;  // over commitRange
  criteriaHash: string;       // sha256 of criteria.json content at capture time
  criteriaTampered: boolean;  // prev receipt's hash vs `git show HEAD:.loops/<id>/criteria.json`
                              // — descriptions edited or items removed ⇒ true ⇒ receipt renders as FAIL
  criteriaFlipped: string[];
  outcome: 'pass' | 'fail' | 'gated' | 'stopped';
  note: string;               // one human line: which plan item
};

// LoopState = fold over receipts (no manual state clicks):
//   status idle|running|gated|stopped|done
//   successRate = passes / last N receipts        ← the "nines" counter
//   trusted = successRate ≥ 0.8 over ≥ 5 receipts
//   circuitOpen = same failure ≥ stop.sameFailureAfter
//   zombie guard: 0 receipts and >3 days running ⇒ auto-stop "no evidence"
```

**Key change from v1: the receipt is machine-filled, not hand-typed.** "Log receipt" runs the loop's verify actions via the (now Windows-working) `runCommand`, plus `git log prevReceiptCommit..HEAD` and `git diff --stat` on `loop.repo`, and appends the receipt. Human contributes one note line. You cannot click your way to a completed loop.

### Tasks
1. `loopEngine.ts`: extend LoopDef → Loop; state fold over receipts; circuit breaker + zombie auto-stop; two prompt renderers (plan/build) reusing `handoff.forbiddenFor` FORBIDDEN blocks. buildPrompt template hard-codes "pick exactly ONE unchecked item from plan.md". Prompts forbid editing `criteria.json`.
2. `loopReceipts.ts`: `captureReceipt(loop)` per the model above (commit range, diffStat, criteria hash/tamper check).
3. `commandRegistry.ts`: register per-repo verify actions (`verify_mazos`, `verify_jobfilter`, `verify_flowlens`, …) — single commands each, chains = multiple actionIds.
4. `loopFactory.ts`: slim to goal+repo+verify → draft (~80 LOC); on save scaffold `.loops/<id>/{plan.md,criteria.json,progress.md}` in the target repo; gate preflight via `taskScoring.scoreTask` — prompts locked until score passes; unverifiable goal → only path is "decompose into criteria first".
5. `/api/mazos/loops`: GET folds receipts; POST actions `verify`, `receipt`, `gate`, `stop`; gate → existing `decisions.ts` wiring; complete refused unless last receipt passed AND all criteria true.
6. `page.tsx` rebuild — **one screen, no tabs**, four zones top-to-bottom:

```
TOPBAR   mission · health dot · bridge status · link: HERMES
1 SHIP NEXT   (shippingSpine) one row per product: objective · next action ·
              evidence · blocker · [Context Pack] [→ New Loop (prefilled via props,
              NOT localStorage — the old handoff was never wired)]
2 LOOP DECK   one card per Loop: name · repo · state · successRate · last receipt
              (commit ✓/✗) · circuit/leash flags. Buttons: [Plan prompt]
              [Build prompt] [Run verify] [Log receipt] [Gate] [Stop] [Add rule].
              Inline gate preflight score. [+ New Loop] drawer.
3 DECISIONS   thin strip (decisions.ts): open gates · approve/deny/answer ·
              copy resolution prompt. Empty = invisible.
4 SHIPPED     shipLog last 7 days, GitHub links. Footer: ~5 proven Action buttons
              (incl. vault scan) + last runs one-line each.
```

Secondary page `/hermes` unchanged. `/research`, `/sessions`, `/openwiki` are gone.

**Phase 2 acceptance:** create one real loop against mazos-ui itself; run verify from the card (real exit code on Windows); log a receipt; receipt JSONL contains commitRange + diffStat + criteriaHash; complete refused while criteria unfinished; a gate lands in the Decisions strip; New-Loop prefill from a Ship Next row works.

---

## PHASE 3 — POLISH

1. Migrate the 5 built-in loop templates to the new schema — each gets a real verify action or gets deleted (principle 14).
2. Leash flag: card turns red when a receipt's diffStat exceeds ~300 changed lines (principle 2). Trusted badge at ≥5 passing receipts (principle 4). `promptVersion` + "Add rule" quick-edit (principle 13).
3. Empty states for all four zones; design rules per `docs/MAZOS_DESIGN_DIRECTION.md` (every row implies action/decision/evidence; no charts, no metrics chrome).
4. Update `LOOP.md` / `STATE.md` / `loop-budget.md` to point at the in-app system — one loop system, not two.
5. `npm run build` + webapp-testing pass over the single screen.

## PHASE 4 — DOGFOOD GATE (calendar-gated, separate from Phase 3)

Run the **Daily Triage loop** for real: 5 iterations over 5 days, machine-captured receipts with commit SHAs in `loop-receipts.jsonl`. This is the acceptance test for the whole rebuild. Documented since July 4, never run once. If receipts don't accumulate, the design failed and gets one more chop.

---

## CONSTRAINTS (hold throughout)

- **No auto agent execution.** Agents launch only via copied prompts. Only shell surface = pre-registered `commandRegistry` allowlist (verify actions + ~5 proven ops actions). Same posture as today.
- **Local-first.** Vercel host + 3047→3046 bridge untouched. `/api/mazos/shipping-spine` and `/api/mazos/repos` contracts preserved (external agents consume them).
- **Minimal code.** Phase 2 extends `loopEngine`/`loopReceipts`/`loopFactory`/`taskScoring`/`runCommand` — no new modules beyond `client.ts`. Net LOC down ~5,000 even after the loop core lands.
- **Git:** branch + PR, never push main. Verify build green before every commit.
- **Stop and ask** if: a deletion breaks a surviving import you can't cheaply rewire; the Windows spawn fix doesn't produce a real exit code; anything secret-shaped appears beyond the known leak.

## FORBIDDEN

No new features beyond this document. No schedulers/cron. No email. No LLM calls from MAZos. No auto-merge. No editing `.loops/*/criteria.json` from any prompt template. No force push. No credential changes beyond deleting the leaked file.
