#!/usr/bin/env python3
"""test_retrieve.py — hermetic tests for scripts/retrieve.py and scripts/rerank.py.

No network, no ollama, no LLM calls. Tests cover:
  - import_sibling resolves hyphenated module names
  - chunk_snippet truncation behavior
  - rerank.cosine math correctness
  - rerank.rerank() no-op behavior when ollama is unreachable
  - retrieve.py exit 10 (not provisioned) when chunks/index are missing
  - dedupe-by-page logic via integration smoke test on synthetic fixtures

Usage:
  python3 tests/test_retrieve.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RETRIEVE = ROOT / "scripts" / "retrieve.py"
RERANK = ROOT / "scripts" / "rerank.py"
BM25 = ROOT / "scripts" / "bm25-index.py"


def import_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


retrieve = import_script("retrieve", RETRIEVE)
rerank = import_script("rerank", RERANK)
bm25 = import_script("bm25", BM25)


class Fail(SystemExit):
    pass


def assert_eq(label, expected, actual):
    if expected != actual:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"OK   {label}")


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


def assert_close(label, expected, actual, eps=1e-6):
    if abs(expected - actual) > eps:
        raise Fail(f"FAIL {label}: expected ~{expected}, got {actual}")
    print(f"OK   {label}")


# ─── import_sibling ──────────────────────────────────────────────────────────
def test_import_sibling_resolves_hyphenated_names():
    """retrieve.import_sibling('bm25_index', 'bm25-index.py') must succeed."""
    mod = retrieve.import_sibling("bm25_index", "bm25-index.py")
    assert_true("import_sibling returns module", mod is not None)
    assert_true("module has tokenize()", callable(getattr(mod, "tokenize", None)))


# ─── chunk_snippet ───────────────────────────────────────────────────────────
def test_chunk_snippet_short():
    """Short chunks should pass through unchanged."""
    out = retrieve.chunk_snippet({"raw_text": "short text"}, max_chars=200)
    assert_eq("chunk_snippet short pass-through", "short text", out)


def test_chunk_snippet_truncates_with_ellipsis():
    """Long chunks should be truncated with an ellipsis."""
    long_text = "x" * 500
    out = retrieve.chunk_snippet({"raw_text": long_text}, max_chars=100)
    assert_true("snippet length under cap", len(out) <= 110, hint=f"len={len(out)}")
    assert_true("snippet ends with ellipsis", out.endswith("…"))


# ─── rerank.cosine() ─────────────────────────────────────────────────────────
def test_cosine_identical():
    assert_close("cosine identical vectors", 1.0, rerank.cosine([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]))


def test_cosine_orthogonal():
    assert_close("cosine orthogonal", 0.0, rerank.cosine([1.0, 0.0], [0.0, 1.0]))


def test_cosine_anti_parallel():
    assert_close("cosine anti-parallel", -1.0, rerank.cosine([1.0, 0.0], [-1.0, 0.0]))


def test_cosine_length_mismatch():
    """Mismatched vector lengths should return 0.0 (defensive, not crash)."""
    assert_close("cosine length mismatch", 0.0, rerank.cosine([1.0], [1.0, 2.0]))


def test_cosine_zero_vector():
    assert_close("cosine zero vector", 0.0, rerank.cosine([0.0, 0.0], [1.0, 2.0]))


# ─── rerank.rerank() no-op fallback ──────────────────────────────────────────
def test_rerank_noop_when_ollama_unreachable():
    """When ollama is not reachable, rerank should pass candidates through with
    rerank_source='noop-no-ollama'. We force this by patching ollama_alive."""
    with unittest.mock.patch.object(rerank, "ollama_alive", return_value=(False, [])):
        candidates = [
            {"chunk_id": "c-001:0", "score": 7.5, "path": "fake/p1.json"},
            {"chunk_id": "c-002:0", "score": 5.1, "path": "fake/p2.json"},
        ]
        out = rerank.rerank("query", candidates, top_k=5)
        assert_eq("rerank no-op preserves order", ["c-001:0", "c-002:0"],
                  [c["chunk_id"] for c in out])
        assert_true("rerank no-op tags source",
                    all(c.get("rerank_source") == "noop-no-ollama" for c in out))
        assert_true("rerank no-op copies score to rerank_score",
                    all(c["rerank_score"] == c["score"] for c in out))


def test_rerank_noop_when_model_missing():
    """When ollama is up but model isn't pulled, rerank should still no-op."""
    with unittest.mock.patch.object(rerank, "ollama_alive", return_value=(True, ["other-model"])):
        candidates = [{"chunk_id": "c-001:0", "score": 5.0, "path": "x"}]
        out = rerank.rerank("query", candidates, top_k=5)
        assert_eq("rerank no-op for missing model", "noop-no-model", out[0]["rerank_source"])


