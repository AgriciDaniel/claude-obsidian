#!/usr/bin/env bash
# Thin compatibility wrapper for the portable claude-obsidian vault workflow.
#
# This wrapper never creates, replaces, or removes vault content itself. It
# translates the legacy setup-vault flags into the canonical Python CLI, where
# dry-run planning, exact plan approval, and recoverable transactions live.
#
# Usage:
#   bash scripts/setup-vault.sh [--dry-run] [--init|--adopt] [--vault PATH|PATH]
#   bash scripts/setup-vault.sh --check [--vault PATH|PATH]
#   bash scripts/setup-vault.sh --apply --approved-plan-sha256 HASH \
#     --generated-at ISO-UTC --operation-id ID [--init|--adopt] [--vault PATH|PATH]
#   bash scripts/setup-vault.sh --dry-run --force --adopt [--vault PATH|PATH]
#
# Compatibility:
#   - preview is the default;
#   - a missing destination selects init, while an existing directory selects
#     adopt unless --init or --adopt is explicit;
#   - --force without an explicit mode retains the legacy meaning of apply;
#   - no path still means the caller's current working directory.

set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

MODE="preview"
MODE_EXPLICIT=false
ACTION="auto"
ACTION_EXPLICIT=false
FORCE=false
VAULT_INPUT=""
POSITIONAL_VAULT=""
APPROVED_PLAN_SHA256=""
GENERATED_AT=""
OPERATION_ID=""

usage() {
  sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'
}

fail_usage() {
  echo "ERR: $*" >&2
  usage >&2
  exit 2
}

set_mode() {
  local requested="$1"
  if $MODE_EXPLICIT && [ "$MODE" != "$requested" ]; then
    fail_usage "choose exactly one of --check, --dry-run, or --apply"
  fi
  MODE="$requested"
  MODE_EXPLICIT=true
}

set_action() {
  local requested="$1"
  if $ACTION_EXPLICIT && [ "$ACTION" != "$requested" ]; then
    fail_usage "choose exactly one of --init or --adopt"
  fi
  ACTION="$requested"
  ACTION_EXPLICIT=true
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check)
      set_mode "check"
      ;;
    --dry-run)
      set_mode "preview"
      ;;
    --apply)
      set_mode "apply"
      ;;
    --init)
      set_action "init"
      ;;
    --adopt)
      set_action "adopt"
      ;;
    --force)
      FORCE=true
      if ! $MODE_EXPLICIT; then
        MODE="apply"
      fi
      ;;
    --approved-plan-sha256)
      [ "$#" -ge 2 ] || fail_usage "--approved-plan-sha256 requires a value"
      [ -z "$APPROVED_PLAN_SHA256" ] || fail_usage \
        "--approved-plan-sha256 may be specified only once"
      APPROVED_PLAN_SHA256="$2"
      shift
      ;;
    --generated-at)
      [ "$#" -ge 2 ] || fail_usage "--generated-at requires a value"
      [ -z "$GENERATED_AT" ] || fail_usage "--generated-at may be specified only once"
      GENERATED_AT="$2"
      shift
      ;;
    --operation-id)
      [ "$#" -ge 2 ] || fail_usage "--operation-id requires a value"
      [ -z "$OPERATION_ID" ] || fail_usage "--operation-id may be specified only once"
      OPERATION_ID="$2"
      shift
      ;;
    --vault)
      [ "$#" -ge 2 ] || fail_usage "--vault requires a path"
      [ -z "$VAULT_INPUT" ] || fail_usage "--vault may be specified only once"
      VAULT_INPUT="$2"
      shift
      ;;
    --vault=*)
      [ -z "$VAULT_INPUT" ] || fail_usage "--vault may be specified only once"
      VAULT_INPUT="${1#--vault=}"
      [ -n "$VAULT_INPUT" ] || fail_usage "--vault requires a path"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      [ "$#" -le 1 ] || fail_usage "only one positional vault path is accepted"
      if [ "$#" -eq 1 ]; then
        POSITIONAL_VAULT="$1"
      fi
      break
      ;;
    -*)
      fail_usage "unknown option: $1"
      ;;
    *)
      [ -z "$POSITIONAL_VAULT" ] || fail_usage \
        "only one positional vault path is accepted"
      POSITIONAL_VAULT="$1"
      ;;
  esac
  shift
done

if [ -n "$VAULT_INPUT" ] && [ -n "$POSITIONAL_VAULT" ]; then
  fail_usage "use either --vault or a positional vault path, not both"
fi

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE="$PLUGIN_ROOT/scripts/claude-obsidian.py"
VAULT="${VAULT_INPUT:-${POSITIONAL_VAULT:-$PWD}}"

if [ "$MODE" = "check" ]; then
  $ACTION_EXPLICIT && fail_usage "--check cannot be combined with --init or --adopt"
  $FORCE && fail_usage "--check cannot be combined with --force"
  [ -z "$APPROVED_PLAN_SHA256" ] || fail_usage \
    "--check cannot be combined with --approved-plan-sha256"
  [ -z "$GENERATED_AT" ] || fail_usage "--check cannot be combined with --generated-at"
  [ -z "$OPERATION_ID" ] || fail_usage "--check cannot be combined with --operation-id"
  exec python3 "$CORE" doctor --vault "$VAULT"
fi

if [ "$ACTION" = "auto" ]; then
  if [ -d "$VAULT" ]; then
    ACTION="adopt"
  else
    ACTION="init"
  fi
fi

COMMAND=(python3 "$CORE" "$ACTION" "$VAULT")
$FORCE && COMMAND+=(--force)
[ -z "$GENERATED_AT" ] || COMMAND+=(--generated-at "$GENERATED_AT")
[ -z "$OPERATION_ID" ] || COMMAND+=(--operation-id "$OPERATION_ID")

case "$MODE" in
  preview)
    [ -z "$APPROVED_PLAN_SHA256" ] || fail_usage \
      "--approved-plan-sha256 is accepted only with --apply"
    ;;
  apply)
    [ -n "$APPROVED_PLAN_SHA256" ] || fail_usage \
      "--apply requires --approved-plan-sha256 from the reviewed dry run"
    COMMAND+=(--approved-plan-sha256 "$APPROVED_PLAN_SHA256" --apply)
    ;;
  *)
    fail_usage "unsupported setup mode: $MODE"
    ;;
esac

exec "${COMMAND[@]}"
