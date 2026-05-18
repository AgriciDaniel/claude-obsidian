#!/usr/bin/env python3
"""wiki-mode.py — read + route helper for v1.8 methodology modes.

Single source of truth for "which mode is this vault in" and "where should
new content of type X be filed under mode Y." Consumed by:

  - skills/wiki-ingest/SKILL.md  (where to file new source/entity/concept pages)
  - skills/save/SKILL.md         (where to file session notes)
  - skills/autoresearch/SKILL.md (where to file research output)
  - bin/setup-mode.sh            (writes .vault-meta/mode.json)

If `.vault-meta/mode.json` is absent → mode = "generic" → behavior identical
to v1.7. No skill needs to special-case the missing-config path.

CLI:
  wiki-mode.py get                      # print current mode (default: generic)
  wiki-mode.py config                   # print full config JSON
  wiki-mode.py route TYPE NAME          # print suggested path for new content
                                        # TYPE: source|entity|concept|session|research
  wiki-mode.py set MODE                 # write mode (lyt|para|zettelkasten|generic)
  wiki-mode.py id                       # mint a Zettelkasten ID (timestamp)
  wiki-mode.py templates                # list per-mode template files

Exit codes:
  0 — success
  2 — usage error
  3 — invalid mode string
  4 — invalid content type
"""

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
META_DIR = VAULT_ROOT / ".vault-meta"
MODE_PATH = META_DIR / "mode.json"

VALID_MODES = ("generic", "lyt", "para", "zettelkasten")
VALID_TYPES = ("source", "entity", "concept", "session", "research")

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
            "id_format": "YYYYMMDDHHMMSSffffff",
            "no_folders": True,
            "root_folder": "wiki/",
        },
        "generic": {
            "sources_folder": "wiki/sources/",
            "entities_folder": "wiki/entities/",
            "concepts_folder": "wiki/concepts/",
            "sessions_folder": "wiki/sessions/",
        },
    },
}


def load_config():
    """Return parsed mode.json, or DEFAULT_CONFIG with mode='generic' if absent."""
    if not MODE_PATH.is_file():
        return dict(DEFAULT_CONFIG)
    try:
        loaded = json.loads(MODE_PATH.read_text(encoding="utf-8"))
        # Merge with defaults so partially-configured files still work
        merged = dict(DEFAULT_CONFIG)
        merged["mode"] = loaded.get("mode", "generic")
        merged["configured_at"] = loaded.get("configured_at")
        loaded_config = loaded.get("config", {})
        for k, v in loaded_config.items():
            if k in merged["config"] and isinstance(v, dict):
                merged["config"][k].update(v)
        return merged
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERR: cannot parse {MODE_PATH}: {e}", file=sys.stderr)
        print("  Falling back to mode=generic. Re-run `bash bin/setup-mode.sh` to fix.",
              file=sys.stderr)
        return dict(DEFAULT_CONFIG)


def save_config(cfg):
    META_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"
    fd, tmp_path = tempfile.mkstemp(prefix="mode.", suffix=".tmp", dir=str(META_DIR))
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
        Path(tmp_path).replace(MODE_PATH)
    except Exception:
        try:
            Path(tmp_path).unlink()
        except OSError:
            pass
        raise


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
    cleaned = re.sub(r"[/\\\x00-\x1f]+", "", name)
    cleaned = cleaned.lstrip(".-")
    return cleaned or "untitled"


def mint_zettel_id():
    """YYYYMMDDHHMMSSffffff in UTC (microsecond resolution).
    Stable across timezones; lexicographically sortable; collision-resistant
    against rapid back-to-back calls in the same second. Microsecond suffix
    closes the v1.8.0 verifier LOW (two rapid mint calls produced the same
    14-digit ID and would have generated colliding filenames).
    """
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def route_path(mode, content_type, name, cfg):
    """Return the suggested vault-relative path for new content under `mode`."""
    if content_type not in VALID_TYPES:
        raise SystemExit(4)
    slug = slugify(name)

    raw = safe_name(name)  # case + spaces preserved, but path-traversal stripped

    if mode == "generic":
        g = cfg["config"]["generic"]
        mapping = {
            "source":   g["sources_folder"] + slug + ".md",
            "entity":   g["entities_folder"] + raw + ".md",  # preserve capitalization for entities
            "concept":  g["concepts_folder"] + raw + ".md",
            "session":  g["sessions_folder"] + slug + ".md",
            "research": g["concepts_folder"] + raw + ".md",
        }
        return mapping[content_type]

    if mode == "lyt":
        notes = cfg["config"]["lyt"]["notes_folder"]
        # All atomic notes flat in wiki/notes/; routing is the same regardless of type
        return notes + slug + ".md"

    if mode == "para":
        p = cfg["config"]["para"]
        mapping = {
            # New sources land in resources/<topic>/ (we use a generic 'incoming' bucket;
            # the user will sort into specific topics via their own workflow)
            "source":   p["resources_folder"] + "incoming/" + slug + ".md",
            "entity":   p["resources_folder"] + "people/" + raw + ".md",
            "concept":  p["resources_folder"] + "concepts/" + raw + ".md",
            # Session notes land in projects/inbox/; user reroutes to specific projects
            "session":  p["projects_folder"] + "inbox/" + slug + ".md",
            "research": p["resources_folder"] + slug + "/" + slug + ".md",
        }
        return mapping[content_type]

    if mode == "zettelkasten":
        z = cfg["config"]["zettelkasten"]
        zid = mint_zettel_id()
        return z["root_folder"] + f"{zid}-{slug}.md"

    raise SystemExit(3)


def main():
    parser = argparse.ArgumentParser(description="Methodology-mode router for v1.8 Compound Vault.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("get", help="Print current mode")
    sub.add_parser("config", help="Print full config JSON")

    sp_route = sub.add_parser("route", help="Print suggested vault path for new content")
    sp_route.add_argument("type", choices=VALID_TYPES)
    sp_route.add_argument("name", help="Content name (will be slugified for filenames)")
    sp_route.add_argument("--mode", choices=VALID_MODES, default=None,
                          help="Preview routing under MODE without writing mode.json (default: use current vault mode)")

    sp_set = sub.add_parser("set", help="Write a mode to .vault-meta/mode.json")
    sp_set.add_argument("mode", choices=VALID_MODES)

    sub.add_parser("id", help="Mint a Zettelkasten ID (timestamp)")
    sub.add_parser("templates", help="List per-mode template files")

    args = parser.parse_args()
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

    if args.cmd == "set":
        cfg["mode"] = args.mode
        cfg["configured_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        save_config(cfg)
        print(f"mode set: {args.mode}")
        return 0

    if args.cmd == "id":
        print(mint_zettel_id())
        return 0

    if args.cmd == "templates":
        templates_dir = VAULT_ROOT / "skills" / "wiki-mode" / "templates"
        if not templates_dir.is_dir():
            print(f"ERR: templates dir missing: {templates_dir}", file=sys.stderr)
            return 2
        for f in sorted(templates_dir.rglob("*.md")):
            print(str(f.relative_to(VAULT_ROOT)))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
