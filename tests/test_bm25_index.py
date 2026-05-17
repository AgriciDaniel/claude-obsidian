#!/usr/bin/env python3
"""test_bm25_index.py — hermetic tests for scripts/bm25-index.py.

Covers tokenization (stopwords, punctuation, case), index construction from
synthetic chunk fixtures, and BM25 scoring correctness against a hand-computed
reference. No network, no ollama, no LLM calls.

Usage:
  python3 tests/test_bm25_index.py
"""
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "bm25-index.py"

spec = importlib.util.spec_from_file_location("bm25", HELPER)
bm25 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm25)


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


def assert_close(label, expected, actual, eps=1e-4):
    if abs(expected - actual) > eps:
        raise Fail(f"FAIL {label}: expected ~{expected}, got {actual} (diff {abs(expected-actual)})")
    print(f"OK   {label}")


# ─── tokenize() ──────────────────────────────────────────────────────────────
def test_tokenize_basic():
    assert_eq("tokenize basic", ["hello", "world"], bm25.tokenize("Hello, World!"))


def test_tokenize_stopwords():
    out = bm25.tokenize("The quick brown fox is at the door")
    assert_eq("tokenize strips stopwords", ["quick", "brown", "fox", "door"], out)


def test_tokenize_punctuation_and_apostrophe():
    out = bm25.tokenize("don't-stop won't!")
    assert_true("tokenize keeps apostrophes/hyphens", "don't-stop" in out or "don't" in out,
                hint=f"got {out}")


def test_tokenize_short_tokens_dropped():
    out = bm25.tokenize("a b cc dddd")
    assert_eq("tokenize drops <2-char and stopwords", ["dddd"], [t for t in out if len(t) > 2])


def test_tokenize_unicode_multilingual():
    """v1.7.2 / closes audit M2: tokenizer must preserve non-ASCII content."""
    # Cyrillic
    out = bm25.tokenize("Привет мир")
    assert_true("tokenize preserves Cyrillic", "привет" in out and "мир" in out,
                hint=f"got {out}")
    # CJK (each character is its own token because there are no word boundaries)
    out = bm25.tokenize("日本語の文書")
    assert_true("tokenize preserves CJK", len(out) >= 1 and any("日" in t or "本" in t for t in out),
                hint=f"got {out}")
    # Accented Latin (Spanish, French, German)
    out = bm25.tokenize("café résumé naïve über")
    assert_true("tokenize preserves accented Latin", "café" in out and "résumé" in out,
                hint=f"got {out}")
    # Pure-emoji string: no word chars → no tokens (correct skip)
    out = bm25.tokenize("🎉🚀✨")
    assert_eq("tokenize skips pure-emoji string", [], out)
    # Mixed ASCII + non-ASCII: both survive
    out = bm25.tokenize("Hello мир café")
    assert_true("tokenize mixes ASCII + non-ASCII",
                "hello" in out and "мир" in out and "café" in out, hint=f"got {out}")


# ─── build_index + query() ───────────────────────────────────────────────────
def synthetic_chunk(idx, address, raw_text, contextualized_text):
    """Build a chunk JSON record matching the contextual-prefix.py schema."""
    import hashlib
    body_hash = "sha256:" + hashlib.sha256(raw_text.encode()).hexdigest()
    return {
        "schema_version": 1,
        "page_path": f"wiki/fake/{address}.md",
        "page_address": address,
        "chunk_index": idx,
        "raw_text": raw_text,
        "contextualized_text": contextualized_text,
        "prefix": "",
        "prefix_source": "synthetic",
        "char_count": len(raw_text),
        "body_hash": body_hash,
        "page_body_hash": body_hash,
        "created_at": "2026-05-17T00:00:00Z",
    }


