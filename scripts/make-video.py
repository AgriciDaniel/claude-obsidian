#!/usr/bin/env python3
"""Turn a slideshow into a 45-90 second spoken script.

A video is not the deck read aloud. Reading every slide of a 13-slide post at
178 wpm lands around 110 seconds, which is outside the band that performed in
the scrape (45-90s; 15-30s is worst). So this selects rather than transcribes:
the hook, the single strongest number, the mechanism, the turn, the payoff.

Selection is by scoring, not by position, because the strongest slide is in a
different place in every deck:
  - numbers      a slide carrying measured values is worth more than one framing
  - ==emphasis== the author already marked the line that matters
  - section tag  on orca decks, BENEFIT/DOWNSIDE/COUNTER carry the argument

Usage:
    python3 scripts/make-video.py content/<deck>
    python3 scripts/make-video.py "content/hgh-*"      # quote the glob in zsh
"""
import argparse
import csv
import glob
import os
import re

WPM = 178                      # measured pace of the competitor videos
TARGET_S = 72                  # mid-band
MAX_WORDS = int(90 / 60 * WPM) # hard ceiling at 90s


def clean(s):
    """Strip emphasis markers and the ' | ' block separator for speech."""
    s = re.sub(r"==(.+?)==", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"[*_]", "", s)
    return " ".join(s.replace("|", " ").split())


def first_sentences(text, n=2):
    """Pick the n sentences that carry the argument, not the first n.

    Taking sentences 1-2 kept 'Exercise alone gave an AUC of 292.6' and dropped
    'after pyridostigmine gave 587.3', which is the half that matters. Score each
    sentence for data and keep the best, in original order.
    """
    parts = [p for p in re.split(r"(?<=[.!?])\s+", clean(text)) if len(p.split()) > 2]
    if len(parts) <= n:
        return " ".join(parts).strip()

    def sent_score(x):
        v = 0
        v += 3 * len(re.findall(r"\b\d[\d.,]*\s*(?:%|cm|mm|ng|µg|mg|SDS|fold|x)\b", x, re.I))
        v += 3 * len(re.findall(r"\bP\s*[<=]\s*0?\.\d+", x))
        v += 2 * len(re.findall(r"\b\d[\d.,]{1,}\b", x))
        v += 2 if re.search(r"\b(against|versus|vs|compared|than)\b", x, re.I) else 0
        v -= 1 if len(x.split()) > 34 else 0
        return v

    ranked = sorted(range(len(parts)), key=lambda i: sent_score(parts[i]), reverse=True)
    best = [ranked[0]]
    # a sentence that opens with a back-reference is meaningless without the one
    # before it: "The same exercise ... gave 587.3" needs the 292.6 it answers.
    BACKREF = re.compile(r"^(the same|and |then |but |that |these |those |it )", re.I)
    i0 = ranked[0]
    if BACKREF.match(parts[i0]) and i0 > 0:
        best.insert(0, i0 - 1)
    for i in ranked[1:]:
        if len(best) >= n:
            break
        if i not in best:
            best.append(i)
    return " ".join(parts[i] for i in sorted(set(best))[:n]).strip()


def score(row):
    """How much does this slide earn its place in 75 seconds?"""
    body = row.get("body") or ""
    if not body.strip():
        return -1                                   # cover and outro handled separately
    s = 0
    s += 3 * len(re.findall(r"\b\d[\d.,]*\s*(?:%|cm|mm|ng|µg|mg|SDS|fold|x)\b", body, re.I))
    s += 2 * len(re.findall(r"\bP\s*[<=]\s*0?\.\d+", body))
    s += 2 * len(re.findall(r"\b\d[\d.,]{1,}\b", body))
    s += 4 if "==" in (row.get("punch") or "") else 0
    sub = (row.get("subhead") or "").upper()
    for tag, w in (("BENEFIT", 4), ("DOWNSIDE", 4), ("COUNTER", 3),
                   ("THE SUMMARY", 5), ("TAKEAWAY", 5), ("LIMIT", 2)):
        if tag in sub:
            s += w
    return s


