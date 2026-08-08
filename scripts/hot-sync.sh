#!/usr/bin/env bash
# hot-sync.sh — regenerate wiki/hot.md from ground truth.
#
# Replaces discretionary LLM "please update hot.md" asks with a deterministic
# rewrite. FACTS (everything outside ACTIVE-THREADS markers) is regenerated
# every run. The Active Threads block between markers is preserved verbatim.
#
# Usage:
#   bash scripts/hot-sync.sh [--force] [vault-root]
#
# Skips the write when Ground Truth is unchanged (fingerprint match), so
# SessionStart hooks do not dirty the tree every open. Pass --force to rewrite.
#
# Exit codes:
#   0 — wrote wiki/hot.md, or skipped (unchanged)
#   2 — usage / missing vault
#   3 — output exceeded soft line budget (still wrote; stderr warning)

set -euo pipefail

FORCE=0
VAULT_ROOT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --force|-f) FORCE=1; shift ;;
    -h|--help)
      echo "Usage: bash scripts/hot-sync.sh [--force] [vault-root]"
      exit 0
      ;;
    *)
      if [ -n "$VAULT_ROOT" ]; then
        echo "hot-sync: unexpected argument: $1" >&2
        exit 2
      fi
      VAULT_ROOT="$1"
      shift
      ;;
  esac
done

if [ -z "$VAULT_ROOT" ]; then
  VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
else
  VAULT_ROOT="$(cd "$VAULT_ROOT" && pwd)"
fi

WIKI_DIR="${VAULT_ROOT}/wiki"
HOT_FILE="${WIKI_DIR}/hot.md"
PLUGIN_JSON="${VAULT_ROOT}/.claude-plugin/plugin.json"
SKILLS_DIR="${VAULT_ROOT}/skills"
DOMAINS_DIR="${WIKI_DIR}/domains"
LOG_FILE="${WIKI_DIR}/log.md"
META_DIR="${VAULT_ROOT}/.vault-meta"
FP_FILE="${META_DIR}/hot-sync.sha"

if [ ! -d "$WIKI_DIR" ]; then
  echo "hot-sync: no wiki/ under ${VAULT_ROOT}" >&2
  exit 2
fi

# --- preserve Active Threads (if any) ---
ACTIVE_THREADS=""
if [ -f "$HOT_FILE" ]; then
  ACTIVE_THREADS="$(
    awk '
      /<!-- ACTIVE-THREADS:START -->/ { in_block=1; next }
      /<!-- ACTIVE-THREADS:END -->/ { in_block=0; next }
      in_block { print }
    ' "$HOT_FILE"
  )"
fi

if [ -z "${ACTIVE_THREADS//[[:space:]]/}" ]; then
  ACTIVE_THREADS="_(none yet — add short bullets between the markers)_"
fi

# --- ground truth ---
NOW="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
TODAY="$(date -u '+%Y-%m-%d')"

VERSION="unknown"
if [ -f "$PLUGIN_JSON" ] && command -v python3 >/dev/null 2>&1; then
  VERSION="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('version','unknown'))" "$PLUGIN_JSON" 2>/dev/null || echo unknown)"
elif [ -f "$PLUGIN_JSON" ]; then
  VERSION="$(grep -E '"version"' "$PLUGIN_JSON" | head -1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')"
fi

SKILL_COUNT=0
if [ -d "$SKILLS_DIR" ]; then
  SKILL_COUNT="$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
fi

DOMAIN_LIST="(none — run /teams-new to create wiki/domains/)"
if [ -d "$DOMAINS_DIR" ]; then
  DOMAIN_NAMES="$(find "$DOMAINS_DIR" -maxdepth 1 -name '*.md' ! -name '_index.md' -exec basename {} .md \; 2>/dev/null | sort | tr '\n' ', ' | sed 's/, $//')"
  if [ -n "$DOMAIN_NAMES" ]; then
    DOMAIN_LIST="$DOMAIN_NAMES"
  fi
fi

