#!/usr/bin/env python3
"""Render a deck in the original restingzone look: grey ground, black condensed
headline, blue caps subhead, plain body, one image band, bold punch.

Measured from the Canva exports in the first decks:
  ground #D9D9D9, headline Anton black, subhead Montserrat 800 #004AAD caps,
  body Poppins, emphasis bold + underline, light-blue #9ACEE8 for arrows and
  highlights. Image sits in a white card in the middle of the slide.

Same 04-slides.csv, same markers, same 03-images/ as render-morph.py, so a deck
renders in either style with no changes. Unlike morph this style USES the
subhead column: headline + subhead together are the sentence.

Images per slide, all optional, in 03-images/:
  slide-NN.{svg,png,jpg}         one image
  slide-NN-a.png + slide-NN-b.png  two, side by side
  studies/*.png                  one receipt per deck, placed on the first slide
                                 with no image of its own (after slide 1)
  credits.txt                    slide-NN: caption under the image

Usage:
    python3 scripts/render-classic.py content/<deck> [--size 3:4|4:5|orig] [--out DIR]
"""
import argparse, csv, glob, html, os, re, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from claude_obsidian.paths import VaultSelectionError, resolve_vault_root


def vault_root() -> Path:
    """Resolve the vault to act on, failing closed when there is none.

    Never derive paths from __file__: under the installed product tree that
    resolves to the plugin directory, and writing there corrupts the install.
    """
    return resolve_vault_root(plugin_root=PLUGIN_ROOT).root

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTRO = os.path.join(HERE, "..", "content", "_STYLES", "03-classic-assets", "outro-boxer.png")
STYLES = {
    # A. the original. grey ground, black Anton, blue caps subhead, plain body
    "classic":  dict(bg="#D9D9D9", ink="#000", body="#111", sub="#004AAD", kw="#111", num="#111",
                     hl="#9ACEE8", card="#fff", hfont="Anton,Impact,sans-serif", outline=False, label=False),
    # B. classic + doctor.morph keywords: blue mechanisms, red numbers, STUDY label + arrow
    "keyword":  dict(bg="#D9D9D9", ink="#000", body="#111", sub="#004AAD", kw="#1B4DE4", num="#D42B2B",
                     hl="#FFE066", card="#fff", hfont="Anton,Impact,sans-serif", outline=False, label=True),
    # C. rpo3212 move: heavy rounded type with a white outline stroke, less body, big punch
    "outline":  dict(bg="#D9D9D9", ink="#000", body="#111", sub="#004AAD", kw="#1B4DE4", num="#D42B2B",
                     hl="#9ACEE8", card="#fff", hfont="'Baloo 2',Poppins,sans-serif", outline=True, label=False),
    # D. _sox9 move: the same format on a dark ground
    "dark":     dict(bg="#1C1C1E", ink="#F5F5F5", body="#E6E6E6", sub="#7FB3FF", kw="#7FB3FF", num="#FF6B6B",
                     hl="#1F3A6E", card="#fff", hfont="Anton,Impact,sans-serif", outline=False, label=True),
    # F. ORCA. Compound monographs for the second account. Near-black ground,
    #    white type, ice accent. Section tags in the subhead are colour-coded:
    #    BENEFIT green, DOWNSIDE red, COUNTER ice, LIMIT amber.
    "orca":     dict(bg="#0B0E13", ink="#FFFFFF", body="#D7DDE4", sub="#3BC9DB", kw="#3BC9DB", num="#FF6B6B",
                     hl="#14506B", card="#fff", hfont="Anton,Impact,sans-serif", outline=False, label=True),
    # G. CLINICAL. White package-insert look. Black type, one red rule accent.
    "clinical": dict(bg="#FFFFFF", ink="#111111", body="#1A1A1A", sub="#C1121F", kw="#0A58CA", num="#C1121F",
                     hl="#FFE8A3", card="#F7F7F5", hfont="'Archivo',Helvetica,sans-serif", outline=False, label=True),
    # H. DOSSIER. Warm paper, serif headline, ink-blue accent. Printed-reference feel.
    "dossier":  dict(bg="#F2EDE3", ink="#1C1A17", body="#2A2724", sub="#1D4E6B", kw="#1D4E6B", num="#A63D2F",
                     hl="#E8D9A8", card="#FFFFFF", hfont="'Playfair Display',Georgia,serif", outline=False, label=True),
    # I. SIGNAL. Light cool grey, heavy condensed headline, electric accent.
    "signal":   dict(bg="#E9ECEF", ink="#0D1117", body="#1C2128", sub="#0066FF", kw="#0066FF", num="#D00000",
                     hl="#FFD60A", card="#FFFFFF", hfont="Anton,Impact,sans-serif", outline=False, label=True),
    # E. warm paper, red subhead, yellow highlighter. doctor.morph's ground with your layout
    "paper":    dict(bg="#EFEAE0", ink="#111", body="#1A1A1A", sub="#B8332A", kw="#1B4DE4", num="#B8332A",
                     hl="#FFE066", card="#fff", hfont="Anton,Impact,sans-serif", outline=False, label=True),
}
SIZES = {"3:4": (1080, 1440), "4:5": (1080, 1350), "orig": (1080, 1536), "9:16": (1080, 1920)}

