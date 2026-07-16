#!/usr/bin/env bash
# wiki-lock.sh — thin wrapper delegating to wiki-lock.py.
#
# The original implementation used `flock` for its meta-lock, which is absent
# from Git Bash/MSYS2 on Windows — so every invocation died and skills fell
# back to unguarded writes. Locking logic moved to wiki-lock.py, which uses
# msvcrt.locking on win32 and fcntl.flock elsewhere (same pattern as
# allocate-address.py). This wrapper is kept — same filename, same exec bit —
# because skills and the PostToolUse hook invoke `bash scripts/wiki-lock.sh`.
#
# Runtime resolution: wiki-lock.py is stdlib-only, so no project env is
# needed. Prefer `uv run --no-project` (no sync, no network); fall back to
# plain python3 where uv is absent (stock Linux). If neither exists, fail
# with exit 1 and a clear message rather than a raw 127 — callers key on the
# documented exit codes (0/1/2/3/4/75) and would misread 127 as "held".
#
# Usage / semantics / exit codes: see wiki-lock.py header docstring
# (acquire|release|list|clear-stale|peek; 75 = held, 4 = bad path).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v uv >/dev/null 2>&1; then
  RUN=(uv run --no-project python "$SCRIPT_DIR/wiki-lock.py")
elif command -v python3 >/dev/null 2>&1; then
  RUN=(python3 "$SCRIPT_DIR/wiki-lock.py")
else
  echo "ERR: wiki-lock needs uv or python3 on PATH; found neither" >&2
  exit 1
fi

# Not `exec`: on Windows/MSYS, redirecting a real (non-MSYS) child process's
# stdout with `>>` from several concurrent bash jobs races at the OS level —
# bash captures the child's output itself and re-emits it with a builtin
# `printf` (same reasoning as allocate-address.sh).
set +e
OUT="$("${RUN[@]}" "$@")"
EC=$?
set -e
[ -n "$OUT" ] && printf '%s\n' "$OUT"
exit "$EC"
