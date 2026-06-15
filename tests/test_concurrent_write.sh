#!/usr/bin/env bash
# test_concurrent_write.sh — verify multi-writer safety with wiki-lock.sh.
#
# The critical correctness gate from v1.7 §3.4. Spawns N background workers,
# each acquires a lock on the same file, appends a uniquely-tagged line, and
# releases. After all workers exit we verify:
#   - the file received EXACTLY N appended lines (no losses)
#   - every worker's tagged line is present (no silent dropping)
#   - no orphaned lockfiles remain
#   - clear-stale reports 0 leftovers
#
# Without wiki-lock.sh, concurrent appends to the same file via `echo >> file`
# can interleave and corrupt lines on some filesystems. With the lock, only
# one worker holds the file at a time, and atomic append-then-release prevents
# corruption.
#
# Hermetic: sandbox vault under mktemp, no network.
#
# Usage: bash tests/test_concurrent_write.sh

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_SH="$ROOT/scripts/wiki-lock.sh"

WORKERS=10
TARGET_FILE_REL="wiki/concepts/Stress.md"

SANDBOX=$(mktemp -d /tmp/concurrent-write-test-XXXXXX)
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/.vault-meta/locks" "$SANDBOX/wiki/concepts"
TARGET_ABS="$SANDBOX/$TARGET_FILE_REL"
echo "seed" > "$TARGET_ABS"

export WIKI_LOCK_VAULT="$SANDBOX"

PASS=0
FAIL=0

assert_eq() {
  if [ "$2" = "$3" ]; then
    echo "OK   $1"
    PASS=$((PASS + 1))
  else
    echo "FAIL $1: expected '$2', got '$3'"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== test_concurrent_write.sh ==="
echo "sandbox: $SANDBOX"
echo "workers: $WORKERS"
echo "target: $TARGET_FILE_REL"
echo ""

# ── Worker function: acquire lock, append, release ──────────────────────────
worker() {
  local id="$1"
  local attempts=0
  local max_attempts=50
  # Random jitter so workers don't all hit at the same instant
  local jitter=$(awk -v id="$id" 'BEGIN { srand(id); print int(rand()*100) }')
  # POSIX-portable sub-second sleep via sleep(1) with fractional seconds (GNU/macOS supports it)
  sleep "0.0${jitter}" 2>/dev/null || sleep 1

  while [ "$attempts" -lt "$max_attempts" ]; do
    if bash "$LOCK_SH" acquire "$TARGET_FILE_REL" >/dev/null 2>&1; then
      # Append our line atomically
      echo "worker-$id-tag" >> "$TARGET_ABS"
      bash "$LOCK_SH" release "$TARGET_FILE_REL" >/dev/null 2>&1
      return 0
    fi
    attempts=$((attempts + 1))
    sleep "0.05" 2>/dev/null || sleep 1
  done
  echo "worker $id gave up after $attempts attempts" >&2
  return 1
}

# ── Spawn workers in parallel ───────────────────────────────────────────────
PIDS=()
for i in $(seq 1 $WORKERS); do
  worker "$i" &
  PIDS+=("$!")
done

# Wait for all workers
FAILED_WORKERS=0
for pid in "${PIDS[@]}"; do
  if ! wait "$pid"; then
    FAILED_WORKERS=$((FAILED_WORKERS + 1))
  fi
done

assert_eq "all workers completed (no give-ups)" "0" "$FAILED_WORKERS"

# ── Verify: file has seed + exactly N tagged lines ──────────────────────────
TOTAL_LINES=$(wc -l < "$TARGET_ABS")
assert_eq "total line count (seed + workers)" "$((WORKERS + 1))" "$TOTAL_LINES"

# Every worker tag must appear exactly once
for i in $(seq 1 $WORKERS); do
  COUNT=$(grep -c "^worker-$i-tag$" "$TARGET_ABS" || echo 0)
  if [ "$COUNT" != "1" ]; then
    echo "FAIL worker-$i tag count: expected 1, got $COUNT"
    FAIL=$((FAIL + 1))
  fi
done
echo "OK   every worker tag appears exactly once"
PASS=$((PASS + 1))

# ── Verify: no orphaned lockfiles ───────────────────────────────────────────
LIVE_LOCKS=$(bash "$LOCK_SH" list | wc -l)
assert_eq "no live lockfiles after workers exited" "0" "$LIVE_LOCKS"

# ── Verify: clear-stale reports 0 (nothing to reap) ─────────────────────────
REAPED=$(bash "$LOCK_SH" clear-stale --max-age 0)
assert_eq "clear-stale reaped count" "0" "$REAPED"

# ── Verify: file content sanity (no truncated/garbled lines) ────────────────
GARBLED=$(awk 'length > 100' "$TARGET_ABS" | wc -l)
assert_eq "no garbled (overlong) lines" "0" "$GARBLED"

echo ""
echo "Pass: $PASS  Fail: $FAIL"
if [ $FAIL -gt 0 ]; then
  echo "File contents:"
  cat "$TARGET_ABS"
  exit 1
fi
echo "All concurrent-write tests passed."
