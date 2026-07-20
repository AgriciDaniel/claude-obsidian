---
date: 2026-07-20
project: agent-nudge
agent: codex
status: completed
---

## What I did
- Reviewed prior one-shot and MAZos build-prompt examples from the shared vault.
- Produced and expanded a 1,501-line, 6,875-word one-batch master build prompt for the Agent Nudge product idea.
- Grounded the integration plan in current Claude Code and Codex hook/MCP capabilities.
- Defined the product thesis, deterministic relevance engine, schemas, daemon, SQLite storage, MCP server, Claude/Codex adapters, safe installer, CLI, Electron desktop app, demo scenarios, security model, test matrix, packaging, build receipt, and validation plan.
- Ran an ultra research pass across protocols, enterprise agent platforms, identity/governance, security, memory products, orchestration tools, GitHub projects, and developer discussions.
- Produced a separate 718-line, 4,041-word future strategy covering the 1-, 3-, 5-, and 10-year opportunity, standards strategy, category design, business model, moat, risks, metrics, and kill criteria.
- Expanded the build prompt with future-proof interfaces while explicitly preventing future-platform scope from bloating the MVP.
- Studied JobFilter's qualification, differentiation, ROI, pricing, and launch discipline and translated the useful patterns for a distinct AI-agent audience.
- Added a revenue-maximizing pricing ladder, paid design-partner motion, packaging rules, expansion triggers, pricing experiments, and commercial metrics.

## Files changed
- `02-PROJECTS/Agent Nudge/2026-07-20-agent-nudge-super-x10-build-prompt.md`
- `02-PROJECTS/Agent Nudge/2026-07-20-agent-nudge-future-ultra-research.md`
- `wiki/sessions/2026-07-20-agent-nudge-codex.md`

## Decisions made
- Positioned Agent Nudge as the notification layer for AI agents, not generic shared memory.
- Made the MVP local-first, Windows-first, deterministic, and free of required cloud/LLM services.
- Required three end-to-end proofs: conflicting edit, changed decision, and failed approach; plus irrelevant-event suppression.
- Kept real agent configuration changes, deployment, publishing, remote creation, and paid actions outside the autonomous build scope.
- Refined the durable category from “notification layer” to “pre-action context assurance”: transport and generic memory are inputs, while relevance, timing, policy, provenance, and measured outcomes are the product.
- Chose MCP for local integration, A2A for future remote agent interoperability, CloudEvents-compatible internal envelopes, and OpenTelemetry for export rather than inventing proprietary plumbing.
- Defined the long-term position as the zero-trust context routing and provenance layer between heterogeneous agents.
- Set initial pricing hypotheses at free local, £19 Pro, £299 Team, £999 Business, and £30k–£150k+ Enterprise, with paid pilots and annual-first packaging; all require validation before launch.

## Next steps
- Open the portable build at `C:\Users\manaz\Projects\agent-nudge\release\Agent-Nudge-Portable-0.1.0-x64.exe` or install the setup build beside it.
- Dogfood the verified MVP with Claude Code and Codex on one real repository for seven days.
- Validate that Agent Nudge prevents measurable rework with fewer than 10–15% ignored nudges before expanding into team or enterprise infrastructure.

## Build execution

- Built the production scaffold at `C:\Users\manaz\Projects\agent-nudge` on `agents/agent-nudge-mvp`.
- Implemented the deterministic routing engine, redaction, SQLite ledger, loopback Fastify API, CLI, MCP server, Claude/Codex fixture adapters, Electron app, and public fixture demo.
- Produced and smoke-tested both the Windows installer and portable EXE; the packaged daemon reported healthy on `127.0.0.1:47831` only.
- Passed lint, formatting, strict TypeScript, 11 unit tests, 8 integration tests, 2 end-to-end tests, a clean `npm ci` build, and a zero-vulnerability production dependency audit.
- Published the public repository at https://github.com/manazoid4/agent-nudge with verified source commit `48278ea` and release receipt commit `1d37956`.
- Deployed and interactively verified the public demo at https://agent-nudge-manazir-s-projects1.vercel.app/#demo.
- Closed GitHub issue #1 with acceptance evidence. Because the repository was initially empty, GitHub made the first `agents/` branch the default; no direct push to `main` was performed.

## Build limitations

- The binaries are not backed by a paid publisher certificate and may trigger Windows SmartScreen.
- Agent configuration installation remains preview-only in v0.1.0.
- Node's built-in SQLite API emits an experimental warning.
- Release executables are retained locally and excluded from Git; hashes are recorded in the project `BUILD_RECEIPT.md`.

## v0.3 live bridge follow-through

### What I did

