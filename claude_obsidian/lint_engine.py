"""Deterministic, read-only linting for an Obsidian wiki vault.

The public API has no process, network, cache, or write dependencies. Its only
clock input is the declared provenance audit date:

``lint_vault(root)``
    Return a JSON-serializable version 1 report for ``root/wiki``.

``render_markdown(report)``
    Render that report without adding volatile metadata.

The parser understands Obsidian wikilinks and embeds, common Markdown path
links, page aliases, heading and block fragments, and code spans/fences.  A
small allowlist may be placed at ``.vault-meta/lint-allowlist.json`` (a JSON
array, or an object with a ``dangling_links``-style array) or at
``.vault-meta/lint-allowlist.txt`` (one target or glob per line).

Link resolution is gitignore-aware: when a wikilink resolves to multiple
candidates and at least one is not gitignored, gitignored candidates (for
example build artifacts shadowing a page's name) are dropped before ambiguity
is reported. Only ``.gitignore`` files inside the vault root are consulted —
never ``.git/info/exclude``, global excludes, or a ``git`` subprocess — so
reports stay deterministic and process-free.

This module never creates directories or files. Even its command-line entry
point writes only to stdout. Provenance freshness uses the explicit ``as_of``
date when supplied and the current UTC calendar date otherwise.
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import html
import io
import json
import os
import posixpath
import re
import sys
import urllib.parse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence, cast

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from claude_obsidian.gitignore import GitignoreMatcher
from claude_obsidian.json_utils import strict_json_loads

REPORT_VERSION = 1
ENGINE_VERSION = "1.1.1"
REQUIRED_FRONTMATTER_FIELDS = ("title", "type", "status", "created", "updated", "tags")

# Obsidian resolves extensionless wikilinks to its note-like file types. Keep
# this list deliberately narrow: arbitrary attachments are normally linked
# with their extension, while Markdown, Canvas, and Bases are addressable by
# stem in the app.
_EXTENSIONLESS_WIKILINK_SUFFIXES = frozenset({".md", ".canvas", ".base"})

_IGNORED_WALK_DIRS = {
    ".git",
    ".obsidian",
    ".vault-meta",
    ".cache",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
}
_ORPHAN_EXCLUDED_NAMES = {
    "_index.md",
    "index.md",
    "log.md",
    "hot.md",
    "overview.md",
    "dashboard.md",
    "wiki map.md",
    "getting-started.md",
}
_ALLOWLIST_JSON_NAMES = ("lint-allowlist.json", "wiki-lint.json", "lint.json")
_ALLOWLIST_KEYS = {
    "dangling_links",
    "allowed_dangling_links",
    "allowlisted_dangling_links",
    "allowlist",
    "dead_links",
}

_TOP_LEVEL_YAML_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")
_FENCE_OPEN_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})(?:[^\r\n]*)$")
_ATX_HEADING_RE = re.compile(r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_BLOCK_ID_RE = re.compile(
    r"(?:^|[ \t])\^([A-Za-z0-9][A-Za-z0-9_-]*)[ \t]*$", re.MULTILINE
)
_WIKILINK_RE = re.compile(r"(?P<embed>!)?\[\[(?P<body>[^\]\r\n]+?)\]\]")
_MARKDOWN_LINK_RE = re.compile(
    r"(?P<embed>!)?\[(?P<label>[^\]\r\n]*)\]\((?P<destination>[^\r\n)]*)\)"
)
_HTML_COMMENT_RE = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL)
_URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


@dataclass(frozen=True)
class _Frontmatter:
    present: bool
    fields: frozenset[str]
    aliases: tuple[str, ...]
    end_offset: int


@dataclass(frozen=True)
class _Page:
    path: str
    absolute: Path
    text: str
    masked: str
    frontmatter: _Frontmatter
    headings: frozenset[str]
    block_ids: frozenset[str]
    is_wiki_page: bool


@dataclass(frozen=True)
class _Target:
    path: str
    absolute: Path
    page: _Page | None

    @property
    def is_markdown(self) -> bool:
        return self.path.casefold().endswith(".md")

    @property
    def without_link_suffix(self) -> str | None:
        suffix = PurePosixPath(self.path).suffix
        if suffix.casefold() not in _EXTENSIONLESS_WIKILINK_SUFFIXES:
            return None
        return self.path[: -len(suffix)]


@dataclass(frozen=True)
class _Link:
    source: str
    line: int
    target: str
    file_part: str
    fragment: str | None
    fragment_kind: str | None
    syntax: str
    markdown_relative: bool


def _path_sort_key(value: str) -> tuple[str, str]:
    return value.casefold(), value


def _entry_sort_key(entry: dict[str, Any]) -> tuple[Any, ...]:
    source = str(entry.get("source", entry.get("path", "")))
    return (
        source.casefold(),
        source,
        int(entry.get("line", 0)),
        str(
            entry.get("target", entry.get("heading", entry.get("basename", "")))
        ).casefold(),
        str(entry.get("target", entry.get("heading", entry.get("basename", "")))),
    )


def _unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        quote = value[0]
        value = value[1:-1]
        if quote == "'":
            return value.replace("''", "'")
        try:
            return cast(str, json.loads(f'"{value}"'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return value.replace(r"\"", '"').replace(r"\\", "\\")
    return value


def _split_inline_yaml_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        scalar = _unquote_yaml_scalar(value)
        return [scalar] if scalar else []
    inner = value[1:-1]
    if not inner.strip():
        return []
    try:
        row = next(csv.reader(io.StringIO(inner), skipinitialspace=True))
    except (csv.Error, StopIteration):
        row = inner.split(",")
    return [item for raw in row if (item := _unquote_yaml_scalar(raw))]


def _parse_frontmatter(text: str) -> _Frontmatter:
    """Parse the small YAML subset needed by lint without a YAML dependency."""

    offset = 1 if text.startswith("\ufeff") else 0
    if not text[offset:].startswith("---\n"):
        return _Frontmatter(False, frozenset(), (), 0)

    header_start = offset + 4
    cursor = header_start
    closing_start = -1
    closing_end = -1
    while cursor <= len(text):
        newline = text.find("\n", cursor)
        if newline < 0:
            line = text[cursor:]
            next_cursor = len(text)
        else:
            line = text[cursor:newline]
            next_cursor = newline + 1
        if line.rstrip("\r") in {"---", "..."}:
            closing_start = cursor
            closing_end = next_cursor
            break
        if newline < 0:
            break
        cursor = next_cursor

    if closing_start < 0:
        return _Frontmatter(False, frozenset(), (), 0)

    raw = text[header_start:closing_start]
    lines = raw.splitlines()
    fields: set[str] = set()
    aliases: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = _TOP_LEVEL_YAML_KEY_RE.match(line)
        if not match:
            index += 1
            continue
        key = match.group(1).casefold()
        value = (match.group(2) or "").strip()
        fields.add(key)
        if key in {"alias", "aliases"}:
            if value:
                aliases.extend(_split_inline_yaml_list(value))
            else:
                lookahead = index + 1
                while lookahead < len(lines):
                    child = lines[lookahead]
                    if _TOP_LEVEL_YAML_KEY_RE.match(child):
                        break
                    item = re.match(r"^[ \t]+-[ \t]+(.+?)[ \t]*$", child)
                    if item:
                        alias = _unquote_yaml_scalar(item.group(1))
                        if alias:
                            aliases.append(alias)
                    lookahead += 1
                index = lookahead - 1
        index += 1

    unique_aliases = tuple(sorted(set(aliases), key=_path_sort_key))
    return _Frontmatter(True, frozenset(fields), unique_aliases, closing_end)


def _mask_range(blocked: list[bool], start: int, end: int) -> None:
    for index in range(max(start, 0), min(end, len(blocked))):
        blocked[index] = True


def _mask_markdown_code(text: str, frontmatter_end: int = 0) -> str:
    """Replace frontmatter and code with spaces while preserving newlines."""

    blocked = [False] * len(text)
    if frontmatter_end:
        _mask_range(blocked, 0, frontmatter_end)
    for comment in _HTML_COMMENT_RE.finditer(text):
        _mask_range(blocked, comment.start(), comment.end())

    in_fence: tuple[str, int] | None = None
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if in_fence is None:
            match = _FENCE_OPEN_RE.match(content)
            if match:
                marker = match.group(1)
                in_fence = (marker[0], len(marker))
                _mask_range(blocked, offset, offset + len(line))
        else:
            marker_char, minimum = in_fence
            close_re = re.compile(
                rf"^[ ]{{0,3}}{re.escape(marker_char)}{{{minimum},}}[ \t]*$"
            )
            _mask_range(blocked, offset, offset + len(line))
            if close_re.match(content):
                in_fence = None
        offset += len(line)

    # CommonMark code spans use matching-length backtick runs.  An unmatched
    # run is ordinary text and must not suppress links after it.
    index = 0
    while index < len(text):
        if blocked[index] or text[index] != "`":
            index += 1
            continue
        run_end = index + 1
        while run_end < len(text) and not blocked[run_end] and text[run_end] == "`":
            run_end += 1
        run_length = run_end - index
        search = run_end
        closer = -1
        while search < len(text):
            if blocked[search] or text[search] != "`":
                search += 1
                continue
            candidate_end = search + 1
            while (
                candidate_end < len(text)
                and not blocked[candidate_end]
                and text[candidate_end] == "`"
            ):
                candidate_end += 1
            if candidate_end - search == run_length:
                closer = candidate_end
                break
            search = candidate_end
        if closer >= 0:
            _mask_range(blocked, index, closer)
            index = closer
        else:
            index = run_end

    return "".join(
        "\n"
        if char == "\n"
        else ("\r" if char == "\r" else " ")
        if blocked[index]
        else char
        for index, char in enumerate(text)
    )


def _normalize_heading(value: str) -> str:
    value = html.unescape(urllib.parse.unquote(value))
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[*_~`]+", "", value)
    value = re.sub(r"[ \t]+#+[ \t]*$", "", value)
    value = re.sub(r"[ \t]+\^[A-Za-z0-9][A-Za-z0-9_-]*[ \t]*$", "", value)
    return " ".join(value.split()).casefold()


def _page_metadata(path: Path, relative: str, wiki_prefix: str) -> _Page:
    text = path.read_text(encoding="utf-8-sig")
    frontmatter = _parse_frontmatter(text)
    masked = _mask_markdown_code(text, frontmatter.end_offset)
    headings = frozenset(
        normalized
        for match in _ATX_HEADING_RE.finditer(masked)
        if (normalized := _normalize_heading(match.group(2)))
    )
    block_ids = frozenset(
        match.group(1).casefold() for match in _BLOCK_ID_RE.finditer(masked)
    )
    is_wiki = relative == wiki_prefix or relative.startswith(f"{wiki_prefix}/")
    return _Page(
        path=relative,
        absolute=path,
        text=text,
        masked=masked,
        frontmatter=frontmatter,
        headings=headings,
        block_ids=block_ids,
        is_wiki_page=is_wiki,
    )


def _walk_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirnames[:] = sorted(
            (
                name
                for name in dirnames
                if name not in _IGNORED_WALK_DIRS
                and not (current_path / name).is_symlink()
            ),
            key=lambda value: (value.casefold(), value),
        )
        for filename in sorted(filenames, key=lambda value: (value.casefold(), value)):
            path = current_path / filename
            if path.is_symlink() or not path.is_file():
                continue
            files.append(path)
    return sorted(
        files, key=lambda path: _path_sort_key(path.relative_to(root).as_posix())
    )


def _wiki_location(root: Path) -> tuple[Path, str]:
    candidate = root / "wiki"
    if candidate.is_dir() and not candidate.is_symlink():
        return candidate, "wiki"
    if root.name.casefold() == "wiki" and root.is_dir():
        return root, "."
    return candidate, "wiki"


def _split_fragment(target: str) -> tuple[str, str | None, str | None]:
    delimiter = -1
    escaped = False
    for index, char in enumerate(target):
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "#" and not escaped:
            delimiter = index
            break
        escaped = False
    if delimiter < 0:
        return target, None, None
    file_part = target[:delimiter]
    fragment = target[delimiter + 1 :].strip()
    if fragment.startswith("^"):
        return file_part, fragment[1:], "block"
    return file_part, fragment, "heading"


def _unescape_wikilink(value: str) -> str:
    return re.sub(r"\\([\\|#\[\]])", r"\1", value)


def _wikilink_target(body: str) -> str:
    # In Markdown tables Obsidian aliases are commonly written ``\|``.  The
    # backslash escapes the table delimiter, not the wikilink alias separator.
    pipe = body.find("|")
    if pipe < 0:
        target = body
    else:
        target = body[:pipe]
        if target.endswith("\\"):
            target = target[:-1]
    return _unescape_wikilink(target.strip())


def _markdown_destination(value: str) -> str:
    value = value.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.find(">")].strip()
    title = re.match(r"^(.*?)[ \t]+(?:\"[^\"]*\"|'[^']*'|\([^)]*\))[ \t]*$", value)
    if title:
        value = title.group(1)
    return value.strip()


def _parse_links(page: _Page) -> list[_Link]:
    links: list[_Link] = []
    occupied: list[tuple[int, int]] = []
    for match in _WIKILINK_RE.finditer(page.masked):
        raw_target = _wikilink_target(match.group("body"))
        if not raw_target:
            continue
        file_part, fragment, fragment_kind = _split_fragment(raw_target)
        syntax = "embed" if match.group("embed") else "wikilink"
        links.append(
            _Link(
                source=page.path,
                line=page.masked.count("\n", 0, match.start()) + 1,
                target=raw_target,
                file_part=file_part,
                fragment=fragment,
                fragment_kind=fragment_kind,
                syntax=syntax,
                markdown_relative=False,
            )
        )
        occupied.append(match.span())

    for match in _MARKDOWN_LINK_RE.finditer(page.masked):
        if any(start <= match.start() < end for start, end in occupied):
            continue
        destination = _markdown_destination(match.group("destination"))
        if (
            not destination
            or destination.startswith("//")
            or _URI_SCHEME_RE.match(destination)
        ):
            continue
        decoded = urllib.parse.unquote(destination)
        file_part, fragment, fragment_kind = _split_fragment(decoded)
        syntax = "markdown-embed" if match.group("embed") else "markdown-link"
        links.append(
            _Link(
                source=page.path,
                line=page.masked.count("\n", 0, match.start()) + 1,
                target=decoded,
                file_part=file_part,
                fragment=fragment,
                fragment_kind=fragment_kind,
                syntax=syntax,
                markdown_relative=True,
            )
        )

    return sorted(
        links,
        key=lambda link: (
            link.line,
            link.target.casefold(),
            link.target,
            link.syntax,
        ),
    )


class _Resolver:
    def __init__(self, targets: Sequence[_Target], wiki_prefix: str) -> None:
        self.targets = tuple(targets)
        self.wiki_prefix = wiki_prefix
        self.by_full: dict[str, list[_Target]] = {}
        self.by_without_link_suffix: dict[str, list[_Target]] = {}
        self.by_basename: dict[str, list[_Target]] = {}
        self.by_alias: dict[str, list[_Target]] = {}
        for target in self.targets:
            full = target.path.casefold()
            self.by_full.setdefault(full, []).append(target)
            name = PurePosixPath(target.path).name
            self.by_basename.setdefault(name.casefold(), []).append(target)
            without_link_suffix = target.without_link_suffix
            if without_link_suffix is not None:
                self.by_without_link_suffix.setdefault(
                    without_link_suffix.casefold(), []
                ).append(target)
                stem = PurePosixPath(without_link_suffix).name
                self.by_basename.setdefault(stem.casefold(), []).append(target)
            if target.page:
                for alias in target.page.frontmatter.aliases:
                    self.by_alias.setdefault(alias.casefold(), []).append(target)

    @staticmethod
    def _deduplicate(candidates: Iterable[_Target]) -> list[_Target]:
        by_path: dict[str, _Target] = {}
        for candidate in candidates:
            by_path[candidate.path] = candidate
        return sorted(by_path.values(), key=lambda item: _path_sort_key(item.path))

    def _exact(self, query: str) -> list[_Target]:
        normalized = posixpath.normpath(query.replace("\\", "/")).lstrip("/")
        if normalized in {"", "."}:
            return []
        candidates: list[_Target] = []
        candidates.extend(self.by_full.get(normalized.casefold(), ()))
        candidates.extend(self.by_without_link_suffix.get(normalized.casefold(), ()))
        return self._deduplicate(candidates)

    def resolve(self, link: _Link) -> list[_Target]:
        raw = urllib.parse.unquote(link.file_part.strip()).replace("\\", "/")
        if not raw:
            return self._exact(link.source)

        raw = raw.lstrip("/")
        source_dir = posixpath.dirname(link.source)
        query_options: list[str] = []
        if link.markdown_relative or raw.startswith(("./", "../")):
            query_options.append(posixpath.normpath(posixpath.join(source_dir, raw)))
        query_options.append(posixpath.normpath(raw))
        if self.wiki_prefix != "." and not raw.casefold().startswith("wiki/"):
            query_options.append(
                posixpath.normpath(posixpath.join(self.wiki_prefix, raw))
            )

        for query in query_options:
            exact = self._exact(query)
            if exact:
                return exact

        if "/" not in raw:
            candidates: list[_Target] = []
            candidates.extend(self.by_basename.get(raw.casefold(), ()))
            candidates.extend(self.by_alias.get(raw.casefold(), ()))
            return self._deduplicate(candidates)

        suffix = posixpath.normpath(raw).casefold()
        candidates = [
            target
            for target in self.targets
            if target.path.casefold().endswith(f"/{suffix}")
            or (
                target.without_link_suffix is not None
                and target.without_link_suffix.casefold().endswith(f"/{suffix}")
            )
        ]
        return self._deduplicate(candidates)


def _allowlist_values(data: Any) -> list[str]:
    if isinstance(data, list):
        return [
            value.strip() for value in data if isinstance(value, str) and value.strip()
        ]
    if not isinstance(data, dict):
        return []
    values: list[str] = []
    for key, value in data.items():
        if str(key).casefold() in _ALLOWLIST_KEYS:
            values.extend(_allowlist_values(value))
    return values


def _load_allowlist(root: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    meta = root / ".vault-meta"
    patterns: list[str] = []
    errors: list[dict[str, str]] = []
    try:
        meta.lstat()
    except FileNotFoundError:
        return (), []
    except OSError as exc:
        return (), [
            {
                "path": ".vault-meta",
                "message": f"cannot inspect allowlist directory: {exc.__class__.__name__}",
            }
        ]
    if meta.is_symlink() or not meta.is_dir():
        return (), [
            {
                "path": ".vault-meta",
                "message": "allowlist directory must be a non-symlink directory",
            }
        ]
    reader = _transaction_reader()
    for filename in _ALLOWLIST_JSON_NAMES:
        relative = f".vault-meta/{filename}"
        try:
            raw = reader(root, relative, limit=1024 * 1024)
            if raw is None:
                continue
            data = strict_json_loads(raw.decode("utf-8"))
        except Exception as exc:
            errors.append(
                {
                    "path": relative,
                    "message": f"invalid allowlist JSON: {exc.__class__.__name__}",
                }
            )
            continue
        patterns.extend(_allowlist_values(data))

    text_path = meta / "lint-allowlist.txt"
    try:
        raw_text = reader(root, ".vault-meta/lint-allowlist.txt", limit=1024 * 1024)
        if raw_text is not None:
            for line in raw_text.decode("utf-8").splitlines():
                value = line.strip()
                if value and not value.startswith("#"):
                    patterns.append(value)
    except Exception as exc:
        errors.append(
            {
                "path": text_path.relative_to(root).as_posix(),
                "message": f"invalid allowlist text: {exc.__class__.__name__}",
            }
        )
    return tuple(sorted(set(patterns), key=_path_sort_key)), sorted(
        errors, key=_entry_sort_key
    )


def _is_allowlisted(link: _Link, patterns: Sequence[str]) -> bool:
    values = {
        link.target.strip().casefold(),
        link.file_part.strip().casefold(),
    }
    suffix = PurePosixPath(link.file_part.strip()).suffix
    if suffix.casefold() in _EXTENSIONLESS_WIKILINK_SUFFIXES:
        values.add(link.file_part[: -len(suffix)].strip().casefold())
    for pattern in patterns:
        normalized = pattern.strip()
        if normalized.startswith("[[") and normalized.endswith("]]"):
            normalized = _wikilink_target(normalized[2:-2])
        normalized = normalized.casefold()
        if any(fnmatch.fnmatchcase(value, normalized) for value in values):
            return True
    return False


def _fragment_error(link: _Link, target: _Target) -> str | None:
    if link.fragment is None:
        return None
    if target.page is None:
        return "fragment-on-non-markdown-target"
    if link.fragment_kind == "block":
        if link.fragment.casefold() not in target.page.block_ids:
            return "block-not-found"
        return None
    if _normalize_heading(link.fragment) not in target.page.headings:
        return "heading-not-found"
    return None


def _empty_sections(page: _Page) -> list[dict[str, Any]]:
    headings: list[tuple[int, int, int, str]] = []
    for match in _ATX_HEADING_RE.finditer(page.masked):
        heading = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(2)).strip()
        headings.append(
            (
                match.start(),
                match.end(),
                len(match.group(1)),
                heading,
            )
        )

    findings: list[dict[str, Any]] = []
    for index, (_, content_start, level, heading) in enumerate(headings):
        content_end = len(page.masked)
        for following_start, _, following_level, _ in headings[index + 1 :]:
            if following_level <= level:
                content_end = following_start
                break
        # Code is hidden from the heading/link parser, but it is still real
        # section content.  Inspect the original slice and blank only nested
        # heading lines that were confirmed outside code by ``page.masked``.
        section_chars = list(page.text[content_start:content_end])
        for nested_start, nested_end, _, _ in headings[index + 1 :]:
            if nested_start >= content_end:
                break
            if nested_start < content_start:
                continue
            relative_start = nested_start - content_start
            relative_end = nested_end - content_start
            for position in range(
                relative_start, min(relative_end, len(section_chars))
            ):
                if section_chars[position] not in "\r\n":
                    section_chars[position] = " "
        section = "".join(section_chars)
        section = _HTML_COMMENT_RE.sub("", section)
        section = re.sub(
            r"^[ \t]*\^[A-Za-z0-9][A-Za-z0-9_-]*[ \t]*$",
            "",
            section,
            flags=re.MULTILINE,
        )
        if section.strip():
            continue
        line = page.masked.count("\n", 0, headings[index][0]) + 1
        findings.append({"path": page.path, "line": line, "heading": heading})
    return findings


def _orphan_candidate(page: _Page, wiki_prefix: str) -> bool:
    name = PurePosixPath(page.path).name.casefold()
    if name in _ORPHAN_EXCLUDED_NAMES:
        return False
    relative = (
        page.path if wiki_prefix == "." else page.path.removeprefix(f"{wiki_prefix}/")
    )
    folded = relative.casefold()
    if folded.startswith("meta/") or folded.startswith("folds/"):
        return False
    return True


def _ledger_contracts() -> tuple[str, str, Any, Any]:
    """Import provenance contracts in package and direct-script modes."""

    try:
        from .ledgers import (
            CLAIM_PATH,
            SOURCE_PATH,
            validate_claim_ledger,
            validate_source_ledger,
        )
    except ImportError:  # pragma: no cover - direct script compatibility
        package_root = str(Path(__file__).resolve().parents[1])
        if package_root not in sys.path:
            sys.path.insert(0, package_root)
        from claude_obsidian.ledgers import (
            CLAIM_PATH,
            SOURCE_PATH,
            validate_claim_ledger,
            validate_source_ledger,
        )
    return SOURCE_PATH, CLAIM_PATH, validate_source_ledger, validate_claim_ledger


def _transaction_reader() -> Any:
    try:
        from .transaction import read_vault_regular
    except ImportError:  # pragma: no cover - direct script compatibility
        package_root = str(Path(__file__).resolve().parents[1])
        if package_root not in sys.path:
            sys.path.insert(0, package_root)
        from claude_obsidian.transaction import read_vault_regular
    return read_vault_regular


def _read_ledger(
    root: Path, relative: str
) -> tuple[Mapping[str, Any] | None, list[dict[str, str]]]:
    """Read one regular vault ledger without following symlinked components."""

    try:
        raw = _transaction_reader()(root, relative, limit=16 * 1024 * 1024)
        if raw is None:
            return None, []
        try:
            from .ledgers import strict_json_loads
        except ImportError:  # pragma: no cover - direct script compatibility
            from claude_obsidian.ledgers import strict_json_loads
        payload = strict_json_loads(raw.decode("utf-8"))
    except Exception as exc:
        return None, [
            {
                "path": relative,
                "message": f"cannot read provenance ledger: {exc.__class__.__name__}",
            }
        ]
    if not isinstance(payload, Mapping):
        return None, [
            {"path": relative, "message": "provenance ledger must be a JSON object"}
        ]
    return payload, []


def _provenance_errors(root: Path, *, as_of: date) -> list[dict[str, str]]:
    """Validate source and claim ledgers without filesystem writes."""

    source_path, claim_path, validate_source, validate_claim = _ledger_contracts()
    source, errors = _read_ledger(root, source_path)
    claim, claim_read_errors = _read_ledger(root, claim_path)
    errors.extend(claim_read_errors)
    if source is None and claim is None:
        return sorted(errors, key=_entry_sort_key)
    if source is None:
        errors.append(
            {
                "path": source_path,
                "message": "source ledger is required when a claim ledger exists",
            }
        )
        return sorted(errors, key=_entry_sort_key)
    for finding in validate_source(source, vault_root=root, as_of=as_of):
        errors.append(
            {
                "path": source_path,
                "field": finding["path"],
                "message": finding["message"],
            }
        )
    if claim is not None:
        for finding in validate_claim(claim, source, as_of=as_of, vault_root=root):
            errors.append(
                {
                    "path": claim_path,
                    "field": finding["path"],
                    "message": finding["message"],
                }
            )
    return sorted(errors, key=_entry_sort_key)


def _safe_report_text(value: str) -> str:
    output: list[str] = []
    for character in value:
        codepoint = ord(character)
        if character == "\\":
            output.append("\\\\")
        elif codepoint < 0x20 or codepoint == 0x7F or 0xD800 <= codepoint <= 0xDFFF:
            output.append(f"\\u{codepoint:04x}")
        else:
            output.append(character)
    return "".join(output)


def _sanitize_report_value(value: Any) -> Any:
    if isinstance(value, str):
        return _safe_report_text(value)
    if isinstance(value, list):
        return [_sanitize_report_value(item) for item in value]
    if isinstance(value, dict):
        return {
            _safe_report_text(key)
            if isinstance(key, str)
            else key: _sanitize_report_value(item)
            for key, item in value.items()
        }
    return value


def lint_vault(
    root: str | os.PathLike[str], *, as_of: date | str | None = None
) -> dict[str, Any]:
    """Return a deterministic, JSON-serializable lint report.

    ``root`` is normally the vault directory containing ``wiki/``.  Passing a
    directory named ``wiki`` is also supported.  Symlinked files and symlinked
    directories are not followed.  The function performs no filesystem writes.
    """

    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        raise ValueError(f"vault root is not a directory: {root_path}")
    root_path = root_path.resolve()
    wiki_dir, wiki_prefix = _wiki_location(root_path)
    vault_root = root_path.parent if wiki_prefix == "." else root_path
    if as_of is None:
        audit_date = datetime.now(timezone.utc).date()
    elif isinstance(as_of, datetime):
        raise ValueError("as_of must be an ISO date, date object, or null")
    elif isinstance(as_of, date):
        audit_date = as_of
    elif isinstance(as_of, str):
        try:
            audit_date = date.fromisoformat(as_of)
        except ValueError as exc:
            raise ValueError("as_of must be an ISO YYYY-MM-DD date") from exc
    else:
        raise ValueError("as_of must be an ISO date, date object, or null")
    patterns, configuration_errors = _load_allowlist(vault_root)

    all_paths = _walk_files(root_path)
    pages_by_path: dict[str, _Page] = {}
    targets: list[_Target] = []
    read_errors: list[dict[str, str]] = []
    for path in all_paths:
        relative = path.relative_to(root_path).as_posix()
        page: _Page | None = None
        if path.suffix.casefold() == ".md":
            try:
                page = _page_metadata(path, relative, wiki_prefix)
                pages_by_path[relative] = page
            except (OSError, UnicodeError) as exc:
                read_errors.append(
                    {
                        "path": relative,
                        "message": f"unable to read Markdown: {exc.__class__.__name__}",
                    }
                )
        targets.append(_Target(path=relative, absolute=path, page=page))

    if wiki_prefix == ".":
        wiki_pages = sorted(
            pages_by_path.values(), key=lambda page: _path_sort_key(page.path)
        )
    elif wiki_dir.is_dir():
        wiki_pages = sorted(
            (page for page in pages_by_path.values() if page.is_wiki_page),
            key=lambda page: _path_sort_key(page.path),
        )
    else:
        wiki_pages = []

    resolver = _Resolver(targets, wiki_prefix)
    gitignore = GitignoreMatcher(root_path)
    incoming: dict[str, set[str]] = {page.path: set() for page in wiki_pages}
    dead_links: list[dict[str, Any]] = []
    ambiguous_targets: list[dict[str, Any]] = []
    allowlisted: list[dict[str, Any]] = []
    stale_index_entries: list[dict[str, Any]] = []
    links_scanned = 0

    for page in wiki_pages:
        is_index = PurePosixPath(page.path).name.casefold() in {"index.md", "_index.md"}
        for link in _parse_links(page):
            links_scanned += 1
            candidates = resolver.resolve(link)
            if len(candidates) > 1:
                unignored = [
                    candidate
                    for candidate in candidates
                    if not gitignore.is_ignored(candidate.path)
                ]
                if unignored:
                    candidates = unignored
            if len(candidates) > 1:
                entry = {
                    "source": link.source,
                    "line": link.line,
                    "target": link.target,
                    "syntax": link.syntax,
                    "candidates": [candidate.path for candidate in candidates],
                }
                ambiguous_targets.append(entry)
                if is_index:
                    stale_index_entries.append({**entry, "reason": "ambiguous-target"})
                continue

            if not candidates:
                reason = "target-not-found"
                if _is_allowlisted(link, patterns):
                    allowlisted.append(
                        {
                            "source": link.source,
                            "line": link.line,
                            "target": link.target,
                            "reason": reason,
                        }
                    )
                    continue
                entry = {
                    "source": link.source,
                    "line": link.line,
                    "target": link.target,
                    "syntax": link.syntax,
                    "reason": reason,
                }
                dead_links.append(entry)
                if is_index:
                    stale_index_entries.append(entry.copy())
                continue

            candidate = candidates[0]
            if candidate.path in incoming and candidate.path != link.source:
                incoming[candidate.path].add(link.source)
            fragment_reason = _fragment_error(link, candidate)
            if fragment_reason is None:
                continue
            if _is_allowlisted(link, patterns):
                allowlisted.append(
                    {
                        "source": link.source,
                        "line": link.line,
                        "target": link.target,
                        "reason": fragment_reason,
                    }
                )
                continue
            entry = {
                "source": link.source,
                "line": link.line,
                "target": link.target,
                "syntax": link.syntax,
                "reason": fragment_reason,
                "resolved_path": candidate.path,
            }
            dead_links.append(entry)
            if is_index:
                stale_index_entries.append(entry.copy())

    duplicate_basenames: list[dict[str, Any]] = []
    basename_groups: dict[str, list[_Page]] = {}
    for page in wiki_pages:
        basename_groups.setdefault(PurePosixPath(page.path).stem.casefold(), []).append(
            page
        )
    for group in basename_groups.values():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda page: _path_sort_key(page.path))
        # Directory-local `_index.md` files are an intentional Obsidian
        # convention. An unsafe unqualified `[[_index]]` still appears in
        # `ambiguous_targets`; path-qualified links remain noise-free.
        if PurePosixPath(ordered[0].path).stem.casefold() == "_index":
            continue
        duplicate_basenames.append(
            {
                "basename": PurePosixPath(ordered[0].path).stem,
                "paths": [page.path for page in ordered],
            }
        )

    orphans = [
        {"path": page.path}
        for page in wiki_pages
        if _orphan_candidate(page, wiki_prefix) and not incoming.get(page.path)
    ]
    missing_frontmatter = []
    empty_sections: list[dict[str, Any]] = []
    for page in wiki_pages:
        missing = [
            field
            for field in REQUIRED_FRONTMATTER_FIELDS
            if field not in page.frontmatter.fields
        ]
        if missing:
            missing_frontmatter.append(
                {
                    "path": page.path,
                    "has_frontmatter": page.frontmatter.present,
                    "missing_fields": missing,
                }
            )
        empty_sections.extend(_empty_sections(page))

    dead_links.sort(key=_entry_sort_key)
    ambiguous_targets.sort(key=_entry_sort_key)
    allowlisted.sort(key=_entry_sort_key)
    stale_index_entries.sort(key=_entry_sort_key)
    duplicate_basenames.sort(key=_entry_sort_key)
    orphans.sort(key=_entry_sort_key)
    missing_frontmatter.sort(key=_entry_sort_key)
    empty_sections.sort(key=_entry_sort_key)
    read_errors.sort(key=_entry_sort_key)
    configuration_errors.sort(key=_entry_sort_key)
    provenance_errors = _provenance_errors(vault_root, as_of=audit_date)

    categories: dict[str, list[dict[str, Any]]] = {
        "dead_links": dead_links,
        "ambiguous_targets": ambiguous_targets,
        "duplicate_basenames": duplicate_basenames,
        "orphans": orphans,
        "missing_frontmatter": missing_frontmatter,
        "empty_sections": empty_sections,
        "stale_index_entries": stale_index_entries,
        "read_errors": read_errors,
        "configuration_errors": configuration_errors,
        "provenance_errors": provenance_errors,
    }
    category_counts = {name: len(entries) for name, entries in categories.items()}
    issues_found = sum(category_counts.values())

    report: dict[str, Any] = {
        "version": REPORT_VERSION,
        "engine_version": ENGINE_VERSION,
        "as_of": audit_date.isoformat(),
        "summary": {
            "pages_scanned": len(wiki_pages),
            "links_scanned": links_scanned,
            "issues_found": issues_found,
            "allowlisted_dangling_links": len(allowlisted),
            "category_counts": category_counts,
        },
        **categories,
        "allowlisted_dangling_links": allowlisted,
    }
    return cast(dict[str, Any], _sanitize_report_value(report))


def _code(value: Any) -> str:
    text = str(value).replace("\n", " ")
    run = 1
    while "`" * run in text:
        run += 1
    fence = "`" * run
    padding = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{padding}{text}{padding}{fence}"


def _none_or_items(
    lines: list[str], entries: Sequence[dict[str, Any]], render: Any
) -> None:
    if not entries:
        lines.append("None.")
        return
    lines.extend(render(entry) for entry in entries)


def render_markdown(report: dict[str, Any]) -> str:
    """Render a version 1 lint report as deterministic Markdown."""

    if report.get("version") != REPORT_VERSION:
        raise ValueError(f"unsupported lint report version: {report.get('version')!r}")
    summary = report.get("summary", {})
    lines = [
        "# Wiki Lint Report",
        "",
        f"Report schema: {_code(report['version'])}. Engine: {_code(report.get('engine_version', 'unknown'))}.",
        f"Provenance freshness as of: {_code(report.get('as_of', 'unknown'))}.",
        "",
        "## Summary",
        "",
        f"- Pages scanned: {summary.get('pages_scanned', 0)}",
        f"- Links scanned: {summary.get('links_scanned', 0)}",
        f"- Issues found: {summary.get('issues_found', 0)}",
        f"- Allowlisted dangling links: {summary.get('allowlisted_dangling_links', 0)}",
    ]

    sections: list[tuple[str, str, Any]] = [
        (
            "Dead Links",
            "dead_links",
            lambda item: (
                f"- {_code(item['source'])}:{item['line']} -> {_code(item['target'])} "
                f"({item['reason']})"
            ),
        ),
        (
            "Ambiguous Targets",
            "ambiguous_targets",
            lambda item: (
                f"- {_code(item['source'])}:{item['line']} -> {_code(item['target'])}; "
                f"candidates: {', '.join(_code(path) for path in item['candidates'])}"
            ),
        ),
        (
            "Duplicate Basenames",
            "duplicate_basenames",
            lambda item: (
                f"- {_code(item['basename'])}: "
                f"{', '.join(_code(path) for path in item['paths'])}"
            ),
        ),
        (
            "Orphan Pages",
            "orphans",
            lambda item: f"- {_code(item['path'])}: no inbound links",
        ),
        (
            "Frontmatter Gaps",
            "missing_frontmatter",
            lambda item: (
                f"- {_code(item['path'])}: missing "
                f"{', '.join(_code(field) for field in item['missing_fields'])}"
            ),
        ),
        (
            "Empty Sections",
            "empty_sections",
            lambda item: (
                f"- {_code(item['path'])}:{item['line']}: {_code(item['heading'])}"
            ),
        ),
        (
            "Stale Index Entries",
            "stale_index_entries",
            lambda item: (
                f"- {_code(item['source'])}:{item['line']} -> {_code(item['target'])} "
                f"({item['reason']})"
            ),
        ),
        (
            "Read Errors",
            "read_errors",
            lambda item: f"- {_code(item['path'])}: {item['message']}",
        ),
        (
            "Configuration Errors",
            "configuration_errors",
            lambda item: f"- {_code(item['path'])}: {item['message']}",
        ),
        (
            "Provenance Errors",
            "provenance_errors",
            lambda item: (
                f"- {_code(item['path'])}"
                f"{':' + _code(item['field']) if item.get('field') else ''}: "
                f"{item['message']}"
            ),
        ),
        (
            "Allowlisted Dangling Links",
            "allowlisted_dangling_links",
            lambda item: (
                f"- {_code(item['source'])}:{item['line']} -> {_code(item['target'])} "
                f"({item['reason']})"
            ),
        ),
    ]
    for title, key, renderer in sections:
        lines.extend(["", f"## {title}", ""])
        entries = report.get(key, [])
        if not isinstance(entries, list):
            raise ValueError(f"report field {key!r} must be a list")
        _none_or_items(lines, entries, renderer)
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint an Obsidian wiki without modifying it"
    )
    parser.add_argument(
        "root", nargs="?", default=".", help="vault root (default: current directory)"
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="stdout format",
    )
    parser.add_argument(
        "--as-of",
        help="ISO YYYY-MM-DD provenance freshness date (default: current UTC date)",
    )
    args = parser.parse_args(argv)
    try:
        report = lint_vault(args.root, as_of=args.as_of)
    except (OSError, ValueError) as exc:
        print(f"lint error: {exc}", file=sys.stderr)
        return 2
    if args.format == "markdown":
        sys.stdout.write(render_markdown(report))
    else:
        json.dump(report, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
