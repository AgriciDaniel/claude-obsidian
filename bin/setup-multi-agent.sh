#!/usr/bin/env bash
# Install portable skill links without overwriting existing host configuration.

set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
MODE="dry-run"
WORKSPACE=""
declare -a HOSTS=()
HOST_COUNT=0

usage() {
  cat <<'EOF'
Usage: bin/setup-multi-agent.sh [--check|--dry-run|--apply]
       [--host codex|opencode|gemini|zcode|cursor|windsurf|all] [--workspace PATH]

Default: dry-run for Codex, OpenCode, and Gemini user-level per-skill links.
ZCode, Cursor and Windsurf are opt-in and require an explicit --host selection;
Cursor and Windsurf also require an explicit --workspace destination.
Existing files and links pointing elsewhere are never replaced.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check) MODE="check" ;;
    --dry-run) MODE="dry-run" ;;
    --apply) MODE="apply" ;;
    --host)
      [ "$#" -ge 2 ] || { echo "ERROR: --host requires a value" >&2; exit 2; }
      HOSTS+=("$2")
      HOST_COUNT=$((HOST_COUNT + 1))
      shift
      ;;
    --workspace)
      [ "$#" -ge 2 ] || { echo "ERROR: --workspace requires a path" >&2; exit 2; }
      WORKSPACE="$2"
      shift
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

[ -d "$SKILLS_DIR" ] || { echo "ERROR: missing skills directory: $SKILLS_DIR" >&2; exit 2; }

if [ "$HOST_COUNT" -eq 0 ]; then
  HOSTS=(codex opencode gemini)
fi

expanded=()
for host in "${HOSTS[@]}"; do
  case "$host" in
    all) expanded+=(codex opencode gemini cursor windsurf) ;;
    codex|opencode|gemini|zcode|cursor|windsurf) expanded+=("$host") ;;
    *) echo "ERROR: unsupported host: $host" >&2; exit 2 ;;
  esac
done

if [ -n "$WORKSPACE" ]; then
  WORKSPACE="$(cd "$WORKSPACE" 2>/dev/null && pwd)" || {
    echo "ERROR: workspace is not an existing directory" >&2
    exit 2
  }
fi

status=0
seen=" "

inspect_link() {
  local host="$1"
  local source="$2"
  local destination="$3"
  local confinement_root="${4:-}"
  local parent
  parent="$(dirname "$destination")"

  if [ -L "$destination" ]; then
    local existing
    existing="$(readlink "$destination")"
    if [ "$existing" = "$source" ]; then
      echo "READY $host $destination"
      return
    fi
    echo "CONFLICT $host $destination points to $existing" >&2
    status=2
    return
  fi
  if [ -e "$destination" ]; then
    echo "CONFLICT $host $destination already exists" >&2
    status=2
    return
  fi
  if [ -n "$confinement_root" ]; then
    local relative cursor component
    case "$parent/" in
      "$confinement_root/"*) relative="${parent#"$confinement_root"/}" ;;
      *)
        echo "CONFLICT $host parent escapes workspace: $parent" >&2
        status=2
        return
        ;;
    esac
    cursor="$confinement_root"
    local -a components=()
    IFS='/' read -r -a components <<< "$relative"
    for component in "${components[@]}"; do
      [ -n "$component" ] || continue
      cursor="$cursor/$component"
      if [ -L "$cursor" ]; then
        echo "CONFLICT $host parent is a symlink: $cursor" >&2
        status=2
        return
      fi
      if [ -e "$cursor" ]; then
        if [ ! -d "$cursor" ]; then
          echo "CONFLICT $host parent is not a directory: $cursor" >&2
          status=2
          return
        fi
      elif [ "$MODE" = "apply" ]; then
        if ! mkdir "$cursor"; then
          echo "CONFLICT $host cannot create confined parent: $cursor" >&2
          status=2
          return
        fi
      else
        continue
      fi
      if [ -e "$cursor" ]; then
        if [ -L "$cursor" ] || [ ! -d "$cursor" ]; then
          echo "CONFLICT $host parent changed during install: $cursor" >&2
          status=2
          return
        fi
      fi
    done
  fi
  if [ "$MODE" = "apply" ]; then
    if [ -z "$confinement_root" ]; then
      mkdir -p "$parent"
    fi
    ln -s "$source" "$destination"
    echo "CREATED $host $destination"
  else
    echo "PLANNED $host $destination"
    if [ "$MODE" = "check" ] && [ "$status" -eq 0 ]; then
      status=1
    fi
  fi
}

for host in "${expanded[@]}"; do
  case "$seen" in
    *" $host "*) continue ;;
  esac
  seen="$seen$host "
  case "$host" in
    codex) destination_root="$HOME/.agents/skills" ;;
    opencode) destination_root="$HOME/.config/opencode/skills" ;;
    gemini) destination_root="$HOME/.gemini/skills" ;;
    zcode) destination_root="$HOME/.zcode/skills" ;;
    cursor|windsurf)
      if [ -z "$WORKSPACE" ]; then
        echo "ERROR: --host $host requires --workspace PATH" >&2
        status=2
        continue
      fi
      destination_root="$WORKSPACE/.$host/skills"
      ;;
  esac
  for source in "$SKILLS_DIR"/*; do
    [ -d "$source" ] || continue
    [ -f "$source/SKILL.md" ] || continue
    skill_name="$(basename "$source")"
    confinement_root=""
    case "$host" in
      cursor|windsurf) confinement_root="$WORKSPACE" ;;
    esac
    inspect_link "$host" "$source" "$destination_root/$skill_name" "$confinement_root"
  done
done

if [ "$MODE" = "dry-run" ]; then
  echo "Dry run only. Repeat with --apply to create the planned links."
fi
exit "$status"
