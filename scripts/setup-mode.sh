#!/usr/bin/env bash
# Thin compatibility wrapper for transactional methodology configuration.

set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$PLUGIN_ROOT/scripts/claude-obsidian.py"
VAULT=""
MODE=""
APPLY=false
CHECK=false
GENERATED_AT=""
APPROVED_PLAN_SHA256=""

usage() {
  cat <<'EOF'
Usage: scripts/setup-mode.sh [--vault PATH] [--mode MODE] [--check] [--apply]
                         [--generated-at ISO-UTC]
                         [--approved-plan-sha256 SHA256]

MODE is generic, lyt, para, or zettelkasten. Without --apply, setting a mode
prints a complete transaction dry run. Without --mode, the current config is
shown. This command never moves existing notes or seeds folders implicitly.
Pin --generated-at for the preview, then repeat that exact value with the
reviewed --approved-plan-sha256 when applying the plan.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --vault)
      [ "$#" -ge 2 ] || { echo "ERROR: --vault requires a path" >&2; exit 2; }
      VAULT="$2"
      shift
      ;;
    --mode)
      [ "$#" -ge 2 ] || { echo "ERROR: --mode requires a value" >&2; exit 2; }
      MODE="$2"
      shift
      ;;
    --check) CHECK=true ;;
    --apply) APPLY=true ;;
    --approved-plan-sha256)
      [ "$#" -ge 2 ] || { echo "ERROR: --approved-plan-sha256 requires a value" >&2; exit 2; }
      APPROVED_PLAN_SHA256="$2"
      shift
      ;;
    --generated-at)
      [ "$#" -ge 2 ] || { echo "ERROR: --generated-at requires a value" >&2; exit 2; }
      GENERATED_AT="$2"
      shift
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

if $CHECK || [ -z "$MODE" ]; then
  if [ -n "$VAULT" ]; then
    exec python3 "$CLI" mode get --vault "$VAULT"
  fi
  exec python3 "$CLI" mode get
fi

case "$MODE" in
  generic|lyt|para|zettelkasten) ;;
  *) echo "ERROR: invalid mode: $MODE" >&2; exit 2 ;;
esac

arguments=(mode set "$MODE")
[ -n "$VAULT" ] && arguments+=(--vault "$VAULT")
$APPLY && arguments+=(--apply)
[ -n "$APPROVED_PLAN_SHA256" ] && arguments+=(--approved-plan-sha256 "$APPROVED_PLAN_SHA256")
[ -n "$GENERATED_AT" ] && arguments+=(--generated-at "$GENERATED_AT")
exec python3 "$CLI" "${arguments[@]}"
