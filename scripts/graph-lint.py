#!/usr/bin/env python3
"""graph-lint.py — wikilink graph health check for an Obsidian vault.

Scans one or more content roots for [[wikilinks]], resolves them the way
Obsidian does (basename match plus frontmatter aliases), and reports:

  - broken links: targets that resolve to no page
  - broken ``up:`` links: the frontmatter hierarchy field many vaults use
    to point a note at its parent MOC / index
  - orphan pages: pages with zero inbound links

Not every dangling link is an error. Calendar dates, planned-but-unwritten
pages, and placeholders in example blocks are legitimate. Instead of editing
those files, accept them via a whitelist file — one regex per line, ``#``
comments — and the report counts them separately as ACCEPTED-DANGLING.
Classify first (legitimate dangling vs genuinely broken), then fix only
what is genuinely broken.

Usage:
  python3 scripts/graph-lint.py                       # scan wiki/ (default)
  python3 scripts/graph-lint.py --root wiki --root notes
  python3 scripts/graph-lint.py --json report.json    # machine-readable dump
  python3 scripts/graph-lint.py --strict              # exit 1 on broken links
  python3 scripts/graph-lint.py --top 20              # show top-N broken targets

Whitelist file: .vault-meta/graph-lint-whitelist.txt (override with
--whitelist PATH). Missing whitelist is fine — nothing is accepted.

Exit codes: 0 clean (or non-strict), 1 strict violation, 2 usage error.
Hermetic: stdlib only, no network.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

FRONTMATTER_HEAD = 4096  # aliases live in frontmatter; reading 4KB is enough

ALIAS_INLINE_RE = re.compile(r"^aliases?:\s*\[([^\]]*)\]", re.M)
ALIAS_BLOCK_RE = re.compile(r"^aliases?:\s*\n((?:\s+-\s+.*\n?)+)", re.M)
ALIAS_ITEM_RE = re.compile(r"^\s+-\s+(.*)$", re.M)
LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:[#\|][^\]]*)?\]\]")
UP_RE = re.compile(r'^up:\s*"?\[\[([^\]\|#]+)', re.M)


def collect_files(roots):
    files = []
    for root in roots:
        if not os.path.isdir(root):
            print(f"WARN: root not found, skipping: {root}", file=sys.stderr)
            continue
        # followlinks stays False (the default) on purpose: a vault with a
        # symlink loop must not hang the lint.
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in filenames:
                if name.endswith(".md"):
                    files.append(os.path.join(dirpath, name).replace(os.sep, "/"))
    return sorted(files)


def parse_aliases(head):
    """Extract frontmatter aliases: inline list or YAML block list."""
    aliases = []
    m = ALIAS_INLINE_RE.search(head)
    if m:
        for item in m.group(1).split(","):
            item = item.strip().strip("\"'")
            if item:
                aliases.append(item)
    m = ALIAS_BLOCK_RE.search(head)
    if m:
        for item in ALIAS_ITEM_RE.findall(m.group(1)):
            item = item.strip().strip("\"'")
            if item:
                aliases.append(item)
    return aliases


def build_resolver(files):
    """Map every resolvable name (basename or alias) to its file(s)."""
    names = {}
    for f in files:
        base = os.path.basename(f)[:-3]
        names.setdefault(base, []).append(f)
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                head = fh.read(FRONTMATTER_HEAD)
        except OSError:
            continue
        for alias in parse_aliases(head):
            names.setdefault(alias, []).append(f)
    return names


def load_whitelist(path):
    patterns = []
    if not path or not os.path.exists(path):
        return patterns
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#")[0].strip()
            if not line:
                continue
            try:
                patterns.append(re.compile(line))
            except re.error as exc:
                print(f"WARN: bad whitelist regex skipped: {line!r} ({exc})",
                      file=sys.stderr)
    return patterns


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Wikilink graph health check for an Obsidian vault.")
    ap.add_argument("--root", action="append", default=None, metavar="DIR",
                    help="content root to scan (repeatable; default: wiki)")
    ap.add_argument("--whitelist", default=".vault-meta/graph-lint-whitelist.txt",
                    metavar="PATH", help="accepted-dangling regex file")
    ap.add_argument("--json", default=None, metavar="PATH",
                    help="write full machine-readable report to PATH")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any broken link or broken up: remains")
    ap.add_argument("--top", type=int, default=25, metavar="N",
                    help="show top-N broken targets (default 25)")
    args = ap.parse_args(argv)

    roots = args.root or ["wiki"]
    files = collect_files(roots)
    if not files:
        print(f"ERR: no .md files under roots: {', '.join(roots)}",
              file=sys.stderr)
        return 2

    names = build_resolver(files)
    whitelist = load_whitelist(args.whitelist)

    def resolve(target):
        target = target.strip()
        # Obsidian resolves path-style links by their last segment too.
        return names.get(target.split("/")[-1]) or names.get(target)

    def whitelisted(target):
        tail = target.strip().split("/")[-1]
        return any(p.search(tail) for p in whitelist)

    inbound = {f: 0 for f in files}
    broken = {}
    accepted = 0
    total_links = up_links = up_resolved = 0

    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for m in UP_RE.finditer(text):
            up_links += 1
            if resolve(m.group(1)):
                up_resolved += 1
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            total_links += 1
            candidates = resolve(target)
            if candidates:
                for c in candidates:
                    if c != f:
                        inbound[c] += 1
            elif whitelisted(target):
                accepted += 1
            else:
                broken.setdefault(f, []).append(target)

    orphans = [f for f in files if inbound[f] == 0]
    orphan_content = [f for f in orphans
                      if not os.path.basename(f).startswith("_")]
    orphan_system = [f for f in orphans if os.path.basename(f).startswith("_")]
    broken_instances = sum(len(v) for v in broken.values())
    broken_up = up_links - up_resolved

    print("SCANNED FILES:", len(files))
    print("TOTAL WIKILINKS:", total_links)
    print("UP LINKS:", up_links, "RESOLVED:", up_resolved,
          "BROKEN_UP:", broken_up)
    print("FILES WITH BROKEN LINKS:", len(broken),
          "TOTAL BROKEN INSTANCES:", broken_instances,
          "| ACCEPTED-DANGLING:", accepted)
    print("ORPHANS total:", len(orphans),
          "| content:", len(orphan_content),
          "| index/system:", len(orphan_system))

    if broken:
        counter = Counter()
        for targets in broken.values():
            for t in targets:
                counter[t.split("/")[-1]] += 1
        print("\nTOP BROKEN TARGETS:")
        for target, n in counter.most_common(args.top):
            print("  %4d  %s" % (n, target))

    if args.json:
        report = {
            "orphans": orphans,
            "orphan_content": orphan_content,
            "orphan_system": orphan_system,
            "broken": broken,
            "stats": {
                "files": len(files),
                "links": total_links,
                "up": up_links,
                "up_resolved": up_resolved,
                "broken_up": broken_up,
                "broken_files": len(broken),
                "broken_instances": broken_instances,
                "accepted_dangling": accepted,
                "orphans": len(orphans),
                "orphan_content": len(orphan_content),
            },
        }
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
        print(f"\nJSON report: {args.json}")

    if args.strict and (broken_instances or broken_up):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
