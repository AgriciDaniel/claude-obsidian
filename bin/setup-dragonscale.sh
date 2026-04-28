#!/usr/bin/env bash
# setup-dragonscale.sh — opt-in installer for DragonScale Memory.
#
# Installs missing dependencies (python) and provisions the runtime files
# that the wiki-ingest and wiki-lint skills feature-detect.
# Safe to re-run (idempotent). Cross-platform: all locking is handled by
# Python (no flock binary required).
#
# Does NOT install ollama or pull any embedding model. Those are
# prerequisites for Mechanism 3 (semantic tiling) and are the user's
# responsibility.
#
# Usage:
#   bash bin/setup-dragonscale.sh [optional: /path/to/vault]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="${1:-$(dirname "$SCRIPT_DIR")}"

echo "Setting up DragonScale Memory at: $VAULT"
cd "$VAULT"

# ── 0. Install missing dependencies ─────────────────────────────────────────

install_python() {
  local os
  os="$(uname -s)"
  case "$os" in
    MINGW*|MSYS*|CYGWIN*)
      echo "  Python not found. Installing on Windows..."
      if command -v choco >/dev/null 2>&1; then
        choco install python3 -y --no-progress 2>&1 | tail -3
      elif command -v winget >/dev/null 2>&1; then
        winget install --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements 2>&1 | tail -3
      else
        echo "ERR: no package manager found. Install Python from https://python.org" >&2
        return 1
      fi
      ;;
    Darwin*)
      if command -v brew >/dev/null 2>&1; then
        brew install python3 2>&1 | tail -3
      else
        echo "ERR: homebrew not found. Install Python via: brew install python3" >&2
        return 1
      fi
      ;;
    Linux*)
      if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get install -y python3 2>&1 | tail -3
      elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y python3 2>&1 | tail -3
      elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --noconfirm python 2>&1 | tail -3
      else
        echo "ERR: no supported package manager found. Install Python manually." >&2
        return 1
      fi
      ;;
  esac
}

echo "Checking dependencies..."

# python (required for all DragonScale mechanisms)
if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
  install_python
  if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    echo "WARN: python install may require a new shell session to take effect." >&2
    echo "      Mechanism 3 (tiling) and 4 (boundary-score) will not work until python is on PATH." >&2
  else
    echo "OK  python installed: $(command -v python || command -v python3)"
  fi
else
  echo "OK  python: $(command -v python || command -v python3)"
fi

echo ""

# ── 1. Verify required artifacts that ship with the plugin ───────────────────
for required in "scripts/allocate-address.py" "scripts/tiling-check.py" "scripts/_lock.py" "skills/wiki-fold/SKILL.md"; do
  if [ ! -e "$required" ]; then
    echo "ERR: missing $required. Reinstall the claude-obsidian plugin." >&2
    exit 1
  fi
done
chmod +x scripts/allocate-address.py scripts/tiling-check.py 2>/dev/null || true

# ── 2. Provision .vault-meta/ ─────────────────────────────────────────────────
mkdir -p .vault-meta
if [ ! -f .vault-meta/address-counter.txt ]; then
  echo "1" > .vault-meta/address-counter.txt
  echo "OK  .vault-meta/address-counter.txt initialized at 1"
else
  echo "--  .vault-meta/address-counter.txt already present (not overwritten)"
fi

if [ ! -f .vault-meta/tiling-thresholds.json ]; then
  cat > .vault-meta/tiling-thresholds.json <<'JSON'
{
  "version": 1,
  "model": "nomic-embed-text",
  "bands": {
    "error": 0.90,
    "review": 0.80
  },
  "calibrated": false,
  "calibration_pairs_labeled": 0,
  "notes": "Conservative seed thresholds, NOT calibrated against this vault. See skills/wiki-lint/SKILL.md Semantic Tiling section for the calibration procedure."
}
JSON
  echo "OK  .vault-meta/tiling-thresholds.json initialized with conservative seed bands"
else
  echo "--  .vault-meta/tiling-thresholds.json already present (not overwritten)"
fi

# ── 3. Provision .raw/.manifest.json (if absent) ──────────────────────────────
mkdir -p .raw
if [ ! -f .raw/.manifest.json ]; then
  cat > .raw/.manifest.json <<'JSON'
{
  "version": 1,
  "created": "DRAGONSCALE_SETUP",
  "description": "Ingest delta tracker and address map for the claude-obsidian vault. Do not hand-edit; wiki-ingest maintains this.",
  "sources": {},
  "address_map": {}
}
JSON
  # Replace placeholder with today's date
  DATE=$(date +%Y-%m-%d)
  sed -i.bak "s/DRAGONSCALE_SETUP/$DATE/" .raw/.manifest.json
  rm -f .raw/.manifest.json.bak
  echo "OK  .raw/.manifest.json initialized (empty sources + address_map)"
else
  echo "--  .raw/.manifest.json already present (not overwritten)"
fi

# ── 4. Rollout-baseline marker in legacy-pages.txt ────────────────────────────
if [ ! -f .vault-meta/legacy-pages.txt ]; then
  cat > .vault-meta/legacy-pages.txt <<EOF
# DragonScale legacy-pages manifest
# rollout: $(date +%Y-%m-%d)
#
# List, one path per line, any pages whose frontmatter \`created:\` date is
# post-rollout but which should still be treated as legacy (i.e. not required
# to have an address). Also lines beginning with "# rollout:" set the
# per-vault rollout baseline used by wiki-lint for severity classification.
# Example:
# wiki/sources/old-page-with-wrong-metadata.md
EOF
  echo "OK  .vault-meta/legacy-pages.txt initialized (rollout baseline set to today)"
else
  echo "--  .vault-meta/legacy-pages.txt already present (not overwritten)"
fi

# ── 5. Sanity checks ──────────────────────────────────────────────────────────
echo ""
echo "Sanity checks:"
PYTHON_CMD=$(command -v python || command -v python3)
NEXT=$("$PYTHON_CMD" ./scripts/allocate-address.py --peek 2>&1 | tail -1)
echo "  next address: c-$(printf '%06d' $NEXT)"

PYTHON=$(command -v python || command -v python3 || echo "not installed")
echo "  python:       $PYTHON"

if command -v curl >/dev/null 2>&1; then
  if curl -sS --max-time 2 http://localhost:11434/api/version >/dev/null 2>&1; then
    echo "  ollama:       reachable at http://localhost:11434"
    if curl -sS --max-time 2 http://localhost:11434/api/tags | grep -q nomic-embed-text; then
      echo "  nomic-embed:  installed"
    else
      echo "  nomic-embed:  NOT installed (run 'ollama pull nomic-embed-text' to enable Mechanism 3)"
    fi
  else
    echo "  ollama:       not reachable (Mechanism 3 will no-op; install from https://ollama.com)"
  fi
else
  echo "  curl:         not installed (cannot check ollama)"
fi

echo ""
echo "DragonScale setup complete."
echo "See wiki/concepts/DragonScale Memory.md for the full spec."
echo "See skills/wiki-fold/ for Mechanism 1 (log folds)."
echo "wiki-ingest and wiki-lint will now feature-detect DragonScale automatically."
