#!/usr/bin/env python3
"""baseline-v16.py — simulate the v1.6 hot→index→drill retrieval chain.

Exists ONLY for benchmarking v1.7's hybrid retrieval against the legacy
v1.6 behavior. Not used by any v1.7 skill; not feature-gated; not part of
the regular vault workflow.

The v1.6 query path (per skills/wiki-query/SKILL.md before v1.7):
  1. Read wiki/hot.md (always; quick context)
  2. Read wiki/index.md (scan for descriptions matching query terms)
  3. Read top-N pages cited in the index whose entries best match query
  4. Caller synthesizes answer

This script approximates that path by:
  1. Tokenizing the query (same stopword-filtered ASCII tokenizer as bm25-index.py)
  2. Scoring each *.md page in wiki/ by the count of distinct query terms it contains
     (case-insensitive substring on the full file body; no semantic matching)
  3. Returning top-K pages by score, with ties broken by:
     a. Presence in hot.md (boost +5)
     b. Presence in index.md (boost +3)
     c. Total raw term-occurrence count

The simulation is intentionally simple — it represents what a human or a
basic agent does when reading hot/index "by hand" without any retrieval
infrastructure. Anything fancier would not be a fair v1.6 baseline.

Usage:
  baseline-v16.py "your query" [--top 5]
  baseline-v16.py "query" --top 5 --json   # output as JSON (default: text)

Exit codes:
  0 — success
  2 — usage error
  3 — wiki directory missing
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = VAULT_ROOT / "wiki"
HOT_PATH = WIKI_DIR / "hot.md"
INDEX_PATH = WIKI_DIR / "index.md"

# Mirror bm25-index.py's tokenizer + stopword list so comparisons are fair.
STOPWORDS = frozenset("""
a an and are as at be by for from has have he her him his i if in is it its
of on or that the their them they this to was were will with you your
""".split())

# Mirrors bm25-index.py's Unicode-aware tokenizer (v1.7.2; closes M2).
TOKEN_RE = re.compile(r"\w[\w'\-]*", re.UNICODE)

HOT_BOOST = 5.0
INDEX_BOOST = 3.0

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_NO_WIKI = 3


def tokenize(text):
    return [t.lower() for t in TOKEN_RE.findall(text)
            if t.lower() not in STOPWORDS and len(t) > 1]


def page_paths():
    if not WIKI_DIR.is_dir():
        print(f"ERR: no wiki directory at {WIKI_DIR}", file=sys.stderr)
        sys.exit(EXIT_NO_WIKI)
    return sorted(p for p in WIKI_DIR.rglob("*.md")
                  if not any(part.startswith(".") for part in p.parts))


def score_page(page_path, query_terms_set, query_terms_counter):
    """Score by distinct-query-term-presence + boost if cited in hot/index.

    Returns (score, distinct_matches, total_occurrences).
    """
    try:
        body = page_path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return (0.0, 0, 0)

    distinct = sum(1 for term in query_terms_set if term in body)
    total = sum(body.count(term) for term in query_terms_set)
    score = float(distinct) + 0.01 * total  # distinct dominates; total is tiebreak

    # Hot-cache boost: if the page is referenced by name in hot.md
    if HOT_PATH.is_file():
        try:
            hot_body = HOT_PATH.read_text(encoding="utf-8", errors="replace")
            page_stem = page_path.stem
            if page_stem in hot_body or str(page_path.relative_to(VAULT_ROOT)) in hot_body:
                score += HOT_BOOST
        except OSError:
            pass

    # Index boost: page is cited in index.md
    if INDEX_PATH.is_file():
        try:
            index_body = INDEX_PATH.read_text(encoding="utf-8", errors="replace")
            page_stem = page_path.stem
            if page_stem in index_body or str(page_path.relative_to(VAULT_ROOT)) in index_body:
                score += INDEX_BOOST
        except OSError:
            pass

    return (score, distinct, total)


def baseline_query(query, top_k=5):
    """Return list of {path, score, distinct, total} for top-K pages."""
    terms = tokenize(query)
    if not terms:
        return []
    terms_set = set(terms)
    terms_counter = Counter(terms)

    scored = []
    for p in page_paths():
        score, distinct, total = score_page(p, terms_set, terms_counter)
        if score > 0:
            scored.append({
                "path": str(p.relative_to(VAULT_ROOT)),
                "score": round(score, 4),
                "distinct_terms": distinct,
                "total_occurrences": total,
            })

    scored.sort(key=lambda d: d["score"], reverse=True)
    return scored[:top_k]


def main():
    parser = argparse.ArgumentParser(description="v1.6 baseline retrieval simulator.")
    parser.add_argument("query", help="Natural-language query")
    parser.add_argument("--top", type=int, default=5, help="Top-K results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = baseline_query(args.query, top_k=args.top)

    if args.json:
        print(json.dumps({
            "query": args.query,
            "strategy": "baseline-v1.6:hot+index+keyword",
            "top_k": args.top,
            "candidates": results,
        }, indent=2))
    else:
        if not results:
            print("(no matches)")
        else:
            print(f"v1.6 baseline for: {args.query!r}")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['path']}  score={r['score']}  distinct={r['distinct_terms']}  occ={r['total_occurrences']}")

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
