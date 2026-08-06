"""Pure-Python ``.gitignore`` evaluation for the deterministic lint engine.

This module reads ``.gitignore`` files found inside a scan root and answers
whether a relative path is ignored, following the documented gitignore
semantics that matter for link resolution:

- later patterns override earlier ones; deeper ``.gitignore`` files override
  shallower ones;
- ``!`` negation re-includes a previously excluded path;
- a pattern containing a non-trailing ``/`` is anchored to its
  ``.gitignore`` directory, otherwise it matches at any depth;
- a trailing ``/`` restricts a pattern to directories;
- ``*`` and ``?`` never cross ``/``; ``**`` does;
- everything inside an excluded directory stays excluded (``.gitignore``
  files inside excluded directories are not read).

Scope is deliberately narrow and deterministic: only ``.gitignore`` files
within the scan root are consulted — never ``.git/info/exclude``, the global
``core.excludesFile``, or a ``git`` subprocess. Matching is always
case-sensitive (git's default), even on case-insensitive filesystems where
git with ``core.ignorecase=true`` would fold case; reading git config would
break the process-free contract. Symlinked ``.gitignore`` files are skipped,
matching the engine's symlink hygiene.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_MAX_GITIGNORE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class _Rule:
    regex: re.Pattern[str]
    negate: bool
    dir_only: bool


def _translate_segment(segment: str) -> str:
    parts: list[str] = []
    index = 0
    while index < len(segment):
        char = segment[index]
        if char == "\\" and index + 1 < len(segment):
            parts.append(re.escape(segment[index + 1]))
            index += 2
            continue
        if char == "*":
            parts.append("[^/]*")
        elif char == "?":
            parts.append("[^/]")
        elif char == "[":
            end = segment.find("]", index + 2)
            if end < 0:
                parts.append(re.escape(char))
            else:
                inner = segment[index + 1 : end]
                if inner.startswith("!"):
                    inner = "^" + inner[1:]
                parts.append(f"[{inner}]")
                index = end + 1
                continue
        else:
            parts.append(re.escape(char))
        index += 1
    return "".join(parts)


def _translate(pattern: str) -> str:
    segments = pattern.split("/")
    parts: list[str] = []
    for position, segment in enumerate(segments):
        last = position == len(segments) - 1
        if segment == "**":
            if position == 0:
                parts.append("(?:[^/]+/)*" if not last else ".*")
            elif last:
                parts.append(".*")
            else:
                parts.append("(?:[^/]+/)*")
            continue
        parts.append(_translate_segment(segment) + ("" if last else "/"))
    return "".join(parts)


def _parse_line(line: str) -> _Rule | None:
    line = line.rstrip("\r\n")
    if not line or line.startswith("#"):
        return None
    while line.endswith(" ") and not line.endswith("\\ "):
        line = line[:-1]
    if not line:
        return None
    negate = line.startswith("!")
    if negate:
        line = line[1:]
    elif line.startswith("\\!") or line.startswith("\\#"):
        line = line[1:]
    dir_only = line.endswith("/")
    if dir_only:
        line = line.rstrip("/")
    if not line:
        return None
    anchored = line.startswith("/") or "/" in line
    line = line.lstrip("/")
    if not line:
        return None
    prefix = "" if anchored else "(?:.*/)?"
    try:
        regex = re.compile(prefix + _translate(line))
    except re.error:
        return None
    return _Rule(regex=regex, negate=negate, dir_only=dir_only)


def _parse_gitignore(path: Path) -> tuple[_Rule, ...]:
    try:
        if path.is_symlink() or not path.is_file():
            return ()
        if path.stat().st_size > _MAX_GITIGNORE_BYTES:
            return ()
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()
    rules = []
    for line in text.splitlines():
        rule = _parse_line(line)
        if rule is not None:
            rules.append(rule)
    return tuple(rules)


class GitignoreMatcher:
    """Lazily evaluate gitignore status for paths relative to ``root``.

    Paths use POSIX separators and are relative to the scan root. Results are
    cached; the matcher performs only file reads and never writes.
    """

    def __init__(self, root: Path) -> None:
        self._root = root
        self._rules: dict[str, tuple[_Rule, ...]] = {}
        self._dir_ignored: dict[str, bool] = {"": False}

    def _rules_for(self, rel_dir: str) -> tuple[_Rule, ...]:
        cached = self._rules.get(rel_dir)
        if cached is None:
            absolute = self._root if rel_dir == "" else self._root / rel_dir
            cached = _parse_gitignore(absolute / ".gitignore")
            self._rules[rel_dir] = cached
        return cached

    def _match(self, rel_path: str, is_dir: bool) -> bool | None:
        """Return the last matching rule's verdict across scopes, or None."""
        parent = str(PurePosixPath(rel_path).parent)
        if parent == ".":
            parent = ""
        scopes = [""]
        if parent:
            pieces = parent.split("/")
            for index in range(len(pieces)):
                scopes.append("/".join(pieces[: index + 1]))
        verdict: bool | None = None
        for scope in scopes:
            if scope == "":
                candidate = rel_path
            else:
                candidate = rel_path[len(scope) + 1 :]
            for rule in self._rules_for(scope):
                if rule.dir_only and not is_dir:
                    continue
                if rule.regex.fullmatch(candidate):
                    verdict = not rule.negate
        return verdict

    def _is_dir_ignored(self, rel_dir: str) -> bool:
        cached = self._dir_ignored.get(rel_dir)
        if cached is not None:
            return cached
        parent = str(PurePosixPath(rel_dir).parent)
        if parent == ".":
            parent = ""
        if self._is_dir_ignored(parent):
            result = True
        else:
            result = self._match(rel_dir, is_dir=True) is True
        self._dir_ignored[rel_dir] = result
        return result

    def is_ignored(self, rel_path: str) -> bool:
        """Return True when the file at ``rel_path`` is gitignored."""
        normalized = rel_path.strip("/")
        if not normalized:
            return False
        parent = str(PurePosixPath(normalized).parent)
        if parent == ".":
            parent = ""
        if parent and self._is_dir_ignored(parent):
            return True
        return self._match(normalized, is_dir=False) is True
