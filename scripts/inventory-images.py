#!/usr/bin/env python3
"""Inventory an image drop folder before classification.

Does the mechanical part so the expensive part (actually looking at each image)
happens once and only on images worth looking at: dedupes by content hash,
flags images too small to use on a 1080x1920 slide, and groups by aspect.

Usage:
    python3 scripts/inventory-images.py content/_image-inbox
    python3 scripts/inventory-images.py <dir> --min-width 700
"""
import argparse
import hashlib
import os
import sys
from collections import defaultdict

try:
    import pymupdf  # reads png/jpg/webp dimensions without Pillow
except ImportError:
    sys.exit("needs pymupdf: python3 -m venv .venv && .venv/bin/pip install pymupdf")

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def digest(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while blk := fh.read(chunk):
            h.update(blk)
    return h.hexdigest()[:16]


def dims(path):
    try:
        pix = pymupdf.Pixmap(path)
        return pix.width, pix.height
    except Exception:
        return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--min-width", type=int, default=700,
                    help="below this, an image will look soft on a 1080px-wide slide")
    args = ap.parse_args()

    files = []
    for root, _, names in os.walk(args.folder):
        for n in sorted(names):
            if os.path.splitext(n)[1].lower() in EXTS:
                files.append(os.path.join(root, n))

    if not files:
        sys.exit(f"no images found under {args.folder}")

    by_hash = defaultdict(list)
    rows = []
    for p in files:
        w, h = dims(p)
        d = digest(p)
        by_hash[d].append(p)
        rows.append((p, w, h, d, os.path.getsize(p)))

    dupes = {d: ps for d, ps in by_hash.items() if len(ps) > 1}
    seen = set()
    usable, too_small, unreadable = [], [], []
    for p, w, h, d, size in rows:
        if d in seen:
            continue
        seen.add(d)
        if w is None:
            unreadable.append(p)
        elif w < args.min_width:
            too_small.append((p, w, h))
        else:
            usable.append((p, w, h, size))

    print(f"{len(files)} files, {len(seen)} unique\n")

    if dupes:
        print(f"-- duplicates ({len(dupes)} sets, {sum(len(v)-1 for v in dupes.values())} redundant)")
        for d, ps in list(dupes.items())[:10]:
            print(f"   {os.path.basename(ps[0])}")
            for extra in ps[1:]:
                print(f"      = {extra}")
        print()

    if too_small:
        print(f"-- below {args.min_width}px wide ({len(too_small)}) — will look soft on a slide")
        for p, w, h in too_small[:15]:
            print(f"   {w}x{h}  {os.path.basename(p)}")
        print()

    if unreadable:
        print(f"-- unreadable ({len(unreadable)})")
        for p in unreadable[:10]:
            print(f"   {os.path.basename(p)}")
        print()

    print(f"-- usable ({len(usable)})")
    for p, w, h, size in usable:
        ratio = w / h if h else 0
        shape = "portrait" if ratio < 0.85 else ("square" if ratio < 1.2 else "landscape")
        print(f"   {w}x{h:<6} {shape:<10} {size//1024:>5}KB  {os.path.relpath(p)}")

    print(f"\nNext: Claude reads the {len(usable)} usable images and classifies them "
          f"(subject, pathway, deck fit, licence status).")


if __name__ == "__main__":
    main()
