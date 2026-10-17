#!/usr/bin/env python3
"""Same deck CSV, three different design directions, so they can be compared.

Styles:
  dark       near-black ground, off-white type, amber and cyan accents.
             Condensed heavy headline. Reads as tech / lab.
  editorial  warm paper, serif display headline, generous spacing.
             Reads as a written piece rather than a graphic.
  blocks     high contrast. Headline reversed out of a solid colour band,
             body on white. Reads as a poster.

Usage:
    python3 scripts/render-v3.py content/<deck> --style dark
    python3 scripts/render-v3.py content/<deck> --style editorial --out /tmp/x
"""
import argparse
import csv
import glob
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

STYLES = {
    "editorial": dict(
        bg="#F7F3EC", ink="#1A1815", accent="#8A3324", accent2="#3F5E4C",
        grey="#8B8378", band="#EDE6DA",
        fonts="family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;700",
        hfont="'Instrument Serif',Georgia,serif", hweight="400",
        bfont="'Inter',sans-serif", bweight="400", pweight="700",
        htransform="none", hspacing="-1px", align="left",
    ),
    "editorial-grey": dict(
        bg="#ECEDEA", ink="#16181A", accent="#1B4DE4", accent2="#B02A37",
        grey="#8A8F94", band="#E1E3DF",
        fonts="family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;700",
        hfont="'Instrument Serif',Georgia,serif", hweight="400",
        bfont="'Inter',sans-serif", bweight="400", pweight="700",
        htransform="none", hspacing="-1px", align="left",
    ),
    "editorial-centre": dict(
        bg="#EFEFEC", ink="#141414", accent="#0F5132", accent2="#8A3324",
        grey="#8A8A85", band="#E4E4E0",
        fonts="family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;700",
        hfont="'Instrument Serif',Georgia,serif", hweight="400",
        bfont="'Inter',sans-serif", bweight="500", pweight="700",
        htransform="none", hspacing="-0.5px", align="center",
    ),
    "morph": dict(
        bg="#E8E9E6", ink="#101418", accent="#1B4DE4", accent2="#D62839",
        grey="#79807E", band="#101418", hl="#FFE066",
        fonts="family=Archivo+Black&family=Archivo:wght@600;700;800",
        hfont="'Archivo Black',sans-serif", hweight="400",
        bfont="'Archivo',sans-serif", bweight="700", pweight="800",
        htransform="uppercase", hspacing="0px", align="center",
    ),
    "dark": dict(
        bg="#0E1116", ink="#F2F4F7", accent="#FFB020", accent2="#3DD6D0",
        grey="#7C8794", band="#161B22",
        fonts="family=Anton&family=Inter:wght@400;600;700",
        hfont="'Anton',sans-serif", hweight="400", bfont="'Inter',sans-serif",
        bweight="400", pweight="700", htransform="none", hspacing="0px",
        align="center",
    ),
    "blocks": dict(
        bg="#FFFFFF", ink="#101010", accent="#FF3B30", accent2="#0A84FF",
        grey="#9A9A9A", band="#101010",
        fonts="family=Anton&family=Archivo:wght@500;700;900",
        hfont="'Anton',sans-serif", hweight="400", bfont="'Archivo',sans-serif",
        bweight="500", pweight="900", htransform="uppercase", hspacing="0.5px",
        align="center",
    ),
}

