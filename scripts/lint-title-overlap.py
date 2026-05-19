#!/usr/bin/env python3
"""Find pages with overlapping titles via Jaccard similarity over filename tokens.

A cheap, embedding-free duplicate-page pre-filter. Catches near-duplicates
that share filename tokens (e.g. `KI-Berater-DE` vs `KI-Berater-DACH`),
misses semantic duplicates with no shared tokens — pair with semantic
tiling (DragonScale M3) or manual MOC review for those.

Output: lines `score\\tpath-a\\tpath-b`, sorted by score descending,
preceded by a `# Title-overlap findings` header. Lines starting with `#`
are comments.

Usage:
  scripts/lint-title-overlap.py [wiki-root] [threshold]
  scripts/lint-title-overlap.py wiki 0.55

Threshold defaults to 0.55. Standard Jaccard over filename stem tokens,
lowercased, German umlauts preserved, tokens shorter than 3 chars
dropped (filters "de", "ai", "ml").
"""
from __future__ import annotations

import argparse
import re
import sys
from itertools import combinations
from pathlib import Path

SKIP_NAMES = {
    "index.md", "hot.md", "log.md", "overview.md", "_index.md",
    "dashboard.md", "Wiki-Map.md", "Wiki Map.md", "getting-started.md",
    "README.md",
}
SKIP_DIRS = {"_templates", "folds", "meta", "_attachments"}
MIN_TOKEN_LEN = 3
TOKEN_SPLIT = re.compile(r"[^a-z0-9äöüß]+")


def tokens(name: str) -> set[str]:
    stem = Path(name).stem.lower()
    return {t for t in TOKEN_SPLIT.split(stem) if len(t) >= MIN_TOKEN_LEN}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def collect_pages(root: Path) -> list[Path]:
    pages: list[Path] = []
    for p in root.rglob("*.md"):
        if p.name in SKIP_NAMES:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        pages.append(p)
    return pages


def find_overlaps(pages: list[Path], threshold: float) -> list[tuple[float, Path, Path]]:
    findings: list[tuple[float, Path, Path]] = []
    cache = {p: tokens(p.name) for p in pages}
    for a, b in combinations(pages, 2):
        s = jaccard(cache[a], cache[b])
        if s >= threshold:
            findings.append((s, a, b))
    findings.sort(reverse=True, key=lambda t: t[0])
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default="wiki", help="Wiki root directory")
    parser.add_argument("threshold", nargs="?", type=float, default=0.55,
                        help="Jaccard threshold, default 0.55")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    pages = collect_pages(root)
    findings = find_overlaps(pages, args.threshold)

    print(f"# Title-overlap findings (threshold={args.threshold}, pages={len(pages)})")
    print(f"# Format: score\\tpath-a\\tpath-b")
    print()
    for score, a, b in findings:
        ra = a.relative_to(root).as_posix()
        rb = b.relative_to(root).as_posix()
        print(f"{score:.2f}\t{ra}\t{rb}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