def build(deck):
    rows = list(csv.DictReader(open(os.path.join(deck, "04-slides.csv"))))
    if len(rows) < 3:
        return None
    spec_path = os.path.join(deck, "00-spec.txt")
    spec = open(spec_path).read().strip() if os.path.exists(spec_path) else ""

    cover, outro = rows[0], rows[-1]
    middle = rows[1:-1]

    # the closing slide is whichever one summarises; otherwise the last middle one
    closer = next((r for r in reversed(middle)
                   if re.search(r"TAKEAWAY|THE SUMMARY|WHAT (THIS|ACTUALLY|HOLDS)",
                                (r.get("subhead") or "").upper())), middle[-1])
    pool = [r for r in middle if r is not closer]
    ranked = sorted(pool, key=score, reverse=True)

    beats, words = [], 0
    hook = clean(cover.get("punch") or cover.get("headline"))
    opener = f"{clean(cover['headline'])}. {hook}"
    beats.append(("hook", opener, "cover card"))
    words += len(opener.split())

    close = first_sentences(closer.get("body") or closer.get("punch"), 2)
    close_punch = clean(closer.get("punch") or "")
    reserved = len(close.split()) + len(close_punch.split()) + 4

    for r in ranked:
        if score(r) <= 0:
            continue
        line = first_sentences(r["body"], 2)
        if not line:
            continue
        if words + len(line.split()) + reserved > MAX_WORDS:
            continue
        cue = (r.get("subhead") or r.get("headline") or "").split("·")[-1].strip().lower()
        beats.append(("beat", line, cue))
        words += len(line.split())
        if words + reserved >= TARGET_S / 60 * WPM:
            break

    # A deck whose slides are mostly prose rather than data scored almost nothing
    # and produced a 28-second script. Backfill in deck order until the floor.
    MIN_WORDS = int(48 / 60 * WPM)
    if words + reserved < MIN_WORDS:
        chosen = {b[1] for b in beats}
        for r in pool:
            line = first_sentences(r.get("body") or "", 2)
            if not line or line in chosen:
                continue
            if words + len(line.split()) + reserved > MAX_WORDS:
                continue
            cue = (r.get("subhead") or r.get("headline") or "").split("·")[-1].strip().lower()
            beats.append(("beat", line, cue))
            chosen.add(line)
            words += len(line.split())
            if words + reserved >= MIN_WORDS:
                break

    # keep the beats in deck order so the argument still runs forwards
    order = {id(r): i for i, r in enumerate(rows)}
    body_beats = sorted([b for b in beats if b[0] == "beat"],
                        key=lambda b: next((order[id(r)] for r in pool
                                            if first_sentences(r["body"], 2) == b[1]), 99))
    beats = [beats[0]] + body_beats
    beats.append(("close", close, "takeaway card"))
    if close_punch:
        beats.append(("close", close_punch, ""))
    words += len(close.split()) + len(close_punch.split())

    cta = clean(outro.get("punch") or "DM for source")
    beats.append(("cta", cta, ""))
    words += len(cta.split())

    title = clean(cover["headline"])
    out = [f"# Video script — {title}", ""]
    if spec:
        out.append(spec)
        out.append("")
    out += [f"{words} words, ~{words * 60 // WPM}s at {WPM} wpm. Target band 45-90s.",
            "", "Spoken lines only. Visual cue in brackets.", "", "---", ""]
    for kind, line, cue in beats:
        out.append(line)
        out.append("")
        if cue:
            out.append(f"[{cue}]")
            out.append("")
    return "\n".join(out).rstrip() + "\n", words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("decks", nargs="+")
    a = ap.parse_args()
    targets = []
    for pat in a.decks:
        targets += [d for d in sorted(glob.glob(pat))
                    if os.path.isfile(os.path.join(d, "04-slides.csv"))]
    for d in targets:
        r = build(d)
        if not r:
            print(f"  skip {os.path.basename(d)} (too few slides)")
            continue
        text, words = r
        open(os.path.join(d, "03-video.md"), "w").write(text)
        secs = words * 60 // WPM
        flag = "" if 45 <= secs <= 90 else "  <- outside band"
        print(f"  {os.path.basename(d):30} {words:4} words  ~{secs:3}s{flag}")


if __name__ == "__main__":
    main()
