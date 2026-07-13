# task completion checklist

Before considering a coding task done in this repo:
1. If `src/claude_obsidian/*.py` logic changed, check whether the mirrored `scripts/*.py` copy (see
   `mem:tech_stack` on the dual-copy issue) also needs the same change — CI/Makefile run the `scripts/` copies.
2. Run the relevant `make test-*` target(s) (or `make test` for full suite) — see `mem:suggested_commands`
   for the target list and the uv-run substitution rule.
3. If you touched any `skills/*/SKILL.md` or `agents/*.md` frontmatter, mentally re-check it has the fields
   CI's lint-skills job requires (`name`+`description` for skills, `tools:` for agents) — no local lint target
   for this, only CI.
4. If you touched `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, or `hooks/hooks.json`,
   validate it parses as JSON.
5. Before `git commit` on a non-trivial change, dispatch the `verifier` agent (per project CLAUDE.md) —
   read-only pass over `git diff --cached`, returns BLOCKER/HIGH/MEDIUM/LOW findings.
6. No repo-wide type checker or formatter is configured (no ruff/mypy config found at root) — don't invent one.
