#!/usr/bin/env python3
"""wiki-mode.py — read + route helper for v1.8 methodology modes.

Single source of truth for "which mode is this vault in" and "where should
new content of type X be filed under mode Y." Consumed by:

  - skills/wiki-ingest/SKILL.md  (where to file new source/entity/concept pages)
  - skills/save/SKILL.md         (where to file session notes)
  - skills/autoresearch/SKILL.md (where to file research output)
  - bin/setup-mode.sh            (delegates configuration to the transaction core)

If `.vault-meta/mode.json` is absent → mode = "generic" → behavior identical
to v1.7. No skill needs to special-case the missing-config path.

CLI:
  wiki-mode.py --vault PATH get         # select a vault explicitly
  wiki-mode.py get                      # print current mode (default: generic)
  wiki-mode.py config                   # print full config JSON
  wiki-mode.py route TYPE NAME          # print suggested path for new content
                                        # TYPE: source|entity|concept|session|research
  wiki-mode.py id                       # mint a Zettelkasten ID (timestamp)
  wiki-mode.py templates                # list per-mode template files

Exit codes:
  0 — success
  2 — usage error
  3 — invalid mode string
  4 — invalid content type
  5 — existing mode configuration is invalid
"""

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from claude_obsidian.mode_config import validate_mode_folders, validate_wiki_route
from claude_obsidian.page_schema import (
    LEGACY_TYPE_ALIASES,
    ROUTABLE_TYPES,
    route_rejection_reason,
)
from claude_obsidian.ledgers import strict_json_loads
from claude_obsidian.paths import VaultSelectionError, resolve_vault_root
from claude_obsidian.transaction import (
    TransactionError,
    _safe_vault_path,
    read_vault_regular,
)

VAULT_ROOT = Path.cwd().resolve()
META_DIR = VAULT_ROOT / ".vault-meta"
MODE_PATH = META_DIR / "mode.json"

VALID_MODES = ("generic", "lyt", "para", "zettelkasten")
# Derived, never restated: claude_obsidian.page_schema is the one declaration.
# The legacy `research` alias stays accepted on the command line.
VALID_TYPES = ROUTABLE_TYPES + tuple(LEGACY_TYPE_ALIASES)
ZETTEL_ID_FORMAT = "YYYYMMDDHHMMSSffffff-UUID4HEX"
MAX_COMPONENT_BYTES = 255
_WINDOWS_RESERVED_STEMS = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "CONIN$",
    "CONOUT$",
    "CLOCK$",
}

DEFAULT_CONFIG = {
    "schema_version": 1,
    "mode": "generic",
    "configured_at": None,
    "config": {
        "lyt": {
            "moc_folder": "wiki/mocs/",
            "notes_folder": "wiki/notes/",
        },
        "para": {
            "projects_folder": "wiki/projects/",
            "areas_folder": "wiki/areas/",
            "resources_folder": "wiki/resources/",
            "archives_folder": "wiki/archives/",
        },
        "zettelkasten": {
            "id_format": ZETTEL_ID_FORMAT,
            "no_folders": True,
            "root_folder": "wiki/",
        },
        "generic": {
            "sources_folder": "wiki/sources/",
            "entities_folder": "wiki/entities/",
            "concepts_folder": "wiki/concepts/",
            "sessions_folder": "wiki/sessions/",
            "questions_folder": "wiki/questions/",
        },
    },
}


def default_config():
    """Return an isolated copy so partial config merges never mutate defaults."""
    return json.loads(json.dumps(DEFAULT_CONFIG))


def configure_vault(explicit=None):
    """Select vault state independently from the plugin installation root."""
    global VAULT_ROOT, META_DIR, MODE_PATH
    try:
        selection = resolve_vault_root(
            explicit,
            start=Path.cwd(),
            plugin_root=PLUGIN_ROOT,
        )
    except VaultSelectionError as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        return False
    VAULT_ROOT = selection.root
    META_DIR = VAULT_ROOT / ".vault-meta"
    MODE_PATH = META_DIR / "mode.json"
    try:
        _safe_vault_path(VAULT_ROOT, ".vault-meta")
        _safe_vault_path(VAULT_ROOT, ".vault-meta/mode.json")
    except (VaultSelectionError, TransactionError) as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        return False
    return True


