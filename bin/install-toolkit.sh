#!/usr/bin/env bash
# install-toolkit.sh — Install the claude-obsidian toolchain to a persistent
# location (~/.claude/obsidian-toolkit/) and register it with Claude Code.
#
# After installation, the toolchain is fully decoupled from any vault project.
# You can delete the vault project and skills/scripts remain available.
#
# Usage:
#   bash bin/install-toolkit.sh                    # install toolkit only (from any vault clone)
#   bash bin/install-toolkit.sh --vault /path/to/vault   # install toolkit + set up vault
#   bash bin/install-toolkit.sh --uninstall        # remove toolkit + deregister
#   bash bin/install-toolkit.sh --help             # this message
#
# Design:
#   The toolchain lives at ~/.claude/obsidian-toolkit/ and contains:
#     scripts/   — shell + Python helpers (detect-transport, wiki-lock, allocate-address, etc.)
#     skills/    — 15+ Claude Code skill definitions (SKILL.md files)
#     agents/    — sub-agent prompt files
#     hooks/     — git hooks for auto-commit and locking
#     bin/       — setup scripts
#     commands/  — slash command definitions
#     docs/      — documentation
#     tests/     — test suite
#     assets/    — diagrams and images
#     .claude-plugin/ — plugin registry
#     CLAUDE.md  — orchestrator instructions
#     WIKI.md    — wiki instructions
#     AGENTS.md  — agent definitions
#     Makefile   — build automation
#
#   A vault project (wiki + .raw + .obsidian) can exist anywhere independently.
#   The vault is found via:
#     1. CLAUDE_OBSIDIAN_VAULT env var (highest priority)
#     2. .claude-obsidian-root marker file in current or parent directory
#     3. Current working directory (fallback)

set -euo pipefail

TOOLKIT_DIR="${CLAUDE_OBSIDIAN_TOOLKIT_HOME:-$HOME/.claude/obsidian-toolkit}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
header(){ echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }

# ── Parse args ────────────────────────────────────────────────────────────────
MODE="install"
VAULT_DIR=""

while [ $# -gt 0 ]; do
  case "$1" in
    --vault)
      VAULT_DIR="$2"
      shift 2
      ;;
    --uninstall)
      MODE="uninstall"
      shift
      ;;
    --help|-h)
      sed -n '3,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      error "unknown flag: $1 (try --help)"
      exit 1
      ;;
  esac
done

# ── Uninstall mode ─────────────────────────────────────────────────────────────
if [ "$MODE" = "uninstall" ]; then
  header "Uninstalling claude-obsidian toolchain"

  if [ -d "$TOOLKIT_DIR" ]; then
    rm -rf "$TOOLKIT_DIR"
    info "Removed $TOOLKIT_DIR"
  else
    warn "Toolkit not found at $TOOLKIT_DIR"
  fi

  # Remove from global settings.json
  SETTINGS="$HOME/.claude/settings.json"
  if [ -f "$SETTINGS" ]; then
    # Create a patched version without our plugin entries
    python3 - "$SETTINGS" <<'PYEOF' || true
import json, sys
with open(sys.argv[1]) as f:
    s = json.load(f)
s.get("extraKnownMarketplaces", {}).pop("agricidaniel-claude-obsidian", None)
s.get("enabledPlugins", {}).pop("claude-obsidian@agricidaniel-claude-obsidian", None)
# Clean up env vars
env = s.get("env", {})
env.pop("CLAUDE_OBSIDIAN_TOOLKIT", None)
env.pop("CLAUDE_OBSIDIAN_VAULT", None)
if not env:
    s.pop("env", None)
with open(sys.argv[1], 'w') as f:
    json.dump(s, f, indent=2)
PYEOF
    info "Cleaned Claude Code global settings"
  fi

  header "Uninstall complete"
  exit 0
fi

# ── Install mode ───────────────────────────────────────────────────────────────

if [ -d "$TOOLKIT_DIR" ]; then
  warn "Toolkit already exists at $TOOLKIT_DIR"
  echo "  Run with --uninstall first if you want a fresh install."
  echo -n "  Overwrite? [y/N] "
  read -r answer
  if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
    echo "  Aborted."
    exit 1
  fi
fi

# Prompt for vault directory if not specified via --vault
if [ -z "$VAULT_DIR" ]; then
  # Suggest project root or current directory as default
  DEFAULT_VAULT="$PROJECT_ROOT"
  echo ""
  info "Vault directory not specified. Detected default: ${DEFAULT_VAULT}"
  echo "  Skills need a vault to store wiki content. This is the directory"
  echo "  that contains (or will contain) wiki/, .raw/, and .claude-obsidian-root."
  echo -n "  Vault path [${DEFAULT_VAULT}]: "
  read -r VAULT_DIR_ANSWER
  VAULT_DIR="${VAULT_DIR_ANSWER:-$DEFAULT_VAULT}"
  info "Vault set to: $VAULT_DIR"
