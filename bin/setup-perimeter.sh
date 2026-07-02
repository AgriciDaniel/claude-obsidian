#!/usr/bin/env bash
# setup-perimeter.sh — opt-in privacy perimeter for vaults with sensitive data.
#
# Installs two git hooks that enforce a deny-by-default privacy boundary:
#
#   pre-commit  Blocks the commit if (1) a staged path matches a sensitive
#               band (glob list), or (2) an ADDED line in the staged diff
#               matches an identifier/secret pattern (regex list), minus a
#               whitelist of known false positives.
#   pre-push    If air-gap mode is enabled, blocks EVERY push. For vaults
#               that must never leave the machine.
#
# Config lives in three plain-text files under .vault-meta/ (one entry per
# line, `#` comments), seeded with commented examples on first run:
#
#   perimeter-paths.txt      staged-path globs to block (e.g. private/*)
#   perimeter-patterns.txt   regexes for added lines (secrets baseline included)
#   perimeter-whitelist.txt  exact-token regexes to accept (false positives)
#
# The hooks are data-local: no network, nothing leaves the repo. Overrides
# are single-shot and explicit:
#
#   PERIMETER_ALLOW=1 git commit ...       # skip the pre-commit gate once
#   PERIMETER_ALLOW_PUSH=1 git push ...    # lift the air-gap for one push
#
# Usage:
#   bash bin/setup-perimeter.sh              # interactive
#   bash bin/setup-perimeter.sh --yes        # non-interactive (CI / scripts)
#   bash bin/setup-perimeter.sh --air-gap    # also enable the push block
#   bash bin/setup-perimeter.sh --check      # diagnostics only, no write
#   bash bin/setup-perimeter.sh --uninstall  # remove managed hooks, restore backups
#
# Existing unmanaged hooks are backed up to <hook>.pre-perimeter.bak and
# restored on --uninstall. Idempotent — safe to re-run.
#
# Exit codes: 0 success, 2 usage error, 3 not a git repository.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="$(dirname "$SCRIPT_DIR")"
MARKER="managed-by: claude-obsidian setup-perimeter"

ASSUME_YES=false
AIR_GAP=false
CHECK_ONLY=false
UNINSTALL=false

while [ $# -gt 0 ]; do
  case "$1" in
    --yes)       ASSUME_YES=true; shift ;;
    --air-gap)   AIR_GAP=true; shift ;;
    --check)     CHECK_ONLY=true; shift ;;
    --uninstall) UNINSTALL=true; shift ;;
    -h|--help)   sed -n '2,38p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "ERR: unknown flag: $1" >&2; exit 2 ;;
  esac
done

say()  { printf '%s\n' "$@"; }
warn() { printf 'WARN: %s\n' "$@" >&2; }

GIT_DIR="$(cd "$VAULT" && git rev-parse --git-dir 2>/dev/null || true)"
if [ -z "$GIT_DIR" ]; then
  warn "not a git repository: $VAULT — the perimeter needs git hooks."
  exit 3
