# claude-obsidian: Windsurf Rules

This repo is a knowledge companion that builds persistent, compounding Obsidian wiki vaults using Andrej Karpathy's LLM Wiki pattern. The skills are written in the cross-platform Agent Skills format and work in Cascade alongside Claude Code.

## Project Type

- **Hybrid**: Claude Code plugin + Obsidian vault
- **Pattern**: LLM Wiki (Karpathy)
- **Stack**: Markdown only: no build step, no runtime dependencies

## What's In This Repo

```
claude-obsidian/
├── skills/              ← 10 SKILL.md files (Agent Skills format)
├── hooks/               ← SessionStart, PostCompact, PostToolUse, Stop
├── .claude-plugin/      ← Claude Code plugin manifest
├── _templates/          ← Obsidian Templater templates
├── wiki/                ← Generated knowledge base
│   ├── hot.md           ← recent context cache (~500 tokens)
│   ├── index.md         ← master catalog
│   ├── log.md           ← append-only operation log
│   ├── concepts/, entities/, sources/, comparisons/, questions/
│   └── meta/dashboard.base ← Obsidian Bases dashboard
└── .raw/                ← Immutable source documents
```

## Skills Available to Cascade

Run `bash bin/setup-multi-agent.sh` once to symlink `skills/` into `.windsurf/skills/`. Then Cascade auto-discovers all 10 skills:

- `wiki`: orchestration, vault scaffolding, hot cache
- `wiki-ingest`: files, URLs, images → 8-15 wiki pages
- `wiki-query`: Quick / Standard / Deep query modes
- `wiki-lint`: health check (orphans, dead links, gaps)
- `save`: file conversation as wiki note
- `autoresearch`: autonomous research loop
- `canvas`: Obsidian canvas (.canvas) files
- `defuddle`: clean web pages before ingest
- `obsidian-markdown`: full Obsidian syntax reference
- `obsidian-bases`: Obsidian Bases (.base) database views

## Critical Rules

- **Never modify `.raw/`**: those are source documents
- **Read `wiki/hot.md` silently at session start** to restore context
- **Use wikilinks** `[[Note Name]]` for all internal references
- **Frontmatter is flat YAML** with plural keys (`tags`, `aliases`)
- **Auto-commit hook** fires on every Write/Edit to `wiki/` and `.raw/`
- **Append to `wiki/log.md`** at the top, never edit past entries

## Bootstrap

When the user opens this project in Windsurf:

1. Read this rules file
2. If `wiki/hot.md` exists, silently read it
3. Wait for triggers like "set up wiki", "ingest", or "query"

## Links

- https://github.com/AgriciDaniel/claude-obsidian
- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://github.com/kepano/obsidian-skills
