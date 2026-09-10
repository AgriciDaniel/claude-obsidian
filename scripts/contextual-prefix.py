#!/usr/bin/env python3
"""contextual-prefix.py — chunk wiki pages and generate per-chunk contextual prefixes.

Implements the ingest-side of Anthropic's Sept 2024 Contextual Retrieval pattern
(https://www.anthropic.com/news/contextual-retrieval). For each chunk of a wiki
page, generates a 1-2 sentence prefix situating the chunk in its source. The
prefixed text is what gets BM25-indexed and embedded. Anthropic reported a
35-49% retrieval-failure reduction in its upstream experiments; this local
implementation requires evaluation on each vault and makes no fixed gain claim.

Three-tier prefix generation (chosen per-run automatically):
  1. If ANTHROPIC_API_KEY is set      → direct Anthropic API call (Haiku 4.5)
                                         with prompt caching on the page body
                                         (only when the body clears the ~16 KB
                                         Haiku 4.5 cache floor; see
                                         cache_control_for()).
                                         Cost varies by current provider pricing,
                                         model, cache behavior, and document size.
                                         REQUIRES --allow-egress (sends bodies off-machine).
  2. Elif `claude` binary on PATH     → `claude -p` subprocess (uses CC subscription;
                                         no API key needed; slower per call).
                                         REQUIRES --allow-egress (subprocess egresses).
  3. Else (default)                   → synthetic prefix from page frontmatter +
                                         first paragraph (zero-cost floor; loses
                                         most of the contextual benefit but BM25
                                         and vector channels still work).

Data-egress posture (v1.7.1+):
  Tiers 1 and 2 send wiki page bodies off-machine. Both are GATED behind
  --allow-egress (default off). Without the flag, pick_prefix_tier() always
  returns "synthetic" regardless of env vars or claude binary presence.
  Mirror of scripts/tiling-check.py:351 --allow-remote-ollama precedent.

Chunk growth bounds:
  Paragraph-aware chunks target 2,000 characters but are hard-split at 4,000
  characters with a 200-character overlap. Context prefixes are capped at 1,000
  characters. This keeps generated contextualized text below bm25-index.py's
  documented 20,000-term expansion ceiling, including 1/2/3-gram CJK text.

Chunk schema written to .vault-meta/chunks/<page-address>/chunk-NNN.json:
{
  "schema_version": 1,
  "page_path": "wiki/concepts/Foo.md",
  "page_address": "c-000042",
  "chunk_index": 3,
  "raw_text": "...",
  "contextualized_text": "<prefix> <raw_text>",
  "prefix_source": "anthropic-api" | "claude-cli" | "synthetic" | "skipped",
  "char_count": 487,
  "body_hash": "sha256:...",     # of raw_text
  "page_body_hash": "sha256:...", # of the WHOLE source page (for invalidation)
  "created_at": "2026-05-17T..."
}

Pages without an `address:` frontmatter field are still chunked (using a
full SHA-256 synthetic address derived from the canonical vault-relative path)
so this tool works on v1.6 vaults without DragonScale Mechanism 2 enabled.

Usage:
  contextual-prefix.py --vault PATH --all # select a vault explicitly
  contextual-prefix.py PATH               # process a single page
  contextual-prefix.py --all              # process every wiki/*.md
  contextual-prefix.py PATH --no-llm      # force synthetic-prefix tier 3
  contextual-prefix.py PATH --rebuild     # ignore existing chunks
  contextual-prefix.py PATH --peek        # print what would happen; write nothing

Exit codes:
  0 — success
  2 — usage error
  3 — page file missing or unreadable
  4 — chunk dir creation failed
  5 — duplicate page address detected; no chunks were changed
  6 — another vault writer holds the operation lock
"""

import argparse
import hashlib
import http.client
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import urllib.error
import urllib.request
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
    _confined_vault_unlink,
    _safe_hash,
    _safe_vault_path,
    read_vault_regular,
)

VAULT_ROOT = Path.cwd().resolve()
WIKI_DIR = VAULT_ROOT / "wiki"
META_DIR = VAULT_ROOT / ".vault-meta"
CHUNKS_DIR = META_DIR / "chunks"
BM25_INDEX_PATH = META_DIR / "bm25" / "index.json"