TPL = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@700;800&family=Playfair+Display:wght@700;800&family=Montserrat:wght@700;800&family=Poppins:wght@400;600;700&family=Baloo+2:wght@800&display=swap" rel="stylesheet">
<style>
 *{{margin:0;padding:0;box-sizing:border-box}}
 html,body{{width:{W}px;height:{H}px;}}
 body{{background:{bg};}}
 .wrap{{position:absolute;inset:0;padding:{padtop}px 96px {padbot}px 72px;display:flex;
        flex-direction:column;align-items:center;justify-content:center;text-align:center;}}
 .headline{{font-family:{hfont};font-size:{hsize}px;line-height:0.98;white-space:nowrap;max-width:100%;
        color:{ink};letter-spacing:-0.5px;{hextra}}}
 .subhead.benefit{{color:#51CF66;}}
 .subhead.downside{{color:#FF6B6B;}}
 .subhead.counter{{color:#3BC9DB;}}
 .subhead.limit{{color:#FFC078;}}
 .spec{{font-family:Poppins,sans-serif;font-weight:700;font-size:{specsize}px;letter-spacing:2px;
        color:{sub};opacity:.85;margin-bottom:{specgap}px;text-transform:uppercase;}}
 .subhead{{font-family:Montserrat,sans-serif;font-weight:800;font-size:{ssize}px;
        line-height:1.15;color:{sub};text-transform:uppercase;letter-spacing:0.5px;
        margin-top:{sgap}px;}}
 .body{{flex:0 1 auto;display:flex;flex-direction:column;align-items:center;
        justify-content:center;width:100%;gap:{bgap}px;margin-top:{bgap}px;}}
 .wrap.cover{{justify-content:center;}}
 .wrap.cover .body{{flex:0 0 auto;margin-top:{bgap}px;}}
 .wrap.cover .headline{{font-size:{hcover}px;}}
 .wrap.cover .punch{{font-size:{pcover}px;margin-top:10px;}}
 .wrap.cover .subhead{{font-size:{scover}px;margin-top:14px;}}
 .blocks{{display:flex;flex-direction:column;gap:{lgap}px;width:100%;}}
 .b{{font-family:Poppins,sans-serif;font-weight:400;font-size:{bsize}px;line-height:1.42;color:{body};}}
 .imgband{{display:flex;justify-content:center;align-items:center;gap:18px;width:100%;}}
 .imgband img{{max-width:100%;max-height:{imax}px;background:{card};border:1px solid #cfcfcf;}}
 .label{{font-family:Poppins,sans-serif;font-weight:700;font-size:{lsize}px;color:{sub};letter-spacing:2px;}}
 .label svg{{vertical-align:middle;margin-left:8px;}}
 .imgband.two img{{max-width:48%;}}
 .imgband.study img{{max-height:{smax}px;padding:8px;}}
 .cap{{font-family:Poppins,sans-serif;font-size:{csize}px;color:{body};opacity:.6;margin-top:-{lgap}px;}}
 .punch{{font-family:Poppins,sans-serif;font-weight:700;font-size:{psize}px;line-height:1.3;color:{ink};}}
 strong{{font-weight:700;color:{num};}}
 em{{font-style:normal;font-weight:700;color:{kw};}}
 u{{font-weight:700;text-decoration:underline;text-decoration-thickness:3px;text-underline-offset:4px;}}
 mark{{background:{hl};color:inherit;padding:0 6px;border-radius:3px;}}
</style></head><body>
<div class="wrap {cover}">
 {spec}
 <div class="headline">{headline}</div>
 {subhead}
 <div class="body">
  {blocks}
  {imgblock}
  {punch}
 </div>
</div>
<script>
(function(){{
const fit=()=>{{
  const px=(el)=>parseFloat(getComputedStyle(el).fontSize);
  const wrap=document.querySelector('.wrap');
  const h=document.querySelector('.headline');
  // 1. headline on one line, shrink until it fits the padded width
  let fs=px(h);
  // on the cover the headline is the whole slide: grow it to ~90% of the column first
  if(wrap.classList.contains('cover')){{
    const target=h.clientWidth*0.96;
    while(h.scrollWidth<target && fs<190){{fs+=2;h.style.fontSize=fs+'px';}}
  }}
  while(h.scrollWidth>h.clientWidth+1 && fs>30){{fs-=2;h.style.fontSize=fs+'px';}}
  // 2. subhead may wrap to two lines at most
  const sub=document.querySelector('.subhead');
  if(sub){{let ss=px(sub);const lh=parseFloat(getComputedStyle(sub).lineHeight);
    while(sub.getBoundingClientRect().height>lh*2.2 && ss>20){{ss-=1;sub.style.fontSize=ss+'px';}}}}
  // 3. If the column overflows, shrink the COPY first and only squeeze the image
  //    once the copy has hit its floor. A dense slide used to starve its diagram
  //    down to a postage stamp because the image yielded first.
  const body=[...document.querySelectorAll('.b')], punch=document.querySelector('.punch'),
        img=document.querySelector('.imgband img');
  const MINCOPY=19, MINIMG=wrap.clientHeight*0.30;
  let guard=0;
  while(wrap.scrollHeight>wrap.clientHeight+1 && guard++<120){{
    const copyFloor = body.every(b=>px(b)<=MINCOPY) && (!punch||px(punch)<=MINCOPY+4);
    if(!copyFloor){{
      body.forEach(b=>{{ if(px(b)>MINCOPY) b.style.fontSize=(px(b)-0.6)+'px'; }});
      if(punch && px(punch)>MINCOPY+4) punch.style.fontSize=(px(punch)-0.6)+'px';
    }} else if(img){{
      const mh=parseFloat(getComputedStyle(img).maxHeight);
      if(mh<=MINIMG) break;
      img.style.maxHeight=Math.max(MINIMG,mh*0.97)+'px';
    }} else break;
  }}
  document.documentElement.setAttribute('data-fitted','1');
}};
if(document.fonts&&document.fonts.ready){{document.fonts.ready.then(fit);}}else{{fit();}}
}})();
</script>
</body></html>"""


def marks(s):
    s = html.escape(s)
    s = re.sub(r"==(.+?)==", r"<mark>\1</mark>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"_(.+?)_", r"<u>\1</u>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


SECTIONS = {"BENEFIT": "benefit", "EVIDENCE FOR": "benefit",
            "DOWNSIDE": "downside", "RISK": "downside", "THE COST": "downside",
            "COUNTER": "counter", "MITIGATION": "counter", "HOW TO COUNTER": "counter",
            "LIMIT": "limit", "UNKNOWN": "limit", "WHAT WE DO NOT KNOW": "limit"}


def secclass(sub):
    """Colour-code the subhead when it opens with a monograph section tag."""
    u = sub.upper()
    for k, v in SECTIONS.items():
        if u.startswith(k):
            return v
    return ""


def find_img(imgdir, i, suffix=""):
    for ext in (".svg", ".png", ".jpg", ".jpeg"):
        c = os.path.join(imgdir, f"slide-{i:02d}{suffix}{ext}")
        if os.path.exists(c):
            return os.path.abspath(c)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--size", default="3:4", choices=SIZES)
    ap.add_argument("--out")
    ap.add_argument("--style", default="classic", choices=STYLES)
    ap.add_argument("--images", default="03-images", help="image folder inside the deck")
    ap.add_argument("--no-outro", action="store_true", help="skip the boxer on the last slide")
    a = ap.parse_args()
    deck = a.deck.rstrip("/")
    W, H = SIZES[a.size]
    st = STYLES[a.style]
    k = (H / 1536) ** 0.7

    rows = list(csv.DictReader(open(os.path.join(deck, "04-slides.csv"))))
    imgdir = os.path.join(deck, a.images)
    credits = {}
    cp = os.path.join(imgdir, "credits.txt")
    if os.path.exists(cp):
        for line in open(cp):
            if ":" in line and not line.startswith("#"):
                kk, v = line.split(":", 1)
                credits[kk.strip()] = v.strip()
    specfile = os.path.join(deck, "00-spec.txt")
    spec = open(specfile).read().strip() if os.path.exists(specfile) else ""
    pool = sorted(glob.glob(os.path.join(imgdir, "studies", "*.png")))
    receipts = 0

    outdir = a.out or os.path.join(deck, f"09-{a.style}" + ("" if a.images == "03-images" else "-" + a.images.split("-")[-1]))
    os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp()

    for i, r in enumerate(rows, 1):
        parts = [p.strip() for p in (r.get("body") or "").split("|") if p.strip()]
        punch = (r.get("punch") or "").strip()
        sub = (r.get("subhead") or "").strip()
        last = i == len(rows)
        spec_i = spec if i == 1 else ""

        img = ""
        one = find_img(imgdir, i)
        two = (find_img(imgdir, i, "-a"), find_img(imgdir, i, "-b"))
        if all(two):
            img = f'<div class="imgband two"><img src="file://{two[0]}"><img src="file://{two[1]}"></div>'
        elif one:
            img = f'<div class="imgband"><img src="file://{one}"></div>'
        elif pool and receipts < 1 and 1 < i < len(rows):
            img = f'<div class="imgband study"><img src="file://{os.path.abspath(pool[0])}"></div>'
            receipts += 1
        elif last and not a.no_outro and a.style in ("classic","keyword","outline","dark","paper") and os.path.exists(OUTRO):
            img = f'<div class="imgband"><img src="file://{os.path.abspath(OUTRO)}"></div>'
        cap = credits.get(f"slide-{i:02d}")
        if img and st["label"] and cap and "et al" in cap:
            arrow = ('<svg width="54" height="40" viewBox="0 0 54 40" fill="none">'
                     f'<path d="M4 4 C 30 4, 44 12, 46 34" stroke="{st["sub"]}" stroke-width="4" stroke-linecap="round"/>'
                     f'<path d="M36 28 L46 36 L52 24" stroke="{st["sub"]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
            img = f'<div class="label">STUDY{arrow}</div>' + img
        if img and cap:
            img += f'<div class="cap">{html.escape(cap)}</div>'

        body_len = sum(len(p) for p in parts)
        # a slide with no image has the whole middle to itself; let the copy use it
        boost = 1.0 if img else 1.28
        hextra = ("-webkit-text-stroke:5px #fff;paint-order:stroke fill;font-weight:800;"
                  "text-shadow:0 4px 0 rgba(0,0,0,.22);letter-spacing:-1px;" if st["outline"] else "")
        page = TPL.format(
            W=W, H=H, hextra=hextra, lsize=int(22 * k), **st,
            headline=marks(r["headline"]),
            subhead=(f'<div class="subhead {secclass(sub)}">{marks(sub)}</div>' if sub else ""),
            spec=(f'<div class="spec">{html.escape(spec_i)}</div>' if spec_i else ""),
            blocks="".join(f'<div class="b">{marks(p)}</div>' for p in parts),
            imgblock=img,
            punch=f'<div class="punch">{marks(punch)}</div>' if punch else "",
            cover="cover" if i == 1 and not img else "", hcover=int(118 * k),
            specsize=int(20 * k), specgap=int(14 * k), pcover=int(50 * k), scover=int(46 * k),
            padtop=int(H * 0.105), padbot=int(H * 0.175), sgap=int(10 * k), bgap=int(34 * k), lgap=int(16 * k),
            hsize=max(int(56 * k), int((92 - max(0, len(r["headline"]) - 16) * 2.2) * k)),
            ssize=max(int(26 * k), int((40 - max(0, len(sub) - 22) * 0.6) * k)),
            bsize=max(int(22 * k), int((31 - max(0, body_len - 180) * 0.03) * k * boost)),
            psize=int(34 * k * boost), csize=int(18 * k),
            imax=int((500 if not parts else max(300, 430 - max(0, body_len - 160) * 0.30)) * k),
            smax=int(200 * k))
        src = os.path.join(tmp, f"s{i:02d}.html")
        open(src, "w").write(page)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={W},{H}",
                        f"--screenshot={os.path.join(outdir, f'slide-{i:02d}.png')}",
                        "--virtual-time-budget=6000", f"file://{src}"],
                       capture_output=True)
    print(f"  {len(rows)} slides -> {outdir}  ({a.size}, {a.style})")


if __name__ == "__main__":
    main()
