#!/usr/bin/env python3
"""test_graph_lint.py — unit tests for scripts/graph-lint.py.

Hermetic: builds a throwaway vault under tempfile, no network, stdlib only.
Covers:
  - basename resolution and inbound counting
  - frontmatter alias resolution (inline AND block YAML list styles)
  - path-style links resolve by last segment
  - broken links reported; whitelisted dangling counted as accepted
  - broken up: detection
  - orphan classification (content vs _system)
  - --strict exit code, --json report contents
  - missing root exits 2

Usage: python3 tests/test_graph_lint.py
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "graph-lint.py")

PASS = 0
FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        print(f"OK   {label}")
        PASS += 1
    else:
        print(f"FAIL {label} {detail}")
        FAIL += 1


def write(base, rel, text):
    path = os.path.join(base, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def run(cwd, *args):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        cwd=cwd, capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        # A links to B by basename and to C by alias; C declares block alias.
        write(tmp, "wiki/A.md",
              "---\ntitle: A\n---\nSee [[B]] and [[Sea Note]].\n")
        write(tmp, "wiki/B.md",
              "---\naliases: [Bee, Buzz]\nup: \"[[A]]\"\n---\nBack to [[A]].\n")
        write(tmp, "wiki/C.md",
              "---\naliases:\n  - Sea Note\nup: \"[[Missing Parent]]\"\n---\n"
              "Inline alias link: [[Bee]]. Path link: [[wiki/A]].\n"
              "Broken: [[Nowhere]]. Dated: [[2026-07-02]].\n")
        # System orphan (underscore prefix) and content orphan.
        write(tmp, "wiki/_index.md", "index, links to nothing resolvable\n")
        write(tmp, "wiki/Lonely.md", "no inbound links\n")
        write(tmp, ".vault-meta/graph-lint-whitelist.txt",
              "# calendar dates are legitimate dangling\n^\\d{4}-\\d{2}-\\d{2}$\n")

        json_path = os.path.join(tmp, "report.json")
        r = run(tmp, "--json", json_path)
        check("exit 0 without --strict", r.returncode == 0, r.stderr)

        with open(json_path, encoding="utf-8") as fh:
            rep = json.load(fh)
        stats = rep["stats"]

        check("scanned 5 files", stats["files"] == 5, str(stats))
        # The up: line is itself a wikilink, so it counts in both categories.
        check("two broken instances (Nowhere + up target)",
              stats["broken_instances"] == 2, str(rep["broken"]))
        broken_targets = {t for v in rep["broken"].values() for t in v}
        check("broken targets are Nowhere and Missing Parent",
              broken_targets == {"Nowhere", "Missing Parent"},
              str(broken_targets))
        check("date accepted via whitelist",
              stats["accepted_dangling"] == 1, str(stats))
        check("up: A resolved, Missing Parent broken",
              stats["up"] == 2 and stats["broken_up"] == 1, str(stats))
        check("Lonely.md is a content orphan",
              any(p.endswith("Lonely.md") for p in rep["orphan_content"]),
              str(rep["orphan_content"]))
        check("_index.md is a system orphan",
              any(p.endswith("_index.md") for p in rep["orphan_system"]),
              str(rep["orphan_system"]))
        check("A/B/C are not orphans",
              not any(p.endswith(("A.md", "B.md", "C.md"))
                      for p in rep["orphans"]), str(rep["orphans"]))

        r = run(tmp, "--strict")
        check("--strict exits 1 while broken links remain",
              r.returncode == 1, str(r.returncode))

        # Fix the breakages: create the missing pages; strict goes green.
        write(tmp, "wiki/Nowhere.md", "now exists, links [[A]]\n")
        write(tmp, "wiki/Missing Parent.md", "parent MOC, links [[A]]\n")
        r = run(tmp, "--strict")
        check("--strict exits 0 once fixed", r.returncode == 0,
              r.stdout + r.stderr)

        r = run(tmp, "--root", "no-such-dir")
        check("missing root exits 2", r.returncode == 2, str(r.returncode))

    print()
    print(f"{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
