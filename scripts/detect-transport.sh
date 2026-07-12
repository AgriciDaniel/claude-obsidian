#!/usr/bin/env bash
# detect-transport.sh — discover which vault-mutation transports are available
# on this machine, write a normalized JSON snapshot to .vault-meta/transport.json,
# and pick a preferred transport per the v1.7 fallback chain.
#
# Fallback chain (highest to lowest precedence):
#   1. cli         — Obsidian CLI binary (Obsidian 1.12+). No MCP server, no TLS, no plugin.
#   2. mcp-obsidian — REST-API-backed MCP server (Local REST API plugin required).
#   3. mcpvault    — Filesystem-backed MCP server (BM25 search; no Obsidian plugin).
#   4. filesystem  — Direct Read/Write/Edit tools. Always available (ultimate floor).
#
# MCP auto-detection is deferred to a v1.7.x patch (calling `claude mcp list` from
# inside a running claude session has reentrancy concerns). For v1.7, we detect
# CLI + filesystem and leave MCP fields as `{"present": null, "detection": "deferred"}`.
# Users with MCP transports configured can either edit transport.json manually or
# follow the legacy guidance in wiki/references/mcp-setup.md.
#
# Usage:
#   ./scripts/detect-transport.sh             # detect and write .vault-meta/transport.json
#   ./scripts/detect-transport.sh --peek      # print result to stdout without writing
#   ./scripts/detect-transport.sh --force     # refresh even if existing snapshot is fresh (<7d)
#   ./scripts/detect-transport.sh --quiet     # suppress informational stderr output
#
# Exit codes:
#   0 — success (transport.json written or peeked)
#   2 — vault-meta/ missing and cannot be created
#   3 — unrecognized flag

set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
META_DIR="${VAULT_ROOT}/.vault-meta"
OUTPUT_FILE="${META_DIR}/transport.json"
STALE_AFTER_DAYS=7

MODE="write"
QUIET=false

while [ $# -gt 0 ]; do
  case "$1" in
    --peek)  MODE="peek" ;;
    --force) MODE="force" ;;
    --quiet) QUIET=true ;;
    -h|--help)
      sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
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

# json_escape: read stdin and emit a JSON-encoded string (including the
# surrounding double quotes). Used for any untrusted value that lands in the
# transport.json heredoc — newlines, backslashes, control chars in upstream
# binaries (obsidian-cli --version) would otherwise break the JSON.
json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()), end="")'
}

mkdir -p "$META_DIR" || {
  echo "ERR: cannot create .vault-meta/ at $META_DIR" >&2
  exit 2
}

# ── 0. Honor manual_override from existing transport.json ────────────────────
# Users can pin a non-detected transport (mcp-obsidian, mcpvault, or any custom
# value) by editing transport.json to set:
#     "manual_override": true
#     "preferred": "<their-choice>"
#     "fallback_chain": [...]
# Auto-detection still runs (to refresh CLI/Obsidian-running flags for visibility),
# but PREFERRED and CHAIN are preserved from the existing file across both the
# normal write path AND --force runs. Documented at
# wiki/references/transport-fallback.md §Manual override.
MANUAL_OVERRIDE_FLAG=false
MANUAL_OVERRIDE_PREFERRED=""
MANUAL_OVERRIDE_CHAIN=""
if [ -f "$OUTPUT_FILE" ]; then
  MANUAL_PARSE="$(python3 - "$OUTPUT_FILE" 2>/dev/null <<'PYEOF'
import json, sys
try:
    with open(sys.argv[1]) as fh:
        data = json.load(fh)
    if data.get("manual_override") is True:
        pref = data.get("preferred", "")
        chain = data.get("fallback_chain", [])
        # Output: line 1 = preferred; line 2 = comma-separated quoted chain entries.
        print(pref)
        print(",".join('"' + str(c) + '"' for c in chain))
except Exception:
    pass
