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
- Paste the complete prompt into a fresh coding-agent session from `C:\Users\manaz\Projects`.
- Build locally at `C:\Users\manaz\Projects\agent-nudge` on `agents/agent-nudge-mvp`.
- Dogfood the verified MVP with Claude Code and Codex on one real repository for seven days.
- Validate that Agent Nudge prevents measurable rework with fewer than 10–15% ignored nudges before expanding into team or enterprise infrastructure.
