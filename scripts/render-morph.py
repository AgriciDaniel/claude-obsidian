#!/usr/bin/env python3
"""A close copy of the doctor.morph slide design.

Built by reading his actual slides. His deck is the second highest performing
slideshow in the scrape, so this is worth copying precisely rather than
approximating.

What his design does, element by element:
  - pale blue-grey ground with a soft cloudy wash, not a flat fill
  - letterspaced brand line in caps at the very top
  - headline in heavy geometric caps with a black-to-blue gradient and a soft
    drop shadow
  - body in bold geometric sans, black, with individual terms in red or blue
  - a thin double-rule ornament with a diamond, separating head from body
  - 960x1280 (3:4), which is his actual canvas

Markers, same as render-v3:
  *term*   blue      **term**  red      _phrase_  underline   ==phrase==  highlight

Usage:
    python3 scripts/render-morph.py content/<deck>
    python3 scripts/render-morph.py content/<deck> --tone darker --brand "YOURNAME"
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
SIZES = {"3:4": (960, 1280), "4:5": (1080, 1350), "9:16": (1080, 1920)}

# Palettes. Same structure as the reference design, different colour worlds, so
# the layout carries over without the look being a copy.
#   bg/w2/w3   ground and the two radial washes
#   ink        body text
#   grad       headline gradient stops
#   acc        mechanism terms
#   acc2       numbers and hard claims
#   hl         highlight background
#   brand      brand line and divider
#   shadow     headline drop shadow
PALETTES = {
    "slate": dict(bg="#D2DAE0", w2="#BFCBD4", w3="#DBE2E7", ink="#0A0C10",
                  grad=("#080A14", "#1B2AA8", "#2438E8"), acc="#2438E8",
                  acc2="#E23A2E", hl="#FFD84D", brand="#12183A",
                  shadow="rgba(20,30,80,0.30)"),
    "forest": dict(bg="#E7EDE4", w2="#D3DFCD", w3="#F1F5EE", ink="#0C140E",
                   grad=("#08140C", "#175E38", "#1F9D55"), acc="#177245",
                   acc2="#C2410C", hl="#FDE68A", brand="#0F2E1C",
                   shadow="rgba(15,60,35,0.28)"),
    "ember": dict(bg="#F2E7DC", w2="#E7D5C3", w3="#FAF2EA", ink="#17100A",
                  grad=("#1A0F06", "#9A3412", "#EA580C"), acc="#B45309",
                  acc2="#B91C1C", hl="#FFE08A", brand="#3B1D0B",
                  shadow="rgba(90,40,10,0.26)"),
    "violet": dict(bg="#E8E5F2", w2="#D7D2E9", w3="#F2F0F8", ink="#100C18",
                   grad=("#0D0818", "#5B21B6", "#8B5CF6"), acc="#6D28D9",
                   acc2="#DB2777", hl="#FDE68A", brand="#2A1B4A",
                   shadow="rgba(60,30,120,0.28)"),
    "midnight": dict(bg="#101720", w2="#16202C", w3="#0C1219", ink="#EEF3F8",
                     grad=("#FFFFFF", "#8FD3FF", "#38BDF8"), acc="#5EEAD4",
                     acc2="#FCA5A5", hl="#3F3F1E", brand="#8FA6BC",
                     shadow="rgba(0,0,0,0.55)"),
    "carbon": dict(bg="#15161A", w2="#1D1F25", w3="#101114", ink="#F2F2F0",
                   grad=("#FFFFFF", "#FFC46B", "#FF9F1C"), acc="#FFB020",
                   acc2="#FF6B6B", hl="#4A3A12", brand="#9A9A96",
                   shadow="rgba(0,0,0,0.6)"),
    "deepgreen": dict(bg="#0E1A14", w2="#14251C", w3="#0A140F", ink="#EAF3ED",
                      grad=("#FFFFFF", "#7EE6A8", "#34D399"), acc="#34D399",
                      acc2="#FCA5A5", hl="#2C3A1C", brand="#7FA891",
                      shadow="rgba(0,0,0,0.55)"),
    "paper": dict(bg="#EDEAE3", w2="#E1DCD1", w3="#F6F4EF", ink="#14120E",
                  grad=("#12100C", "#3F5E4C", "#5C8A6E"), acc="#3F5E4C",
                  acc2="#9A3324", hl="#F2D680", brand="#2A2620",
                  shadow="rgba(40,35,25,0.22)"),
}

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
 *{{margin:0;padding:0;box-sizing:border-box}}
 html,body{{width:{W}px;height:{H}px;}}
 body{{background:
    radial-gradient(120% 80% at 78% 8%, {wash2} 0%, transparent 55%),
    radial-gradient(100% 70% at 12% 92%, {wash3} 0%, transparent 60%),
    {bg};}}
 .wrap{{position:absolute;inset:0;padding:{padtop}px 46px 54px;
        display:flex;flex-direction:column;align-items:center;text-align:center;}}
 .body{{flex:1;display:flex;flex-direction:column;align-items:center;
        justify-content:center;width:100%;}}
 /* Slide 1 carries one short hook. Letting .body eat the leftover height strands
    it halfway down the frame, so the cover centres headline and hook together. */
 .wrap.cover{{justify-content:center;}}
 .wrap.cover .body{{flex:0 0 auto;}}
 .wrap.cover .blocks{{margin-top:{covtop}px;}}
 .brand{{font-family:Poppins,sans-serif;font-weight:800;font-size:{brandsize}px;
        letter-spacing:{brandls}px;color:{brand};margin-bottom:{brandgap}px;}}
 .headline{{font-family:Poppins,sans-serif;font-weight:900;font-size:{hsize}px;
        line-height:1.02;letter-spacing:-0.5px;text-transform:uppercase;
        background:linear-gradient(96deg,{g0} 12%,{g1} 58%,{g2} 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        filter:drop-shadow(0 5px 7px {shadow});}}
 .divider{{width:76%;margin:{divgap}px auto 0;display:flex;align-items:center;
        justify-content:center;gap:12px;}}
 .divider .ln{{flex:1;height:3px;background:linear-gradient(90deg,transparent,{brand} 35%,{brand} 65%,transparent);}}
 .divider .dot{{width:16px;height:16px;background:{brand};transform:rotate(45deg);}}
 .blocks{{margin-top:{btop}px;display:flex;flex-direction:column;gap:{bgap}px;width:100%;}}
 .b{{font-family:Poppins,sans-serif;font-weight:700;font-size:{bsize}px;
     line-height:1.30;color:{ink};}}
 .punch{{font-family:Poppins,sans-serif;font-weight:900;font-size:{psize}px;
     line-height:1.24;color:{ink};margin-top:{pgap}px;}}
 .imgband{{margin:{igap}px 0 4px;width:100%;display:flex;justify-content:center;}}
 .imgband img{{max-width:98%;max-height:{imax}px;}}
 .imgband.study img{{background:#fff;padding:12px;border:2px solid {brand}33;max-height:{smax}px;}}
 .studylabel{{font-family:Poppins,sans-serif;font-weight:900;font-size:{slsize}px;
     color:{acc};letter-spacing:4px;margin-top:26px;}}
 .arrow{{font-family:Poppins,sans-serif;font-size:{arrowsize}px;font-weight:800;
     color:{acc};margin-top:34px;}}
 .foot{{position:absolute;bottom:26px;left:46px;right:46px;font-family:Poppins,sans-serif;
     font-weight:600;font-size:{footsize}px;color:{brand};opacity:.75;text-align:center;}}
 em{{font-style:normal;color:{acc};}}
 strong{{color:{acc2};font-weight:800;}}
 u{{text-decoration:underline;text-decoration-thickness:4px;text-underline-offset:6px;
    text-decoration-color:{acc};}}
 mark{{background:{hl};color:inherit;padding:2px 9px;border-radius:4px;}}
</style></head><body>
<div class="wrap {covercls}">
 <div class="brand">{brandtext}</div>
 <div class="headline">{headline}</div>
 <div class="divider"><div class="ln"></div><div class="dot"></div><div class="ln"></div></div>
 <div class="body">
  {imgblock}
  <div class="blocks">{blocks}</div>
  {punch}
  {arrow}
 </div>
</div>
<div class="foot">{foot}</div>
</body></html>"""


