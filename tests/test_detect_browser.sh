#!/usr/bin/env bash
# test_detect_browser.sh — unit tests for scripts/detect-browser.sh.
#
# Hermetic: the script derives VAULT_ROOT from its own location, so we copy it
# into a throwaway vault under mktemp and run it there. The repo's real
# .vault-meta/browser.json is never read, written, or even created. No network.
#
# Covers:
#   - --peek emits valid JSON and writes NOTHING
#   - the snapshot carries every key the fallback chain consumers read
#   - preferred is one of playwright|cdp|fetch, and fetch is always present
#     (the floor is never absent; that is what makes it the floor)
#   - fallback_chain always terminates in "fetch"
#   - --force writes a file, and the written file is valid JSON
#   - the freshness cache short-circuits a plain run
#   - an unrecognized flag exits 3
#
# macOS-safe by construction: bash 3.2 (no associative arrays, no `readlink -f`,
# no GNU-only flags). JSON is inspected with python3, which detect-browser.sh
# already depends on.
#
# Usage: bash tests/test_detect_browser.sh

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/scripts/detect-browser.sh"

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

# Read one field out of a JSON document on stdin. Dotted path, list index by int.
# Prints the value; prints nothing and returns 1 if the path is absent.
json_get() {
  python3 -c '
import json, sys
doc = json.load(sys.stdin)
node = doc
for part in sys.argv[1].split("."):
    if isinstance(node, list):
        node = node[int(part)]
    else:
        if part not in node:
            sys.exit(1)
        node = node[part]
if isinstance(node, bool):
    print("true" if node else "false")
elif node is None:
    print("null")
else:
    print(node)
' "$1"
}

# ── Sandbox vault: the script resolves VAULT_ROOT as $(dirname $0)/.. ─────────
SANDBOX=$(mktemp -d /tmp/detect-browser-test-XXXXXX)
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/scripts"
cp "$SRC" "$SANDBOX/scripts/detect-browser.sh"
chmod +x "$SANDBOX/scripts/detect-browser.sh"

DB="$SANDBOX/scripts/detect-browser.sh"
OUT="$SANDBOX/.vault-meta/browser.json"

db() { bash "$DB" --quiet "$@"; }

echo "=== test_detect_browser.sh ==="
echo "sandbox: $SANDBOX"
echo ""

# ── --peek emits valid JSON ──────────────────────────────────────────────────
PEEK="$(db --peek)"
PEEK_RC=$?
assert_eq "peek rc" "0" "$PEEK_RC"

printf '%s' "$PEEK" | python3 -m json.tool >/dev/null 2>&1
assert_eq "peek output is valid JSON" "0" "$?"

# ── --peek writes nothing ────────────────────────────────────────────────────
assert_true "peek does NOT write browser.json" [ ! -f "$OUT" ]

# ── Required keys ────────────────────────────────────────────────────────────
SCHEMA="$(printf '%s' "$PEEK" | json_get schema_version)"
assert_eq "schema_version is 1" "1" "$SCHEMA"

PREFERRED="$(printf '%s' "$PEEK" | json_get preferred)"
case "$PREFERRED" in
  playwright|cdp|fetch)
    assert_eq "preferred is one of playwright|cdp|fetch" "yes" "yes" ;;
  *)
    assert_eq "preferred is one of playwright|cdp|fetch" "yes" "no($PREFERRED)" ;;
esac

printf '%s' "$PEEK" | json_get fallback_chain >/dev/null 2>&1
assert_eq "fallback_chain key present" "0" "$?"

printf '%s' "$PEEK" | json_get available >/dev/null 2>&1
assert_eq "available key present" "0" "$?"

printf '%s' "$PEEK" | json_get detected_at >/dev/null 2>&1
assert_eq "detected_at key present" "0" "$?"

# ── The floor: fetch is ALWAYS available ─────────────────────────────────────
# If fetch could be absent it would not be a floor, and every consumer's
# "fall all the way back" branch would be reaching for something that is not there.
FETCH_PRESENT="$(printf '%s' "$PEEK" | json_get available.fetch.present)"
assert_eq "available.fetch.present is always true" "true" "$FETCH_PRESENT"

# ── fallback_chain always terminates in "fetch" ──────────────────────────────
CHAIN_LAST="$(printf '%s' "$PEEK" | python3 -c '
import json, sys
print(json.load(sys.stdin)["fallback_chain"][-1])
')"
assert_eq "fallback_chain ends with fetch" "fetch" "$CHAIN_LAST"

