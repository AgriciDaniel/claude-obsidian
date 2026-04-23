#!/usr/bin/env bash
# test_allocate_address.sh — smoke tests for scripts/allocate-address.sh.
#
# Runs in a throwaway temp vault so it never touches the real
# .vault-meta/address-counter.txt. Exits non-zero on any failure.
#
# Usage: bash tests/test_allocate_address.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(dirname "$SCRIPT_DIR")"
ALLOC="$VAULT_ROOT/scripts/allocate-address.sh"

PASS=0
FAIL=0
pass() { echo "OK   $1"; PASS=$((PASS+1)); }
fail() { echo "FAIL $1"; FAIL=$((FAIL+1)); }

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then pass "$label (got $actual)"
  else fail "$label: expected '$expected', got '$actual'"
  fi
}

# Create a fresh throwaway vault
TMP=$(mktemp -d -t ds-test-XXXXXX)
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/scripts" "$TMP/wiki"
cp "$ALLOC" "$TMP/scripts/allocate-address.sh"
chmod +x "$TMP/scripts/allocate-address.sh"
cd "$TMP"

# --- Test 1: rebuild on empty vault = 1 ---
OUT=$(./scripts/allocate-address.sh --rebuild 2>&1)
assert_eq "rebuild on empty vault" "Counter rebuilt: next = 1" "$OUT"
assert_eq "counter file value" "1" "$(cat .vault-meta/address-counter.txt)"

# --- Test 2: peek does not increment ---
P1=$(./scripts/allocate-address.sh --peek)
P2=$(./scripts/allocate-address.sh --peek)
assert_eq "peek idempotent" "$P1" "$P2"

# --- Test 3: allocate returns c-000001 and increments ---
A1=$(./scripts/allocate-address.sh)
assert_eq "first alloc" "c-000001" "$A1"
assert_eq "counter after 1 alloc" "2" "$(cat .vault-meta/address-counter.txt)"

# --- Test 4: monotonic sequence ---
A2=$(./scripts/allocate-address.sh)
A3=$(./scripts/allocate-address.sh)
assert_eq "second alloc"  "c-000002" "$A2"
assert_eq "third alloc"   "c-000003" "$A3"

# --- Test 5: concurrent allocations are unique ---
./scripts/allocate-address.sh --rebuild >/dev/null
for i in $(seq 1 10); do
  (./scripts/allocate-address.sh >> concurrent.txt) &
done
wait
UNIQ=$(sort -u concurrent.txt | wc -l)
TOTAL=$(wc -l < concurrent.txt)
assert_eq "10 concurrent allocs: unique count" "10" "$UNIQ"
assert_eq "10 concurrent allocs: total count"  "10" "$TOTAL"

# --- Test 6: corrupt counter -> exit 3 ---
echo "not-a-number" > .vault-meta/address-counter.txt
set +e
./scripts/allocate-address.sh > /dev/null 2>&1
EC=$?
set -e
assert_eq "corrupt counter exit" "3" "$EC"
./scripts/allocate-address.sh --rebuild > /dev/null

# --- Test 7: missing counter recovers from max(c-)+1 ---
rm -f .vault-meta/address-counter.txt
# Drop a fake page into wiki/ with a real frontmatter address so rebuild finds it
cat > wiki/fake.md <<'EOF'
---
type: concept
address: c-000500
---
EOF
REC=$(./scripts/allocate-address.sh --peek 2>/dev/null)
assert_eq "recovery from max observed" "501" "$REC"

# --- Test 8: frontmatter-only scan ignores code-block examples ---
rm wiki/fake.md
echo "1" > .vault-meta/address-counter.txt
cat > wiki/doc.md <<'EOF'
---
type: concept
---
# Doc with a code-block example
```yaml
address: c-999999
```
EOF
REBUILT=$(./scripts/allocate-address.sh --rebuild 2>&1)
assert_eq "code-block ignored, rebuild to 1" "Counter rebuilt: next = 1" "$REBUILT"

# --- Summary ---
echo ""
echo "Passed: $PASS"
echo "Failed: $FAIL"
[ "$FAIL" -eq 0 ]
