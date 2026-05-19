#!/usr/bin/env python3
"""Deterministic bilingual-terminology lint checks.

Reads every page under <wiki-root> and applies five checks:

  1. dnt_class set but aliases has < 2 entries          (error)
  2. dnt_class set but page absent from termbase index  (warn)
  3. termbase index entry points to a non-existent page (warn)
  4. termbase entry points to a page that no longer has dnt_class (warn)
  5. dnt_class value is not in the allowed set          (error)

Output: a Markdown report on stdout. Lines starting with `ERROR`, `WARN`,
or `INFO` are machine-parseable for downstream tooling. Exit code is 0
even when findings exist — lint *surfaces* problems, does not fail builds.

Usage:
  scripts/lint-terminology.py [wiki-root]
  scripts/lint-terminology.py wiki

Optional flags:
  --json     Emit findings as JSON instead of Markdown.
  --strict   Exit 2 when any ERROR finding is emitted.

See docs/bilingual-terminology-policy.md for the policy this enforces.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterator

VALID_DNT = {"term-of-art", "eigenname", "coined", "hybrid"}
TERMBASE_REL = "meta/termbase.md"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
SCALAR_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.+?)\s*$")
LIST_HEADER_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$")
LIST_ITEM_RE = re.compile(r"^\s*-\s*(.+?)\s*$")
TERMBASE_ROW_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


@dataclass
class Finding:
    severity: str  # ERROR | WARN | INFO
    check: str
    path: str
    message: str
    suggestion: str = ""


@dataclass
class PageFrontmatter:
    path: Path
    dnt_class: str | None = None
    lang: str | None = None
    aliases: list[str] = field(default_factory=list)
    raw_fields: dict[str, str] = field(default_factory=dict)


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
    """Return (scalars, aliases_list) from the YAML-ish frontmatter block."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, []

    block = match.group(1).splitlines()
    scalars: dict[str, str] = {}
    aliases: list[str] = []
    current_list: str | None = None

    for raw in block:
        if not raw.strip():
            current_list = None
            continue

        item_match = LIST_ITEM_RE.match(raw)
        if item_match and current_list:
            value = item_match.group(1).strip().strip('"').strip("'")
            if current_list == "aliases":
                aliases.append(value)
            continue

        header_match = LIST_HEADER_RE.match(raw)
        if header_match:
            current_list = header_match.group(1)
            continue

        current_list = None
        scalar_match = SCALAR_RE.match(raw)
        if scalar_match:
            key, value = scalar_match.group(1), scalar_match.group(2)
            scalars[key] = value.strip().strip('"').strip("'")

    return scalars, aliases


def load_page(path: Path) -> PageFrontmatter:
    text = path.read_text(encoding="utf-8", errors="replace")
    scalars, aliases = parse_frontmatter(text)
    return PageFrontmatter(
        path=path,
        dnt_class=scalars.get("dnt_class"),
        lang=scalars.get("lang"),
        aliases=aliases,
        raw_fields=scalars,
    )


def iter_pages(root: Path) -> Iterator[Path]:
    for p in root.rglob("*.md"):
        if "_templates" in p.parts:
            continue
        if "folds" in p.parts:
            continue
        yield p


def parse_termbase(termbase_path: Path) -> set[str]:
    """Return the set of wikilink targets referenced from termbase.md."""
    if not termbase_path.exists():
        return set()
    text = termbase_path.read_text(encoding="utf-8", errors="replace")
    return set(TERMBASE_ROW_RE.findall(text))


def check_page(page: PageFrontmatter, termbase_targets: set[str], wiki_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    rel = page.path.relative_to(wiki_root).as_posix()

    if page.dnt_class is None:
        return findings

    # Check 5: invalid value
    if page.dnt_class not in VALID_DNT:
        findings.append(Finding(
            severity="ERROR",
            check="invalid-dnt-class",
            path=rel,
            message=f"dnt_class={page.dnt_class!r} is not one of {sorted(VALID_DNT)}",
            suggestion="Set dnt_class to one of: term-of-art, eigenname, coined, hybrid",
        ))

    # Check 1: aliases must carry both native + English gloss
    if len(page.aliases) < 2:
        findings.append(Finding(
            severity="ERROR",
            check="missing-alias",
            path=rel,
            message=f"dnt_class is set but aliases has {len(page.aliases)} entries (need >= 2)",
            suggestion="Add both the native form and an English gloss to aliases",
        ))

    # Check 2: page must be linked from termbase index
    stem = page.path.stem
    if stem not in termbase_targets:
        findings.append(Finding(
            severity="WARN",
            check="termbase-drift",
            path=rel,
            message=f"Page has dnt_class but is not listed in wiki/{TERMBASE_REL}",
            suggestion=f"Add a row to the termbase index linking to [[{stem}]]",
        ))

    return findings


def check_termbase_orphans(
    termbase_targets: set[str],
    all_pages: list[PageFrontmatter],
    wiki_root: Path,
) -> list[Finding]:
    findings: list[Finding] = []
    pages_by_stem = {p.path.stem: p for p in all_pages}
    for target in sorted(termbase_targets):
        page = pages_by_stem.get(target)
        if page is None:
            findings.append(Finding(
                severity="WARN",
                check="orphan-termbase-entry",
                path=f"{TERMBASE_REL}",
                message=f"Termbase links to [[{target}]] but no such page exists",
                suggestion="Remove the row or create the page",
            ))
        elif page.dnt_class is None:
            findings.append(Finding(
                severity="WARN",
                check="orphan-termbase-entry",
                path=f"{TERMBASE_REL}",
                message=f"Termbase links to [[{target}]] but page has no dnt_class",
                suggestion="Restore dnt_class on the page, or remove the termbase row",
            ))
    return findings


def format_markdown(findings: list[Finding]) -> str:
    if not findings:
        return "# Bilingual Terminology Lint\n\nNo findings.\n"
    lines = ["# Bilingual Terminology Lint", ""]
    by_severity: dict[str, list[Finding]] = {"ERROR": [], "WARN": [], "INFO": []}
    for f in findings:
        by_severity[f.severity].append(f)
    for sev in ("ERROR", "WARN", "INFO"):
        bucket = by_severity[sev]
        if not bucket:
            continue
        lines.append(f"## {sev} ({len(bucket)})")
        lines.append("")
        for f in bucket:
            lines.append(f"- **{f.check}** `{f.path}` — {f.message}")
            if f.suggestion:
                lines.append(f"  - Suggest: {f.suggestion}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default="wiki", help="Wiki root directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument("--strict", action="store_true", help="Exit 2 on any ERROR")
    args = parser.parse_args(argv)

    wiki_root = Path(args.root).resolve()
    if not wiki_root.is_dir():
        print(f"ERROR: {wiki_root} is not a directory", file=sys.stderr)
        return 2

    termbase_path = wiki_root / TERMBASE_REL
    termbase_targets = parse_termbase(termbase_path)
    pages = [load_page(p) for p in iter_pages(wiki_root)]

    findings: list[Finding] = []
    for page in pages:
        findings.extend(check_page(page, termbase_targets, wiki_root))
    findings.extend(check_termbase_orphans(termbase_targets, pages, wiki_root))

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2, ensure_ascii=False))
    else:
        print(format_markdown(findings))

    if args.strict and any(f.severity == "ERROR" for f in findings):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
