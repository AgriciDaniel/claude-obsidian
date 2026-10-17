#!/usr/bin/env python3
"""Flag deck claims that need a verbatim source quote and don't have one.

Built after a real failure. The Gebhardt mandible deck said nandrolone
"altered" mandibular growth, hedged as "not increased, not improved". The paper
actually reports +27.2% vs +24.5% length in juveniles and +4.7% vs +0.3% in
adults: it clearly grew. The deck was written from a one-line vault summary
that said "altered", never from the PDF. 20k views went out saying roughly the
opposite of the source.

The failure is structural, not careless: paper -> one-line summary -> deck loses
direction and magnitude in the middle. So any slide carrying a number or a
direction has to be traceable to a sentence in the actual paper.

Each deck gets 07-claims.md:

    ## slide 3
    CLAIM: length rose 27.2% vs 24.5% in juveniles
    QUOTE: "Mandibular length (variable 2) increased by an average of 27.2%
      (15.8 mm) in the juvenile E animals and by an average of 24.5% (14.0 mm)
      in the C animals."
    SOURCE: Gebhardt & Pancherz 2003, p437

Usage:
    python3 scripts/verify-claims.py                       # all decks
    python3 scripts/verify-claims.py content/<deck>
"""
import glob
import os
import re
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

# A slide needs backing if it asserts a number or a direction of effect.
NUMERIC = re.compile(r"\b\d+(\.\d+)?\s*(%|mm|cm|kg|mg|ng|iu|fold|x\b)|\b\d+\.\d+\b")
DIRECTION = re.compile(
    r"\b(increas|decreas|reduc|rose|fell|higher|lower|longer|shorter|greater|"
    r"grew|shrank|improv|worsen|prevent|accelerat|delay|suppress|doubl|halv)", re.I)


def audit(deck):
    csv_path = os.path.join(deck, "04-slides.csv")
    if not os.path.exists(csv_path):
        return None
    import csv as _csv
    rows = list(_csv.DictReader(open(csv_path)))

    claims_path = os.path.join(deck, "07-claims.md")
    verified = set()
    if os.path.exists(claims_path):
        text = open(claims_path).read()
        for m in re.finditer(r"##\s*slide\s*(\d+)", text, re.I):
            block = text[m.end():text.find("## slide", m.end()) if "## slide" in text[m.end():] else len(text)]
            if "QUOTE:" in block and "SOURCE:" in block:
                verified.add(int(m.group(1)))

    needs, missing = [], []
    for i, r in enumerate(rows, 1):
        body = f"{r.get('body','')} {r.get('punch','')}"
        if NUMERIC.search(body) or DIRECTION.search(body):
            needs.append(i)
            if i not in verified:
                missing.append(i)
    return len(rows), needs, missing


def main():
    targets = sys.argv[1:] or sorted(glob.glob("content/*/"))
    targets = [t for t in targets if os.path.isdir(t)]
    total_missing = 0
    print(f"{'deck':<40}{'slides':>7}{'need':>6}{'unverified':>12}")
    print("-" * 65)
    for t in targets:
        res = audit(t.rstrip("/"))
        if not res:
            continue
        n, needs, missing = res
        total_missing += len(missing)
        mark = "" if not missing else ("  <-- " + ",".join(map(str, missing)))
        print(f"{os.path.basename(t.rstrip('/')):<40}{n:>7}{len(needs):>6}{len(missing):>12}{mark}")
    print(f"\n{total_missing} slides assert a number or a direction with no verbatim quote behind them.")
    print("Priority: any deck you are about to post. A wrong direction reads as a lie, not a nuance.")


if __name__ == "__main__":
    main()