CHUNK_TARGET_TOKENS = 500  # rough; we approximate via chars/4
CHUNK_TARGET_CHARS = CHUNK_TARGET_TOKENS * 4
CHUNK_OVERLAP_CHARS = 200
CHUNK_HARD_MAX_CHARS = 4000
CONTEXT_PREFIX_MAX_CHARS = 1000

ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_TIMEOUT_SEC = 30
ANTHROPIC_RESPONSE_MAX_BYTES = 256 * 1024
CLAUDE_CLI_TIMEOUT_SEC = 60

# Anthropic prompt caching ignores any cached prefix below the model's minimum
# cacheable size — 4,096 tokens for Haiku 4.5 (verified against the prompt-caching
# docs, 2026-05). At ~4 chars/token that is ~16 KB. We attach cache_control only
# when the body clears this floor so the marker reflects reality: below the floor
# the API treats it as a silent no-op. The per-call local cache statistics in
# anthropic_api_prefix() is what actually measures hit rate. The check counts the
# body only — a deliberately conservative ~370-char underestimate that ignores the
# system_msg + <page> wrapper also inside the cached prefix — so near the boundary
# it errs toward not-marking, never toward a wrongly-attached marker.
HAIKU_CACHE_MIN_CHARS = 16384  # 4096 tokens * 4 chars/token

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_PAGE_MISSING = 3
EXIT_CHUNK_DIR = 4
EXIT_ADDRESS_COLLISION = 5
EXIT_LOCK = 6

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
ADDRESS_RE = re.compile(r"^address:\s*([cl]-\d{6})\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^title:\s*['\"]?(.+?)['\"]?\s*$", re.MULTILINE)


def configure_vault(explicit=None):
    global VAULT_ROOT, WIKI_DIR, META_DIR, CHUNKS_DIR, BM25_INDEX_PATH
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
    WIKI_DIR = VAULT_ROOT / "wiki"
    META_DIR = VAULT_ROOT / ".vault-meta"
    CHUNKS_DIR = META_DIR / "chunks"
    BM25_INDEX_PATH = META_DIR / "bm25" / "index.json"
    try:
        for relative in (
            "wiki",
            ".vault-meta",
            ".vault-meta/chunks",
            ".vault-meta/bm25/index.json",
        ):
            _safe_vault_path(VAULT_ROOT, relative)
    except (VaultSelectionError, TransactionError) as exc:
        log(f"ERR {exc.code}: {exc}")
        return False
    return True


def log(msg):
    print(msg, file=sys.stderr)


def sha256(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _directory_flags():
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )


def _open_runtime_directory(parent_fd, name):
    descriptor = os.open(name, _directory_flags(), dir_fd=parent_fd)
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise OSError(f"runtime component is not a directory: {name}")
    return descriptor


def _pinned_chunk_paths(meta_fd):
    """List chunk records from one pinned metadata namespace."""

    try:
        chunks_fd = _open_runtime_directory(meta_fd, "chunks")
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise TransactionError(
            "UNSAFE_RUNTIME_PATH", f"cannot open pinned chunks directory: {exc}"
        ) from exc
    paths = []
    try:
        with os.scandir(chunks_fd) as addresses:
            names = sorted(
                entry.name for entry in addresses if entry.is_dir(follow_symlinks=False)
            )
        for address in names:
            try:
                address_fd = _open_runtime_directory(chunks_fd, address)
            except OSError:
                continue
            try:
                with os.scandir(address_fd) as entries:
                    for entry in sorted(entries, key=lambda value: value.name):
                        if (
                            entry.is_file(follow_symlinks=False)
                            and entry.name.startswith("chunk-")
                            and entry.name.endswith(".json")
                        ):
                            paths.append(CHUNKS_DIR / address / entry.name)
            finally:
                os.close(address_fd)
    finally:
        os.close(chunks_fd)
    return paths


def _read_pinned_runtime(path, meta_fd):
    relative = path.relative_to(META_DIR).as_posix()
    raw = read_vault_regular(
        META_DIR,
        relative,
        limit=8 * 1024 * 1024,
        missing_ok=False,
        root_fd=meta_fd,
    )
    assert raw is not None
    return json.loads(raw.decode("utf-8"))