fi
case "$GIT_DIR" in
  /*|[A-Za-z]:*) HOOKS="$GIT_DIR/hooks" ;;
  *)             HOOKS="$VAULT/$GIT_DIR/hooks" ;;
esac
META="$VAULT/.vault-meta"

is_managed() { [ -f "$1" ] && grep -q "$MARKER" "$1"; }

hook_status() {
  local h="$1"
  if is_managed "$HOOKS/$h"; then echo "managed"
  elif [ -f "$HOOKS/$h" ]; then echo "unmanaged"
  else echo "absent"; fi
}

say "═══ privacy perimeter setup ═══"
say "Vault: $VAULT"
say ""

if [ "$CHECK_ONLY" = true ]; then
  say "pre-commit:  $(hook_status pre-commit)"
  say "pre-push:    $(hook_status pre-push)"
  [ -f "$META/perimeter-airgap" ] && say "air-gap:     ENABLED (pushes blocked)" \
                                   || say "air-gap:     disabled"
  for cfg in perimeter-paths.txt perimeter-patterns.txt perimeter-whitelist.txt; do
    if [ -f "$META/$cfg" ]; then
      n=$(grep -cvE '^[[:space:]]*(#|$)' "$META/$cfg" || true)
      say "config:      $cfg ($n active entries)"
    else
      say "config:      $cfg (missing)"
    fi
  done
  exit 0
fi

if [ "$UNINSTALL" = true ]; then
  for h in pre-commit pre-push; do
    if is_managed "$HOOKS/$h"; then
      rm -f "$HOOKS/$h"
      say "removed managed hook: $h"
      if [ -f "$HOOKS/$h.pre-perimeter.bak" ]; then
        mv "$HOOKS/$h.pre-perimeter.bak" "$HOOKS/$h"
        say "restored backup:      $h.pre-perimeter.bak -> $h"
      fi
    else
      say "skip $h: $(hook_status "$h") (not managed by this setup)"
    fi
  done
  rm -f "$META/perimeter-airgap"
  say "air-gap flag removed. Config files under .vault-meta/ kept (delete manually if unwanted)."
  exit 0
fi

# ── Consent ─────────────────────────────────────────────────────────────────
say "This installs git pre-commit + pre-push hooks in this repository."
say "They run locally on every commit/push; nothing leaves your machine."
if [ "$ASSUME_YES" != true ]; then
  printf 'Proceed? [y/N] '
  read -r reply
  case "$reply" in y|Y|yes|YES) ;; *) say "Aborted. Nothing written."; exit 0 ;; esac
fi

mkdir -p "$META" "$HOOKS"

# ── Seed config files (never overwrite user edits) ──────────────────────────
if [ ! -f "$META/perimeter-paths.txt" ]; then
  cat > "$META/perimeter-paths.txt" <<'EOF'
# perimeter-paths.txt — staged-path globs that must NEVER be committed.
# One glob per line, matched against the repo-relative staged path.
# Examples (uncomment / adapt):
#   private/*
#   journal/*
#   */secrets/*
#   *.db
EOF
  say "seeded: .vault-meta/perimeter-paths.txt (edit to add your sensitive bands)"
fi

if [ ! -f "$META/perimeter-patterns.txt" ]; then
  cat > "$META/perimeter-patterns.txt" <<'EOF'
# perimeter-patterns.txt — regexes checked against ADDED lines in the staged
# diff (grep -E syntax). One per line. A generic secrets baseline is always
# active in the hook itself; add identifier formats for your jurisdiction here.
# Examples (uncomment / adapt):
# Spanish national ID (DNI/NIE) and company ID (CIF):
#   \b[0-9]{8}[A-Za-z]\b
#   \b[XYZxyz][0-9]{7}[A-Za-z]\b
#   \b[A-HJNPQRSUVWa-hjnpqrsuvw][0-9]{7}[0-9A-Ja-j]\b
# US Social Security number:
#   \b[0-9]{3}-[0-9]{2}-[0-9]{4}\b
EOF
  say "seeded: .vault-meta/perimeter-patterns.txt (edit to add PII formats)"
fi

if [ ! -f "$META/perimeter-whitelist.txt" ]; then
  cat > "$META/perimeter-whitelist.txt" <<'EOF'
# perimeter-whitelist.txt — exact-token regexes that are known false
# positives (public registry codes, documented test IDs). One per line.
# Example:
#   ^12345678Z$
EOF
  say "seeded: .vault-meta/perimeter-whitelist.txt"
fi

# ── Back up unmanaged hooks, then install ───────────────────────────────────
for h in pre-commit pre-push; do
  if [ -f "$HOOKS/$h" ] && ! is_managed "$HOOKS/$h"; then
    cp "$HOOKS/$h" "$HOOKS/$h.pre-perimeter.bak"
    warn "existing $h hook backed up to $h.pre-perimeter.bak (restored on --uninstall)"
  fi
done

cat > "$HOOKS/pre-commit" <<'HOOK'
#!/usr/bin/env bash
# managed-by: claude-obsidian setup-perimeter v1
# Privacy perimeter — blocks committing sensitive paths and leaked identifiers.
# Single-shot override (use with eyes open):  PERIMETER_ALLOW=1 git commit ...
set -euo pipefail
[ "${PERIMETER_ALLOW:-0}" = "1" ] && { echo "perimeter: override active — commit allowed." >&2; exit 0; }

ROOT="$(git rev-parse --show-toplevel)"
META="$ROOT/.vault-meta"
staged=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$staged" ] && exit 0
viol=0

# (1) Sensitive path bands — name check only, cheap even on huge commits.
if [ -f "$META/perimeter-paths.txt" ]; then
  while IFS= read -r pat; do
    pat="${pat%%#*}"
    pat="$(printf '%s' "$pat" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [ -z "$pat" ] && continue
    while IFS= read -r f; do
      # shellcheck disable=SC2254  # unquoted on purpose: config line is a glob
      case "$f" in
        $pat)
          echo "BLOCK: sensitive path staged: $f  (matches '$pat')" >&2
          viol=1 ;;
      esac
    done <<< "$staged"
  done < "$META/perimeter-paths.txt"
fi

# (2) Identifier/secret patterns in ADDED lines — one pass over the whole diff.
SECRET_RE='BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|(^|[^A-Za-z])(password|passwd|api[_-]?key|secret|token)[[:space:]]*[:=][[:space:]]*[^[:space:]]'
user_re=""
if [ -f "$META/perimeter-patterns.txt" ]; then
  user_re="$(grep -vE '^[[:space:]]*(#|$)' "$META/perimeter-patterns.txt" | sed 's/^[[:space:]]*//' | paste -sd'|' -)"
