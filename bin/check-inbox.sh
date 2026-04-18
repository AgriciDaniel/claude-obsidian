#!/usr/bin/env bash
# Checks inbox/ for unprocessed notes (excludes README.md)
VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INBOX="$VAULT_DIR/inbox"

files=$(find "$INBOX" -maxdepth 1 -name "*.md" ! -name "README.md" 2>/dev/null)
count=$(echo "$files" | grep -c "\.md$" 2>/dev/null)
[ -z "$count" ] && count=0

if [ "$count" -gt 0 ]; then
  echo "INBOX: $count unprocessed note(s) in inbox/ — say \"process my inbox\" to classify and file them."
  echo "$files" | while read -r f; do
    echo "  - $(basename "$f")"
  done
fi