PYEOF
)" || MANUAL_PARSE=""
  if [ -n "${MANUAL_PARSE:-}" ]; then
    MANUAL_OVERRIDE_FLAG=true
    MANUAL_OVERRIDE_PREFERRED="$(printf '%s\n' "$MANUAL_PARSE" | sed -n '1p')"
    MANUAL_OVERRIDE_CHAIN="$(printf '%s\n' "$MANUAL_PARSE" | sed -n '2p')"
    log "manual_override=true; preserving preferred=${MANUAL_OVERRIDE_PREFERRED}"
  fi
fi

# ── Freshness check: skip detection if snapshot is recent ────────────────────
if [ "$MODE" = "write" ] && [ -f "$OUTPUT_FILE" ]; then
  if find "$OUTPUT_FILE" -mtime -${STALE_AFTER_DAYS} -print 2>/dev/null | grep -q .; then
    log "transport.json is fresh (<${STALE_AFTER_DAYS}d). Use --force to refresh."
    cat "$OUTPUT_FILE"
    exit 0
  fi
fi

# _spawn_bounded OUTFILE CMD [ARGS...] — start CMD in its OWN PROCESS GROUP,
# redirecting stdout to OUTFILE (use /dev/null to discard). Sets _BOUNDED_PID.
#
# The pid comes back in a GLOBAL, not on stdout, and that is deliberate. Calling
# this as `pid="$(_spawn_bounded ...)"` would run it in a command-substitution
# subshell, making the background job a child of THAT subshell rather than of the
# caller. `wait` in the caller then fails, the probe looks like it errored, and the
# CLI gets reported as absent. A plain function call does not fork, so the job stays
# a direct child and `wait` works.
#
# The process group is the point. Killing just the leader leaves anything it
# spawned running, reparented to PID 1. The hang we are guarding against is an
# Electron launcher, which spawns helpers freely, so a bare `kill -9 $pid` would
# leak orphans on every timed-out probe — and detect-transport.sh runs from
# several skills, so they would accumulate across a session.
#
# `set -m` (job control) makes bash put each background job in its own process
# group whose PGID equals its PID, which is what lets _reap_group signal the whole
# tree. macOS ships no setsid(1), so this is the portable route. The group is
# fixed at fork time, so restoring the old -m state immediately after is safe.
_BOUNDED_PID=""
_spawn_bounded() {
  local outfile="$1"; shift

  local had_m=0
  case "$-" in *m*) had_m=1 ;; esac

  set -m
  "$@" >"$outfile" 2>/dev/null &
  _BOUNDED_PID=$!
  [ "$had_m" -eq 1 ] || set +m
}

# _reap_group PID SECS — poll PID, then SIGKILL its whole process group past SECS.
# Returns the command's status, or 1 if it had to be killed. macOS ships no
# timeout(1) (it is GNU coreutils), so the bound is hand-rolled to stay portable.
_reap_group() {
  local pid="$1" secs="$2"
  local waited=0
  local limit=$(( secs * 10 ))

  while kill -0 "$pid" 2>/dev/null; do
    if [ "$waited" -ge "$limit" ]; then
      # Negative pid == the process group. Fall back to the bare pid if the group
      # is already gone, so we never leave the leader alive.
      kill -9 -"$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null || true
      return 1
    fi
    sleep 0.1
    waited=$(( waited + 1 ))
  done

  wait "$pid"
}

# probe_with_timeout SECS CMD [ARGS...] — run CMD for its EXIT STATUS only.
# Output is discarded. Use for capability probes, never to read a command's result.
probe_with_timeout() {
  local secs="$1"; shift
  _spawn_bounded /dev/null "$@"
  _reap_group "$_BOUNDED_PID" "$secs"
}

