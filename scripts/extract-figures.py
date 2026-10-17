"""Workstream 6 — pull figure images out of the study PDFs.

Writes images to _attachments/figures/<paper-slug>/ and one stub page per figure
to wiki/figures/. Filters out logos, rules and decorative marks by size and shape,
and pulls the caption line beneath each image so the `shows:` field starts filled.
"""
import re, sys
from pathlib import Path
from datetime import date
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
PDFS = ROOT/".raw/Studies"
IMGS = ROOT/"_attachments/figures"
PAGES= ROOT/"wiki/figures"
IMGS.mkdir(parents=True, exist_ok=True); PAGES.mkdir(parents=True, exist_ok=True)
today = date.today().isoformat()

MIN_W, MIN_H, MIN_PX = 220, 160, 90_000     # below this it's a logo or a rule
CAPTION = re.compile(r"(fig(?:ure)?\.?\s*\d+[a-z]?\.?\s*[^\n]{10,220})", re.I)

def slug(s, n=60):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:n] or "untitled"

def classify(caption, w, h):
    c = (caption or "").lower()
    if re.search(r"surviv|kaplan|meier", c):                 return "survival"
    if re.search(r"forest|meta-analys|odds ratio|hazard", c): return "forest-plot"
    if re.search(r"blot|western|gel|pcr|flow cytom|facs", c): return "blot-gel-flow"
    if re.search(r"stain|histolog|micrograph|h&e|immunohist|section", c): return "histology"
    if re.search(r"dose|concentration.{0,20}response|ec50|ic50", c): return "dose-response"
    if re.search(r"time.?course|over time|week|day \d|hours", c):return "time-course"
    if re.search(r"schematic|pathway|model|mechanism|diagram", c):return "mechanism-schematic"
    if re.search(r"anatom|skeleton|radiograph|x-ray|mri|ct\b", c): return "anatomical"
    if re.search(r"\bvs\b|versus|compared|group", c):          return "comparison-bars"
    return "uncategorised"

pdfs = sorted(p for p in PDFS.rglob("*.pdf"))
if len(sys.argv) > 1: pdfs = pdfs[:int(sys.argv[1])]
print(f"scanning {len(pdfs)} pdfs\n")

tot_fig = 0; per_type = {}; papers = 0; errs = 0
for pdf in pdfs:
    try:
        doc = pymupdf.open(pdf)
    except Exception:
        errs += 1; continue
    stem = slug(pdf.stem)
    outdir = IMGS/stem
    n_here = 0
    for pno in range(len(doc)):
        page = doc[pno]
        try: text = page.get_text()
        except Exception: text = ""
        caps = CAPTION.findall(text)
        for i, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try: pix = pymupdf.Pixmap(doc, xref)
            except Exception: continue
            w, h = pix.width, pix.height
            if w < MIN_W or h < MIN_H or w*h < MIN_PX:
                pix = None; continue
            if max(w,h)/max(min(w,h),1) > 8:          # banner/rule
                pix = None; continue
            n_here += 1
            cap = caps[min(i, len(caps)-1)] if caps else ""
            cap = re.sub(r"\s+"," ",cap).strip()
            dtype = classify(cap, w, h)
            per_type[dtype] = per_type.get(dtype,0)+1
            outdir.mkdir(parents=True, exist_ok=True)
            fid = f"fig-{stem[:40]}-p{pno+1:03d}-{n_here:02d}"
            try:
                if pix.n - pix.alpha >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                pix.save(outdir/f"{fid}.png")
            except Exception:
                pix=None; continue
            pix = None
            (PAGES/f"{fid}.md").write_text(
f"""---
type: figure
figure_id: "{fid}"
source_pdf: "{pdf.name}"
page: {pno+1}
display_type: "{dtype}"
dimensions: "{w}x{h}"
shows: "{cap[:180].replace('"',"'")}"
licence: "publisher — redraw, do not republish"
status: {"captioned" if cap else "needs-description"}
created: {today}
updated: {today}
tags: [figure, {dtype}]
---

# {fid}

![[figures/{stem}/{fid}.png]]

**Caption as printed:** {cap or "_none found on this page — describe it yourself_"}

**Shows:** _one line, as you would say it out loud_

**Redraw as:** _what to draw instead of reusing the original_

**Source:** `{pdf.name}` page {pno+1}

**Used in:**
""")
            tot_fig += 1
    doc.close()
    if n_here: papers += 1

print(f"{tot_fig} figures from {papers} papers ({errs} unreadable)\n")
print(f"{'display type':<24}{'count':>7}")
for k,v in sorted(per_type.items(), key=lambda x:-x[1]):
    print(f"{k:<24}{v:>7}")