- Audited all 19 owned GitHub repositories and translated reusable patterns into Agent Nudge without merging product identities or exposing private repository names in the public demo.
- Ran parallel market, protocol, architecture, operator, and implementation perspectives across shared memory, agent teams, coordination research, hooks, MCP, pricing, trust, and execution-state design.
- Repositioned the product from generic shared memory to an independent pre-action context assurance and receipt layer.
- Implemented the real local live loop: check-in, heartbeat, task intent, project-scoped fact fan-out, sync cursor/digest, peer presence, exact-path leases, HOLD/REVIEW/CLEAR, release, acknowledgement, HTTP, CLI, MCP, SQLite persistence, and the production-path desktop proof.
- Reworked the site around “Two agents. One repository. No stale decisions,” the `declare → preflight → act → receipt` loop, public-safe live coordination, and a Community/Pro/Studio/Team/Enterprise pricing ladder.
- Upgraded Electron and pinned the patched esbuild line; the full production and development dependency audit now reports zero vulnerabilities.
- Passed clean install/build, typecheck, lint, format, 17 unit, 11 integration, and 2 end-to-end tests; completed desktop/mobile browser QA; built both Windows v0.3 executables; smoke-tested the portable executable.
- Deployed v0.3 to [agent-nudge-bay.vercel.app](https://agent-nudge-bay.vercel.app), merged [PR #3](https://github.com/manazoid4/agent-nudge/pull/3), and closed issue #2.
- Ingested [Full Walkthrough: Workflow for AI Coding](https://www.youtube.com/watch?v=-QFHIoCo-Ko) into the shared vault with its original English automatic-caption VTT, SHA-256 provenance, timestamped source claims, entity/concept pages, and this project application.

### Files changed

- Agent Nudge repository: live-sync core/schema/storage/server/CLI/MCP/UI/tests/docs, v0.3 version/security dependencies, and build receipts.
- `.raw/articles/full-walkthrough-workflow-for-ai-coding-matt-pocock-2026-04-24.en-orig.vtt`
- `.raw/.manifest.json`
- `.vault-meta/address-counter.txt`
- `wiki/sources/Full-Walkthrough-Workflow-for-AI-Coding.md`
- `wiki/entities/Matt Pocock.md`
- `wiki/concepts/AI Engineering Delivery Loop.md`
- `02-PROJECTS/Agent Nudge/2026-07-20-live-agent-bridge.md`
- `wiki/index.md`, `wiki/hot.md`, and `wiki/log.md`

### Decisions made

- The durable moat is the outcome graph from sourced constraint → intended action → timed delivery → acknowledgement → changed action → verified outcome.
- Structured execution state is the shared contract; raw transcripts, hidden reasoning, command bodies, secrets, and file contents are not.
- Agent Nudge should complement native Claude/Codex/GitHub coordination, not become another general memory store or orchestrator.
- Exact-path leases are an honest v0.3 primitive, not a claim of semantic or worktree-aware enforcement.
- Automatic provider connection must be reversible, project-scoped, backup-first, and labelled `ENFORCED`, `ADVISORY`, or `OBSERVED` according to the host’s real capability.

### Next steps

- Ship reversible `connect`/`disconnect` for Claude Code, Codex, and OpenCode with dry-run previews, owned markers, backups, capability labels, and a disk-backed outbox.
- Dogfood v0.3 for seven days across Agent Nudge and one active revenue project; keep the wedge only if it records verified avoided work while wrong/ignored nudges stay below 15%.
- Add branch, worktree, base-commit, and semantic-contract awareness before treating claims as hard cross-worktree conflicts.

## v0.4 Live Connect code audit

### What I did

- Performed a read-only audit of the merged v0.3 adapter, install-preview, CLI, Electron, packaging, daemon, MCP, and relevant tests.
- Traced the existing provider-event path and the separate Live Sync path end to end, with exact source-line evidence.
- Identified the minimum modules and test seams needed for real, reversible Claude Code, Codex, and OpenCode connection.
- Re-ran strict TypeScript checking and the full integration suite; both passed, with 11 integration tests passing.

### Files changed

- `wiki/sessions/2026-07-20-agent-nudge-codex.md` only; the Agent Nudge repository was not modified.

### Decisions made

- Treat current hook normalization as an observed-event primitive, not a live connector: it only stores generic events and does not check in, sync, claim, publish, acknowledge, or translate HOLD into provider behavior.
- Build v0.4 around provider-owned parse/merge/remove logic plus a shared transaction layer with byte-preserving backups, atomic writes, drift detection, and a durable install manifest.
- Unify the Electron, daemon, CLI, and MCP data-directory contract before claiming one connected local ledger.
- Keep all filesystem mutation in the Node/Electron main process; expose plan/apply/disconnect/status to the renderer through narrow IPC only.

### Next steps

- Implement provider-specific connection plans and a production hook runner, then add temp-project round-trip tests for connect, idempotent reconnect, drift refusal, and exact disconnect restoration.
- Extend Windows packaging smoke coverage to prove the shipped executable can connect and disconnect a disposable project without touching real user configuration.
