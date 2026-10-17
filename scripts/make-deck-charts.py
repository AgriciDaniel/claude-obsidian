#!/usr/bin/env python3
"""Generate the chart assets the decks need, as SVG, in the channel's palette.

Several slides call for a chart no published figure provides — a proliferation
collapse, a catch-up curve, two conflicting trial outcomes. Rather than leave
those as "redraw" TODOs, this emits them directly.

SVG because it stays crisp at 1080x1920, imports into Canva (Pro), and can be
restyled by editing the palette below rather than regenerating art.

Usage:
    python3 scripts/make-deck-charts.py            # write all charts
    python3 scripts/make-deck-charts.py --list     # show what it makes
"""
import sys
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

# Channel palette, taken from the existing decks
CREAM = "#F2EDE4"
INK = "#111111"
BLUE = "#1A5FD0"
MUTED = "#9A9187"
W, H = 1000, 700


def frame(body, title, sub=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<rect width="{W}" height="{H}" fill="{CREAM}"/>
<text x="50" y="70" font-family="Arial Black, Arial, sans-serif" font-size="44" font-weight="900" fill="{INK}">{title}</text>
<text x="50" y="112" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="{BLUE}">{sub}</text>
{body}
</svg>'''


def axes(x0, y0, x1, y1):
    return (f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="4"/>'
            f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="4"/>')


def label(x, y, t, size=22, color=INK, weight="700", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{t}</text>')


def proliferation_collapse():
    """Resting-zone slide 3: >95% at birth -> <10% by 17 weeks."""
    x0, y0, x1, y1 = 130, 170, 930, 560
    pts = [(0, 96), (2, 88), (4, 70), (6, 50), (9, 30), (12, 18), (17, 8)]
    def px(w): return x0 + (w / 17) * (x1 - x0)
    def py(p): return y1 - (p / 100) * (y1 - y0)
    path = " ".join(f"{'M' if i == 0 else 'L'}{px(w):.0f},{py(p):.0f}" for i, (w, p) in enumerate(pts))
    dots = "".join(f'<circle cx="{px(w):.0f}" cy="{py(p):.0f}" r="7" fill="{BLUE}"/>' for w, p in pts)
    body = (axes(x0, y0, x1, y1)
            + f'<path d="{path}" fill="none" stroke="{BLUE}" stroke-width="7" stroke-linejoin="round"/>'
            + dots
            + label(x0 + 10, py(96) - 22, "&gt;95% dividing at birth", 26)
            + label(x1 - 10, py(8) - 26, "&lt;10% by 17 weeks", 26, anchor="end")
            + label((x0 + x1) / 2, y1 + 52, "Age (weeks)", 24, MUTED, anchor="middle")
            + f'<text x="70" y="{(y0+y1)/2}" font-family="Arial" font-size="24" font-weight="700" '
              f'fill="{MUTED}" text-anchor="middle" transform="rotate(-90 70 {(y0+y1)/2})">% cells dividing</text>')
    return frame(body, "The reserve empties", "RESTING ZONE PROLIFERATION")


def catchup_curve():
    """Catch-up slide 1: suppression then overshoot."""
    x0, y0, x1, y1 = 130, 170, 930, 560
    normal = [(0, 50), (2, 56), (4, 62), (6, 68), (8, 74), (10, 80)]
    treated = [(0, 50), (2, 52), (4, 48), (6, 58), (8, 76), (10, 84)]
    def px(t): return x0 + (t / 10) * (x1 - x0)
    def py(v): return y1 - ((v - 40) / 50) * (y1 - y0)
    def mk(pts): return " ".join(f"{'M' if i == 0 else 'L'}{px(t):.0f},{py(v):.0f}" for i, (t, v) in enumerate(pts))
    body = (axes(x0, y0, x1, y1)
            + f'<rect x="{px(2):.0f}" y="{y0}" width="{px(5)-px(2):.0f}" height="{y1-y0}" fill="{MUTED}" opacity="0.18"/>'
            + label(px(3.5), y0 + 30, "suppressed", 22, MUTED, anchor="middle")
            + f'<path d="{mk(normal)}" fill="none" stroke="{MUTED}" stroke-width="6" stroke-dasharray="12 10"/>'
            + f'<path d="{mk(treated)}" fill="none" stroke="{BLUE}" stroke-width="8" stroke-linejoin="round"/>'
            # "expected" sits below its own line and left of the crossover, so it
            # collides with neither the grey line nor the rising blue one
            + label(px(7.6), py(66), "expected", 24, MUTED, anchor="middle")
            + label(px(10) - 6, py(84) - 20, "actual", 24, BLUE, anchor="end")
            + label((x0 + x1) / 2, y1 + 52, "Time", 24, MUTED, anchor="middle")
            + f'<text x="70" y="{(y0+y1)/2}" font-family="Arial" font-size="24" font-weight="700" '
              f'fill="{MUTED}" text-anchor="middle" transform="rotate(-90 70 {(y0+y1)/2})">Height</text>')
    return frame(body, "Growth overshoots", "AFTER SUPPRESSION LIFTS")


def gh_conflict():
    """GH deck: the two conflicting results, side by side."""
    body = []
    # left: ISS meta-analysis gain
    body.append(f'<rect x="120" y="200" width="150" height="300" fill="{MUTED}" opacity="0.35"/>')
    body.append(f'<rect x="300" y="150" width="150" height="350" fill="{BLUE}"/>')
    body.append(label(195, 540, "control", 22, MUTED, anchor="middle"))
    body.append(label(375, 540, "treated", 22, INK, anchor="middle"))
    body.append(label(285, 605, "ISS meta-analyses: +4-6cm", 24, BLUE, anchor="middle"))
    # right: 1997 unfavourable outcome
    body.append(f'<rect x="590" y="170" width="150" height="330" fill="{MUTED}" opacity="0.35"/>')
    body.append(f'<rect x="770" y="250" width="150" height="250" fill="{INK}"/>')
    body.append(label(665, 540, "untreated", 22, MUTED, anchor="middle"))
    body.append(label(845, 540, "GH-treated", 22, INK, anchor="middle"))
    body.append(label(665, 155, "162.0cm", 24, MUTED, anchor="middle"))
    body.append(label(845, 235, "154.2cm", 24, INK, anchor="middle"))
    body.append(label(755, 605, "J Pediatr 1997: -8cm", 24, INK, anchor="middle"))
    body.append(f'<line x1="520" y1="140" x2="520" y2="620" stroke="{MUTED}" stroke-width="3" stroke-dasharray="8 8"/>')
    return frame("".join(body), "Both are real studies", "THE LITERATURE DISAGREES")


CHARTS = {
    "resting-zone-stem-cells/03-images/slide-03-proliferation-collapse.svg": proliferation_collapse,
    "catch-up-growth/03-images/slide-01-catchup-curve.svg": catchup_curve,
    "gh-height-myth/03-images/slide-03-conflicting-results.svg": gh_conflict,
}


def main():
    if "--list" in sys.argv:
        for p in CHARTS:
            print(p)
        return
    root = Path("content")
    for rel, fn in CHARTS.items():
        out = root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(fn())
        print(f"wrote {out}")
    print("\nSVG: crisp at any size, imports to Canva Pro, restyle via the "
          "palette constants at the top of this file.")


if __name__ == "__main__":
    main()