def invalidate_bm25_index(*, meta_fd=None):
    """Remove a derived index before changing its source chunk set."""
    try:
        if meta_fd is None:
            base = VAULT_ROOT
            relative = BM25_INDEX_PATH.relative_to(VAULT_ROOT).as_posix()
        else:
            base = META_DIR
            relative = BM25_INDEX_PATH.relative_to(META_DIR).as_posix()
        digest = _safe_hash(base, relative, root_fd=meta_fd)
        if digest is None:
            return False
        _confined_vault_unlink(base, relative, expected_sha256=digest, root_fd=meta_fd)
        log(f"   invalidated stale BM25 index: {BM25_INDEX_PATH}")
        return True
    except (OSError, TransactionError) as e:
        log(f"ERR: cannot invalidate stale BM25 index {BM25_INDEX_PATH}: {e}")
        raise SystemExit(EXIT_CHUNK_DIR)


def chunk_record_matches(
    path,
    page_path,
    address,
    index,
    body_hash,
    page_body_hash,
    *,
    meta_fd=None,
):
    """Return whether an existing derived record exactly matches its source."""
    try:
        if meta_fd is None:
            if path.is_symlink():
                return False
            path.resolve(strict=True).relative_to(CHUNKS_DIR.resolve())
            record = json.loads(path.read_text(encoding="utf-8"))
        else:
            record = _read_pinned_runtime(path, meta_fd)
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        OSError,
        ValueError,
        TransactionError,
    ):
        return False
    return (
        record.get("page_path") == page_path
        and record.get("page_address") == address
        and record.get("chunk_index") == index
        and record.get("body_hash") == body_hash
        and record.get("page_body_hash") == page_body_hash
    )


def stale_chunks_for_page(page_path, chunk_dir, active_paths, *, meta_fd=None):
    """Find surplus chunks for a page, including records under an old address."""
    if meta_fd is None:
        stale = set(chunk_dir.glob("chunk-*.json")) - active_paths
        if not CHUNKS_DIR.is_dir():
            return stale
        candidates = CHUNKS_DIR.glob("*/chunk-*.json")
    else:
        candidates = _pinned_chunk_paths(meta_fd)
        stale = {
            path
            for path in candidates
            if path.parent == chunk_dir and path not in active_paths
        }
    if meta_fd is None and not CHUNKS_DIR.is_dir():
        return stale
    for candidate in candidates:
        if candidate in active_paths or candidate in stale:
            continue
        if meta_fd is None and candidate.is_symlink():
            stale.add(candidate)
            continue
        try:
            if meta_fd is None:
                candidate.resolve(strict=True).relative_to(CHUNKS_DIR.resolve())
        except (OSError, ValueError):
            stale.add(candidate)
            continue
        try:
            record = (
                json.loads(candidate.read_text(encoding="utf-8"))
                if meta_fd is None
                else _read_pinned_runtime(candidate, meta_fd)
            )
        except (json.JSONDecodeError, UnicodeDecodeError, OSError, TransactionError):
            continue
        if record.get("page_path") == page_path:
            stale.add(candidate)
    return stale


def remove_stale_chunks(paths, peek=False, *, meta_fd=None):
    """Remove derived chunk files and now-empty address directories."""
    removed = 0
    for path in sorted(paths):
        if peek:
            log(f"   would remove stale {path.relative_to(VAULT_ROOT)}")
            continue
        try:
            if meta_fd is None:
                base = VAULT_ROOT
                relative = path.relative_to(VAULT_ROOT).as_posix()
            else:
                base = META_DIR
                relative = path.relative_to(META_DIR).as_posix()
            digest = _safe_hash(base, relative, root_fd=meta_fd)
            if digest is None:
                continue
            _confined_vault_unlink(
                base, relative, expected_sha256=digest, root_fd=meta_fd
            )
            removed += 1
        except (OSError, TransactionError) as e:
            log(f"ERR: cannot remove stale chunk {path}: {e}")
            raise SystemExit(EXIT_CHUNK_DIR)
    return removed


def reconcile_chunk_store(active_paths, peek=False, *, meta_fd=None):
    """Prune derived chunks not produced by a complete ``--all`` scan."""
    active = set(active_paths)
    if meta_fd is None:
        if not CHUNKS_DIR.is_dir():
            return 0
        stale = set(CHUNKS_DIR.glob("*/chunk-*.json")) - active
    else:
        stale = set(_pinned_chunk_paths(meta_fd)) - active
    if stale and not peek:
        invalidate_bm25_index(meta_fd=meta_fd)
    return remove_stale_chunks(stale, peek=peek, meta_fd=meta_fd)


