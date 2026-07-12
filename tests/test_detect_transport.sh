#!/usr/bin/env bash
# test_detect_transport.sh — vault-addressability tests for scripts/detect-transport.sh.
#
# The CLI targets a vault by NAME, resolved against Obsidian's registry, never by
# path. So a present binary does NOT mean the binary can reach the vault we are
# standing in. If another directory is registered under the same name, every CLI
# call silently reads and writes THAT directory while reporting success.
#
# That is not hypothetical: a stray copy of this repo registered under the same
# name absorbed an entire session's CLI writes while the real working tree sat
# untouched. These tests pin the guard that now prevents it.
#
# Runs against a mock obsidian-cli in a throwaway vault, so it is hermetic and
# needs no Obsidian install.
#
# Usage: bash tests/test_detect_transport.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(dirname "$SCRIPT_DIR")"
DETECT="$VAULT_ROOT/scripts/detect-transport.sh"

PASS=0
FAIL=0
pass() { echo "OK   $1"; PASS=$((PASS+1)); }
fail() { echo "FAIL $1"; FAIL=$((FAIL+1)); }

TMP=$(mktemp -d -t dt-test-XXXXXX)
trap 'rm -rf "$TMP"' EXIT

# Throwaway vault mirroring the real layout (the script derives its root from its
# own location, so it must live under <vault>/scripts/).
VAULT="$TMP/vault"
mkdir -p "$VAULT/scripts" "$VAULT/wiki"
cp "$DETECT" "$VAULT/scripts/detect-transport.sh"
chmod +x "$VAULT/scripts/detect-transport.sh"
VAULT_REAL="$(cd "$VAULT" && pwd -P)"

# Mock obsidian-cli. `vaults verbose` emits <name>\t<path>; the path it reports is
# whatever MOCK_VAULT_PATH says, which is how we simulate the mismatch.
MOCKBIN="$TMP/mockbin"
mkdir -p "$MOCKBIN"
cat > "$MOCKBIN/obsidian-cli" <<'MOCK'
#!/usr/bin/env bash
case "${1:-}" in
  version) echo "1.12.7 (installer 1.12.7)"; exit 0 ;;
  vaults)  printf '%s\t%s\n' "${MOCK_VAULT_NAME:-some-vault}" "${MOCK_VAULT_PATH:-/nonexistent/elsewhere}"; exit 0 ;;
  *)       echo "Error: Command \"${1:-}\" not found."; exit 1 ;;
esac
MOCK
chmod +x "$MOCKBIN/obsidian-cli"

read_json() { python3 -c "import json,sys;print(json.load(open('$1'))$2)" 2>/dev/null; }

run_detect() {
  ( cd "$VAULT" && PATH="$MOCKBIN:$PATH" bash scripts/detect-transport.sh --force --quiet >/dev/null 2>&1 )
  echo "$VAULT/.vault-meta/transport.json"
}

# ── 1. Vault IS registered under a name → cli preferred, name published ──────
export MOCK_VAULT_NAME="my-registered-vault"
export MOCK_VAULT_PATH="$VAULT_REAL"
SNAP="$(run_detect)"

got_pref="$(read_json "$SNAP" "['preferred']")"
got_addr="$(read_json "$SNAP" "['available']['cli']['vault_addressable']")"
got_name="$(read_json "$SNAP" "['available']['cli']['vault_name']")"

[ "$got_pref" = "cli" ] \
  && pass "vault registered at this path -> preferred=cli" \
  || fail "vault registered at this path -> expected preferred=cli, got '$got_pref'"

[ "$got_addr" = "True" ] \
  && pass "vault_addressable=true when the path matches" \
  || fail "vault_addressable expected true, got '$got_addr'"

[ "$got_name" = "my-registered-vault" ] \
  && pass "resolved vault_name published for consumers (got '$got_name')" \
  || fail "vault_name expected 'my-registered-vault', got '$got_name'"

# ── 2. THE BUG: a DIFFERENT dir registered under a name → must NOT prefer cli ─
# The binary works, `vaults` succeeds, everything looks healthy. But the only
# vault Obsidian knows lives somewhere else, so any CLI write would land there.
export MOCK_VAULT_NAME="claude-obsidian"
export MOCK_VAULT_PATH="$TMP/some-other-copy"
mkdir -p "$TMP/some-other-copy"
SNAP="$(run_detect)"

got_pref="$(read_json "$SNAP" "['preferred']")"
got_present="$(read_json "$SNAP" "['available']['cli']['present']")"
got_addr="$(read_json "$SNAP" "['available']['cli']['vault_addressable']")"

[ "$got_pref" = "filesystem" ] \
  && pass "vault registered ELSEWHERE -> falls back to filesystem (no silent wrong-target)" \
  || fail "vault registered elsewhere -> expected filesystem, got '$got_pref' (WOULD WRITE TO THE WRONG DIRECTORY)"

[ "$got_present" = "True" ] \
  && pass "cli.present stays true (the binary IS there; it just cannot reach us)" \
  || fail "cli.present expected true, got '$got_present'"

[ "$got_addr" = "False" ] \
  && pass "vault_addressable=false when the registered path differs" \
  || fail "vault_addressable expected false, got '$got_addr'"

# ── 3. Obsidian knows NO vaults at all → filesystem ──────────────────────────
cat > "$MOCKBIN/obsidian-cli" <<'MOCK'
#!/usr/bin/env bash
case "${1:-}" in
  version) echo "1.12.7"; exit 0 ;;
  vaults)  exit 0 ;;   # no vaults registered
  *)       exit 1 ;;
esac
MOCK
chmod +x "$MOCKBIN/obsidian-cli"
SNAP="$(run_detect)"

got_pref="$(read_json "$SNAP" "['preferred']")"
[ "$got_pref" = "filesystem" ] \
  && pass "no vaults registered -> filesystem" \
  || fail "no vaults registered -> expected filesystem, got '$got_pref'"

# ── 4. Snapshot stays valid JSON on every path ───────────────────────────────
python3 -c "import json;json.load(open('$SNAP'))" 2>/dev/null \
  && pass "snapshot is valid JSON" \
  || fail "snapshot is not valid JSON"

echo
echo "passed: $PASS  failed: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
echo "All detect-transport tests passed."
