#!/usr/bin/env python3
"""test_tiling_check.py — unit tests for scripts/tiling-check.py.

Does NOT require ollama; tests cover parsing, cosine, inclusion logic,
hash properties, cache schema, and the localhost-URL guard. Tests that
need ollama are marked and skipped cleanly when the helper reports
exit 10/11.

Usage:
  python3 tests/test_tiling_check.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "tiling-check.py"

spec = importlib.util.spec_from_file_location("tc", HELPER)
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)


class Fail(SystemExit):
    pass


def assert_eq(label, expected, actual):
    if expected != actual:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"OK   {label}")


def assert_true(label, cond):
    if not cond:
        raise Fail(f"FAIL {label}")
    print(f"OK   {label}")


def test_cosine():
    assert_eq("cosine identical", 1.0, tc.cosine([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]))
    assert_eq("cosine orthogonal", 0.0, tc.cosine([1.0, 0.0], [0.0, 1.0]))
    assert_eq("cosine anti-parallel", -1.0, tc.cosine([1.0, 0.0], [-1.0, 0.0]))
    assert_eq("cosine zero vector", 0.0, tc.cosine([0.0, 0.0], [1.0, 2.0]))
    try:
        tc.cosine([1.0], [1.0, 2.0])
        raise Fail("FAIL dim mismatch should raise")
    except ValueError:
        print("OK   cosine dim mismatch raises ValueError")


def test_frontmatter():
    fm, body = tc.parse_frontmatter("---\ntype: concept\ntitle: Foo\n---\n# Body\n")
    assert_eq("parse type", "concept", fm.get("type"))
    assert_eq("parse body", "# Body\n", body)
    fm, body = tc.parse_frontmatter("# Just a title\n")
    assert_eq("no frontmatter -> empty", {}, fm)
    fm, _ = tc.parse_frontmatter('---\ntype: "meta"\n---\nbody\n')
    assert_eq("quoted type stripped", "meta", fm.get("type"))


def test_body_hash_model_scoped():
    h1 = tc.body_hash("body", "model-A")
    h2 = tc.body_hash("body", "model-B")
    h3 = tc.body_hash("body", "model-A")
    assert_true("different models hash differently", h1 != h2)
    assert_eq("same body+model hashes identically", h1, h3)


def test_included_basic():
    cases = [
        (ROOT / "wiki/concepts/Foo.md",         {"type": "concept"}, True,  "included"),
        (ROOT / "wiki/index.md",                {"type": "meta"},    False, "excluded filename"),
        (ROOT / "wiki/folds/fold-1.md",         {"type": "fold"},    False, "under wiki/folds/"),
        (ROOT / "wiki/meta/session.md",         {"type": "session"}, False, "under wiki/meta/"),
        (ROOT / "wiki/entities/Person.md",      {"type": "entity"},  True,  "included"),
    ]
    for path, fm, expected_ok, expected_reason in cases:
        ok, reason = tc.included(path, fm)
        label = f"included({path.relative_to(ROOT)}, {fm.get('type')})"
        assert_eq(label + ".ok",     expected_ok,     ok)
        assert_eq(label + ".reason", expected_reason, reason)


def test_is_local_url():
    assert_true("127.0.0.1 is local", tc._is_local_url("http://127.0.0.1:11434"))
    assert_true("localhost is local", tc._is_local_url("http://localhost:11434"))
    assert_true("::1 is local",       tc._is_local_url("http://[::1]:11434"))
    assert_true("example.com NOT local",   not tc._is_local_url("http://example.com"))
    assert_true("1.2.3.4 NOT local",       not tc._is_local_url("http://1.2.3.4"))


def test_cache_schema():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        original_cache = tc.CACHE_PATH
        original_meta = tc.META_DIR
        tc.CACHE_PATH = tmp / "cache.json"
        tc.META_DIR = tmp
        try:
            c = tc.load_cache("m1")
            assert_eq("empty cache -> version 1", 1, c["version"])
            assert_eq("empty cache -> empty embeddings", {}, c["embeddings"])

            tc.CACHE_PATH.write_text(json.dumps({"version": 1, "model": "m1", "embeddings": {"a.md": {"hash": "h", "embedding": [1.0]}}}))
            c = tc.load_cache("m1")
            assert_eq("valid cache loads", 1, len(c["embeddings"]))

            c = tc.load_cache("m2")
            assert_eq("model drift -> empty", {}, c["embeddings"])
            assert_eq("model drift -> new model", "m2", c["model"])

            tc.CACHE_PATH.write_text("not-json{{")
            try:
                tc.load_cache("m1")
                raise Fail("FAIL corrupt cache should SystemExit")
            except SystemExit as e:
                assert_eq("corrupt cache exit", 3, e.code)

            tc.CACHE_PATH.write_text(json.dumps({"version": 999, "embeddings": {}}))
            try:
                tc.load_cache("m1")
                raise Fail("FAIL wrong version should SystemExit")
            except SystemExit as e:
                assert_eq("wrong version exit", 3, e.code)
        finally:
            tc.CACHE_PATH = original_cache
            tc.META_DIR = original_meta


def test_url_guard_via_subprocess():
    env = os.environ.copy()
    env["OLLAMA_URL"] = "http://example.com:11434"
    result = subprocess.run(
        [sys.executable, str(HELPER), "--peek"],
        env=env, capture_output=True, text=True, timeout=10,
    )
    assert_eq("remote URL without flag exit", 2, result.returncode)
    assert_true("remote URL error message", "not localhost" in result.stderr)


if __name__ == "__main__":
    try:
        test_cosine()
        test_frontmatter()
        test_body_hash_model_scoped()
        test_included_basic()
        test_is_local_url()
        test_cache_schema()
        test_url_guard_via_subprocess()
    except Fail as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    print("\nAll tests passed.")
