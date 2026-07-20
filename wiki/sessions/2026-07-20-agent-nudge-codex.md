---
date: 2026-07-20
project: agent-nudge
agent: codex
status: completed
---

## What I did
- Reviewed prior one-shot and MAZos build-prompt examples from the shared vault.
- Produced a 1,402-line, 5,902-word one-batch master build prompt for the Agent Nudge product idea.
- Grounded the integration plan in current Claude Code and Codex hook/MCP capabilities.
- Defined the product thesis, deterministic relevance engine, schemas, daemon, SQLite storage, MCP server, Claude/Codex adapters, safe installer, CLI, Electron desktop app, demo scenarios, security model, test matrix, packaging, build receipt, and validation plan.

## Files changed
- `02-PROJECTS/Agent Nudge/2026-07-20-agent-nudge-super-x10-build-prompt.md`
- `wiki/sessions/2026-07-20-agent-nudge-codex.md`

## Decisions made
- Positioned Agent Nudge as the notification layer for AI agents, not generic shared memory.
- Made the MVP local-first, Windows-first, deterministic, and free of required cloud/LLM services.
- Required three end-to-end proofs: conflicting edit, changed decision, and failed approach; plus irrelevant-event suppression.
- Kept real agent configuration changes, deployment, publishing, remote creation, and paid actions outside the autonomous build scope.

## Next steps
- Paste the complete prompt into a fresh coding-agent session from `C:\Users\manaz\Projects`.
- Build locally at `C:\Users\manaz\Projects\agent-nudge` on `agents/agent-nudge-mvp`.
- Dogfood the verified MVP with Claude Code and Codex on one real repository for seven days.
