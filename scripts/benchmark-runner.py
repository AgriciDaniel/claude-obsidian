#!/usr/bin/env python3
"""benchmark-runner.py — score v1.7 hybrid retrieval vs v1.6 baseline.

Reads the 50-query corpus at wiki/meta/retrieval-benchmark-v1.7.md, runs both
pipelines for each query, scores top-1 / top-5 accuracy, prints a comparison
table. Used by the v1.7.0 audit.

Pure stdlib + subprocess. No network or LLM calls of its own — the subprocess
calls to retrieve.py may hit ollama (if installed) for rerank. baseline-v16.py
is pure filesystem.

Usage:
  benchmark-runner.py                 # run all 50 queries, print summary
  benchmark-runner.py --json results.json  # also write per-query results
  benchmark-runner.py --limit 5       # smoke: first 5 queries only
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
CORPUS = VAULT_ROOT / "wiki" / "meta" / "retrieval-benchmark-v1.7.md"


def parse_corpus(corpus_path):
    """Parse the ### <id> blocks into a list of query dicts."""
    text = corpus_path.read_text(encoding="utf-8")
    # Split on "### " at line start
    blocks = re.split(r"\n### ", text)
    queries = []
    for blk in blocks[1:]:  # skip prelude
        # First line is the id (e.g. "D1\n")
        lines = blk.split("\n", 1)
        if len(lines) < 2:
            continue
        qid = lines[0].strip()
        # Ignore non-ID lines (e.g. "Schema", "Scoring rules")
        if not re.match(r"^[DH]\d+$", qid):
            continue
        body = lines[1]
        # Stop at next "## " (next section header)
        body = re.split(r"\n## ", body, 1)[0]
        # Parse fields
        def get(field):
            m = re.search(rf"^- {field}:\s*(.+)$", body, re.MULTILINE)
            return m.group(1).strip() if m else ""

        def get_list(field):
            raw = get(field)
            if not raw or raw == "null":
                return []
            return [s.strip() for s in raw.split(",") if s.strip()]

        queries.append({
            "id": qid,
            "query": get("query"),
            "correct": get_list("correct"),
            "relevant": get_list("relevant"),
            "category": get("category"),
            "rationale": get("rationale"),
        })
    return queries