def marks(s):
    s = html.escape(s)
    s = re.sub(r"==(.+?)==", r"<mark>\1</mark>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"_(.+?)_", r"<u>\1</u>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--size", choices=list(SIZES), default="3:4")
    ap.add_argument("--palette", choices=list(PALETTES), default="slate")
    ap.add_argument("--brand", default="RESTINGZONE")
    ap.add_argument("--images", choices=["none", "few", "mixed", "many"], default="mixed")
    ap.add_argument("--out")
    a = ap.parse_args()

    deck = a.deck.rstrip("/")
    W, H = SIZES[a.size]
    P = PALETTES[a.palette]
    k = H / 1280.0                      # everything scales off his canvas height

    rows = list(csv.DictReader(open(os.path.join(deck, "04-slides.csv"))))
    imgdir = os.path.join(deck, "03-images")
    credits = {}
    cp = os.path.join(imgdir, "credits.txt")
    if os.path.exists(cp):
        for line in open(cp):
            if ":" in line and not line.startswith("#"):
                kk, v = line.split(":", 1)
                credits[kk.strip()] = v.strip()

    outdir = a.out or os.path.join(deck, f"09-{a.palette}")
    os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    receipts = 0

    for i, r in enumerate(rows, 1):
        parts = [p.strip() for p in (r.get("body") or "").split("|") if p.strip()]
        blocks = "".join(f'<div class="b">{marks(p)}</div>' for p in parts)
        punch = (r.get("punch") or "").strip()

        img = ""
        if a.images != "none":
            for ext in (".svg", ".png", ".jpg"):
                c = os.path.join(imgdir, f"slide-{i:02d}{ext}")
                if os.path.exists(c):
                    img = f'<div class="imgband"><img src="file://{os.path.abspath(c)}"></div>'
                    break
            if not img and a.images in ("mixed", "many"):
                pool = sorted(glob.glob(os.path.join(imgdir, "studies", "*.png")))
                # one receipt per deck. Repeating the same screenshot across slides
                # reads as padding rather than evidence.
                cap = 1
                if pool and receipts < cap and 1 < i < len(rows):
                    img = ('<div class="studylabel">THE STUDY</div>'
                           f'<div class="imgband study"><img src="file://'
                           f'{os.path.abspath(pool[receipts % len(pool)])}"></div>')
                    receipts += 1

        body_len = len("".join(parts)) + len(punch)
        page = TPL.format(
            W=W, H=H, bg=P['bg'], wash2=P['w2'], wash3=P['w3'],
            ink=P['ink'], acc=P['acc'], acc2=P['acc2'], hl=P['hl'],
            brand=P['brand'], shadow=P['shadow'],
            g0=P['grad'][0], g1=P['grad'][1], g2=P['grad'][2],
            brandtext=html.escape(a.brand), headline=marks(r["headline"]),
            blocks=blocks,
            punch=f'<div class="punch">{marks(punch)}</div>' if punch else "",
            imgblock=img, covercls="cover" if i == 1 else "",
            covtop=int(46 * k),
            arrow='<div class="arrow">&#10148;</div>' if i == 1 else "",
            foot=html.escape(credits.get(f"slide-{i:02d}", "")),
            padtop=int(30 * k), brandsize=int(30 * k), brandls=int(7 * k),
            brandgap=int(12 * k), divgap=int(20 * k), btop=int(30 * k),
            bgap=int(26 * k), pgap=int(34 * k), igap=int(26 * k),
            imax=int(430 * k), smax=int(210 * k), slsize=int(24 * k),
            arrowsize=int(60 * k), footsize=int(19 * k),
            hsize=max(int(40 * k), int((78 - max(0, len(r["headline"]) - 16) * 1.5) * k)),
            bsize=max(int(24 * k), int((40 - max(0, body_len - 150) * 0.030) * k)),
            psize=max(int(26 * k), int((44 - max(0, len(punch) - 60) * 0.055) * k)))

        src = os.path.join(tmp, f"s{i:02d}.html")
        open(src, "w").write(page)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={W},{H}",
                        "--virtual-time-budget=4500",
                        f"--screenshot={os.path.join(outdir, f'slide-{i:02d}.png')}",
                        f"file://{src}"], capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  {len(rows)} slides -> {outdir}  ({a.size}, {a.palette})")


if __name__ == "__main__":
    main()
