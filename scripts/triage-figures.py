"""Triage extracted figures so the vault does not drown in stubs.

A figure earns a top-level page only if it has a printed caption AND a
classified display type. Everything else keeps its image but its stub moves
to wiki/figures/_unreviewed/, and each paper gets one index page instead.
"""
import argparse
import re, shutil
from pathlib import Path
from collections import defaultdict
from datetime import date
import sys

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

if __name__ == "__main__":
    argparse.ArgumentParser(description="Triage extracted figures so the vault does not drown in stubs").parse_args()

    ROOT  = Path(__file__).resolve().parent.parent
    PAGES = ROOT/"wiki/figures"
    UNREV = PAGES/"_unreviewed"
    UNREV.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    def fm(txt, key):
        m = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', txt, re.M)
        return (m.group(1) if m else "").strip()

    kept, moved = 0, 0
    by_type = defaultdict(int); by_paper = defaultdict(list)

    for p in sorted(PAGES.glob("fig-*.md")):
        txt = p.read_text()
        shows  = fm(txt, "shows")
        dtype  = fm(txt, "display_type")
        paper  = fm(txt, "source_pdf")
        # hand-written specs keep their description in the body, not frontmatter
        hand = "**Redraw as:**" in txt and "_what to draw" not in txt
        good = hand or (bool(shows) and dtype and dtype != "uncategorised")
        by_paper[paper].append((p.stem, dtype, shows[:120], good))
        if good:
            kept += 1; by_type[dtype] += 1
        else:
            shutil.move(str(p), str(UNREV/p.name)); moved += 1

    # one index page per paper, so the images stay findable without 2700 stubs
    IDX = PAGES/"_by-paper"; IDX.mkdir(exist_ok=True)
    for paper, figs in by_paper.items():
        if not paper: continue
        slug = re.sub(r"[^a-z0-9]+","-",paper.lower()).strip("-")[:70]
        L = [f"---\ntype: figure-index\npaper: \"{paper}\"\nfigures: {len(figs)}\n"
             f"reviewed: {sum(1 for f in figs if f[3])}\ncreated: {today}\nupdated: {today}\n"
             f"tags: [figure-index]\n---\n", f"# Figures in {paper}\n",
             "| Figure | Type | Caption |", "|---|---|---|"]
        for stem, dt, sh, good in sorted(figs):
            mark = "" if good else " _(unreviewed)_"
            L.append(f"| [[{stem}]] | {dt}{mark} | {sh or '—'} |")
        (IDX/f"{slug}.md").write_text("\n".join(L)+"\n")

    L = [f"---\ntype: meta\ntitle: \"Figure library\"\nfigures_total: {kept+moved}\n"
         f"reviewed: {kept}\nunreviewed: {moved}\ncreated: {today}\nupdated: {today}\n"
         f"tags: [meta, figures]\n---\n", "# Figure library\n",
         f"**{kept+moved}** figures extracted from the study PDFs. "
         f"**{kept}** carry a printed caption and a classified display type and sit in this folder. "
         f"**{moved}** are in `_unreviewed/` awaiting a one-line `shows:` description.\n",
         "Images live in `_attachments/figures/<paper>/`. Per-paper indexes are in `_by-paper/`.\n",
         "## By display type\n", "| Type | Count | Reach for it when |", "|---|---|---|"]
    USE = {"mechanism-schematic":"you need a pathway slide","dose-response":"arguing more is not better",
     "time-course":"onset, decay, recovery","histology":"a tissue-level claim",
     "anatomical":"showing where a thing is","comparison-bars":"group A vs group B",
     "survival":"long-run risk","forest-plot":"summarising a literature",
     "blot-gel-flow":"molecular evidence (rarely reads on a phone)"}
    for k,v in sorted(by_type.items(), key=lambda x:-x[1]):
        L.append(f"| `{k}` | {v} | {USE.get(k,'—')} |")
    L += ["\n> [!warning] Licence",
          "> These are publisher figures. Use them to decide **what to draw**, not to republish.",
          "> Each page carries a `redraw_spec` field for that purpose.\n"]
    (PAGES/"_index.md").write_text("\n".join(L)+"\n")

    print(f"kept {kept} captioned+classified · moved {moved} to _unreviewed/ · {len(by_paper)} paper indexes")
    for k,v in sorted(by_type.items(), key=lambda x:-x[1]): print(f"  {k:<24}{v:>6}")
