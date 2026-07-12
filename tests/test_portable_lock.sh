#!/usr/bin/env bash
# test_portable_lock.sh — correctness tests for scripts/lib/portable-lock.sh.
#
# These assert BEHAVIOR (mutual exclusion, timeout, release-on-exit), not
# implementation details, so they hold on both the flock(1) and python3 backends.
#
# The mutual-exclusion test is the important one and is deliberately brutal. An
# earlier hand-rolled mkdir+reap lock passed casual inspection, passed a review,
# and still let two workers into the critical section — it was caught only by
# hammering it. Do not weaken this test.
#
# Usage: bash tests/test_portable_lock.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(dirname "$SCRIPT_DIR")"
LIB="$VAULT_ROOT/scripts/lib/portable-lock.sh"

PASS=0
FAIL=0
pass() { echo "OK   $1"; PASS=$((PASS+1)); }
fail() { echo "FAIL $1"; FAIL=$((FAIL+1)); }

TMP=$(mktemp -d -t plock-XXXXXX)
trap 'rm -rf "$TMP"' EXIT

# shellcheck source=../scripts/lib/portable-lock.sh
. "$LIB"

# Determine the backend by ACQUIRING a lock and asking the library what it used —
# not by probing for flock ourselves. Those can differ (PORTABLE_LOCK_FORCE_BACKEND),
# and a test that guesses would let CI's forced-python3 run silently exercise flock.
( portable_lock_acquire "$TMP/probe.lock" 5 >/dev/null 2>&1
  echo "${PORTABLE_LOCK_LAST_BACKEND:-unknown}" > "$TMP/backend" ) 2>/dev/null
BACKEND="$(cat "$TMP/backend" 2>/dev/null || echo unknown)"

# If a backend was demanded, prove we actually got it.
if [ -n "${PORTABLE_LOCK_FORCE_BACKEND:-}" ]; then
  if [ "$BACKEND" = "$PORTABLE_LOCK_FORCE_BACKEND" ]; then
    pass "forced backend honored: PORTABLE_LOCK_FORCE_BACKEND=$PORTABLE_LOCK_FORCE_BACKEND actually ran"
  else
    fail "forced backend IGNORED: asked for '$PORTABLE_LOCK_FORCE_BACKEND', library used '$BACKEND'"
  fi
fi

# ── 1. Mutual exclusion under contention ─────────────────────────────────────
# Each worker claims the critical section by writing its id, sleeps, then checks
# the claim is still its own. If two workers are ever inside at once, the second
# overwrites the first's claim and the first sees a foreign id. No timestamps
# involved, so this cannot be fooled by clock resolution.
#
# Repeated over several rounds: the bug this replaced surfaced in roughly 1 round
# in 5, so a single round would have shipped it.
VIOLATIONS=0
ROUNDS=6
WORKERS=20
for round in $(seq 1 "$ROUNDS"); do
  LOCK="$TMP/mutex-$round.lock"
  HOLDER="$TMP/holder-$round"
  VIOL="$TMP/viol-$round"
  : > "$VIOL"
  for i in $(seq 1 "$WORKERS"); do
    (
      if portable_lock_acquire "$LOCK" 30 >/dev/null 2>&1; then
        echo "$i" > "$HOLDER"
        sleep 0.01
        seen=$(cat "$HOLDER" 2>/dev/null)
        [ "$seen" = "$i" ] || echo "worker $i entered with holder=$seen" >> "$VIOL"
      else
        echo "worker $i TIMED OUT" >> "$VIOL"
      fi
    ) &
  done
  wait
  v=$(wc -l < "$VIOL" | tr -d '[:space:]')
  VIOLATIONS=$(( VIOLATIONS + v ))
  [ "$v" -gt 0 ] && sed 's/^/     /' "$VIOL"
done

if [ "$VIOLATIONS" -eq 0 ]; then
  pass "mutual exclusion held: $ROUNDS rounds x $WORKERS workers, 0 violations"
else
  fail "mutual exclusion VIOLATED $VIOLATIONS times across $ROUNDS rounds"
