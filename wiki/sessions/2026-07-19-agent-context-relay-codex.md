---
date: 2026-07-19
project: agent-context-relay
agent: codex
status: completed
---

## What I did
- Clarified the product idea as an agent-to-agent context relay, not another shared-memory store.
- Identified the core loop: observe agent work, detect a relevant context delta, and nudge another agent with the smallest useful handoff.
- Confirmed the idea overlaps a previously recorded MAZos next step: an agent-memory diff before task launch.
- Researched current competitors across product sites, GitHub, Reddit, vendor platforms, MCP, and A2A.
- Found close competitors including ContextStream, Pathmark, shared-agent-memory, Colony, ContextRelay, Handoff, Wenlan, AgentFiles, AgentMem, and deja-vu.

## Files changed
- `wiki/sessions/2026-07-19-agent-context-relay-codex.md`

## Decisions made
- The product wedge is timely context delivery between heterogeneous agents, rather than storing all project history.
- The first version should be a local-first Windows sidecar/CLI with Git and filesystem inputs plus MCP or generated prompt outputs.
- Every nudge should include provenance, relevance, freshness, and an accept/ignore control.
- Do not position the product as generic shared memory; that category is crowded.
- Differentiate on proactive recipient selection, minimal deltas, acknowledgement, expiry, interruption policy, and measurable avoided rework.
- Treat GitHub Agent HQ as the strongest platform threat because it already offers Claude, Codex, and Copilot on shared context and memory inside GitHub.

## Next steps
- Define a narrow MVP around Claude Code, Codex, and Git repositories.
- Prototype agent receipts and a deterministic context-diff engine before adding cloud synchronization.
- Validate demand with a landing page and a small hook-based prototype before building a broad memory platform.
- Test three events first: conflicting file edit, changed project decision, and failed approach another agent is about to repeat.

## Research sources
- https://contextstream.io/
- https://github.com/hacksurvivor/pathmark
- https://github.com/dan-calin/shared-agent-memory
- https://github.com/opencue/colony
- https://github.com/cmhashim/ContextRelay
- https://handoff.computer/docs
- https://github.com/7xuanlu/wenlan
- https://www.agentfiles.io/
- https://agentmem.dev/
- https://github.com/vshulcz/deja-vu
- https://github.blog/changelog/2026-02-26-claude-and-codex-now-available-for-copilot-business-pro-users/
- https://developers.googleblog.com/en/developers-guide-to-ai-agent-protocols/
