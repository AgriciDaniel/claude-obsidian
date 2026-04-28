#!/usr/bin/env python3
"""boundary-score.py — DragonScale Mechanism 4: boundary-first autoresearch scorer.

Reads `wiki/**/*.md`, builds a wikilink graph, and emits per-page boundary
scores to stdout (text) or as JSON for tooling.

boundary_score(p) = (out_degree(p) - in_degree(p)) * recency_weight(p)

- out_degree(p): count of distinct wikilinks in p that resolve to a
  scoreable page (scoreable = non-meta, non-fold, non-excluded).
- in_degree(p):  count of distinct scoreable pages that link to p.
- recency_weight(p): exp(-days_since_updated / RECENCY_HALFLIFE_DAYS).
  No floor; very old pages approach zero weight, which is the intended
  semantic of "frontier" (recently-touched and outward-pointing).

High score = the page points at many things, is pointed at by few, and
has been touched recently. That is a vault frontier page. Low or
negative score = hub / integrated page.

Feature-gated opt-in: autoresearch only invokes this when DragonScale
setup is detected. Safe to run standalone even without DragonScale set
up (reads wiki/ only; never writes).

This script is intentionally stdout-only. There is no `--report PATH`
equivalent to `tiling-check.py --report` because the helper is small
enough to pipe directly (`./scripts/boundary-score.py --json | jq ...`)
and keeping it read-only removes a write-path attack surface.

Usage:
  boundary-score.py                         # top-10 frontier, text
  boundary-score.py --top N                 # top N frontier
  boundary-score.py --json                  # JSON output
  boundary-score.py --page PATH             # score for a single page
  boundary-score.py --include-score-zero    # include pages with score=0

Exit codes:
  0  success
  2  usage error
"""

import argparse
import json
import math
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _vault import resolve_vault_or_die

VAULT_ROOT = resolve_vault_or_die()
WIKI_DIR = VAULT_ROOT / "wiki"

EXCLUDE_TYPES = {"meta", "fold"}
EXCLUDE_FILENAMES = {
    "_index.md", "index.md", "log.md", "hot.md", "overview.md",
    "dashboard.md", "Wiki Map.md", "getting-started.md",
}
EXCLUDE_PATH_PREFIXES = ("wiki/folds/", "wiki/meta/")