# capture_with_timeout SECS CMD [ARGS...] — run CMD and echo its STDOUT, bounded.
# Separate from probe_with_timeout because that one sends stdout to /dev/null, so
# capturing through it silently yields nothing (which is exactly the bug this
# comment exists to stop someone re-introducing).
capture_with_timeout() {
  local secs="$1"; shift
  local out
  out="$(mktemp)" || return 1

  local rc=0
  _spawn_bounded "$out" "$@"
  _reap_group "$_BOUNDED_PID" "$secs" || rc=$?

  cat "$out"
  rm -f "$out"
  return $rc
}

# ── 1. CLI detection ─────────────────────────────────────────────────────────
# Probe order: PATH first (respects a user's own symlink or wrapper), then the
# known app-bundle locations. Obsidian 1.12 ships the CLI *inside* the bundle and
# does NOT symlink it onto PATH, so a PATH-only probe misses it on every stock
# macOS install and silently downgrades the vault to the filesystem floor.
#
# CLI_BINARY is whatever string a consumer must exec — a bare name when it is on
# PATH, an absolute path when it is only in the bundle. Consumers invoke it
# verbatim; they must not assume it is PATH-resolvable.
CLI_PRESENT=false
CLI_BINARY=""
CLI_VERSION=""
CLI_VERSION_RAW=""

# Order matters. `obsidian-cli` is an unambiguous CLI name, so it wins. The bundle
# paths come next: they are stable, whereas a PATH symlink can point into a
# Gatekeeper-translocated bundle whose path is randomized per launch. Bare
# `obsidian` is LAST because on some installs it is the Electron GUI launcher, and
# probing a GUI launcher risks popping a window during an unattended detection run.
CLI_CANDIDATES=(
  "obsidian-cli"
  "/Applications/Obsidian.app/Contents/MacOS/obsidian-cli"
  "${HOME}/Applications/Obsidian.app/Contents/MacOS/obsidian-cli"
  "obsidian"
)