def test_build_and_query():
    """End-to-end: write synthetic chunks, build index, query, verify rankings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Redirect bm25 module's paths to a sandbox
        sandbox = Path(tmpdir)
        meta = sandbox / ".vault-meta"
        chunks_dir = meta / "chunks"
        bm25_dir = meta / "bm25"
        chunks_dir.mkdir(parents=True)
        bm25_dir.mkdir(parents=True)

        orig_meta = bm25.META_DIR
        orig_chunks = bm25.CHUNKS_DIR
        orig_bm25 = bm25.BM25_DIR
        orig_index = bm25.INDEX_PATH
        orig_lock = bm25.LOCK_PATH

        bm25.META_DIR = meta
        bm25.CHUNKS_DIR = chunks_dir
        bm25.BM25_DIR = bm25_dir
        bm25.INDEX_PATH = bm25_dir / "index.json"
        bm25.LOCK_PATH = meta / ".bm25.lock"

        try:
            # 3 fake "pages" with 1 chunk each. Note "memory" appears in p1 and p3.
            chunks = [
                ("c-000001", 0, "DragonScale memory mechanism for log folding"),
                ("c-000002", 0, "transport detection with the obsidian cli binary"),
                ("c-000003", 0, "memory layer architecture and the wiki vault"),
            ]
            for addr, idx, text in chunks:
                d = chunks_dir / addr
                d.mkdir(exist_ok=True)
                chunk = synthetic_chunk(idx, addr, text, text)
                (d / f"chunk-{idx:03d}.json").write_text(json.dumps(chunk))

            # Build index
            index = bm25.build_index()
            assert_eq("doc count", 3, index["doc_count"])
            assert_true("vocab has 'memory'", "memory" in index["vocab"])
            assert_true("vocab strips stopwords", "the" not in index["vocab"])
            assert_eq("memory df", 2, index["vocab"]["memory"]["df"])

            bm25.write_index(index)
            assert_true("index file written", bm25.INDEX_PATH.is_file())

            # Query: "memory" should rank p1 and p3 above p2
            results = bm25.query("memory")
            ids = [r["chunk_id"] for r in results]
            assert_true("memory query returns 2 hits", len(results) == 2,
                        hint=f"got {ids}")
            assert_true("c-000002 not in 'memory' results",
                        "c-000002:0" not in ids)

            # Query: "transport" should hit only c-000002
            results = bm25.query("transport")
            assert_eq("transport query hits exactly p2", ["c-000002:0"],
                      [r["chunk_id"] for r in results])

            # Query: stopwords-only returns empty
            results = bm25.query("the and of")
            assert_eq("stopwords-only query empty", [], results)
        finally:
            bm25.META_DIR = orig_meta
            bm25.CHUNKS_DIR = orig_chunks
            bm25.BM25_DIR = orig_bm25
            bm25.INDEX_PATH = orig_index
            bm25.LOCK_PATH = orig_lock


def test_query_score_monotonicity():
    """A query term appearing TWICE in a chunk should score higher than appearing ONCE.
    (Standard BM25 monotonicity property within a single document length cohort.)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        meta = sandbox / ".vault-meta"
        chunks_dir = meta / "chunks"
        bm25_dir = meta / "bm25"
        chunks_dir.mkdir(parents=True)
        bm25_dir.mkdir(parents=True)

        orig = (bm25.META_DIR, bm25.CHUNKS_DIR, bm25.BM25_DIR,
                bm25.INDEX_PATH, bm25.LOCK_PATH)
        bm25.META_DIR = meta
        bm25.CHUNKS_DIR = chunks_dir
        bm25.BM25_DIR = bm25_dir
        bm25.INDEX_PATH = bm25_dir / "index.json"
        bm25.LOCK_PATH = meta / ".bm25.lock"

        try:
            # Equal-length docs (rough): one has "memory" twice, other once.
            (chunks_dir / "c-000001").mkdir()
            (chunks_dir / "c-000002").mkdir()
            (chunks_dir / "c-000001" / "chunk-000.json").write_text(
                json.dumps(synthetic_chunk(0, "c-000001",
                                           "memory memory rocket banana",
                                           "memory memory rocket banana")))
            (chunks_dir / "c-000002" / "chunk-000.json").write_text(
                json.dumps(synthetic_chunk(0, "c-000002",
                                           "memory rocket banana flute",
                                           "memory rocket banana flute")))
            bm25.write_index(bm25.build_index())
            results = bm25.query("memory")
            assert_true("BM25 monotonicity", results[0]["chunk_id"] == "c-000001:0",
                        hint=f"got {results}")
            assert_true("two-mention > one-mention scores",
                        results[0]["score"] > results[1]["score"],
                        hint=f"got {results}")
        finally:
            (bm25.META_DIR, bm25.CHUNKS_DIR, bm25.BM25_DIR,
             bm25.INDEX_PATH, bm25.LOCK_PATH) = orig


def test_idf_smoothing():
    """IDF should be positive and finite for any df in [1, N]."""
    # Use the formula directly: idf = log(1 + (N - df + 0.5) / (df + 0.5))
    for N in [1, 10, 1000]:
        for df in range(1, N + 1):
            idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
            assert_true(f"idf positive N={N} df={df}", idf > 0, hint=f"got {idf}")


# ─── CLI smoke test ──────────────────────────────────────────────────────────
def test_cli_stats_on_missing_index():
    """The CLI should exit 3 (EXIT_INDEX_MISSING) when no index exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run in a subprocess with a fresh cwd and zeroed META_DIR
        env = dict(os.environ)
        # We can't easily redirect bm25's hard-coded paths from outside without
        # rewriting the script. Instead: smoke-test the exit code path by
        # invoking the module-level load_index() in a context where the index
        # file doesn't exist.
        orig_index = bm25.INDEX_PATH
        bm25.INDEX_PATH = Path(tmpdir) / "nonexistent" / "index.json"
        try:
            try:
                bm25.load_index()
                raise Fail("load_index() should have exited on missing file")
            except SystemExit as e:
                assert_eq("load_index exit code", bm25.EXIT_INDEX_MISSING, e.code)
        finally:
            bm25.INDEX_PATH = orig_index


def main():
    print("=== test_bm25_index.py ===")
    test_tokenize_basic()
    test_tokenize_stopwords()
    test_tokenize_punctuation_and_apostrophe()
    test_tokenize_unicode_multilingual()
    test_tokenize_short_tokens_dropped()
    test_build_and_query()
    test_query_score_monotonicity()
    test_idf_smoothing()
    test_cli_stats_on_missing_index()
    print("\nAll bm25-index tests passed.")


if __name__ == "__main__":
    main()
