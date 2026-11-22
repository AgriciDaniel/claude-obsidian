#!/usr/bin/env python3
"""bm25-index.py — sparse BM25 inverted index over contextualized wiki chunks.

Pure stdlib (no rank_bm25 dep). Standard Okapi BM25 with k1=1.5, b=0.75.
Indexes the `contextualized_text` field of every chunk under .vault-meta/chunks/,
emits a single JSON file at .vault-meta/bm25/index.json with the schema below.

Concurrency:
- Shares the vault-wide process-held mutation lock with contextual-prefix.
- Atomic .tmp + rename for the index file.

Index schema (.vault-meta/bm25/index.json):
{
  "schema_version": 2,
  "params": {"k1": 1.5, "b": 0.75},
  "doc_count": 1234,
  "avg_dl": 487.5,
  "updated_at": "2026-05-17T...",
  "vocab": {
    "<term>": {"df": 17, "postings": [["c-000001:0", 3], ["c-000042:2", 1], ...]}
  },
  "docs": {
    "<chunk_id>": {"path": ".vault-meta/chunks/c-000001/chunk-000.json", "dl": 487}
  }
}

Chunk id format: "<page-address>:<chunk-index>" (e.g. "c-000042:3").

Tokenization: NFKC-normalize, lowercase, collapse whitespace, and drop
punctuation except in-word apostrophes, hyphens, and underscores. Han,
Hiragana, Katakana, Bopomofo, and Hangul runs emit deterministic 1-, 2-, and
3-character n-grams, so unsegmented and one-character CJK queries overlap
longer documents. Each document/query is capped at MAX_TOKEN_INPUT_CHARS and
MAX_TOKEN_TERMS before materializing an oversized term list. ASCII-only
stopwords are filtered (small list; favors recall over precision).

Query interface (used by retrieve.py at query time):
  bm25-index.py query "your text here" [--top 20]

Build interface:
  bm25-index.py build               # full rebuild (always; incremental is v1.7.x scope)
  bm25-index.py stats               # print index stats

Exit codes:
  0 — success
  1 — lock acquisition failed
  2 — usage error
  3 — index file missing or corrupt (query mode)
  4 — chunks directory missing
"""

import argparse
import hashlib
import json
import math
import os
import re
import shlex
import stat
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from claude_obsidian.paths import VaultSelectionError, resolve_vault_root
from claude_obsidian.transaction import (
    MutationLock,
    TransactionError,
    _atomic_vault_write,
    _safe_vault_path,
    read_vault_regular,
)

VAULT_ROOT = Path.cwd().resolve()
META_DIR = VAULT_ROOT / ".vault-meta"
CHUNKS_DIR = META_DIR / "chunks"
BM25_DIR = META_DIR / "bm25"
INDEX_PATH = BM25_DIR / "index.json"


def configure_vault(explicit=None):
    global VAULT_ROOT, META_DIR, CHUNKS_DIR, BM25_DIR, INDEX_PATH
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
    BM25_DIR = META_DIR / "bm25"
    INDEX_PATH = BM25_DIR / "index.json"
    try:
        for relative in (
            ".vault-meta",
            ".vault-meta/chunks",
            ".vault-meta/bm25",
            ".vault-meta/bm25/index.json",
            ".vault-meta/mutation.lock",
        ):
            _safe_vault_path(VAULT_ROOT, relative)
    except (VaultSelectionError, TransactionError) as exc:
        log(f"ERR {exc.code}: {exc}")
        return False
    return True

K1 = 1.5
B = 0.75

# Small high-frequency-stopword list (English). Conservative — keep recall high.
STOPWORDS = frozenset("""
a an and are as at be by for from has have he her him his i if in is it its
of on or that the their them they this to was were will with you your
""".split())

# Unicode-aware word matcher. \w under re.UNICODE matches letters and digits
# from any script (CJK, Cyrillic, accented Latin, Devanagari, etc.) plus
# underscore. Internal apostrophes and hyphens are preserved so "user's" and
# "well-formed" stay single tokens. Pure-symbol or pure-emoji tokens fail the
# leading \w anchor and are correctly skipped.
TOKEN_RE = re.compile(r"\w[\w'\-]*", re.UNICODE)

