# claude-obsidian vault

This directory is a **claude-obsidian wiki vault**. The automation toolchain is
installed at `~/.claude/obsidian-toolkit/` and registered globally with Claude Code.

**Vault path:** This directory — open in Obsidian directly.

## What's in this vault

- `wiki/` — wiki content (concepts, entities, sources, articles, meta)
- `.raw/` — source files for ingestion (articles, transcripts, images)
- `.vault-meta/` — runtime state (transport config, locks, mode, address counter)
- `.obsidian/` — Obsidian app configuration

## Available skills

- `/claude-obsidian:wiki-ingest` — ingest sources into the wiki
- `/claude-obsidian:wiki-lint` — health check for the wiki
- `/claude-obsidian:wiki-query` — query the wiki
- `/wiki` — wiki setup, scaffold, and orchestration
- `/autoresearch [topic]` — autonomous web research
- `/save` — log the current conversation as a structured note
- `/think [problem]` — structured thinking framework

## How the decoupled architecture works

The toolchain lives at `~/.claude/obsidian-toolkit/` and is independent of this
vault project. You can delete this vault project and re-create it elsewhere —
just set `CLAUDE_OBSIDIAN_VAULT` to point to the new vault root.

**Env vars** (set in `~/.claude/settings.json`):
- `CLAUDE_OBSIDIAN_TOOLKIT` — path to the installed toolchain
- `CLAUDE_OBSIDIAN_VAULT` — path to this vault's root

## First-time setup for a new vault

```bash
# Clone a vault or create directories
mkdir -p my-vault/wiki/concepts my-vault/wiki/entities
touch my-vault/.claude-obsidian-root

# Set the vault path in Claude Code settings
claude settings set env.CLAUDE_OBSIDIAN_VAULT /absolute/path/to/my-vault
```

## See also

- [Toolkit CLAUDE.md](~/.claude/obsidian-toolkit/CLAUDE.md) — full orchestrator instructions
- `wiki/index.md` — page index for this vault
