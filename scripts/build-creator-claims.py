"""Pipeline B — competitor slideshows to creator-claim pages.

Reads the OCR'd slide corpus plus post metadata, groups posts by topic, and
writes one page per topic to wiki/creators/ recording what each account
asserted, with views attached. Everything written here is evidence_tier X:
a record of what the niche believes, never a source of fact.
"""
import argparse
import json, csv, re, unicodedata
from pathlib import Path
from collections import defaultdict
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
SA   = ROOT / "content/_style-analysis"
OUT  = ROOT / "wiki/creators"

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
    argparse.ArgumentParser(description="Pipeline B — competitor slideshows to creator-claim pages").parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    meta = {}
    with open(SA/"all-posts.csv") as f:
        for r in csv.DictReader(f):
            for k in ("plays","likes","comments","shares","saves"):
                r[k] = int(r[k] or 0)
            meta[(r["acct"], r["id"])] = r

    slides = defaultdict(list)
    with open(SA/"slide-text.jsonl") as f:
        for line in f:
            d = json.loads(line)
            slides[(d["acct"], d["post"])].append((d["slide"], d["text"]))

    # topic taxonomy: ordered, first match wins, so specific beats general
    TOPICS = [
     ("Growth plate hypoxia",      r"hypoxi|HIF-?1|hemoglobin|haemoglobin|oxygen.{0,20}(plate|cartilage|chondro)"),
     ("FGFR3 and plate closure",   r"fgfr3|achondropl|erdafitinib|infigratinib|\btyra\b"),
     ("GH and IGF-1 axis",         r"\bgh\b|growth hormone|igf-?1|igf-?i\b|somatropin|jak.?stat|stat5"),
     ("Bone age and plate closure",r"bone age|epiphys|growth plate clos|fusion|final adult height|\bfah\b"),
     ("Oestrogen and bone",        r"estrogen|oestrogen|aromatase|\be2\b|anastrozol|letrozol|\bai\b.{0,10}bone"),
     ("Androgens and AAS",         r"testosterone|androgen|\baas\b|steroid|trenbolone|anavar|\btrt\b|dht"),
     ("Mandible and facial bone",  r"mandib|gonial|ramus|masseter|maxilla|zygomat|canthal|bone smash"),
     ("Hair follicle and DHT",     r"minoxidil|finasterid|dutasterid|follicle|alopecia|balding|hair loss"),
     ("Skin and photoageing",      r"collagen|retinoid|retinol|tretinoin|photoag|sunscreen|\bspf\b|wrinkl"),
     ("Nootropics and cognition",  r"nootropic|racetam|modafinil|dopamine|acetylcholin|cognit|adhd|memory"),
     ("Peptides",                  r"bpc-?157|tb-?500|ghk|ipamorelin|cjc-?1295|sermorelin|mots-?c|peptide"),
     ("Sleep and circadian",       r"circadian|melatonin|slow.?wave|\bn3\b|sleep"),
     ("Thyroid and metabolism",    r"thyroid|\bt3\b|\bt4\b|tsh|metabolic rate|brown fat|thermogen"),
     ("Creatine and supplements",  r"creatine|vitamin d|zinc\b|magnesium|omega-?3|supplement"),
     ("Mechanical loading",        r"mechanotransduc|osteocyte|osteoblast|osteoclast|mechanical load|strain rate|pemf"),
    ]

    CLAIM = re.compile(
        r"\b(increase|decrease|boost|reduce|improve|cause|block|suppress|stimulat|activat|inhibit|"
        r"lower|raise|acceler|stunt|prevent|trigger|enhance|upregulat|downregulat|promot|delay|close)\w*\b",
        re.I)
    STUDY = re.compile(r"\b(study|studies|trial|research|journal|published|et al|shown|showed|data)\b", re.I)
    CITE  = re.compile(r"\b([A-Z][a-zA-Z\-]{2,20}(?:\s+et\s*al\.?)?)[,\s(]+((?:19|20)\d{2})\b")
    BADCITE = {"the","this","that","and","for","but","with","from","was","were","not","june","july",
               "aug","sep","oct","nov","dec","jan","feb","mar","apr","may","feb","figure","table","aufrufe"}

    def clean(t):
        t = unicodedata.normalize("NFKC", t)
        t = re.sub(r"[^\S\n]+", " ", t)
        return t.strip()

    def topic_of(text):
        hits = []
        for name, pat in TOPICS:
            n = len(re.findall(pat, text, re.I))
            if n: hits.append((n, name))
        if not hits: return None
        hits.sort(reverse=True)
        return hits[0][1]

    def sentences(t):
        flat = re.sub(r"\s+", " ", t)
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat) if 30 < len(s.strip()) < 320]

    # Slides that are screenshots of paper figures OCR into noise. Keep only text that
    # still reads as English, or the pages fill with garbage that looks like evidence.
    COMMON = set("""the a an and or but if then than that this these those is are was were be been
    being has have had do does did can could will would should may might must of in on at to for
    from with by as it its they them their we you your not no more most less least than when while
    because so also into over under after before between during both each other such only same
    very just about above again further once here there all any few own too s t""".split())

    def legible(s):
        letters = sum(c.isalpha() for c in s)
        if letters < 0.62 * len(s):                 # too much punctuation/symbol soup
            return False
        if re.search(r"[�⁢-⁩]", s):  # OCR replacement chars
            return False
        words = re.findall(r"[A-Za-z']+", s.lower())
        if len(words) < 8:
            return False
        if sum(w in COMMON for w in words) < 0.22 * len(words):
            return False                            # no connective tissue = not a sentence
        if sum(1 for w in words if len(w) > 14) > 1:
            return False                            # run-together OCR blobs
        return True

    buckets = defaultdict(lambda: defaultdict(list))   # topic -> acct -> [post records]
    for (acct, post), sl in slides.items():
        m = meta.get((acct, post))
        if not m: continue
        sl.sort()
        full = clean(" ".join(t for _, t in sl))
        topic = topic_of(full)
        if not topic: continue

        claims, cites = [], set()
        for s in sentences(full):
            if CLAIM.search(s) and legible(s):
                claims.append(s)
        for mm in CITE.finditer(full):
            nm, yr = mm.group(1).strip(), mm.group(2)
            if nm.lower() not in BADCITE and len(nm) > 3:
                cites.add(f"{nm} {yr}")

        buckets[topic][acct].append(dict(
            post=post, views=m["plays"], saves=m["saves"], slides=len(sl),
            desc=m["desc"].strip(), claims=claims[:6], cites=sorted(cites)[:8],
            evidenced=sum(1 for c in claims if STUDY.search(c)), nclaims=len(claims)))

    def slug(s):
        return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

    today = date.today().isoformat()
    written = []
    for topic, accts in sorted(buckets.items()):
        posts = [p for ps in accts.values() for p in ps]
        total_views = sum(p["views"] for p in posts)
        all_cites = sorted({c for p in posts for c in p["cites"]})
        tot_claims = sum(p["nclaims"] for p in posts)
        tot_ev = sum(p["evidenced"] for p in posts)

        L = []
        L.append("---")
        L.append("type: creator-claim")
        L.append(f'topic: "{topic}"')
        L.append("evidence_tier: X")
        L.append(f"posts_analysed: {len(posts)}")
        L.append(f"accounts: {len(accts)}")
        L.append(f"total_views: {total_views}")
        L.append(f"claims_extracted: {tot_claims}")
        L.append(f"claims_with_study_language: {tot_ev}")
        L.append(f"created: {today}")
        L.append(f"updated: {today}")
        L.append("tags:\n  - creator-claim\n  - competitor-corpus\n  - tier-x")
        L.append("status: seed")
        L.append("---\n")
        L.append(f"# {topic} — what the niche asserts\n")
        L.append("> [!warning] Evidence tier X")
        L.append("> Everything on this page is **what creators said**, transcribed from their own slides.")
        L.append("> It is a record of the niche's beliefs, not a source of fact. Verify against")
        L.append("> `wiki/sources/` before any of it reaches a slide of yours.\n")
        L.append(f"**{len(posts)} posts** across **{len(accts)} accounts**, "
                 f"**{total_views:,}** combined views. "
                 f"{tot_ev} of {tot_claims} extracted claims use study language "
                 f"({(100*tot_ev/tot_claims if tot_claims else 0):.0f}%).\n")

        L.append("## Positions by account\n")
        for acct, ps in sorted(accts.items(), key=lambda kv: -sum(p["views"] for p in kv[1])):
            av = sum(p["views"] for p in ps)
            L.append(f"### {acct} — {len(ps)} post(s), {av:,} views\n")
            for p in sorted(ps, key=lambda x: -x["views"])[:4]:
                L.append(f"**Post `{p['post']}`** · {p['views']:,} views · {p['saves']:,} saves · {p['slides']} slides")
                if p["desc"]:
                    L.append(f"> Caption: {p['desc'][:180]}")
                if p["cites"]:
                    L.append(f"> Cites: {', '.join(p['cites'])}")
                if p["claims"]:
                    L.append("")
                    for c in p["claims"][:4]:
                        L.append(f"- {c}")
                L.append("")

        if all_cites:
            L.append("## Studies this topic points at\n")
            L.append("Verify each before use. Some are OCR artefacts.\n")
            for c in all_cites[:30]:
                L.append(f"- [ ] `{c}` — not yet matched to a page in `wiki/sources/`")
            L.append("")

        L.append("## To do\n")
        L.append("- [ ] Split the genuine claims from the OCR noise above")
        L.append("- [ ] Create a `wiki/claims/` page for any claim two or more accounts repeat")
        L.append("- [ ] Mark where accounts contradict each other")
        L.append(f"- [ ] Link to the concept page for this topic\n")
        L.append("## Related\n")
        L.append("- [[index]]")

        path = OUT / f"{slug(topic)}.md"
        path.write_text("\n".join(L))
        written.append((topic, len(posts), len(accts), total_views, tot_claims))

    print(f"{len(written)} creator-claim pages written to wiki/creators/\n")
    print(f"{'topic':<30}{'posts':>7}{'accts':>7}{'views':>12}{'claims':>8}")
    for t,p,a,v,c in sorted(written, key=lambda x:-x[3]):
        print(f"{t:<30}{p:>7}{a:>7}{v:>12,}{c:>8}")