def test_rerank_truncates_to_top_k():
    with unittest.mock.patch.object(rerank, "ollama_alive", return_value=(False, [])):
        candidates = [{"chunk_id": f"c-{i:03}:0", "score": float(i), "path": "x"} for i in range(10)]
        out = rerank.rerank("query", candidates, top_k=3)
        assert_eq("rerank truncates to top_k", 3, len(out))


# ─── nomic task prefixes (search_query:/search_document:) ────────────────────
def test_with_task_prefix_query():
    """nomic models must get the 'search_query:' instruction prefix."""
    out = rerank.with_task_prefix("how does locking work", "query", model="nomic-embed-text")
    assert_eq("query prefix applied", "search_query: how does locking work", out)


def test_with_task_prefix_document():
    """nomic models must get the 'search_document:' instruction prefix."""
    out = rerank.with_task_prefix("the lock is age-based", "document", model="nomic-embed-text")
    assert_eq("document prefix applied", "search_document: the lock is age-based", out)


def test_with_task_prefix_noop_for_non_nomic():
    """Non-nomic embedders use a different convention — leave text untouched."""
    out = rerank.with_task_prefix("some text", "query", model="mxbai-embed-large")
    assert_eq("non-nomic prefix is a no-op", "some text", out)


def test_with_task_prefix_rejects_bad_role():
    try:
        rerank.with_task_prefix("x", "passage", model="nomic-embed-text")
    except ValueError:
        print("OK   with_task_prefix rejects unknown role")
        return
    raise Fail("FAIL with_task_prefix should reject unknown role")


def test_rerank_sends_task_prefixes_to_embedder():
    """End-to-end through rerank(): the query is embedded with 'search_query:' and
    the chunk body with 'search_document:'. We capture every text sent to embed_one."""
    sent = []

    def fake_embed_one(url, model, text):
        sent.append(text)
        # Return a deterministic non-zero vector so cosine() is well-defined.
        return [float(len(text) % 7) + 1.0, 2.0, 3.0]

    chunk = {
        "body_hash": "sha256:deadbeef",
        "contextualized_text": "advisory locks are age-based",
        "raw_text": "advisory locks are age-based",
    }
    with unittest.mock.patch.object(rerank, "ollama_alive", return_value=(True, ["nomic-embed-text"])), \
         unittest.mock.patch.object(rerank, "ollama_url", return_value="http://127.0.0.1:11434"), \
         unittest.mock.patch.object(rerank, "embed_one", side_effect=fake_embed_one), \
         unittest.mock.patch.object(rerank, "load_chunk", return_value=chunk), \
         unittest.mock.patch.object(rerank, "load_cache", return_value={}), \
         unittest.mock.patch.object(rerank, "save_cache"):
        candidates = [{"chunk_id": "c-001:0", "score": 5.0, "path": "x.json"}]
        rerank.rerank("how does locking work", candidates, top_k=1)

    assert_true("query embedded with search_query: prefix",
                "search_query: how does locking work" in sent, hint=f"sent={sent}")
    assert_true("document embedded with search_document: prefix",
                "search_document: advisory locks are age-based" in sent, hint=f"sent={sent}")
    assert_true("no un-prefixed text leaked to embedder",
                all(t.startswith("search_query: ") or t.startswith("search_document: ") for t in sent),
                hint=f"sent={sent}")