def read_page(path, *, root_fd=None):
    if root_fd is None:
        if not path.is_file():
            raise SystemExit(EXIT_PAGE_MISSING)
        # Byte-identical with the fd branch below: read_text would CRLF-
        # normalize, so the same page would hash differently per branch and
        # every derived chunk would be treated as stale on CRLF vaults.
        return path.read_bytes().decode("utf-8", errors="replace")
    try:
        relative = path.relative_to(VAULT_ROOT).as_posix()
        raw = read_vault_regular(
            VAULT_ROOT,
            relative,
            limit=64 * 1024 * 1024,
            missing_ok=False,
            root_fd=root_fd,
        )
    except (ValueError, TransactionError) as exc:
        log(f"ERR: cannot read pinned page {path}: {exc}")
        raise SystemExit(EXIT_PAGE_MISSING) from exc
    assert raw is not None
    return raw.decode("utf-8", errors="replace")


def parse_frontmatter(body):
    m = FRONTMATTER_RE.match(body)
    if not m:
        return {}, body
    fm_text = m.group(1)
    rest = body[m.end() :]
    addr_m = ADDRESS_RE.search(fm_text)
    title_m = TITLE_RE.search(fm_text)
    return {
        "address": addr_m.group(1) if addr_m else None,
        "title": title_m.group(1) if title_m else None,
        "raw": fm_text,
    }, rest


def derive_synthetic_address(page_path):
    """Stable per-path address-shaped string when no real address is set.
    A full SHA-256 namespace avoids the 24-bit birthday collisions produced by
    the historical six-hex form. Distinct from allocator addresses; used only
    for derived chunk filing.
    """
    rel = page_path.relative_to(VAULT_ROOT).as_posix()
    return "syn-" + hashlib.sha256(rel.encode("utf-8")).hexdigest()


def preflight_unique_addresses(page_paths, *, root_fd=None):
    """Validate the whole vault address namespace before any derived write."""
    seen: dict[str, Path] = {}
    for page_path in sorted(page_paths):
        body = read_page(page_path, root_fd=root_fd)
        fm, _ = parse_frontmatter(body)
        address = fm.get("address") or derive_synthetic_address(page_path)
        prior = seen.get(address)
        if prior is not None:
            first = prior.relative_to(VAULT_ROOT).as_posix()
            second = page_path.relative_to(VAULT_ROOT).as_posix()
            log(
                f"ERR: duplicate page address {address}: {first} and {second}; "
                "no chunks were changed"
            )
            return False
        seen[address] = page_path
    return True


def _hard_split_chunk(text, hard_max_chars, overlap):
    """Split one oversized chunk with deterministic bounded overlap."""
    if len(text) <= hard_max_chars:
        return [text]
    pieces = []
    start = 0
    while start < len(text):
        end = min(start + hard_max_chars, len(text))
        pieces.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return pieces


def chunk_body(
    body,
    target_chars=CHUNK_TARGET_CHARS,
    overlap=CHUNK_OVERLAP_CHARS,
    hard_max_chars=CHUNK_HARD_MAX_CHARS,
):
    """Split body into overlapping chunks on paragraph boundaries when possible.
    Heuristic: walk the body, accumulate paragraphs until len exceeds target,
    flush, then keep the trailing `overlap` chars as the seed of the next chunk.
    Empty paragraphs collapse to single boundaries. A final hard split ensures
    an oversized single paragraph can never bypass ``hard_max_chars``.
    """
    if target_chars <= 0:
        raise ValueError("target_chars must be positive")
    if hard_max_chars <= 0 or overlap < 0 or overlap >= hard_max_chars:
        raise ValueError("overlap must be non-negative and smaller than hard_max_chars")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    chunks = []
    cur = []
    cur_len = 0
    for p in paragraphs:
        cur.append(p)
        cur_len += len(p) + 2
        if cur_len >= target_chars:
            chunk_text = "\n\n".join(cur)
            chunks.append(chunk_text)
            # seed next chunk with the tail
            tail = chunk_text[-overlap:] if overlap > 0 else ""
            cur = [tail] if tail else []
            cur_len = len(tail)
    if cur and "".join(cur).strip():
        trailing = "\n\n".join(cur)
        # After a terminal flush ``cur`` contains only the overlap seed. It is
        # context for a future paragraph, not a standalone duplicate chunk.
        overlap_only = bool(chunks and overlap and trailing == chunks[-1][-overlap:])
        if not overlap_only:
            chunks.append(trailing)
    if not chunks and body.strip():
        # tiny page — single chunk
        chunks = [body.strip()]
    bounded = []
    for chunk in chunks:
        bounded.extend(_hard_split_chunk(chunk, hard_max_chars, overlap))
    return bounded