# Word boundaries are not normally present inside Japanese and Chinese text.
# Unigrams make one-character queries retrievable, bigrams supply substring
# recall, and trigrams add useful specificity. The fixed 1/2/3 range bounds
# growth to at most 3n-3 terms for a run of n characters. Korean and Bopomofo
# ranges use the same treatment so the behavior consistently covers the CJK
# writing systems.
CJK_NGRAM_SIZES = (1, 2, 3)
CJK_RANGES = (
    (0x1100, 0x11FF),  # Hangul Jamo
    (0x3040, 0x309F),  # Hiragana
    (0x30A0, 0x30FF),  # Katakana
    (0x3100, 0x312F),  # Bopomofo
    (0x3130, 0x318F),  # Hangul Compatibility Jamo
    (0x31A0, 0x31BF),  # Bopomofo Extended
    (0x31F0, 0x31FF),  # Katakana Phonetic Extensions
    (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0xA960, 0xA97F),  # Hangul Jamo Extended-A
    (0xAC00, 0xD7AF),  # Hangul Syllables
    (0xD7B0, 0xD7FF),  # Hangul Jamo Extended-B
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
    (0xFF66, 0xFF9F),  # Halfwidth Katakana
    (0x20000, 0x2FA1F),  # Supplementary CJK ideographs and compatibility forms
    (0x30000, 0x323AF),  # CJK Unified Ideographs Extensions G through H
)

EXIT_OK = 0
EXIT_LOCK = 1
EXIT_USAGE = 2
EXIT_INDEX_MISSING = 3
EXIT_NO_CHUNKS = 4

# Schema 2 denotes the finalized pre-release CJK n-gram tokenizer, including
# NFKC normalization and bounded unigrams. No schema-2 artifact was published
# before these semantics were finalized. Schema 1 indexes must be rebuilt:
# querying an old vocabulary with new query tokens would otherwise silently
# lose CJK recall. Indexes are disposable derived state and load_index() emits
# an exact rebuild command when validation rejects an older schema.
INDEX_SCHEMA_VERSION = 2
MAX_INDEX_COUNT = 2_147_483_647
MAX_K1 = 100.0
# Generated chunks contain at most 4,000 raw characters plus a 1,000-character
# prefix. The 8,000-character input ceiling leaves headroom for normalization;
# twenty thousand terms bounds the 3n-3 CJK expansion. Both checks reject
# manually supplied chunks and adversarial queries before their complete term
# list or an unbounded vocabulary key is materialized.
MAX_TOKEN_INPUT_CHARS = 8_000
MAX_TOKEN_TERMS = 20_000
MAX_TOP_RESULTS = 1_000


class IndexValidationError(ValueError):
    """A syntactically valid index does not satisfy the BM25 schema."""


class TokenGrowthLimitError(ValueError):
    """Normalized token expansion exceeds the documented per-text ceiling."""


class QueryTooLargeError(ValueError):
    """A query cannot be tokenized within the bounded retrieval budget."""


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


def _directory_flags():
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )


def _open_runtime_directory(parent_fd, name):
    """Open one derived-runtime directory without following a replaced alias."""

    descriptor = os.open(name, _directory_flags(), dir_fd=parent_fd)
    metadata = os.fstat(descriptor)
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(descriptor)
        raise OSError(f"runtime component is not a directory: {name}")
    return descriptor


def _pinned_chunk_documents(meta_fd):
    """Yield bounded chunk JSON from the exact metadata namespace being locked."""

    try:
        chunks_fd = _open_runtime_directory(meta_fd, "chunks")
    except FileNotFoundError:
        log(f"ERR: no chunks directory at {CHUNKS_DIR}")
        raise SystemExit(EXIT_NO_CHUNKS)
    except OSError as exc:
        raise TransactionError(
            "UNSAFE_RUNTIME_PATH",
            f"cannot open the pinned chunk directory: {exc}",
        ) from exc
    try:
        with os.scandir(chunks_fd) as addresses:
            address_names = sorted(
                entry.name for entry in addresses if entry.is_dir(follow_symlinks=False)
            )
        for address in address_names:
            try:
                address_fd = _open_runtime_directory(chunks_fd, address)
            except OSError:
                log(f"  skip (unsafe runtime directory): {CHUNKS_DIR / address}")
                continue
            try:
                with os.scandir(address_fd) as entries:
                    names = sorted(
                        entry.name
                        for entry in entries
                        if entry.is_file(follow_symlinks=False)
                        and entry.name.startswith("chunk-")
                        and entry.name.endswith(".json")
                    )
                for name in names:
                    relative = f"chunks/{address}/{name}"
                    try:
                        raw = read_vault_regular(
                            META_DIR,
                            relative,
                            limit=8 * 1024 * 1024,
                            missing_ok=False,
                            root_fd=meta_fd,
                        )
                        assert raw is not None
                        data = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError, OSError, TransactionError) as exc:
                        log(f"  skip (unreadable): {CHUNKS_DIR / address / name} — {exc}")
                        continue
                    yield address, name, data
            finally:
                os.close(address_fd)
    finally:
        os.close(chunks_fd)


