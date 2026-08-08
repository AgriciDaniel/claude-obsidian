---
title: Missing Skills and Repos Sweep
created: 2026-08-08
updated: 2026-08-08
session_id: 019fe272-7b91-7220-bc12-60298909a4b9
worker_agent_id: 019fe29d-47f2-7761-80d4-d7038c57044d
tags: [codex, skills, repos, inventory]
---

# Missing Skills and Repos Sweep

## Inspected

- `C:\Users\manaz\.codex\AGENTS.md`
- `C:\Users\manaz\.codex\skills`
- `C:\Users\manaz\.claude\transcripts`, `sessions`, `plans`, `history.jsonl`
- `C:\Users\manaz\.claude\skills`
- `C:\Users\manaz\.agents\skills`, `skills-library`
- `C:\Users\manaz\Desktop\Obsidian Main Vault\wiki\sessions`
- Non-Zawiya project records for JobFilter, InkWeave, and OpenFlowKit

Zawiya private content was excluded.

## Findings

- `https://github.com/AgentWrapper/agent-orchestrator` appeared in previous Claude transcripts but had no durable vault record.
- `https://github.com/manazoid4/flowlens` appeared in a previous Claude plan and exists locally at `C:\Users\manaz\flowlens`, but lacked a project index.
- Claude-only skills found outside Codex:
  - `task-observer`
  - `agency-agents`
  - `agent-skills`
- Broader uncertain skill/repo candidates were mentioned in transcripts, but evidence showed research/discussion rather than a clear install decision:
  - `anthropics/skills`
  - `affaan-m/everything-claude-code`
  - `ComposioHQ/awesome-claude-skills`
  - `majiayu000/claude-skill-registry`

## Actions Taken

- Added FlowLens to durable project records.
- Added `AgentWrapper/agent-orchestrator` as an external reference.
- Copied Claude-only skills into `C:\Users\manaz\.codex\skills`:
  - `task-observer`
  - `agency-agents`
  - `agent-skills`

## Remaining Decisions

- Do not install broad uncertain skill repositories without an explicit user request.
- Do not integrate `AgentWrapper/agent-orchestrator` until the user asks for clone/install/fork/integration work.
