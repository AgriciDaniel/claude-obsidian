#!/usr/bin/env bash
# detect-browser.sh — discover which browser-automation transports are available
# on this machine, write a normalized JSON snapshot to .vault-meta/browser.json,
# and pick a preferred transport per the v2.0 browser fallback chain.
#
# Fallback chain (highest to lowest precedence):
#   1. playwright  — Playwright MCP / CLI. Full control: click, type, auth, wait for JS.
#   2. cdp         — A Chrome/Chromium binary driven headless over the DevTools protocol.
#                    Renders JS and screenshots. No scripted interaction.
#   3. fetch       — Plain HTTP via WebFetch/curl. No JS. Always available (ultimate floor).
#
# WHY THIS EXISTS: WebFetch retrieves HTML. A huge share of the modern web renders
# its content in JS, gates it behind a login, or serves a cookie wall. To those
# pages WebFetch is blind, and it fails SILENTLY: it returns the shell of the page
# and reports success. The browser transport is what makes those pages ingestible.
#
# macOS NOTE (this is the whole reason the probe is not a one-liner): browsers on
# macOS live inside .app bundles and do NOT symlink their binary onto PATH. A
# PATH-only probe therefore reports "no browser" on a Mac that has Chrome sitting
# right there in /Applications. That is exactly the bug that made the Obsidian CLI
# transport silently never engage on any Mac (see wiki/hot.md, 2026-07-12). We
# probe bundle paths first, PATH second.
#
# Usage:
#   ./scripts/detect-browser.sh             # detect and write .vault-meta/browser.json
#   ./scripts/detect-browser.sh --peek      # print result to stdout without writing
#   ./scripts/detect-browser.sh --force     # refresh even if existing snapshot is fresh (<7d)
#   ./scripts/detect-browser.sh --quiet     # suppress informational stderr output
#
# Exit codes:
#   0 — success (browser.json written or peeked)
#   2 — vault-meta/ missing and cannot be created
#   3 — unrecognized flag

set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
META_DIR="${VAULT_ROOT}/.vault-meta"
OUTPUT_FILE="${META_DIR}/browser.json"
STALE_AFTER_DAYS=7

MODE="write"
QUIET=false

while [ $# -gt 0 ]; do
  case "$1" in
    --peek)  MODE="peek" ;;
    --force) MODE="force" ;;
    --quiet) QUIET=true ;;
    -h|--help)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "ERR: unknown flag: $1" >&2
      exit 3
      ;;
  esac
  shift
done

log() { $QUIET || echo "$@" >&2; }

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()), end="")'
}

mkdir -p "$META_DIR" || {
  echo "ERR: cannot create .vault-meta/ at $META_DIR" >&2
  exit 2
}

# ── Freshness check ──────────────────────────────────────────────────────────
if [ "$MODE" = "write" ] && [ -f "$OUTPUT_FILE" ]; then
  if find "$OUTPUT_FILE" -mtime -${STALE_AFTER_DAYS} -print 2>/dev/null | grep -q .; then
    log "browser.json is fresh (<${STALE_AFTER_DAYS}d). Use --force to refresh."
    cat "$OUTPUT_FILE"
    exit 0
  fi
fi

# ── 1. Chrome / Chromium binary detection ────────────────────────────────────
# Bundle paths FIRST (macOS), then PATH (Linux, and Macs where the user linked it).
CHROME_BIN=""
CHROME_FLAVOR=""

BUNDLE_CANDIDATES=(
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome|chrome"
  "/Applications/Chromium.app/Contents/MacOS/Chromium|chromium"
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge|edge"
  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser|brave"
  "${HOME}/Applications/Google Chrome.app/Contents/MacOS/Google Chrome|chrome"
)

for entry in "${BUNDLE_CANDIDATES[@]}"; do
  candidate="${entry%|*}"
  flavor="${entry##*|}"
  if [ -x "$candidate" ]; then
    CHROME_BIN="$candidate"
    CHROME_FLAVOR="$flavor"
    break
  fi
done

if [ -z "$CHROME_BIN" ]; then
  for entry in "google-chrome|chrome" "google-chrome-stable|chrome" \
               "chromium|chromium" "chromium-browser|chromium" \
               "microsoft-edge|edge" "brave-browser|brave"; do
    candidate="${entry%|*}"
    flavor="${entry##*|}"
    if command -v "$candidate" >/dev/null 2>&1; then
      CHROME_BIN="$(command -v "$candidate")"
      CHROME_FLAVOR="$flavor"
      break
    fi
  done
fi

