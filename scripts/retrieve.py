#!/usr/bin/env python3
"""retrieve.py — hybrid retrieval orchestrator for the Compound Vault.

Pipeline:
  query  →  bm25-index.py query (top-K candidates by BM25 over contextualized chunks)
         →  rerank.py        (optional cosine on selected Ollama embeddings,
                              or no-op if ollama unavailable)
         →  drill            (return chunk pages with absolute paths so the
                              caller can Read them and synthesize)

Loads sibling scripts as Python modules (no subprocess overhead). Falls back
gracefully when index or rerank stage is missing:
- If .vault-meta/bm25/index.json is absent     → exit 10 with friendly message;
                                                  caller falls back to v1.6 legacy
                                                  hot→index→drill read order.
- If .vault-meta/chunks/ is empty              → exit 10 (same).
- If rerank stage cannot embed (no ollama)     → no-op rerank, returns BM25 order.

Output schema (JSON to stdout):
{
  "query": "...",
  "strategy": "bm25+rerank:cosine:<model>" | "bm25+noop-rerank",
  "top_k": 5,
  "candidates": [
    {
      "chunk_id": "c-000042:3",
      "page_address": "c-000042",
      "page_path": "wiki/concepts/Foo.md",
      "absolute_path": "/abs/path/to/wiki/concepts/Foo.md",
      "chunk_index": 3,
      "bm25_score": 7.12,
      "rerank_score": 0.81,
      "rerank_source": "cosine:<selected-model>",
      "snippet": "... first 200 chars of the chunk ..."
    },
    ...
  ]
}

Usage:
  retrieve.py --vault PATH "query"      # select a vault explicitly
  retrieve.py "your query here"           # standard: BM25 top-20, rerank to top-5
  retrieve.py "query" --top 10            # change result count
  retrieve.py "query" --no-rerank         # skip rerank, BM25-only
  retrieve.py "query" --model nomic-embed-text  # explicit v1.5 reranker
  retrieve.py "query" --explain           # include per-stage diagnostics

Exit codes:
  0 — success
  2 — usage error
  10 — feature unavailable (missing/corrupt index or no chunks); caller falls
       back to the standard vault query path and may rebuild derived caches
"""

import argparse
import hashlib
import importlib.util
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from claude_obsidian.paths import VaultSelectionError, resolve_vault_root
from claude_obsidian.transaction import TransactionError, _safe_vault_path

VAULT_ROOT = Path.cwd().resolve()
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
MAX_TOP_RESULTS = 1_000


def parse_top_k(value):
    """Parse a positive, bounded result count for command-line callers."""
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if not 1 <= parsed <= MAX_TOP_RESULTS:
        raise argparse.ArgumentTypeError(
            f"must be between 1 and {MAX_TOP_RESULTS}"
        )
    return parsed
META_DIR = VAULT_ROOT / ".vault-meta"
CHUNKS_DIR = META_DIR / "chunks"
BM25_INDEX = META_DIR / "bm25" / "index.json"
WIKI_DIR = VAULT_ROOT / "wiki"

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_NOT_PROVISIONED = 10


def configure_vault(explicit=None):
    global VAULT_ROOT, META_DIR, CHUNKS_DIR, BM25_INDEX, WIKI_DIR
    try:
        selected = resolve_vault_root(
            explicit,
            start=Path.cwd(),
            plugin_root=PLUGIN_ROOT,
        )
    except VaultSelectionError as exc:
        log(f"ERR {exc.code}: {exc}")
        return False
    VAULT_ROOT = selected.root
    META_DIR = VAULT_ROOT / ".vault-meta"
    CHUNKS_DIR = META_DIR / "chunks"
    BM25_INDEX = META_DIR / "bm25" / "index.json"
    WIKI_DIR = VAULT_ROOT / "wiki"
    try:
        for relative in (
            ".vault-meta",
            ".vault-meta/chunks",
            ".vault-meta/bm25/index.json",
            "wiki",
        ):
            _safe_vault_path(VAULT_ROOT, relative)
    except (VaultSelectionError, TransactionError) as exc:
        log(f"ERR {exc.code}: {exc}")
        return False
    return True


def log(msg):
    print(msg, file=sys.stderr)


