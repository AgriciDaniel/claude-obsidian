#!/usr/bin/env python3
"""Render decks in the style the data says wins. Replaces render-slides.py.

Built from FINDINGS.md, measured on 1,951 competitor posts:

- White ground, not the cream card. Every top performer uses white.
- Body is STACKED STATEMENTS with whitespace between, not a paragraph. Split
  the body field on " | " and each part becomes its own block.
- Key terms colour-coded inside black text, so the deck can be skimmed by
  reading only the coloured words. Mark them *blue* and **red** in the CSV.
- Section header slides supported: put SECTION in the subhead field.
- Slide 1 carries a promise and a swipe arrow, not a claim.

CSV columns: headline, subhead, body, punch
    body:  "statement one | statement two | statement three"
    marks: *term* renders blue, **term** renders red

Usage:
    python3 scripts/render-v2.py content/<deck>
    python3 scripts/render-v2.py content/<deck> --out /tmp/preview
"""
import argparse
import csv
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SIZES = {"9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080)}
W, H = SIZES["9:16"]

INK = "#141414"
BG  = "#EDEDEA"   # soft light grey, easier on the eye than pure white
BLUE = "#1B4DE4"
RED = "#E0243B"
GREY = "#8A8A8A"

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Figtree:wght@500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  html,body{{width:{W}px;height:{H}px;background:{BG};}}
  .wrap{{position:absolute;inset:0;padding:96px 62px 90px;
        display:flex;flex-direction:column;align-items:center;text-align:center;
        justify-content:{justify};}}
  .headline{{font-family:'Archivo Black',sans-serif;font-weight:400;font-size:{hsize}px;
        line-height:1.0;color:{INK};letter-spacing:-1px;}}
  .section{{font-family:'Archivo Black',sans-serif;font-weight:400;font-size:70px;
        color:{BLUE};letter-spacing:1px;margin-bottom:16px;}}
  .sub{{font-family:Figtree,sans-serif;font-weight:800;font-size:44px;
        color:{BLUE};margin-top:20px;line-height:1.1;}}
  .blocks{{margin-top:52px;display:flex;flex-direction:column;gap:44px;width:100%;}}
  .b{{font-family:Figtree,sans-serif;font-weight:600;font-size:{bsize}px;
      line-height:1.28;color:{INK};}}
  .punch{{font-family:Figtree,sans-serif;font-weight:800;font-size:{psize}px;
      line-height:1.2;color:{INK};margin-top:56px;}}
  .imgband{{margin:40px 0 10px;width:100%;display:flex;justify-content:center;}}
  .imgband img{{max-width:96%;max-height:620px;}}
  .arrow{{font-size:96px;color:{INK};margin-top:60px;font-family:Figtree,sans-serif;font-weight:800;}}
  .foot{{position:absolute;bottom:44px;left:0;right:0;
      font-weight:600;font-size:23px;color:{GREY};text-align:center;font-family:Figtree,sans-serif;}}
  em{{font-style:normal;color:{BLUE};}}
  strong{{font-weight:700;color:{RED};}}
</style></head><body>
<div class="wrap">
  {section}
  <div class="headline">{headline}</div>
  {sub}
  {imgblock}
  <div class="blocks">{blocks}</div>
  {punch}
  {arrow}
</div>
<div class="foot">{foot}</div>
</body></html>"""


def marks(s):
    """*term* -> blue, **term** -> red. Escape first so copy can't inject HTML."""
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def fit(text, base, floor, budget):
    return max(floor, int(base - max(0, len(text) - budget) * 0.085))


def render(deck, outdir, handle):
    path = os.path.join(deck, "04-slides.csv")
    if not os.path.exists(path):
        sys.exit(f"no 04-slides.csv in {deck}")
    rows = list(csv.DictReader(open(path)))
    imgdir = os.path.join(deck, "03-images")

    credits = {}
    cp = os.path.join(imgdir, "credits.txt")
    if os.path.exists(cp):
        for line in open(cp):
            if ":" in line and not line.startswith("#"):
                k, v = line.split(":", 1)
                credits[k.strip()] = v.strip()

    os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for i, r in enumerate(rows, 1):
        body = (r.get("body") or "").strip()
        parts = [p.strip() for p in body.split("|") if p.strip()]
        blocks = "".join(f'<div class="b">{marks(p)}</div>' for p in parts)

        img = ""
        for ext in (".png", ".jpg", ".jpeg", ".svg"):
            c = os.path.join(imgdir, f"slide-{i:02d}{ext}")
            if os.path.exists(c):
                img = f'<div class="imgband"><img src="file://{os.path.abspath(c)}"></div>'
                break

        sub = r.get("subhead") or ""
        is_section = sub.strip().upper().startswith("SECTION:")
        section_html = f'<div class="section">{marks(sub.split(":",1)[1].strip())}</div>' if is_section else ""
        sub_html = "" if is_section or not sub else f'<div class="sub">{marks(sub)}</div>'

        punch = (r.get("punch") or "").strip()
        punch_html = f'<div class="punch">{marks(punch)}</div>' if punch else ""
        arrow = '<div class="arrow">&#8594;</div>' if i == 1 else ""

        # handle removed by request; footer now carries only the legally
        # required image credit, and is blank when a slide has no image
        foot = credits.get(f"slide-{i:02d}", "")
        allcopy = body + punch
        page = TEMPLATE.format(
            W=W, H=H, INK=INK, BLUE=BLUE, RED=RED, GREY=GREY, BG=BG,
            justify="center" if not img else "flex-start",
            hsize=fit(r["headline"], 108, 62, 20),
            bsize=fit(allcopy, 52, 34, 210),
            psize=fit(punch, 56, 40, 80),
            headline=marks(r["headline"]), section=section_html, sub=sub_html,
            blocks=blocks, punch=punch_html, imgblock=img, arrow=arrow,
            foot=html.escape(foot))
        src = os.path.join(tmp, f"s{i:02d}.html")
        open(src, "w").write(page)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={W},{H}",
                        "--virtual-time-budget=4000",
                        f"--screenshot={os.path.join(outdir, f'slide-{i:02d}.png')}",
                        f"file://{src}"], capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  {len(rows)} slides -> {outdir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--out")
    ap.add_argument("--size", choices=list(SIZES), default="9:16",
                    help="4:5 keeps content clear of TikTok's UI overlay")
    ap.add_argument("--handle", default="@restingzone")
    a = ap.parse_args()
    global W, H
    W, H = SIZES[a.size]
    d = a.deck.rstrip("/")
    render(d, a.out or os.path.join(d, "07-rendered"), a.handle)


if __name__ == "__main__":
    main()
