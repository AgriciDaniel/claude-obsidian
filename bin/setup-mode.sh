#!/usr/bin/env bash
# setup-mode.sh — interactive methodology mode selector (v1.8+).
#
# Sets the vault's .vault-meta/mode.json and optionally seeds template
# folders for the chosen mode. Idempotent — safe to re-run to switch modes.
# Existing files are NOT auto-migrated; the new mode only affects future
# filing operations.
#
# Usage:
#   bash bin/setup-mode.sh                    # interactive
#   bash bin/setup-mode.sh --mode lyt          # non-interactive (CI / scripts)
#   bash bin/setup-mode.sh --mode generic --no-seed
#   bash bin/setup-mode.sh --check             # diagnostics only, no write
#
# Flags:
#   --mode MODE     Skip the interactive prompt; pick MODE directly.
#                   Valid: generic | lyt | para | zettelkasten | gtd
#   --no-seed       Skip the optional folder-seeding step
#   --check         Print current mode + diagnostics; write nothing
#
# Exit codes:
#   0 — success
#   2 — usage error
#   3 — invalid mode string

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="$(dirname "$SCRIPT_DIR")"
WM="$VAULT/scripts/wiki-mode.py"

# Detect Python executable — test actual execution, not just presence.
# Windows has a fake python3.exe stub that opens the Store; skip it.
_pick_python() {
  for candidate in "py -X utf8" python3 python; do
    if $candidate -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
      echo "$candidate"; return 0
    fi
  done
  return 1
}
PY=$(_pick_python) || { echo "ERR: no working Python interpreter found" >&2; exit 3; }

REQUESTED_MODE=""
NO_SEED=false
CHECK_ONLY=false

while [ $# -gt 0 ]; do
  case "$1" in
    --mode)     REQUESTED_MODE="${2:-}"; shift 2 ;;
    --no-seed)  NO_SEED=true; shift ;;
    --check)    CHECK_ONLY=true; shift ;;
    -h|--help)
      sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "ERR: unknown flag: $1" >&2; exit 2 ;;
  esac
done

say() { printf '%s\n' "$@"; }
warn() { printf 'WARN: %s\n' "$@" >&2; }

say "═══ wiki-mode setup (v1.8+) ═══"
say "Vault: $VAULT"
say ""

# ── Sanity check ────────────────────────────────────────────────────────────
if [ ! -x "$WM" ]; then
  warn "scripts/wiki-mode.py not found or not executable: $WM"
  exit 3
fi

# ── Diagnostics ─────────────────────────────────────────────────────────────
CURRENT=$($PY "$WM" get 2>/dev/null || echo "generic")
say "Current mode: $CURRENT"

if $CHECK_ONLY; then
  say ""
  $PY "$WM" config
  exit 0
fi

# ── Mode selection ──────────────────────────────────────────────────────────
if [ -z "$REQUESTED_MODE" ]; then
  say ""
  say "Pick a methodology mode for this vault:"
  say "  1) generic       — v1.7 default; wiki/sources/, entities/, concepts/"
  say "  2) lyt           — Linking Your Thinking (MOCs + atomic notes flat under wiki/notes/)"
  say "  3) para          — Projects / Areas / Resources / Archives"
  say "  4) zettelkasten  — timestamped IDs, flat under wiki/, dense linking"
  say "  5) gtd           — GTD (David Allen): today/backlog/waiting/someday/reference buckets"
  say ""
  printf "Pick [1-5, default 1]: "
  read -r choice || choice="1"
  case "${choice:-1}" in
    1|generic)       REQUESTED_MODE="generic" ;;
    2|lyt)           REQUESTED_MODE="lyt" ;;
    3|para)          REQUESTED_MODE="para" ;;
    4|zettelkasten)  REQUESTED_MODE="zettelkasten" ;;
    5|gtd)           REQUESTED_MODE="gtd" ;;
    *) warn "invalid choice: $choice"; exit 3 ;;
  esac
fi

case "$REQUESTED_MODE" in
  generic|lyt|para|zettelkasten|gtd) ;;
  *) warn "invalid mode: $REQUESTED_MODE (valid: generic|lyt|para|zettelkasten|gtd)"; exit 3 ;;
esac

# ── Write the mode ──────────────────────────────────────────────────────────
$PY "$WM" set "$REQUESTED_MODE"

# ── Seed template folders (optional) ────────────────────────────────────────
if ! $NO_SEED; then
  if [ -t 0 ]; then
    say ""
    printf "Seed template folders for %s? [y/N]: " "$REQUESTED_MODE"
    read -r seed || seed="n"
  else
    seed="n"
  fi
  case "${seed:-n}" in
    [yY]|[yY][eE][sS])
      case "$REQUESTED_MODE" in
        lyt)
          mkdir -p "$VAULT/wiki/mocs" "$VAULT/wiki/notes"
          say "✓ Created wiki/mocs/ and wiki/notes/"
          ;;
        para)
          mkdir -p "$VAULT/wiki/projects/inbox" "$VAULT/wiki/areas" \
                   "$VAULT/wiki/resources/incoming" "$VAULT/wiki/resources/people" \
                   "$VAULT/wiki/resources/concepts" "$VAULT/wiki/archives"
          say "✓ Created PARA folder structure: projects/{inbox}/, areas/, resources/{incoming,people,concepts}/, archives/"
          ;;
        zettelkasten)
          say "✓ Zettelkasten uses no subfolders; all notes file flat under wiki/"
          ;;
        generic)
          mkdir -p "$VAULT/wiki/sources" "$VAULT/wiki/entities" \
                   "$VAULT/wiki/concepts" "$VAULT/wiki/sessions"
          say "✓ Created generic folders: sources/, entities/, concepts/, sessions/"
          ;;
        gtd)
          mkdir -p "$VAULT/wiki/gtd/today" "$VAULT/wiki/gtd/backlog" \
                   "$VAULT/wiki/gtd/waiting" "$VAULT/wiki/gtd/someday" \
                   "$VAULT/wiki/gtd/reference"
          say "✓ Created GTD folder structure: gtd/{today,backlog,waiting,someday,reference}/"
          ;;
      esac
      ;;
    *) say "(skipped folder seeding)" ;;
  esac
fi

say ""
say "═══ Done. Mode is: $REQUESTED_MODE ═══"
say ""
say "Other skills (wiki-ingest, save, autoresearch) will consult this mode automatically."
say "Existing files are NOT auto-migrated. New files will follow the new mode's conventions."
say ""
say "To switch modes later: re-run \`bash bin/setup-mode.sh\`."
