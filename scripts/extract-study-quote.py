#!/usr/bin/env python3
"""Crop the exact sentence a claim rests on, and highlight it.

Better than a title screenshot: instead of "here is a paper", the slide shows
"here is the line that says it", with the line marked. It is the strongest
possible receipt because the viewer can read the evidence themselves.

Two modes:
  title   just the journal line and title, cropped tight. Small, for one slide.
  quote   find a phrase anywhere in the PDF, crop the surrounding lines, and
          draw a highlight over the phrase itself.

Usage:
    python3 scripts/extract-study-quote.py <pdf> --title out.png
    python3 scripts/extract-study-quote.py <pdf> --quote "increased by an average of 27.2%" out.png
"""
import argparse
import os
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("needs pymupdf")

HIGHLIGHT = (1, 0.84, 0.10)   # marker yellow
PAD = 14


def title_only(doc, out, dpi=460):
    """Journal line plus title, nothing else. Stops at the author line."""
    page = doc[0]
    pr = page.rect
    d = page.get_text("dict")
    spans = []
    for b in d.get("blocks", []):
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                txt = s.get("text", "").strip()
                if len(txt) > 3:
                    spans.append((s["bbox"][1], s["bbox"][3], s["size"], txt))
    if not spans:
        return False
    spans.sort()
    top_region = [s for s in spans if s[0] < pr.y0 + pr.height * 0.30]
    if not top_region:
        return False
    biggest = max(s[2] for s in top_region)
    # title lines are the ones at or near the biggest size in the top region
    title_lines = [s for s in top_region if s[2] >= biggest * 0.88]
    bottom = max(s[1] for s in title_lines) + 6
    top = max(pr.y0, min(s[0] for s in top_region) - 10)
    rect = pymupdf.Rect(pr.x0 + 18, top, pr.x1 - 18, bottom)
    page.get_pixmap(dpi=dpi, clip=rect).save(out)
    print(f"  title -> {os.path.basename(out)}")
    return True


def quote(doc, phrase, out, dpi=460, context=2):
    """Find the phrase, crop the lines around it, highlight the phrase."""
    for pno in range(doc.page_count):
        page = doc[pno]
        hits = page.search_for(phrase)
        if not hits:
            continue
        band = hits[0]
        for h in hits[1:]:
            band |= h
        # Find the column by walking outward from the hit along its own line and
        # stopping at the first gap wider than a word space. Anything else on the
        # same height (a sidebar, a caption spanning the page) is a different
        # column and must not widen the crop. That is how an author's contact
        # block once ended up on a slide.
        words = page.get_text("words")
        line_h = band.height or 12
        on_line = sorted((w for w in words if abs(w[1] - band.y0) < line_h * 0.6), key=lambda w: w[0])
        GAP = 14
        idx = [k for k, w in enumerate(on_line) if w[2] > band.x0 and w[0] < band.x1]
        lo = hi = idx[0] if idx else 0
        while lo > 0 and on_line[lo][0] - on_line[lo - 1][2] < GAP:
            lo -= 1
        while hi + 1 < len(on_line) and on_line[hi + 1][0] - on_line[hi][2] < GAP:
            hi += 1
        col_left, col_right = on_line[lo][0], on_line[hi][2]
        # the column's true right edge is the widest line in it, not this line
        ymin, ymax = band.y0 - line_h * (context + 1), band.y1 + line_h * (context + 1)
        in_col = [w for w in words if ymin < w[1] < ymax and w[0] >= col_left - 6 and w[0] < col_right]
        col_right = max([w[2] for w in in_col], default=col_right)
        left, right = col_left - PAD, col_right + PAD
        clip = pymupdf.Rect(max(page.rect.x0, left),
                            max(page.rect.y0, band.y0 - line_h * context),
                            min(page.rect.x1, right),
                            min(page.rect.y1, band.y1 + line_h * context))
        # draw the highlight before rendering
        for h in hits:
            page.draw_rect(h, color=None, fill=HIGHLIGHT, fill_opacity=0.45,
                           overlay=True)
        page.get_pixmap(dpi=dpi, clip=clip).save(out)
        print(f"  quote p{pno+1} -> {os.path.basename(out)}")
        return True
    print(f"  phrase not found: {phrase[:60]}")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--title", metavar="OUT")
    ap.add_argument("--quote", nargs=2, metavar=("PHRASE", "OUT"))
    a = ap.parse_args()
    if not os.path.exists(a.pdf):
        sys.exit(f"no such pdf: {a.pdf}")
    doc = pymupdf.open(a.pdf)
    if a.title:
        title_only(doc, a.title)
    if a.quote:
        quote(doc, a.quote[0], a.quote[1])
    if not (a.title or a.quote):
        sys.exit("use --title or --quote")


if __name__ == "__main__":
    main()
