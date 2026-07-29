# MAZos Research Prompt — Proof Receipts, Safe Action Capsules, Revenue Radar

Date: 2026-07-06
Status: delivered to Maz in chat; ready to hand to research agent (Gemini)
Grounding: repo state as of PR #22 (operator inbox, flight recorder, explainable ranking). Excludes already-researched feed/inbox territory (PR #16). Targets roadmap features 3–5 in `docs/MAZOS_MARKET_BREAKER_ROADMAP.md` plus "Next Improvements" from `MAZOS_AI_FEED_REPORT.md`.

Related: [[2026-07-05-ai-feed-research-prompt]], [[2026-07-06-operator-inbox-session]]

---

```markdown
# MAZos Research Brief — Proof, Safe Actions & Trust Layer for a Solo-Founder AI Cockpit

## Who I am and what MAZos is

I'm a solo founder running multiple products (JobFilter — revenue priority, Recall, OpenFlowKit, MAZos itself). MAZos is my private AI operating cockpit: a local-first Next.js app (hosted read-only mirror on Vercel) that tells me *what to ship next* and lets me hand scoped missions to coding agents (Claude Code, Codex, OpenCode, Hermes).

It is deliberately NOT: a chat UI, a CRM, a calendar/email suite, or an autonomous agent loop. Doctrine: every panel must reduce decision load and answer "what should ship next."

## What is already built (do not re-research these)

- **Shipping Spine** — evidence-ranked "ship next" verdict across all products, with per-product playbooks and ready-made agent handoff prompts.
- **AI Feed v1.2 — Operator Inbox**: lane-based triage inbox (Needs Decision, Blocked, Failed Checks, System Pressure, Stale Work, Ready to Ship, Knowledge Gaps, Watch, Done). Item states (unread/seen/saved/snoozed/done) persisted locally. Morning Command Brief strip. Deterministic aggregation only — no LLM calls, no crawling, no cron.
- **Explainable ranking** — every feed item carries a score breakdown (urgency, revenue weight, blocker, evidence, risk, recency, spine-fit, system pressure).
- **Evidence quality grading** — strong/partial/weak/missing per item, from file paths, corroboration, freshness.
- **Flight Recorder v1** — deterministic per-product timeline of agent runs, decision gates, preflight scores, mission plans; explicitly lists what is `notVerified` rather than inventing history.
- **Agent Task Gate + mission planner** — preflight scoring before an agent launch; structured launch prompts (MISSION / CONTEXT / EVIDENCE / SUCCESS CRITERIA / FORBIDDEN / STOP-AND-ASK / REPORT BACK).
- **Safety posture**: L1–L5 safety levels, safe mode on, no shell/push/destructive actions from the UI, PR-only workflow.

## What I need researched (next roadmap features)

### 1. Proof Receipts (primary focus)
I want every "done" claim by an agent to be backed by a verifiable receipt: what command ran, what output proved success, links to CI/deploy/commit. Research:
- Prior art on verifiable agent work: how do Devin, OpenHands, Cursor background agents, GitHub Copilot coding agent, Sweep, Factory.ai *prove* a task is done vs merely claim it? What artifacts do they attach (test output, screenshots, diffs, deploy checks)?
- LLM observability patterns (Langfuse, Helicone, Braintrust, OpenTelemetry GenAI conventions): what event/span schemas exist for "task attempted → evidence → verified"? Anything I can adopt as a receipt schema rather than inventing one?
- Attestation ideas from CI/CD: signed provenance (SLSA, in-toto, GitHub attestations) — is a lightweight local analogue sensible for agent receipts, or overkill for single-machine use?
- Concrete recommendation: a minimal receipt JSON schema (fields + evidence-quality grading) that a deterministic aggregator can validate WITHOUT calling an LLM.

### 2. Safe Action Capsules (secondary)
One-click, pre-scoped, reversible actions from the cockpit (e.g. "re-run failing check", "open PR from branch", "snooze + create decision"). Research:
- How do production tools bound blast radius for one-click actions? (GitHub required reviews, Vercel promote/rollback, database migration dry-runs, Terraform plan/apply split, "two-man rule" patterns.)
- Patterns for undo/rollback and idempotency in local automation. What makes an action safe enough to run without confirmation vs needing a gate?
- Recommend a capsule definition format: preconditions, dry-run output, execute step, verify step, rollback step, max blast radius.

### 3. Founder Revenue Radar (light scan only)
- What do solo founders / indie hackers actually track daily that changes shipping decisions (MRR events, churn signals, conversion breaks)? Survey what Baremetrics/ProfitWell/Stripe webhooks expose, and which 3–5 signals would justify re-ranking a shipping feed. No dashboard designs — signals only.

## Hard constraints (respect these in every recommendation)

- Local-first, single machine, Windows. Hosted mirror is read-only.
- Deterministic core: no LLM calls inside the feed/receipt pipeline (LLM summarization may exist later as a copy-prompt, never automatic).
- No autonomous loops, no cron, no crawling, no new databases (flat JSON/markdown files preferred).
- Solo-founder scale: reject anything needing a team, a server fleet, or enterprise SSO. Prefer boring, minimal, verifiable.

## Deliverable format

1. **Executive verdict** — which of the 3 features has the highest leverage next, in one paragraph.
2. **Per-feature findings** — prior art table (tool → mechanism → what to steal → what to skip), then a concrete design recommendation sized to a 1–2 PR implementation.
3. **Receipt schema draft** (feature 1) — actual JSON field list with rationale.
4. **Capsule format draft** (feature 2) — actual field list with rationale.
5. **Sources** — links for every claim; mark anything you couldn't verify as unverified.

Keep total output under ~2,500 words. Evidence over opinion. If prior art contradicts my constraints, say so and propose the constraint-respecting alternative rather than silently dropping it.
```
