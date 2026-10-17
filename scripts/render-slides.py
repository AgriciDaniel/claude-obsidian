#!/usr/bin/env python3
"""Render a deck CSV straight to 1080x1920 PNGs. No design tool involved.

This is the full-automation path. Canva always needs hands on it: upload the
CSV, right-click each element to connect a column, drag images in. That floor
exists unless you have Enterprise autofill. Rendering directly removes it.

Per-slide images: drop files in the deck's 03-images/ named slide-01.png,
slide-02.png and so on. Any slide with a matching file gets it composited into
the image band; slides without one just close the gap.

Usage:
    python3 scripts/render-slides.py content/growth-plate-fusion
    python3 scripts/render-slides.py content/<deck> --out /tmp/preview
"""
import argparse
import csv
import html
import os
import shutil
import subprocess
import sys
import tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 1080, 1920

# Channel palette, lifted from the existing decks
CREAM = "#F2EDE4"
INK = "#111111"
BLUE = "#1A5FD0"
SURROUND = "#0D0D0D"

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ width:{W}px; height:{H}px; background:{SURROUND}; }}
  .card {{
    position:absolute; inset:44px 34px; background:{CREAM};
    border-radius:46px; padding:76px 58px 64px;
    display:flex; flex-direction:column; align-items:center; text-align:center;
    justify-content:center;
    box-shadow:0 0 90px 30px rgba(0,0,0,0.55);
  }}
  .headline {{
    font-family:'Anton',Impact,sans-serif; font-size:{hsize}px; line-height:0.94;
    color:{INK}; letter-spacing:-0.5px; text-transform:none;
  }}
  .subhead {{
    font-family:'Archivo',Helvetica,sans-serif; font-weight:700; font-size:52px;
    color:{BLUE}; letter-spacing:0.5px; margin-top:18px; line-height:1.06;
  }}
  .hgroup {{ position:absolute; top:76px; left:58px; right:58px; }}
  .gap {{ height:34px; }}
  .imgband {{ width:100%; display:flex; justify-content:center; margin:26px 0; }}
  .imgband img {{ max-width:100%; max-height:660px; border-radius:14px; }}
  .body {{
    font-family:'Archivo',Helvetica,sans-serif; font-weight:400; font-size:{bsize}px;
    line-height:1.34; color:{INK}; max-width:900px;
  }}
  .punch {{
    font-family:'Archivo',Helvetica,sans-serif; font-weight:700; font-size:{psize}px;
    line-height:1.24; color:{INK}; max-width:900px; margin-top:34px;
  }}
  .foot {{
    font-family:'Archivo',Helvetica,sans-serif; font-size:26px; color:#8C8377;
    position:absolute; bottom:52px; left:0; right:0;
  }}
</style></head><body>
<div class="card">
  <div class="hgroup">
    <div class="headline">{headline}</div>
    <div class="subhead">{subhead}</div>
  </div>
  {imgblock}
  <div class="body">{body}</div>
  <div class="punch">{punch}</div>
  <div class="foot">{handle}</div>
</div></body></html>"""


def fit(text, base, floor, per_char):
    """Shrink type as copy grows, so long slides don't overflow the card."""
    n = len(text)
    return max(floor, int(base - max(0, n - per_char) * 0.10))


def render(deck, outdir, handle):
    csv_path = os.path.join(deck, "04-slides.csv")
    if not os.path.exists(csv_path):
        sys.exit(f"no 04-slides.csv in {deck}")
    if not os.path.exists(CHROME):
        sys.exit("Google Chrome not found at the expected path")

    rows = list(csv.DictReader(open(csv_path)))
    imgdir = os.path.join(deck, "03-images")

    # CC BY images legally require attribution. Credits live in
    # 03-images/credits.txt as "slide-05: Trompet et al. 2024, CC BY 4.0" and
    # get printed in the footer of that slide.
    credits = {}
    cpath = os.path.join(imgdir, "credits.txt")
    if os.path.exists(cpath):
        for line in open(cpath):
            if ":" in line and line.strip() and not line.startswith("#"):
                k, v = line.split(":", 1)
                credits[k.strip()] = v.strip()
    os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp()

    for i, r in enumerate(rows, 1):
        img = ""
        for ext in (".png", ".jpg", ".jpeg", ".svg"):
            cand = os.path.join(imgdir, f"slide-{i:02d}{ext}")
            if os.path.exists(cand):
                img = f'<div class="imgband"><img src="file://{os.path.abspath(cand)}"></div>'
                break

        page = TEMPLATE.format(
            W=W, H=H, CREAM=CREAM, INK=INK, BLUE=BLUE, SURROUND=SURROUND,
            hsize=fit(r["headline"], 120, 74, 16),
            bsize=fit(r["body"], 46, 34, 150),
            psize=fit(r["punch"], 50, 38, 70),
            headline=html.escape(r["headline"]),
            subhead=html.escape(r["subhead"]).upper(),
            body=html.escape(r["body"]),
            punch=html.escape(r["punch"]),
            imgblock=img,
            handle=html.escape(handle + ("   ·   " + credits[f"slide-{i:02d}"]
                                         if f"slide-{i:02d}" in credits else "")))

        src = os.path.join(tmp, f"s{i:02d}.html")
        open(src, "w").write(page)
        out = os.path.join(outdir, f"slide-{i:02d}.png")
        subprocess.run([
            CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", f"--window-size={W},{H}",
            "--virtual-time-budget=4000",
            f"--screenshot={out}", f"file://{src}",
        ], capture_output=True)
        print(f"  slide-{i:02d}.png{'  [image]' if img else ''}")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(rows)} slides -> {outdir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--out")
    ap.add_argument("--handle", default="@metroraz")
    a = ap.parse_args()
    render(a.deck.rstrip("/"), a.out or os.path.join(a.deck.rstrip("/"), "07-rendered"), a.handle)


if __name__ == "__main__":
    main()