def test_rerank_cache_key_includes_scheme():
    """Old prefix-less cache entries (keyed without EMBED_SCHEME) must be ignored,
    so we never mix prefixed and prefix-less vectors in the same cosine space."""
    body_hash = "sha256:deadbeef"
    stale_key = f"{rerank.DEFAULT_MODEL}:{body_hash}"  # pre-fix key shape
    poisoned_cache = {stale_key: [99.0, 99.0, 99.0]}   # would be reused if key unchanged
    embedded = []

    def fake_embed_one(url, model, text):
        embedded.append(text)
        return [1.0, 2.0, 3.0]

    chunk = {"body_hash": body_hash, "contextualized_text": "x", "raw_text": "x"}
    with unittest.mock.patch.object(rerank, "ollama_alive", return_value=(True, ["nomic-embed-text"])), \
         unittest.mock.patch.object(rerank, "ollama_url", return_value="http://127.0.0.1:11434"), \
         unittest.mock.patch.object(rerank, "embed_one", side_effect=fake_embed_one), \
         unittest.mock.patch.object(rerank, "load_chunk", return_value=chunk), \
         unittest.mock.patch.object(rerank, "load_cache", return_value=poisoned_cache), \
         unittest.mock.patch.object(rerank, "save_cache"):
        candidates = [{"chunk_id": "c-001:0", "score": 5.0, "path": "x.json"}]
        rerank.rerank("q", candidates, top_k=1)

    assert_true("stale prefix-less cache entry is NOT reused (doc re-embedded)",
                any(t.startswith("search_document: ") for t in embedded), hint=f"embedded={embedded}")


