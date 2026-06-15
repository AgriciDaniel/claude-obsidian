#!/usr/bin/env bash
# setup-retrieve.sh — opt-in bootstrap for wiki-retrieve (v1.7+).
#
# Provisions the contextual-prefix + BM25 + rerank pipeline. Idempotent;
# safe to re-run after schema changes or full vault re-ingest.
#
# What this does (in order):
#   1. Sanity-check that scripts/contextual-prefix.py, bm25-index.py,
#      rerank.py, retrieve.py are present and executable.
#   2. Create .vault-meta/chunks/ and .vault-meta/bm25/ directories.
#   3. Check for ollama + nomic-embed-text (informational; not required for
#      contextual prefix tier 2/3, but required for the rerank cosine stage).
#   4. Data-egress consent (v1.7.1+). If a non-synthetic prefix tier
#      (anthropic-api or claude-cli) would otherwise be chosen, prompt
#      the user for explicit y/N consent. Default is abort (synthetic-only
#      remains the safe alternative). On consent, pass --allow-egress
#      through to contextual-prefix.py. Pass --no-llm at the CLI to skip
#      the prompt entirely and stay on tier-3 (synthetic).
#   5. Run contextual-prefix.py --all to chunk + contextualize every wiki page.
#      Tier picker (synthetic by default; non-synthetic only with consent):
#        tier 1: Anthropic API   (--allow-egress + ANTHROPIC_API_KEY set)
#        tier 2: claude CLI -p   (--allow-egress + `claude` on PATH)
#        tier 3: synthetic       (no flag, --no-llm, or no consent)
#      Stage 1 exit code is captured; non-zero aborts with a recovery hint
#      (rc=5) before Stage 2.
#   6. Run bm25-index.py build to build the inverted index.
#
# After completion the wiki-retrieve skill is "feature-detected" by other
# skills (wiki-query checks for scripts/retrieve.py + .vault-meta/chunks/).
#
# This is fully opt-in. Doing nothing leaves v1.6 behavior intact.
#
# Usage:
#   bash bin/setup-retrieve.sh
#   bash bin/setup-retrieve.sh --no-llm     # force tier-3 synthetic-only
#   bash bin/setup-retrieve.sh --rebuild    # rebuild all chunks
#   bash bin/setup-retrieve.sh --check      # diagnostics only; no provisioning

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="$(dirname "$SCRIPT_DIR")"
META="$VAULT/.vault-meta"

NO_LLM=false
REBUILD=false
CHECK_ONLY=false

while [ $# -gt 0 ]; do
  case "$1" in
    --no-llm)   NO_LLM=true ;;
    --rebuild)  REBUILD=true ;;
    --check)    CHECK_ONLY=true ;;
    -h|--help)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "ERR: unknown flag: $1" >&2
      exit 2
      ;;
  esac
  shift
done

say() { printf '%s\n' "$@"; }
warn() { printf 'WARN: %s\n' "$@" >&2; }

say "═══ wiki-retrieve setup (v1.7+) ═══"
say "Vault: $VAULT"
say ""

# ── 1. Sanity check ──────────────────────────────────────────────────────────
REQUIRED=(
  "$VAULT/scripts/contextual-prefix.py"
  "$VAULT/scripts/bm25-index.py"
  "$VAULT/scripts/rerank.py"
  "$VAULT/scripts/retrieve.py"
)
missing=0
for f in "${REQUIRED[@]}"; do
  if [ ! -x "$f" ]; then
    warn "missing or not executable: $f"
    missing=$((missing+1))
  fi
done
if [ $missing -gt 0 ]; then
  say "FAIL: $missing required script(s) missing."
  exit 3
fi
say "✓ All 4 retrieval scripts present and executable"

# ── 2. Provision .vault-meta state directories ───────────────────────────────
mkdir -p "$META/chunks" "$META/bm25"
say "✓ State directories: $META/chunks/, $META/bm25/"

# ── 3. Check ollama (informational) ──────────────────────────────────────────
OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
# v1.9.1 / closes audit S4: if OLLAMA_URL was overridden to point off-machine,
# refuse to probe unless the caller passes --allow-remote-ollama (mirrors the
# existing scripts/tiling-check.py:351 gate). Same allowlist of localhost
# patterns ollama itself recommends.
case "$OLLAMA_URL" in
  "http://127.0.0.1:"*|"http://localhost:"*|"http://[::1]:"*) ;;
  *)
    if ! printf '%s ' "$@" | grep -q -- '--allow-remote-ollama'; then
      warn "OLLAMA_URL points off-localhost: $OLLAMA_URL"
      warn "Refusing to probe remote ollama without explicit consent."
      warn "Pass --allow-remote-ollama to bin/setup-retrieve.sh to opt in, or"
      warn "unset OLLAMA_URL to use the default http://127.0.0.1:11434."
      OLLAMA_URL=""
    fi
    ;;
esac
OLLAMA_ALIVE=false
MODEL_PRESENT=false
if [ -n "$OLLAMA_URL" ] && command -v curl >/dev/null 2>&1; then
  if curl -fsS --max-time 3 "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
    OLLAMA_ALIVE=true
    if curl -fsS --max-time 3 "$OLLAMA_URL/api/tags" 2>/dev/null \
       | grep -q '"nomic-embed-text'; then
      MODEL_PRESENT=true
    fi
  fi