def log(msg):
    print(msg, file=sys.stderr)


def _is_cjk_character(character):
    """Return whether a character belongs to an unsegmented CJK script."""
    codepoint = ord(character)
    return any(start <= codepoint <= end for start, end in CJK_RANGES)


def _script_runs(token):
    """Split one regex word token whenever it enters or leaves a CJK script."""
    if not token:
        return
    start = 0
    cjk = _is_cjk_character(token[0])
    for position, character in enumerate(token[1:], start=1):
        next_cjk = _is_cjk_character(character)
        if next_cjk != cjk:
            yield token[start:position], cjk
            start = position
            cjk = next_cjk
    yield token[start:], cjk


def _cjk_ngrams(run):
    """Return bounded character n-grams for one uninterrupted CJK run."""
    return [
        run[offset : offset + size]
        for size in CJK_NGRAM_SIZES
        if len(run) >= size
        for offset in range(len(run) - size + 1)
    ]


def _cjk_ngram_count(length):
    """Return the exact bounded n-gram count without materializing terms."""
    return sum(length - size + 1 for size in CJK_NGRAM_SIZES if length >= size)


def _require_term_capacity(current_count, added_count):
    if current_count + added_count > MAX_TOKEN_TERMS:
        raise TokenGrowthLimitError(
            f"normalized tokenization exceeds the {MAX_TOKEN_TERMS}-term limit"
        )



ARABIC_DIACRITICS_RE = re.compile(r"[\u0640\u064B-\u065F\u0670\u06D6-\u06ED]")
ARABIC_ALEF_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"})


def _normalize_arabic_for_bm25(text: str) -> str:
    if not any("\u0600" <= ch <= "\u06FF" for ch in text):
        return text
    cleaned = ARABIC_DIACRITICS_RE.sub("", text)
    return cleaned.translate(ARABIC_ALEF_MAP)


def tokenize(text):
    """NFKC-normalize and segment text within input and term growth ceilings."""
    if not isinstance(text, str):
        raise TokenGrowthLimitError("tokenizer input must be text")
    if len(text) > MAX_TOKEN_INPUT_CHARS:
        raise TokenGrowthLimitError(
            f"tokenizer input exceeds the {MAX_TOKEN_INPUT_CHARS}-character limit"
        )
    terms: list[str] = []
    normalized = _normalize_arabic_for_bm25(unicodedata.normalize("NFKC", text))
    if len(normalized) > MAX_TOKEN_INPUT_CHARS:
        raise TokenGrowthLimitError(
            "NFKC-normalized tokenizer input exceeds the "
            f"{MAX_TOKEN_INPUT_CHARS}-character limit"
        )
    for match in TOKEN_RE.finditer(normalized):
        token = match.group(0).lower()
        for run, is_cjk in _script_runs(token):
            if is_cjk:
                _require_term_capacity(len(terms), _cjk_ngram_count(len(run)))
                terms.extend(_cjk_ngrams(run))
                continue
            # A script transition can leave separators at the edge. Strip
            # those artifacts while preserving internal identifiers such as
            # ``search_term`` as one token.
            run = run.strip("'_-")
            if len(run) > 1 and run not in STOPWORDS:
                _require_term_capacity(len(terms), 1)
                terms.append(run)
    return terms


