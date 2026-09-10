#!/usr/bin/env python3
"""test_contextual_prefix.py — hermetic tests for scripts/contextual-prefix.py.

Covers the Haiku cache-floor decision (cache_control_for). The network paths
(tier-1 Anthropic API, tier-2 claude CLI) are egress-gated and excluded from
hermetic tests by design; only the pure floor logic is exercised here. No
network, no LLM, no ollama. Pure stdlib.

Usage:
  python3 tests/test_contextual_prefix.py
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from claude_obsidian.transaction import MutationLock

HELPER = ROOT / "scripts" / "contextual-prefix.py"

spec = importlib.util.spec_from_file_location("contextual_prefix", HELPER)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


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


# ─── Below the floor → no cache_control (silent no-op avoided) ───────────────
def test_below_floor_returns_none():
    body = "x" * (cp.HAIKU_CACHE_MIN_CHARS - 1)
    assert_eq("body 1 char below floor → None", None, cp.cache_control_for(body))


def test_empty_body_returns_none():
    assert_eq("empty body → None", None, cp.cache_control_for(""))


# ─── At / above the floor → ephemeral cache_control ──────────────────────────
def test_at_floor_returns_ephemeral():
    body = "x" * cp.HAIKU_CACHE_MIN_CHARS
    assert_eq(
        "body exactly at floor → ephemeral",
        {"type": "ephemeral"},
        cp.cache_control_for(body),
    )


def test_above_floor_returns_ephemeral():
    body = "x" * (cp.HAIKU_CACHE_MIN_CHARS * 3)
    assert_eq(
        "body well above floor → ephemeral",
        {"type": "ephemeral"},
        cp.cache_control_for(body),
    )


# ─── Integration: built payload attaches cache_control only above the floor ──
def test_payload_attaches_cache_control_by_body_size():
    """Mock the network. Assert the API payload attaches cache_control to the
    page block only when the body clears the floor, and the multi-line model
    reply is truncated to one line. No network, no LLM."""
    captured = {}

    class _Resp:
        def __init__(self, d):
            self._d = json.dumps(d).encode()

        def read(self, limit=None):
            return self._d

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode())
        return _Resp(
            {
                "content": [{"type": "text", "text": "one situating line.\nIGNORED"}],
                "usage": {
                    "cache_creation_input_tokens": 7,
                    "cache_read_input_tokens": 3,
                },
            }
        )

    with mock.patch.object(cp.urllib.request, "urlopen", _fake_urlopen):
        out = cp.anthropic_api_prefix(
            "KEY", "T", "x" * cp.HAIKU_CACHE_MIN_CHARS, "chunk"
        )
        assert_eq("multi-line reply truncated to one line", "one situating line.", out)
        assert_true(
            "above-floor body attaches cache_control",
            "cache_control" in captured["body"]["system"][1],
        )
        cp.anthropic_api_prefix("KEY", "T", "tiny", "chunk")
        assert_true(
            "below-floor body omits cache_control",
            "cache_control" not in captured["body"]["system"][1],
        )


def test_anthropic_api_response_read_is_bounded():
    captured = {}

    class _Resp:
        def read(self, limit):
            captured["limit"] = limit
            return b"x" * limit

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with mock.patch.object(cp.urllib.request, "urlopen", return_value=_Resp()):
        result = cp.anthropic_api_prefix("KEY", "T", "body", "chunk")

    assert_eq("oversized Anthropic response is rejected", None, result)
    assert_eq(
        "Anthropic response read is bounded",
        cp.ANTHROPIC_RESPONSE_MAX_BYTES + 1,
        captured["limit"],
    )


def test_anthropic_api_response_boundaries_and_shapes():
    class _Resp:
        def __init__(self, raw):
            self.raw = raw

        def read(self, limit):
            assert_eq(
                "Anthropic response boundary read uses sentinel",
                cp.ANTHROPIC_RESPONSE_MAX_BYTES + 1,
                limit,
            )
            return self.raw

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    valid = json.dumps(
        {"content": [{"type": "text", "text": "exact boundary"}], "usage": {}},
        separators=(",", ":"),
    ).encode("utf-8")
    valid += b" " * (cp.ANTHROPIC_RESPONSE_MAX_BYTES - len(valid))
    with mock.patch.object(cp.urllib.request, "urlopen", return_value=_Resp(valid)):
        assert_eq(
            "exact-size Anthropic response is accepted",
            "exact boundary",
            cp.anthropic_api_prefix("KEY", "T", "body", "chunk"),
        )

    malformed_payloads = [
        b'"not an object"',
        json.dumps({"content": {"type": "text"}}).encode("utf-8"),
        json.dumps({"content": [1]}).encode("utf-8"),
        json.dumps({"content": [{"type": "text", "text": 1}]}).encode("utf-8"),
        b'{"content":[]}\xff',
    ]
    for index, malformed in enumerate(malformed_payloads):
        with mock.patch.object(
            cp.urllib.request, "urlopen", return_value=_Resp(malformed)
        ):
            assert_eq(
                f"malformed Anthropic response {index} fails closed",
                None,
                cp.anthropic_api_prefix("KEY", "T", "body", "chunk"),
            )

    class _ReadFailureResp:
        def read(self, limit):
            raise OSError("simulated response-body read failure")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with mock.patch.object(
        cp.urllib.request, "urlopen", return_value=_ReadFailureResp()
    ):
        assert_eq(
            "Anthropic response read failure fails closed",
            None,
            cp.anthropic_api_prefix("KEY", "T", "body", "chunk"),
        )

    with mock.patch.object(
        cp.urllib.request,
        "urlopen",
        side_effect=cp.urllib.error.URLError("simulated HTTP transport failure"),
    ):
        assert_eq(
            "Anthropic HTTP failure fails closed",
            None,
            cp.anthropic_api_prefix("KEY", "T", "body", "chunk"),
        )

    with (
        mock.patch.object(cp.urllib.request, "urlopen", return_value=_Resp(b"{}")),
        mock.patch.object(cp.json, "loads", side_effect=RecursionError),
    ):
        assert_eq(
            "Anthropic JSON recursion failure fails closed",
            None,
            cp.anthropic_api_prefix("KEY", "T", "body", "chunk"),
        )

    with (
        mock.patch.object(cp.urllib.request, "urlopen", return_value=_Resp(b"{}")),
        mock.patch.object(cp.json, "loads", side_effect=ValueError),
    ):
        assert_eq(
            "Anthropic JSON value failure fails closed",
            None,
            cp.anthropic_api_prefix("KEY", "T", "body", "chunk"),
        )

    empty_text = json.dumps(
        {"content": [{"type": "text", "text": " \n "}], "usage": {}}
    ).encode("utf-8")
    with mock.patch.object(
        cp.urllib.request, "urlopen", return_value=_Resp(empty_text)
    ):
        assert_eq(
            "empty Anthropic text fails closed",
            None,
            cp.anthropic_api_prefix("KEY", "T", "body", "chunk"),
        )


def test_remote_prefix_tiers_remain_explicit_opt_in():
    """Environment state alone must never send a page body off-machine."""
    with (
        mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True),
        mock.patch.object(cp.shutil, "which", return_value="/usr/bin/claude"),
    ):
        assert_eq(
            "default prefix tier stays local",
            "synthetic",
            cp.pick_prefix_tier(False, allow_egress=False),
        )
        assert_eq(
            "explicit egress enables API tier",
            "anthropic-api",
            cp.pick_prefix_tier(False, allow_egress=True),
        )
        assert_eq(
            "--no-llm overrides egress consent",
            "synthetic",
            cp.pick_prefix_tier(True, allow_egress=True),
        )


def test_claude_cli_prompt_uses_stdin_not_process_argv():
    captured = {}

    def fake_run(arguments, **kwargs):
        captured["arguments"] = arguments
        captured["input"] = kwargs.get("input")
        return subprocess.CompletedProcess(arguments, 0, "safe prefix\nignored\n", "")

    with mock.patch.object(cp.subprocess, "run", fake_run):
        result = cp.claude_cli_prefix(
            "Private title", "SECRET_PAGE_BODY", "SECRET_CHUNK"
        )
    assert_eq("Claude CLI prefix returns first line", "safe prefix", result)
    assert_eq(
        "Claude CLI argv contains no prompt", ["claude", "-p"], captured["arguments"]
    )
    assert_true(
        "Claude CLI prompt is delivered over stdin",
        "SECRET_PAGE_BODY" in captured["input"],
    )
    assert_true(
        "Claude CLI chunk is delivered over stdin", "SECRET_CHUNK" in captured["input"]
    )


def test_long_single_paragraph_is_hard_split_with_bounded_prefixes():
    long_paragraph = "".join(
        chr(0x4E00 + (offset % 2000))
        for offset in range(cp.CHUNK_HARD_MAX_CHARS * 2 + 137)
    )
    chunks = cp.chunk_body(long_paragraph)
    assert_eq("long paragraph is split without overlap-only tail", 3, len(chunks))
    assert_true(
        "every raw chunk respects the hard character bound",
        all(len(chunk) <= cp.CHUNK_HARD_MAX_CHARS for chunk in chunks),
    )
    for previous, current in zip(chunks, chunks[1:]):
        assert_eq(
            "hard-split chunks retain configured overlap",
            previous[-cp.CHUNK_OVERLAP_CHARS :],
            current[: cp.CHUNK_OVERLAP_CHARS],
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        page = root / "wiki" / "long.md"
        page.parent.mkdir(parents=True)
        page.write_text(
            "---\naddress: c-000777\ntitle: "
            + "T" * (cp.CONTEXT_PREFIX_MAX_CHARS * 2)
            + "\n---\n"
            + long_paragraph,
            encoding="utf-8",
        )
        original = (
            cp.VAULT_ROOT,
            cp.WIKI_DIR,
            cp.META_DIR,
            cp.CHUNKS_DIR,
            cp.BM25_INDEX_PATH,
        )
        cp.VAULT_ROOT = root
        cp.WIKI_DIR = root / "wiki"
        cp.META_DIR = root / ".vault-meta"
        cp.CHUNKS_DIR = cp.META_DIR / "chunks"
        cp.BM25_INDEX_PATH = cp.META_DIR / "bm25/index.json"
        try:
            result = cp.process_page(page, force_synthetic=True)
            records = [
                json.loads(
                    (cp.CHUNKS_DIR / "c-000777" / name).read_text(encoding="utf-8")
                )
                for name in result["written"]
            ]
            assert_eq("process_page writes every hard split", len(chunks), len(records))
            assert_true(
                "generated raw chunks remain hard-bounded",
                all(
                    len(record["raw_text"]) <= cp.CHUNK_HARD_MAX_CHARS
                    for record in records
                ),
            )
            assert_true(
                "generated prefixes remain hard-bounded",
                all(
                    len(record["prefix"]) <= cp.CONTEXT_PREFIX_MAX_CHARS
                    for record in records
                ),
            )
            assert_true(
                "contextualized chunks remain within documented character budget",
                all(
                    len(record["contextualized_text"])
                    <= cp.CHUNK_HARD_MAX_CHARS + cp.CONTEXT_PREFIX_MAX_CHARS + 2
                    for record in records
                ),
            )
        finally:
            (
                cp.VAULT_ROOT,
                cp.WIKI_DIR,
                cp.META_DIR,
                cp.CHUNKS_DIR,
                cp.BM25_INDEX_PATH,
            ) = original


def test_process_page_prunes_surplus_chunks_and_invalidates_index():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        page = root / "wiki" / "topic.md"
        page.parent.mkdir(parents=True)
        page.write_text(
            "---\naddress: c-000001\ntitle: Topic\n---\nA short current page.\n",
            encoding="utf-8",
        )
        chunks = root / ".vault-meta" / "chunks"
        chunk_dir = chunks / "c-000001"
        chunk_dir.mkdir(parents=True)
        stale_record = {
            "page_path": "wiki/topic.md",
            "page_address": "c-000001",
            "chunk_index": 1,
            "body_hash": "sha256:old",
            "page_body_hash": "sha256:old",
        }
        (chunk_dir / "chunk-000.json").write_text(json.dumps(stale_record))
        (chunk_dir / "chunk-001.json").write_text(json.dumps(stale_record))
        index = root / ".vault-meta" / "bm25" / "index.json"
        index.parent.mkdir(parents=True)
        index.write_text("{}")

        original = (
            cp.VAULT_ROOT,
            cp.WIKI_DIR,
            cp.META_DIR,
            cp.CHUNKS_DIR,
            cp.BM25_INDEX_PATH,
        )
        cp.VAULT_ROOT = root
        cp.WIKI_DIR = root / "wiki"
        cp.META_DIR = root / ".vault-meta"
        cp.CHUNKS_DIR = chunks
        cp.BM25_INDEX_PATH = index
        try:
            result = cp.process_page(page, force_synthetic=True)
            assert_eq(
                "changed page writes one current chunk",
                ["chunk-000.json"],
                result["written"],
            )
            assert_eq("surplus chunk is pruned", 1, result["removed"])
            assert_true(
                "surplus chunk no longer exists",
                not (chunk_dir / "chunk-001.json").exists(),
            )
            assert_true("changed chunk set invalidates BM25 index", not index.exists())
        finally:
            (
                cp.VAULT_ROOT,
                cp.WIKI_DIR,
                cp.META_DIR,
                cp.CHUNKS_DIR,
                cp.BM25_INDEX_PATH,
            ) = original


def test_full_reconcile_removes_deleted_page_chunks():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        chunks = root / ".vault-meta" / "chunks"
        orphan_dir = chunks / "c-000099"
        orphan_dir.mkdir(parents=True)
        orphan = orphan_dir / "chunk-000.json"
        orphan.write_text(json.dumps({"page_path": "wiki/deleted.md"}))
        index = root / ".vault-meta" / "bm25" / "index.json"
        index.parent.mkdir(parents=True)
        index.write_text("{}")

        original = (cp.VAULT_ROOT, cp.META_DIR, cp.CHUNKS_DIR, cp.BM25_INDEX_PATH)
        cp.VAULT_ROOT = root
        cp.META_DIR = root / ".vault-meta"
        cp.CHUNKS_DIR = chunks
        cp.BM25_INDEX_PATH = index
        try:
            removed = cp.reconcile_chunk_store(set())
            assert_eq("full scan removes deleted-page chunk", 1, removed)
            assert_true("orphan chunk removed", not orphan.exists())
            assert_true("orphan removal invalidates index", not index.exists())
        finally:
            (cp.VAULT_ROOT, cp.META_DIR, cp.CHUNKS_DIR, cp.BM25_INDEX_PATH) = original


def test_historical_synthetic_collision_paths_remain_distinct() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        wiki = root / "wiki"
        wiki.mkdir()
        (root / ".obsidian").mkdir()
        for name in ("Page-988.md", "Page-3676.md"):
            (wiki / name).write_text(
                f"---\ntitle: {name}\n---\nUnique body for {name}.\n",
                encoding="utf-8",
            )
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--vault",
                str(root),
                "--all",
                "--no-llm",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert_eq(
            "historical collision pair processes successfully", 0, result.returncode
        )
        records = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((root / ".vault-meta/chunks").glob("*/chunk-000.json"))
        ]
        assert_eq("both formerly colliding pages retain chunks", 2, len(records))
        assert_eq(
            "synthetic addresses remain unique",
            2,
            len({record["page_address"] for record in records}),
        )
        assert_eq(
            "both page paths remain represented",
            ["wiki/Page-3676.md", "wiki/Page-988.md"],
            sorted(record["page_path"] for record in records),
        )


def test_duplicate_explicit_address_fails_before_any_write() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        wiki = root / "wiki"
        wiki.mkdir()
        (root / ".obsidian").mkdir()
        for name in ("A.md", "B.md"):
            (wiki / name).write_text(
                f"---\naddress: c-000001\ntitle: {name}\n---\nBody {name}.\n",
                encoding="utf-8",
            )
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--vault",
                str(root),
                "--all",
                "--no-llm",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert_eq(
            "duplicate explicit address exits 5",
            cp.EXIT_ADDRESS_COLLISION,
            result.returncode,
        )
        assert_true(
            "duplicate diagnostic is stable",
            "duplicate page address c-000001" in result.stderr,
        )
        assert_true(
            "collision preflight writes no runtime state",
            not (root / ".vault-meta").exists(),
        )


def test_symlinked_chunk_address_never_writes_or_deletes_outside() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        root = base / "vault"
        wiki = root / "wiki"
        wiki.mkdir(parents=True)
        (root / ".obsidian").mkdir()
        page = wiki / "Page.md"
        page.write_text(
            "---\naddress: c-000001\ntitle: Page\n---\nBody.\n", encoding="utf-8"
        )
        outside = base / "outside"
        outside.mkdir()
        sentinel = outside / "chunk-000.json"
        sentinel.write_text(json.dumps({"page_path": "wiki/Page.md"}), encoding="utf-8")
        chunks = root / ".vault-meta/chunks"
        chunks.mkdir(parents=True)
        (chunks / "c-000001").symlink_to(outside, target_is_directory=True)
        before = sentinel.read_bytes()
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--vault",
                str(root),
                "--all",
                "--no-llm",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert_eq(
            "symlinked address directory exits safely",
            cp.EXIT_CHUNK_DIR,
            result.returncode,
        )
        assert_eq("outside chunk bytes stay unchanged", before, sentinel.read_bytes())
        assert_eq(
            "outside directory gains no files",
            ["chunk-000.json"],
            sorted(p.name for p in outside.iterdir()),
        )


def test_explicit_page_symlink_is_rejected_without_replacing_real_chunks() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        wiki = root / "wiki"
        wiki.mkdir()
        (root / ".obsidian").mkdir()
        real = wiki / "Real.md"
        real.write_text(
            "---\naddress: c-000001\ntitle: Real\n---\nReal body.\n", encoding="utf-8"
        )
        alias = wiki / "Alias.md"
        alias.symlink_to(real)
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--vault",
                str(root),
                "wiki/Alias.md",
                "--no-llm",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert_eq(
            "explicit page symlink exits as usage error",
            cp.EXIT_USAGE,
            result.returncode,
        )
        assert_true(
            "explicit page symlink creates no chunks",
            not (root / ".vault-meta").exists(),
        )


def test_prefix_generation_refuses_shared_vault_writer_lock() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        wiki = root / "wiki"
        wiki.mkdir()
        (root / ".obsidian").mkdir()
        (wiki / "Page.md").write_text(
            "---\naddress: c-000001\ntitle: Page\n---\nCurrent body.\n",
            encoding="utf-8",
        )
        with MutationLock(root):
            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--vault",
                    str(root),
                    "--all",
                    "--no-llm",
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        assert_eq(
            "prefix generation returns lock exit", cp.EXIT_LOCK, result.returncode
        )
        assert_true(
            "blocked prefix generation creates no chunks",
            not (root / ".vault-meta/chunks").exists(),
        )


def test_pinned_contextual_write_survives_root_replacement() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        temporary = Path(tmpdir)
        root = temporary / "vault"
        page = root / "wiki/topic.md"
        page.parent.mkdir(parents=True)
        (root / ".obsidian").mkdir()
        page.write_text(
            "---\naddress: c-000001\ntitle: Topic\n---\nPinned body.\n",
            encoding="utf-8",
        )
        original = (
            cp.VAULT_ROOT,
            cp.WIKI_DIR,
            cp.META_DIR,
            cp.CHUNKS_DIR,
            cp.BM25_INDEX_PATH,
        )
        cp.VAULT_ROOT = root
        cp.WIKI_DIR = root / "wiki"
        cp.META_DIR = root / ".vault-meta"
        cp.CHUNKS_DIR = cp.META_DIR / "chunks"
        cp.BM25_INDEX_PATH = cp.META_DIR / "bm25/index.json"
        held_root = temporary / "held-vault"
        try:
            with MutationLock(root) as lock:
                root_fd = lock.duplicate_root_fd()
                meta_fd = lock.duplicate_parent_fd()
                try:
                    root.rename(held_root)
                    replacement_address = root / ".vault-meta/chunks/c-000001"
                    replacement_address.mkdir(parents=True)
                    sentinel = replacement_address / "sentinel"
                    sentinel.write_bytes(b"replacement-must-survive\n")
                    result = cp.process_page(
                        page,
                        force_synthetic=True,
                        root_fd=root_fd,
                        meta_fd=meta_fd,
                    )
                finally:
                    os.close(meta_fd)
                    os.close(root_fd)
            assert_eq(
                "pinned contextual write count", ["chunk-000.json"], result["written"]
            )
            assert_true(
                "pinned root receives contextual chunk",
                (held_root / ".vault-meta/chunks/c-000001/chunk-000.json").is_file(),
            )
            assert_true(
                "replacement root receives no contextual chunk",
                not (replacement_address / "chunk-000.json").exists(),
            )
            assert_eq(
                "replacement root sentinel unchanged",
                b"replacement-must-survive\n",
                sentinel.read_bytes(),
            )
        finally:
            (
                cp.VAULT_ROOT,
                cp.WIKI_DIR,
                cp.META_DIR,
                cp.CHUNKS_DIR,
                cp.BM25_INDEX_PATH,
            ) = original


def test_chunk_parent_swap_never_redirects_atomic_publication() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        temporary = Path(tmpdir)
        root = temporary / "vault"
        page = root / "wiki/topic.md"
        page.parent.mkdir(parents=True)
        (root / ".obsidian").mkdir()
        page.write_text(
            "---\naddress: c-000001\ntitle: Topic\n---\nPinned body.\n",
            encoding="utf-8",
        )
        address = root / ".vault-meta/chunks/c-000001"
        address.mkdir(parents=True)
        held_address = address.with_name("c-000001-held")
        outside = temporary / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel"
        sentinel.write_bytes(b"outside-must-survive\n")
        original_paths = (
            cp.VAULT_ROOT,
            cp.WIKI_DIR,
            cp.META_DIR,
            cp.CHUNKS_DIR,
            cp.BM25_INDEX_PATH,
        )
        original_write = cp._atomic_vault_write
        cp.VAULT_ROOT = root
        cp.WIKI_DIR = root / "wiki"
        cp.META_DIR = root / ".vault-meta"
        cp.CHUNKS_DIR = cp.META_DIR / "chunks"
        cp.BM25_INDEX_PATH = cp.META_DIR / "bm25/index.json"
        swapped = False

        def swap_then_write(*args, **kwargs):
            nonlocal swapped
            if not swapped:
                swapped = True
                address.rename(held_address)
                address.symlink_to(outside, target_is_directory=True)
            return original_write(*args, **kwargs)

        try:
            with MutationLock(root) as lock:
                root_fd = lock.duplicate_root_fd()
                meta_fd = lock.duplicate_parent_fd()
                try:
                    with mock.patch.object(cp, "_atomic_vault_write", swap_then_write):
                        try:
                            cp.process_page(
                                page,
                                force_synthetic=True,
                                root_fd=root_fd,
                                meta_fd=meta_fd,
                            )
                            raise Fail(
                                "contextual publication followed a swapped address"
                            )
                        except SystemExit as exc:
                            assert_eq(
                                "swapped chunk parent exits safely",
                                cp.EXIT_CHUNK_DIR,
                                exc.code,
                            )
                finally:
                    os.close(meta_fd)
                    os.close(root_fd)
            assert_true("chunk parent swap was exercised", swapped)
            assert_eq(
                "outside chunk target unchanged",
                b"outside-must-survive\n",
                sentinel.read_bytes(),
            )
            assert_eq(
                "outside chunk target gains no entries",
                ["sentinel"],
                sorted(path.name for path in outside.iterdir()),
            )
        finally:
            (
                cp.VAULT_ROOT,
                cp.WIKI_DIR,
                cp.META_DIR,
                cp.CHUNKS_DIR,
                cp.BM25_INDEX_PATH,
            ) = original_paths


def test_read_page_preserves_crlf_bytes() -> None:
    # Regression: read_page previously used read_text, which normalizes CRLF,
    # so the chunker's page_body_hash diverged from the byte-exact hash used
    # under the writer lock and by the retriever.
    with tempfile.TemporaryDirectory() as tmpdir:
        page = Path(tmpdir) / "c.md"
        page.write_bytes(b"line one\r\nline two\r\n")
        text = cp.read_page(page)
        assert "\r\n" in text, "read_page must not normalize line endings"


def main():
    print("=== test_contextual_prefix.py ===")
    test_below_floor_returns_none()
    test_empty_body_returns_none()
    test_at_floor_returns_ephemeral()
    test_above_floor_returns_ephemeral()
    test_payload_attaches_cache_control_by_body_size()
    test_anthropic_api_response_read_is_bounded()
    test_anthropic_api_response_boundaries_and_shapes()
    test_remote_prefix_tiers_remain_explicit_opt_in()
    test_claude_cli_prompt_uses_stdin_not_process_argv()
    test_long_single_paragraph_is_hard_split_with_bounded_prefixes()
    test_process_page_prunes_surplus_chunks_and_invalidates_index()
    test_full_reconcile_removes_deleted_page_chunks()
    test_historical_synthetic_collision_paths_remain_distinct()
    test_duplicate_explicit_address_fails_before_any_write()
    test_symlinked_chunk_address_never_writes_or_deletes_outside()
    test_explicit_page_symlink_is_rejected_without_replacing_real_chunks()
    test_prefix_generation_refuses_shared_vault_writer_lock()
    test_pinned_contextual_write_survives_root_replacement()
    test_chunk_parent_swap_never_redirects_atomic_publication()
    test_read_page_preserves_crlf_bytes()
    print("\nAll contextual-prefix tests passed.")


if __name__ == "__main__":
    main()
