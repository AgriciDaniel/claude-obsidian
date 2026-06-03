# claude-obsidian: Agent Instructions

This repository is an Obsidian vault scaffold and a Codex skill package for building persistent, compounding Markdown knowledge bases.

The public repo contains the reusable mechanism only: skills, commands, templates, setup scripts, tests, and seed examples. Do not add private vault contents, personal logs, client files, source imports, finance data, or generated user outputs to this repository.

## Supported Agent Surface

The polished public surface is Codex + Obsidian. Keep other agent integrations out of the public pitch unless they are deliberately reintroduced, documented, and tested.

## Skills Discovery

All skills live in `skills/<name>/SKILL.md`.

For Codex:

```bash
ln -s "$(pwd)/skills" ~/.codex/skills/claude-obsidian
```

## Available Skills

| Skill | Purpose |
|---|---|
| `wiki` | Bootstrap or continue a structured Obsidian wiki. |
| `wiki-ingest` | Convert sources into linked Markdown notes. |
| `wiki-query` | Answer questions from the local wiki with citations. |
| `wiki-lint` | Find orphans, dead links, stale pages, and missing structure. |
| `save` | File useful conversations as wiki notes. |

## Public Vault Conventions

- `wiki/`: generated public example knowledge pages and seed docs.
- `raw/`: source examples for a public seed vault, if present.
- `_templates/`: reusable Obsidian note templates.
- `.vault-meta/`: runtime state for public helper scripts.
- `docs/`: installation, architecture, privacy, and release documentation.

Private working vault folders are intentionally ignored by `.gitignore`.

## Bootstrap

When an agent starts in this repository:

1. Read this file.
2. Read `README.md` for the public project shape.
3. Read `skills/wiki/SKILL.md` when the user asks to set up or operate the wiki.
4. Read only task-relevant files. Do not scan private local-vault folders.

## Optional DragonScale

DragonScale is the optional advanced layer for large vaults. It adds:

- extractive log folds
- deterministic page addresses
- semantic tiling lint

Use `docs/dragonscale-guide.md` for shipped behavior. Keep it opt-in; the base public surface is wiki setup, ingest, query, lint, and save.

## Privacy Rule

Public docs should describe mechanisms with placeholders and fictional examples.

Never commit:

- private notes
- conversation logs
- source imports
- client work
- finance or health data
- daily records
- generated user outputs
- local workflow artifacts

Before staging, inspect:

```bash
git status --short
git diff --cached --name-only
```

Avoid broad `git add .` from a working vault.
