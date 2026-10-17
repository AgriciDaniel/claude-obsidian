#!/usr/bin/env python3
"""Generate per-slide diagram images for decks, in the channel palette.

Most slides need one of a small set of recurring visuals: a growth plate with
zones, a split pathway, a curve that dips and overshoots, two bars compared, a
blocked receptor. Rather than draw 400 images, these are parameterised
generators.

Output goes to content/<deck>/03-images/slide-NN.svg, which is exactly where
render-slides.py looks for it.

Usage:
    python3 scripts/make-deck-images.py            # build everything mapped below
    python3 scripts/make-deck-images.py --list     # show the mapping
"""
import os
import sys

CREAM, INK, BLUE, MUTED, WARM = "#F2EDE4", "#111111", "#1A5FD0", "#9A9187", "#C9BFAE"
W, H = 900, 620


def svg(body, h=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" '
            f'width="{W}" height="{h}"><rect width="{W}" height="{h}" fill="{CREAM}"/>{body}</svg>')


def t(x, y, s, size=26, fill=INK, weight="700", anchor="middle", style=""):
    return (f'<text x="{x}" y="{y}" font-family="Archivo,Helvetica,sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {style}>{s}</text>')


# ---------------------------------------------------------------- primitives

def growth_plate(labels=True, highlight=None):
    """Cross-section: resting / proliferative / hypertrophic zones."""
    x, w = 250, 400
    zones = [("Resting zone", 90, 90, WARM), ("Proliferative zone", 180, 200, "#E4D9C4"),
             ("Hypertrophic zone", 380, 130, WARM)]
    b = [f'<rect x="{x}" y="60" width="{w}" height="30" fill="{MUTED}" opacity="0.5"/>']
    for name, y, hgt, col in zones:
        fill = BLUE if highlight and highlight in name else col
        op = "0.85" if highlight and highlight in name else "1"
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{hgt}" fill="{fill}" opacity="{op}" stroke="{INK}" stroke-width="3"/>')
        if labels:
            b.append(t(x - 20, y + hgt / 2 + 8, name, 24, INK, "700", "end"))
    b.append(f'<rect x="{x}" y="510" width="{w}" height="50" fill="{MUTED}" opacity="0.5"/>')
    if labels:
        b.append(t(x + w / 2, 545, "bone", 22, INK, "400"))
    return svg("".join(b))


def split_path(left_label, right_label, top_label, left_note="", right_note=""):
    """One input splitting into two outcomes."""
    b = [t(450, 70, top_label, 34)]
    b.append(f'<line x1="450" y1="90" x2="450" y2="150" stroke="{INK}" stroke-width="5"/>')
    b.append(f'<path d="M450,150 L230,220" stroke="{INK}" stroke-width="5" fill="none"/>')
    b.append(f'<path d="M450,150 L670,220" stroke="{INK}" stroke-width="5" fill="none"/>')
    b.append(f'<rect x="70" y="230" width="320" height="120" rx="14" fill="{BLUE}"/>')
    b.append(t(230, 300, left_label, 32, CREAM))
    b.append(f'<rect x="510" y="230" width="320" height="120" rx="14" fill="{INK}"/>')
    b.append(t(670, 300, right_label, 32, CREAM))
    if left_note:
        b.append(t(230, 400, left_note, 24, INK, "400"))
    if right_note:
        b.append(t(670, 400, right_note, 24, INK, "400"))
    return svg("".join(b), 470)


def curve(points, label_a, label_b, shade=None, title=""):
    """Two-line chart. points = (baseline[], actual[]) as 0-100 values."""
    x0, y0, x1, y1 = 110, 90, 830, 470
    base, act = points
    def px(i, n): return x0 + i / (n - 1) * (x1 - x0)
    def py(v): return y1 - v / 100 * (y1 - y0)
    def path(vals): return " ".join(f"{'M' if i == 0 else 'L'}{px(i, len(vals)):.0f},{py(v):.0f}"
                                    for i, v in enumerate(vals))
    b = []
    if title:
        b.append(t(450, 50, title, 30))
    if shade:
        a, z = shade
        b.append(f'<rect x="{px(a,len(base)):.0f}" y="{y0}" width="{px(z,len(base))-px(a,len(base)):.0f}" '
                 f'height="{y1-y0}" fill="{MUTED}" opacity="0.2"/>')
    b.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="4"/>')
    b.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="4"/>')
    b.append(f'<path d="{path(base)}" fill="none" stroke="{MUTED}" stroke-width="6" stroke-dasharray="12 10"/>')
    b.append(f'<path d="{path(act)}" fill="none" stroke="{BLUE}" stroke-width="8" stroke-linejoin="round"/>')
    b.append(t(x1 - 10, py(base[-1]) + 42, label_a, 26, MUTED, "700", "end"))
    b.append(t(x1 - 10, py(act[-1]) - 22, label_b, 26, BLUE, "700", "end"))
    return svg("".join(b), 520)


def bars(items, title=""):
    """items = [(label, value 0-100, colour)]"""
    b = [t(450, 50, title, 30)] if title else []
    n = len(items)
    slot = 760 / n
    for i, (lab, val, col) in enumerate(items):
        bw = slot * 0.52
        bx = 90 + i * slot + (slot - bw) / 2
        bh = val / 100 * 330
        b.append(f'<rect x="{bx:.0f}" y="{440-bh:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="{col}"/>')
        b.append(t(bx + bw / 2, 480, lab, 24, INK))
    b.append(f'<line x1="70" y1="440" x2="830" y2="440" stroke="{INK}" stroke-width="4"/>')
    return svg("".join(b), 520)