for candidate in "${CLI_CANDIDATES[@]}"; do
  # Bare names must resolve on PATH; absolute paths must be executable files.
  case "$candidate" in
    /*) [ -x "$candidate" ] || continue ;;
    *)  command -v "$candidate" >/dev/null 2>&1 || continue ;;
  esac

  # Confirm it is really the CLI and not a GUI launcher. The Obsidian CLI takes a
  # `version` subcommand (it rejects `--version`), so a clean exit is the probe.
  #
  # Bounded, because we cannot be sure how a non-CLI binary reacts: an Electron
  # launcher special-cases `--version` but may treat a bare `version` as a file to
  # open, and would then sit there with a window up. detect-transport.sh runs from
  # several skills, so a hang here would wedge them. A timeout degrades that to a
  # failed probe and we simply move to the next candidate.
  if ! probe_with_timeout 3 "$candidate" version; then
    continue
  fi

  CLI_PRESENT=true
  CLI_BINARY="$candidate"
  # Keep two views of the version: RAW for the human log line, JSON-escaped
  # for the transport.json heredoc. CLI_VERSION below is pre-quoted (includes
  # the surrounding double quotes), so the heredoc emits ${CLI_VERSION}
  # without wrapping quotes.
  CLI_VERSION_RAW="$("$candidate" version 2>/dev/null | head -1 || echo unknown)"
  CLI_VERSION="$(printf '%s' "$CLI_VERSION_RAW" | json_escape || echo '"unknown"')"
  break
done
# Fallback default when neither binary was found: must still be a valid JSON literal.
if [ -z "$CLI_VERSION" ]; then
  CLI_VERSION='""'
  CLI_VERSION_RAW=""
fi

# The binary is now sometimes an absolute path, not a bare name. Escape it the same
# way as the version string rather than trusting it to be JSON-safe by construction —
# the candidate list is hardcoded today, but a user-configurable path would not be.
CLI_BINARY_JSON="$(printf '%s' "$CLI_BINARY" | json_escape || echo '""')"

# ── 2. Obsidian app running? (informational only; CLI works either way) ──────
OBSIDIAN_RUNNING=false
if command -v pgrep >/dev/null 2>&1; then
  if pgrep -if 'obsidian' >/dev/null 2>&1; then
    OBSIDIAN_RUNNING=true
  fi
fi

# ── 2b. Can the CLI actually ADDRESS this vault? ─────────────────────────────
# The CLI targets a vault by NAME (`vault=<name>`), resolved against Obsidian's
# own registry — never by path. So "the binary exists" does NOT imply "the binary
# can reach the vault we are standing in":
#
#   - Obsidian may not have this directory open as a vault at all.
#   - Another directory may be registered under the same name, in which case every
#     CLI call silently reads and writes THAT directory while reporting success.
#
# The second case is not hypothetical; it is how this check came to exist. A stray
# copy of the repo registered under the same name absorbed an entire session's CLI
# writes while the real working tree sat untouched. That is the same silent
# wrong-target failure this script was already fixed once to prevent.
#
# So: ask the CLI which vaults it knows, and find the one whose PATH is this vault
# root. If none is, the CLI cannot be trusted here and we fall back to filesystem.
# The resolved name is published so consumers pass a verified `vault=` rather than
# guessing from the directory basename.
CLI_VAULT_NAME=""
CLI_VAULT_ADDRESSABLE=false

if $CLI_PRESENT; then
  # Resolve symlinks on both sides so /tmp vs /private/tmp (and friends) match.
  VAULT_ROOT_REAL="$(cd "$VAULT_ROOT" 2>/dev/null && pwd -P || echo "$VAULT_ROOT")"

  VAULT_REGISTRY="$(capture_with_timeout 5 "$CLI_BINARY" vaults verbose 2>/dev/null || true)"

  # `vaults verbose` emits: <name>\t<path>
  while IFS="$(printf '\t')" read -r v_name v_path; do
    [ -n "${v_path:-}" ] || continue
    v_path_real="$(cd "$v_path" 2>/dev/null && pwd -P || echo "$v_path")"
    if [ "$v_path_real" = "$VAULT_ROOT_REAL" ]; then
      CLI_VAULT_NAME="$v_name"
      CLI_VAULT_ADDRESSABLE=true
      break
    fi
  done <<EOF
$VAULT_REGISTRY
EOF

  # Matching by PATH is only half the job. We then hand consumers a NAME, and the
  # CLI resolves `vault=<name>` through the registry — so if two registered vaults
  # share a name, the name we publish is ambiguous and can resolve to the other one.
  # That would reinstate the exact silent-wrong-target bug this block exists to stop,
  # inside the fix for it. Obsidian derives the vault name from the folder basename,
  # so two checkouts of the same repo in different directories collide by default,
  # which is precisely the situation that caused the original incident.
  #
  # The CLI offers no way to target a vault by path, so a collision is unfixable here:
  # refuse `cli` rather than guess.
  if $CLI_VAULT_ADDRESSABLE; then
    NAME_COUNT="$(printf '%s\n' "$VAULT_REGISTRY" \
      | awk -F'\t' -v n="$CLI_VAULT_NAME" 'NF && $1 == n { c++ } END { print c+0 }')"

    if [ "${NAME_COUNT:-0}" -gt 1 ]; then
      CLI_VAULT_ADDRESSABLE=false
      CLI_VAULT_NAME=""
      log "WARN: Obsidian has ${NAME_COUNT} vaults registered under the name"
      log "      '$(printf '%s' "$VAULT_REGISTRY" | awk -F'\t' 'NF{print $1}' | sort | uniq -d | head -1)'."
      log "      \`vault=<name>\` cannot distinguish them, so a CLI call could hit the"
      log "      wrong one. Rename or remove the duplicate vault in Obsidian."
      log "      Falling back to: filesystem."
    fi
  fi

  if ! $CLI_VAULT_ADDRESSABLE; then
    # Two very different causes, two very different fixes. Do not tell someone to
    # register a vault they already registered; the app just is not running.
    if ! $OBSIDIAN_RUNNING; then
      log "WARN: the Obsidian CLI is installed, but Obsidian is not running, so it"
      log "      cannot report which vaults exist. The vault may well be registered."
      log "      Start Obsidian and re-run with --force. Falling back to: filesystem."
    else
      log "WARN: the Obsidian CLI is installed and Obsidian is running, but no vault"
      log "      is registered at ${VAULT_ROOT_REAL}"
      log "      A CLI call would target a DIFFERENT directory (or fail), so the cli"
      log "      transport is being skipped. Open this folder as a vault in Obsidian"
      log "      to enable it. Falling back to: filesystem."
    fi
  fi
fi

CLI_VAULT_NAME_JSON="$(printf '%s' "$CLI_VAULT_NAME" | json_escape || echo '""')"

# ── 3. Compute preferred + fallback chain ────────────────────────────────────
# `cli` requires BOTH a working binary and a vault the binary can actually address.
# A present-but-unaddressable CLI is worse than no CLI: it succeeds against the
# wrong directory.
if $CLI_PRESENT && $CLI_VAULT_ADDRESSABLE; then
  PREFERRED="cli"
  CHAIN='"cli", "filesystem"'
else
  PREFERRED="filesystem"
  CHAIN='"filesystem"'
fi

# ── 3b. Apply manual_override if it was parsed from the existing snapshot ────
# Auto-detected PREFERRED/CHAIN above are overridden so the user's pinned
# transport survives every refresh cycle including --force.
if $MANUAL_OVERRIDE_FLAG; then
  PREFERRED="$MANUAL_OVERRIDE_PREFERRED"
  CHAIN="$MANUAL_OVERRIDE_CHAIN"
fi

# ── 4. Build JSON snapshot ───────────────────────────────────────────────────
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HOSTNAME="$(hostname 2>/dev/null || echo unknown)"

snapshot() {
  cat <<JSON
{
  "schema_version": 1,
  "detected_at": "${TIMESTAMP}",
  "host": "${HOSTNAME}",
  "vault_root": "${VAULT_ROOT}",
  "manual_override": ${MANUAL_OVERRIDE_FLAG},
  "preferred": "${PREFERRED}",
  "fallback_chain": [${CHAIN}],
  "available": {
    "cli": {
      "present": ${CLI_PRESENT},
      "binary": ${CLI_BINARY_JSON},
      "version_string": ${CLI_VERSION},
      "vault_addressable": ${CLI_VAULT_ADDRESSABLE},
      "vault_name": ${CLI_VAULT_NAME_JSON},
      "obsidian_app_running": ${OBSIDIAN_RUNNING}
    },
    "filesystem": {
      "present": true,
      "vault_root": "${VAULT_ROOT}",
      "note": "ultimate fallback; uses Claude's Read/Write/Edit tools directly"
    },
    "mcp_obsidian": {
      "present": null,
      "detection": "deferred",
      "note": "v1.7 does not auto-detect MCP servers. Configure manually per wiki/references/mcp-setup.md and edit this file by hand if needed."
    },
    "mcpvault": {
      "present": null,
      "detection": "deferred",
      "note": "v1.7 does not auto-detect MCP servers. Configure manually per wiki/references/mcp-setup.md and edit this file by hand if needed."
    }
  }
}
JSON
}

if [ "$MODE" = "peek" ]; then
  snapshot
  exit 0
fi

# Atomic write: stage to .tmp then rename. Avoids partial files if killed mid-write.
TMP="${OUTPUT_FILE}.$$.tmp"
trap 'rm -f "$TMP"' EXIT
snapshot > "$TMP"
mv "$TMP" "$OUTPUT_FILE"
trap - EXIT

log "Wrote: ${OUTPUT_FILE}"
log "Preferred transport: ${PREFERRED}"
$CLI_PRESENT && log "  CLI:        ${CLI_BINARY} (${CLI_VERSION_RAW})"
log "  Filesystem: always available (Read/Write/Edit tools)"
log "  MCP:        not auto-detected (see wiki/references/mcp-setup.md to configure)"
