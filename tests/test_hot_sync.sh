#!/usr/bin/env bash
# test_hot_sync.sh — hermetic tests for scripts/hot-sync.sh

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOT_SH="$ROOT/scripts/hot-sync.sh"

PASS=0
FAIL=0

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

assert_false() {
  local label="$1"
  shift
  if "$@"; then
    echo "FAIL $label"
    FAIL=$((FAIL + 1))
  else
    echo "OK   $label"
    PASS=$((PASS + 1))
  fi
}

assert_contains() {
  local label="$1" needle="$2" haystack="$3"
  if grep -Fq "$needle" <<<"$haystack"; then
    echo "OK   $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label (missing: $needle)"
    FAIL=$((FAIL + 1))
  fi
}

SANDBOX=$(mktemp -d /tmp/hot-sync-test-XXXXXX)
trap 'rm -rf "$SANDBOX"' EXIT

mkdir -p "$SANDBOX/wiki" "$SANDBOX/.claude-plugin" "$SANDBOX/skills/alpha" "$SANDBOX/skills/beta"
printf '%s\n' '{"name":"vault-os","version":"9.9.9"}' >"$SANDBOX/.claude-plugin/plugin.json"
cat >"$SANDBOX/wiki/log.md" <<'EOF'
## [2026-08-01] save | first
## [2026-07-01] save | second
EOF

# Seed hot.md with an Active Threads block that must survive
cat >"$SANDBOX/wiki/hot.md" <<'EOF'
---
title: old
---
garbage fossil content claiming version 1.0.0

## Active Threads

<!-- ACTIVE-THREADS:START -->
- keep this bullet
<!-- ACTIVE-THREADS:END -->
EOF

# Init a tiny git repo so commits section works
git -C "$SANDBOX" init -q
git -C "$SANDBOX" config user.email "test@example.com"
git -C "$SANDBOX" config user.name "test"
git -C "$SANDBOX" add -A
git -C "$SANDBOX" commit -qm "seed"

OUT1="$(bash "$HOT_SH" "$SANDBOX")"
HOT="$(cat "$SANDBOX/wiki/hot.md")"

assert_contains "writes version from plugin.json" "Version**: 9.9.9" "$HOT"
assert_contains "writes skill count" "Skills**: 2" "$HOT"
assert_contains "marks generator" "generator: hot-sync" "$HOT"
assert_contains "preserves active thread" "keep this bullet" "$HOT"
assert_false "drops fossil claim" grep -q 'version 1.0.0' <<<"$HOT"
assert_true "under line budget" test "$(wc -l <"$SANDBOX/wiki/hot.md" | tr -d ' ')" -le 60

# Second run with unchanged ground truth should skip write
OUT2="$(bash "$HOT_SH" "$SANDBOX")"
assert_contains "skips when unchanged" "unchanged" "$OUT2"
HOT2="$(cat "$SANDBOX/wiki/hot.md")"
assert_contains "second run preserves threads" "keep this bullet" "$HOT2"

# --force rewrites
OUT3="$(bash "$HOT_SH" --force "$SANDBOX")"
assert_contains "force rewrites" "wrote" "$OUT3"

# Dead path must not reappear
assert_false "no Desktop/claude-obsidian path" grep -q 'Desktop/claude-obsidian' <<<"$HOT2"

echo ""
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ]
