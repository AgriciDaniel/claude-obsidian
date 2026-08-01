#!/usr/bin/env bash
# Checks .claude/learn-queue.json for pending preference reviews
VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
QUEUE="$VAULT_DIR/.claude/learn-queue.json"

[ ! -f "$QUEUE" ] && exit 0

# Count pending items without requiring jq — count occurrences of "status": "pending"
count=$(grep -c '"status"[[:space:]]*:[[:space:]]*"pending"' "$QUEUE" 2>/dev/null)
[ -z "$count" ] && count=0

if [ "$count" -gt 0 ]; then
  echo "LEARN: $count preference(s) pending review — say \"review learnings\" to walk through the queue."
fi
