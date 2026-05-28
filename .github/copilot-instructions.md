# claude-obsidian: GitHub Copilot Instructions

This repository is a **Claude Code plugin and Obsidian vault** that builds persistent, compounding knowledge bases using Andrej Karpathy's LLM Wiki pattern. It is markdown-only. No build step, no compiled code, no runtime dependencies.

## Project Type

- Agent Skills package (cross-platform Agent Skills standard)
- Obsidian vault (interpretable by Obsidian directly)
- Claude Code plugin (installable via marketplace)

## Repository Layout

- `skills/`: 10 skills, each with a `SKILL.md` defining trigger phrases and instructions
- `hooks/hooks.json`: Claude Code lifecycle hooks (SessionStart, PostCompact, PostToolUse, Stop)
- `.claude-plugin/plugin.json`: plugin manifest
- `wiki/`: generated knowledge base (Markdown files with YAML frontmatter)
- `.raw/`: immutable source documents (never modify)
- `_templates/`: Obsidian Templater templates
- `_attachments/`: images and PDFs referenced by wiki pages

## Conventions Copilot Should Follow

When suggesting edits:

1. **Frontmatter is flat YAML** with plural keys: `tags`, `aliases`, `cssclasses`
2. **Internal links are wikilinks**: `[[Note Name]]`, not Markdown links to `.md` paths
3. **Dates are `YYYY-MM-DD`**, not ISO datetimes
4. **`.raw/` is immutable**. Never suggest edits to anything under that path
5. **`wiki/log.md` is append-only**, with new entries at the top
6. **`wiki/hot.md` is overwritten** at session end, not appended to
7. **Skills use only `name` and `description` in frontmatter**. No `allowed-tools`, no `triggers`, no `globs` (these are not part of the Agent Skills spec)
8. **Custom callouts**: this vault defines `[!contradiction]`, `[!gap]`, `[!key-insight]`, `[!stale]` in `.obsidian/snippets/vault-colors.css`. These render only with that snippet enabled.

## When Editing Skills (`skills/<name>/SKILL.md`)

- Frontmatter: `name` (matches directory name) and `description` (single quoted line, max ~250 useful chars)
- Body: short, imperative instructions. Reference files with backticks. Do not paste large code blocks unless they're essential.
- Trigger phrases go in the `description` field, not in body or non-standard fields

## When Editing Hooks (`hooks/hooks.json`)

- Valid event names only: `SessionStart`, `Stop`, `PreToolUse`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`
- Hook types: `command` (shell), `prompt` (LLM), `http` (POST), `agent` (subagent)
- `matcher` field uses regex against tool names for `PreToolUse`/`PostToolUse`
- For `SessionStart`: matcher uses `startup`, `resume`, `clear`, or `compact`

## Cross-Reference

- Plugin: https://github.com/AgriciDaniel/claude-obsidian
- Pattern source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Authoritative Obsidian-specific skills: https://github.com/kepano/obsidian-skills