CHAIN_HEAD="$(printf '%s' "$PEEK" | python3 -c '
import json, sys
print(json.load(sys.stdin)["fallback_chain"][0])
')"
assert_eq "fallback_chain head equals preferred" "$PREFERRED" "$CHAIN_HEAD"

# ── The chain is consistent with what was actually detected ──────────────────
# preferred=playwright implies playwright.present; preferred=cdp implies cdp.present.
PW_PRESENT="$(printf '%s' "$PEEK" | json_get available.playwright.present)"
CDP_PRESENT="$(printf '%s' "$PEEK" | json_get available.cdp.present)"
case "$PREFERRED" in
  playwright) assert_eq "preferred=playwright implies playwright.present" "true" "$PW_PRESENT" ;;
  cdp)        assert_eq "preferred=cdp implies cdp.present"               "true" "$CDP_PRESENT" ;;
  fetch)      assert_eq "preferred=fetch implies no playwright"           "false" "$PW_PRESENT" ;;
esac

# Every chain entry must be a known transport.
BAD_ENTRY="$(printf '%s' "$PEEK" | python3 -c '
import json, sys
known = {"playwright", "cdp", "fetch"}
bad = [t for t in json.load(sys.stdin)["fallback_chain"] if t not in known]
print(",".join(bad))
')"
assert_eq "no unknown transports in fallback_chain" "" "$BAD_ENTRY"

# ── --force writes the file, and the file is valid JSON ──────────────────────
db --force >/dev/null
assert_eq "force rc" "0" "$?"
assert_true "force writes browser.json" [ -f "$OUT" ]

python3 -m json.tool < "$OUT" >/dev/null 2>&1
assert_eq "written browser.json is valid JSON" "0" "$?"

WRITTEN_PREFERRED="$(json_get preferred < "$OUT")"
assert_eq "written preferred matches peeked preferred" "$PREFERRED" "$WRITTEN_PREFERRED"

WRITTEN_FETCH="$(json_get available.fetch.present < "$OUT")"
assert_eq "written available.fetch.present is true" "true" "$WRITTEN_FETCH"

# No temp file left behind by the atomic write.
LEFTOVER=$(find "$SANDBOX/.vault-meta" -name 'browser.json.*.tmp' 2>/dev/null | wc -l | tr -d ' ')
assert_eq "no leftover .tmp after write" "0" "$LEFTOVER"

# ── Freshness cache: a plain run reuses a fresh snapshot ─────────────────────
# Overwrite the snapshot with a marker. A plain run must NOT re-detect: it must
# find the file fresh (<7d) and echo it back verbatim.
printf '{"marker": "cached"}\n' > "$OUT"
PLAIN="$(db)"
assert_eq "plain run rc" "0" "$?"
case "$PLAIN" in
  *cached*) assert_eq "fresh snapshot is reused, not re-detected" "yes" "yes" ;;
  *)        assert_eq "fresh snapshot is reused, not re-detected" "yes" "no" ;;
esac

# ── --force overrides the freshness cache ────────────────────────────────────
db --force >/dev/null
# grep -c prints '0' and exits 1 when there is no match, so no `|| echo 0`
# fallback here: it would append a second line to the count.
MARKER_GONE="$(grep -c 'marker' "$OUT" 2>/dev/null)"
assert_eq "force overrides the freshness cache" "0" "$MARKER_GONE"
FORCED_SCHEMA="$(json_get schema_version < "$OUT")"
assert_eq "force re-detected a real snapshot" "1" "$FORCED_SCHEMA"

# ── Unrecognized flag exits 3 ────────────────────────────────────────────────
RC_BAD=$( (bash "$DB" --bogus >/dev/null 2>&1); echo $? )
assert_eq "unknown flag exits 3" "3" "$RC_BAD"

RC_BAD2=$( (bash "$DB" --peek --nope >/dev/null 2>&1); echo $? )
assert_eq "unknown flag after a valid one still exits 3" "3" "$RC_BAD2"

# ── --help exits 0 ───────────────────────────────────────────────────────────
RC_HELP=$( (bash "$DB" --help >/dev/null 2>&1); echo $? )
assert_eq "--help exits 0" "0" "$RC_HELP"

# ── The real vault was never touched ─────────────────────────────────────────
# The whole point of the sandbox. If this fails, the test is not hermetic.
assert_true "real .vault-meta/browser.json not created" [ ! -f "$ROOT/.vault-meta/browser.json" ]

# ── summary ──────────────────────────────────────────────────────────────────
echo ""
echo "Pass: $PASS  Fail: $FAIL"
if [ $FAIL -gt 0 ]; then
  exit 1
fi
echo "All detect-browser tests passed."
