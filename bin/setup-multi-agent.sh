#!/usr/bin/env bash
# vault-os: multi-agent skill installer
# Symlinks the skills/ directory into each AI agent's expected location.
# Idempotent: safe to run multiple times.
#
# Supported agents:
#   - Claude Code    : auto-discovered via .claude-plugin/ (no symlink needed)
#   - Cursor         : auto-discovered via .cursor-plugin/ when installed from
#                      the marketplace; the .cursor/skills symlink is only
#                      created for in-repo dev work (see CURSOR_DEV_SYMLINK).
#   - Codex CLI      : symlink to ~/.codex/skills/vault-os
#   - OpenCode       : symlink to ~/.opencode/skills/vault-os
#   - Gemini CLI     : symlink to ~/.gemini/skills/vault-os
#   - Windsurf       : symlink to .windsurf/skills (in repo)
#
# Bootstrap files (AGENTS.md, GEMINI.md, rules/vault-os.mdc, .windsurf/rules/,
# .github/copilot-instructions.md) are already committed in the repo.
# This script just wires up the skills directory.
#
# Set CURSOR_DEV_SYMLINK=1 to force-create the .cursor/skills symlink even
# when .cursor-plugin/plugin.json exists. Useful when you're editing skills
# in this repo and want them picked up by the local Cursor agent without
# going through the plugin loader.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "ERROR: $SKILLS_DIR does not exist. Are you running this from the claude-obsidian repo?"
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

echo "claude-obsidian: multi-agent skill installer"
echo "Repo: $REPO_ROOT"
echo

# Codex CLI
link_if_missing "$SKILLS_DIR" "$HOME/.codex/skills/vault-os" "Codex CLI"

# OpenCode
link_if_missing "$SKILLS_DIR" "$HOME/.opencode/skills/vault-os" "OpenCode"

# Gemini CLI
link_if_missing "$SKILLS_DIR" "$HOME/.gemini/skills/vault-os" "Gemini CLI"

# Cursor (workspace-local).
# Skip the symlink when the repo ships .cursor-plugin/plugin.json AND the user
# hasn't explicitly opted into the dev symlink. With the plugin manifest in
# place, Cursor discovers skills/ on its own once installed from the
# marketplace, and a stale .cursor/skills symlink can shadow that.
if [ -f "$REPO_ROOT/.cursor-plugin/plugin.json" ] && [ "${CURSOR_DEV_SYMLINK:-0}" != "1" ]; then
  echo -e "${GRAY}[Cursor] .cursor-plugin/plugin.json found — skipping .cursor/skills symlink (set CURSOR_DEV_SYMLINK=1 to force).${NC}"
else
  link_if_missing "$SKILLS_DIR" "$REPO_ROOT/.cursor/skills" "Cursor"
fi

# Windsurf (workspace-local)
link_if_missing "$SKILLS_DIR" "$REPO_ROOT/.windsurf/skills" "Windsurf"

echo
echo -e "${GREEN}Done.${NC} Bootstrap files (AGENTS.md, GEMINI.md, rules/vault-os.mdc, .windsurf/rules/, .github/copilot-instructions.md) are already in this repo."
echo
echo "To verify each agent picks up the skills:"
echo "  - Claude Code: open the project, type /wiki"
echo "  - Cursor:      install via marketplace (saixso/vault-os) or set CURSOR_DEV_SYMLINK=1 and rerun"
echo "  - Codex CLI:   codex --list-skills | grep vault-os"
echo "  - Windsurf:    open in Cascade, ask 'what skills do you have?'"
echo "  - Gemini CLI:  gemini --list-skills (if supported)"
