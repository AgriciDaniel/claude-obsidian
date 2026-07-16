# conventions

- Skills live at `skills/<name>/SKILL.md` with required YAML frontmatter: `name` + `description` (enforced by CI
  lint-skills job) — every new skill must have both or CI fails.
- Agents live at `agents/<name>.md` with required frontmatter key `tools:` (enforced by CI) — e.g. `agents/verifier.md`
  is read-only (Read, Grep, Glob, Bash) by design, never give it Edit/Write.
- Plugin manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) and `hooks/hooks.json` must
  stay valid JSON (CI checks with `python3 -c "import json; json.load(...)"`).
- Feature versioning is documented inline in `CLAUDE.md`'s skill table (e.g. "(v1.7)", "(v1.8)") — new opt-in
  features get a version tag and a corresponding `bin/setup-*.sh` installer plus a `docs/*-guide.md`.
- `.vault-meta/` holds all generated/runtime state (transport.json, mode.json, locks, caches) — gitignored by
  default; `mode.json` needs `git add -f` if the user wants it committed.
- Wiki content conventions (page structure, frontmatter, wikilinks) are governed by the `obsidian-markdown` skill,
  not this memory — consult it before generating/editing wiki/*.md pages.