def import_sibling(name, filename):
    """Import a hyphenated sibling .py file as a Python module.

    Wrapped in try/except (v1.7.2; closes audit M5) so a syntax error or
    missing dependency in a sibling helper produces a friendly diagnostic
    instead of a bare Python traceback at the user's first retrieve call.
    """
    target = SCRIPTS_DIR / filename
    if not target.is_file():
        log(f"ERR: sibling helper {filename} not found at {target}")
        log("  Run `bash scripts/setup-retrieve.sh --check` to verify the install.")
        sys.exit(EXIT_NOT_PROVISIONED)
    try:
        spec = importlib.util.spec_from_file_location(name, target)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot create import spec for {target}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except (ImportError, SyntaxError, AttributeError) as e:
        log(f"ERR: failed to import sibling helper {filename}: {type(e).__name__}: {e}")
        log("  This likely means the helper script is corrupted or has a syntax error.")
        log("  Run `python3 scripts/<helper>.py --help` directly to see the underlying error.")
        log("  If it persists: re-clone the repo or check `git status` for local damage.")
        sys.exit(EXIT_NOT_PROVISIONED)


def chunk_snippet(chunk_data, max_chars=200):
    text = chunk_data.get("raw_text", "")
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def sha256(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_sha256(value):
    return isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def resolve_vault_file(relative_path, required_root=None):
    """Resolve a relative path without allowing it to escape the vault."""
    if not isinstance(relative_path, str) or not relative_path:
        return None
    rel = Path(relative_path)
    if rel.is_absolute():
        return None
    root = VAULT_ROOT.resolve()
    resolved = (root / rel).resolve()
    boundary = (required_root or VAULT_ROOT).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_relative_to(boundary):
        return None
    return resolved if resolved.is_file() else None


def chunk_is_current(hit, chunk, page_path, page_hash_cache):
    """Reject chunk/index records stale relative to each other or their page."""
    expected_chunk_id = f"{chunk.get('page_address')}:{chunk.get('chunk_index')}"
    if hit.get("chunk_id") != expected_chunk_id:
        return False

    raw_text = chunk.get("raw_text")
    body_hash = chunk.get("body_hash")
    page_hash = chunk.get("page_body_hash")
    if not isinstance(raw_text, str) or not valid_sha256(body_hash):
        return False
    if sha256(raw_text) != body_hash or not valid_sha256(page_hash):
        return False

    indexed_body_hash = hit.get("body_hash")
    if not valid_sha256(indexed_body_hash) or indexed_body_hash != body_hash:
        return False
    indexed_page_hash = hit.get("page_body_hash")
    if not valid_sha256(indexed_page_hash) or indexed_page_hash != page_hash:
        return False

    cache_key = str(page_path)
    if cache_key not in page_hash_cache:
        try:
            # read_bytes keeps CRLF content byte-identical with the hash the
            # chunker computed; read_text would normalize newlines and drop
            # every candidate as stale on CRLF vaults.
            page_hash_cache[cache_key] = sha256(
                page_path.read_bytes().decode("utf-8", errors="replace")
            )
        except OSError:
            page_hash_cache[cache_key] = None
    return page_hash_cache[cache_key] == page_hash


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hybrid retrieval over the vault.")
    parser.add_argument("--vault", help="Explicit vault root")
    parser.add_argument("query", help="Natural-language query")
    parser.add_argument("--top", type=parse_top_k, default=5, help="Final result count (post-rerank)")
    parser.add_argument("--bm25-top", type=parse_top_k, default=20,
                        help="Candidate count from BM25 (pre-rerank)")
    parser.add_argument("--no-rerank", action="store_true",
                        help="Skip the rerank stage; return BM25-only")
    parser.add_argument(
        "--model",
        help=(
            "Installed Ollama embedding model; defaults to multilingual "
            "nomic-embed-text-v2-moe and is never downloaded automatically"
        ),
    )
    parser.add_argument("--explain", action="store_true",
                        help="Include per-stage diagnostics in output")
    parser.add_argument("--allow-remote-ollama", action="store_true",
                        help="Forwarded to rerank.py")
    args = parser.parse_args(argv)
    if not configure_vault(args.vault):
        return EXIT_USAGE

    reranker = import_sibling("rerank", "rerank.py")
    try:
        selected_model = reranker.validate_model_name(
            args.model or reranker.DEFAULT_MODEL
        )
    except ValueError as exc:
        log(f"ERR: invalid --model: {exc}")
        return EXIT_USAGE

    if not BM25_INDEX.is_file():
        log(f"ERR: no BM25 index at {BM25_INDEX}. Run `bash scripts/setup-retrieve.sh` "
            "to provision, or fall back to legacy hot→index→drill.")
        return EXIT_NOT_PROVISIONED
    if not CHUNKS_DIR.is_dir() or not any(CHUNKS_DIR.iterdir()):
        log(f"ERR: no chunks at {CHUNKS_DIR}. Run "
            "`python3 scripts/contextual-prefix.py --all` first.")
        return EXIT_NOT_PROVISIONED

    bm25 = import_sibling("bm25_index", "bm25-index.py")
    if not bm25.configure_vault(str(VAULT_ROOT)):
        return EXIT_NOT_PROVISIONED
    if not reranker.configure_vault(str(VAULT_ROOT)):
        return EXIT_NOT_PROVISIONED

    try:
        bm25_hits = bm25.query(args.query, top_k=args.bm25_top)
    except bm25.QueryTooLargeError as exc:
        log(f"ERR BM25_QUERY_TOO_LARGE: {exc}. Shorten the query and retry.")
        return EXIT_USAGE
    except SystemExit as exc:
        if exc.code != getattr(bm25, "EXIT_INDEX_MISSING", 3):
            raise
        log("ERR RETRIEVAL_INDEX_UNAVAILABLE: the BM25 index is missing or corrupt.")
        log(
            "  Rebuild with: python3 scripts/bm25-index.py "
            f"--vault {shlex.quote(str(VAULT_ROOT))} build"
        )
        log("  Until rebuilt, fall back to the standard vault query/text-search path.")
        return EXIT_NOT_PROVISIONED
    log(f"bm25: {len(bm25_hits)} hits")

    candidates: list[dict[str, Any]] = []
    stale_candidates = 0
    page_hash_cache: dict[str, str | None] = {}
    for h in bm25_hits:
        chunk_path = resolve_vault_file(h.get("path"), required_root=CHUNKS_DIR)
        if chunk_path is None:
            stale_candidates += 1
            continue
        try:
            chunk = json.loads(chunk_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            stale_candidates += 1
            continue
        page_path = resolve_vault_file(chunk.get("page_path"), required_root=WIKI_DIR)
        if page_path is None or not chunk_is_current(h, chunk, page_path, page_hash_cache):
            stale_candidates += 1
            continue
        candidates.append({
            "chunk_id": h["chunk_id"],
            "page_address": chunk.get("page_address"),
            "page_path": chunk.get("page_path"),
            "absolute_path": str(page_path),
            "chunk_index": chunk.get("chunk_index"),
            "bm25_score": h["score"],
            "path": h["path"],
            "snippet": chunk_snippet(chunk),
        })

    if args.no_rerank:
        final = candidates
        strategy = "bm25-only"
        for c in final:
            c["rerank_score"] = c["bm25_score"]
            c["rerank_source"] = "skipped"
    elif not candidates:
        final = []
        strategy = "bm25+noop-rerank:no-current-candidates"
    else:
        final = reranker.rerank(
            args.query, candidates, top_k=len(candidates),
            allow_remote=args.allow_remote_ollama,
            model=selected_model,
        )
        # Derive strategy from first candidate's rerank_source
        first_src = (final[0].get("rerank_source") if final else "unknown")
        strategy = f"bm25+rerank:{first_src}"

    # Dedupe after ranking the full candidate set. Truncating first can return
    # fewer than --top pages when several high-scoring chunks share one page.
    by_page: dict[object, dict[str, Any]] = {}
    for c in final:
        addr = c.get("page_address") or c.get("page_path")
        if addr not in by_page or c.get("rerank_score", 0) > by_page[addr].get("rerank_score", 0):
            by_page[addr] = c
    deduped = list(by_page.values())
    deduped.sort(key=lambda c: c.get("rerank_score", 0), reverse=True)

    out = {
        "query": args.query,
        "strategy": strategy,
        "top_k": args.top,
        "candidates": deduped[:args.top],
    }
    if args.explain:
        out["explain"] = {
            "bm25_candidate_count": len(bm25_hits),
            "post_rerank_count": len(final),
            "deduped_count": len(deduped),
            "bm25_top_param": args.bm25_top,
            "rerank_model": None if args.no_rerank else selected_model,
            "stale_candidates_skipped": stale_candidates,
        }

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
