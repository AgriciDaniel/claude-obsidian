#!/usr/bin/env python3
"""Tests for scripts/lint-title-overlap.py.

Self-contained: builds a synthetic wiki tree, runs the script, parses
the tab-separated output. No pytest dependency.

Run:
  python3 tests/test_lint_title_overlap.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lint-title-overlap.py"


def write(p: Path, text: str = "stub\n") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def make_vault(root: Path) -> None:
    # Near-duplicate pair — high overlap (token set differs by one)
    write(root / "concepts" / "KI-Berater-Tagessatz-DE.md")
    write(root / "concepts" / "KI-Berater-Tagessatz-DACH.md")

    # Umlaut handling — strong overlap (2 of 3 tokens) so it crosses 0.55
    write(root / "concepts" / "Geschäftsführer-Haftung.md")
    write(root / "concepts" / "Geschäftsführer-Haftung-Limits.md")

    # Umlaut handling — single-token overlap stays BELOW threshold (correct behavior)
    write(root / "concepts" / "Gewerbe-Anmeldung-DE.md")
    write(root / "concepts" / "Gewerbe-Steuer-DE.md")

    # Distinct pages — should not overlap above threshold
    write(root / "concepts" / "Lean-Canvas.md")
    write(root / "concepts" / "Product-Market-Fit.md")

    # Skip-worthy paths — should not appear in results
    write(root / "_templates" / "concept.md")
    write(root / "folds" / "fold-k3-from-2026-04-10-to-2026-04-23-n8.md")
    write(root / "meta" / "termbase.md")
    write(root / "index.md")
    write(root / "hot.md")
    write(root / "log.md")


def run_script(root: Path, threshold: float = 0.55) -> list[tuple[float, str, str]]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(root), str(threshold)],
        capture_output=True, text=True, check=True,
    )
    pairs: list[tuple[float, str, str]] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        pairs.append((float(parts[0]), parts[1], parts[2]))
    return pairs


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "wiki"
        make_vault(root)
        pairs = run_script(root, threshold=0.55)

    paths_in_pairs = {p for _, a, b in pairs for p in (a, b)}

    # Must include the obvious duplicates
    must_include = [
        ("KI-Berater-Tagessatz-DE.md", "KI-Berater-Tagessatz-DACH.md"),
        ("Geschäftsführer-Haftung.md", "Geschäftsführer-Haftung-Limits.md"),
    ]
    for a, b in must_include:
        matched = any(
            (a in pa and b in pb) or (a in pb and b in pa)
            for _, pa, pb in pairs
        )
        if not matched:
            raise AssertionError(f"Expected pair {a} ↔ {b} not found in:\n{pairs}")

    # Must exclude template, fold, meta, and root meta files
    forbidden_substrings = ["_templates/", "/folds/", "/meta/", "index.md", "hot.md", "log.md"]
    for path in paths_in_pairs:
        for bad in forbidden_substrings:
            if bad in path:
                raise AssertionError(f"Skip-list violation: {path} contains {bad!r}")

    # Distinct pages must NOT be flagged
    distinct = [
        ("Lean-Canvas.md", "Product-Market-Fit.md"),
        ("Gewerbe-Anmeldung-DE.md", "Gewerbe-Steuer-DE.md"),  # single shared token → below threshold
    ]
    for a, b in distinct:
        for _, pa, pb in pairs:
            if (a in pa and b in pb) or (a in pb and b in pa):
                raise AssertionError(
                    f"Distinct pair {a} ↔ {b} unexpectedly flagged"
                )

    print(f"OK — {len(pairs)} pairs found, all expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
