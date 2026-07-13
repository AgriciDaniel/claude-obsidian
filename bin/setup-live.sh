#!/usr/bin/env bash
# setup-live.sh — one-shot setup for v2.0 "Live Core".
#
# Wires up the four v2.0 capabilities:
#   1. Network policy   (.vault-meta/net.json)      — always-on inbound, gated egress
#   2. Browser transport (.vault-meta/browser.json) — playwright > cdp > fetch
#   3. Rule packs        (rules/ -> 6 agent dialects)
#   4. Workflows         (workflows/*.js, run via the Workflow tool)
#
# Idempotent. Safe to re-run.
#
# Usage:
#   bash bin/setup-live.sh                # interactive
#   bash bin/setup-live.sh --mode live    # non-interactive, pick the net mode up front
#   bash bin/setup-live.sh --check        # report status, change nothing

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

NET_MODE=""
CHECK_ONLY=false

while [ $# -gt 0 ]; do
  case "$1" in
    --mode)  NET_MODE="${2:-}"; shift ;;
    --check) CHECK_ONLY=true ;;
    -h|--help)
      sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "ERR: unknown flag: $1" >&2; exit 3 ;;
  esac
  shift
done

echo "claude-obsidian v2.0 'Live Core' setup"
echo "Repo: $REPO_ROOT"
echo

# ── status check ─────────────────────────────────────────────────────────────
if $CHECK_ONLY; then
  echo "── Status ──"
  if [ -f .vault-meta/net.json ]; then
    echo -e "${GREEN}net${NC}      mode=$(python3 scripts/net-policy.py get)"
  else
    echo -e "${YELLOW}net${NC}      not configured (defaults apply: live inbound, explicit egress)"
  fi
  if [ -f .vault-meta/browser.json ]; then
    pref="$(python3 -c 'import json;print(json.load(open(".vault-meta/browser.json"))["preferred"])' 2>/dev/null || echo '?')"
    echo -e "${GREEN}browser${NC}  preferred=${pref}"
  else
    echo -e "${YELLOW}browser${NC}  not detected (run without --check)"
  fi
  if python3 scripts/render-rules.py check >/dev/null 2>&1; then
    echo -e "${GREEN}rules${NC}    rendered files are current"
  else
    echo -e "${RED}rules${NC}    STALE. Run: python3 scripts/render-rules.py render"
  fi
  echo -e "${GRAY}workflows${NC} $(ls workflows/*.js 2>/dev/null | wc -l | tr -d ' ') available"
  exit 0
fi

# ── 1. Network policy ────────────────────────────────────────────────────────
echo "── 1. Network policy ──"
echo
echo "  The vault reads the web freely. Sending vault content OUT to a third"
echo "  party always asks first. Those are different acts and they get different"
echo "  defaults; that asymmetry is the whole design."
echo
echo "    live     read the web at will; egress asks for consent  (recommended)"
echo "    ask      confirm before every fetch"
echo "    offline  no network at all"
echo

if [ -z "$NET_MODE" ]; then
  if [ -t 0 ]; then
    printf "  Mode [live]: "
    read -r NET_MODE || NET_MODE=""
  fi
  NET_MODE="${NET_MODE:-live}"
fi

python3 scripts/net-policy.py set-mode "$NET_MODE" >/dev/null
echo -e "  ${GREEN}net mode = ${NET_MODE}${NC}"
echo -e "  ${GRAY}SSRF guard on: loopback, private, and cloud-metadata addresses are denied.${NC}"
echo -e "  ${GRAY}Secrets (.env, keys, .aws/, .ssh/) can never egress, consent or not.${NC}"
echo

# ── 2. Browser ───────────────────────────────────────────────────────────────
echo "── 2. Browser transport ──"
bash scripts/detect-browser.sh --force --quiet >/dev/null
PREF="$(python3 -c 'import json;print(json.load(open(".vault-meta/browser.json"))["preferred"])')"
echo -e "  ${GREEN}preferred = ${PREF}${NC}"
case "$PREF" in
  playwright) echo -e "  ${GRAY}Full interaction available: click, type, auth, wait-for-selector.${NC}" ;;
  cdp)        echo -e "  ${GRAY}Headless Chrome: render, screenshot, dump-dom. No scripted interaction.${NC}"
              echo -e "  ${GRAY}For login-gated pages, install Playwright: npx playwright install chromium${NC}" ;;
  fetch)      echo -e "  ${YELLOW}No browser found. Plain HTTP only: JS-rendered pages will be invisible.${NC}"
              echo -e "  ${GRAY}Install Chrome, or: npx playwright install chromium${NC}" ;;
esac
echo

# ── 3. Rules ─────────────────────────────────────────────────────────────────
echo "── 3. Rule packs ──"
python3 scripts/render-rules.py render | sed 's/^/  /'
echo -e "  ${GRAY}Authored once in rules/, compiled to each agent's dialect.${NC}"
echo -e "  ${GRAY}Never hand-edit a rendered file: 'render-rules.py check' will fail the build.${NC}"
echo

# ── 4. Workflows ─────────────────────────────────────────────────────────────
echo "── 4. Workflows ──"
for wf in workflows/*.js; do
  [ -e "$wf" ] || continue
  name="$(basename "$wf" .js)"
  desc="$(grep -m1 "description:" "$wf" | sed "s/.*description: *'//; s/',*$//")"
  printf "  %-16s %s\n" "$name" "$desc"
done
echo -e "  ${GRAY}Opt-in and token-expensive. Ask for one by name.${NC}"
echo

echo -e "${GREEN}Done.${NC} Check status any time with: bash bin/setup-live.sh --check"
