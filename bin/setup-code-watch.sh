#!/usr/bin/env bash
# setup-code-watch.sh — install commit-triggered Mode B wiki sync (v1.10+).
#
# Installs git hooks into a CODE repo so that each commit cheaply enqueues its
# changed paths into THIS vault's .vault-meta/code-sync-queue.jsonl. A separate
# stage drains the queue: in-session by default (the SessionStart hook surfaces
# drift and you run /wiki-code-ingest --sync), or autonomously via a detached
# headless `claude -p` when --autonomous is set.
#
# The installed git hook never blocks the commit and runs no LLM — it only
# appends to the queue (and, in autonomous mode, kicks a debounced background
# launcher).
#
# Usage:
#   bash bin/setup-code-watch.sh <repo-path>               # watch (in-session drain)
#   bash bin/setup-code-watch.sh <repo-path> --autonomous   # watch (headless drain on commit)
#   bash bin/setup-code-watch.sh <repo-path> --unwatch       # remove hooks + unregister
#   bash bin/setup-code-watch.sh --status                     # list watched repos
#
# Exit codes:
#   0 — success
#   2 — usage error
#   3 — <repo-path> is not a git repository
#   4 — refused: <repo-path> is the vault's own repo (would create a sync loop)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="$(dirname "$SCRIPT_DIR")"
CSC="$VAULT/scripts/code-sync-check.py"

MARK_BEGIN="# >>> claude-obsidian code-watch >>>"
MARK_END="# <<< claude-obsidian code-watch <<<"
HOOK_EVENTS="post-commit post-merge post-rewrite"

REPO=""
MODE="in-session"
ACTION="watch"

while [ $# -gt 0 ]; do
  case "$1" in
    --autonomous) MODE="autonomous"; shift ;;
    --unwatch)    ACTION="unwatch"; shift ;;
    --status)     ACTION="status"; shift ;;
    -h|--help)    sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*)           echo "ERR: unknown flag: $1" >&2; exit 2 ;;
    *)            REPO="$1"; shift ;;
  esac
done

say()  { printf '%s\n' "$@"; }
warn() { printf 'WARN: %s\n' "$@" >&2; }

if [ "$ACTION" = "status" ]; then
  python3 "$CSC" --status
  exit 0
fi

[ -n "$REPO" ] || { echo "ERR: <repo-path> required" >&2; exit 2; }

# ── Validate the target is a git repo ────────────────────────────────────────
if ! git -C "$REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  warn "not a git repository: $REPO"
  exit 3
fi
REPO_TOP="$(cd "$REPO" && git rev-parse --show-toplevel)"
GIT_DIR="$(git -C "$REPO_TOP" rev-parse --absolute-git-dir)"
HOOKS_DIR="$GIT_DIR/hooks"
MANAGED="$HOOKS_DIR/claude-obsidian-code-sync"

# ── Loop guard: never watch the vault's own repo ─────────────────────────────
VAULT_TOP="$(git -C "$VAULT" rev-parse --show-toplevel 2>/dev/null || echo "$VAULT")"
if [ "$(cd "$REPO_TOP" && pwd -P)" = "$(cd "$VAULT_TOP" && pwd -P)" ]; then
  warn "refusing to watch the vault's own git repo ($REPO_TOP) — this would create a commit→sync→commit loop."
  exit 4
fi

strip_block() {  # remove our marker block from a hook file, delete file if now trivial
  local f="$1"
  [ -f "$f" ] || return 0
  sed -i "/$MARK_BEGIN/,/$MARK_END/d" "$f" 2>/dev/null || \
    sed -i '' "/$MARK_BEGIN/,/$MARK_END/d" "$f" 2>/dev/null || true
  # if nothing but a shebang / blank lines / comments remains, remove the file
  if ! grep -qvE '^\s*(#.*)?$' "$f"; then
    rm -f "$f"
  fi
}

if [ "$ACTION" = "unwatch" ]; then
  rm -f "$MANAGED"
  for ev in $HOOK_EVENTS; do strip_block "$HOOKS_DIR/$ev"; done
  python3 "$CSC" --unregister --repo "$REPO_TOP"
  say "✓ Unwatched $REPO_TOP (hooks removed)."
  exit 0
fi

# ── Install the managed hook script ──────────────────────────────────────────
mkdir -p "$HOOKS_DIR" "$VAULT/.vault-meta"
cat > "$MANAGED" <<EOF
#!/usr/bin/env bash
# Managed by claude-obsidian /wiki-code-watch — do not edit.
# Enqueues this commit's changed paths into the vault's code-sync queue, then
# (if this repo is in autonomous mode) kicks a debounced background sync.
VAULT="$VAULT"
REPO="\$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
SHA="\$(git rev-parse HEAD 2>/dev/null)" || exit 0
[ -n "\$REPO" ] && [ -n "\$SHA" ] || exit 0
python3 "\$VAULT/scripts/code-sync-check.py" --enqueue --repo "\$REPO" --commit "\$SHA" >/dev/null 2>&1 || true
if [ -x "\$VAULT/bin/code-sync-launch.sh" ]; then
  nohup bash "\$VAULT/bin/code-sync-launch.sh" "\$REPO" >/dev/null 2>&1 &
fi
exit 0
EOF
chmod +x "$MANAGED"

# ── Chain it into each commit-ish hook (preserving any existing hook) ─────────
for ev in $HOOK_EVENTS; do
  HOOK_FILE="$HOOKS_DIR/$ev"
  if [ ! -e "$HOOK_FILE" ]; then
    cat > "$HOOK_FILE" <<EOF
#!/bin/sh
$MARK_BEGIN
"\$(dirname "\$0")/claude-obsidian-code-sync" || true
$MARK_END
EOF
    chmod +x "$HOOK_FILE"
  elif ! grep -qF "$MARK_BEGIN" "$HOOK_FILE"; then
    printf '\n%s\n%s\n%s\n' "$MARK_BEGIN" \
      '"$(dirname "$0")/claude-obsidian-code-sync" || true' "$MARK_END" >> "$HOOK_FILE"
    chmod +x "$HOOK_FILE"
  fi
done

# ── Register in state ────────────────────────────────────────────────────────
python3 "$CSC" --register --repo "$REPO_TOP" --mode "$MODE"

say ""
say "═══ Code-watch installed ═══"
say "Repo:   $REPO_TOP"
say "Vault:  $VAULT"
say "Drain:  $MODE"
say ""
if [ "$MODE" = "autonomous" ]; then
  say "Autonomous drain is ON. On each commit the hook debounces and launches a detached"
  say "headless 'claude -p' sync. Requires ANTHROPIC_API_KEY in the commit environment;"
  say "without it, commits still enqueue and you drain in-session."
else
  say "In-session drain (default). Each commit enqueues changed paths; the next Claude"
  say "session surfaces the drift and you run /wiki-code-ingest --sync."
  say "Switch to autonomous later: re-run with --autonomous."
fi
say ""
say "Remove with: bash bin/setup-code-watch.sh \"$REPO_TOP\" --unwatch"