RECENCY_HALFLIFE_DAYS = 30.0
# No recency floor: a truly stale page should NOT dominate the frontier
# ranking, even if its out-degree is high. The exponential decay takes
# weight toward zero for year-old pages, which is the intended semantic
# of "frontier" (recently-touched and outward-pointing).
DEFAULT_TOP = 10
MAX_BODY_BYTES = 256 * 1024
# CommonMark-ish fence tracking: opening fence records (char, length);
# a closing fence must use the SAME char with SAME-OR-LONGER run length.
# Tilde fences (~~~) are supported alongside backtick fences (```). Indented
# code blocks (4+ spaces) are NOT filtered; in Obsidian usage, indented
# bullets commonly contain wikilinks and should count as edges.

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
TYPE_RE = re.compile(r"^type:\s*(\S+)", re.MULTILINE)
UPDATED_RE = re.compile(r"^updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.MULTILINE)
CREATED_RE = re.compile(r"^created:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.MULTILINE)
TITLE_RE = re.compile(r'^title:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)
# Obsidian wikilinks: [[Target]] or [[Target|Alias]] or [[Target#Heading]]
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")

EXIT_OK = 0
EXIT_USAGE = 2


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = text[m.end():]
    fm: dict = {}
    for key, regex in (("type", TYPE_RE), ("updated", UPDATED_RE),
                       ("created", CREATED_RE), ("title", TITLE_RE)):
        tm = regex.search(fm_raw)
        if tm:
            fm[key] = tm.group(1).strip().strip('"').strip("'")
    return fm, body


def included(path: Path, fm: dict) -> bool:
    if path.is_symlink():
        return False
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(VAULT_ROOT.resolve())
    except (OSError, ValueError):
        return False
    rel = path.relative_to(VAULT_ROOT).as_posix()
    if path.name in EXCLUDE_FILENAMES:
        return False
    for prefix in EXCLUDE_PATH_PREFIXES:
        if rel.startswith(prefix):
            return False
    if fm.get("type") in EXCLUDE_TYPES:
        return False
    return True


def days_since(date_str: str | None) -> float:
    """Return days since the given YYYY-MM-DD string, or a large sentinel if missing."""
    if not date_str:
        return 10_000.0
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        return 10_000.0
    delta = (date.today() - d).days
    return max(0.0, float(delta))


def recency_weight(days: float,
                   halflife: float = RECENCY_HALFLIFE_DAYS) -> float:
    return math.exp(-days / halflife)


_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")


def extract_wikilinks(body: str) -> set[str]:
    """Extract unique link targets (without alias or heading suffix) from the body.

    Skips wikilinks inside fenced code blocks so documentation examples
    (including in this repo's own skill files) do not pollute the graph.

    Fence handling: backtick AND tilde fences, with length tracking per
    CommonMark: the opening run sets (char, min_len); the closing line
    must use the SAME char with a run of SAME-OR-LONGER length. Indented
    code blocks (4+ spaces) are intentionally NOT filtered — indented
    bullets in Obsidian often contain wikilinks.
    """
    cleaned: list[str] = []
    fence_char: str | None = None
    fence_len: int = 0
    for line in body.splitlines():
        m = _FENCE_RE.match(line)
        if m:
            char = m.group(2)[0]
            length = len(m.group(2))
            if fence_char is None:
                fence_char = char
                fence_len = length
                continue
            if char == fence_char and length >= fence_len:
                fence_char = None
                fence_len = 0
                continue
        if fence_char is not None:
            continue
        cleaned.append(line)
    scan = "\n".join(cleaned)
    results: set[str] = set()
    for m in WIKILINK_RE.finditer(scan):
        raw = m.group(1).strip()
        # Folder-qualified links like [[notes/Foo]] resolve to Foo.md by stem.
        # This matches Obsidian default behavior for unique filenames.
        stem = raw.rsplit("/", 1)[-1]
        if stem:
            results.add(stem)
    return results


def collect_pages() -> dict[str, dict]:
    """Scan wiki/, return {title_key: {path, title, body, fm}} for scoreable pages.

    `title_key` is the filename stem, which is what Obsidian wikilinks resolve
    to by default. Assumes filenames are unique across the vault (enforced by
    wiki-lint naming convention).
    """
    pages: dict[str, dict] = {}
    if not WIKI_DIR.is_dir():
        return pages
    for md in sorted(WIKI_DIR.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if len(text.encode("utf-8")) > MAX_BODY_BYTES:
            continue
        fm, body = parse_frontmatter(text)
        if not included(md, fm):
            continue
        title_key = md.stem  # Obsidian wikilinks are filename-based
        pages[title_key] = {
            "path": md.relative_to(VAULT_ROOT).as_posix(),
            "title": fm.get("title", title_key),
            "body": body,
            "fm": fm,
        }
    return pages


def build_graph(pages: dict[str, dict]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Return (out_edges, in_edges) where each maps title_key -> set(title_key).

    Only edges whose target is a known scoreable page are counted. Self-loops
    are ignored.
    """
    out_edges: dict[str, set[str]] = {k: set() for k in pages}
    in_edges: dict[str, set[str]] = {k: set() for k in pages}
    for src, entry in pages.items():
        links = extract_wikilinks(entry["body"])
        for target in links:
            if target == src:
                continue
            if target in pages:
                out_edges[src].add(target)
                in_edges[target].add(src)
    return out_edges, in_edges


def score_page(title_key: str,
               pages: dict[str, dict],
               out_edges: dict[str, set[str]],
               in_edges: dict[str, set[str]]) -> dict:
    entry = pages[title_key]
    fm = entry["fm"]
    out_deg = len(out_edges.get(title_key, set()))
    in_deg = len(in_edges.get(title_key, set()))
    date_str = fm.get("updated") or fm.get("created")
    days = days_since(date_str)
    rw = recency_weight(days)
    score = (out_deg - in_deg) * rw
    return {
        "title": entry["title"],
        "title_key": title_key,
        "path": entry["path"],
        "out_degree": out_deg,
        "in_degree": in_deg,
        "age_days": days,
        "recency_weight": round(rw, 4),
        "score": round(score, 4),
    }


def run(top: int, want_json: bool, include_zero: bool, page_filter: str | None) -> int:
    pages = collect_pages()
    out_edges, in_edges = build_graph(pages)
    scored = [score_page(k, pages, out_edges, in_edges) for k in pages]
    if page_filter:
        key = Path(page_filter).stem
        matched = [s for s in scored if s["title_key"] == key or s["path"] == page_filter]
        if not matched:
            log(f"ERR: no scoreable page matches '{page_filter}'")
            return EXIT_USAGE
        scored = matched
    else:
        if not include_zero:
            scored = [s for s in scored if s["score"] > 0.0]
        scored.sort(key=lambda s: (-s["score"], s["title_key"]))
        scored = scored[:top]

    if want_json:
        print(json.dumps({
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "halflife_days": RECENCY_HALFLIFE_DAYS,
            "page_count_scoreable": len(pages),
            "results": scored,
        }, indent=2))
    else:
        print("# Boundary Score Report")
        print(f"scoreable pages: {len(pages)}; halflife: {RECENCY_HALFLIFE_DAYS} days")
        if not scored:
            print("\nNo positive-score frontier pages found.")
        else:
            print("")
            print("| # | score | out | in | age_d | title | path |")
            print("|---|---|---|---|---|---|---|")
            for i, s in enumerate(scored, 1):
                print(f"| {i} | {s['score']:.3f} | {s['out_degree']} | {s['in_degree']} | "
                      f"{int(s['age_days'])} | {s['title']} | {s['path']} |")
    return EXIT_OK


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--top", type=int, default=DEFAULT_TOP)
    p.add_argument("--json", action="store_true")
    p.add_argument("--include-score-zero", action="store_true",
                   help="Include pages whose score is zero or negative in the output")
    p.add_argument("--page", default=None, help="Score a single page by path or stem")
    args = p.parse_args(argv)
    if args.top < 1:
        log("ERR: --top must be >= 1")
        return EXIT_USAGE
    return run(args.top, args.json, args.include_score_zero, args.page)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
