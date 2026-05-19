#!/usr/bin/env python3
"""Convert an evals/results/*.json file to a human-readable Markdown summary.

Usage:
  python3 evals/score-summary.py evals/results/<timestamp>.json
  python3 evals/score-summary.py evals/results/<timestamp>.json > summary.md
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: score-summary.py <results.json>", file=sys.stderr)
        return 2

    results_path = Path(argv[0])
    if not results_path.is_file():
        print(f"ERROR: {results_path} not found", file=sys.stderr)
        return 2

    data = json.loads(results_path.read_text())
    by_skill: dict[str, list[dict]] = defaultdict(list)
    for entry in data:
        if not isinstance(entry, dict):
            continue
        by_skill[entry.get("skill", "unknown")].append(entry)

    lines = [
        f"# Eval Run — {results_path.stem}",
        "",
        f"Source: `{results_path}`",
        "",
    ]

    for skill in sorted(by_skill):
        cases = by_skill[skill]
        ok = sum(1 for c in cases if c.get("status") == "ok")
        failed = sum(1 for c in cases if c.get("status") == "fail")
        manual = sum(1 for c in cases if c.get("status") == "manual")
        skipped = sum(1 for c in cases if c.get("status") == "skipped")
        lines.append(f"## {skill}")
        lines.append("")
        lines.append(
            f"- ok: {ok}  |  fail: {failed}  |  manual: {manual}  |  skipped: {skipped}"
        )
        # Aggregate deterministic metrics where available
        recalls = [c["metrics"]["recall"] for c in cases
                   if c.get("metrics", {}).get("recall") is not None]
        if recalls:
            avg = sum(recalls) / len(recalls)
            lines.append(f"- avg recall: {avg:.3f}")
        false_pos = [c["metrics"]["false_positive_rate"] for c in cases
                     if c.get("metrics", {}).get("false_positive_rate") is not None]
        if false_pos:
            avg_fp = sum(false_pos) / len(false_pos)
            lines.append(f"- avg false-positive rate: {avg_fp:.3f}")
        lines.append("")
        for c in cases:
            status = c.get("status", "?")
            case_id = Path(c.get("case", "?")).name
            line = f"  - [{status}] {case_id}"
            metrics = c.get("metrics", {})
            if metrics:
                summary = ", ".join(f"{k}={v}" for k, v in metrics.items())
                line += f"  ({summary})"
            elif c.get("reason"):
                line += f"  ({c['reason']})"
            lines.append(line)
        lines.append("")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
