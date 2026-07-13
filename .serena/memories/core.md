# claude-obsidian — core

Dual-nature repo: Claude Code **plugin** (`.claude-plugin/`) + Obsidian **vault** (this dir opens directly in Obsidian).
Plugin ships skills (`skills/*/SKILL.md`), agents (`agents/*.md`), hooks (`hooks/hooks.json`), and a small
Python package (`src/claude_obsidian/`) exposed as `co-*` CLI entrypoints (see `mem:tech_stack`).

## Top-level map
- `skills/` — Claude Code skills (wiki, wiki-ingest, wiki-query, wiki-lint, wiki-cli, wiki-retrieve, wiki-mode, save, canvas, autoresearch, think, defuddle, obsidian-bases, obsidian-markdown, wiki-fold)
- `src/claude_obsidian/` — installable package backing `co-*` scripts; also mirrored/invoked as `scripts/*.py` (legacy direct-invoke path — see `mem:tech_stack`)
- `scripts/` — shell + python utilities invoked directly by skills (not all migrated into the package)
- `bin/` — setup scripts (`setup-dragonscale.sh`, `setup-retrieve.sh`, `setup-mode.sh`) — opt-in feature installers
- `tests/` — hermetic python + bash tests, run via `Makefile` targets, mirrored in CI (`mem:task_completion`)
- `wiki/` — the actual Obsidian knowledge base content (generated/curated, not source code)
- `.raw/` — immutable source docs; Claude reads, never modifies
- `agents/` — includes `verifier.md`, a read-only pre-commit review agent (Read/Grep/Glob/Bash only)
- `.vault-meta/` — gitignored runtime state (locks, caches, transport/mode detection) — see `mem:conventions`
- Docs entry points: `docs/compound-vault-guide.md` (v1.7 architecture), `docs/methodology-modes-guide.md` (v1.8)

## Project-wide invariants
- Version currently 1.9.2 (`pyproject.toml`). Track `CHANGELOG.md` for what changed between minor versions.
- Skills consult `.vault-meta/*.json` state files (transport, mode) before mutating the vault — never hardcode a transport/mode assumption.
- Multi-writer safety: any wiki page write should be guarded by `scripts/wiki-lock.sh` acquire/release (per-file advisory locks).

See also: `mem:tech_stack`, `mem:suggested_commands`, `mem:conventions`, `mem:task_completion`.
