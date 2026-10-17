#!/usr/bin/env python3
"""Map each deck's cited sources to the actual PDF path in .raw/Studies.

The briefs cite studies by name and vault wikilink, which is fine for reading
but useless for opening the paper. This resolves each citation to a real file
path so a deck links straight through to the PDF it rests on.

Writes content/<deck>/06-sources.md.

Usage:
    python3 scripts/link-deck-sources.py
"""
import glob
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import argparse
from claude_obsidian.paths import VaultSelectionError, resolve_vault_root


def vault_root() -> Path:
    """Resolve the vault to act on, failing closed when there is none.

    Never derive paths from __file__: under the installed product tree that
    resolves to the plugin directory, and writing there corrupts the install.
    """
    return resolve_vault_root(plugin_root=PLUGIN_ROOT).root

STUDIES = ".raw/Studies"
VAULT_SOURCES = "wiki/sources"


def norm(s):
    """Lowercase alnum-only, for tolerant matching across naming styles."""
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def build_index():
    """PDF basename (normalised) -> real path."""
    idx = []
    for p in glob.glob(f"{STUDIES}/**/*.pdf", recursive=True):
        if "DUPLICATE" in p:
            continue
        idx.append((norm(os.path.splitext(os.path.basename(p))[0]), p))
    return idx


def source_note_title(slug):
    """A vault source note's frontmatter title, which matches the PDF better
    than the slug does."""
    p = os.path.join(VAULT_SOURCES, slug + ".md")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r'title:\s*"?(.+?)"?\s*$', line)
            if m:
                return m.group(1)
    return None


def best_match(query, idx, floor=0.55):
    q = norm(query)
    if not q:
        return None, 0.0
    best, score = None, 0.0
    for cand, path in idx:
        r = SequenceMatcher(None, q, cand).ratio()
        # a strong containment signal beats a mediocre global ratio
        if q in cand or cand in q:
            r = max(r, 0.85)
        if r > score:
            best, score = path, r
    return (best, score) if score >= floor else (None, score)


def main():
    parser = argparse.ArgumentParser(description="Map each deck's cited sources to the actual PDF path in .raw/Studies")
    parser.add_argument("paths", nargs="*", help="files or globs to act on")
    args = parser.parse_args()
    idx = build_index()
    if not idx:
        sys.exit(f"no PDFs found under {STUDIES}")
    print(f"indexed {len(idx)} PDFs\n")

    for brief in sorted(glob.glob("content/*/01-research.md")):
        deck = os.path.basename(os.path.dirname(brief))
        text = open(brief, encoding="utf-8", errors="replace").read()
        links = re.findall(r"\[\[([^\]|]+)", text)
        seen, rows = set(), []
        for slug in links:
            slug = slug.strip()
            if slug in seen:
                continue
            seen.add(slug)
            title = source_note_title(slug)
            path, score = best_match(title or slug, idx)
            if not path and title:
                path, score = best_match(slug, idx)
            rows.append((slug, title, path, score))

        if not rows:
            continue

        out = [f"# Source files — {deck}", "",
               "Each citation in `01-research.md` resolved to the actual PDF in",
               "your library. Paths are relative to the vault root.", ""]
        hit = [r for r in rows if r[2]]
        miss = [r for r in rows if not r[2]]

        if hit:
            out += ["## Papers you have", ""]
            for slug, title, path, score in hit:
                conf = "high" if score > 0.8 else "check"
                out.append(f"- **{title or slug}**")
                out.append(f"  `{path}`  _(match: {conf})_")
            out.append("")
        if miss:
            out += ["## Cited but not found in `.raw/Studies`", "",
                    "Either not downloaded, or filed under a different name.", ""]
            for slug, title, _, score in miss:
                out.append(f"- {title or slug}  _(best score {score:.2f})_")
            out.append("")

        with open(f"content/{deck}/06-sources.md", "w") as fh:
            fh.write("\n".join(out))
        print(f"{deck:<38} {len(hit)} found / {len(miss)} missing")


if __name__ == "__main__":
    main()