def synthetic_prefix(fm, body, chunk_text):
    """Tier-3 prefix: page title + first sentence of the page body.
    Free, hermetic, deterministic. Provides modest BM25 lift via title-word
    re-injection into the chunk corpus.
    """
    title = (fm.get("title") or "").strip() or "(untitled)"
    # First sentence of the body (not the chunk — gives the chunk a page-level frame)
    first_sentence = re.split(r"(?<=[.!?])\s+", body.strip(), maxsplit=1)
    first = first_sentence[0][:300] if first_sentence else ""
    return f'This passage is from the wiki page "{title}". The page opens: {first}'


def cache_control_for(page_body):
    """Ephemeral cache_control dict when the page body clears the Haiku cache
    floor, else None. Pure function so the floor decision is unit-testable
    without the network (the API call itself stays egress-gated).
    """
    if len(page_body) >= HAIKU_CACHE_MIN_CHARS:
        return {"type": "ephemeral"}
    return None


def anthropic_api_prefix(api_key, page_title, page_body, chunk_text):
    """Tier-1 prefix: direct Anthropic API call, Haiku, prompt-cached page body.

    The page body is the stable prefix shared by every chunk of a page, so it
    goes in `system` behind a cache breakpoint and the variable chunk goes in
    `messages`. Cache reads only land because chunks are processed sequentially
    (chunk 0 warms the prefix) — see the loop note in process_page().
    """
    system_msg = (
        "You are a retrieval-augmentation assistant. Given a wiki page and one "
        "chunk extracted from it, write a single short sentence (under 35 words) "
        "that situates the chunk within the page's scope and topic. Output only "
        "the sentence — no prefix, no quotation marks, no commentary."
    )
    page_block = {
        "type": "text",
        "text": f'<page title="{page_title}">\n{page_body}\n</page>',
    }
    cc = cache_control_for(page_body)
    if cc:
        page_block["cache_control"] = cc
    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 100,
        "system": [
            {"type": "text", "text": system_msg},
            page_block,
        ],
        "messages": [
            {
                "role": "user",
                "content": (
                    "Write the single contextualizing sentence for this chunk:\n\n"
                    f"<chunk>\n{chunk_text}\n</chunk>"
                ),
            }
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        # The request target is the module-level fixed HTTPS Anthropic API URL.
        with urllib.request.urlopen(req, timeout=ANTHROPIC_TIMEOUT_SEC) as resp:  # nosec B310
            raw = resp.read(ANTHROPIC_RESPONSE_MAX_BYTES + 1)
            if len(raw) > ANTHROPIC_RESPONSE_MAX_BYTES:
                log("  anthropic-api response exceeded the safe byte limit")
                return None
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                log("  anthropic-api response has an invalid object shape")
                return None
            # Local cache statistics: integer token counts only, never page content, so
            # the data-egress posture holds. Confirms whether the body cache is
            # actually firing given the Haiku floor (wrote>0 on chunk 0, read>0
            # on later chunks of the same page).
            usage = data.get("usage", {})
            if not isinstance(usage, dict):
                usage = {}
            log(
                f"  cache: wrote={usage.get('cache_creation_input_tokens', 0)} "
                f"read={usage.get('cache_read_input_tokens', 0)} tok"
            )
            content = data.get("content", [])
            if not isinstance(content, list):
                log("  anthropic-api response has an invalid content shape")
                return None
            for block in content:
                if not isinstance(block, dict):
                    log("  anthropic-api response has an invalid content block")
                    return None
                if block.get("type") == "text":
                    text = block.get("text")
                    if not isinstance(text, str):
                        log("  anthropic-api response has invalid text content")
                        return None
                    lines = text.strip().splitlines()
                    return lines[0] if lines else None
    except (
        http.client.HTTPException,
        OSError,
        RecursionError,
        urllib.error.URLError,
        UnicodeDecodeError,
        ValueError,
        KeyError,
    ):
        log("  anthropic-api call failed safely")
        return None
    return None


def claude_cli_prefix(page_title, page_body, chunk_text):
    """Tier-2 prefix: `claude -p` subprocess (uses CC subscription, no API key)."""
    prompt = (
        f'Wiki page "{page_title}":\n\n'
        f"---\n{page_body[:4000]}\n---\n\n"
        f"Chunk:\n<chunk>\n{chunk_text}\n</chunk>\n\n"
        "Write one short sentence (under 35 words) situating this chunk within "
        "the page's scope. Output only the sentence."
    )
    try:
        result = subprocess.run(
            ["claude", "-p"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=CLAUDE_CLI_TIMEOUT_SEC,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().splitlines()[0]
        log(f"  claude-cli rc={result.returncode}: {result.stderr.strip()[:200]}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log(f"  claude-cli call failed: {e}")
    return None


def pick_prefix_tier(force_synthetic, allow_egress=False):
    """Choose the contextual-prefix generation tier.

    Without allow_egress=True, ALWAYS returns "synthetic" regardless of
    env vars or claude binary availability. This is the v1.7.1 data-egress
    guard: tiers 1 (Anthropic API) and 2 (claude CLI subprocess) both send
    wiki page bodies off-machine, so they require explicit user consent via
    the --allow-egress flag at the CLI layer.

    Mirrors scripts/tiling-check.py:351 --allow-remote-ollama default-deny.
    """
    if force_synthetic or not allow_egress:
        return "synthetic"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic-api"
    if shutil.which("claude"):
        return "claude-cli"
    return "synthetic"


def generate_prefix(tier, fm, body, chunk_text):
    """Asymmetric fallback by design:
    - tier="anthropic-api" → on failure, try claude-cli (subprocess,
      free) before synthetic. The API is the user's stated preference,
      and claude-cli is the closer-in-quality fallback.
    - tier="claude-cli"    → on failure, go straight to synthetic. The
      user has either no API key or has not opted into one; climbing
      back to the API would silently spend money they did not authorize.
    - tier="synthetic"     → always synthetic.
    """
    title = fm.get("title") or "(untitled)"
    if tier == "anthropic-api":
        result = anthropic_api_prefix(
            os.environ["ANTHROPIC_API_KEY"], title, body, chunk_text
        )
        if result:
            return result, "anthropic-api"
        if shutil.which("claude"):
            result = claude_cli_prefix(title, body, chunk_text)
            if result:
                return result, "claude-cli"
        return synthetic_prefix(fm, body, chunk_text), "synthetic"
    if tier == "claude-cli":
        result = claude_cli_prefix(title, body, chunk_text)
        if result:
            return result, "claude-cli"
        return synthetic_prefix(fm, body, chunk_text), "synthetic"
    return synthetic_prefix(fm, body, chunk_text), "synthetic"


def process_page(
    page_path,
    force_synthetic=False,
    rebuild=False,
    peek=False,
    allow_egress=False,
    progress_label="",
    root_fd=None,
    meta_fd=None,
):
    body = read_page(page_path, root_fd=root_fd)
    fm, content = parse_frontmatter(body)
    address = fm.get("address") or derive_synthetic_address(page_path)
    page_body_hash = sha256(body)
    chunk_dir = CHUNKS_DIR / address
    try:
        _safe_vault_path(VAULT_ROOT, chunk_dir.relative_to(VAULT_ROOT).as_posix())
    except TransactionError as exc:
        log(f"ERR: unsafe chunk directory for {address}: {exc}")
        raise SystemExit(EXIT_CHUNK_DIR) from exc
    chunks = chunk_body(content)
    tier = pick_prefix_tier(force_synthetic, allow_egress=allow_egress)
    progress = (progress_label + " ") if progress_label else ""
    page_rel = str(page_path.relative_to(VAULT_ROOT))

    planned = []
    active_paths = set()
    skipped = 0
    for idx, raw in enumerate(chunks):
        chunk_path = chunk_dir / f"chunk-{idx:03d}.json"
        body_hash = sha256(raw)
        active_paths.add(chunk_path)
        unchanged = (
            not rebuild
            and chunk_path.exists()
            and chunk_record_matches(
                chunk_path,
                page_rel,
                address,
                idx,
                body_hash,
                page_body_hash,
                meta_fd=meta_fd,
            )
        )
        if unchanged:
            skipped += 1
        else:
            planned.append((idx, raw, body_hash, chunk_path))

    stale_paths = stale_chunks_for_page(
        page_rel,
        chunk_dir,
        active_paths,
        meta_fd=meta_fd,
    )
    if (planned or stale_paths) and not peek:
        # Invalidate first. If this process later fails, retrieval becomes
        # unavailable rather than silently reading an index for a mixed chunk set.
        invalidate_bm25_index(meta_fd=meta_fd)

    if not chunks:
        log(
            f"{progress}WARN: {page_rel} has no chunkable body content "
            f"(empty after frontmatter strip). Removing derived chunks for this page."
        )
        removed = remove_stale_chunks(stale_paths, peek=peek, meta_fd=meta_fd)
        return {
            "address": address,
            "written": [],
            "skipped": 0,
            "removed": removed,
            "tier": tier,
            "active_paths": active_paths,
        }

    log(
        f"{progress}-> {page_rel}  address={address}  chunks={len(chunks)}  tier={tier}"
    )

    written = []

    # Keep this loop sequential. The tier-1 Anthropic path caches the page body;
    # a cache entry is only readable after the first response begins (Anthropic
    # prompt-caching concurrency rule), so chunk 0 warms the prefix and chunks
    # 1..N read it. Parallelizing here would silently zero every cache read.
    for idx, raw, body_hash, chunk_path in planned:
        if peek:
            log(f"   would write {chunk_path.name} ({len(raw)} chars)")
            continue

        prefix, prefix_source = generate_prefix(tier, fm, content, raw)
        prefix = (prefix or "").strip()[:CONTEXT_PREFIX_MAX_CHARS].rstrip()
        contextualized = f"{prefix}\n\n{raw}" if prefix else raw

        record = {
            "schema_version": 1,
            "page_path": page_rel,
            "page_address": address,
            "chunk_index": idx,
            "raw_text": raw,
            "contextualized_text": contextualized,
            "prefix": prefix or "",
            "prefix_source": prefix_source,
            "char_count": len(raw),
            "body_hash": body_hash,
            "page_body_hash": page_body_hash,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        try:
            if meta_fd is None:
                base = VAULT_ROOT
                relative = chunk_path.relative_to(VAULT_ROOT).as_posix()
            else:
                base = META_DIR
                relative = chunk_path.relative_to(META_DIR).as_posix()
            data = json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8")
            _atomic_vault_write(
                base,
                relative,
                data,
                mode=0o600,
                root_fd=meta_fd,
            )
        except (OSError, TransactionError) as exc:
            log(f"ERR: cannot write confined chunk {chunk_path.name}: {exc}")
            raise SystemExit(EXIT_CHUNK_DIR) from exc
        written.append(chunk_path.name)

    removed = remove_stale_chunks(stale_paths, peek=peek, meta_fd=meta_fd)
    log(
        f"   wrote={len(written)}  skipped(unchanged)={skipped}  removed(stale)={removed}"
    )
    return {
        "address": address,
        "written": written,
        "skipped": skipped,
        "removed": removed,
        "tier": tier,
        "active_paths": active_paths,
    }


def collect_pages(target):
    if target == "--all" or target is None:
        pages = []
        for path in WIKI_DIR.rglob("*.md"):
            relative_parts = path.relative_to(WIKI_DIR).parts
            if (
                any(part.startswith(".") for part in relative_parts)
                or path.is_symlink()
            ):
                continue
            try:
                path.resolve(strict=True).relative_to(WIKI_DIR.resolve())
            except (OSError, ValueError):
                continue
            pages.append(path)
        return sorted(pages)
    p = Path(target)
    # Deliberately no rooted-/drive-prefix rejection here (unlike the chunk
    # validators in rerank.py/bm25-index.py): this is CLI target selection, and
    # process_selection() enforces containment via resolve()+is_relative_to
    # against WIKI_DIR plus _safe_vault_path before any chunk is touched.
    if not p.is_absolute():
        p = VAULT_ROOT / p
    return [p]


def process_selection(args, pages, *, root_fd=None, meta_fd=None):
    """Process one validated selection while the caller owns the writer lock."""

    # Filter to actual files up front so progress counter is meaningful
    # (v1.7.2; closes audit L2: tier-2 over 47 pages can take 5+ min — the
    # user needs a count, not just per-page log lines).
    files = [p for p in pages if p.is_file()]
    skipped_non_files = len(pages) - len(files)
    if skipped_non_files:
        log(f"({skipped_non_files} non-file paths skipped)")
    # Chunk directories are a vault-global namespace. Even a single-page run
    # must preflight every page, otherwise it could overwrite an existing page
    # that declares the same real address.
    if not preflight_unique_addresses(collect_pages("--all"), root_fd=root_fd):
        return EXIT_ADDRESS_COLLISION
    total = len(files)
    total_written = 0
    total_skipped = 0
    total_removed = 0
    active_paths = set()
    for i, page in enumerate(files, 1):
        result = process_page(
            page,
            force_synthetic=args.no_llm,
            rebuild=args.rebuild,
            peek=args.peek,
            allow_egress=args.allow_egress,
            progress_label=f"[{i}/{total}]",
            root_fd=root_fd,
            meta_fd=meta_fd,
        )
        total_written += len(result["written"])
        total_skipped += result["skipped"]
        total_removed += result["removed"]
        active_paths.update(result["active_paths"])

    if args.path == "--all":
        total_removed += reconcile_chunk_store(
            active_paths,
            peek=args.peek,
            meta_fd=meta_fd,
        )

    log(
        f"\nDone. pages={total}  chunks_written={total_written}  "
        f"chunks_unchanged={total_skipped}  chunks_removed={total_removed}"
    )
    return EXIT_OK


def main():
    parser = argparse.ArgumentParser(description="Chunk + contextualize wiki pages.")
    parser.add_argument("--vault", help="Explicit vault root")
    parser.add_argument(
        "path",
        nargs="?",
        help="Page path relative to vault root. Omit (or pass --all) "
        "to process every wiki page.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process every wiki page (equivalent to omitting path).",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Force tier-3 synthetic prefix (skip LLM calls).",
    )
    parser.add_argument(
        "--allow-egress",
        action="store_true",
        help="Allow tier-1 (Anthropic API) or tier-2 (claude CLI "
        "subprocess) prefix generation. Without this flag, page "
        "bodies stay on-machine and only the tier-3 synthetic "
        "prefix is used. Mirror of tiling-check.py's "
        "--allow-remote-ollama guard.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Re-process chunks even if body_hash matches.",
    )
    parser.add_argument(
        "--peek", action="store_true", help="Print plan, write nothing."
    )
    args = parser.parse_args()
    if not configure_vault(args.vault):
        return EXIT_USAGE

    if args.all and not args.path:
        args.path = "--all"
    elif not args.path:
        # No path and no --all: default to all (matches the help text)
        args.path = "--all"

    pages = collect_pages(args.path)
    # Explicit single-path invocations must point at a readable file inside the
    # vault. --all only ever yields in-vault files, so this guard is explicit-only.
    # Without it a typo'd path exited 0 silently, and an out-of-vault path raised
    # a raw ValueError from relative_to().
    if args.path != "--all":
        target = pages[0].resolve()
        if not target.is_relative_to(WIKI_DIR.resolve()):
            log(
                f"ERR: {args.path} must resolve inside the wiki directory ({WIKI_DIR})."
            )
            return EXIT_USAGE
        try:
            _safe_vault_path(VAULT_ROOT, pages[0].relative_to(VAULT_ROOT).as_posix())
        except (ValueError, TransactionError) as exc:
            log(f"ERR: explicit page path may not traverse symlinks: {exc}")
            return EXIT_USAGE
        if not target.is_file():
            log(f"ERR: {args.path} is not a readable file.")
            return EXIT_PAGE_MISSING
    if args.peek:
        return process_selection(args, pages)

    # Reject a known address collision before creating runtime lock state. The
    # same preflight runs again under the lock to close the check/use window.
    if not preflight_unique_addresses(collect_pages("--all")):
        return EXIT_ADDRESS_COLLISION

    try:
        # Prefix generation and BM25 publication share the vault-wide writer
        # lock. This prevents an index builder from observing and publishing a
        # partially reconciled chunk generation.
        with MutationLock(VAULT_ROOT, timeout=0.0) as mutation_lock:
            root_fd = mutation_lock.duplicate_root_fd()
            meta_fd = mutation_lock.duplicate_parent_fd()
            try:
                return process_selection(
                    args,
                    pages,
                    root_fd=root_fd,
                    meta_fd=meta_fd,
                )
            finally:
                os.close(meta_fd)
                os.close(root_fd)
    except TransactionError as exc:
        log(f"ERR {exc.code}: {exc}")
        return EXIT_LOCK


if __name__ == "__main__":
    sys.exit(main())
