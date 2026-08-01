#!/usr/bin/env bash
# Checks if wiki/_claude/observations.md is >24h stale and emits a reminder.
# Uses .claude/last-observation.json as source of truth.

VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$VAULT_DIR/.claude/last-observation.json"

[ ! -f "$STATE" ] && exit 0

# Extract last_run value (works without jq)
last_run=$(grep -oE '"last_run"[[:space:]]*:[[:space:]]*"[^"]*"' "$STATE" 2>/dev/null | sed -E 's/.*"([^"]*)"$/\1/')

if [ -z "$last_run" ] || [ "$last_run" = "null" ]; then
  echo "OBSERVATIONS: notebook has never been generated — run /analyze-patterns or say \"analyze my patterns\" to create the first pass."
  exit 0
fi

# Convert ISO timestamp to epoch seconds
last_epoch=$(date -d "$last_run" +%s 2>/dev/null)
now_epoch=$(date +%s)

# If date parsing failed, skip silently
[ -z "$last_epoch" ] && exit 0

age_seconds=$((now_epoch - last_epoch))
age_hours=$((age_seconds / 3600))

if [ "$age_hours" -ge 24 ]; then
  echo "OBSERVATIONS: notebook is ${age_hours}h stale — run /analyze-patterns to refresh Claude's behavioral observations of the user."
fi