fi

header "Installing claude-obsidian toolchain"

# Create toolkit directory
mkdir -p "$TOOLKIT_DIR"
info "Created $TOOLKIT_DIR"

# Create the .claude-plugin dir for proper plugin registration
mkdir -p "$TOOLKIT_DIR/.claude-plugin"

# ── Copy infrastructure directories ────────────────────────────────────────────
echo
header "Copying infrastructure files"

for dir in scripts skills agents hooks bin commands docs tests assets _templates; do
  src="$PROJECT_ROOT/$dir"
  if [ -d "$src" ]; then
    cp -r "$src" "$TOOLKIT_DIR/$dir"
    info "Copied $dir/ ($(find "$src" -type f | wc -l | tr -d ' ') files)"
  else
    warn "Directory $dir/ not found, skipping"
  fi
done

# ── Copy root config files ─────────────────────────────────────────────────────
header "Copying config files"

for file in CLAUDE.md WIKI.md AGENTS.md Makefile .gitignore; do
  src="$PROJECT_ROOT/$file"
  if [ -f "$src" ]; then
    cp "$src" "$TOOLKIT_DIR/$file"
    info "Copied $file"
  fi
done

# Copy plugin.json and marketplace.json
if [ -f "$PROJECT_ROOT/.claude-plugin/plugin.json" ]; then
  cp "$PROJECT_ROOT/.claude-plugin/plugin.json" "$TOOLKIT_DIR/.claude-plugin/plugin.json"
  info "Copied plugin.json"
fi
if [ -f "$PROJECT_ROOT/.claude-plugin/marketplace.json" ]; then
  cp "$PROJECT_ROOT/.claude-plugin/marketplace.json" "$TOOLKIT_DIR/.claude-plugin/marketplace.json"
  info "Copied marketplace.json"
fi

# Copy hooks.json
if [ -f "$PROJECT_ROOT/hooks/hooks.json" ]; then
  mkdir -p "$TOOLKIT_DIR/hooks"
  cp "$PROJECT_ROOT/hooks/hooks.json" "$TOOLKIT_DIR/hooks/hooks.json"
  info "Copied hooks/hooks.json"
fi

# ── Set executable permissions ─────────────────────────────────────────────────
header "Setting permissions"
find "$TOOLKIT_DIR/scripts" -name '*.sh' -exec chmod +x {} \; 2>/dev/null || true
find "$TOOLKIT_DIR/scripts" -name '*.py' -exec chmod +x {} \; 2>/dev/null || true
find "$TOOLKIT_DIR/bin" -name '*.sh' -exec chmod +x {} \; 2>/dev/null || true
info "Set executable permissions on scripts"

# ── Register with Claude Code global settings ──────────────────────────────────
header "Registering with Claude Code"

SETTINGS="$HOME/.claude/settings.json"
mkdir -p "$(dirname "$SETTINGS")"

# Read existing settings or create new
if [ -f "$SETTINGS" ]; then
  PYTHON_SCRIPT=$(cat <<'PYEOF'
import json, sys

with open(sys.argv[1]) as f:
    s = json.load(f)

# Ensure extraKnownMarketplaces
ekm = s.setdefault("extraKnownMarketplaces", {})
ekm["agricidaniel-claude-obsidian"] = {
    "source": {
        "source": "directory",
        "path": sys.argv[2]
    }
}

# Enable the plugin
ep = s.setdefault("enabledPlugins", {})
ep["claude-obsidian@agricidaniel-claude-obsidian"] = True

# Set env vars
env = s.setdefault("env", {})
env["CLAUDE_OBSIDIAN_TOOLKIT"] = sys.argv[2]
# Don't overwrite an existing CLAUDE_OBSIDIAN_VAULT
if "CLAUDE_OBSIDIAN_VAULT" not in env:
    env["CLAUDE_OBSIDIAN_VAULT"] = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else ""

with open(sys.argv[1], 'w') as f:
    json.dump(s, f, indent=2, sort_keys=False)
PYEOF
  )
  python3 -c "$PYTHON_SCRIPT" "$SETTINGS" "$TOOLKIT_DIR" "${VAULT_DIR:-}"
  info "Updated $SETTINGS (plugin path → $TOOLKIT_DIR)"
