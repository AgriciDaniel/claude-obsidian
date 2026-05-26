#!/usr/bin/env bash
# agentic-knowledge-management: multi-agent skill installer
# Symlinks the skills/ directory into each AI agent's expected location.
# Idempotent: safe to run multiple times.
#
# Supported agents:
#   - Claude Code    : auto-discovered via .claude-plugin/ (no symlink needed)
#   - Codex CLI      : symlink to ~/.codex/skills/agentic-knowledge-management
#   - OpenCode       : symlink to ~/.opencode/skills/agentic-knowledge-management
#   - Gemini CLI     : symlink to ~/.gemini/skills/agentic-knowledge-management
#   - Cursor         : symlink to .cursor/skills (in repo)
#   - Windsurf       : symlink to .windsurf/skills (in repo)
#
# Bootstrap files (AGENTS.md, GEMINI.md, .cursor/rules/, .windsurf/rules/,
# .github/copilot-instructions.md) are already committed in the repo.
# This script just wires up the skills directory.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "ERROR: $SKILLS_DIR does not exist. Are you running this from the agentic-knowledge-management repo?"
  exit 1
fi

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
NC='\033[0m'

link_if_missing() {
  local target="$1"
  local dest="$2"
  local agent_name="$3"

  mkdir -p "$(dirname "$dest")"

  if [ -L "$dest" ]; then
    local existing="$(readlink "$dest")"
    if [ "$existing" = "$target" ]; then
      echo -e "${GRAY}[$agent_name] already linked: $dest${NC}"
      return
    else
      echo -e "${YELLOW}[$agent_name] symlink exists but points elsewhere: $dest -> $existing (skipping, remove manually if you want to relink)${NC}"
      return
    fi
  fi

  if [ -e "$dest" ]; then
    echo -e "${YELLOW}[$agent_name] path exists and is not a symlink: $dest (skipping)${NC}"
    return
  fi

  ln -s "$target" "$dest"
  echo -e "${GREEN}[$agent_name] linked: $dest -> $target${NC}"
}

echo "agentic-knowledge-management: multi-agent skill installer"
echo "Repo: $REPO_ROOT"
echo

# Codex CLI
link_if_missing "$SKILLS_DIR" "$HOME/.codex/skills/agentic-knowledge-management" "Codex CLI"

# OpenCode
link_if_missing "$SKILLS_DIR" "$HOME/.opencode/skills/agentic-knowledge-management" "OpenCode"

# Gemini CLI
link_if_missing "$SKILLS_DIR" "$HOME/.gemini/skills/agentic-knowledge-management" "Gemini CLI"

# Cursor (workspace-local)
link_if_missing "$SKILLS_DIR" "$REPO_ROOT/.cursor/skills" "Cursor"

# Windsurf (workspace-local)
link_if_missing "$SKILLS_DIR" "$REPO_ROOT/.windsurf/skills" "Windsurf"

echo
echo -e "${GREEN}Done.${NC} Bootstrap files (AGENTS.md, GEMINI.md, .cursor/rules/, .windsurf/rules/, .github/copilot-instructions.md) are already in this repo."
echo
echo "To verify each agent picks up the skills:"
echo "  - Claude Code: open the project, type /wiki"
echo "  - Codex CLI:   codex --list-skills | grep agentic-knowledge-management"
echo "  - Cursor:      open the project, ask 'what skills do you have?'"
echo "  - Windsurf:    open in Cascade, ask the same"
echo "  - Gemini CLI:  gemini --list-skills (if supported)"
