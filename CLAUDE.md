# vault-os Development

Fork of [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) by AgriciDaniel.
vault-os = upstream wiki skills + custom extensions, shipped as one plugin.

## Ownership Model

| Directory | Owner | Editable? |
|-----------|-------|-----------|
| `skills/` (existing upstream skills) | upstream (claude-obsidian) | **No** — merge conflicts |
| `agents/` (existing upstream agents) | upstream (claude-obsidian) | **No** — merge conflicts |
| `hooks/hooks.json`, `commands/` | upstream (claude-obsidian) | **No** — merge conflicts |
| `.claude-plugin/`, `README.md`, `ATTRIBUTION.md` | vault-os (branded) | Yes |
| `.cursor-plugin/` | vault-os (branded, Cursor manifest) | Yes |
| `rules/` (plugin-shipped Cursor rules) | vault-os (custom) | Yes |
| `hooks/cursor-hooks.json` | vault-os (custom, Cursor hook config) | Yes |
| `skills/<new-skill>/` (new dirs) | vault-os (custom) | Yes — this is where you build |
| `agents/<new-agent>.md` (new files) | vault-os (custom) | Yes |
| `docs/`, `bin/` | vault-os (custom) | Yes |

**Rule: new features go in new files/dirs. Never modify upstream files.**

## Dev Workflow

This repo **is** the plugin. Claude Code auto-discovers skills/agents/hooks from the project directory.

### Dev mode (building & testing)
1. Work inside this repo — local auto-discovery loads all skills
2. Disable marketplace plugin (`vault-os@vault-os-marketplace` in `~/.claude/settings.json`) to avoid duplicates
3. Create a new skill: `skills/<name>/SKILL.md` (see `docs/templates/SKILL-TEMPLATE.md`)
4. Create a new agent: `agents/<name>.md` (see `docs/templates/AGENT-TEMPLATE.md`)
5. Optionally add a slash command: `commands/<name>.md`
6. Test the skill live — invoke it, verify behavior, iterate

### Test as consumer
1. `cd` to a different project
2. Re-enable `vault-os@vault-os-marketplace` in `~/.claude/settings.json`
3. Verify skills load and work from the published GitHub source

### Publish
Push to `saixso/vault-os` on GitHub — the marketplace serves from this repo.

## Adding a New Skill

```
skills/<name>/
├── SKILL.md              # Required — skill definition
└── references/           # Optional — supporting docs the skill can read
    └── patterns.md
```

**SKILL.md frontmatter:**
```yaml
---
name: <skill-name>
description: >
  One-line pitch. Trigger phrases: "X", "Y", "/z".
allowed-tools: Read Write Edit Glob Grep Bash WebFetch
---
```

**SKILL.md body:** Role statement, workflow steps, output format, constraints.
See `docs/templates/SKILL-TEMPLATE.md` for a copyable starter.

## Adding a New Agent

Create `agents/<name>.md` with:
```yaml
---
name: <agent-name>
description: >
  What it does. When to dispatch.
model: sonnet
maxTurns: 30
tools: Read, Write, Edit, Glob, Grep
---
```

Body: role, inputs, process steps, output format.
See `docs/templates/AGENT-TEMPLATE.md` for a copyable starter.

## Adding a Slash Command

Create `commands/<name>.md`:
```yaml
---
description: One-line description of what /name does.
---

Read the `<skill-name>` skill. Then run the workflow.

Usage:
- `/<name>` — default behavior
- `/<name> [args]` — with arguments
```

## Fork Sync

```bash
git fetch upstream
git merge upstream/main
```

Conflicts only hit branded files (`.claude-plugin/`, `README.md`, `ATTRIBUTION.md`).
Custom skills in new dirs are never touched by upstream merges.

## Branch Convention

`feat/<name>` off `main` for new features. PR to `saixso/vault-os`.

## Release Checklist

1. Bump version in `.claude-plugin/plugin.json`
2. Test locally (dev mode) — invoke each new skill
3. Test as consumer (marketplace mode) from a different project
4. Push to `main`
5. Verify marketplace serves the update

## Docs

- `docs/architecture.md` — plugin structure and ownership model
- `docs/roadmap.md` — phases and milestones
- `docs/templates/` — copyable starters for skills and agents
- `CONTRIBUTING.md` — detailed dev guide
