#!/usr/bin/env python3
"""
provenance-check.py — DragonScale Mechanism 5 validator.

Walks a wiki page or directory. For each non-meta page, checks that every body
paragraph is followed by either a Provenance Block (callout `[!provenance]`)
or an exemption tag (`[derived]` / `[conjecture]` / `[editorial]`). Validates
that each Provenance Block points at a real source page and a paragraph index
that exists in the underlying `.raw/` source.

See `skills/wiki-provenance/SKILL.md` for the full semantic spec.

Usage
-----
  ./scripts/provenance-check.py <path>            single file or directory
  ./scripts/provenance-check.py --missing <path>  paragraphs lacking provenance
  ./scripts/provenance-check.py --broken <path>   dangling pointers only
  ./scripts/provenance-check.py --audit <path>    vault-wide coverage report
  ./scripts/provenance-check.py --json <path>     machine-readable output

Exit codes
----------
  0  no errors found (warnings and informationals are allowed)
  1  at least one error found
  2  vault root could not be located above the target
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

# Match a YAML frontmatter block at the start of a document.
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

# Pointer line inside a Provenance Block (after the leading ">" is stripped).
# Captures: source-page, optional ^block-id, optional paragraph index, quote.
POINTER_RE = re.compile(
    r"^\s*-\s*"
    r"\[\[(?P<source>[^\]\|\#]+)(?:#\^(?P<block>[^\]\|]+))?(?:\|[^\]]+)?\]\]"
    r"(?:\s+paragraph\s+(?P<para>\d+))?"
    r'\s*:\s*"(?P<quote>[^"]+)"',
    re.MULTILINE,
)

EXEMPT_TAGS = ("[derived]", "[conjecture]", "[editorial]")

# Always excluded from provenance checking, regardless of frontmatter.
ALWAYS_EXCLUDED_FILENAMES = {
    "_index.md",
    "index.md",
    "log.md",
    "hot.md",
    "overview.md",
    "dashboard.md",
    "Wiki Map.md",
    "getting-started.md",
}
ALWAYS_EXCLUDED_PATH_PARTS = {"folds", "meta"}

# Default `provenance:` setting for each `type:` if not explicit.
REQUIRES_BY_TYPE = {
    "source": "required",
    "concept": "required",
    "comparison": "required",
    "question": "required",
    "entity": "required",
    "meta": "exempt",
    "fold": "exempt",
}

ROLLOUT_DATE = "2026-04-23"


@dataclass
class Issue:
    path: str
    line: int
    issue: str
    severity: str  # "error" | "warning" | "info"


@dataclass
class FileReport:
    path: str
    page_type: Optional[str]
    page_provenance: str
    paragraphs_total: int = 0
    paragraphs_covered: int = 0
    cover_provenance: int = 0
    cover_derived: int = 0
    cover_conjecture: int = 0
    cover_editorial: int = 0
    issues: list = field(default_factory=list)


# ---------- frontmatter / body parsing ----------

def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("-"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def get_body_and_offset(text: str):
    """Return (body, line_offset) where line_offset is the body's first line number."""
    m = FRONTMATTER_RE.match(text)
    if m:
        offset = text[: m.end()].count("\n")
        return text[m.end():], offset
    return text, 0


def is_path_excluded(rel_path: Path) -> bool:
    if rel_path.name in ALWAYS_EXCLUDED_FILENAMES:
        return True
    return bool(set(rel_path.parts) & ALWAYS_EXCLUDED_PATH_PARTS)


# ---------- block splitter ----------

CODE_FENCE_RE = re.compile(r"^(`{3,}|~{3,})")


def split_into_blocks(body: str):
    """
    Walk lines and emit (start_line, end_line, kind, content) for each block.
    kind is one of: paragraph, codefence, callout, blank.
    Line numbers are 0-based offsets within `body`; callers add the frontmatter offset.
    """
    blocks = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            blocks.append((i, i, "blank", ""))
            i += 1
            continue

        m = CODE_FENCE_RE.match(stripped)
        if m:
            fence = m.group(1)
            start = i
            i += 1
            while i < len(lines):
                inner = CODE_FENCE_RE.match(lines[i].strip())
                if (
                    inner
                    and inner.group(1)[0] == fence[0]
                    and len(inner.group(1)) >= len(fence)
                ):
                    break
                i += 1
            end = i if i < len(lines) else len(lines) - 1
            blocks.append((start, end, "codefence", "\n".join(lines[start: end + 1])))
            i += 1
            continue

        if line.lstrip().startswith(">"):
            start = i
            content = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                content.append(lines[i])
                i += 1
            blocks.append((start, i - 1, "callout", "\n".join(content)))
            continue

        # Paragraph: consume until blank or block-starter
        start = i
        para_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if not nxt.strip():
                break
            if nxt.lstrip().startswith(">"):
                break
            if CODE_FENCE_RE.match(nxt.strip()):
                break
            para_lines.append(nxt)
            i += 1
        blocks.append((start, i - 1, "paragraph", "\n".join(para_lines)))

    return blocks


