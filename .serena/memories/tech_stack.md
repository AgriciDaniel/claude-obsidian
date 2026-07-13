# tech stack

- Python >=3.9, no runtime dependencies (`pyproject.toml`: `dependencies = []`).
- Package manager: `uv` (project convention, not bare pip/python — see `mem:suggested_commands`).
- Build backend: hatchling. Package root `src/claude_obsidian/`, wheel target `src/claude_obsidian`.
- CLI entrypoints (`[project.scripts]`) map `co-*` commands to package modules:
  co-retrieve, co-bm25, co-rerank, co-contextual, co-boundary, co-tiling, co-mode, co-baseline, co-benchmark.
- IMPORTANT: two parallel copies of the same logic can exist — `src/claude_obsidian/*.py` (installable package)
  and `scripts/*.py` / `scripts/*.sh` (legacy direct-invoke, still what skills/CI actually shell out to via
  `python3 scripts/foo.py`). When editing behavior, check both locations aren't drifting; CI (`test.yml`) and
  the Makefile invoke the `scripts/` copies directly, not the installed package.
- Test runner: no pytest — hermetic hand-rolled `tests/test_*.py` (run as scripts, not via pytest) + `tests/test_*.sh` (bash).
- CI: GitHub Actions `.github/workflows/test.yml`, two jobs — `test` (make test + wiki-mode/transport CLI smoke checks)
  and `lint-skills` (validates every `SKILL.md` frontmatter, every `agents/*.md` has `tools:`, plugin/marketplace/hooks JSON valid).
