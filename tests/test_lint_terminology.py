#!/usr/bin/env python3
"""Tests for scripts/lint-terminology.py.

Self-contained: builds a synthetic wiki tree in a tempdir, runs the script
as a subprocess against it, asserts on the JSON output. No pytest dependency.

Run:
  python3 tests/test_lint_terminology.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lint-terminology.py"


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def make_vault(root: Path) -> None:
    """Build a synthetic wiki vault covering all check cases."""
    # 1. Page with dnt_class and proper aliases → no finding
    write(root / "concepts" / "IHK.md", '''---
type: entity
title: "IHK"
dnt_class: eigenname
lang: de
aliases:
  - "IHK"
  - "Industrie- und Handelskammer"
  - "Chamber of Commerce Germany"
---
Body.
''')

    # 2. Page with dnt_class but only one alias → ERROR missing-alias
    write(root / "concepts" / "AGB.md", '''---
type: concept
title: "AGB"
dnt_class: term-of-art
aliases:
  - "AGB"
---
Body.
''')

    # 3. Page with invalid dnt_class value → ERROR invalid-dnt-class
    write(root / "concepts" / "BadClass.md", '''---
type: concept
title: "BadClass"
dnt_class: legalese
aliases:
  - "BadClass"
  - "Bad Class"
---
Body.
''')

    # 4. Translatable page (no dnt_class) → no finding
    write(root / "concepts" / "Lean-Canvas.md", '''---
type: concept
title: "Lean Canvas"
---
Body.
''')

    # 5. Termbase index — references IHK (ok), Ghost (orphan), AGB (ok)
    write(root / "meta" / "termbase.md", '''---
type: meta
title: "Termbase"
---
# Termbase

- [[IHK]] — eigenname
- [[AGB]] — term-of-art
- [[Ghost]] — term-of-art
''')

    # 6. Drift case: page with dnt_class but not in termbase → WARN termbase-drift
    write(root / "concepts" / "Vorstand.md", '''---
type: concept
title: "Vorstand"
dnt_class: term-of-art
aliases:
  - "Vorstand"
  - "management board"
---
Body.
''')


def run_script(root: Path) -> list[dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(root), "--json"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def assert_finding(findings: list[dict], severity: str, check: str, path_substr: str) -> None:
    for f in findings:
        if (f["severity"] == severity and f["check"] == check
                and path_substr in f["path"]):
            return
    raise AssertionError(
        f"Expected {severity} {check} on path containing {path_substr!r}, got:\n"
        + json.dumps(findings, indent=2)
    )


def assert_no_finding(findings: list[dict], check: str, path_substr: str) -> None:
    for f in findings:
        if f["check"] == check and path_substr in f["path"]:
            raise AssertionError(
                f"Unexpected {check} finding on {path_substr}:\n{json.dumps(f, indent=2)}"
            )


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "wiki"
        make_vault(root)
        findings = run_script(root)

    # Expected ERRORs
    assert_finding(findings, "ERROR", "missing-alias", "AGB.md")
    assert_finding(findings, "ERROR", "invalid-dnt-class", "BadClass.md")

    # Expected WARNs
    assert_finding(findings, "WARN", "termbase-drift", "Vorstand.md")
    assert_finding(findings, "WARN", "orphan-termbase-entry", "termbase.md")

    # IHK is fine
    assert_no_finding(findings, "missing-alias", "IHK.md")
    assert_no_finding(findings, "termbase-drift", "IHK.md")

    # Lean-Canvas has no dnt_class — no findings at all
    assert_no_finding(findings, "missing-alias", "Lean-Canvas.md")
    assert_no_finding(findings, "termbase-drift", "Lean-Canvas.md")

    print(f"OK — {len(findings)} findings, all expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
