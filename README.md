
# vault-os

A schema-agnostic context bus for AI agents. Load the right knowledge, from the right sources, in the right order — so every token in the context window earns its keep.

**Fork of [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) by [AgriciDaniel](https://github.com/AgriciDaniel).** Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-8B5CF6)](https://code.claude.com/docs/en/discover-plugins)
[![Cursor](https://img.shields.io/badge/Cursor-plugin-1e1e1e)](https://cursor.com/docs/plugins)
[![Upstream](https://img.shields.io/badge/upstream-claude--obsidian-orange)](https://github.com/AgriciDaniel/claude-obsidian)
[![Blog Post](https://img.shields.io/badge/Deep_Dive-Blog_Post-22c55e)](https://agricidaniel.com/blog/claude-obsidian-ai-second-brain)

A running notetaker that builds and maintains a persistent, compounding wiki vault. Every source you add gets integrated. Every question you ask pulls from everything that has been read. Knowledge compounds like interest.

**11 skills. Zero manual filing. Multi-agent support. Optional [DragonScale Memory](docs/dragonscale-guide.md) extension** (log folds, deterministic page addresses, semantic tiling lint, boundary-first autoresearch).

---

## The Problem

AI agents start blank. Every session, you re-explain the same context: why you're building this way, what constraints matter, what the business needs. The agent writes correct code but not the *right* code — because it's missing the human layer.

Docs tell agents *how*. Repo configs tell agents *where*. Nothing tells them *why*.

## The Vision

vault-os composes agent context windows from three non-overlapping tiers:

| Tier | Answers | Source |
|------|---------|--------|
| **Local harness** | *Where* — repo-specific facts, file paths, conventions | CLAUDE.md, `.vault-os.yml` |
| **Structured knowledge API** | *How* — domain reference, docs, runbooks | Any MCP server or docs API |
| **Vault** | *Why* — business context, axioms, intent, priorities | Obsidian vault |

With all three tiers composed, multi-turn disambiguation loops collapse into single turns.

### Schema-agnostic

The plugin has zero opinions on how you organize your vault. You define the schema — DDD bounded contexts, flat files, topic clusters, whatever fits your mental model. The plugin loads what you point it at, respects the order and budget, and gets out of the way.

```yaml
# .vault-os.yml — you define the structure
vault: ~/my-vault
context:
  - path: axioms.md
  - path: domains/backend/context.md
  - api: my-docs-server
budget:
  per_source: 2000
  total: 10000
```

### Swappable middle tier

Same architecture, different domains. Swap the structured API and the pattern serves any use case:

| Use case | Structured API | Vault context |
|----------|---------------|---------------|
| Infrastructure | infra docs MCP | business priorities, team ownership |
| ML project | model/dataset docs | why this model, constraints |
| Incident response | monitoring dashboards | who's on call, blast radius |

The vault is the constant. The API tier is swappable. The local harness is throwaway.

### Compounding, not accumulating

Most knowledge systems accumulate notes and RAG from scratch every time. vault-os compounds — each new source builds on existing wiki pages. Context-aware read-before-write.

---

## What It Does Today

A Claude Code **and Cursor** plugin that manages a persistent, compounding wiki vault in Obsidian.

| Command | What it does |
|---------|------------|
| `/wiki` | Setup, scaffold, or continue where you left off |
| `ingest [file]` | Read source, create wiki pages, update index |
| `what do you know about X?` | Query wiki, synthesize answer |
| `/save` | File current conversation as a wiki note |
| `/autoresearch [topic]` | Autonomous research loop: search, fetch, synthesize |
| `lint the wiki` | Health check: orphans, dead links, gaps |

10 skills included. See [upstream docs](https://github.com/AgriciDaniel/claude-obsidian) for full documentation.

---

## Roadmap

1. **Wiki Engine** (done) — Ingest, query, lint, index. Compounding knowledge base.
2. **Plugin + Skills** (current) — Claude Code plugin. 10 skills for vault operations.
3. **Context Bus** — Three-tier architecture. `.vault-os.yml` declaration. Schema-agnostic loading with token budgets.
4. **Public Release** — End-to-end install. Community templates. Drop vault-os on any vault.

---

## Quick Start

### Claude Code

```bash
claude plugin marketplace add saixso/vault-os
claude plugin install vault-os@vault-os-marketplace
```

### Cursor

Once approved on the official marketplace:

```
Open Cursor → Marketplace → search "vault-os" → Install
```

Until then, self-hosted install from this repo:

```
Settings → Plugins → Add marketplace → saixso/vault-os
```

### Other agents (Codex CLI, OpenCode, Gemini CLI, Windsurf)

```bash
git clone https://github.com/saixso/vault-os.git
cd vault-os
bash bin/setup-multi-agent.sh
```

In any session: `/wiki`.

---

## Attribution

Fork of [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) by [AgriciDaniel](https://github.com/AgriciDaniel), licensed under MIT. See [ATTRIBUTION.md](ATTRIBUTION.md).

*Built by [saixso](https://github.com/saixso).*