def load_config():
    """Return parsed mode.json, or DEFAULT_CONFIG with mode='generic' if absent."""
    try:
        raw = read_vault_regular(
            VAULT_ROOT,
            ".vault-meta/mode.json",
            limit=1024 * 1024,
        )
    except TransactionError as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if raw is None:
        return default_config()
    try:
        loaded = strict_json_loads(raw.decode("utf-8"))
        if not isinstance(loaded, dict) or loaded.get("mode", "generic") not in VALID_MODES:
            raise ValueError("root must be an object with a supported mode")
        # Merge with defaults so partially-configured files still work
        merged = default_config()
        merged["mode"] = loaded.get("mode", "generic")
        merged["configured_at"] = loaded.get("configured_at")
        loaded_config = loaded.get("config", {})
        if not isinstance(loaded_config, dict):
            raise ValueError("config must be an object")
        for k, v in loaded_config.items():
            if k in merged["config"] and isinstance(v, dict):
                merged["config"][k].update(v)
        # The historical field was descriptive and the helper never executed
        # custom formats. Report the effective allocator format so legacy
        # metadata cannot contradict routing behavior. A reviewed `mode set`
        # persists this normalized value through the transaction core.
        merged["config"]["zettelkasten"]["id_format"] = ZETTEL_ID_FORMAT
        validate_mode_folders(merged)
        return merged
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
        print(f"ERR: cannot parse {MODE_PATH}: {e}", file=sys.stderr)
        print(
            "  Existing mode configuration is invalid; repair it before routing.",
            file=sys.stderr,
        )
        raise SystemExit(5) from e

def slugify(name):
    """Filesystem-safe slug; matches the convention used by the existing skills.
    Any run of non-word, non-hyphen characters becomes a single hyphen so that
    'v1.8 launch! prep?' → 'v1-8-launch-prep' (not 'v18launchprep').
    Unicode word characters (CJK, accented Latin, Cyrillic, etc.) are preserved.
    """
    s = re.sub(r"[^\w\-]+", "-", name, flags=re.UNICODE)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "untitled"


def safe_name(name):
    """Sanitize a name that intentionally preserves case + spaces (entity/concept).
    Strips path separators, null bytes, control characters, and leading dots or
    hyphens so the returned string cannot escape its parent directory or be
    interpreted as a hidden file or flag. Spaces and case are preserved.
    """
    cleaned = re.sub(r"[/\\\x00-\x1f\x7f<>:\"|?*\ud800-\udfff]+", "", name)
    cleaned = cleaned.lstrip(".- ").rstrip(". ")
    return cleaned or "untitled"


def _portable_stem(stem):
    """Return a non-reserved filename stem for common desktop filesystems."""
    candidate = stem.rstrip(". ") or "untitled"
    # Windows treats a device token as reserved even when another extension is
    # appended (for example, CON.txt). Superscript 1/2/3 are also recognized as
    # COM/LPT digits by the Win32 namespace.
    device_token = candidate.split(".", 1)[0].rstrip(". ").upper()
    numbered_device = re.fullmatch(r"(?:COM|LPT)(?:[1-9]|[¹²³])", device_token)
    if device_token in _WINDOWS_RESERVED_STEMS or numbered_device:
        candidate = "_" + candidate
    return candidate


def _bounded_stem(stem, max_bytes):
    """Fit a stem in a UTF-8 byte budget without splitting a code point.

    When truncation is necessary, retain a deterministic SHA-256 suffix so two
    long names with the same visible prefix do not silently alias.
    """
    candidate = _portable_stem(stem)
    encoded = candidate.encode("utf-8")
    if len(encoded) <= max_bytes:
        return candidate
    digest_suffix = "-" + hashlib.sha256(encoded).hexdigest()[:16]
    prefix_budget = max_bytes - len(digest_suffix.encode("ascii"))
    if prefix_budget < 1:
        raise ValueError("filename byte budget is too small")
    readable = encoded[:prefix_budget].decode("utf-8", errors="ignore")
    readable = readable.rstrip("-. ") or "u"
    result = readable + digest_suffix
    if len(result.encode("utf-8")) > max_bytes:
        raise AssertionError("bounded filename stem exceeded its byte budget")
    return result


def _markdown_filename(stem, prefix=""):
    """Build one portable Markdown leaf component within the 255-byte floor."""
    suffix = ".md"
    fixed_bytes = len(prefix.encode("utf-8")) + len(suffix.encode("ascii"))
    bounded = _bounded_stem(stem, MAX_COMPONENT_BYTES - fixed_bytes)
    filename = prefix + bounded + suffix
    if len(filename.encode("utf-8")) > MAX_COMPONENT_BYTES:
        raise AssertionError("Markdown filename exceeded its component limit")
    return filename