CHROME_PRESENT=false
CHROME_VERSION='""'
CHROME_VERSION_RAW=""
if [ -n "$CHROME_BIN" ]; then
  CHROME_PRESENT=true
  CHROME_VERSION_RAW="$("$CHROME_BIN" --version 2>/dev/null | head -1 || echo unknown)"
  CHROME_VERSION="$(printf '%s' "$CHROME_VERSION_RAW" | json_escape || echo '"unknown"')"
fi

# ── 2. Playwright detection ──────────────────────────────────────────────────
# Either a global `playwright` binary, or a local node_modules install.
PLAYWRIGHT_PRESENT=false
PLAYWRIGHT_HOW=""
PLAYWRIGHT_VERSION='""'
PLAYWRIGHT_VERSION_RAW=""

if command -v playwright >/dev/null 2>&1; then
  PLAYWRIGHT_PRESENT=true
  PLAYWRIGHT_HOW="binary"
  PLAYWRIGHT_VERSION_RAW="$(playwright --version 2>/dev/null | head -1 || echo unknown)"
elif [ -x "${VAULT_ROOT}/node_modules/.bin/playwright" ]; then
  PLAYWRIGHT_PRESENT=true
  PLAYWRIGHT_HOW="node_modules"
  PLAYWRIGHT_VERSION_RAW="$("${VAULT_ROOT}/node_modules/.bin/playwright" --version 2>/dev/null | head -1 || echo unknown)"
fi

if [ -n "$PLAYWRIGHT_VERSION_RAW" ]; then
  PLAYWRIGHT_VERSION="$(printf '%s' "$PLAYWRIGHT_VERSION_RAW" | json_escape || echo '"unknown"')"
fi

# ── 3. Compute preferred + fallback chain ────────────────────────────────────
# NOTE: we deliberately do NOT probe for a chrome-devtools MCP server here.
# Calling `claude mcp list` from inside a running claude session has the same
# reentrancy problem detect-transport.sh documents. MCP stays user-declared.
if $PLAYWRIGHT_PRESENT; then
  PREFERRED="playwright"
  CHAIN='"playwright", "cdp", "fetch"'
elif $CHROME_PRESENT; then
  PREFERRED="cdp"
  CHAIN='"cdp", "fetch"'
else
  PREFERRED="fetch"
  CHAIN='"fetch"'
fi

# ── 4. Build JSON snapshot ───────────────────────────────────────────────────
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HOSTNAME_VAL="$(hostname 2>/dev/null || echo unknown)"
CHROME_BIN_JSON="$(printf '%s' "$CHROME_BIN" | json_escape)"

snapshot() {
  cat <<JSON
{
  "schema_version": 1,
  "detected_at": "${TIMESTAMP}",
  "host": "${HOSTNAME_VAL}",
  "vault_root": "${VAULT_ROOT}",
  "preferred": "${PREFERRED}",
  "fallback_chain": [${CHAIN}],
  "available": {
    "playwright": {
      "present": ${PLAYWRIGHT_PRESENT},
      "how": "${PLAYWRIGHT_HOW}",
      "version_string": ${PLAYWRIGHT_VERSION},
      "note": "full interaction: click, type, auth, wait-for-selector"
    },
    "cdp": {
      "present": ${CHROME_PRESENT},
      "binary": ${CHROME_BIN_JSON},
      "flavor": "${CHROME_FLAVOR}",
      "version_string": ${CHROME_VERSION},
      "note": "headless render + screenshot + dump-dom; no scripted interaction"
    },
    "fetch": {
      "present": true,
      "note": "ultimate fallback; plain HTTP, no JS execution. Blind to JS-rendered and auth-gated pages."
    },
    "chrome_devtools_mcp": {
      "present": null,
      "detection": "deferred",
      "note": "MCP servers are not auto-probed (reentrancy). Declare manually and set preferred by hand."
    }
  }
}
JSON
}

if [ "$MODE" = "peek" ]; then
  snapshot
  exit 0
fi

TMP="${OUTPUT_FILE}.$$.tmp"
trap 'rm -f "$TMP"' EXIT
snapshot > "$TMP"
mv "$TMP" "$OUTPUT_FILE"
trap - EXIT

log "Wrote: ${OUTPUT_FILE}"
log "Preferred browser transport: ${PREFERRED}"
$PLAYWRIGHT_PRESENT && log "  Playwright: present (${PLAYWRIGHT_HOW}, ${PLAYWRIGHT_VERSION_RAW})"
$CHROME_PRESENT     && log "  CDP:        ${CHROME_FLAVOR} at ${CHROME_BIN} (${CHROME_VERSION_RAW})"
log "  Fetch:      always available (no JS execution)"