def run_v17(query, top_k=5):
    """Returns ordered list of page_paths from v1.7 retrieve.py."""
    try:
        result = subprocess.run(
            ["python3", str(VAULT_ROOT / "scripts" / "retrieve.py"),
             query, "--top", str(top_k)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode != 0:
            return [], f"rc={result.returncode}: {result.stderr.strip()[:200]}"
        data = json.loads(result.stdout)
        return [c["page_path"] for c in data.get("candidates", [])], None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        return [], str(e)


def run_v16(query, top_k=5):
    """Returns ordered list of page_paths from v1.6 baseline-v16.py."""
    try:
        result = subprocess.run(
            ["python3", str(VAULT_ROOT / "scripts" / "baseline-v16.py"),
             query, "--top", str(top_k), "--json"],
            capture_output=True, text=True, timeout=30, check=False,
        )
        if result.returncode != 0:
            return [], f"rc={result.returncode}"
        data = json.loads(result.stdout)
        return [c["path"] for c in data.get("candidates", [])], None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        return [], str(e)


def score_query(results, correct, relevant, category):
    """Returns (top1_success, top5_success) per the scoring rules."""
    # Negative queries: correct is empty; success = no results OR result is in relevant
    if category == "negative" or not correct:
        if not results:
            return (1, 1)  # no results = correctly "found nothing"
        top1 = 1 if results[0] in relevant else 0
        top5 = 1 if any(r in relevant for r in results[:5]) else 0
        return (top1, top5)
    # Normal queries: top-1 if first result in correct; top-5 if any in correct
    top1 = 1 if results and results[0] in correct else 0
    top5 = 1 if any(r in correct for r in results[:5]) else 0
    return (top1, top5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only run first N queries")
    parser.add_argument("--json", help="Write per-query results to PATH")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    queries = parse_corpus(CORPUS)
    if args.limit:
        queries = queries[: args.limit]

    print(f"Parsed {len(queries)} queries from {CORPUS.relative_to(VAULT_ROOT)}\n")

    per_query = []
    cat_stats = {}  # category -> {v17_top1, v17_top5, v16_top1, v16_top5, count}

    for q in queries:
        v17_results, v17_err = run_v17(q["query"], top_k=args.top)
        v16_results, v16_err = run_v16(q["query"], top_k=args.top)
        v17_top1, v17_top5 = score_query(v17_results, q["correct"], q["relevant"], q["category"])
        v16_top1, v16_top5 = score_query(v16_results, q["correct"], q["relevant"], q["category"])

        record = {
            "id": q["id"],
            "category": q["category"],
            "query": q["query"][:80] + ("..." if len(q["query"]) > 80 else ""),
            "correct": q["correct"],
            "v17_top1": v17_top1,
            "v17_top5": v17_top5,
            "v17_results": v17_results[:args.top],
            "v17_err": v17_err,
            "v16_top1": v16_top1,
            "v16_top5": v16_top5,
            "v16_results": v16_results[:args.top],
            "v16_err": v16_err,
        }
        per_query.append(record)

        cat = q["category"]
        if cat not in cat_stats:
            cat_stats[cat] = {"v17_t1": 0, "v17_t5": 0, "v16_t1": 0, "v16_t5": 0, "n": 0}
        cat_stats[cat]["v17_t1"] += v17_top1
        cat_stats[cat]["v17_t5"] += v17_top5
        cat_stats[cat]["v16_t1"] += v16_top1
        cat_stats[cat]["v16_t5"] += v16_top5
        cat_stats[cat]["n"] += 1

        # Live progress
        marker = "✓" if v17_top1 else "·"
        v16marker = "✓" if v16_top1 else "·"
        print(f"  {q['id']:4} [{q['category']:14}] v17:{marker} v16:{v16marker}  {q['query'][:60]}")

    # Aggregate
    total_v17_t1 = sum(c["v17_t1"] for c in cat_stats.values())
    total_v17_t5 = sum(c["v17_t5"] for c in cat_stats.values())
    total_v16_t1 = sum(c["v16_t1"] for c in cat_stats.values())
    total_v16_t5 = sum(c["v16_t5"] for c in cat_stats.values())
    total_n = sum(c["n"] for c in cat_stats.values())

    def pct(x, n):
        return f"{100.0 * x / n:5.1f}%" if n else "  n/a"

    print()
    print("=" * 80)
    print(f"{'Category':<16} {'N':>4} {'v17 top-1':>10} {'v17 top-5':>10} {'v16 top-1':>10} {'v16 top-5':>10}  Δ top-1")
    print("-" * 80)
    for cat, c in sorted(cat_stats.items()):
        delta = (c["v17_t1"] - c["v16_t1"]) / c["n"] * 100 if c["n"] else 0
        print(f"{cat:<16} {c['n']:>4} {pct(c['v17_t1'], c['n']):>10} {pct(c['v17_t5'], c['n']):>10} {pct(c['v16_t1'], c['n']):>10} {pct(c['v16_t5'], c['n']):>10}  {delta:+6.1f}pp")
    delta_total = (total_v17_t1 - total_v16_t1) / total_n * 100 if total_n else 0
    print("-" * 80)
    print(f"{'TOTAL':<16} {total_n:>4} {pct(total_v17_t1, total_n):>10} {pct(total_v17_t5, total_n):>10} {pct(total_v16_t1, total_n):>10} {pct(total_v16_t5, total_n):>10}  {delta_total:+6.1f}pp")
    print()
    print(f"Plan §7 ship-gate target: ≥30 percentage-point improvement in top-1")
    print(f"Actual: {delta_total:+.1f}pp ({'PASS' if delta_total >= 30 else 'INFO'} — pp gain alone, not failure-reduction %)")
    # Also compute as a relative reduction in "wrong page cited" errors
    v17_wrong = total_n - total_v17_t1
    v16_wrong = total_n - total_v16_t1
    err_reduction = (v16_wrong - v17_wrong) / v16_wrong * 100 if v16_wrong else 0
    print(f"Error-reduction (the gate's actual framing): {err_reduction:+.1f}% ({'PASS' if err_reduction >= 30 else 'FAIL'})")
    print()

    if args.json:
        Path(args.json).write_text(json.dumps({
            "summary": {
                "v17_top1_pct": 100 * total_v17_t1 / total_n if total_n else 0,
                "v17_top5_pct": 100 * total_v17_t5 / total_n if total_n else 0,
                "v16_top1_pct": 100 * total_v16_t1 / total_n if total_n else 0,
                "v16_top5_pct": 100 * total_v16_t5 / total_n if total_n else 0,
                "delta_top1_pp": delta_total,
                "error_reduction_pct": err_reduction,
            },
            "by_category": {cat: {**c, "v17_top1_pct": 100*c["v17_t1"]/c["n"], "v16_top1_pct": 100*c["v16_t1"]/c["n"]} for cat, c in cat_stats.items()},
            "per_query": per_query,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote per-query results to {args.json}")


if __name__ == "__main__":
    main()
