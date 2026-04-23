#!/usr/bin/env bash
# setup-dragonscale.sh — opt-in installer for DragonScale Memory.
#
# Provisions the runtime files that the wiki-ingest and wiki-lint skills
# feature-detect. Safe to re-run (idempotent).
#
# Does NOT install ollama or pull any embedding model. Those are
# prerequisites for Mechanism 3 (semantic tiling) and are the user's
# responsibility. Mechanism 1 (fold) and Mechanism 2 (addresses) have no
# external prerequisites.
#
# Usage:
#   bash bin/setup-dragonscale.sh [optional: /path/to/vault]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="${1:-$(dirname "$SCRIPT_DIR")}"

echo "Setting up DragonScale Memory at: $VAULT"
cd "$VAULT"

# ── 1. Verify required artifacts that ship with the plugin ───────────────────
for required in "scripts/allocate-address.sh" "scripts/tiling-check.py" "skills/wiki-fold/SKILL.md"; do
  if [ ! -e "$required" ]; then
    echo "ERR: missing $required. Reinstall the claude-obsidian plugin." >&2
    exit 1
  fi
done
chmod +x scripts/allocate-address.sh scripts/tiling-check.py

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
NEXT=$(./scripts/allocate-address.sh --peek 2>&1 | tail -1)
echo "  next address: c-$(printf '%06d' $NEXT)"

PYTHON=$(command -v python3 || echo "not installed")
echo "  python3:      $PYTHON"

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
