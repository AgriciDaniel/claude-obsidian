#!/usr/bin/env python3
"""Validate a slideshow CSV before it goes anywhere near Canva Bulk Create.

Catches the failure modes that cost a full re-run: wrong column set, empty
cells (Bulk Create leaves a blank element), copy that overflows the text box,
and slides with no open loop to drive the swipe.

Usage:
    python3 scripts/check-deck.py content/<deck>/04-slides.csv
    python3 scripts/check-deck.py "content/*/04-slides.csv"    # quote in zsh

Note the quotes on the glob: zsh errors on an unmatched glob before the script
ever runs, so quoting hands the pattern through for the script to expand.
"""
import csv
import os
import xml.dom.minidom
import glob
import re
import sys
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

COLUMNS = ["headline", "subhead", "body", "punch"]

# Ceilings measured against the built Canva template. Raise these only after
# re-testing the template — they are what guarantees copy fits the boxes.
LIMITS = {"headline": 36, "subhead": 48, "body": 620, "punch": 160}

# Deliberately NOT checked: whether each slide leaves an open loop. That's a
# semantic property, and a regex for it fired on 4 of 9 slides that genuinely
# had hooks. A lint that cries wolf gets ignored, which is worse than no lint.
# Open loops stay a human review item — see 02-slideshow.md design notes.


def check(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    errs, warns = [], []

    if not rows:
        return [f"{path}: empty file"], []

    cols = [c for c in rows[0].keys() if c is not None]
    if cols != COLUMNS:
        errs.append(f"columns are {cols}, expected {COLUMNS}")

    # Field drift: an unquoted comma inside a field splits it, pushing the tail
    # into DictReader's None key. The row still has all five NAMED keys, so a
    # column check alone sails straight past it — and Canva then renders a
    # truncated punch line with the tier flag as the tag. Caught this only
    # after 10 rows across 8 decks had already drifted.
    for i, r in enumerate(rows, 1):
        if None in r:
            errs.append(
                f"slide {i}: field drift — an unquoted comma split a field "
                f"(overflow: {r[None]!r}). Quote the field containing the comma."
            )

    # Save rate rises with slide count in the scrape: 4.1 per 1k saves at 1-3
    # slides, 18.7 at 4-7, 28.9 at 8-11, 33.7 at 12+. So a long deck is a target,
    # not a fault. Only flag decks too short to build the swipe habit.
    if len(rows) < 8:
        warns.append(f"{len(rows)} slides — under 8 saves poorly (see FINDINGS.md §2)")

    for i, r in enumerate(rows, 1):
        for col in cols:
            val = (r.get(col) or "").strip()
            if not val:
                # subhead is optional: render-morph.py does not read it, and it is
                # deliberately blank on most slides where the headline carries the
                # line on its own. Only the columns the renderer draws are required.
                # cover and outro carry headline + subhead + punch only
                if col == "body" and i not in (1, len(rows)):
                    errs.append(f"slide {i}: '{col}' is empty — the renderer will draw a gap")
                continue
            cap = LIMITS.get(col)
            if cap and len(val) > cap:
                errs.append(f"slide {i}: '{col}' is {len(val)} chars, over the {cap} ceiling — will overflow")
    # A bare "<" or "&" in SVG text content (from copy like "P < 0.001") makes the
    # file invalid XML. Chrome renders nothing and the slide ships with a hole in
    # it, silently. Ten shipped that way before this check existed.
    imgdir = os.path.join(os.path.dirname(path), "03-images")
    for d in [imgdir] + sorted(glob.glob(imgdir + "-*")):
        for svg in sorted(glob.glob(os.path.join(d, "*.svg"))):
            try:
                xml.dom.minidom.parse(svg)
            except Exception as e:
                errs.append(f"{os.path.relpath(svg, os.path.dirname(path))} is not valid "
                            f"XML and will render as a blank space: {e}")

    # Em dashes are banned in deck copy by house style.
    for i, r in enumerate(rows, 1):
        for col in COLUMNS:
            if "\u2014" in (r.get(col) or ""):
                errs.append(f"slide {i}: em dash in '{col}' - house style bans them")

    return errs, warns


def main():
    parser = argparse.ArgumentParser(description="Validate a slideshow CSV before it goes anywhere near Canva Bulk Create")
    parser.add_argument("paths", nargs="*", help="files or globs to act on")
    args = parser.parse_args()
    paths = []
    for arg in args.paths:
        paths.extend(glob.glob(arg))
    if not paths:
        sys.exit("usage: check-deck.py <csv> [csv ...]")

    failed = False
    for path in sorted(paths):
        errs, warns = check(path)
        status = "FAIL" if errs else ("warn" if warns else "ok")
        print(f"\n[{status}] {path}")
        for e in errs:
            print(f"   ERROR  {e}")
        for w in warns:
            print(f"   warn   {w}")
        if not errs and not warns:
            print("   all checks passed")
        failed |= bool(errs)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
