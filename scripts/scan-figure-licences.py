#!/usr/bin/env python3
"""Scan .raw/Studies PDFs for reuse licences and figure counts.

Answers one question: which figures in the library can legally go into
monetised short-form content? The channel sells an ebook and consultations,
so CC-BY-NC does NOT qualify.

Usage:
    python3 scripts/scan-figure-licences.py [--json]

Requires pymupdf:
    python3 -m venv .venv && .venv/bin/pip install pymupdf
    .venv/bin/python scripts/scan-figure-licences.py
"""
import glob
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import argparse
from claude_obsidian.paths import VaultSelectionError, resolve_vault_root


def vault_root() -> Path:
    """Resolve the vault to act on, failing closed when there is none.

    Never derive paths from __file__: under the installed product tree that
    resolves to the plugin directory, and writing there corrupts the install.
    """
    return resolve_vault_root(plugin_root=PLUGIN_ROOT).root

pymupdf = None


def require_deps():
    """Import the optional dependencies on demand.

    Kept out of module scope so that --help, and any other argument parsing,
    works on a machine where these are not installed.
    """
    global pymupdf
    try:
        import pymupdf
    except ImportError:
        sys.exit('pymupdf not installed — see docstring')

ROOT = ".raw/Studies"
USABLE = ("CC-BY", "CC-BY-SA", "CC0/PD")


def classify(text_lower):
    """Order matters: NC variants must be tested before plain BY."""
    t = text_lower
    if re.search(r"licenses/by-nc-nd|cc[\s-]?by[\s-]?nc[\s-]?nd", t):
        return "CC-BY-NC-ND"
    if re.search(r"licenses/by-nc|cc[\s-]?by[\s-]?nc|noncommercial|non-commercial (?:use|licen)", t):
        return "CC-BY-NC"
    if re.search(r"licenses/by-sa", t):
        return "CC-BY-SA"
    if re.search(r"publicdomain/zero|\bcc0\b", t):
        return "CC0/PD"
    if re.search(r"licenses/by/[34]\.0|creative commons attribution(?![\s-]*non)", t):
        return "CC-BY"
    if re.search(r"all rights reserved", t):
        return "ARR"
    return "UNKNOWN"


def scan():
    rows = []
    for path in sorted(glob.glob(f"{ROOT}/**/*.pdf", recursive=True)):
        try:
            doc = pymupdf.open(path)
            full = "".join(doc[i].get_text() for i in range(doc.page_count)).lower()
        except Exception as exc:
            print(f"  skip {os.path.basename(path)}: {exc}", file=sys.stderr)
            continue
        rows.append({
            "f": os.path.relpath(path, ROOT),
            "lic": classify(full),
            "pages": doc.page_count,
            "figs": len(set(re.findall(r"(?:figure|fig\.)\s*(\d{1,2})[.:]", full))),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="Scan .raw/Studies PDFs for reuse licences and figure counts")
    parser.add_argument("paths", nargs="*", help="files or globs to act on")
    args = parser.parse_args()
    require_deps()
    rows = scan()
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
        return
    counts = Counter(r["lic"] for r in rows)
    print(f"{len(rows)} PDFs scanned\n")
    for lic, n in counts.most_common():
        mark = "OK " if lic in USABLE else "   "
        print(f"  {mark}{lic:14} {n}")
    ok = [r for r in rows if r["lic"] in USABLE]
    print(f"\nCommercially usable: {len(ok)} papers / {sum(r['figs'] for r in ok)} figures")
    for folder, n in Counter(r["f"].split("/")[0] for r in ok).most_common():
        print(f"   {folder}: {n}")
    print("\nUNKNOWN means no licence string was found — verify manually before use.")


if __name__ == "__main__":
    main()