def blocked(signal, receptor, note=""):
    """A signal arriving at a broken/blocked receiver."""
    b = [t(190, 130, signal, 32, BLUE)]
    b.append(f'<line x1="190" y1="160" x2="190" y2="250" stroke="{BLUE}" stroke-width="8"/>')
    b.append(f'<path d="M170,240 L190,265 L210,240" fill="{BLUE}"/>')
    b.append(f'<rect x="90" y="280" width="200" height="110" rx="12" fill="none" stroke="{INK}" stroke-width="5"/>')
    b.append(t(190, 345, receptor, 26))
    b.append(f'<line x1="105" y1="295" x2="275" y2="375" stroke="#B33" stroke-width="9"/>')
    b.append(f'<line x1="275" y1="295" x2="105" y2="375" stroke="#B33" stroke-width="9"/>')
    b.append(f'<line x1="320" y1="335" x2="470" y2="335" stroke="{MUTED}" stroke-width="6" stroke-dasharray="14 12"/>')
    b.append(t(690, 300, "no response", 34, MUTED))
    if note:
        b.append(t(450, 450, note, 26, INK, "400"))
    return svg("".join(b), 500)


# ---------------------------------------------------------------- mapping
# deck -> {slide number: (generator, args)}
MAP = {
    "growth-plate-fusion": {
        5: (curve, ([[50,58,66,74,82,90],[50,57,63,68,71,73]], "if capacity were infinite", "actual growth",
                    None, "Growth rate declines before anything fuses")),
    },
    "resting-zone-stem-cells": {
        2: (growth_plate, (True, "Resting")),
        3: (curve, ([[95,95,95,95,95,95],[95,88,70,45,22,8]], "if it never depleted", "% cells dividing",
                    None, "Resting zone proliferation, birth to 17 weeks")),
    },
    "local-conversion-growth-plate": {
        1: (growth_plate, (True, None)),
        6: (split_path, ("ESTRADIOL", "DHT", "TESTOSTERONE", "closes the plate", "cannot aromatise")),
    },
    "estrogen-sets-final-height": {
        4: (blocked, ("estradiol x10", "estrogen receptor", "Hormone present. Receiver broken.")),
    },
    "aromatase-deficient-man": {
        3: (split_path, ("BLOCKED", "TESTOSTERONE", "AROMATASE MISSING", "no estradiol made", "stays androgen")),
    },
    "catch-up-growth": {
        1: (curve, ([[50,56,62,68,74,80],[50,52,48,58,76,84]], "expected", "actual",
                    (1, 3), "Suppression, then overshoot")),
    },
    "suppression-conserves-capacity": {
        6: (curve, ([[50,56,62,68,74,80],[50,52,48,58,76,84]], "expected", "actual",
                    (1, 3), "Slow the division rate, keep the reserve")),
    },
    "gh-height-myth": {
        3: (bars, ([("control", 62, MUTED), ("GH treated", 78, BLUE)], "ISS meta-analyses: +4 to 6 cm")),
        4: (bars, ([("untreated", 88, MUTED), ("GH treated", 68, INK)], "J Pediatr 1997: 162.0 vs 154.2 cm")),
    },
    "thyroid-receptor-phenotypes": {
        3: (bars, ([("wild type", 60, MUTED), ("TR-beta mutant", 88, BLUE)], "Skeletal thyrotoxicosis")),
        4: (bars, ([("wild type", 60, MUTED), ("TR-alpha mutant", 30, INK)], "Skeletal hypothyroidism")),
    },
    "trenbolone-bone-length": {
        4: (bars, ([("control", 70, MUTED), ("exercise", 71, MUTED), ("trenbolone", 63, INK)],
                   "Femur length after 4 weeks")),
    },
    "different-bones-different-clocks": {
        3: (bars, ([("phalanges", 40, INK), ("metacarpals", 48, INK), ("tibia", 78, BLUE), ("femur", 85, BLUE)],
                   "Time until senescence, by bone")),
    },
    "aas-neurotoxicity": {
        7: (blocked, ("androgen", "androgen receptor", "Flutamide blocks it. Neurons live.")),
    },
    "cartilage-targeted-igf1": {
        7: (bars, ([("serum IGF-1", 85, MUTED), ("what the plate sees", 40, BLUE)],
                   "Blood level vs local concentration")),
    },
    "pulsatile-gh": {
        4: (curve, ([[40,40,40,40,40,40,40,40],[10,85,15,80,12,88,14,82]], "continuous", "pulsatile",
                    None, "Same total dose, different delivery")),
    },
    "bone-age-drivers": {
        1: (growth_plate, (True, None)),
    },
    "insulin-aromatase-obesity": {
        5: (split_path, ("AROMATASE UP", "MORE ESTRADIOL", "HIGH INSULIN", "in the plate", "closes earlier")),
    },
}


def main():
    if "--list" in sys.argv:
        for d, m in MAP.items():
            print(f"{d}: slides {sorted(m)}")
        return
    n = 0
    for deck, slides in MAP.items():
        outdir = f"content/{deck}/03-images"
        if not os.path.isdir(f"content/{deck}"):
            print(f"  skip (no deck): {deck}")
            continue
        os.makedirs(outdir, exist_ok=True)
        for num, (fn, args) in slides.items():
            path = f"{outdir}/slide-{num:02d}.svg"
            open(path, "w").write(fn(*args))
            n += 1
        print(f"{deck}: {len(slides)} images")
    print(f"\n{n} images generated")


if __name__ == "__main__":
    main()
