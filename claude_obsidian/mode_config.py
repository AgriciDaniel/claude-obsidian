"""Shared validation for methodology-mode filing paths."""

from __future__ import annotations

import unicodedata
from pathlib import PurePosixPath
from typing import Any, Mapping


MODE_FOLDER_KEYS = {
    "generic": (
        "sources_folder",
        "entities_folder",
        "concepts_folder",
        "sessions_folder",
        "questions_folder",
    ),
    "lyt": ("moc_folder", "notes_folder"),
    "para": ("projects_folder", "areas_folder", "resources_folder", "archives_folder"),
    "zettelkasten": ("root_folder",),
}

def _has_control(value: str) -> bool:
    return any(unicodedata.category(character).startswith("C") for character in value)


def validate_wiki_folder(value: Any, *, field: str) -> str:
    """Return one canonical trailing-slash folder rooted below ``wiki/``."""

    if (
        not isinstance(value, str)
        or not value.endswith("/")
        or "\\" in value
        or _has_control(value)
    ):
        raise ValueError(f"{field} must be a canonical wiki/ folder")
    raw = value[:-1]
    parsed = PurePosixPath(raw)
    if (
        not raw
        or parsed.is_absolute()
        or parsed.as_posix() != raw
        or not parsed.parts
        or parsed.parts[0] != "wiki"
        or any(part in {"", ".", ".."} for part in parsed.parts)
    ):
        raise ValueError(f"{field} must be a canonical wiki/ folder")
    return value


def validate_mode_folders(document: Mapping[str, Any]) -> None:
    """Validate every built-in methodology folder without rejecting extensions."""

    config = document.get("config")
    if not isinstance(config, Mapping):
        raise ValueError("mode config must contain a configuration object")
    for mode_name, folder_keys in MODE_FOLDER_KEYS.items():
        settings = config.get(mode_name)
        if not isinstance(settings, Mapping):
            raise ValueError(f"mode config section {mode_name!r} must be an object")
        for key in folder_keys:
            validate_wiki_folder(settings.get(key), field=f"config.{mode_name}.{key}")


def validate_wiki_route(value: Any) -> str:
    """Return one canonical Markdown page path contained below ``wiki/``."""

    if not isinstance(value, str) or "\\" in value or _has_control(value):
        raise ValueError("routed page must be a canonical wiki Markdown path")
    parsed = PurePosixPath(value)
    if (
        parsed.is_absolute()
        or parsed.as_posix() != value
        or len(parsed.parts) < 2
        or parsed.parts[0] != "wiki"
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or parsed.suffix.lower() != ".md"
    ):
        raise ValueError("routed page must be a canonical wiki Markdown path")
    return value


__all__ = [
    "MODE_FOLDER_KEYS",
    "validate_mode_folders",
    "validate_wiki_folder",
    "validate_wiki_route",
]
