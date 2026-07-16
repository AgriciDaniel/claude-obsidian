# suggested commands

Dev shell is Windows/PowerShell for the user, but this repo's own tests/scripts are bash + python3,
run hermetically (CI is ubuntu-latest). When running repo tests/scripts locally on Windows, use Git Bash
(the `Bash` tool) not PowerShell — Makefile and scripts/*.sh assume POSIX sh.

Per user's global CLAUDE.md: always invoke python via `uv run <script>.py`, never bare `python`/`python3`
(not installed / not to be installed) — this overrides the repo's own `python3 scripts/foo.py` examples
found in Makefile/CI; translate `python3 X` -> `uv run X` when running commands yourself.

## Test targets (Makefile — see `mem:task_completion` for the full gate)
- `make test` — all v1.7 tests (address, tiling, boundary, bm25, retrieve, lock, concurrent, mode, contextual)
- Individual targets: `make test-address|test-tiling|test-boundary|test-bm25|test-retrieve|test-lock|test-concurrent|test-mode|test-contextual`
- `make clean-test-state` — wipe `.vault-meta/` runtime locks/caches (locks, tiling/embed cache, transport/mode json, hook.log)

## Opt-in feature setup
- `bash bin/setup-dragonscale.sh`
- `bash bin/setup-retrieve.sh` (v1.7 hybrid retrieval)
- `bash bin/setup-mode.sh` (v1.8 methodology mode picker)

## Ad hoc CLI smoke checks (from CI, useful for manual verification)
- `python3 scripts/wiki-mode.py get|config|id|templates`
- `bash scripts/detect-transport.sh --peek`
