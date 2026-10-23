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

The walk skips every dot-prefixed directory by default, mirroring Obsidian's
own indexer, so a duplicated or archived page under a hidden folder (a
``.raw`` ingest archive, a ``.claude`` agent worktree, Obsidian's own
``.trash``, and similar) is never a link-resolution candidate. ``exclude``
globs, passed to ``lint_vault`` or set vault-side, scope specific paths out of
every finding category.

Link resolution is gitignore-aware: when a wikilink resolves to multiple
candidates and at least one is not gitignored, gitignored candidates (for
example build artifacts shadowing a page's name) are dropped before ambiguity
is reported. Only ``.gitignore`` files inside the vault root are consulted,
never ``.git/info/exclude``, global excludes, or a ``git`` subprocess, so
reports stay deterministic and process-free.

This module never creates directories or files. Even its command-line entry
point writes only to stdout. Provenance freshness uses the explicit ``as_of``
date when supplied and the current UTC calendar date otherwise.
"""

from __future__ import annotations

import argparse
import bisect
import fnmatch
import html
import json
import os
import posixpath
import re
import stat
import sys
import urllib.parse
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence, cast

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from claude_obsidian.gitignore import GitignoreMatcher
from claude_obsidian.json_utils import strict_json_loads
from claude_obsidian.visible_paths import is_visible_path
from claude_obsidian.limits import MAX_CANONICAL_LEDGER_BYTES
from claude_obsidian.markdown_links import (
    HTML_COMPLETE_TAG_RE as _HTML_COMPLETE_TAG_RE, html_block_start as _html_block_start,
    iter_markdown_links, iter_wikilinks,
    markdown_destination as _markdown_destination,
    markdown_visible_text,
    mask_comments as _mask_comments,
    mask_protected_regions as _mask_markdown_code,
)
from claude_obsidian.paths import is_name_surrogate

REPORT_VERSION = 1
ENGINE_VERSION = "1.2.0"
REQUIRED_FRONTMATTER_FIELDS = ("title", "type", "status", "created", "updated", "tags")

# Obsidian resolves extensionless wikilinks to its note-like file types. Keep
# this list deliberately narrow: arbitrary attachments are normally linked
# with their extension, while Markdown, Canvas, and Bases are addressable by
# stem in the app.
_EXTENSIONLESS_WIKILINK_SUFFIXES = frozenset({".md", ".canvas", ".base"})

_IGNORED_WALK_DIRS = {
    "node_modules",
    "__pycache__",
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
# The label alternation avoids lazy backtracking over long trailing spaces.
# Indentation is spaces only: a tab reaches the indented-code column.
_ATX_HEADING_RE = re.compile(
    r"^ {0,3}(#{1,6})[ \t]+(.*[^ \t\r\n]|[ \t])[ \t]*$", re.MULTILINE
)
_ATX_CLOSING_RE = re.compile(r"(?<![ \t])[ \t]+#+[ \t]*$")
_HEADING_BLOCK_ID_RE = re.compile(r"(?<![ \t])[ \t]+\^[A-Za-z0-9][A-Za-z0-9_-]*[ \t]*$")
# Obsidian strips these from heading link text; compare both sides that way.
_HEADING_LINK_STRIPPED_RE = re.compile(r"%%|[:|^#\[\]]")
_SETEXT_UNDERLINE_RE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
_THEMATIC_BREAK_RE = re.compile(r"^ {0,3}(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})$")
# One container marker: a blockquote or list item, with one following space.
_CONTAINER_MARKER_RE = re.compile(r" {0,3}(?:>[ \t]?|(?:[-+*]|\d{1,9}[.)])(?:[ \t]|$))")
# Inner content starting one of these blocks leaves no paragraph to continue.
_NON_PARAGRAPH_START_RE = re.compile(
    r" {0,3}(?:#{1,6}(?:[ \t]|$)|`{3,}|~{3,}|<!--|<\?|<![A-Za-z]|<!\[CDATA\[)"
)
# These block starts cannot supply paragraph text to a following Setext line.
_PARAGRAPH_BREAK_RE = re.compile(
    r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|>|[-+*][ \t]|\d{1,9}[.)][ \t]|"
    r"(?:\*[ \t]*){3,}$|(?:_[ \t]*){3,}$|(?:-[ \t]*){3,}$)"
)
_BLOCK_ID_RE = re.compile(
    r"(?:^|[ \t])\^([A-Za-z0-9][A-Za-z0-9_-]*)[ \t]*$", re.MULTILINE
)
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
    values: Mapping[str, Any]
    value_lines: Mapping[str, int]
    property_ranges: tuple[tuple[int, int], ...]
    duplicate_fields: frozenset[str]


@dataclass(frozen=True)
class _Page:
    path: str
    absolute: Path
    text: str
    masked: str
    frontmatter: _Frontmatter
    headings: frozenset[str]
    heading_paths: tuple[tuple[str, ...], ...]
    heading_sections: tuple[tuple[int, int, int, str], ...]
    block_ids: frozenset[str]
    is_wiki_page: bool


@dataclass(frozen=True)
class _Target:
    path: str
    absolute: Path
    page: _Page | None
    _canonical_path: str
    root: Path | None = None

    @property
    def is_markdown(self) -> bool:
        return self.path.casefold().endswith(".md")

    @property
    def without_link_suffix(self) -> str | None:
        suffix = PurePosixPath(self._canonical_path).suffix
        if suffix.casefold() not in _EXTENSIONLESS_WIKILINK_SUFFIXES:
            return None
        return self._canonical_path[: -len(suffix)]


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


def _name_key(value: str) -> str:
    # macOS and iCloud store names decomposed (NFD) while links typed in
    # Obsidian are composed (NFC); Obsidian treats both spellings as one name.
    return unicodedata.normalize("NFC", unicodedata.normalize("NFC", value).casefold())


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


def _newline_offsets(text: str) -> list[int]:
    """Index newlines once so many source lines cost a bisection each."""
    return [match.start() for match in re.finditer("\n", text)]


def _line_at(newlines: Sequence[int], offset: int) -> int:
    return bisect.bisect_left(newlines, offset) + 1


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


def _yaml_without_comment(value: str) -> str:
    """Remove a trailing YAML comment while respecting quoted scalars."""
    quote: str | None = None
    index = 0
    while index < len(value):
        char = value[index]
        if quote:
            if quote == '"' and char == "\\":
                index += 2
                continue
            if char == quote:
                if quote == "'" and value[index:index + 2] == "''":
                    index += 2
                    continue
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
        index += 1
    return value.rstrip()


def _yaml_scalar(value: str) -> Any:
    """Read a flat property scalar; complex YAML stays explicitly unsupported."""
    value = _yaml_without_comment(value).strip()
    if not value or value in {"~", "null", "Null", "NULL"}:
        return None
    if value.startswith(("'", '"')):
        if len(value) < 2 or value[-1] != value[0]:
            return {"unsupported_yaml": True}
        if value.startswith("'") and not re.fullmatch(r"'(?:[^']|'')*'", value):
            return {"unsupported_yaml": True}
        if value.startswith('"'):
            try:
                return json.loads(value)
            except ValueError:
                return {"unsupported_yaml": True}
        return _unquote_yaml_scalar(value)
    if value.casefold() in {"true", "false"}:
        return value.casefold() == "true"
    if re.fullmatch(r"[-+]?[0-9]+", value):
        return int(value) if len(value) <= 1000 else {"unsupported_yaml": True}
    if re.fullmatch(r"[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?", value):
        return float(value)
    if value.startswith(("[", "{", "&", "*", "!", "|", ">")):
        return {"unsupported_yaml": True}
    if re.search(r":(?:\s|$)", value):
        return {"unsupported_yaml": True}
    return value


def _yaml_property_tokens(value: str) -> list[tuple[str, int, int]] | None:
    """Return scalar tokens and offsets for a supported flat YAML list/value."""
    value = _yaml_without_comment(value)
    start = len(value) - len(value.lstrip())
    end = len(value.rstrip())
    if start == end:
        return []
    if value[start] != "[":
        return [(value[start:end], start, end)]
    if value[end - 1] != "]":
        return None
    tokens: list[tuple[str, int, int]] = []
    quote: str | None = None
    cursor = start + 1
    token_start = cursor
    while cursor < end - 1:
        char = value[cursor]
        if quote:
            if quote == '"' and char == "\\":
                cursor += 2
                continue
            if char == quote:
                if quote == "'" and value[cursor:cursor + 2] == "''":
                    cursor += 2
                    continue
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char in "[]{}":
            return None
        elif char == ",":
            left = token_start + len(value[token_start:cursor]) - len(value[token_start:cursor].lstrip())
            right = cursor - len(value[token_start:cursor]) + len(value[token_start:cursor].rstrip())
            # A comma always terminates an entry. Preserve an omitted entry as
            # an empty token so the value parser records null instead of
            # silently repairing a malformed flow sequence. A final trailing
            # comma is legal and is handled separately below.
            tokens.append((value[left:right], left, right))
            token_start = cursor + 1
        cursor += 1
    if quote:
        return None
    left = token_start + len(value[token_start:end - 1]) - len(value[token_start:end - 1].lstrip())
    right = end - 1 - len(value[token_start:end - 1]) + len(value[token_start:end - 1].rstrip())
    if left < right:
        tokens.append((value[left:right], left, right))
    return tokens


def _parse_frontmatter(text: str) -> _Frontmatter:
    """Parse the small YAML subset needed by lint without a YAML dependency."""

    offset = 1 if text.startswith("\ufeff") else 0
    if not text[offset:].startswith("---\n"):
        return _Frontmatter(False, frozenset(), (), 0, {}, {}, (), frozenset())

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
        return _Frontmatter(False, frozenset(), (), 0, {}, {}, (), frozenset())

    raw = text[header_start:closing_start]
    lines = raw.splitlines()
    fields: set[str] = set()
    duplicate_fields: set[str] = set()
    aliases: list[str] = []
    values: dict[str, Any] = {}
    value_lines: dict[str, int] = {}
    property_ranges: list[tuple[int, int]] = []
    line_offsets: list[int] = []
    line_cursor = header_start
    for line in raw.splitlines(keepends=True):
        line_offsets.append(line_cursor)
        line_cursor += len(line)
    index = 0
    while index < len(lines):
        line = lines[index]
        match = _TOP_LEVEL_YAML_KEY_RE.match(line)
        if not match:
            index += 1
            continue
        key = match.group(1).casefold()
        value = _yaml_without_comment(match.group(2) or "").strip()
        if key in fields:
            duplicate_fields.add(key)
        fields.add(key)
        value_lines[key] = index + 2
        tokens: list[tuple[str, int, int]] = []
        value_start = line.index(":") + 1
        inline = _yaml_property_tokens(line[value_start:])
        if value:
            if value.startswith("["):
                values[key] = [_yaml_scalar(token) for token, _, _ in inline] if inline is not None else {"unsupported_yaml": True}
            else:
                values[key] = _yaml_scalar(value)
            if inline is not None:
                tokens.extend((token, line_offsets[index] + value_start + left,
                               line_offsets[index] + value_start + right)
                              for token, left, right in inline)
        else:
            children: list[Any] = []
            simple_list = True
            lookahead = index + 1
            while lookahead < len(lines) and not _TOP_LEVEL_YAML_KEY_RE.match(lines[lookahead]):
                child = lines[lookahead]
                item = re.match(r"^[ \t]*-[ \t]+(.*?)[ \t]*$", child)
                if item:
                    children.append(_yaml_scalar(item.group(1)))
                    item_offset = line_offsets[lookahead] + item.start(1)
                    tokens.append((item.group(1), item_offset, item_offset + len(item.group(1))))
                elif child.strip() and not child.lstrip().startswith("#"):
                    children.append({"unsupported_yaml": True})
                    simple_list = False
                lookahead += 1
            values[key] = children if children else None
            if not simple_list:
                tokens = []
        if key not in {"alias", "aliases"}:
            for token, start, end in tokens:
                scalar = _yaml_without_comment(token).strip()
                if (len(scalar) >= 2 and scalar[0] == scalar[-1]
                        and scalar[0] in {"'", '"'}
                        and isinstance(_yaml_scalar(scalar), str)):
                    property_ranges.append((start, start + len(scalar)))
        if key in {"alias", "aliases"}:
            parsed_aliases = values[key]
            if isinstance(parsed_aliases, str):
                aliases.append(parsed_aliases)
            elif isinstance(parsed_aliases, list):
                aliases.extend(
                    alias for alias in parsed_aliases
                    if isinstance(alias, str) and alias
                )
        index += 1

    unique_aliases = tuple(sorted(set(aliases), key=_path_sort_key))
    return _Frontmatter(True, frozenset(fields), unique_aliases, closing_end,
                        values, value_lines, tuple(property_ranges), frozenset(duplicate_fields))


def _normalize_heading(value: str, *, render_inline: bool = True) -> str:
    value = html.unescape(urllib.parse.unquote(value))
    if render_inline:
        value = markdown_visible_text(value)
        # Use protected-region offsets so code that resembles a wikilink stays
        # literal text, just as it does for supported Markdown link labels.
        masked = _mask_markdown_code(value)
        pieces: list[str] = []
        cursor = 0
        for match in iter_wikilinks(masked):
            pieces.append(value[cursor:match.start()])
            pieces.append(_wikilink_visible_label(match))
            cursor = match.end()
        pieces.append(value[cursor:])
        value = ''.join(pieces)
    value = re.sub(r"[*_~`]+", "", value)
    value = _ATX_CLOSING_RE.sub("", value)
    value = _HEADING_BLOCK_ID_RE.sub("", value)
    exact = " ".join(value.split()).casefold()
    # A heading made only of stripped characters keeps its exact spelling.
    return " ".join(_HEADING_LINK_STRIPPED_RE.sub(" ", exact).split()) or exact


def _wikilink_visible_label(match: re.Match[str]) -> str:
    """Return the text made visible by a supported wikilink heading label."""
    target, separator, alias = match.group("body").partition("|")
    visible = alias if separator and alias.strip() else target
    return _unescape_wikilink(visible.strip())


def _container_state(line: str) -> tuple[bool, int | None]:
    """Describe what a blockquote or list line leaves open for later lines.

    The first value is true when paragraph text is open: only that absorbs
    following lazy lines. An empty marker or a heading, thematic break, fence,
    indented code or HTML block inside the container leaves nothing to
    continue. The second value is the content column of a list-only container
    whose HTML block continues on lines indented at least that far.
    """
    rest = line.expandtabs(4)
    container = quoted = False
    while not _THEMATIC_BREAK_RE.match(rest) and (marker := _CONTAINER_MARKER_RE.match(rest)):
        container = True
        quoted = quoted or ">" in marker.group(0)
        rest = rest[marker.end():]
    column = len(line.expandtabs(4)) - len(rest)
    if not container or not rest.strip() or _THEMATIC_BREAK_RE.match(rest):
        return False, None
    if len(rest) - len(rest.lstrip(" ")) >= 4:
        return False, None
    if _HTML_COMPLETE_TAG_RE.match(rest) or _html_block_start(rest) or rest.lstrip(" ").startswith("<!--"):
        return False, None if quoted else column
    return not _NON_PARAGRAPH_START_RE.match(rest), None


def _split_lines(text: str) -> list[str]:
    """Split only at ``\n``; masking may blank other Unicode line separators."""
    return [line for line in re.split(r"(?<=\n)", text) if line]


def _headings(masked: str, labels: str) -> list[tuple[int, int, int, str]]:
    """Scan ATX and paragraph-based Setext headings outside protected regions.

    Offsets cover the entire heading, including a Setext underline, so metadata,
    hierarchy and empty-section checks share the same section boundaries.
    Inline code remains visible in labels; only the default protected mask can
    authorize heading markers or paragraph-interrupting block syntax.
    """
    headings: list[tuple[int, int, int, str]] = []
    paragraph: list[tuple[int, str]] = []
    lazy_container = False
    html_column: int | None = None
    offset = 0
    for raw_line, label_raw in zip(_split_lines(masked), _split_lines(labels)):
        line = raw_line.rstrip('\r\n')
        label_line = label_raw.rstrip('\r\n')
        atx = _ATX_HEADING_RE.fullmatch(line)
        label_atx = _ATX_HEADING_RE.fullmatch(label_line) if atx else None
        # Inline code directly after the marker, as in ``#`x` y``, is
        # paragraph text: the masked line only looks like a heading.
        literal_hash = atx is not None and label_atx is None
        underline = _SETEXT_UNDERLINE_RE.fullmatch(line)
        if atx and label_atx:
            headings.append((offset, offset + len(line), len(atx.group(1)),
                             _ATX_CLOSING_RE.sub("", label_atx.group(2)).strip()))
            paragraph = []
            lazy_container, html_column = False, None
        elif underline and _SETEXT_UNDERLINE_RE.fullmatch(label_line) and paragraph:
            label = ' '.join(text.strip() for _, text in paragraph)
            headings.append((paragraph[0][0], offset + len(line),
                             1 if underline.group(1).startswith('=') else 2, label))
            paragraph = []
        elif not label_line.strip() or underline or (
                not literal_hash and _PARAGRAPH_BREAK_RE.match(line)):
            paragraph = []
            # A list item or quote paragraph absorbs following lazy lines, and
            # a Setext underline cannot be a lazy continuation line.
            lazy_container, html_column = _container_state(label_line)
        elif lazy_container:
            pass
        elif html_column is not None and (
                len(expanded := label_line.expandtabs(4)) - len(expanded.lstrip(" ")) >= html_column):
            pass  # Indented content of an HTML block that opened a list item.
        else:
            html_column = None
            paragraph.append((offset, label_line))
        offset += len(raw_line)
    return headings


def _mask_heading_html(text: str, frontmatter_end: int, *, preserve_inline_code: bool = False) -> str:
    """Mask supported raw HTML within the same heading protection scan.

    Raw text elements run through their closing tag. Recognized block tags use
    CommonMark's blank-line boundary. Generic custom tags, HTML rendering and
    plugin-specific HTML behavior remain outside this bounded heading scanner.
    """
    return _mask_markdown_code(text, frontmatter_end,
                               preserve_inline_code=preserve_inline_code,
                               mask_html_blocks=True)


def _page_metadata(
    vault_root: Path,
    canonical: str,
    path: Path,
    relative: str,
    wiki_prefix: str,
) -> _Page:
    raw = _transaction_reader()(
        vault_root,
        canonical,
        limit=_transaction_file_limit(),
        missing_ok=False,
        existing=True,
    )
    assert raw is not None
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    frontmatter = _parse_frontmatter(text)
    masked = _mask_markdown_code(text, frontmatter.end_offset)
    heading_masked = _mask_heading_html(text, frontmatter.end_offset)
    heading_labels = _mask_heading_html(text, frontmatter.end_offset, preserve_inline_code=True)
    parsed_headings = _headings(heading_masked, heading_labels)
    normalized_headings = [_normalize_heading(heading) for _, _, _, heading in parsed_headings]
    headings = frozenset(normalized for normalized in normalized_headings if normalized)
    heading_stack: list[tuple[int, str]] = []
    heading_paths: list[tuple[str, ...]] = []
    for (_, _, level, _), normalized in zip(parsed_headings, normalized_headings):
        while heading_stack and heading_stack[-1][0] >= level:
            heading_stack.pop()
        heading_stack.append((level, normalized))
        heading_paths.append(tuple(label for _, label in heading_stack))
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
        heading_paths=tuple(heading_paths),
        heading_sections=tuple(parsed_headings),
        block_ids=block_ids,
        is_wiki_page=is_wiki,
    )


def _walk_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        safe_directories: list[str] = []
        for name in sorted(dirnames, key=lambda value: (value.casefold(), value)):
            path = current_path / name
            if name in _IGNORED_WALK_DIRS or not is_visible_path(name):
                continue
            try:
                metadata = path.lstat()
            except OSError:
                continue
            if is_name_surrogate(metadata) or not stat.S_ISDIR(metadata.st_mode):
                continue
            safe_directories.append(name)
        dirnames[:] = safe_directories
        for filename in sorted(filenames, key=lambda value: (value.casefold(), value)):
            path = current_path / filename
            if not is_visible_path(filename):
                continue
            try:
                metadata = path.lstat()
            except OSError:
                continue
            if is_name_surrogate(metadata) or not stat.S_ISREG(metadata.st_mode):
                continue
            files.append(path)
    return sorted(
        files, key=lambda path: _path_sort_key(path.relative_to(root).as_posix())
    )


def _is_declared_vault(path: Path) -> bool:
    """Report whether ``path`` holds a regular workspace marker file."""
    try:
        metadata = (path / ".claude-obsidian.json").lstat()
    except OSError:
        return False
    return stat.S_ISREG(metadata.st_mode) and not is_name_surrogate(metadata)


def _wiki_location(root: Path) -> tuple[Path, str]:
    candidate = root / "wiki"
    if candidate.is_dir() and not candidate.is_symlink():
        return candidate, "wiki"
    if root.name.casefold() == "wiki" and root.is_dir():
        return root, "."
    return candidate, "wiki"


def _split_fragment(
    target: str, *, decode_fragment: bool = False
) -> tuple[str, str | None, str | None]:
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
    if decode_fragment:
        fragment = urllib.parse.unquote(fragment)
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


def _parse_links(page: _Page) -> list[_Link]:
    links: list[_Link] = []
    occupied: list[tuple[int, int]] = []
    newlines = _newline_offsets(page.masked)
    wikilink_matches = [
        (match, False, None) for match in iter_wikilinks(page.masked)
    ]
    for start, end in page.frontmatter.property_ranges:
        value = _yaml_scalar(page.text[start:end])
        if isinstance(value, str):
            property_line = page.text.count("\n", 0, start) + 1
            wikilink_matches.extend((match, True, property_line)
                                   for match in iter_wikilinks(value))
    for match, in_property, property_line in wikilink_matches:
        raw_target = _wikilink_target(match.group("body"))
        if not raw_target:
            continue
        file_part, fragment, fragment_kind = _split_fragment(raw_target)
        syntax = "embed" if match.group("embed") else "wikilink"
        if in_property:
            syntax = "property-wikilink"
        links.append(
            _Link(
                source=page.path,
                line=property_line if property_line is not None else _line_at(newlines, match.start()),
                target=raw_target,
                file_part=file_part,
                fragment=fragment,
                fragment_kind=fragment_kind,
                syntax=syntax,
                markdown_relative=False,
            )
        )
        if not in_property:
            occupied.append(match.span())

    # Body wikilink spans are disjoint and ascending, so one bisection finds
    # the only span that could contain a Markdown link start.
    occupied_starts = [start for start, _ in occupied]
    for match in iter_markdown_links(page.masked):
        position = bisect.bisect_right(occupied_starts, match.start) - 1
        if position >= 0 and match.start < occupied[position][1]:
            continue
        destination = match.destination
        if (
            not destination
            or destination.startswith("//")
            or _URI_SCHEME_RE.match(destination)
        ):
            continue
        decoded = urllib.parse.unquote(destination)
        # Split before decoding so a literal percent-encoded hash in a filename
        # cannot become the fragment delimiter. The resolver decodes paths once.
        file_part, fragment, fragment_kind = _split_fragment(
            destination, decode_fragment=True
        )
        syntax = "markdown-embed" if match.embed else "markdown-link"
        links.append(
            _Link(
                source=page.path,
                line=_line_at(newlines, match.start),
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


def _link_queries(
    link: _Link, wiki_prefix: str, source_path: str | None = None
) -> tuple[str, list[str]]:
    # Obsidian wikilink targets are literal; only Markdown destinations are
    # percent-encoded URLs.
    raw = link.file_part.strip()
    if link.markdown_relative:
        raw = urllib.parse.unquote(raw)
    raw = raw.replace("\\", "/")
    source = source_path or link.source
    if not raw:
        return raw, [source]
    raw = raw.lstrip("/")
    queries: list[str] = []
    if link.markdown_relative or raw.startswith(("./", "../")):
        queries.append(posixpath.normpath(posixpath.join(posixpath.dirname(source), raw)))
    queries.append(posixpath.normpath(raw))
    if wiki_prefix != "." and not raw.casefold().startswith("wiki/"):
        queries.append(posixpath.normpath(posixpath.join(wiki_prefix, raw)))
    return raw, queries


def _supports_hidden_checks() -> bool:
    return (os.open in os.supports_dir_fd and os.stat in os.supports_dir_fd
            and os.stat in os.supports_follow_symlinks
            and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"))


def _hidden_target_queries(
    link: _Link, wiki_prefix: str, source_path: str | None = None,
    within: str | None = None,
) -> list[str]:
    """Return queries naming a dot-prefixed directory or leaf file.

    ``within`` confines the queries to the page root when its parent is not
    a declared vault.
    """
    _, queries = _link_queries(link, wiki_prefix, source_path)
    return [query for query in queries if (
        (parts := PurePosixPath(query).parts)
        and not any(part in {"..", "/"} for part in parts)
        and any(part.startswith(".") for part in parts)
        and (within is None or (len(parts) > 1 and parts[0] == within))
    )]


def _confined_hidden_target(
    root: Path, link: _Link, wiki_prefix: str, source_path: str | None = None,
    within: str | None = None,
) -> str | None:
    """Inspect explicit hidden targets without indexing or reading their payloads.

    Directory descriptors and no-follow stat prevent traversal through swapped
    ancestors or symlinks. Platforms without these primitives fail closed.
    """
    if not _supports_hidden_checks():
        return None
    for query in _hidden_target_queries(link, wiki_prefix, source_path, within):
        variants = [query]
        if not PurePosixPath(query).suffix:
            variants.extend(query + suffix for suffix in sorted(_EXTENSIONLESS_WIKILINK_SUFFIXES))
        for variant in variants:
            descriptor = -1
            try:
                descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                variant_parts = PurePosixPath(variant).parts
                for part in variant_parts[:-1]:
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                    dir_fd=descriptor)
                    os.close(descriptor)
                    descriptor = child
                metadata = os.stat(variant_parts[-1], dir_fd=descriptor, follow_symlinks=False)
                if stat.S_ISREG(metadata.st_mode):
                    return variant
            except OSError:
                continue
            finally:
                if descriptor >= 0:
                    os.close(descriptor)
    return None


class _Resolver:
    def __init__(
        self,
        targets: Sequence[_Target],
        wiki_prefix: str,
        source_paths: Mapping[str, str] | None = None,
    ) -> None:
        self.targets = tuple(targets)
        self.wiki_prefix = wiki_prefix
        self.source_paths = dict(source_paths or {})
        self.by_full: dict[str, list[_Target]] = {}
        self.by_without_link_suffix: dict[str, list[_Target]] = {}
        self.by_basename: dict[str, list[_Target]] = {}
        self.by_alias: dict[str, list[_Target]] = {}
        for target in self.targets:
            full = _name_key(target._canonical_path)
            self.by_full.setdefault(full, []).append(target)
            name = PurePosixPath(target._canonical_path).name
            self.by_basename.setdefault(_name_key(name), []).append(target)
            without_link_suffix = target.without_link_suffix
            if without_link_suffix is not None:
                self.by_without_link_suffix.setdefault(
                    _name_key(without_link_suffix), []
                ).append(target)
                stem = PurePosixPath(without_link_suffix).name
                self.by_basename.setdefault(_name_key(stem), []).append(target)
            if target.page:
                for alias in target.page.frontmatter.aliases:
                    self.by_alias.setdefault(_name_key(alias), []).append(target)

    @staticmethod
    def _deduplicate(candidates: Iterable[_Target]) -> list[_Target]:
        by_path: dict[str, _Target] = {}
        for candidate in candidates:
            by_path[candidate._canonical_path] = candidate
        return sorted(
            by_path.values(),
            key=lambda item: (_path_sort_key(item.path), _path_sort_key(item._canonical_path)),
        )

    def _exact(self, query: str) -> list[_Target]:
        normalized = posixpath.normpath(query.replace("\\", "/")).lstrip("/")
        if normalized in {"", "."}:
            return []
        candidates: list[_Target] = []
        key = _name_key(normalized)
        candidates.extend(self.by_full.get(key, ()))
        candidates.extend(self.by_without_link_suffix.get(key, ()))
        return self._deduplicate(candidates)

    def resolve(self, link: _Link) -> list[_Target]:
        raw, query_options = _link_queries(
            link, self.wiki_prefix, self.source_paths.get(link.source)
        )

        for query in query_options:
            exact = self._exact(query)
            if exact:
                return exact

        if "/" not in raw:
            candidates: list[_Target] = []
            key = _name_key(raw)
            candidates.extend(self.by_basename.get(key, ()))
            candidates.extend(self.by_alias.get(key, ()))
            return self._deduplicate(candidates)

        suffix = _name_key(posixpath.normpath(raw))
        candidates = [
            target
            for target in self.targets
            if _name_key(target._canonical_path).endswith(f"/{suffix}")
            or (
                target.without_link_suffix is not None
                and _name_key(target.without_link_suffix).endswith(f"/{suffix}")
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


_EXCLUDE_KEYS = {
    "exclude",
    "exclude_globs",
    "excluded_paths",
}


def _exclude_values(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return []
    values: list[str] = []
    for key, value in data.items():
        if str(key).casefold() in _EXCLUDE_KEYS and isinstance(value, list):
            values.extend(
                item.strip() for item in value if isinstance(item, str) and item.strip()
            )
    return values


def _normalize_exclude_patterns(values: Sequence[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    result: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError("exclude patterns must be strings")
        stripped = value.strip()
        if stripped:
            result.append(stripped)
    return tuple(result)


def _is_excluded(relative: str, patterns: Sequence[str]) -> bool:
    if not patterns:
        return False
    candidate = relative.casefold()
    return any(
        fnmatch.fnmatchcase(candidate, pattern.casefold()) for pattern in patterns
    )


def _load_allowlist(
    root: Path,
) -> tuple[tuple[str, ...], tuple[str, ...], list[dict[str, str]]]:
    meta = root / ".vault-meta"
    patterns: list[str] = []
    exclude_patterns: list[str] = []
    errors: list[dict[str, str]] = []
    try:
        meta.lstat()
    except FileNotFoundError:
        return (), (), []
    except OSError as exc:
        return (), (), [
            {
                "path": ".vault-meta",
                "message": f"cannot inspect allowlist directory: {exc.__class__.__name__}",
            }
        ]
    if meta.is_symlink() or not meta.is_dir():
        return (), (), [
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
        exclude_patterns.extend(_exclude_values(data))

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
    return (
        tuple(sorted(set(patterns), key=_path_sort_key)),
        tuple(sorted(set(exclude_patterns), key=_path_sort_key)),
        sorted(errors, key=_entry_sort_key),
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


def _frontmatter_policy(
    root: Path, requested: str | None
) -> tuple[str, list[dict[str, str]]]:
    if requested is not None:
        if requested not in {"presence", "generated"}:
            raise ValueError("frontmatter_policy must be 'presence' or 'generated'")
        return requested, []
    configured: set[str] = set()
    errors: list[dict[str, str]] = []
    reader = _transaction_reader()
    for filename in _ALLOWLIST_JSON_NAMES:
        relative = f".vault-meta/{filename}"
        try:
            raw = reader(root, relative, limit=1024 * 1024)
            if raw is None:
                continue
            payload = strict_json_loads(raw.decode("utf-8"))
        except Exception:
            # The allowlist reader already reports unsafe or malformed files.
            continue
        if not isinstance(payload, dict) or "frontmatter_policy" not in payload:
            continue
        policy = payload["frontmatter_policy"]
        if not isinstance(policy, str) or policy not in {"presence", "generated"}:
            errors.append({"path": relative, "message": "frontmatter_policy must be 'presence' or 'generated'"})
        else:
            configured.add(policy)
    if len(configured) > 1:
        errors.append({"path": ".vault-meta", "message": "conflicting frontmatter_policy settings; select one policy"})
    return (next(iter(configured)) if len(configured) == 1 else "presence"), errors


def _generated_frontmatter_errors(page: _Page) -> list[dict[str, Any]]:
    """Validate only the explicit generated-page profile, never adopted schemas."""
    from claude_obsidian.page_schema import PAGE_TYPES

    findings: list[dict[str, Any]] = []
    values = page.frontmatter.values
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in values:
            continue  # Presence is already reported in missing_frontmatter.
        if field in page.frontmatter.duplicate_fields:
            findings.append({
                "path": page.path, "line": page.frontmatter.value_lines[field],
                "field": field, "reason": "duplicate-property",
                "message": "generated required properties must occur exactly once",
            })
        value = values[field]
        message: str | None = None
        if field in {"title", "status"}:
            if not isinstance(value, str) or not value.strip():
                message = f"{field} must be a nonempty text value"
        elif field == "type":
            if not isinstance(value, str) or value not in PAGE_TYPES:
                message = f"type must be one of: {', '.join(PAGE_TYPES)}"
        elif field in {"created", "updated"}:
            if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
                message = f"{field} must be a calendar date in YYYY-MM-DD form"
            else:
                try:
                    date.fromisoformat(value)
                except ValueError:
                    message = f"{field} must be a real calendar date"
        elif field == "tags":
            if not isinstance(value, list):
                message = "tags must be a list of text values"
            elif any(
                not isinstance(tag, str) or not tag
                or all(unicodedata.category(character).startswith("N") for character in tag)
                or any(character.isspace() or unicodedata.category(character) in {"Cc", "Cs"}
                       or character == "#" for character in tag)
                for tag in value
            ):
                message = "tags must contain a nonnumeric character and cannot contain whitespace, hash prefixes or control characters"
        if message:
            findings.append({"path": page.path, "line": page.frontmatter.value_lines[field],
                             "field": field, "message": message})
    return findings


def _unsupported_frontmatter_values(page: _Page) -> list[dict[str, Any]]:
    """Describe the parser boundary without declaring an adopted schema invalid."""
    def outside_subset(value: Any) -> bool:
        if isinstance(value, dict):
            return True
        if isinstance(value, list):
            return any(outside_subset(item) for item in value)
        return False

    return [
        {"path": page.path, "field": field,
         "line": page.frontmatter.value_lines[field],
         "reason": "outside-flat-parser-subset"}
        for field, value in page.frontmatter.values.items()
        if outside_subset(value)
    ]


def _base_view_names(target: _Target) -> tuple[str, ...] | None:
    """Read explicit names in flat Base view mappings, preserving all content.

    This deliberately is not a general YAML loader or a Base formula evaluator.
    Anchors, merge keys, flow mappings and multiline names need native checking.
    """
    try:
        if target.root is None:
            return None
        raw = _transaction_reader()(
            target.root, target._canonical_path, limit=1024 * 1024
        )
        if raw is None:
            return None
        text = raw.decode("utf-8-sig")
    except Exception:
        return None
    if text.lstrip().startswith("{"):
        try:
            data = strict_json_loads(text)
        except ValueError:
            return None
        if not isinstance(data, dict) or not isinstance(data.get("views"), list):
            return None
        names = [view.get("name") if isinstance(view, dict) else None for view in data["views"]]
        return tuple(names) if all(isinstance(name, str) and name for name in names) else None
    lines = text.splitlines()
    view_starts = [index for index, line in enumerate(lines) if re.match(r"^views:", line)]
    if len(view_starts) != 1:
        return None
    index = view_starts[0]
    value = _yaml_without_comment(lines[index].split(":", 1)[1]).strip()
    if value == "[]":
        return ()
    if value:
        return None
    names: list[str] = []
    item_indent: int | None = None
    current_name: str | None = None
    in_item = False
    for line in lines[index + 1:]:
        stripped = _yaml_without_comment(line).strip()
        if not stripped:
            continue
        if "\t" in line[:len(line) - len(line.lstrip())] or "<<:" in stripped:
            return None
        if line == line.lstrip() and not line.startswith("-"):
            break
        item = re.match(r"^( *)-[ ]+(.*)$", line)
        if item and (item_indent is None or len(item.group(1)) == item_indent):
            if in_item:
                if current_name is None:
                    return None
                names.append(current_name)
            item_indent = len(item.group(1))
            current_name = None
            in_item = True
            property_text = item.group(2)
        elif item_indent is not None and len(line) - len(line.lstrip()) == item_indent + 2:
            property_text = line.lstrip()
        else:
            continue
        property_match = _TOP_LEVEL_YAML_KEY_RE.match(property_text)
        if property_match is None:
            return None
        if property_match.group(1) == "name":
            name = _yaml_scalar(property_match.group(2) or "")
            if not isinstance(name, str) or not name or current_name is not None:
                return None
            current_name = name
    if in_item:
        if current_name is None:
            return None
        names.append(current_name)
    return tuple(names)


def _valid_pdf_fragment(fragment: str) -> bool:
    options: dict[str, str] = {}
    for option in fragment.split("&"):
        if option.count("=") != 1:
            return False
        key, value = option.split("=", 1)
        if key not in {"page", "height"} or key in options:
            return False
        if not re.fullmatch(r"[0-9]+", value) or not value.strip("0"):
            return False
        options[key] = value
    return bool(options)


def _heading_path_exists(fragment: str, page: _Page) -> bool:
    # Fragments already name visible text. Rendering them as new inline markup
    # would make literal code headings collide with links that share a label.
    requested = tuple(_normalize_heading(part, render_inline=False) for part in fragment.split("#"))
    if any(not part for part in requested):
        return False
    if len(requested) == 1:
        return requested[0] in page.headings
    for heading_path in page.heading_paths:
        if heading_path[-1] != requested[-1]:
            continue
        cursor = 0
        for heading in heading_path:
            if heading == requested[cursor]:
                cursor += 1
                if cursor == len(requested):
                    return True
    return False


def _fragment_error(link: _Link, target: _Target) -> str | None:
    if link.fragment is None:
        return None
    if target.page is None:
        suffix = PurePosixPath(target.path).suffix.casefold()
        if suffix == ".pdf":
            return None if _valid_pdf_fragment(link.fragment) else "invalid-pdf-fragment"
        if suffix == ".base":
            names = _base_view_names(target)
            if names is None:
                return "base-view-semantics-unsupported"
            matches = names.count(link.fragment)
            if matches > 1:
                return "base-view-ambiguous"
            return None if matches == 1 else "base-view-not-found"
        return "fragment-on-non-markdown-target"
    if link.fragment_kind == "block":
        if link.fragment.casefold() not in target.page.block_ids:
            return "block-not-found"
        return None
    if not _heading_path_exists(link.fragment, target.page):
        return "heading-not-found"
    return None


def _empty_sections(page: _Page) -> list[dict[str, Any]]:
    headings = page.heading_sections

    findings: list[dict[str, Any]] = []
    newlines: list[int] | None = None
    for index, (_, content_start, level, heading) in enumerate(headings):
        content_end = len(page.masked)
        # Index ranges avoid copying the remaining headings for every section.
        for following in range(index + 1, len(headings)):
            following_start, _, following_level, _ = headings[following]
            if following_level <= level:
                content_end = following_start
                break
        # Code is hidden from the heading/link parser, but it is still real
        # section content.  Inspect the original slice and blank only nested
        # heading lines that were confirmed outside code by ``page.masked``.
        section_chars = list(page.text[content_start:content_end])
        for following in range(index + 1, len(headings)):
            nested_start, nested_end, _, _ = headings[following]
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
        section = _mask_comments("".join(section_chars))
        section = re.sub(
            r"^[ \t]*\^[A-Za-z0-9][A-Za-z0-9_-]*[ \t]*$",
            "",
            section,
            flags=re.MULTILINE,
        )
        if section.strip():
            continue
        if newlines is None:
            newlines = _newline_offsets(page.masked)
        line = _line_at(newlines, headings[index][0])
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


def _transaction_error_type() -> type[Exception]:
    try:
        from .transaction import TransactionError
    except ImportError:  # pragma: no cover - direct script compatibility
        package_root = str(Path(__file__).resolve().parents[1])
        if package_root not in sys.path:
            sys.path.insert(0, package_root)
        from claude_obsidian.transaction import TransactionError
    return TransactionError


def _transaction_file_limit() -> int:
    try:
        from .transaction import MAX_TRANSACTION_FILE_BYTES
    except ImportError:  # pragma: no cover - direct script compatibility
        package_root = str(Path(__file__).resolve().parents[1])
        if package_root not in sys.path:
            sys.path.insert(0, package_root)
        from claude_obsidian.transaction import MAX_TRANSACTION_FILE_BYTES
    return MAX_TRANSACTION_FILE_BYTES


def _read_ledger(
    root: Path, relative: str
) -> tuple[Mapping[str, Any] | None, list[dict[str, str]]]:
    """Read one regular vault ledger without following symlinked components."""

    try:
        raw = _transaction_reader()(root, relative, limit=MAX_CANONICAL_LEDGER_BYTES)
        if raw is None:
            return None, []
        try:
            from .ledgers import strict_json_loads
        except ImportError:  # pragma: no cover - direct script compatibility
            from claude_obsidian.ledgers import strict_json_loads
        payload = strict_json_loads(raw.decode("utf-8"))
    except Exception as exc:
        code = getattr(exc, "code", None)
        message = f"cannot read provenance ledger: {exc.__class__.__name__}"
        if isinstance(code, str):
            message += f" {code}"
        if code == "VAULT_FILE_TOO_LARGE":
            message += (
                f"; the ledger exceeds {MAX_CANONICAL_LEDGER_BYTES} bytes. Run "
                "`claude-obsidian.py capacity` and preview `capacity compact`; "
                "never truncate ledger records"
            )
        return None, [{"path": relative, "message": message}]
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
    root: str | os.PathLike[str],
    *,
    as_of: date | str | None = None,
    exclude: Sequence[str] | None = None,
    frontmatter_policy: str | None = None,
) -> dict[str, Any]:
    """Return a deterministic, JSON-serializable lint report.

    ``root`` is normally the vault directory containing ``wiki/``.  Passing a
    directory named ``wiki`` is also supported; its links resolve to parent
    files only when that parent declares ``.claude-obsidian.json``. Symlinked
    files and symlinked directories are not followed.  The function performs
    no filesystem writes.

    ``exclude`` is an optional sequence of shell-style glob patterns (matched
    case-insensitively with :mod:`fnmatch`, where ``*`` also matches ``/``)
    evaluated against each candidate's path relative to ``root``. A matching
    path is dropped before page parsing, so it contributes no page, no
    link-resolution candidate, and no orphan/frontmatter/empty-section/
    stale-index finding. The same patterns may be set vault-side via an
    ``exclude`` (or ``exclude_globs`` / ``excluded_paths``) array in
    ``.vault-meta/lint-allowlist.json``, ``wiki-lint.json``, or ``lint.json``;
    CLI-supplied and vault-config patterns are combined. When ``root`` is the
    ``wiki`` directory itself, relative paths omit the ``wiki/`` prefix, so
    vault-config patterns written as ``wiki/...`` do not match in that mode.

    ``frontmatter_policy='generated'`` opts into canonical page-type, required
    scalar, ISO date and tag-value checks. The default ``presence`` profile
    preserves existing adopted-vault vocabularies. Vault-side lint JSON may
    select the same profile with a ``frontmatter_policy`` property.
    """

    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        raise ValueError(f"vault root is not a directory: {root_path}")
    root_path = root_path.resolve()
    wiki_dir, wiki_prefix = _wiki_location(root_path)
    vault_root = root_path.parent if wiki_prefix == "." else root_path
    canonical_wiki_prefix = wiki_dir.relative_to(vault_root).as_posix()
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
    patterns, config_exclude_patterns, configuration_errors = _load_allowlist(vault_root)
    selected_policy, policy_errors = _frontmatter_policy(vault_root, frontmatter_policy)
    configuration_errors.extend(policy_errors)

    all_paths = _walk_files(root_path)
    exclude_patterns = tuple(
        sorted(
            {*_normalize_exclude_patterns(exclude), *config_exclude_patterns},
            key=_path_sort_key,
        )
    )
    excluded_paths = 0
    markdown_files_discovered = sum(path.suffix.casefold() == ".md" for path in all_paths)
    markdown_files_excluded = 0
    markdown_files_outside_scope = 0
    pages_by_path: dict[str, _Page] = {}
    targets: list[_Target] = []
    read_errors: list[dict[str, str]] = []
    for path in all_paths:
        relative = path.relative_to(root_path).as_posix()
        if _is_excluded(relative, exclude_patterns):
            excluded_paths += 1
            markdown_files_excluded += path.suffix.casefold() == ".md"
            continue
        page: _Page | None = None
        canonical = path.relative_to(vault_root).as_posix()
        if path.suffix.casefold() == ".md":
            if wiki_prefix != "." and not relative.startswith(f"{wiki_prefix}/"):
                markdown_files_outside_scope += 1
            try:
                page = _page_metadata(
                    vault_root, canonical, path, relative, wiki_prefix
                )
                pages_by_path[relative] = page
            except (OSError, UnicodeError, _transaction_error_type()) as exc:
                read_errors.append(
                    {
                        "path": relative,
                        "message": f"unable to read Markdown: {exc.__class__.__name__}",
                    }
                )
        targets.append(
            _Target(
                path=relative,
                absolute=path,
                page=page,
                _canonical_path=canonical,
                root=vault_root,
            )
        )

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

    if not wiki_pages and markdown_files_outside_scope:
        configuration_errors.append({
            "path": wiki_prefix,
            "reason": "no-pages-in-scope",
            "message": "no Markdown pages scanned under wiki/; visible Markdown exists outside the configured page scope",
        })

    resolution_targets = list(targets)
    # A directly linted wiki root resolves parent attachments only inside a
    # declared vault. An arbitrary parent may hold unrelated private projects.
    resolution_scope = (
        None if root_path == vault_root or _is_declared_vault(vault_root)
        else canonical_wiki_prefix
    )
    if resolution_scope is None and root_path != vault_root:
        scanned = set(all_paths)
        for path in _walk_files(vault_root):
            if path in scanned:
                continue
            canonical = path.relative_to(vault_root).as_posix()
            display = Path(os.path.relpath(path, root_path)).as_posix()
            if _is_excluded(display, exclude_patterns):
                continue
            page = None
            if path.suffix.casefold() == ".md":
                try:
                    page = _page_metadata(
                        vault_root, canonical, path, display, wiki_prefix
                    )
                except (OSError, UnicodeError, _transaction_error_type()):
                    pass
            resolution_targets.append(
                _Target(
                    path=display,
                    absolute=path,
                    page=page,
                    _canonical_path=canonical,
                    root=vault_root,
                )
            )

    source_paths = {
        target.path: target._canonical_path
        for target in targets
        if target.page is not None
    }
    resolver = _Resolver(resolution_targets, canonical_wiki_prefix, source_paths)
    gitignore = GitignoreMatcher(vault_root)
    incoming: dict[str, set[str]] = {page.path: set() for page in wiki_pages}
    dead_links: list[dict[str, Any]] = []
    ambiguous_targets: list[dict[str, Any]] = []
    allowlisted: list[dict[str, Any]] = []
    stale_index_entries: list[dict[str, Any]] = []
    hidden_target_links: list[dict[str, Any]] = []
    unsupported_fragments: list[dict[str, Any]] = []
    links_scanned = 0
    property_links_scanned = 0
    pdf_fragments_syntax_checked = 0

    for page in wiki_pages:
        is_index = PurePosixPath(page.path).name.casefold() in {"index.md", "_index.md"}
        for link in _parse_links(page):
            links_scanned += 1
            property_links_scanned += link.syntax == "property-wikilink"
            candidates = resolver.resolve(link)
            if len(candidates) > 1:
                unignored = [
                    candidate
                    for candidate in candidates
                    if not gitignore.is_ignored(candidate._canonical_path)
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
                source_path = source_paths.get(link.source)
                hidden_path = _confined_hidden_target(
                    vault_root, link, canonical_wiki_prefix, source_path,
                    resolution_scope,
                )
                if hidden_path is not None:
                    hidden_target_links.append({
                        "source": link.source, "line": link.line, "target": link.target,
                        "syntax": link.syntax, "reason": "hidden-target-exists-not-indexed",
                        "resolved_path": hidden_path,
                    })
                    continue
                if (not _supports_hidden_checks()
                        and _hidden_target_queries(
                            link, canonical_wiki_prefix, source_path,
                            resolution_scope,
                        )):
                    hidden_target_links.append({
                        "source": link.source, "line": link.line, "target": link.target,
                        "syntax": link.syntax, "reason": "hidden-target-status-unverified",
                    })
                    continue
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
                if link.fragment is not None and PurePosixPath(candidate.path).suffix.casefold() == ".pdf":
                    pdf_fragments_syntax_checked += 1
                continue
            if fragment_reason == "base-view-semantics-unsupported":
                unsupported_fragments.append({
                    "source": link.source, "line": link.line, "target": link.target,
                    "syntax": link.syntax, "reason": fragment_reason,
                    "resolved_path": candidate.path,
                })
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
        basename_groups.setdefault(_name_key(PurePosixPath(page.path).stem), []).append(
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
    invalid_frontmatter: list[dict[str, Any]] = []
    unsupported_frontmatter_values: list[dict[str, Any]] = []
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
        if selected_policy == "generated":
            invalid_frontmatter.extend(_generated_frontmatter_errors(page))
        unsupported_frontmatter_values.extend(_unsupported_frontmatter_values(page))
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
    hidden_target_links.sort(key=_entry_sort_key)
    unsupported_fragments.sort(key=_entry_sort_key)
    invalid_frontmatter.sort(key=_entry_sort_key)
    unsupported_frontmatter_values.sort(key=_entry_sort_key)

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
        "hidden_target_links": hidden_target_links,
        "unsupported_fragments": unsupported_fragments,
        "invalid_frontmatter": invalid_frontmatter,
    }
    category_counts = {name: len(entries) for name, entries in categories.items()}
    issues_found = sum(category_counts.values())
    if not wiki_pages and markdown_files_outside_scope:
        coverage = "no-pages-in-scope"
    elif markdown_files_outside_scope or markdown_files_excluded or read_errors:
        coverage = "partial"
    elif not markdown_files_discovered:
        coverage = "empty"
    else:
        coverage = "complete"

    report: dict[str, Any] = {
        "version": REPORT_VERSION,
        "engine_version": ENGINE_VERSION,
        "as_of": audit_date.isoformat(),
        "summary": {
            "pages_scanned": len(wiki_pages),
            "links_scanned": links_scanned,
            "issues_found": issues_found,
            "allowlisted_dangling_links": len(allowlisted),
            "excluded_paths": excluded_paths,
            "markdown_files_discovered": markdown_files_discovered,
            "markdown_files_excluded": markdown_files_excluded,
            "markdown_files_outside_scope": markdown_files_outside_scope,
            "link_targets_indexed": len(targets),
            "property_links_scanned": property_links_scanned,
            "pdf_fragments_syntax_checked": pdf_fragments_syntax_checked,
            "unsupported_frontmatter_values": len(unsupported_frontmatter_values),
            "category_counts": category_counts,
        },
        "scope": {
            "page_root": wiki_prefix,
            "coverage": coverage,
            "frontmatter_policy": selected_policy,
            "frontmatter_values_coverage": "partial" if unsupported_frontmatter_values else "complete",
            "unsupported_frontmatter_values": unsupported_frontmatter_values,
            "limitations": [
                "Hidden directories and symlinks are excluded from graph candidates",
                "Hidden target existence checks require no-follow directory descriptor support",
                "Only quoted flat text/list property wikilinks are scanned; aliases remain names",
                "Frontmatter value coverage describes the bounded parser subset, not full YAML semantics",
                "PDF page counts and rendering are not checked",
                "Base formulas, YAML anchors and complex view syntax require native validation",
                "Same-stem Markdown, Base and Canvas precedence is unverified; ambiguity is retained",
            ],
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
        f"- Excluded paths: {summary.get('excluded_paths', 0)}",
        f"- Issues found: {summary.get('issues_found', 0)}",
        f"- Allowlisted dangling links: {summary.get('allowlisted_dangling_links', 0)}",
    ]
    scope = report.get("scope")
    if isinstance(scope, dict):
        lines.extend([
            f"- Page scope: {_code(scope.get('page_root', 'unknown'))}",
            f"- Coverage: {_code(scope.get('coverage', 'unknown'))}",
            f"- Frontmatter policy: {_code(scope.get('frontmatter_policy', 'unknown'))}",
            f"- Frontmatter value coverage: {_code(scope.get('frontmatter_values_coverage', 'unknown'))}",
            f"- Markdown files discovered: {summary.get('markdown_files_discovered', 0)}",
            f"- Markdown files outside page scope: {summary.get('markdown_files_outside_scope', 0)}",
            f"- Markdown files excluded: {summary.get('markdown_files_excluded', 0)}",
            f"- Property links scanned: {summary.get('property_links_scanned', 0)}",
            f"- PDF fragments checked for syntax only: {summary.get('pdf_fragments_syntax_checked', 0)}",
        ])

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
            "Frontmatter Values",
            "invalid_frontmatter",
            lambda item: (
                f"- {_code(item['path'])}:{item['line']}: {_code(item['field'])}: {item['message']}"
            ),
        ),
        (
            "Hidden Target Links",
            "hidden_target_links",
            lambda item: (
                f"- {_code(item['source'])}:{item['line']} -> {_code(item['target'])}; "
                + (f"existing hidden file {_code(item['resolved_path'])} is outside the Obsidian graph"
                   if item.get("resolved_path") else "hidden target status requires no-follow directory descriptor support")
            ),
        ),
        (
            "Unsupported Fragment Checks",
            "unsupported_fragments",
            lambda item: (
                f"- {_code(item['source'])}:{item['line']} -> {_code(item['target'])}: {item['reason']}"
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
    if isinstance(scope, dict) and isinstance(scope.get("limitations"), list):
        unsupported_values = scope.get("unsupported_frontmatter_values", [])
        if isinstance(unsupported_values, list) and unsupported_values:
            lines.extend(["", "## Frontmatter Parser Scope", ""])
            lines.extend(
                f"- {_code(item['path'])}:{item['line']}: {_code(item['field'])}: {item['reason']}"
                for item in unsupported_values
            )
        lines.extend(["", "## Coverage Limits", ""])
        lines.extend(f"- {limitation}" for limitation in scope["limitations"])
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