def sha256(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_sha256(value):
    return isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def source_page_is_current(data, vault_root, hash_cache, *, vault_root_fd=None):
    """Validate that a derived chunk still matches an in-vault source page.

    Hashless legacy records are derived caches, not evidence, and must be
    rebuilt. Current records are skipped after a source edit until
    contextual-prefix regenerates them.
    """
    raw_text = data.get("raw_text")
    body_hash = data.get("body_hash")
    if not isinstance(raw_text, str) or not valid_sha256(body_hash):
        return False, "missing or invalid body_hash"
    if sha256(raw_text) != body_hash:
        return False, "chunk body changed"

    page_path = data.get("page_path")
    if not isinstance(page_path, str) or not page_path:
        return False, "missing page_path"

    rel = Path(page_path)
    # On Windows a drive-less rooted path ("/x") and a drive prefix ("C:x")
    # are not "absolute" under pathlib but still escape a joined root.
    if (
        rel.is_absolute()
        or page_path.startswith(("/", "\\"))
        or re.match(r"^[A-Za-z]:", page_path)
    ):
        return False, "absolute page_path"

    root = vault_root.resolve()
    if ".." in rel.parts or not rel.parts or rel.parts[0] != "wiki":
        return False, "page_path is outside wiki"

    expected_hash = data.get("page_body_hash")
    if not valid_sha256(expected_hash):
        return False, "missing or invalid page_body_hash; rebuild required"
    cache_key = rel.as_posix() if vault_root_fd is not None else str(root / rel)
    if cache_key not in hash_cache:
        try:
            if vault_root_fd is None:
                raw_source = root / rel
                if raw_source.is_symlink():
                    return False, "source page is a symlink"
                source = raw_source.resolve()
                if not source.is_relative_to(root):
                    return False, "page_path escapes vault"
                if not source.is_relative_to((root / "wiki").resolve()):
                    return False, "page_path is outside wiki"
                if not source.is_file():
                    return False, "source page missing"
                # Byte-identical with the fd branch below: read_text would
                # CRLF-normalize, making the same page hash two different ways
                # and permanently marking every chunk stale on CRLF vaults.
                text = source.read_bytes().decode("utf-8")
            else:
                raw = read_vault_regular(
                    root,
                    rel.as_posix(),
                    limit=64 * 1024 * 1024,
                    missing_ok=False,
                    root_fd=vault_root_fd,
                    existing=True,
                )
                assert raw is not None
                text = raw.decode("utf-8")
            hash_cache[cache_key] = sha256(text)
        except (OSError, TransactionError, UnicodeDecodeError):
            hash_cache[cache_key] = None
    if hash_cache[cache_key] != expected_hash:
        return False, "source page changed"
    return True, "current"


def discover_chunks(*, meta_fd=None, vault_root_fd=None):
    """Yield current chunk records for every valid derived chunk on disk.

    The yielded `path` is relative to the directory two levels above CHUNKS_DIR
    (i.e. .vault-meta/chunks/<addr>/ → relative to the vault root). This works
    both in production (CHUNKS_DIR is `<vault>/.vault-meta/chunks`) and when
    tests monkey-patch CHUNKS_DIR to a sandbox `<tmp>/.vault-meta/chunks`.
    """
    rel_root = CHUNKS_DIR.parent.parent
    source_hashes: dict[str, str | None] = {}
    if meta_fd is None:
        if not CHUNKS_DIR.is_dir():
            log(f"ERR: no chunks directory at {CHUNKS_DIR}")
            sys.exit(EXIT_NO_CHUNKS)
        candidates = []
        for chunk_file in sorted(CHUNKS_DIR.glob("*/chunk-*.json")):
            if chunk_file.is_symlink():
                log(f"  skip (unsafe symlink): {chunk_file}")
                continue
            try:
                chunk_file.resolve(strict=True).relative_to(CHUNKS_DIR.resolve())
            except (OSError, ValueError):
                log(f"  skip (path escape): {chunk_file}")
                continue
            try:
                data = json.loads(chunk_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                log(f"  skip (unreadable): {chunk_file} — {e}")
                continue
            candidates.append((chunk_file.parent.name, chunk_file.name, data))
    else:
        candidates = _pinned_chunk_documents(meta_fd)

    for directory_name, file_name, data in candidates:
        chunk_file = CHUNKS_DIR / directory_name / file_name
        address = data.get("page_address")
        idx = data.get("chunk_index")
        text = data.get("contextualized_text") or data.get("raw_text", "")
        if address is None or idx is None:
            continue
        current, reason = source_page_is_current(
            data,
            rel_root,
            source_hashes,
            vault_root_fd=vault_root_fd,
        )
        if not current:
            log(f"  skip (stale): {chunk_file} — {reason}")
            continue
        chunk_id = f"{address}:{idx}"
        rel_path = str(chunk_file.relative_to(rel_root))
        yield chunk_id, rel_path, text, data


def build_index(*, meta_fd=None, vault_root_fd=None):
    docs = {}
    df: Counter[str] = Counter()
    postings = defaultdict(list)

    for chunk_id, rel_path, text, record in discover_chunks(
        meta_fd=meta_fd,
        vault_root_fd=vault_root_fd,
    ):
        if chunk_id in docs:
            log(f"  skip (duplicate chunk_id): {chunk_id} at {rel_path}")
            continue
        try:
            tokens = tokenize(text)
        except TokenGrowthLimitError as exc:
            log(
                f"  skip (token growth limit): {rel_path} — {exc}. "
                "Regenerate bounded chunks with contextual-prefix.py, then rebuild."
            )
            continue
        tf = Counter(tokens)
        docs[chunk_id] = {
            "path": rel_path,
            "dl": len(tokens),
            "body_hash": record.get("body_hash"),
            "page_body_hash": record.get("page_body_hash"),
        }
        for term, count in tf.items():
            df[term] += 1
            postings[term].append([chunk_id, count])

    if not docs:
        log("WARN: no current chunks indexed; writing an empty index")

    avg_dl = (sum(d["dl"] for d in docs.values()) / len(docs)) if docs else 0.0
    vocab = {term: {"df": df[term], "postings": postings[term]}
             for term in sorted(df.keys())}

    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "params": {"k1": K1, "b": B},
        "doc_count": len(docs),
        "avg_dl": avg_dl,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vocab": vocab,
        "docs": docs,
    }


def write_index(index, *, meta_fd=None):
    if meta_fd is not None:
        _atomic_vault_write(
            META_DIR,
            "bm25/index.json",
            json.dumps(index, ensure_ascii=False).encode("utf-8"),
            mode=0o600,
            root_fd=meta_fd,
        )
        return
    BM25_DIR.mkdir(parents=True, exist_ok=True)
    tmp = INDEX_PATH.with_suffix(f".{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, INDEX_PATH)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def _is_int(value):
    """Return true for integers but not bool, which is an int subclass."""
    return isinstance(value, int) and not isinstance(value, bool)


def _finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _require_field(mapping, field):
    if field not in mapping:
        raise IndexValidationError(f"missing field {field!r}")
    return mapping[field]


def validate_index(index):
    """Validate every query-visible field before callers access the index.

    Indexes are disposable derived state, so rejecting an internally
    inconsistent file is safer than trying to salvage a partial result.  The
    bounds also keep adversarial JSON numbers away from BM25's float math.
    """
    if not isinstance(index, dict):
        raise IndexValidationError("index root must be an object")

    schema_version = _require_field(index, "schema_version")
    if not _is_int(schema_version) or schema_version != INDEX_SCHEMA_VERSION:
        raise IndexValidationError(
            f"schema_version must be integer {INDEX_SCHEMA_VERSION}"
        )

    params = _require_field(index, "params")
    if not isinstance(params, dict):
        raise IndexValidationError("params must be an object")
    k1 = _require_field(params, "k1")
    b = _require_field(params, "b")
    if not _finite_number(k1) or not 0.0 < k1 <= MAX_K1:
        raise IndexValidationError(f"params.k1 must be finite and in (0, {MAX_K1:g}]")
    if not _finite_number(b) or not 0.0 <= b <= 1.0:
        raise IndexValidationError("params.b must be finite and in [0, 1]")

    doc_count = _require_field(index, "doc_count")
    if not _is_int(doc_count) or not 0 <= doc_count <= MAX_INDEX_COUNT:
        raise IndexValidationError(
            f"doc_count must be an integer in [0, {MAX_INDEX_COUNT}]"
        )
    avg_dl = _require_field(index, "avg_dl")
    if not _finite_number(avg_dl) or not 0.0 <= avg_dl <= MAX_INDEX_COUNT:
        raise IndexValidationError(
            f"avg_dl must be finite and in [0, {MAX_INDEX_COUNT}]"
        )
    updated_at = _require_field(index, "updated_at")
    if not isinstance(updated_at, str) or not updated_at.strip():
        raise IndexValidationError("updated_at must be a non-empty string")

    docs = _require_field(index, "docs")
    if not isinstance(docs, dict):
        raise IndexValidationError("docs must be an object")
    if len(docs) != doc_count:
        raise IndexValidationError("doc_count does not match docs size")

    total_dl = 0
    for chunk_id, document in docs.items():
        if not isinstance(chunk_id, str) or not chunk_id:
            raise IndexValidationError("docs keys must be non-empty strings")
        if not isinstance(document, dict):
            raise IndexValidationError(f"docs[{chunk_id!r}] must be an object")
        path = _require_field(document, "path")
        if not isinstance(path, str) or not path:
            raise IndexValidationError(f"docs[{chunk_id!r}].path must be a string")
        relative = Path(path)
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or relative.parts[:2] != (".vault-meta", "chunks")
        ):
            raise IndexValidationError(
                f"docs[{chunk_id!r}].path must be under .vault-meta/chunks"
            )
        dl = _require_field(document, "dl")
        if not _is_int(dl) or not 0 <= dl <= MAX_INDEX_COUNT:
            raise IndexValidationError(
                f"docs[{chunk_id!r}].dl must be an integer in [0, {MAX_INDEX_COUNT}]"
            )
        total_dl += dl
        for hash_field in ("body_hash", "page_body_hash"):
            hash_value = document.get(hash_field)
            if hash_value is not None and not isinstance(hash_value, str):
                raise IndexValidationError(
                    f"docs[{chunk_id!r}].{hash_field} must be a string or null"
                )

    expected_avg = total_dl / doc_count if doc_count else 0.0
    if not math.isclose(avg_dl, expected_avg, rel_tol=1e-12, abs_tol=1e-12):
        raise IndexValidationError("avg_dl does not match document lengths")

    vocab = _require_field(index, "vocab")
    if not isinstance(vocab, dict):
        raise IndexValidationError("vocab must be an object")
    for term, entry in vocab.items():
        if not isinstance(term, str) or not term:
            raise IndexValidationError("vocab keys must be non-empty strings")
        if not isinstance(entry, dict):
            raise IndexValidationError(f"vocab[{term!r}] must be an object")
        df = _require_field(entry, "df")
        if not _is_int(df) or not 1 <= df <= doc_count:
            raise IndexValidationError(
                f"vocab[{term!r}].df must be an integer in [1, doc_count]"
            )
        postings = _require_field(entry, "postings")
        if not isinstance(postings, list):
            raise IndexValidationError(f"vocab[{term!r}].postings must be an array")
        seen = set()
        for position, posting in enumerate(postings):
            if not isinstance(posting, list) or len(posting) != 2:
                raise IndexValidationError(
                    f"vocab[{term!r}].postings[{position}] must be [chunk_id, count]"
                )
            chunk_id, count = posting
            if not isinstance(chunk_id, str) or chunk_id not in docs:
                raise IndexValidationError(
                    f"vocab[{term!r}] posting references an unknown document"
                )
            if chunk_id in seen:
                raise IndexValidationError(
                    f"vocab[{term!r}] contains duplicate document postings"
                )
            seen.add(chunk_id)
            if not _is_int(count) or not 1 <= count <= MAX_INDEX_COUNT:
                raise IndexValidationError(
                    f"vocab[{term!r}] posting count must be an integer in "
                    f"[1, {MAX_INDEX_COUNT}]"
                )
        if len(seen) != df:
            raise IndexValidationError(f"vocab[{term!r}].df does not match postings")

    return index


def corrupt_index(reason):
    """Emit the stable corrupt-cache diagnostic and terminate with exit 3."""
    log(f"ERR BM25_INDEX_CORRUPT: {reason}")
    log(
        "  Rebuild with: python3 scripts/bm25-index.py "
        f"--vault {shlex.quote(str(VAULT_ROOT))} build"
    )
    sys.exit(EXIT_INDEX_MISSING)


def load_index():
    if not INDEX_PATH.is_file():
        log(f"ERR: no index at {INDEX_PATH}. Run `bm25-index.py build` first.")
        sys.exit(EXIT_INDEX_MISSING)
    try:
        raw = INDEX_PATH.read_text(encoding="utf-8")
    except OSError:
        corrupt_index("index is unreadable")
    try:
        index = json.loads(raw)
    except json.JSONDecodeError:
        corrupt_index("index is not valid JSON")
    try:
        return validate_index(index)
    except IndexValidationError as exc:
        corrupt_index(str(exc))


def query(text, top_k=20):
    idx = load_index()
    vocab = idx["vocab"]
    docs = idx["docs"]
    params = idx["params"]
    avg_dl = idx["avg_dl"]
    N = idx["doc_count"]
    k1 = params["k1"]
    b = params["b"]

    try:
        qterms = tokenize(text)
    except TokenGrowthLimitError as exc:
        raise QueryTooLargeError(str(exc)) from exc
    if not qterms:
        return []

    # Defensive guard (v1.7.2; closes audit L7): avg_dl can only be 0 if the
    # vocab is also empty (all chunks have zero tokens), in which case the
    # loop never enters this divide path. But future refactors could change
    # that invariant; the `or 1.0` keeps it safe by construction.
    avg_dl_safe = avg_dl or 1.0
    scores: defaultdict[str, float] = defaultdict(float)
    for term in qterms:
        v = vocab.get(term)
        if not v:
            continue
        df = v["df"]
        idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
        for cid, cnt in v["postings"]:
            dl = docs[cid]["dl"]
            denom = cnt + k1 * (1 - b + b * dl / avg_dl_safe)
            scores[cid] += idf * (cnt * (k1 + 1)) / denom

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [
        {
            "chunk_id": cid,
            "score": round(score, 6),
            "path": docs[cid]["path"],
            "body_hash": docs[cid].get("body_hash"),
            "page_body_hash": docs[cid].get("page_body_hash"),
        }
        for cid, score in ranked
    ]


def stats():
    idx = load_index()
    print(json.dumps({
        "doc_count": idx["doc_count"],
        "avg_dl": round(idx["avg_dl"], 2),
        "vocab_size": len(idx["vocab"]),
        "updated_at": idx["updated_at"],
        "params": idx["params"],
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="BM25 inverted index over wiki chunks.")
    parser.add_argument("--vault", help="Explicit vault root")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="Build the index (full rebuild every time in v1.7).")

    sp_query = sub.add_parser("query", help="Query the index.")
    sp_query.add_argument("text", help="Query text")
    sp_query.add_argument("--top", type=parse_top_k, default=20, help="Top-K results")

    sub.add_parser("stats", help="Print index stats.")

    raw_argv = sys.argv[1:]
    vault_parser = argparse.ArgumentParser(add_help=False)
    vault_parser.add_argument("--vault")
    vault_args, remaining = vault_parser.parse_known_args(raw_argv)
    args = parser.parse_args(remaining)
    if not configure_vault(vault_args.vault):
        return EXIT_USAGE

    if args.cmd == "build":
        try:
            with MutationLock(VAULT_ROOT, timeout=0.0) as mutation_lock:
                root_fd = mutation_lock.duplicate_root_fd()
                meta_fd = mutation_lock.duplicate_parent_fd()
                try:
                    index = build_index(meta_fd=meta_fd, vault_root_fd=root_fd)
                    write_index(index, meta_fd=meta_fd)
                finally:
                    os.close(meta_fd)
                    os.close(root_fd)
                log(f"Wrote {INDEX_PATH}  docs={index['doc_count']}  vocab={len(index['vocab'])}  avg_dl={index['avg_dl']:.1f}")
        except TransactionError as exc:
            log(f"ERR {exc.code}: {exc}")
            return EXIT_LOCK
        return EXIT_OK

    if args.cmd == "query":
        try:
            results = query(args.text, top_k=args.top)
        except QueryTooLargeError as exc:
            log(f"ERR BM25_QUERY_TOO_LARGE: {exc}. Shorten the query and retry.")
            return EXIT_USAGE
        print(json.dumps(results, indent=2))
        return EXIT_OK

    if args.cmd == "stats":
        stats()
        return EXIT_OK

    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
