#!/usr/bin/env python3
"""Find CC-BY licensed papers with usable figures, by topic, via Europe PMC.

Solves the real bottleneck: not downloading figures, but knowing which of
thousands of open-access papers actually contains the diagram you need.
Searches Europe PMC, filters to CC-BY (commercially reusable — CC-BY-NC is
excluded because this channel is monetised), then pulls every figure caption
so you can see what's in each paper before opening it.

Usage:
    python3 scripts/find-oa-figures.py "growth plate senescence"
    python3 scripts/find-oa-figures.py "aromatase bone" --limit 15 --reviews
    python3 scripts/find-oa-figures.py "IGF-1 chondrocyte" --out catalogue.md

Figures themselves: open the PMC link and save the image. PMC blocks scripted
image fetches, so that step stays manual — but you'll know exactly which
figure to grab.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request

REST = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = {"User-Agent": "figure-catalogue/1.0 (research use)"}


def get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as exc:
            if attempt == retries - 1:
                print(f"  ! {exc}", file=sys.stderr)
                return ""
            time.sleep(1.5 * (attempt + 1))
    return ""


def search(topic, limit, reviews_only):
    q = f'({topic}) AND (OPEN_ACCESS:y) AND (LICENSE:"cc by")'
    if reviews_only:
        q += ' AND (PUB_TYPE:"review")'
    url = f"{REST}/search?query={urllib.parse.quote(q)}&format=json&pageSize={limit}&resultType=core"
    raw = get(url)
    if not raw:
        return [], 0
    data = json.loads(raw)
    return data.get("resultList", {}).get("result", []), data.get("hitCount", 0)


def figures(pmcid):
    """Return [(label, caption)] for one article."""
    xml = get(f"{REST}/{pmcid}/fullTextXML")
    if not xml:
        return []
    out = []
    for block in re.findall(r"<fig[ >].*?</fig>", xml, re.S):
        label = re.search(r"<label>(.*?)</label>", block, re.S)
        cap = re.search(r"<caption>(.*?)</caption>", block, re.S)
        label = re.sub(r"<[^>]+>", "", label.group(1)).strip() if label else "Figure"
        cap = " ".join(re.sub(r"<[^>]+>", "", cap.group(1)).split()) if cap else ""
        out.append((label, cap))
    return out


# Captions that signal a figure is a diagram/schematic rather than a data plot
# or a methods artefact — diagrams are what illustrate a mechanism on a slide.
GOOD = re.compile(
    r"schematic|diagram|overview|model|illustration|mechanism|pathway|signalling|signaling|"
    r"structure|zones?\b|architecture|summary|graphical abstract",
    re.I,
)
SKIP = re.compile(r"prisma|flow diagram|flowchart|search strategy|forest plot|funnel plot", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--reviews", action="store_true", help="reviews only (best figures)")
    ap.add_argument("--must", help="comma-separated terms; keep only papers whose "
                                   "TITLE contains at least one. Without this, broad "
                                   "queries return topically-adjacent junk.")
    ap.add_argument("--out", help="write markdown here instead of stdout")
    args = ap.parse_args()

    results, total = search(args.topic, args.limit, args.reviews)

    if args.must:
        terms = [t.strip().lower() for t in args.must.split(",") if t.strip()]
        kept = [r for r in results
                if any(t in (r.get("title") or "").lower() for t in terms)]
        print(f"  title filter kept {len(kept)}/{len(results)}", file=sys.stderr)
        results = kept
    lines = [f"# OA figure catalogue — {args.topic}", ""]
    lines.append(f"{total} CC-BY matches in Europe PMC; showing {len(results)}.")
    lines.append("All CC BY 4.0 — commercial reuse permitted **with attribution**.")
    lines.append("")

    for r in results:
        pmcid = r.get("pmcid")
        if not pmcid:
            continue
        title = r.get("title", "").rstrip(".")
        journal = r.get("journalInfo", {}).get("journal", {}).get("title", "")
        year = r.get("pubYear", "")
        figs = figures(pmcid)
        picks = [(l, c) for l, c in figs if GOOD.search(c or l) and not SKIP.search(c or l)]
        if not figs:
            continue
        lines.append(f"## {title}")
        lines.append(f"*{journal}* {year} · [{pmcid}](https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/) "
                     f"· {len(figs)} figures, {len(picks)} diagram-like")
        lines.append("")
        for label, cap in (picks or figs):
            flag = " ⭐" if (label, cap) in picks else ""
            lines.append(f"- **{label}**{flag} {cap[:190]}")
        lines.append("")
        time.sleep(0.4)  # be polite to the API

    text = "\n".join(lines)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
        print(f"wrote {args.out} ({len(results)} papers)")
    else:
        print(text)


if __name__ == "__main__":
    main()