fi
if $OLLAMA_ALIVE && $MODEL_PRESENT; then
  say "✓ ollama reachable at $OLLAMA_URL with nomic-embed-text pulled (rerank will use cosine)"
elif $OLLAMA_ALIVE; then
  warn "ollama reachable but nomic-embed-text is not pulled. Run: ollama pull nomic-embed-text"
  warn "rerank stage will no-op until the model is available."
else
  warn "ollama not reachable at $OLLAMA_URL"
  warn "rerank stage will no-op until ollama is running. BM25 retrieval still works."
  warn "Install: https://ollama.com/download; then: ollama pull nomic-embed-text"
fi

# ── 4. Prefix-tier picker (informational) ────────────────────────────────────
# v1.7.1: tier reflects what WOULD run if --allow-egress were passed.
# Without consent, the actual run forces tier-3 synthetic.
if $NO_LLM; then
  PREFIX_TIER="synthetic (forced via --no-llm)"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  PREFIX_TIER="anthropic-api (ANTHROPIC_API_KEY detected; ~\$12/1000 docs)"
elif command -v claude >/dev/null 2>&1; then
  PREFIX_TIER="claude-cli subprocess (no API key needed; uses CC subscription)"
else
  PREFIX_TIER="synthetic (no API key, no claude CLI; reduced retrieval quality)"
fi
say "✓ Contextual-prefix tier (if --allow-egress): $PREFIX_TIER"

if $CHECK_ONLY; then
  say ""
  say "── --check passed; not provisioning."
  exit 0
fi

# ── 4b. Egress consent (v1.7.1) ──────────────────────────────────────────────
# If a non-synthetic tier would otherwise be selected, require explicit consent
# before letting contextual-prefix.py send page bodies off-machine. Mirrors the
# --allow-remote-ollama precedent in scripts/tiling-check.py.
ALLOW_EGRESS=false
if ! $NO_LLM; then
  case "$PREFIX_TIER" in
    anthropic-api*|claude-cli*)
      say ""
      say "⚠️  Stage 1 will send wiki page BODIES off-machine via the '$PREFIX_TIER' tier."
      say "    Estimated cost: ~\$0 (claude-cli, free) to ~\$12 per 1,000 pages (Anthropic API)."
      say "    Per-page bodies are POSTed to the provider; review their privacy policy first."
      say "    Default is NO. Tier-3 (synthetic, on-machine) is the safe alternative."
      printf "    Continue with egress? [y/N]: "
      read -r reply || reply=""
      case "$reply" in
        [yY]|[yY][eE][sS])
          say "→ Proceeding with egress."
          ALLOW_EGRESS=true
          ;;
        *)
          say "→ Aborted. Re-run with --no-llm for the synthetic-only path,"
          say "  or set ANTHROPIC_API_KEY and use the claude CLI deliberately."
          exit 0
          ;;
      esac
      ;;
  esac
fi

# ── 5. Chunk + contextualize every wiki page ─────────────────────────────────
say ""
say "═══ Stage 1/2: chunking + contextual-prefix generation ═══"
ARGS=("--all")
$NO_LLM && ARGS+=("--no-llm")
$ALLOW_EGRESS && ARGS+=("--allow-egress")
$REBUILD && ARGS+=("--rebuild")
# Disable set -e for the call so we can inspect the exit code and offer a
# concrete recovery hint instead of aborting with a bare trace.
set +e
python3 "$VAULT/scripts/contextual-prefix.py" "${ARGS[@]}"
STAGE1_RC=$?
set -e
if [ "$STAGE1_RC" -ne 0 ]; then
  warn "Stage 1 failed (rc=$STAGE1_RC). Partial chunks may exist at:"
  warn "  $META/chunks/"
  warn "Recovery options:"
  warn "  1. Re-run setup-retrieve.sh — body_hash skips already-processed chunks."
  warn "  2. Wipe and start over:  rm -rf $META/chunks/ && bash bin/setup-retrieve.sh"
  warn "  3. Re-process one page:  python3 scripts/contextual-prefix.py wiki/<failing-page>.md --rebuild"
  exit 5
fi

# ── 6. Build BM25 index ──────────────────────────────────────────────────────
say ""
say "═══ Stage 2/2: BM25 index build ═══"
python3 "$VAULT/scripts/bm25-index.py" build

# ── 7. Smoke-test retrieve.py ────────────────────────────────────────────────
say ""
say "═══ Smoke test ═══"
SMOKE_OUT="$(python3 "$VAULT/scripts/retrieve.py" "wiki" --top 1 2>/dev/null || echo '{}')"
if echo "$SMOKE_OUT" | grep -q '"candidates":'; then
  say "✓ retrieve.py returns valid JSON"
else
  warn "retrieve.py smoke test produced unexpected output. Run manually for details."
fi

say ""
say "═══ wiki-retrieve is provisioned. ═══"
say ""
say "Usage from the command line:"
say "  python3 scripts/retrieve.py \"your question here\" --top 5"
say ""
say "Other skills (wiki-query, autoresearch) will now automatically use the"
say "hybrid pipeline when answering questions. See skills/wiki-retrieve/SKILL.md."
