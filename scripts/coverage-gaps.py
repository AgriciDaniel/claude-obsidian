"""Pipeline D targeting — what the niche discusses that the vault cannot back up.

Counts how often each compound/pathway/hormone appears across the competitor
corpus (weighted by views), then checks whether wiki/sources/ has anything on it.
High discussion + zero sources = the paper you should go and find next.
"""
import argparse
import json, csv, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
SA   = ROOT/"content/_style-analysis"
SRC  = ROOT/"wiki/sources"

# terms worth tracking: things a monograph or pathway page could be written about
TERMS = {
 "IGF-1":r"igf-?1|igf-?i\b", "Growth hormone":r"\bgh\b|growth hormone|somatropin",
 "FGFR3":r"fgfr3", "CNP / NPR-B":r"\bcnp\b|npr-?b|vosoritide",
 "PTHrP":r"pthrp|pth-?rp", "Indian hedgehog":r"\bihh\b|indian hedgehog",
 "BMP":r"\bbmp-?\d?\b|bone morphogenetic", "VEGF":r"\bvegf\b",
 "HIF-1α":r"hif-?1|hif1a", "SOX9":r"\bsox-?9\b", "RUNX2":r"runx-?2",
 "Aromatase":r"aromatase|anastrozol|letrozol|exemestan",
 "Oestrogen receptor":r"estrogen receptor|oestrogen receptor|\ber-?alpha\b|esr1",
 "Testosterone":r"testosterone", "DHT":r"\bdht\b|dihydrotestosterone",
 "5-alpha reductase":r"5-?alpha-?reductase|finasterid|dutasterid",
 "Minoxidil":r"minoxidil", "Melatonin":r"melatonin",
 "Thyroid T3/T4":r"\bt3\b|\bt4\b|levothyrox|liothyron",
 "Creatine":r"creatine", "Vitamin D":r"vitamin ?d\b|cholecalciferol",
 "BPC-157":r"bpc-?157", "TB-500":r"tb-?500|thymosin",
 "GHK-Cu":r"ghk-?cu", "Ipamorelin":r"ipamorelin", "CJC-1295":r"cjc-?1295",
 "Tesamorelin":r"tesamorelin", "MK-677":r"mk-?677|ibutamoren",
 "Retinoid / tretinoin":r"tretinoin|retinoid|isotretinoin|retinol",
 "Collagen":r"collagen", "RANKL / OPG":r"rankl|osteoprotegerin|\bopg\b",
 "Sclerostin":r"sclerostin|romosozumab", "Odanacatib":r"odanacatib|cathepsin ?k",
 "PEMF":r"\bpemf\b|pulsed electromagnetic", "Mechanotransduction":r"mechanotransduc|osteocyte",
 "Modafinil":r"modafinil|armodafinil", "Racetams":r"racetam",
 "Caffeine":r"caffeine", "L-theanine":r"theanine",
 "Orexin":r"orexin|hypocretin", "Dopamine D2":r"\bd2\b receptor|dopamine receptor",
 "Semaglutide / GLP-1":r"semaglutide|glp-?1|tirzepatide",
 "Myostatin":r"myostatin|follistatin", "SARMs":r"\bsarm|ostarine|rad-?140|lgd-?4033",
 "Anavar / oxandrolone":r"anavar|oxandrolone", "hCG":r"\bhcg\b",
 "Clomiphene / SERM":r"clomiphen|tamoxifen|\bserm\b|enclomiphene",
}

meta={}

import sys

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from claude_obsidian.paths import VaultSelectionError, resolve_vault_root


def vault_root() -> Path:
    """Resolve the vault to act on, failing closed when there is none.

    Never derive paths from __file__: under the installed product tree that
    resolves to the plugin directory, so writing there corrupts the install.
    """
    return resolve_vault_root(plugin_root=PLUGIN_ROOT).root


if __name__ == "__main__":
    argparse.ArgumentParser(description="Pipeline D targeting — what the niche discusses that the vault cannot back up").parse_args()

    with open(SA/"all-posts.csv") as f:
        for r in csv.DictReader(f):
            r["plays"]=int(r["plays"] or 0); meta[(r["acct"],r["id"])]=r

    slides=defaultdict(list)
    with open(SA/"slide-text.jsonl") as f:
        for line in f:
            d=json.loads(line); slides[(d["acct"],d["post"])].append(d["text"])

    # optional: fold in video transcripts if the run has produced any
    vt = SA/"video-text.jsonl"
    nvid=0
    if vt.exists():
        for line in vt.open():
            try: d=json.loads(line)
            except Exception: continue
            if d.get("text"):
                slides[(d["acct"],d["post"])].append(d["text"]); nvid+=1

    # what the vault already covers, from source page filenames + titles
    have=[]
    for p in SRC.glob("*.md"):
        t=p.stem.replace("-"," ").lower()
        try: t += " " + p.read_text()[:600].lower()
        except Exception: pass
        have.append(t)
    haystack=" || ".join(have)

    rows=[]
    for term, pat in TERMS.items():
        posts=0; views=0
        for k, texts in slides.items():
            blob=" ".join(texts)
            if re.search(pat, blob, re.I):
                posts+=1
                m=meta.get(k)
                if m: views+=m["plays"]
        nsrc=len(re.findall(pat, haystack, re.I))
        rows.append((term, posts, views, nsrc))

    rows.sort(key=lambda r:-r[2])
    print(f"corpus: {len(slides)} posts ({nvid} video transcripts folded in)")
    print(f"vault:  {len(have)} source pages scanned\n")
    print(f"{'term':<26}{'posts':>6}{'views':>11}{'src hits':>10}   verdict")
    print("-"*72)
    gaps=[]
    for term,posts,views,nsrc in rows:
        if posts==0: continue
        if nsrc==0:      v="** NO SOURCE — go find one **"; gaps.append((term,posts,views))
        elif nsrc<3:     v="thin"
        else:            v="covered"
        print(f"{term:<26}{posts:>6}{views:>11,}{nsrc:>10}   {v}")

    print(f"\n{len(gaps)} terms discussed in the corpus with zero coverage in wiki/sources/:")
    for t,p,v in sorted(gaps,key=lambda x:-x[2]):
        print(f"  {t:<26} {p:>3} posts  {v:>10,} views")
