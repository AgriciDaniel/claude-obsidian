#!/usr/bin/env python3
"""Crop the title block out of a paper so a slide can show the receipt.

doctor.morph's best-performing deck puts "STUDY" with an arrow pointing at a
screenshot of the actual journal header. It is proof as an image rather than a
citation line in small text, and it is the device most worth stealing.

This finds the title block on page 1 by locating the largest text on the page
and cropping from there down through the author line.

Usage:
    python3 scripts/extract-study-headers.py "<pdf path>" out.png
    python3 scripts/extract-study-headers.py --deck content/<deck>
        reads that deck's 06-sources.md and pulls a header for each paper
"""
import argparse
import os
import re
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("needs pymupdf")


def header_rect(page):
    """Top band of page 1: journal line, title, authors, affiliation.

    An earlier version looked for the largest text span and anchored to it.
    That broke on any paper with a drop cap, because a single huge letter beats
    the title on font size. Cropping a fixed top band is dumber and works.

    The band ends just above the abstract or the first body column, found by
    looking for the first wide run of small text.
    """
    pr = page.rect
    d = page.get_text("dict")
    cutoff = pr.y0 + pr.height * 0.32
    sizes = []
    for b in d.get("blocks", []):
        for l in b.get("lines", []):
            for sp in l.get("spans", []):
                if len(sp.get("text", "").strip()) > 20:
                    sizes.append((sp["bbox"][1], sp["size"]))
    if sizes:
        sizes.sort()
        body = sorted(sz for _, sz in sizes)[len(sizes) // 2]
        # first long line at body size, below the top 8%, ends the header
        for y, sz in sizes:
            if sz <= body * 1.05 and y > pr.y0 + pr.height * 0.10:
                cutoff = min(cutoff, y - 6)
                break
    return pymupdf.Rect(pr.x0 + 20, pr.y0 + 8, pr.x1 - 20,
                        max(cutoff, pr.y0 + pr.height * 0.12))


def grab(pdf, out, dpi=500):
    d = pymupdf.open(pdf)
    r = header_rect(d[0])
    if r is None:
        print(f"  no title block found: {os.path.basename(pdf)}")
        return False
    pix = d[0].get_pixmap(dpi=dpi, clip=r)
    pix.save(out)
    print(f"  {os.path.basename(out)}  {pix.width}x{pix.height}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--deck", help="read 06-sources.md and grab every paper")
    a = ap.parse_args()

    if a.deck:
        src = os.path.join(a.deck, "06-sources.md")
        if not os.path.exists(src):
            sys.exit(f"no 06-sources.md in {a.deck}")
        outdir = os.path.join(a.deck, "03-images", "studies")
        os.makedirs(outdir, exist_ok=True)
        paths = re.findall(r"`(\.raw/Studies/[^`]+\.pdf)`", open(src).read())
        if not paths:
            sys.exit("no PDF paths found in 06-sources.md")
        for i, p in enumerate(dict.fromkeys(paths), 1):
            if os.path.exists(p):
                grab(p, os.path.join(outdir, f"study-{i:02d}.png"))
            else:
                print(f"  missing: {p}")
        return

    if not (a.pdf and a.out):
        sys.exit("give a pdf and an output path, or use --deck")
    grab(a.pdf, a.out)


if __name__ == "__main__":
    main()
