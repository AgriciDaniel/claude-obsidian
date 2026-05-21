#!/usr/bin/env bash
# finalize-md.sh — Stage 4 of the doc→ingest pipeline (agentic-knowledge-management).
#
# Takes an APPROVED staging file (raw MD + inline review annotations) and emits
# a clean, ingest-ready Markdown: the <!-- PIPELINE-REVIEW ... --> header and all
# <!-- REVIEW[...] --> comments are stripped. The staging file is left untouched
# as the audit trail.
#
# Guard: refuses to run unless the PIPELINE-REVIEW header says `status: approved`
# (override with --force). This is the approval gate.
#
# Usage:
#   "$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/finalize-md.sh" <staging-file.md> [--out-dir DIR] [--force]
#
# Default out-dir = <vault>/.raw  (ingest-ready; picked up by the wiki-ingest skill)
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

SRC="${1:?usage: finalize-md.sh <staging-file.md> [--out-dir DIR] [--force]}"
shift || true
OUT_DIR="$ROOT/.raw"
FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir) OUT_DIR="$2"; shift 2;;
    --force)   FORCE=1; shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[ -f "$SRC" ] || { echo "ERROR: not found: $SRC" >&2; exit 1; }

# ---- approval gate ----
if [ "$FORCE" -eq 0 ]; then
  if ! grep -Eq '^[[:space:]]*status:[[:space:]]*approved' "$SRC"; then
    echo "✗ BLOCKED: '$(basename "$SRC")' is not approved." >&2
    echo "  Set 'status: approved' in its <!-- PIPELINE-REVIEW --> header (or use --force)." >&2
    exit 3
  fi
fi

base="$(basename "$SRC")"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/$base"

# ---- strip pipeline metadata + annotations, tidy whitespace ----
#  1) remove the multi-line <!-- PIPELINE-REVIEW ... --> header
#  2) remove every single-/multi-line <!-- REVIEW[...] ... --> annotation
#  3) collapse 3+ consecutive blank lines to a single blank line
#  4) drop leading blank lines
# NOTE: do NOT trim trailing whitespace — two trailing spaces are meaningful
#       Markdown hard line breaks and must survive into the ingest-ready file.
perl -0777 -pe '
  s/<!--\s*PIPELINE-REVIEW\b.*?-->\s*//s;
  s/[ \t]*<!--\s*REVIEW\[.*?\].*?-->[ \t]*\n?//gs;
  s/\n{3,}/\n\n/g;
  s/\A\n+//;
' "$SRC" > "$OUT"

remaining="$(grep -c -E '<!--\s*(PIPELINE-)?REVIEW' "$OUT" || true)"
words="$(wc -w < "$OUT" | tr -d ' ')"
echo "✓ ingest-ready: ${OUT#$ROOT/}  (${words} words)"
if [ "${remaining:-0}" -gt 0 ]; then
  echo "  ⚠ $remaining review marker(s) still present — inspect manually." >&2
fi
echo "  audit trail kept at: ${SRC#$ROOT/}"
