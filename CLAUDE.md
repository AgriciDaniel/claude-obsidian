# vault-os Development

Independent product descended from [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) by AgriciDaniel.
vault-os is no longer tracking upstream. See [ATTRIBUTION.md](ATTRIBUTION.md).

## Ownership Model

The whole plugin tree is vault-os owned. Edit any path when the change serves this product.

| Directory | Notes |
|-----------|-------|
| `skills/`, `agents/`, `commands/`, `hooks/` | First-class product surface |
| `.claude-plugin/`, `.cursor-plugin/` | Marketplace manifests |
| `rules/`, `scripts/`, `bin/`, `docs/` | Custom tooling and docs |
| `wiki/`, `.raw/` | Dogfood vault (`.raw/` remains immutable at runtime) |

Prefer additive skills (`skills/<new-name>/`) when introducing a capability so history stays readable. There is no upstream merge gate anymore.

## Dev Workflow

This repo **is** the plugin. Claude Code and Cursor auto-discover skills/agents/hooks from the project directory.

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

## Upstream

vault-os does **not** routinely merge `upstream/main`. The `upstream` git remote may remain for archaeology or rare cherry-picks. Do not run `git merge upstream/main` as part of normal development.

## Branch Convention

`feat/<name>` off `main` for new features. PR to `saixso/vault-os`.

## Release Checklist

1. Bump version in `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`
2. Test locally (dev mode) — invoke each new skill
3. Test as consumer (marketplace mode) from a different project
4. Push to `main`
5. Verify marketplace serves the update

## Docs

- `docs/architecture.md` — plugin structure and ownership model
- `docs/roadmap.md` — phases and milestones
- `docs/templates/` — copyable starters for skills and agents
- `CONTRIBUTING.md` — detailed dev guide