fi
pat_re="$SECRET_RE"
[ -n "$user_re" ] && pat_re="$pat_re|$user_re"

wl_re='^$'
if [ -f "$META/perimeter-whitelist.txt" ]; then
  wl="$(grep -vE '^[[:space:]]*(#|$)' "$META/perimeter-whitelist.txt" | sed 's/^[[:space:]]*//' | paste -sd'|' -)"
  [ -n "$wl" ] && wl_re="$wl"
fi

hits=$(git diff --cached -U0 --diff-filter=ACM 2>/dev/null \
        | grep -E '^\+' | grep -vE '^\+\+\+' \
        | grep -oE "$pat_re" 2>/dev/null | sort -u | grep -vE "$wl_re" || true)
if [ -n "$hits" ]; then
  echo "BLOCK: possible identifier/secret in staged additions:" >&2
  echo "$hits" | head -10 | sed 's/^/    /' >&2
  viol=1
fi

if [ "$viol" = "1" ]; then
  echo "" >&2
  echo "Commit blocked by the privacy perimeter. Redact/anonymize, adjust" >&2
  echo ".vault-meta/perimeter-*.txt, or (known false positive, single shot):" >&2
  echo "  PERIMETER_ALLOW=1 git commit ..." >&2
  exit 1
fi
exit 0
HOOK
chmod +x "$HOOKS/pre-commit"
say "installed: pre-commit (path bands + identifier scan)"

cat > "$HOOKS/pre-push" <<'HOOK'
#!/usr/bin/env bash
# managed-by: claude-obsidian setup-perimeter v1
# Air-gap guard — when enabled, this repository never pushes to any remote.
# Single-shot override:  PERIMETER_ALLOW_PUSH=1 git push ...
if [ "${PERIMETER_ALLOW_PUSH:-0}" = "1" ]; then
  echo "perimeter: air-gap override active — allowing this push." >&2
  exit 0
fi
ROOT="$(git rev-parse --show-toplevel)"
if [ -f "$ROOT/.vault-meta/perimeter-airgap" ]; then
  echo "" >&2
  echo "AIR-GAP: push blocked. This vault is air-gapped by design." >&2
  echo "  One push only:  PERIMETER_ALLOW_PUSH=1 git push <...>" >&2
  echo "  Disable:        rm .vault-meta/perimeter-airgap" >&2
  echo "" >&2
  exit 1
fi
exit 0
HOOK
chmod +x "$HOOKS/pre-push"
say "installed: pre-push (air-gap guard)"

if [ "$AIR_GAP" = true ]; then
  printf 'enabled %s\n' "$(date '+%Y-%m-%d')" > "$META/perimeter-airgap"
  say "air-gap: ENABLED — every push from this repo is now blocked."
else
  say "air-gap: not enabled (pass --air-gap for vaults that must never push)."
fi

say ""
say "Done. Edit .vault-meta/perimeter-paths.txt and perimeter-patterns.txt to"
say "match your vault's sensitive bands, then test with a dummy commit."
exit 0
