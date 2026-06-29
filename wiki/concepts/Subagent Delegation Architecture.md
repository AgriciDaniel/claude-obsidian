---
address: c-000012
type: concept
title: "Subagent Delegation Architecture"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - claude-code
  - multi-agent
status: developing
related:
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[Claude Code Extensibility]]"
  - "[[Deny-First Permission Model]]"
  - "[[Dive into Claude Code]]"
---

# Subagent Delegation Architecture

Claude Code's multi-agent design: 6 built-in agent types, custom agents via `.claude/agents/*.md`, sidechain transcript isolation, and three isolation modes. The key tradeoff is SkillTool (cheap, same context) vs AgentTool (expensive, isolated context).

## SkillTool vs AgentTool

| | SkillTool | AgentTool |
|:--|:---------|:----------|
| Context | Injects into current window | Spawns isolated new window |
| Cost | Low | ~7x tokens vs current context |
| Use when | Instructions are compact, context safe | Task is large or context-polluting |
| Isolation | None | Full (own conversation, own tools) |

> [!key-insight] Agent Teams Cost ~7x
> Running a multi-agent plan in `plan` mode costs approximately 7x the tokens of a direct task. The sidechain architecture (summaries only return to parent) limits this — without it, subagent verbosity would blow up the parent context.

## 6 Built-in Agent Types

1. **Explore** — fast read-only code search and location
2. **Plan** — software architect; designs implementation plans
3. **General-purpose** — complex multi-step tasks, open-ended research
4. **Claude Code Guide** — questions about Claude Code itself (CLI, API, SDK)
5. **Verification** — pre-commit audit; read-only, advisory output only
6. **Statusline-setup** — configure status line setting

## Custom Agents

`.claude/agents/*.md` with YAML frontmatter supporting: `tools`, `disallowedTools`, `model`, `effort`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, memory scope, background flag, isolation mode.

## Three Isolation Modes

| Mode | Mechanism | Default |
|:-----|:----------|:--------|
| In-process | Shared filesystem, isolated conversation | Yes |
| Worktree | Git worktree (full filesystem isolation) | No |
| Remote | Remote execution (internal-only) | No |

## Sidechain Transcripts

Each subagent writes its own `.jsonl` file. Only a summary message returns to the parent context. Full history never enters the parent window.

Multi-instance coordination: POSIX `flock()`. Zero external dependencies — no message queue, no broker, no database.

## Permission Inheritance

Subagent `permissionMode` applies UNLESS the parent is in `bypassPermissions`, `acceptEdits`, or `auto` mode — explicit user decisions always take precedence over subagent defaults. See [[Deny-First Permission Model]].

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228)
- [[Dive-into-Claude-Code-Architecture]]

## Related

- [[Claude Code Extensibility]] — AgentTool is the high-cost extension path; SkillTool is low-cost
- [[queryLoop Architecture]] — each subagent runs its own queryLoop instance
- [[Deny-First Permission Model]] — permission inheritance rules
- [[Agent Harness Engineering]] — subagent architecture is one of the 6 core design decisions
