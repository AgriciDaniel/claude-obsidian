#!/usr/bin/env bash
# test_setup_perimeter.sh — unit tests for bin/setup-perimeter.sh.
#
# Hermetic: creates a throwaway git repo under mktemp, no network. Covers:
#   - install (--yes) writes both managed hooks + seeds config files
#   - clean commit passes
#   - staged sensitive path is blocked
#   - added identifier matching a configured pattern is blocked
#   - whitelisted token passes
#   - PERIMETER_ALLOW=1 single-shot override works
#   - air-gap OFF: pre-push hook exits 0; air-gap ON: exits 1;
#     PERIMETER_ALLOW_PUSH=1 overrides
#   - existing unmanaged hook is backed up and restored on --uninstall
#   - --check runs read-only; re-run is idempotent
#
# Usage: bash tests/test_setup_perimeter.sh

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETUP="$ROOT/bin/setup-perimeter.sh"

PASS=0
FAIL=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    echo "OK   $label"; PASS=$((PASS + 1))
  else
    echo "FAIL $label: expected '$expected', got '$actual'"; FAIL=$((FAIL + 1))
  fi
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"

git init -q .
git config user.email test@example.com
git config user.name "Perimeter Test"

# Pre-existing unmanaged hook: must be backed up, then restored on uninstall.
mkdir -p .git/hooks
printf '#!/bin/sh\nexit 0\n' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# The setup script derives the vault root from its own location, so run a
# copy from inside the temp repo (mirrors a vault that vendors the plugin).
mkdir -p bin
cp "$SETUP" bin/setup-perimeter.sh

bash bin/setup-perimeter.sh --yes >/dev/null 2>&1
assert_eq "install exit code" "0" "$?"

grep -q "managed-by: claude-obsidian setup-perimeter" .git/hooks/pre-commit \
  && assert_eq "pre-commit is managed" "0" "0" \
  || assert_eq "pre-commit is managed" "0" "1"
[ -f .git/hooks/pre-commit.pre-perimeter.bak ] \
  && assert_eq "unmanaged hook backed up" "0" "0" \
  || assert_eq "unmanaged hook backed up" "0" "1"
[ -f .vault-meta/perimeter-paths.txt ] \
  && assert_eq "config seeded" "0" "0" \
  || assert_eq "config seeded" "0" "1"

# Activate a path band and a pattern (Spanish DNI-style: 8 digits + letter).
printf 'private/*\n' >> .vault-meta/perimeter-paths.txt
printf '\\b[0-9]{8}[A-Za-z]\\b\n' >> .vault-meta/perimeter-patterns.txt
printf '^11111111H$\n' >> .vault-meta/perimeter-whitelist.txt

# Clean commit passes.
echo "just a note" > note.md
git add note.md
git commit -q -m "clean" >/dev/null 2>&1
assert_eq "clean commit passes" "0" "$?"

# Sensitive path blocked.
mkdir -p private
echo "diary" > private/journal.md
git add -f private/journal.md
git commit -q -m "leak path" >/dev/null 2>&1
assert_eq "sensitive path blocked" "1" "$?"
git reset -q HEAD private/journal.md && rm -rf private

# Identifier pattern blocked.
echo "client id 43215678Z appears here" > leak.md
git add leak.md
git commit -q -m "leak id" >/dev/null 2>&1
assert_eq "identifier blocked" "1" "$?"

# Single-shot override lets it through.
PERIMETER_ALLOW=1 git commit -q -m "allowed leak" >/dev/null 2>&1
assert_eq "PERIMETER_ALLOW=1 override" "0" "$?"

# Whitelisted token passes without override.
echo "public registry code 11111111H is documented" > public.md
git add public.md
git commit -q -m "whitelisted" >/dev/null 2>&1
assert_eq "whitelisted token passes" "0" "$?"

# Air-gap: off by default -> pre-push exits 0.
bash .git/hooks/pre-push origin https://example.invalid/repo.git </dev/null >/dev/null 2>&1
assert_eq "pre-push open when air-gap off" "0" "$?"

# Enable air-gap -> pre-push blocks; override lifts it once.
echo enabled > .vault-meta/perimeter-airgap
bash .git/hooks/pre-push origin https://example.invalid/repo.git </dev/null >/dev/null 2>&1
assert_eq "pre-push blocked when air-gap on" "1" "$?"
PERIMETER_ALLOW_PUSH=1 bash .git/hooks/pre-push origin https://example.invalid/repo.git </dev/null >/dev/null 2>&1
assert_eq "PERIMETER_ALLOW_PUSH=1 override" "0" "$?"

# --check is read-only and succeeds.
bash bin/setup-perimeter.sh --check >/dev/null 2>&1
assert_eq "--check exit code" "0" "$?"

# Re-run is idempotent (config not clobbered: our appended band survives).
bash bin/setup-perimeter.sh --yes >/dev/null 2>&1
grep -q 'private/\*' .vault-meta/perimeter-paths.txt \
  && assert_eq "re-run keeps user config" "0" "0" \
  || assert_eq "re-run keeps user config" "0" "1"

# Uninstall removes managed hooks and restores the original unmanaged hook.
bash bin/setup-perimeter.sh --uninstall >/dev/null 2>&1
assert_eq "uninstall exit code" "0" "$?"
if [ -f .git/hooks/pre-commit ] \
   && ! grep -q "managed-by: claude-obsidian setup-perimeter" .git/hooks/pre-commit; then
  assert_eq "original hook restored" "0" "0"
else
  assert_eq "original hook restored" "0" "1"
fi
[ ! -f .git/hooks/pre-push ] \
  && assert_eq "managed pre-push removed" "0" "0" \
  || assert_eq "managed pre-push removed" "0" "1"

echo ""
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