fi

# ── 2. Serialization is real, not just non-overlapping writes ────────────────
# Every worker reads a counter under the lock, then increments it. Correct
# serialization means each worker observes a DISTINCT value.
LOCK="$TMP/serial.lock"
COUNTER="$TMP/counter.txt"
: > "$COUNTER"
for i in $(seq 1 20); do
  (
    if portable_lock_acquire "$LOCK" 30 >/dev/null 2>&1; then
      n=$(wc -l < "$COUNTER" | tr -d '[:space:]')
      sleep 0.01
      printf 'worker-%s-saw-%s\n' "$i" "$n" >> "$COUNTER"
    fi
  ) &
done
wait

LINES=$(wc -l < "$COUNTER" | tr -d '[:space:]')
DISTINCT=$(sed 's/.*-saw-//' "$COUNTER" | sort -u | wc -l | tr -d '[:space:]')
if [ "$LINES" = "20" ] && [ "$DISTINCT" = "20" ]; then
  pass "20 workers each observed a distinct counter value (true serialization)"
else
  fail "serialization broken: $LINES writes, only $DISTINCT distinct observations"
fi

# ── 3. Lock is released when the holding subshell exits ──────────────────────
LOCK="$TMP/scope.lock"
( portable_lock_acquire "$LOCK" 5 >/dev/null 2>&1 ) 2>/dev/null
if ( portable_lock_acquire "$LOCK" 2 >/dev/null 2>&1 ); then
  pass "lock is reacquirable after the holding subshell exits"
else
  fail "lock leaked: still held after the holding subshell exited"
fi

# ── 4. Lock is reclaimed when the holder is SIGKILLed (kernel-backed) ────────
# A stale-lockfile scheme would wedge here forever. The kernel drops flock(2) on
# process death, including SIGKILL, with no reaping logic on our side.
#
# `exec sleep` matters: a forked child would INHERIT fd 9 and keep the open file
# description — and therefore the lock — alive after we kill the parent. That is
# real flock(1) semantics, not a defect, so the test holds the lock in exactly
# one process to assert the property it actually means to assert.
LOCK="$TMP/kill.lock"
(
  portable_lock_acquire "$LOCK" 5 >/dev/null 2>&1
  exec sleep 30
) &
KILLED_PID=$!
sleep 1
kill -9 "$KILLED_PID" 2>/dev/null
wait "$KILLED_PID" 2>/dev/null

if ( portable_lock_acquire "$LOCK" 3 >/dev/null 2>&1 ); then
  pass "lock is reclaimable after the holder is SIGKILLed (no stale wedge)"
else
  fail "lock wedged after holder was SIGKILLed"
fi

# ── 5. Timeout is honored when the lock is genuinely held ────────────────────
LOCK="$TMP/timeout.lock"
HOLD_READY="$TMP/held"
(
  portable_lock_acquire "$LOCK" 5 >/dev/null 2>&1
  touch "$HOLD_READY"
  sleep 5
) &
HOLDER_PID=$!
# Wait for the holder to actually have it before we test contention.
for _ in $(seq 1 50); do [ -f "$HOLD_READY" ] && break; sleep 0.1; done

START=$(date +%s)
if ( portable_lock_acquire "$LOCK" 1 >/dev/null 2>&1 ); then
  fail "acquired a lock that was already held (mutual exclusion broken)"
else
  ELAPSED=$(( $(date +%s) - START ))
  if [ "$ELAPSED" -ge 1 ] && [ "$ELAPSED" -le 3 ]; then
    pass "contended acquire fails after honoring its ~1s timeout (waited ${ELAPSED}s)"
  else
    fail "timeout not honored: expected ~1s, waited ${ELAPSED}s"
  fi
fi
kill -9 "$HOLDER_PID" 2>/dev/null
wait "$HOLDER_PID" 2>/dev/null

echo
echo "backend exercised: $BACKEND"
echo "passed: $PASS  failed: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
echo "All portable-lock tests passed."
