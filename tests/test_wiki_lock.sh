#!/usr/bin/env bash
# test_wiki_lock.sh — unit tests for scripts/wiki-lock.sh.
#
# Hermetic: creates a throwaway vault under mktemp, no network, no external
# deps beyond bash + standard POSIX utilities. Covers:
#   - acquire returns 0 on first call, 75 on second call from a holding context
#   - release frees the lock and re-acquire works
#   - list shows held locks; reflects releases
#   - clear-stale removes locks for dead PIDs
#   - peek is read-only and reports unheld/held correctly
#   - path validation rejects absolute paths and traversal
#
# Usage: bash tests/test_wiki_lock.sh

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_SH="$ROOT/scripts/wiki-lock.sh"

PASS=0
FAIL=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    echo "OK   $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label: expected '$expected', got '$actual'"
    FAIL=$((FAIL + 1))
  fi
}

assert_true() {
  local label="$1"
  shift
  if "$@"; then
    echo "OK   $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label"
    FAIL=$((FAIL + 1))
  fi
}

# Set up a sandbox vault for the duration of this run
SANDBOX=$(mktemp -d /tmp/wiki-lock-test-XXXXXX)
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/.vault-meta/locks"
export WIKI_LOCK_VAULT="$SANDBOX"

# Helper: run wiki-lock.sh against the sandbox; return rc
wl() {
  bash "$LOCK_SH" "$@"
}

echo "=== test_wiki_lock.sh ==="
echo "sandbox: $SANDBOX"
echo ""

# ── acquire on a fresh path returns 0 ────────────────────────────────────────
wl acquire wiki/concepts/Foo.md >/dev/null
assert_eq "first acquire rc" "0" "$?"

# ── second acquire while the lock is fresh returns 75 ────────────────────────
# With age-based staleness (STALE_AFTER_SEC=60 default), the lock is held until
# either an explicit release OR 60 seconds elapse. A second acquire immediately
# after the first should refuse.
RC2=$( (wl acquire wiki/concepts/Foo.md >/dev/null); echo $? )
assert_eq "second acquire while fresh rc" "75" "$RC2"

# ── peek shows the lock ──────────────────────────────────────────────────────
PEEK_OUT=$(wl peek wiki/concepts/Foo.md)
case "$PEEK_OUT" in
  *"wiki/concepts/Foo.md"*) assert_eq "peek includes path" "yes" "yes" ;;
  *) assert_eq "peek includes path" "yes" "no($PEEK_OUT)" ;;
esac

# ── list shows the held lock ─────────────────────────────────────────────────
LIST_OUT=$(wl list)
case "$LIST_OUT" in
  *"wiki/concepts/Foo.md"*) assert_eq "list shows held lock" "yes" "yes" ;;
  *) assert_eq "list shows held lock" "yes" "no" ;;
esac

# ── release frees the lock (cross-process release is allowed by design) ─────
wl release wiki/concepts/Foo.md
LIST_AFTER_RELEASE=$(wl list)
assert_eq "list empty after release" "" "$LIST_AFTER_RELEASE"

# ── re-acquire after release succeeds ───────────────────────────────────────
wl acquire wiki/concepts/Foo.md >/dev/null
assert_eq "re-acquire after release rc" "0" "$?"
wl release wiki/concepts/Foo.md

# ── short --stale-after-sec lets us test age-based reap quickly ─────────────
# Acquire with a 1-second stale window, sleep 2s, second acquire should succeed
wl --stale-after-sec 1 acquire wiki/concepts/Aged.md >/dev/null 2>&1 || \
  bash "$LOCK_SH" acquire --stale-after-sec 1 wiki/concepts/Aged.md >/dev/null 2>&1
# (flag order tolerance) — make sure the lock exists
PEEK_AGED=$(wl peek wiki/concepts/Aged.md)
case "$PEEK_AGED" in
  *Aged.md*) : ;;
  *) echo "DEBUG: aged peek was: $PEEK_AGED" ;;
esac
sleep 2
RC_AGED=$( (bash "$LOCK_SH" --stale-after-sec 1 acquire wiki/concepts/Aged.md >/dev/null 2>&1); echo $? )
assert_eq "age-based stale reap allows re-acquire" "0" "$RC_AGED"
wl release wiki/concepts/Aged.md

# ── clear-stale with max-age=0 reaps everything ──────────────────────────────
# First seed a lock to reap
wl acquire wiki/concepts/Reap.md >/dev/null
REMOVED=$(wl clear-stale --max-age 0)
# Should have removed 1 (the Reap.md lock)
case "$REMOVED" in
  [1-9]*) assert_eq "clear-stale removed count >=1" "yes" "yes" ;;
  *) assert_eq "clear-stale removed count >=1" "yes" "no($REMOVED)" ;;
esac
LIST_AFTER_CLEAR=$(wl list)
assert_eq "list empty after clear-stale" "" "$LIST_AFTER_CLEAR"

# ── peek on unheld path ──────────────────────────────────────────────────────
PEEK_UNHELD=$(wl peek wiki/concepts/Never.md)
assert_eq "peek unheld" "unheld" "$PEEK_UNHELD"

# ── path validation: absolute path rejected ──────────────────────────────────
RC_ABS=$( (wl acquire /etc/passwd >/dev/null 2>&1); echo $? )
assert_eq "acquire absolute path rejected" "4" "$RC_ABS"

# ── path validation: traversal rejected ──────────────────────────────────────
RC_DOTDOT=$( (wl acquire ../escape.md >/dev/null 2>&1); echo $? )
assert_eq "acquire ../ rejected" "4" "$RC_DOTDOT"

# ── path validation: empty rejected ──────────────────────────────────────────
RC_EMPTY=$( (wl acquire "" >/dev/null 2>&1); echo $? )
assert_eq "acquire empty path rejected" "4" "$RC_EMPTY"

# ── path validation: newline rejected (v1.7.2; closes audit M4) ──────────────
# Newlines in lock paths would break the meta-lock line format (key=value lines
# separated by literal \n). Must be rejected at validate_path() time.
RC_NL=$( (wl acquire $'wiki/concepts/Foo\nbar.md' >/dev/null 2>&1); echo $? )
assert_eq "acquire newline path rejected" "4" "$RC_NL"

# ── path validation: carriage return rejected (v1.7.2; closes audit M4) ──────
RC_CR=$( (wl acquire $'wiki/concepts/Foo\rbar.md' >/dev/null 2>&1); echo $? )
assert_eq "acquire carriage-return path rejected" "4" "$RC_CR"

# ── stress: 10 unique paths all acquire cleanly ──────────────────────────────
for i in $(seq 1 10); do
  wl acquire "wiki/stress/page-$i.md" >/dev/null
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL stress acquire $i: rc=$rc"
    FAIL=$((FAIL + 1))
    break
  fi
done
LIST_COUNT=$(wl list | wc -l)
assert_eq "10 unique paths all acquired" "10" "$LIST_COUNT"
wl clear-stale --max-age 0 >/dev/null

# ── summary ──────────────────────────────────────────────────────────────────
echo ""
echo "Pass: $PASS  Fail: $FAIL"
if [ $FAIL -gt 0 ]; then
  exit 1
fi
echo "All wiki-lock tests passed."
