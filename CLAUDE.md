# Personal Second Brain: LLM Wiki

Mode: D (Personal Second Brain)
Purpose: Persistent, compounding personal knowledge base for goals, learning, relationships, and life areas.
Owner: sosik27@gmail.com
Created: 2026-05-01

## Structure

```
.raw/           source documents — immutable
wiki/
├── goals/      personal and professional goals
├── learning/   concepts, skills, courses
├── people/     relationships, follow-ups
├── areas/      life areas: health, career, finance, creative
├── resources/  books, courses, tools, articles
├── concepts/   ideas, patterns, frameworks
├── sources/    raw source summaries
├── questions/  filed answers
├── comparisons/ side-by-side analyses
└── meta/       dashboards, lint reports
_templates/     Obsidian Templater templates
```

## Conventions

- All notes use YAML frontmatter: type, status, created, updated, tags (minimum)
- Wikilinks use [[Note Name]] format: filenames are unique, no paths needed
- .raw/ contains source documents: never modify them
- wiki/index.md is the master catalog: update on every ingest
- wiki/log.md is append-only: never edit past entries
- New log entries go at the TOP of the file

## Operations

- Ingest: drop source in .raw/, say "ingest [filename]"
- Query: ask any question: Claude reads index first, then drills in
- Lint: say "lint the wiki" to run a health check
- Archive: move cold sources to .archive/ to keep .raw/ clean

## Plugin Skills

| Skill | Trigger |
|-------|---------|
| `/wiki` | Setup, scaffold, route to sub-skills |
| `ingest [source]` | Single or batch source ingestion |
| `query: [question]` | Answer from wiki content |
| `lint the wiki` | Health check |
| `/save` | File current conversation as structured wiki note |
| `/autoresearch [topic]` | Autonomous research loop |
| `/canvas` | Visual layer: add images to Obsidian canvas |

## Cross-Project Access

To reference this wiki from another Claude Code project, add to that project's CLAUDE.md:

```markdown
## Wiki Knowledge Base
Path: C:\Projekty C\claude-obsidian

When you need context not already in this project:
1. Read wiki/hot.md first (recent context, ~500 words)
2. If not enough, read wiki/index.md (full catalog)
3. If you need domain specifics, read wiki/<domain>/_index.md
4. Only then read individual wiki pages
```