else
  # Create new settings file
  settings_obj=$(cat <<JSON
{
  "extraKnownMarketplaces": {
    "agricidaniel-claude-obsidian": {
      "source": {
        "source": "directory",
        "path": "$TOOLKIT_DIR"
      }
    }
  },
  "enabledPlugins": {
    "claude-obsidian@agricidaniel-claude-obsidian": true
  },
  "env": {
    "CLAUDE_OBSIDIAN_TOOLKIT": "$TOOLKIT_DIR",
    "CLAUDE_OBSIDIAN_VAULT": "${VAULT_DIR:-}"
  }
}
JSON
  )
  echo "$settings_obj" > "$SETTINGS"
  info "Created $SETTINGS (plugin path → $TOOLKIT_DIR)"
fi

# ── Set up vault (optional) ────────────────────────────────────────────────────
if [ -n "$VAULT_DIR" ]; then
  header "Setting up vault at $VAULT_DIR"
  mkdir -p "$VAULT_DIR"
  mkdir -p "$VAULT_DIR/wiki/concepts" "$VAULT_DIR/wiki/entities" "$VAULT_DIR/wiki/sources" "$VAULT_DIR/wiki/meta"
  mkdir -p "$VAULT_DIR/.raw"
  mkdir -p "$VAULT_DIR/.vault-meta"

  # Create vault root marker
  touch "$VAULT_DIR/.claude-obsidian-root"
  info "Created .claude-obsidian-root marker"

  # Create vault CLAUDE.md
  if [ ! -f "$VAULT_DIR/CLAUDE.md" ]; then
    cat > "$VAULT_DIR/CLAUDE.md" << 'VCLAUDE'
# claude-obsidian vault

This directory is a **claude-obsidian wiki vault**. The automation toolchain
is installed at `~/.claude/obsidian-toolkit/` and is decoupled from this project.

## How it works

- **Wiki content** lives in `wiki/` (plain Markdown files).
- **Source files** for ingestion go in `.raw/`.
- **Runtime state** (transport config, locks, mode) lives in `.vault-meta/`.
- **Skills and scripts** are loaded from `~/.claude/obsidian-toolkit/` via global
  Claude Code settings. No local scripts directory needed.

## Quick start

```
# Ingest a source
/claude-obsidian:wiki-ingest <file>

# Lint the wiki
/claude-obsidian:wiki-lint

# Query the wiki
ask "what do you know about X?"
```

## Override env vars (optional)

Set these in `~/.claude/settings.json` or `.claude/settings.json`:
- `CLAUDE_OBSIDIAN_TOOLKIT` — path to toolchain (default: `~/.claude/obsidian-toolkit/`)
- `CLAUDE_OBSIDIAN_VAULT` — path to vault root (default: current working directory)
VCLAUDE
    info "Created vault CLAUDE.md"
  fi

  # Create .gitignore
  if [ ! -f "$VAULT_DIR/.gitignore" ]; then
    cat > "$VAULT_DIR/.gitignore" << 'VGITIGNORE'
# claude-obsidian vault — wiki content only
# The toolchain is installed separately at ~/.claude/obsidian-toolkit/

# Obsidian runtime state
.vault-meta/*.lock
.vault-meta/tiling-cache.json
.vault-meta/tiling-cache.*.tmp
.vault-meta/transport.json
.vault-meta/hook.log
.vault-meta/.wiki-lock.meta
.vault-meta/locks/*
!.vault-meta/locks/.gitkeep
.vault-meta/chunks/
.vault-meta/bm25/
.vault-meta/embed-cache.json
.vault-meta/embed-cache.*.tmp
.vault-meta/mode.json

# Attachments
_attachments/

# OS
.DS_Store
Thumbs.db
VGITIGNORE
    info "Created vault .gitignore"
  fi
fi

# ── Done ───────────────────────────────────────────────────────────────────────
header "Installation complete"
echo ""
echo -e "  ${GREEN}Toolkit:${NC}       $TOOLKIT_DIR"
echo -e "  ${GREEN}Skills:${NC}        $(find "$TOOLKIT_DIR/skills" -name 'SKILL.md' | wc -l | tr -d ' ') registered"
echo -e "  ${GREEN}Scripts:${NC}       $(find "$TOOLKIT_DIR/scripts" -type f | wc -l | tr -d ' ') files"
echo ""
if [ -n "$VAULT_DIR" ]; then
  echo -e "  ${GREEN}Vault:${NC}         $VAULT_DIR"
else
  echo -e "  ${YELLOW}Vault:${NC}         not specified — auto-discovered from .claude-obsidian-root"
  echo -e "  ${YELLOW}       ${NC}         or current working directory (see README)"
fi
echo ""
echo "  Next steps:"
echo "   1. Restart Claude Code session (or it picks up changes next time)"
echo "   2. Type /claude-obsidian:wiki-ingest to test"
echo "   3. The vault project can now be deleted — skills persist"
echo ""
