#!/usr/bin/env bash
# test_code_watch_setup.sh — hermetic integration test for bin/setup-code-watch.sh.
#
# Builds a throwaway "vault" (copies the scripts the installer needs) and a
# throwaway git repo, then verifies: hook install, state registration, that a
# commit enqueues, existing-hook chaining, the vault-repo loop guard, and unwatch.
# No network, no LLM. Requires git.

set -u
PASS=0; FAIL=0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

ok()   { PASS=$((PASS+1)); printf 'OK   %s\n' "$1"; }
no()   { FAIL=$((FAIL+1)); printf 'FAIL %s%s\n' "$1" "${2:+: $2}"; }
check(){ if eval "$2"; then ok "$1"; else no "$1" "$3"; fi; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ── Build a fake vault with just the files the installer needs ───────────────
VAULT="$TMP/vault"
mkdir -p "$VAULT/scripts" "$VAULT/bin" "$VAULT/wiki" "$VAULT/.vault-meta"
cp "$ROOT/scripts/code-sync-check.py" "$VAULT/scripts/"
cp "$ROOT/bin/setup-code-watch.sh" "$ROOT/bin/code-sync-launch.sh" "$VAULT/bin/"
chmod +x "$VAULT/scripts/code-sync-check.py" "$VAULT/bin/"*.sh

# ── Build a watched code repo ────────────────────────────────────────────────
REPO="$TMP/repo"
mkdir -p "$REPO/app"
printf 'print(1)\n' > "$REPO/app/main.py"
git -C "$REPO" init -q
git -C "$REPO" config user.email t@example.com
git -C "$REPO" config user.name Test
git -C "$REPO" add app
git -C "$REPO" commit -q -m init

# ── Install (in-session) ─────────────────────────────────────────────────────
bash "$VAULT/bin/setup-code-watch.sh" "$REPO" >/dev/null 2>&1
GH="$REPO/.git/hooks"
check "managed hook installed" "[ -x '$GH/claude-obsidian-code-sync' ]"
check "post-commit installed"  "[ -x '$GH/post-commit' ]"
check "post-merge installed"   "[ -x '$GH/post-merge' ]"
check "state registered repo"  "grep -q '\"path\"' '$VAULT/.vault-meta/code-sync-state.json'"

# ── A new commit should enqueue ──────────────────────────────────────────────
printf 'print(2)\n' >> "$REPO/app/main.py"
git -C "$REPO" add app
git -C "$REPO" commit -q -m change
# give the (synchronous) enqueue a moment; the launch is backgrounded + no-ops in-session
sleep 1
check "commit enqueued to queue" "[ -f '$VAULT/.vault-meta/code-sync-queue.jsonl' ]"
check "queue has a pending entry" "grep -q '\"status\": \"pending\"' '$VAULT/.vault-meta/code-sync-queue.jsonl'"
check "queue captured changed path" "grep -q 'app/main.py' '$VAULT/.vault-meta/code-sync-queue.jsonl'"

# ── Existing-hook chaining is preserved ──────────────────────────────────────
REPO2="$TMP/repo2"
mkdir -p "$REPO2"
git -C "$REPO2" init -q
git -C "$REPO2" config user.email t@example.com
git -C "$REPO2" config user.name Test
printf 'x\n' > "$REPO2/f.txt"; git -C "$REPO2" add f.txt; git -C "$REPO2" commit -q -m init
printf '#!/bin/sh\necho ORIGINAL_HOOK\n' > "$REPO2/.git/hooks/post-commit"
chmod +x "$REPO2/.git/hooks/post-commit"
bash "$VAULT/bin/setup-code-watch.sh" "$REPO2" >/dev/null 2>&1
check "existing hook content preserved" "grep -q 'ORIGINAL_HOOK' '$REPO2/.git/hooks/post-commit'"
check "our marker chained in"           "grep -q 'claude-obsidian code-watch' '$REPO2/.git/hooks/post-commit'"

# ── Loop guard: refuse to watch the vault's own repo ─────────────────────────
git -C "$VAULT" init -q
git -C "$VAULT" config user.email t@example.com
git -C "$VAULT" config user.name Test
bash "$VAULT/bin/setup-code-watch.sh" "$VAULT" >/dev/null 2>&1; GUARD_RC=$?
check "loop guard returns exit 4" "[ $GUARD_RC -eq 4 ]" "got rc=$GUARD_RC"

# ── Unwatch removes the managed hook + unregisters ───────────────────────────
bash "$VAULT/bin/setup-code-watch.sh" "$REPO" --unwatch >/dev/null 2>&1
check "managed hook removed" "[ ! -e '$GH/claude-obsidian-code-sync' ]"
# match the exact quoted path so $TMP/repo doesn't also match $TMP/repo2
if grep -qF "\"$REPO\"" "$VAULT/.vault-meta/code-sync-state.json"; then
  no "repo unregistered" "still present in state"
else
  ok "repo unregistered"
fi

echo ""
echo "test_code_watch_setup.sh: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