def is_provenance_callout(callout_content: str) -> bool:
    first_line = callout_content.split("\n", 1)[0].strip()
    return bool(re.match(r"^>\s*\[!provenance\]", first_line, re.IGNORECASE))


def parse_pointers(callout_content: str) -> list:
    cleaned = "\n".join(re.sub(r"^>\s?", "", l) for l in callout_content.splitlines())
    cleaned = re.sub(
        r"^\s*\[!provenance\][^\n]*\n",
        "",
        cleaned,
        count=1,
        flags=re.IGNORECASE,
    )
    pointers = []
    for m in POINTER_RE.finditer(cleaned):
        pointers.append(
            {
                "source": m.group("source").strip(),
                "block_id": m.group("block"),
                "paragraph": int(m.group("para")) if m.group("para") else None,
                "quote": m.group("quote"),
            }
        )
    return pointers


def matches_exemption_tag(content: str) -> Optional[str]:
    stripped = content.strip()
    for tag in EXEMPT_TAGS:
        if stripped == tag or stripped.endswith("\n" + tag):
            return tag
    return None


# ---------- source resolution ----------

def find_source_paragraph(
    source_page: str, paragraph_idx: int, vault_root: Path
):
    """Locate the cited source paragraph in the underlying `.raw/` file.

    Returns (in_range, paragraph_text). in_range is False if the source page
    can't be found, has no `raw_file` frontmatter, the raw file is missing,
    or the paragraph index is out of bounds.
    """
    candidates = []
    sources_dir = vault_root / "wiki" / "sources"
    if sources_dir.exists():
        candidates.extend(sources_dir.glob(f"{source_page}.md"))
    if not candidates:
        candidates.extend((vault_root / "wiki").rglob(f"{source_page}.md"))
    if not candidates:
        return False, None

    fm = parse_frontmatter(candidates[0].read_text(encoding="utf-8"))
    raw_rel = fm.get("raw_file")
    if not raw_rel:
        return False, None

    raw_path = vault_root / raw_rel
    if not raw_path.exists():
        return False, None

    raw_text = raw_path.read_text(encoding="utf-8")
    body, _ = get_body_and_offset(raw_text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if paragraph_idx < 0 or paragraph_idx >= len(paragraphs):
        return False, None
    return True, paragraphs[paragraph_idx]


# ---------- per-file check ----------

def check_file(path: Path, vault_root: Path) -> FileReport:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    page_type = fm.get("type")
    page_provenance = fm.get("provenance") or REQUIRES_BY_TYPE.get(page_type, "optional")
    rel_path = path.relative_to(vault_root).as_posix()
    report = FileReport(path=rel_path, page_type=page_type, page_provenance=page_provenance)

    if page_provenance == "exempt" or is_path_excluded(path.relative_to(vault_root)):
        return report

    body, offset = get_body_and_offset(text)
    blocks = split_into_blocks(body)
    is_legacy = (fm.get("created", "") or "") < ROLLOUT_DATE

    for idx, (start, _end, kind, content) in enumerate(blocks):
        if kind != "paragraph":
            continue

        # Skip headings
        first_line = content.lstrip().split("\n", 1)[0]
        if first_line.lstrip().startswith("#"):
            continue

        # Self-tagged paragraph (tag is the last line, no blank between)
        ex_tag = matches_exemption_tag(content)
        if ex_tag:
            report.paragraphs_total += 1
            report.paragraphs_covered += 1
            _bump_cover(report, ex_tag)
            continue

        # Look for the next non-blank block to determine coverage
        nxt = idx + 1
        while nxt < len(blocks) and blocks[nxt][2] == "blank":
            nxt += 1

        report.paragraphs_total += 1

        if nxt < len(blocks):
            n_kind, n_content = blocks[nxt][2], blocks[nxt][3]

            # Provenance Block coverage
            if n_kind == "callout" and is_provenance_callout(n_content):
                report.paragraphs_covered += 1
                report.cover_provenance += 1
                _validate_pointers(
                    report, rel_path, vault_root, offset, blocks[nxt][0], n_content
                )
                continue

            # Tag-only paragraph follows
            if n_kind == "paragraph":
                tag = matches_exemption_tag(n_content)
                if tag:
                    report.paragraphs_covered += 1
                    _bump_cover(report, tag)
                    continue

        # Uncovered: emit issue with severity per spec
        if page_provenance == "required":
            severity = "error" if page_type == "source" else "warning"
        elif page_provenance == "optional":
            severity = "info"
        else:
            severity = "info"
        if is_legacy:
            severity = "info"

        report.issues.append(
            Issue(
                path=rel_path,
                line=offset + start + 1,
                issue="Paragraph lacks provenance and exemption tag",
                severity=severity,
            )
        )

    return report


def _bump_cover(report: FileReport, tag: str) -> None:
    if tag == "[derived]":
        report.cover_derived += 1
    elif tag == "[conjecture]":
        report.cover_conjecture += 1
    elif tag == "[editorial]":
        report.cover_editorial += 1


def _validate_pointers(report, rel_path, vault_root, body_offset, callout_start, callout_content):
    pointers = parse_pointers(callout_content)
    if not pointers:
        report.issues.append(
            Issue(
                path=rel_path,
                line=body_offset + callout_start + 1,
                issue="Provenance Block has no parseable pointers",
                severity="error",
            )
        )
        return

    for p in pointers:
        if p["paragraph"] is None and p["block_id"] is None:
            report.issues.append(
                Issue(
                    path=rel_path,
                    line=body_offset + callout_start + 1,
                    issue=f"Pointer to [[{p['source']}]] has no paragraph index or block ID",
                    severity="warning",
                )
            )
            continue

        if p["paragraph"] is not None:
            in_range, src_text = find_source_paragraph(p["source"], p["paragraph"], vault_root)
            if not in_range:
                report.issues.append(
                    Issue(
                        path=rel_path,
                        line=body_offset + callout_start + 1,
                        issue=(
                            f"[[{p['source']}]] paragraph {p['paragraph']} "
                            "is missing or out of range"
                        ),
                        severity="error",
                    )
                )
            elif src_text and p["quote"] not in src_text:
                report.issues.append(
                    Issue(
                        path=rel_path,
                        line=body_offset + callout_start + 1,
                        issue=(
                            f"Quote drift: cited quote not found in "
                            f"[[{p['source']}]] paragraph {p['paragraph']}"
                        ),
                        severity="warning",
                    )
                )


# ---------- driver ----------

def walk(target: Path, vault_root: Path) -> list:
    if target.is_file():
        return [check_file(target, vault_root)]
    reports = []
    for f in target.rglob("*.md"):
        rel = f.relative_to(vault_root)
        if is_path_excluded(rel):
            continue
        reports.append(check_file(f, vault_root))
    return reports


def find_vault_root(target: Path) -> Optional[Path]:
    cur = target if target.is_dir() else target.parent
    while True:
        if (cur / "wiki").is_dir() and (cur / ".raw").is_dir():
            return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


def print_audit(reports: list, vault_root: Path) -> None:
    total = len(reports)
    requiring = [r for r in reports if r.page_provenance == "required"]
    para_total = sum(r.paragraphs_total for r in requiring)
    para_covered = sum(r.paragraphs_covered for r in requiring)
    via_prov = sum(r.cover_provenance for r in requiring)
    via_d = sum(r.cover_derived for r in requiring)
    via_c = sum(r.cover_conjecture for r in requiring)
    via_e = sum(r.cover_editorial for r in requiring)
    broken = sum(
        1
        for r in reports
        for i in r.issues
        if "out of range" in i.issue or "is missing" in i.issue
    )
    pct = (para_covered / para_total * 100) if para_total else 0.0
    print(f"provenance audit: {vault_root}/wiki")
    print(f"  pages scanned:                  {total}")
    print(f"  pages requiring coverage:       {len(requiring)}")
    print(f"  paragraphs requiring coverage:  {para_total}")
    print(f"  paragraphs covered:             {para_covered}  ({pct:.1f}%)")
    print(f"    via provenance block:         {via_prov}")
    print(f"    via [derived]:                {via_d}")
    print(f"    via [conjecture]:             {via_c}")
    print(f"    via [editorial]:              {via_e}")
    print(f"  paragraphs uncovered:           {para_total - para_covered}")
    print(f"  broken pointers:                {broken}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path", help="file or directory to check")
    ap.add_argument("--missing", action="store_true", help="paragraphs lacking provenance")
    ap.add_argument("--broken", action="store_true", help="dangling pointers only")
    ap.add_argument("--audit", action="store_true", help="vault-wide coverage report")
    ap.add_argument("--json", dest="as_json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    target = Path(args.path).resolve()
    vault_root = find_vault_root(target)
    if vault_root is None:
        print(f"ERR: vault root not found above {target}", file=sys.stderr)
        sys.exit(2)

    reports = walk(target, vault_root)

    if args.audit:
        print_audit(reports, vault_root)
        return

    rows = []
    for r in reports:
        for iss in r.issues:
            if args.missing and "lacks provenance" not in iss.issue:
                continue
            if args.broken and ("out of range" not in iss.issue and "missing" not in iss.issue):
                continue
            rows.append(iss)

    if args.as_json:
        print(json.dumps([asdict(r) for r in rows], indent=2))
    else:
        if not rows:
            print("OK: no provenance issues found.")
        else:
            print(f"{'path':<48} {'line':>5} {'sev':<7} issue")
            for r in rows:
                print(f"{r.path:<48} {r.line:>5} {r.severity:<7} {r.issue}")
        errors = sum(1 for r in rows if r.severity == "error")
        warnings = sum(1 for r in rows if r.severity == "warning")
        infos = sum(1 for r in rows if r.severity == "info")
        print(
            f"\n{errors} errors, {warnings} warnings, {infos} informational "
            f"across {len(reports)} pages."
        )

    sys.exit(1 if any(r.severity == "error" for r in rows) else 0)


if __name__ == "__main__":
    main()
