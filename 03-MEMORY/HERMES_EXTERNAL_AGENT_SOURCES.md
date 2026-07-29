# Hermes External Agent Sources

Date: 2026-07-01

## Summary

Hermes now has local external agent/source repos installed at:

`C:\Users\manaz\.hermes\external-sources`

MAZos records the same sources as Git submodules under:

`C:\Users\manaz\Projects\mazos-ui\external\agent-sources`

MAZos registry:

`C:\Users\manaz\Projects\mazos-ui\research\mazos\HERMES_EXTERNAL_SOURCES.md`

Hermes registry:

`C:\Users\manaz\.hermes\mazos\EXTERNAL_SOURCES.md`

## Installed

- Headroom: context compression, token reduction, reversible retrieval, cross-agent memory, MCP/proxy compression.
- Agent Reach: web reach for agents: webpages, YouTube, RSS, GitHub, and explicit user-configured social access.
- NVIDIA Skills: verified NVIDIA agent skills for CUDA, Jetson, NeMo, cuOpt, GPU/RAG/AI blueprint workflows.
- Claude Skills: large reusable skill/command/agent-role library.
- Claude Skills `CLAUDE.md`: copied to `C:\Users\manaz\.hermes\external-sources\CLAUDE.alirezarezvani-claude-skills.md`.
- Maxun: browser automation and web extraction architecture.
- Loop Engineering: recurring agent loops, PR/CI loops, cost checks, stop conditions, loop audits.
- Awesome n8n Templates: n8n workflow templates, webhook/integration automation examples, no-code automation patterns, and workflow blueprint inspiration.

Note: the MAZos `awesome-n8n-templates` submodule is sparse because the full repo contains Windows long-path template filenames. Hermes should use the full local clone at `C:\Users\manaz\.hermes\external-sources\awesome-n8n-templates`.

## Unresolved

`https://github.com/alirezarezvani/claude` was not accessible from GitHub. The public related repo `https://github.com/alirezarezvani/claude-skills` was installed instead, along with the linked `CLAUDE.md`.

## Hermes Rule

When using these sources, Hermes should not load all repos by default. It should route narrowly:

- Headroom for heavy context/log/token work.
- Agent Reach for web research/reach.
- NVIDIA Skills for NVIDIA/GPU platform work.
- Claude Skills for agent workflow design.
- Maxun for browser automation architecture.
- Loop Engineering for recurring automations and multi-step loops.
- Awesome n8n Templates for n8n workflows, webhook/integration automations, no-code automations, and reusable workflow blueprints.

Agent Reach and Maxun must not be used to bypass authentication, scrape private content, or violate platform terms.

Every recurring loop must have a goal, stop condition, budget, run log, and human gate.

n8n templates must be adapted manually with credential review and must not be blindly activated after import.
