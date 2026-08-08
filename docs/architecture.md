# vault-os Architecture

## What It Is

A Claude Code + Cursor plugin that turns any directory into a persistent, compounding Obsidian wiki vault. Descended from claude-obsidian; vault-os is now an independent product (no routine upstream merges).

## Plugin Structure

```
vault-os/
├── .claude-plugin/        Plugin manifests (vault-os branded)
│   ├── plugin.json        Plugin identity, version, author
│   └── marketplace.json   Marketplace distribution config
├── skills/                Agent skills (wiki, hot-sync, teams-*, …)
├── hooks/                 Claude (`hooks.json`) + Cursor (`cursor-hooks.json`)
├── agents/                Agent definitions
├── commands/              Slash commands
├── scripts/               Vault tooling (hot-sync, retrieve, locks, …)
├── bin/                   Setup scripts
├── rules/                 Cursor always-on rules
├── docs/                  Project documentation
└── CLAUDE.md              Agent dev instructions
```

## Ownership

The full tree is vault-os owned. Prefer additive `skills/<new-name>/` for new capabilities. Historical credit for the fork lineage lives in `ATTRIBUTION.md`. Do not plan work around upstream merge conflicts.

## Per-Vault Runtime (not committed)

When a user installs the plugin and runs `/wiki`, these are created in their project:

```
.raw/            Source documents (immutable, Claude reads only)
wiki/            Generated wiki pages
_templates/      Obsidian Templater templates
_attachments/    Images and PDFs
```

## How Ingest Works

1. User drops source into `.raw/`
2. `ingest [file]` triggers wiki-ingest skill
3. Skill classifies source → extracts entities/concepts
4. Calls `create-note.sh` / `update-note.sh` to write wiki pages
5. Updates `wiki/index.md` and `wiki/hot.md`

Token cost: ~$0.10-0.50 per source depending on size.
Use `sonnet` for bulk ingest, `opus` for complex synthesis.

## Fork Sync

Upstream improvements flow in via:
```bash
git fetch upstream
git merge upstream/main
```

Conflicts only hit the 4 branded files. Custom work in harness/ is never touched.
