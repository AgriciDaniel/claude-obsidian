---
date: 2026-07-20
project: agent-nudge
type: implementation-plan
status: completed
sources:
  - "[[Full-Walkthrough-Workflow-for-AI-Coding]]"
  - "[[2026-07-20-agent-nudge-future-ultra-research]]"
---

# Agent Nudge v0.3 — Live Agent Bridge

## Decision

The next shipment is the first production-path coordination loop. Portfolio context and deterministic packs remain useful read models, but the home-screen promise is now:

> Two agents. One repository. No stale decisions.

The category is **pre-action context assurance**, not generic shared memory. Agent Nudge should prove that the current constraint reached the relevant agent before an edit, commit, deploy, or decision—and record what the agent did next.

## Why this follows from the portfolio

Across the repositories, the same coordination primitives recur:

- MAZos: gates, explicit state, bounded loops, verified receipts.
- JobFilter: explainable qualification and action thresholds.
- Portfolio Deck: cross-repository attention and freshness.
- Recall and claude-obsidian: source-backed durable knowledge.
- AgentDock: handoffs and human review boundaries.
- FlowLens: friction capture and outcome measurement.

Agent Nudge combines these as product principles without merging their codebases or copying their identities. Its unique ownership is the last-responsible-moment boundary between agents.

## Live loop

```text
agent check-in + task/path intent
  → relevant fact or expiring claim enters the local ledger
  → deterministic fan-out to active same-project recipients
  → recipient sync receives only changes after its cursor
  → HOLD / REVIEW / CLEAR before action
  → acknowledge, release, or replan
  → append outcome receipt
```

## v0.3 vertical slice

- Session check-in and heartbeat with provider, project, task, and paths.
- Fact publication automatically scored against active same-project recipients.
- Per-recipient sync cursor, peer presence, deterministic context-pack digest, and acknowledgement list.
- Expiring file/path claims with acquire and release.
- Claim conflict produces HOLD; release or expiry produces CLEAR.
- HTTP and MCP paths use the same storage and decision engine.
- UI makes live sync primary and keeps Context Mesh secondary.
- No raw prompts, responses, hidden reasoning, file contents, or secrets.
- Production-path tests run from a clean database without `/demo` seeding.

## Definition of done for this slice

1. Claude and Codex check into one project.
2. Claude claims `src/lib/cache.ts` with a lease.
3. Codex declares work on the same path and receives an evidence-backed HOLD.
4. Claude releases the claim; Codex syncs again and receives CLEAR.
5. A relevant changed decision fans out exactly once; an irrelevant or cross-project fact does not.
6. Acknowledgement changes the context digest and prevents repeat delivery.
7. The full flow survives SQLite restart and is callable through MCP.
8. Unit, integration, E2E, lint, typecheck, build, Windows packaging, and portable smoke checks pass.

## Next slice after v0.3

Build **reversible project connection** for Claude, Codex, and OpenCode:

- dry-run first;
- explicit apply;
- owned markers;
- backup and exact disconnect;
- capability labels: `ENFORCED`, `ADVISORY`, `OBSERVED`;
- pre-tool checks where the provider supports them;
- short fail-open timeout and a disk-backed retry outbox.

Do not broaden into cloud sync, orchestration, vector memory, or billing before the local live loop is dogfooded.

## Shipped result

- Source feature commit: `3b240581eabebbfa3ec834d37bb2717b3298c230`
- Release receipt commit: `920ad39`
- GitHub PR: [#3 — Ship Agent Nudge v0.3 Live Agent Bridge](https://github.com/manazoid4/agent-nudge/pull/3), merged as `12a65a593c9c41048ed1a07bfe4eab638a5f849d`
- Production: [agent-nudge-bay.vercel.app](https://agent-nudge-bay.vercel.app)
- Windows: installer and portable v0.3.0 executables built locally; the portable executable passed its loopback health smoke test.
- Quality gate: clean lockfile install, build, typecheck, lint, formatting, 17 unit tests, 11 integration tests, 2 end-to-end tests, and full dependency audit with zero vulnerabilities.
- Live proof: a conflicting exact-path lease produced HOLD, release produced CLEAR, duplicate facts/nudges deduplicated, acknowledgement persisted, and the monotonic cursor advanced.

The automatic provider hook installer and branch/worktree-aware conflict model were deliberately kept out of v0.3; they remain the next shipment.

## Validation gate

Run Agent Nudge for seven days across its own repository and one active revenue project. Keep the wedge only if it produces at least one verified prevented collision, avoided repeated failure, correctly delivered decision change, or materially faster session resumption, while keeping ignored/wrong nudges below 15%.

## Commercial path

- Community: free local loop.
- Pro: £19/month or £190/year for encrypted personal sync, history, and advanced rules.
- Studio: £79/month or £790/year for five people, multi-project rooms, GitHub/Obsidian connectors, and outcome reporting.
- Team: £299/month or £2,990/year for policies, approvals, and audit exports.
- Business: £999/month for SSO, retention, private relay, and priority support.
- Enterprise: £30k–£150k/year plus scoped onboarding for private deployment, compliance, and integrations.

The first revenue experiment should be a paid 30-day Agent Coordination Pilot, not premature self-serve checkout.
