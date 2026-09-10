#!/usr/bin/env bash
# Compatibility entry point for dry-run-first DragonScale state provisioning.

set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$PLUGIN_ROOT/scripts/claude-obsidian.py"
VAULT=""
APPLY=false
CHECK=false
GENERATED_AT=""
APPROVED_PLAN_SHA256=""

usage() {
  cat <<'EOF'
Usage: scripts/setup-dragonscale.sh [--vault PATH] [--check] [--apply]
                                [--generated-at ISO-UTC]
                                [--approved-plan-sha256 SHA256]

The default prints a create-only transaction plan. --apply creates only missing
address/tiling compatibility state. Existing values and raw manifests are never
replaced. This does not install, probe, or download Ollama or any model.
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

if $CHECK && $APPLY; then
  echo "ERROR: --check cannot be combined with --apply" >&2
  exit 2
fi
if $CHECK && [ -n "$APPROVED_PLAN_SHA256" ]; then
  echo "ERROR: --check cannot be combined with --approved-plan-sha256" >&2
  exit 2
fi

arguments=(extension dragonscale)
[ -n "$VAULT" ] && arguments+=(--vault "$VAULT")
$APPLY && arguments+=(--apply)
[ -n "$APPROVED_PLAN_SHA256" ] && arguments+=(--approved-plan-sha256 "$APPROVED_PLAN_SHA256")
[ -n "$GENERATED_AT" ] && arguments+=(--generated-at "$GENERATED_AT")

if $CHECK; then
  arguments+=(--check)
fi
exec python3 "$CLI" "${arguments[@]}"