BRANCH="n/a"
HEAD_SHA="n/a"
DIRTY="clean"
RECENT_COMMITS="(not a git repo)"
if [ -d "${VAULT_ROOT}/.git" ] || git -C "$VAULT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  BRANCH="$(git -C "$VAULT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo n/a)"
  HEAD_SHA="$(git -C "$VAULT_ROOT" rev-parse --short HEAD 2>/dev/null || echo n/a)"
  if [ -n "$(git -C "$VAULT_ROOT" status --porcelain 2>/dev/null)" ]; then
    DIRTY="dirty"
  fi
  RECENT_COMMITS="$(git -C "$VAULT_ROOT" log --oneline -5 2>/dev/null || echo '(no commits)')"
fi

LOG_TAIL="(no log.md)"
if [ -f "$LOG_FILE" ]; then
  LOG_TAIL="$(grep -E '^## \[' "$LOG_FILE" | head -3 || echo '(no dated entries)')"
fi

PAGE_COUNTS=""
for sub in concepts entities sources questions comparisons meta folds domains; do
  if [ -d "${WIKI_DIR}/${sub}" ]; then
    n="$(find "${WIKI_DIR}/${sub}" -type f -name '*.md' ! -name '_index.md' 2>/dev/null | wc -l | tr -d ' ')"
    PAGE_COUNTS="${PAGE_COUNTS}${sub}=${n} "
  fi
done
PAGE_COUNTS="$(echo "$PAGE_COUNTS" | sed 's/[[:space:]]*$//')"

# Fingerprint excludes timestamps and dirty flag so SessionStart is stable mid-edit.
FP_SRC=$(printf '%s\0' "$VERSION" "$BRANCH" "$HEAD_SHA" "$SKILL_COUNT" "$DOMAIN_LIST" "$PAGE_COUNTS" "$RECENT_COMMITS" "$LOG_TAIL")
if command -v shasum >/dev/null 2>&1; then
  FINGERPRINT="$(printf '%s' "$FP_SRC" | shasum -a 256 | awk '{print $1}')"
else
  FINGERPRINT="$(printf '%s' "$FP_SRC" | sha256sum | awk '{print $1}')"
fi

if [ "$FORCE" -eq 0 ] && [ -f "$HOT_FILE" ] && [ -f "$FP_FILE" ] && [ "$(cat "$FP_FILE")" = "$FINGERPRINT" ]; then
  if grep -q 'generator: hot-sync' "$HOT_FILE" 2>/dev/null; then
    echo "hot-sync: unchanged (version=${VERSION}, head=${HEAD_SHA})"
    exit 0
  fi
fi

# Soft budget: ~500 tokens ≈ ~40 short lines. Warn if we blow past 60 lines.
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

{
  cat <<EOF
---
type: meta
title: "Hot Cache"
updated: ${NOW}
tags:
  - meta
  - hot-cache
status: evergreen
generator: hot-sync
---

# Recent Context

Navigation: [[index]] | [[log]] | [[overview]]

## Last Updated

${TODAY} (hot-sync). Regenerated from git + plugin.json. Do not hand-edit the Ground Truth block; edit Active Threads only.

## Ground Truth

- **Version**: ${VERSION}
- **Repo**: ${VAULT_ROOT}
- **Branch**: ${BRANCH} @ ${HEAD_SHA} (${DIRTY})
- **Skills**: ${SKILL_COUNT}
- **Domains**: ${DOMAIN_LIST}
- **Wiki pages**: ${PAGE_COUNTS:-n/a}

### Recent commits

\`\`\`
${RECENT_COMMITS}
\`\`\`

### Recent log headers

\`\`\`
${LOG_TAIL}
\`\`\`

## Active Threads

<!-- ACTIVE-THREADS:START -->
${ACTIVE_THREADS}
<!-- ACTIVE-THREADS:END -->

## Notes

- This file is a cache. Ground Truth is owned by \`scripts/hot-sync.sh\`.
- Prefer \`/save\` for durable notes; prefer \`/hot-sync\` (or SessionStart) to refresh this file.
- Create real work domains with \`/teams-new\` before relying on \`/teams-sync\`.
EOF
} >"$TMP"

LINE_COUNT="$(wc -l <"$TMP" | tr -d ' ')"
mkdir -p "$META_DIR"
mv "$TMP" "$HOT_FILE"
printf '%s\n' "$FINGERPRINT" >"$FP_FILE"
trap - EXIT

echo "hot-sync: wrote ${HOT_FILE} (${LINE_COUNT} lines, version=${VERSION}, skills=${SKILL_COUNT})"

if [ "$LINE_COUNT" -gt 60 ]; then
  echo "hot-sync: warning: output is ${LINE_COUNT} lines (target ≤60 for ~500-token budget)" >&2
  exit 3
fi

exit 0
