#!/usr/bin/env bash
# allocate-address.sh — thin wrapper delegating to allocate-address.py.
#
# The original flock-based implementation didn't run under Git Bash/MSYS2 on
# Windows (no flock binary). Locking logic moved to allocate-address.py,
# which uses msvcrt.locking on win32 and fcntl.flock elsewhere (same pattern
# as bm25-index.py). This wrapper is kept — same filename, same exec bit —
# because skills/docs feature-detect DragonScale via
# `[ -x ./scripts/allocate-address.sh ]`.
#
# Usage: see allocate-address.py --help / header docstring.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Not `exec`: on Windows/MSYS, redirecting a real (non-MSYS) child process's
# stdout with `>>` from several concurrent bash jobs races at the OS level
# (each native child gets its own append-mode handle, and Windows does not
# serialize those writes the way POSIX processes sharing an msys fd do) —
# so bash captures the child's output itself and re-emits it with a plain
# builtin `printf`, which uses the same append fd bash always has.
set +e
OUT="$(uv run --project "$SCRIPT_DIR/.." python "$SCRIPT_DIR/allocate-address.py" "$@")"
EC=$?
set -e
[ -n "$OUT" ] && printf '%s\n' "$OUT"
exit "$EC"