# How *term* and **term** render. The winning competitor decks use colour, but
# underline and weight are worth testing since they survive greyscale and
# colourblind viewers.
EMPHASIS = {
    "colour":    ("color:{accent2};font-weight:700",              "color:{accent};font-weight:700"),
    "bold":      ("font-weight:800",                              "font-weight:800;color:{accent}"),
    "underline": ("text-decoration:underline;text-decoration-thickness:4px;text-underline-offset:6px;text-decoration-color:{accent2}",
                  "text-decoration:underline;text-decoration-thickness:5px;text-underline-offset:6px;text-decoration-color:{accent};font-weight:700"),
    "highlight": ("background:{accent2}22;padding:2px 6px;border-radius:4px;font-weight:700",
                  "background:{accent}22;padding:2px 6px;border-radius:4px;font-weight:700;color:{accent}"),
}

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<style>
 *{{margin:0;padding:0;box-sizing:border-box}}
 html,body{{width:{W}px;height:{H}px;background:{bg};}}
 .wrap{{position:absolute;inset:0;padding:{pad};display:flex;flex-direction:column;
        align-items:{align};text-align:{talign};justify-content:center;}}
 .band{{position:absolute;top:0;left:0;right:0;padding:74px 62px 56px;background:{bandbg};}}
 .headline{{font-family:{hfont};font-weight:{hweight};font-size:{hsize}px;
        line-height:{hlh};color:{hcolor};letter-spacing:{hspacing};
        text-transform:{htransform};}}
 .sub{{font-family:{bfont};font-weight:700;font-size:40px;color:{accent};
        margin-top:18px;letter-spacing:1px;}}
 .blocks{{margin-top:{btop}px;display:flex;flex-direction:column;gap:{bgap}px;width:100%;}}
 .b{{font-family:{bfont};font-weight:{bweight};font-size:{bsize}px;
     line-height:1.42;color:{ink};}}
 .punch{{font-family:{bfont};font-weight:{pweight};font-size:{psize}px;
     line-height:1.24;color:{ink};margin-top:54px;}}
 .rule{{width:120px;height:5px;background:{accent};margin:36px 0 0;}}
 .imgband{{margin:34px 0 6px;width:100%;display:flex;justify-content:{align};}}
 .imgband img{{max-width:96%;max-height:600px;}}
 .imgband.study img{{max-height:420px;border:2px solid {grey}55;background:#fff;padding:10px;}}
 .studylabel{{font-family:{bfont};font-weight:800;font-size:30px;color:{accent};
     letter-spacing:3px;margin-top:30px;}}
 .arrow{{font-family:{bfont};font-size:82px;font-weight:700;color:{accent};margin-top:52px;}}
 .foot{{position:absolute;bottom:44px;left:62px;right:62px;font-family:{bfont};
     font-weight:400;font-size:22px;color:{grey};text-align:{talign};}}
 em{{font-style:normal;color:{accent};font-weight:700;}}
 strong{{color:{accent2};font-weight:800;}}
 u{{text-decoration:underline;text-decoration-thickness:4px;
    text-underline-offset:7px;text-decoration-color:{accent};}}
 mark{{background:{hl};color:inherit;padding:3px 10px;border-radius:5px;}}
</style></head><body>
{bandhtml}
<div class="wrap">
 {headhtml}
 {imgblock}
 <div class="blocks">{blocks}</div>
 {punch}
 {arrow}
</div>
<div class="foot">{foot}</div>
</body></html>"""


def marks(s):
    """Four markers, each carrying a different meaning so the reader learns
    what a treatment signals rather than seeing decoration:

      *term*        blue      a mechanism, receptor, gene or enzyme
      **number**    red bold  a figure or a hard finding
      _phrase_      underline the conclusion of the slide
      ==phrase==    highlight the thing to remember
    """
    s = html.escape(s)
    s = re.sub(r"==(.+?)==", r'<mark>\1</mark>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"_(.+?)_", r"<u>\1</u>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def fit(t, base, floor, budget):
    """Shrink for long copy, then scale to the canvas.

    4:5 is 1350px tall against 9:16's 1920. Without the height scale the same
    type ran off the bottom of the shorter canvas, which is what was cropping
    content."""
    size = base - max(0, len(t) - budget) * 0.085
    return max(int(floor * (H / 1920) ** 0.5), int(size * (H / 1920) ** 0.62))


def render(deck, style, outdir, emphasis="colour", images="mixed"):
    render._receipts = 0
    S = STYLES[style]
    rows = list(csv.DictReader(open(os.path.join(deck, "04-slides.csv"))))
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
        parts = [p.strip() for p in (r.get("body") or "").split("|") if p.strip()]
        blocks = "".join(f'<div class="b">{marks(p)}</div>' for p in parts)
        img = ""
        if images != "none":
            for ext in (".svg", ".png", ".jpg"):
                c = os.path.join(imgdir, f"slide-{i:02d}{ext}")
                if os.path.exists(c):
                    img = f'<div class="imgband"><img src="file://{os.path.abspath(c)}"></div>'
                    break
            # 'many' fills the gaps with study receipts: a screenshot of the
            # actual paper header, which is the device the top competitor deck
            # uses instead of a citation line
            # 'mixed' is the default blend: generated diagrams carry the
            # mechanism, real figures carry the evidence, and a small number of
            # study receipts carry the proof. Receipts are capped at 2 so they
            # stay a punctuation mark rather than the texture of the deck.
            if not img and images == "mixed":
                pool = sorted(glob.glob(os.path.join(imgdir, "studies", "*.png")))
                used = getattr(render, "_receipts", 0)
                if pool and used < 2 and i in (max(2, len(rows) // 3), len(rows) - 3):
                    pick = pool[used % len(pool)]
                    render._receipts = used + 1
                    img = ('<div class="studylabel">THE STUDY</div>'
                           f'<div class="imgband study"><img src="file://{os.path.abspath(pick)}"></div>')
            if not img and images == "many":
                pool = sorted(glob.glob(os.path.join(imgdir, "studies", "*.png")))
                if pool and 1 < i < len(rows):
                    pick = pool[(i - 2) % len(pool)]
                    img = ('<div class="studylabel">STUDY</div>'
                           f'<div class="imgband study"><img src="file://{os.path.abspath(pick)}"></div>')
        sub = (r.get("subhead") or "").strip()
        if sub.upper().startswith("SECTION:"):
            sub = sub.split(":", 1)[1].strip()
        punch = (r.get("punch") or "").strip()
        hsize = fit(r["headline"], 122 if style.startswith("editorial") else 112, 64, 20)

        head = (f'<div class="headline">{marks(r["headline"])}</div>'
                + (f'<div class="sub">{marks(sub.upper())}</div>' if sub else "")
                + ('<div class="rule"></div>' if style.startswith("editorial") else ""))
        # blocks style puts the headline in a solid band at the top
        bandhtml = f'<div class="band">{head}</div>' if style == "blocks" else ""
        headhtml = "" if style == "blocks" else head

        page = TPL.format(
            W=W, H=H, fonts=S["fonts"], bg=S["bg"], ink=S["ink"], accent=S["accent"],
            accent2=S["accent2"], grey=S["grey"],
            bandbg=S["band"], hcolor=S["bg"] if style == "blocks" else S["ink"],
            hfont=S["hfont"], hweight=S["hweight"], bfont=S["bfont"],
            bweight=S["bweight"], pweight=S["pweight"],
            htransform=S["htransform"], hspacing=S["hspacing"],
            hlh="1.04" if style.startswith("editorial") else "0.98",
            pad="330px 62px 100px" if style == "blocks" else "96px 62px 92px",
            align="flex-start" if S["align"] == "left" else "center",
            talign=S["align"],
            btop=46 if style != "blocks" else 20, bgap=40,
            hsize=hsize, bsize=fit("".join(parts) + punch, 50, 34, 210),
            psize=fit(punch, 54, 38, 80),
            headhtml=headhtml, bandhtml=bandhtml, blocks=blocks,
            punch=f'<div class="punch">{marks(punch)}</div>' if punch else "",
            imgblock=img,
            arrow='<div class="arrow">&#8594;</div>' if i == 1 else "",
            hl=S.get("hl","#FFE58A"),
            foot=html.escape(credits.get(f"slide-{i:02d}", "")))
        src = os.path.join(tmp, f"s{i:02d}.html")
        open(src, "w").write(page)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={W},{H}",
                        "--virtual-time-budget=4500",
                        f"--screenshot={os.path.join(outdir, f'slide-{i:02d}.png')}",
                        f"file://{src}"], capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  [{style}] {len(rows)} slides -> {outdir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--style", choices=list(STYLES), required=True)
    ap.add_argument("--emphasis", choices=list(EMPHASIS), default="colour")
    ap.add_argument("--images", choices=["none","few","mixed","many"], default="mixed")
    ap.add_argument("--out")
    ap.add_argument("--size", choices=list(SIZES), default="9:16",
                    help="4:5 keeps content clear of TikTok's UI overlay")
    a = ap.parse_args()
    global W, H
    W, H = SIZES[a.size]
    d = a.deck.rstrip("/")
    render(d, a.style, a.out or os.path.join(d, f"08-{a.style}"), a.emphasis, a.images)


if __name__ == "__main__":
    main()
