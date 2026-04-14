#!/usr/bin/env bash
# claude-obsidian: claude code directory sync script
# Creates symlinks in .claude/ for Claude Code's agent discovery.
# This script targets *nix/macOS environments where symlinks are standard.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="$REPO_ROOT/.claude"

echo "Syncing Claude Code directories to .claude/..."

mkdir -p "$CLAUDE_DIR"

cd "$CLAUDE_DIR"

# Use relative symlinks so they remain valid if the vault is moved.
# The -n flag ensures we don't nest symlinks if they already exist.
# The -f flag forces an overwrite if the symlink needs updating.
ln -snf ../skills skills
ln -snf ../commands commands

echo "✓ Claude Code directories synced."
