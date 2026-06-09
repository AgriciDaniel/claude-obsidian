#!/usr/bin/env python3
"""wiki-link-resolve-check.py — Obsidian-accurate wikilink resolution lint.

Obsidian resolves `[[X]]` to a file literally named `X.md` (or a page whose
frontmatter `aliases:` contains `X`) — NOT to a page whose frontmatter `title:`
equals `X`. A wiki that links by human title (`[[Content Generation]]`) while its
files are slugs (`domain-content-generation.md`) with no `aliases:` therefore has
*every* internal link broken, even though a title-based checker would call them fine.

This lint models the real resolver (filename stems ∪ aliases) and reports:

  1. Unresolved links — `[[X]]` where no file is named `X.md` and no page aliases `X`.
  2. Shadowed / unreachable code pages — a Mode B code page whose own `title` does not
     resolve to *itself* (either nothing is named after it / aliases it, or the title
     resolves to a DIFFERENT file — e.g. an empty root stub shadowing the real page).

The safe fix for the Mode B class is to add `aliases: ["<title>"]` to each page (and
to make `/wiki-code-ingest` emit it going forward). Read-only; this lint never edits.

Links inside fenced/inline code and inside `_templates/`, `wiki/meta/`, and
`conventions.md` are ignored — those carry *example* link syntax, not navigation.

Usage:
  wiki-link-resolve-check.py                 # scan; human summary to stdout
  wiki-link-resolve-check.py --peek          # diagnostics only (N pages, N resolvable names)
  wiki-link-resolve-check.py --report PATH   # append a "## Link Resolution" section to PATH
  wiki-link-resolve-check.py --json          # machine-readable findings

Exit codes:
  0  — success (unresolved links are a finding, not a script error)
  2  — usage error
  3  — unreadable wiki directory
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent

CODE_PAGE_TYPES = {"module", "component", "dependency", "flow", "decision"}

# Link SOURCES to ignore (example syntax, not navigation).
EXCLUDE_SOURCE_PREFIXES = ("_templates/", "wiki/meta/")
EXCLUDE_SOURCE_FILENAMES = {"conventions.md"}

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_WIKI_UNREADABLE = 3

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
KEY_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FENCED_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def log(msg):
    print(msg, file=sys.stderr)


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text[len(m.group(0)):] if m else text
    fm = {}
    cur_key = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and cur_key is not None and isinstance(fm.get(cur_key), list):
            fm[cur_key].append(stripped[2:].strip().strip('"').strip("'"))
            continue
        km = KEY_RE.match(line)
        if km:
            key, rest = km.group(1), km.group(2).strip()
            if rest == "":
                cur_key = key
                fm[key] = []
            else:
                cur_key = None
                fm[key] = rest.strip().strip('"').strip("'")
        else:
            cur_key = None
    return fm, text[m.end():]


def normalise_list(value):
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str) and v]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            return [p.strip().strip('"').strip("'") for p in inner.split(",") if p.strip()] if inner else []
        return [s] if s else []
    return []


def link_target(raw):
    """`[[Path/Note#Heading|alias]]` → basename 'Note'."""
    t = raw.split("|")[0].split("#")[0].split("^")[0].strip()
    if not t:
        return ""
    return t.rsplit("/", 1)[-1].strip()


def is_code_page(fm):
    return (fm.get("source_type") == "code"
            or fm.get("type") in CODE_PAGE_TYPES
            or bool(fm.get("source_paths")) or bool(fm.get("code_anchors")))


def collect(vault_root):
    """Walk the vault; return (pages, by_stem, by_alias).

    pages[rel] = {stem, title, fm, body, is_code}
    by_stem[name] = [rel...]   filename-stem index (Obsidian primary resolution)
    by_alias[name] = [rel...]  alias index (Obsidian secondary resolution)
    """
    pages = {}
    by_stem = defaultdict(list)
    by_alias = defaultdict(list)
    for root, dirs, files in os.walk(vault_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.endswith(".md"):
                continue
            full = Path(root) / f
            if full.is_symlink():
                continue
            rel = full.relative_to(vault_root).as_posix()
            try:
                text = full.read_text(encoding="utf-8")
            except OSError:
                continue
            fm, body = parse_frontmatter(text)
            stem = f[:-3]
            title = (fm.get("title") or "").strip()
            rec = {"stem": stem, "title": title, "fm": fm, "body": body,
                   "is_code": is_code_page(fm)}
            pages[rel] = rec
            by_stem[stem].append(rel)
            for a in normalise_list(fm.get("aliases")):
                by_alias[a.strip()].append(rel)
    return pages, by_stem, by_alias


def resolve(target, by_stem, by_alias):
    """Return list of rel paths a `[[target]]` resolves to (filename first, then alias)."""
    return list(dict.fromkeys(by_stem.get(target, []) + by_alias.get(target, [])))


def scan(vault_root):
    pages, by_stem, by_alias = collect(vault_root)

    # 1. unresolved links from real navigation pages
    unresolved = defaultdict(list)   # target -> [source rel...]
    total_links = 0
    for rel, rec in pages.items():
        if rel.startswith(EXCLUDE_SOURCE_PREFIXES) or os.path.basename(rel) in EXCLUDE_SOURCE_FILENAMES:
            continue
        body = INLINE_CODE_RE.sub("", FENCED_RE.sub("", rec["body"]))
        for raw in WIKILINK_RE.findall(body):
            tgt = link_target(raw)
            if not tgt:
                continue
            total_links += 1
            if not resolve(tgt, by_stem, by_alias):
                unresolved[tgt].append(rel)

    # 2. code pages unreachable / shadowed by their own title
    unreachable = []   # title resolves to nothing
    shadowed = []      # title resolves, but not to this page (decoy/stub shadow)
    for rel, rec in pages.items():
        if rel.startswith(EXCLUDE_SOURCE_PREFIXES) or os.path.basename(rel) in EXCLUDE_SOURCE_FILENAMES:
            continue  # templates / meta scaffolding are not navigable pages
        if not rec["is_code"] or not rec["title"]:
            continue
        targets = resolve(rec["title"], by_stem, by_alias)
        if not targets:
            unreachable.append({"page": rel, "title": rec["title"]})
        elif rel not in targets:
            shadowed.append({"page": rel, "title": rec["title"], "resolves_to": targets})

    return {
        "pages": len(pages),
        "resolvable_names": len(set(by_stem) | set(by_alias)),
        "total_links": total_links,
        "unresolved": {k: sorted(v) for k, v in unresolved.items()},
        "unreachable": unreachable,
        "shadowed": shadowed,
    }


def render_report(res):
    lines = ["## Link Resolution",
             f"- Navigation links checked: {res['total_links']} across {res['pages']} page(s); "
             f"{res['resolvable_names']} resolvable name(s) (filenames ∪ aliases)"]

    lines.append("")
    lines.append("### Unresolved wikilinks (no file named after them, no alias)")
    if res["unresolved"]:
        lines.append(f"- {len(res['unresolved'])} distinct target(s) resolve to nothing:")
        for tgt in sorted(res["unresolved"]):
            srcs = res["unresolved"][tgt]
            head = ", ".join(f"`{s}`" for s in srcs[:4]) + (" …" if len(srcs) > 4 else "")
            lines.append(f"  - `[[{tgt}]]` ({len(srcs)} inbound) — from {head}")
    else:
        lines.append("- _All navigation links resolve._")

    lines.append("")
    lines.append("### Mode B pages unreachable by their title (add `aliases:`)")
    if res["unreachable"]:
        lines.append(f"- {len(res['unreachable'])} code page(s) cannot be reached via `[[Title]]` — "
                     f"add `aliases: [\"<title>\"]` (and fix `/wiki-code-ingest` to emit it):")
        for u in res["unreachable"]:
            lines.append(f"  - [[{u['title']}]] (`{u['page']}`)")
    else:
        lines.append("- _Every code page is reachable by its title._")

    if res["shadowed"]:
        lines.append("")
        lines.append("### Shadowed titles (title resolves to the WRONG file — likely an empty stub)")
        for s in res["shadowed"]:
            tgt = ", ".join(f"`{t}`" for t in s["resolves_to"])
            lines.append(f"  - [[{s['title']}]] should be `{s['page']}` but resolves to {tgt}. "
                         f"Delete the decoy / fix the alias.")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Obsidian-accurate wikilink resolution lint (read-only).")
    ap.add_argument("--vault", default=str(VAULT_ROOT),
                    help="vault root containing wiki/ (default: this script's vault)")
    ap.add_argument("--report", default=None, help="append a '## Link Resolution' section to this file")
    ap.add_argument("--peek", action="store_true", help="diagnostics only")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    vault_root = Path(args.vault)
    if not (vault_root / "wiki").is_dir():
        log(f"ERR: wiki dir not found: {vault_root / 'wiki'}")
        return EXIT_WIKI_UNREADABLE

    if args.peek:
        pages, by_stem, by_alias = collect(vault_root)
        code_pages = sum(1 for r in pages.values() if r["is_code"])
        print(json.dumps({
            "vault": str(vault_root),
            "pages": len(pages),
            "resolvable_names": len(set(by_stem) | set(by_alias)),
            "code_pages": code_pages,
        }))
        return EXIT_OK

    res = scan(vault_root)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"link-resolution: {res['total_links']} link(s) checked, "
              f"{len(res['unresolved'])} unresolved target(s), "
              f"{len(res['unreachable'])} code page(s) unreachable by title, "
              f"{len(res['shadowed'])} shadowed.")

    if args.report:
        rp = Path(args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with rp.open("a", encoding="utf-8") as fh:
            fh.write(f"\n<!-- wiki-link-resolve-check {stamp} -->\n")
            fh.write(render_report(res))

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
