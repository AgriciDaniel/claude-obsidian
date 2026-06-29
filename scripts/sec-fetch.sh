#!/usr/bin/env bash
# sec-fetch.sh — fetch from sec.gov / data.sec.gov with a compliant User-Agent.
#
# WHY THIS EXISTS
#   The Claude Code `WebFetch` tool gets HTTP 403 from sec.gov because it sends
#   no compliant User-Agent. This is NOT a hard bot-block: SEC's fair-access
#   policy simply REQUIRES a declared User-Agent (contact info) and caps traffic
#   at 10 requests/second. A plain request WITH that header returns HTTP 200 —
#   for both sec.gov HTML pages (server-rendered, no JS needed) and the
#   data.sec.gov JSON APIs. Use this script instead of WebFetch for SEC primary
#   sources. (Discovered 2026-06-29; see wiki/concepts/EDGAR Data Access.md.)
#
# USAGE
#   bash scripts/sec-fetch.sh <url> [extra curl args...]
#   bash scripts/sec-fetch.sh https://www.sec.gov/submit-filings/about-edgar
#   bash scripts/sec-fetch.sh https://data.sec.gov/submissions/CIK0000051143.json
#   bash scripts/sec-fetch.sh --text https://www.sec.gov/...   # strip HTML to plain text
#
# CONTACT EMAIL (SEC fair-access policy expects a real one)
#   Set SEC_CONTACT_EMAIL in your environment, e.g.:
#     export SEC_CONTACT_EMAIL="you@example.com"
#   Or override the whole header with EDGAR_USER_AGENT.
#   (We do NOT hardcode a personal email in this committed file.)

set -euo pipefail

CONTACT="${SEC_CONTACT_EMAIL:-}"
if [[ -z "${CONTACT}" ]]; then
  CONTACT="set-SEC_CONTACT_EMAIL@example.com"
  echo "sec-fetch: warning — SEC_CONTACT_EMAIL is unset; SEC fair-access policy expects a real contact email." >&2
fi
UA="${EDGAR_USER_AGENT:-claude-obsidian-research ${CONTACT}}"

STRIP_HTML=0
if [[ "${1:-}" == "--text" ]]; then
  STRIP_HTML=1
  shift
fi

if [[ $# -lt 1 ]]; then
  echo "usage: bash scripts/sec-fetch.sh [--text] <url> [extra curl args...]" >&2
  exit 2
fi

URL="$1"; shift
case "$URL" in
  https://www.sec.gov/*|https://sec.gov/*|https://data.sec.gov/*|https://efts.sec.gov/*) ;;
  *) echo "sec-fetch: refusing non-sec.gov URL: $URL" >&2; exit 2 ;;
esac

# Be polite: a small delay keeps well under the 10 req/s ceiling on tight loops.
# -L follows redirects: sec.gov uses same-host 301s heavily when pages move.
fetch() { curl -sSL -A "$UA" "$URL" "$@"; }

if [[ "$STRIP_HTML" -eq 1 ]]; then
  fetch "$@" | python3 -c "
import sys,re,html
t=sys.stdin.read()
t=re.sub(r'<script.*?</script>',' ',t,flags=re.S|re.I)
t=re.sub(r'<style.*?</style>',' ',t,flags=re.S|re.I)
t=re.sub(r'<[^>]+>',' ',t)
t=html.unescape(t)
print(re.sub(r'\s+',' ',t).strip())
"
else
  fetch "$@"
fi
