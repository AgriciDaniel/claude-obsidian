---
address: c-000011
type: concept
title: "Claude Code Extensibility"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - claude-code
  - extensibility
status: developing
related:
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[Dive into Claude Code]]"
  - "[[Subagent Delegation Architecture]]"
---

# Claude Code Extensibility

Four extension mechanisms at graduated context cost, injecting into three fixed points in the agent loop.

## Four Mechanisms (Graduated Context Cost)

| Mechanism | Context Cost | Key Capability |
|:----------|:-------------|:---------------|
| **Hooks** | Zero | 27 events, 4 execution types |
| **Skills** | Low | SKILL.md injected via SkillTool meta-tool |
| **Plugins** | Medium | 10 component types (commands, agents, skills, hooks, MCP, LSP, styles...) |
| **MCP Servers** | High | External tools via 7 transport types |

> [!key-insight] Not All Extensions Cost Tokens
> Hooks execute at zero context cost. A hook that logs, blocks, or runs a shell script consumes no model context at all. The cost ladder (zero → low → medium → high) is a design choice, not a constraint.

## Three Injection Points in the Agent Loop

- **assemble()** — what the model *sees*: CLAUDE.md instructions, skill descriptions, MCP resources, hook-injected context
- **model()** — what the model can *reach*: built-in tools, MCP tools, SkillTool, AgentTool
- **execute()** — whether/how actions *run*: permission rules, PreToolUse/PostToolUse hooks, Stop hooks

## Hook System (Zero Cost)

27 hook events across 5 categories. Four execution types:
1. Shell — arbitrary bash, zero context cost
2. LLM-evaluated — separate model call, independent context
3. Webhook — external HTTP endpoint
4. Subagent verifier — specialized read-only agent (e.g. pre-commit audit)

## Skill System (Low Cost)

SKILL.md with 15+ YAML frontmatter fields. Injected into current context via SkillTool (cheap, same window). Contrast with AgentTool which spawns an isolated window. See [[Subagent Delegation Architecture]].

## Tool Pool Assembly (5 Steps)

1. Base enumeration (up to 54 tools)
2. Mode filtering (active permission mode removes inapplicable tools)
3. Deny rule pre-filtering (strip denied tools from model's view entirely)
4. MCP integration (add server-provided tools)
5. Deduplication

## MCP Transport Types (7)

stdio, SSE, HTTP, WebSocket, SDK, IDE, and one additional. 42 tool subdirectories in the backend layer.

## Plugin Manifest

10 component types: commands, agents, skills, hooks, MCP servers, LSP servers, output styles, channels, settings, user config.

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228)
- [[Dive-into-Claude-Code-Architecture]]

## Related

- [[queryLoop Architecture]] — the loop these mechanisms extend at 3 injection points
- [[Agent Harness Engineering]] — extensibility is one of the 6 core harness design decisions
- [[Subagent Delegation Architecture]] — AgentTool is the most expensive extension path