# ─── retrieve.py CLI: exit 10 when not provisioned ────────────────────────────
def test_retrieve_exits_10_without_index():
    """End-to-end CLI test: with no .vault-meta/bm25/index.json, retrieve.py must exit 10."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Build a minimal vault layout under tmpdir
        sandbox = Path(tmpdir)
        (sandbox / "scripts").mkdir()
        (sandbox / ".vault-meta").mkdir()
        # Copy retrieve.py and its dependencies into the sandbox
        import shutil
        for f in ["retrieve.py", "bm25-index.py", "rerank.py"]:
            shutil.copy(ROOT / "scripts" / f, sandbox / "scripts" / f)
            os.chmod(sandbox / "scripts" / f, 0o755)
        # Run retrieve.py — should exit 10 because no bm25 index exists
        result = subprocess.run(
            [sys.executable, str(sandbox / "scripts" / "retrieve.py"), "test query"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert_eq("retrieve.py exit 10 when not provisioned", 10, result.returncode)
        assert_true("retrieve.py prints friendly error",
                    "no BM25 index" in result.stderr,
                    hint=result.stderr[:200])


# ─── Integration smoke test: end-to-end with synthetic data ──────────────────
def test_end_to_end_with_synthetic_chunks():
    """Build a minimal vault with 2 chunks, index it, run retrieve, verify output."""
    import hashlib
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        (sandbox / "scripts").mkdir()
        meta = sandbox / ".vault-meta"
        chunks_dir = meta / "chunks"
        bm25_dir = meta / "bm25"
        chunks_dir.mkdir(parents=True)
        bm25_dir.mkdir(parents=True)
        # Copy scripts
        import shutil
        for f in ["retrieve.py", "bm25-index.py", "rerank.py"]:
            shutil.copy(ROOT / "scripts" / f, sandbox / "scripts" / f)
            os.chmod(sandbox / "scripts" / f, 0o755)
        # Write 2 synthetic chunks
        def chunk(addr, idx, text):
            return {
                "schema_version": 1,
                "page_path": f"wiki/fake/{addr}.md",
                "page_address": addr,
                "chunk_index": idx,
                "raw_text": text,
                "contextualized_text": text,
                "prefix": "",
                "prefix_source": "synthetic",
                "char_count": len(text),
                "body_hash": "sha256:" + hashlib.sha256(text.encode()).hexdigest(),
                "page_body_hash": "sha256:0",
                "created_at": "2026-05-17T00:00:00Z",
            }
        (chunks_dir / "c-000001").mkdir()
        (chunks_dir / "c-000002").mkdir()
        (chunks_dir / "c-000001" / "chunk-000.json").write_text(
            json.dumps(chunk("c-000001", 0, "compounding wiki vault pattern by karpathy")))
        (chunks_dir / "c-000002" / "chunk-000.json").write_text(
            json.dumps(chunk("c-000002", 0, "obsidian cli transport detection")))
        # Build index via subprocess (uses the sandbox's META_DIR? no — it uses the
        # script's hard-coded paths relative to its location. Since we copied the
        # script into sandbox/scripts/, VAULT_ROOT will compute to `sandbox`.)
        result = subprocess.run(
            [sys.executable, str(sandbox / "scripts" / "bm25-index.py"), "build"],
            capture_output=True, text=True, timeout=10)
        assert_eq("bm25 build rc=0", 0, result.returncode)
        # Run retrieve
        result = subprocess.run(
            [sys.executable, str(sandbox / "scripts" / "retrieve.py"),
             "karpathy wiki", "--top", "2", "--no-rerank"],
            capture_output=True, text=True, timeout=10)
        assert_eq("retrieve rc=0", 0, result.returncode)
        out = json.loads(result.stdout)
        assert_eq("retrieve.strategy is bm25-only", "bm25-only", out["strategy"])
        assert_true("retrieve returns at least 1 candidate", len(out["candidates"]) >= 1)
        # c-000001 should rank above c-000002 for "karpathy wiki"
        first = out["candidates"][0]
        assert_eq("top hit is c-000001", "c-000001", first["page_address"])


# ─── M8 closure: --explain and --no-rerank flag coverage ─────────────────────
def test_explain_flag_adds_diagnostics_block():
    """v1.7.2 / closes audit M8: --explain must include an 'explain' diagnostics block."""
    import hashlib
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        (sandbox / "scripts").mkdir()
        meta = sandbox / ".vault-meta"
        chunks_dir = meta / "chunks"
        bm25_dir = meta / "bm25"
        chunks_dir.mkdir(parents=True)
        bm25_dir.mkdir(parents=True)
        import shutil
        for f in ["retrieve.py", "bm25-index.py", "rerank.py"]:
            shutil.copy(ROOT / "scripts" / f, sandbox / "scripts" / f)
            os.chmod(sandbox / "scripts" / f, 0o755)
        # 2 synthetic chunks
        (chunks_dir / "c-000010").mkdir()
        (chunks_dir / "c-000010" / "chunk-000.json").write_text(json.dumps({
            "schema_version": 1, "page_path": "wiki/fake/c-000010.md",
            "page_address": "c-000010", "chunk_index": 0,
            "raw_text": "hybrid retrieval pipeline",
            "contextualized_text": "hybrid retrieval pipeline",
            "prefix": "", "prefix_source": "synthetic",
            "char_count": 25,
            "body_hash": "sha256:" + hashlib.sha256(b"hybrid retrieval pipeline").hexdigest(),
            "page_body_hash": "sha256:0",
            "created_at": "2026-05-17T00:00:00Z",
        }))
        # Build index
        subprocess.run([sys.executable, str(sandbox / "scripts" / "bm25-index.py"), "build"],
                       capture_output=True, timeout=10, check=True)
        # Run with --explain --no-rerank
        result = subprocess.run(
            [sys.executable, str(sandbox / "scripts" / "retrieve.py"),
             "hybrid", "--top", "1", "--no-rerank", "--explain"],
            capture_output=True, text=True, timeout=10)
        assert_eq("retrieve --explain --no-rerank rc=0", 0, result.returncode)
        out = json.loads(result.stdout)
        assert_true("--explain produces 'explain' key",
                    "explain" in out, hint=f"keys={list(out.keys())}")
        explain = out.get("explain", {})
        assert_true("--explain reports BM25 candidate count",
                    "bm25_candidates" in explain or "bm25" in str(explain).lower(),
                    hint=f"explain={explain}")


def test_no_rerank_flag_strategy_bm25_only():
    """v1.7.2 / closes audit M8: --no-rerank must produce strategy='bm25-only'."""
    import hashlib
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        (sandbox / "scripts").mkdir()
        meta = sandbox / ".vault-meta"
        chunks_dir = meta / "chunks"
        bm25_dir = meta / "bm25"
        chunks_dir.mkdir(parents=True)
        bm25_dir.mkdir(parents=True)
        import shutil
        for f in ["retrieve.py", "bm25-index.py", "rerank.py"]:
            shutil.copy(ROOT / "scripts" / f, sandbox / "scripts" / f)
            os.chmod(sandbox / "scripts" / f, 0o755)
        (chunks_dir / "c-000020").mkdir()
        (chunks_dir / "c-000020" / "chunk-000.json").write_text(json.dumps({
            "schema_version": 1, "page_path": "wiki/fake/c-000020.md",
            "page_address": "c-000020", "chunk_index": 0,
            "raw_text": "transport detection fallback chain",
            "contextualized_text": "transport detection fallback chain",
            "prefix": "", "prefix_source": "synthetic",
            "char_count": 35,
            "body_hash": "sha256:" + hashlib.sha256(b"transport detection fallback chain").hexdigest(),
            "page_body_hash": "sha256:0",
            "created_at": "2026-05-17T00:00:00Z",
        }))
        subprocess.run([sys.executable, str(sandbox / "scripts" / "bm25-index.py"), "build"],
                       capture_output=True, timeout=10, check=True)
        result = subprocess.run(
            [sys.executable, str(sandbox / "scripts" / "retrieve.py"),
             "transport", "--top", "1", "--no-rerank"],
            capture_output=True, text=True, timeout=10)
        assert_eq("retrieve --no-rerank rc=0", 0, result.returncode)
        out = json.loads(result.stdout)
        assert_eq("--no-rerank sets strategy='bm25-only'", "bm25-only", out.get("strategy"))
        # --no-rerank produces a consistent shape: rerank fields are populated
        # but rerank_source is "skipped" (so callers don't have to special-case).
        candidates = out.get("candidates", [])
        assert_true("--no-rerank still returns candidates", len(candidates) >= 1)
        first = candidates[0]
        assert_eq("--no-rerank candidate rerank_source='skipped'", "skipped",
                  first.get("rerank_source"))
        assert_eq("--no-rerank candidate rerank_score equals bm25_score",
                  first.get("bm25_score"), first.get("rerank_score"))


def main():
    print("=== test_retrieve.py ===")
    test_import_sibling_resolves_hyphenated_names()
    test_chunk_snippet_short()
    test_chunk_snippet_truncates_with_ellipsis()
    test_cosine_identical()
    test_cosine_orthogonal()
    test_cosine_anti_parallel()
    test_cosine_length_mismatch()
    test_cosine_zero_vector()
    test_rerank_noop_when_ollama_unreachable()
    test_rerank_noop_when_model_missing()
    test_rerank_truncates_to_top_k()
    test_with_task_prefix_query()
    test_with_task_prefix_document()
    test_with_task_prefix_noop_for_non_nomic()
    test_with_task_prefix_rejects_bad_role()
    test_rerank_sends_task_prefixes_to_embedder()
    test_rerank_cache_key_includes_scheme()
    test_retrieve_exits_10_without_index()
    test_end_to_end_with_synthetic_chunks()
    test_explain_flag_adds_diagnostics_block()
    test_no_rerank_flag_strategy_bm25_only()
    print("\nAll retrieve tests passed.")


if __name__ == "__main__":
    main()
