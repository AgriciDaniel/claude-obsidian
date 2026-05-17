#!/usr/bin/env python3
"""bm25-index.py — sparse BM25 inverted index over contextualized wiki chunks.

Pure stdlib (no rank_bm25 dep). Standard Okapi BM25 with k1=1.5, b=0.75.
Indexes the `contextualized_text` field of every chunk under .vault-meta/chunks/,
emits a single JSON file at .vault-meta/bm25/index.json with the schema below.

Concurrency:
- Locks .vault-meta/.bm25.lock (fcntl exclusive) around any index write.
- Atomic .tmp + rename for the index file.

Index schema (.vault-meta/bm25/index.json):
{
  "schema_version": 1,
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

Tokenization: lowercase, collapse whitespace, drop punctuation except in-word
apostrophes and hyphens. ASCII-only stopwords filtered (small list; favors
recall over precision).

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
import fcntl
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
META_DIR = VAULT_ROOT / ".vault-meta"
CHUNKS_DIR = META_DIR / "chunks"
BM25_DIR = META_DIR / "bm25"
INDEX_PATH = BM25_DIR / "index.json"
LOCK_PATH = META_DIR / ".bm25.lock"

K1 = 1.5
B = 0.75

# Small high-frequency-stopword list (English). Conservative — keep recall high.
STOPWORDS = frozenset("""
a an and are as at be by for from has have he her him his i if in is it its
of on or that the their them they this to was were will with you your
""".split())

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'\-]*")

EXIT_OK = 0
EXIT_LOCK = 1
EXIT_USAGE = 2
EXIT_INDEX_MISSING = 3
EXIT_NO_CHUNKS = 4


def log(msg):
    print(msg, file=sys.stderr)


def tokenize(text):
    """Lowercase, strip punctuation, drop stopwords. Returns a list of terms."""
    return [t.lower() for t in TOKEN_RE.findall(text)
            if t.lower() not in STOPWORDS and len(t) > 1]


def acquire_lock():
    META_DIR.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        log("ERR: could not acquire bm25 lock")
        sys.exit(EXIT_LOCK)
    return fd


def release_lock(fd):
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def discover_chunks():
    """Yield (chunk_id, path, contextualized_text) for every chunk on disk.

    The yielded `path` is relative to the directory two levels above CHUNKS_DIR
    (i.e. .vault-meta/chunks/<addr>/ → relative to the vault root). This works
    both in production (CHUNKS_DIR is `<vault>/.vault-meta/chunks`) and when
    tests monkey-patch CHUNKS_DIR to a sandbox `<tmp>/.vault-meta/chunks`.
    """
    if not CHUNKS_DIR.is_dir():
        log(f"ERR: no chunks directory at {CHUNKS_DIR}")
        sys.exit(EXIT_NO_CHUNKS)
    rel_root = CHUNKS_DIR.parent.parent
    for chunk_file in sorted(CHUNKS_DIR.glob("*/chunk-*.json")):
        try:
            data = json.loads(chunk_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            log(f"  skip (unreadable): {chunk_file} — {e}")
            continue
        address = data.get("page_address")
        idx = data.get("chunk_index")
        text = data.get("contextualized_text") or data.get("raw_text", "")
        if address is None or idx is None:
            continue
        chunk_id = f"{address}:{idx}"
        rel_path = str(chunk_file.relative_to(rel_root))
        yield chunk_id, rel_path, text


def build_index():
    docs = {}
    df = Counter()
    postings = defaultdict(list)

    for chunk_id, rel_path, text in discover_chunks():
        tokens = tokenize(text)
        tf = Counter(tokens)
        docs[chunk_id] = {"path": rel_path, "dl": len(tokens)}
        for term, count in tf.items():
            df[term] += 1
            postings[term].append([chunk_id, count])

    if not docs:
        log("WARN: no chunks indexed")
        return None

    avg_dl = sum(d["dl"] for d in docs.values()) / len(docs)
    vocab = {term: {"df": df[term], "postings": postings[term]}
             for term in sorted(df.keys())}

    return {
        "schema_version": 1,
        "params": {"k1": K1, "b": B},
        "doc_count": len(docs),
        "avg_dl": avg_dl,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vocab": vocab,
        "docs": docs,
    }


def write_index(index):
    BM25_DIR.mkdir(parents=True, exist_ok=True)
    tmp = INDEX_PATH.with_suffix(f".{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, INDEX_PATH)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def load_index():
    if not INDEX_PATH.is_file():
        log(f"ERR: no index at {INDEX_PATH}. Run `bm25-index.py build` first.")
        sys.exit(EXIT_INDEX_MISSING)
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log(f"ERR: index corrupt: {e}")
        sys.exit(EXIT_INDEX_MISSING)


def query(text, top_k=20):
    idx = load_index()
    vocab = idx["vocab"]
    docs = idx["docs"]
    params = idx["params"]
    avg_dl = idx["avg_dl"]
    N = idx["doc_count"]
    k1 = params["k1"]
    b = params["b"]

    qterms = tokenize(text)
    if not qterms:
        return []

    scores = defaultdict(float)
    for term in qterms:
        v = vocab.get(term)
        if not v:
            continue
        df = v["df"]
        idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
        for cid, cnt in v["postings"]:
            dl = docs[cid]["dl"]
            denom = cnt + k1 * (1 - b + b * dl / avg_dl)
            scores[cid] += idf * (cnt * (k1 + 1)) / denom

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [
        {
            "chunk_id": cid,
            "score": round(score, 6),
            "path": docs[cid]["path"],
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
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="Build the index (full rebuild every time in v1.7).")

    sp_query = sub.add_parser("query", help="Query the index.")
    sp_query.add_argument("text", help="Query text")
    sp_query.add_argument("--top", type=int, default=20, help="Top-K results")

    sub.add_parser("stats", help="Print index stats.")

    args = parser.parse_args()

    if args.cmd == "build":
        fd = acquire_lock()
        try:
            index = build_index()
            if index is None:
                log("Nothing to index.")
                return EXIT_OK
            write_index(index)
            log(f"Wrote {INDEX_PATH}  docs={index['doc_count']}  vocab={len(index['vocab'])}  avg_dl={index['avg_dl']:.1f}")
        finally:
            release_lock(fd)
        return EXIT_OK

    if args.cmd == "query":
        results = query(args.text, top_k=args.top)
        print(json.dumps(results, indent=2))
        return EXIT_OK

    if args.cmd == "stats":
        stats()
        return EXIT_OK

    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
