# vault-os: Agent Instructions

This repo is a Claude Code + Cursor plugin **and** an Obsidian vault that builds persistent, compounding knowledge bases using Andrej Karpathy's LLM Wiki pattern. It works with **any AI coding agent** that supports the Agent Skills standard, including Codex CLI, OpenCode, Cursor, and similar.

Originally built for Claude Code, the skills follow the cross-platform Agent Skills spec. Newer skills (`wiki-fold`, `wiki-ingest`, `wiki-lint`) use only `name` and `description` frontmatter (kepano convention). Some older skills still carry an optional `allowed-tools` field for Claude Code compatibility; cross-platform agents that do not recognize it should ignore it.

## Skills Discovery

All skills live in `skills/<name>/SKILL.md`. Discovery depends on the agent:

- **Claude Code**: auto-discovered via `.claude-plugin/plugin.json` (install from the `vault-os-marketplace`).
- **Cursor**: auto-discovered via `.cursor-plugin/plugin.json` once the plugin is installed from the marketplace (`saixso/vault-os`) or as a self-hosted marketplace. No symlink needed.
- **Codex CLI / OpenCode / Gemini CLI / Windsurf**: still need a symlink. Run:

```bash
bash bin/setup-multi-agent.sh
```

Or manually:

```bash
# Codex CLI
ln -s "$(pwd)/skills" ~/.codex/skills/vault-os

# OpenCode
ln -s "$(pwd)/skills" ~/.opencode/skills/vault-os
```

## Available Skills

| Skill | Trigger phrases |
|---|---|
| `wiki` | `/wiki`, set up wiki, scaffold vault |
| `wiki-ingest` | ingest, ingest this url, ingest this image, batch ingest |
| `wiki-query` | query, what do you know about, query quick:, query deep: |
| `wiki-lint` | lint the wiki, health check, find orphans |
| `wiki-fold` | fold the log, run a fold, log rollup (DragonScale Mechanism 1, opt-in) |
| `hot-sync` | /hot-sync, /hot, refresh hot cache, regenerate hot.md |
| `save` | /save, file this conversation |
| `autoresearch` | autoresearch, autonomous research loop |
| `canvas` | /canvas, add to canvas, create canvas |
| `defuddle` | clean this url, defuddle |
| `obsidian-markdown` | obsidian syntax, wikilink, callout |
| `obsidian-bases` | obsidian bases, .base file, dynamic table |

## Key Conventions

- **Vault root**: the directory containing `wiki/` and `.raw/`
- **Hot cache**: `wiki/hot.md` (read at session start; Ground Truth owned by `scripts/hot-sync.sh`)
- **Source documents**: `.raw/` (immutable: agents never modify these)
- **Generated knowledge**: `wiki/` (agent-owned, links to sources via wikilinks)
- **Manifest**: `.raw/.manifest.json` tracks ingested sources (delta tracking)
- **Lineage**: descended from claude-obsidian; vault-os is the product of record and does not track upstream merges

## Bootstrap

When the user opens this project for the first time:

1. Read this file (`AGENTS.md`) and the project `CLAUDE.md` for full context
2. Read `skills/wiki/SKILL.md` for the orchestration pattern
3. If `wiki/hot.md` exists, read it silently to restore recent context (SessionStart may have already run `scripts/hot-sync.sh`)
4. If the user types `/wiki` (or "set up wiki"), follow the wiki skill's scaffold workflow

## Reference

- Plugin source: https://github.com/saixso/vault-os
- Historical upstream: https://github.com/AgriciDaniel/claude-obsidian
- Pattern source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Cross-reference: https://github.com/kepano/obsidian-skills (authoritative Obsidian-specific skills)
