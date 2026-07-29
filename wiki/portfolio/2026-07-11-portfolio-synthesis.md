# Portfolio Focus — Deep Research Synthesis

**Date:** 2026-07-11
**Sources:** READMEs (flowlens, JobFilterV1, inkweave, mazos-ui, saved-brain/recall, flipsignal), FlowLens `docs/product/` (thesis, positioning, pricing), JobFilter `docs/SIX_MONTH_REVENUE_PLAN.md`, vault notes (`wiki/projects/*` — jobfilter index + STICKY-TODO, inkweave overview + selling-points, flipsignal index, recall index + strategy, mazos declutter log, project-locations).
**Method:** synthesis, not summary — agreements, contradictions, genuine uncertainty, then one decision.

---

## Where the sources AGREE

1. **One unifying thesis exists and you wrote it down once.** Recall strategy (2026-06-09): *"Every strong project in this portfolio = AI signal recovery for underserved communities."* JobFilter (signal for tradesmen), Recall (signal for savers), FlipSignal (signal for flippers), FlowLens (signal for ops teams) all fit. This is the portfolio's actual identity — it appears implicitly in every product doc but explicitly only once.

2. **Scored-signal + next-action is your repeated design pattern.** JobFilter scores leads 0–100 with reason codes; Recall scores GOLD/SILVER/BRONZE ("borrows the useful JobFilter principle" — its own README says so); FlipSignal scores deals 0–100; MAZos Task Gate scores tasks 0–100; FlowLens scores friction. Same product, five markets.

3. **JobFilter is the only project with a written revenue plan and a hard priority marker.** Vault index (2026-07-05): "Status: Pre-launch / active development (**#1 priority**)". Six-month plan: £2–5k MRR month 3, £10–25k month 6. No other project has either.

4. **Everything blocked on JobFilter is founder-only, not code.** STICKY-TODO (2026-06-11): run one SQL migration, set WhatsApp + Stripe + CRON_SECRET env vars, merge waiting PRs, register webhook. Its own header: "Code is already written and waiting."

5. **MAZos is a meta-tool, not a product.** Its entire feature set (Shipping Spine, Task Gate, Feed) exists to answer "what should ship next" across the *other* projects. It generates zero revenue by design and its own declutter log shows it consuming multiple full agent sessions.

## Where the sources CONTRADICT each other

1. **InkWeave: archived vs active.** Recall strategy (2026-06-09): "InkWeave — **Archived** — no code, crowded market, no edge." But inkweave repo README still says "Stage 1 — MVP planning", vault overview updated 2026-06-15 keeps it current, and your memory index (2026-07) lists it as a live project. You archived it and then kept treating it as alive. Pick one.

2. **JobFilter's stack is described two incompatible ways.** Vault index (2026-07-05): "React 19 + Vite 6 + Express + **Firebase** + Stripe, hosted on Firebase Hosting." README + STICKY-TODO: Next.js app router, **Supabase** migrations, **Vercel** env vars, jobfilter.uk on Vercel. Both dated within weeks of each other. One of these documents describes a repo that no longer exists — the vault index is stale and would misdirect any agent that trusts it.

3. **FlowLens "has revenue" vs no revenue evidence anywhere.** Memory note (2026-07-08): "actual revenue product." But FlowLens docs are entirely pre-revenue artifacts: pricing *rationale*, buyer *personas*, positioning statement, "wow moment" thesis, mock AI provider, demo seed data, apps/desktop and extension "not yet implemented". Nothing — no customer, no Stripe live mode, no MRR figure — corroborates revenue. Either revenue exists undocumented (fix the docs) or the memory is wrong (fix the memory).

4. **What each product is "for" drifts by date.** Saved Brain → Recall pivoted from "IG/Twitter saves → knowledge base" (June 4) to "user-owned personal intelligence layer / memory OS for agents" (June 16) — a much bigger claim. FlipSignal's vault note froze at "phase-1-scaffolded" (June 15) with scrapers returning `[]`, yet the README sells a working "AI-powered marketplace arbitrage engine". Aspirational READMEs vs actual state is a systematic pattern, not a one-off.

5. **Local paths are fiction.** project-locations.md maps 8 projects to Desktop folders; today only `saved-brain` and `Projects\mazos-ui` exist on disk. Your default-working-directory memory points at `Desktop\jobfilter\jobfilterv1`, which is gone. Every agent session starting from these maps burns its first N minutes discovering this.

## What is GENUINELY uncertain (not decided, not contradicted — just unknown)

1. **Whether anyone will pay.** Zero documented paying customers across all repos. JobFilter's plan says "record 50 lead-quality samples" — no evidence this happened. The entire portfolio is pre-first-pound.
2. **JobFilter lead quality at the wedge.** Contracts Finder (public procurement) may simply not carry enough electrician/roofer jobs in West Midlands for £29–39/mo to be worth it. Known limitation in the README itself ("notices do not always include exact delivery postcodes or values"). This is THE product risk and it's testable in a week.
3. **FlowLens market entry as a solo founder.** Corporate-first pricing (£120–£1,200/mo) requires sales motion — demos, security questionnaires, procurement. Nothing in the docs addresses who does that.
4. **Your own time budget.** No document states hours/week available. Every plan implicitly assumes full-time attention on that one project.

## What you keep RE-LITIGATING (already decided — stop reopening)

- OpenFlowKit → folded into Recall (decided 2026-06-09).
- AgentDock → mothballed (decided 2026-06-09).
- InkWeave, LimitLens → archived (decided 2026-06-09 — see contradiction #1; the decision was made, honor it).
- SecureShift + JobFilter share infrastructure, separate brands (decided 2026-06-09).

## THE DECISION the evidence supports

**Finish JobFilter's founder-action checklist and launch it. Everything else goes to maintenance until JobFilter has 10 paying trades or is disproven.**

Why this and not FlowLens/Recall:

- JobFilter is the only project where the remaining work is **hours of founder admin, not months of build** (migration + env vars + merge PRs + Stripe product = one afternoon).
- It's the only one with a written revenue plan, a named wedge (electricians/roofers, West Midlands), a price (£29–39/mo), and a domain (jobfilter.uk).
- You marked it #1 priority yourself on 2026-07-05 and it's your most recently pushed repo (2026-07-10). Behavior and stated priority already agree — the only thing missing is closing the STICKY-TODO.
- FlowLens is the better *long-term* asset (bigger ACV, real moat thesis) but needs a sales motion you haven't designed; it's the wrong *first* revenue.
- The riskiest assumption (Contracts Finder lead quality for trades) is cheaply testable *after* launch with real users' behavior — launch is the experiment.

**Immediate sequence:** (1) run the Supabase migration, (2) set WhatsApp/Stripe/CRON env vars in Vercel, (3) merge PR #252 chain to main, (4) end-to-end test intake → WhatsApp GOLD alert, (5) outreach to 20 Birmingham trades. Also: fix the stale vault index (stack description) and the dead local paths so agents stop tripping on them.