def mint_zettel_id():
    """Return a time-sortable UTC prefix plus an independent UUIDv4 nonce.

    Wall-clock microseconds alone are not injective: rapid calls can observe the
    same clock value, and separate processes have no shared counter. The UUIDv4
    suffix makes IDs collision-resistant across batches and processes without
    writing allocator state or weakening this helper's read-only contract.
    Existing timestamp-only filenames remain valid and are never renamed.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{timestamp}-{uuid.uuid4().hex}"


def route_path(mode, content_type, name, cfg):
    """Return the suggested vault-relative path for new content under `mode`."""
    reason = route_rejection_reason(content_type)
    if reason is not None:
        # Was a bare SystemExit(4): a caller could not tell a typo from a valid
        # page type that simply has no filing destination.
        print(f"ERR: {reason}", file=sys.stderr)
        raise SystemExit(4)
    slug = slugify(name)

    raw = safe_name(name)  # case + spaces preserved, but path-traversal stripped

    if mode == "generic":
        g = cfg["config"]["generic"]
        mapping = {
            "source":   g["sources_folder"] + _markdown_filename(slug),
            "entity":   g["entities_folder"] + _markdown_filename(raw),
            "concept":  g["concepts_folder"] + _markdown_filename(raw),
            "session":  g["sessions_folder"] + _markdown_filename(slug),
            "question": g["questions_folder"] + _markdown_filename(slug),
            # Legacy alias of `concept`; its existing destination is preserved
            # rather than rewritten, so accepted calls keep their exact paths.
            "research": g["concepts_folder"] + _markdown_filename(raw),
        }
        result = mapping[content_type]

    elif mode == "lyt":
        notes = cfg["config"]["lyt"]["notes_folder"]
        # All atomic notes flat in wiki/notes/; routing is the same regardless of type
        result = notes + _markdown_filename(slug)

    elif mode == "para":
        p = cfg["config"]["para"]
        research_stem = _bounded_stem(slug, MAX_COMPONENT_BYTES - len(".md"))
        mapping = {
            # New sources land in resources/<topic>/ (we use a generic 'incoming' bucket;
            # the user will sort into specific topics via their own workflow)
            "source":   p["resources_folder"] + "incoming/" + _markdown_filename(slug),
            "entity":   p["resources_folder"] + "people/" + _markdown_filename(raw),
            "concept":  p["resources_folder"] + "concepts/" + _markdown_filename(raw),
            # Session notes land in projects/inbox/; user reroutes to specific projects
            "session":  p["projects_folder"] + "inbox/" + _markdown_filename(slug),
            "question": p["resources_folder"] + "questions/" + _markdown_filename(slug),
            "research": p["resources_folder"] + research_stem + "/" + research_stem + ".md",
        }
        result = mapping[content_type]

    elif mode == "zettelkasten":
        z = cfg["config"]["zettelkasten"]
        zid = mint_zettel_id()
        result = z["root_folder"] + _markdown_filename(slug, prefix=f"{zid}-")

    else:
        raise SystemExit(3)
    return validate_wiki_route(result)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Methodology-mode router for v1.8 Compound Vault.")
    parser.add_argument("--vault", help="Explicit vault root (overrides environment and cwd discovery)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("get", help="Print current mode")
    sub.add_parser("config", help="Print full config JSON")

    sp_route = sub.add_parser("route", help="Print suggested vault path for new content")
    # No argparse `choices` here on purpose: it rejects before route_path runs, so
    # every bad type produced the same usage dump and a valid-but-unroutable type
    # was indistinguishable from a typo. route_path owns the explanation.
    sp_route.add_argument(
        "type",
        metavar="TYPE",
        help="Page type to file. Routable: " + ", ".join(VALID_TYPES),
    )
    sp_route.add_argument("name", help="Content name (will be slugified for filenames)")
    sp_route.add_argument("--mode", choices=VALID_MODES, default=None,
                          help="Preview routing under MODE without writing mode.json (default: use current vault mode)")

    sub.add_parser("id", help="Mint a Zettelkasten ID (timestamp)")
    sub.add_parser("templates", help="List per-mode template files")

    # Accept --vault after the subcommand as well as before it. Extract it in a
    # tiny pre-pass, then let the existing subparser validate everything else.
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    vault_parser = argparse.ArgumentParser(add_help=False)
    vault_parser.add_argument("--vault")
    vault_args, remaining = vault_parser.parse_known_args(raw_argv)
    args = parser.parse_args(remaining)
    args.vault = vault_args.vault
    if not configure_vault(args.vault):
        return 2
    cfg = load_config()

    if args.cmd == "get":
        print(cfg["mode"])
        return 0

    if args.cmd == "config":
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "route":
        active_mode = args.mode if args.mode else cfg["mode"]
        path = route_path(active_mode, args.type, args.name, cfg)
        print(path)
        return 0

    if args.cmd == "id":
        print(mint_zettel_id())
        return 0

    if args.cmd == "templates":
        templates_dir = PLUGIN_ROOT / "skills" / "wiki-mode" / "templates"
        if not templates_dir.is_dir():
            print(f"ERR: templates dir missing: {templates_dir}", file=sys.stderr)
            return 2
        for f in sorted(templates_dir.rglob("*.md")):
            print(str(f.relative_to(PLUGIN_ROOT)))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
