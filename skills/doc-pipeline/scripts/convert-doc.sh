#!/usr/bin/env bash
# convert-doc.sh — Stage 1 of the doc→ingest pipeline (agentic-knowledge-management).
#
# Deterministic RAW conversion of a source document to Markdown via `markit`,
# with format pre-handling for legacy/macro formats and an optional `pandoc`
# reference output used by the QC stage to measure conversion fidelity.
#
# This script does NO judgement work. It only produces bytes. All quality
# control, annotation, and approval happen in later stages (see SKILL.md).
#
# Usage:
#   "$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/convert-doc.sh" <source-file> [--out-dir DIR] [--no-ref] [--keep-images]
#
# Output (relative to the current vault root):
#   <out-dir>/<slug>.md             raw markdown (markit)
#   <out-dir>/_ref/<slug>.ref.md    pandoc reference (docx/doc/html/epub only)
#
# Defaults: out-dir = <vault>/.raw/_staging   (override with --out-dir for custom layouts,
#           e.g. a vault that stages under .raw/training/_staging)
#
# Format handling:
#   .docx .pdf .pptx .xlsx .html .epub .csv ...  → markit directly
#   .doc   (legacy OLE2)  → textutil → .docx → markit   (+ pandoc reference)
#   .pptm  (macro PPTX)   → copied to .pptx            → markit
#   .xls   (legacy)       → attempted directly, warns if unsupported
set -euo pipefail

# ---- vault root = current working tree (NOT the plugin dir) ----
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ---- args ----
SRC="${1:?usage: convert-doc.sh <source-file> [--out-dir DIR] [--no-ref] [--keep-images]}"
shift || true
OUT_DIR="$ROOT/.raw/_staging"
MAKE_REF=1
KEEP_IMAGES=0
while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir)     OUT_DIR="$2"; shift 2;;
    --no-ref)      MAKE_REF=0; shift;;
    --keep-images) KEEP_IMAGES=1; shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[ -f "$SRC" ] || { echo "ERROR: source not found: $SRC" >&2; exit 1; }
command -v markit >/dev/null || { echo "ERROR: markit not installed (npm i -g markit-ai / brew install markit?)" >&2; exit 1; }

# ---- derive a clean slug from the filename ----
base="$(basename "$SRC")"
stem="${base%.*}"
ext="$(printf '%s' "${base##*.}" | tr '[:upper:]' '[:lower:]')"
slug="$(printf '%s' "$stem" \
  | tr '[:upper:]' '[:lower:]' \
  | tr ' _' '--' \
  | sed -E 's/[^a-z0-9äöüß-]+//g; s/-+/-/g; s/^-//; s/-$//')"
[ -n "$slug" ] || slug="doc"

mkdir -p "$OUT_DIR" "$OUT_DIR/_ref"
OUT="$OUT_DIR/$slug.md"
REF="$OUT_DIR/_ref/$slug.ref.md"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/markit-conv.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# ---- normalize source into a markit-friendly file ----
markit_src="$SRC"
pre=""
case "$ext" in
  doc)
    # Legacy Word (OLE2): neither markit nor pandoc read it. textutil → docx (macOS).
    # Shell redirect (not -output) avoids the macOS provenance flag blocking textutil.
    if command -v textutil >/dev/null; then
      textutil -convert docx -stdout "$SRC" > "$WORK/$slug.docx"
      markit_src="$WORK/$slug.docx"; pre="textutil .doc→.docx"
    elif command -v libreoffice >/dev/null; then
      libreoffice --headless --convert-to docx --outdir "$WORK" "$SRC" >/dev/null 2>&1
      markit_src="$WORK/$stem.docx"; pre="libreoffice .doc→.docx"
    else
      echo "ERROR: .doc needs textutil (macOS) or libreoffice." >&2; exit 1
    fi
    ;;
  pptm)
    cp "$SRC" "$WORK/$slug.pptx"; markit_src="$WORK/$slug.pptx"; pre="copy .pptm→.pptx"
    ;;
  xls)
    echo "WARN: legacy .xls may be unsupported by markit; attempting directly." >&2
    pre="legacy .xls (best effort)"
    ;;
esac

# ---- primary conversion (markit) ----
# NOTE: markit's -q/-i/-o are GLOBAL options and must precede the source.
# The `convert` subcommand form silently ignores -o, so we use the default command.
echo "→ markit convert: $base${pre:+  [$pre]}"
markit -q -i "$WORK/img" -o "$OUT" "$markit_src" \
  || { echo "ERROR: markit failed on $base" >&2; exit 1; }

# ---- clean up broken/temporary local image links ----
# markit extracts images to a temp dir we discard, leaving dead absolute paths.
# Replace them with a REVIEW marker that preserves the alt text so the QC stage
# can decide whether the image mattered.
if [ "$KEEP_IMAGES" -eq 0 ] && [ -s "$OUT" ]; then
  perl -i -pe 's{!\[([^\]]*)\]\((?!https?://)[^)]*\)}{<!-- REVIEW[image|info]: Bild im Original entfernt (alt: "$1") - bei Relevanz manuell ergaenzen -->}g' "$OUT"
fi

# ---- reference conversion (pandoc) for the fidelity diff ----
if [ "$MAKE_REF" -eq 1 ] && command -v pandoc >/dev/null; then
  ref_src="" ; ref_fmt=""
  case "$ext" in
    docx)     ref_src="$SRC";              ref_fmt="docx";;
    doc)      ref_src="$markit_src";       ref_fmt="docx";;
    html|htm) ref_src="$SRC";              ref_fmt="html";;
    epub)     ref_src="$SRC";              ref_fmt="epub";;
  esac
  if [ -n "$ref_src" ]; then
    if pandoc -f "$ref_fmt" -t markdown "$ref_src" -o "$REF" 2>/dev/null; then
      echo "→ pandoc reference: ${REF#$ROOT/}"
    else
      echo "WARN: pandoc reference failed (non-fatal)" >&2; rm -f "$REF"
    fi
  else
    echo "ℹ no pandoc reference for .$ext — QC must compare raw MD vs. the original"
  fi
fi

# ---- summary ----
words="$(wc -w < "$OUT" | tr -d ' ')"; lines="$(wc -l < "$OUT" | tr -d ' ')"
echo "✓ raw markdown: ${OUT#$ROOT/}  (${lines} lines, ${words} words)"
[ -f "$REF" ] && echo "  reference:    ${REF#$ROOT/}"
echo
echo "Next: QC stage annotates this file in place (see the doc-pipeline skill), then"
echo "      set 'status: approved' in its PIPELINE-REVIEW header and run finalize-md.sh."
