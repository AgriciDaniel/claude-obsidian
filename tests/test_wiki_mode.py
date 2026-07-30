#!/usr/bin/env python3
"""test_wiki_mode.py — hermetic tests for scripts/wiki-mode.py.

Covers config load/save round-trip, all 4 modes' routing, slugification, ID
minting, and the default-to-generic fallback when .vault-meta/mode.json is
absent. No network, no LLM, no ollama. Pure stdlib + subprocess.

Usage:
  python3 tests/test_wiki_mode.py
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "wiki-mode.py"
os.environ["CLAUDE_OBSIDIAN_VAULT"] = str(ROOT)

spec = importlib.util.spec_from_file_location("wiki_mode", HELPER)
wm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wm)


class Fail(SystemExit):
    pass


def assert_eq(label, expected, actual):
    if expected != actual:
        raise Fail(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    print(f"OK   {label}")


def assert_true(label, cond, hint=""):
    if not cond:
        raise Fail(f"FAIL {label}{(': ' + hint) if hint else ''}")
    print(f"OK   {label}")


# ─── Default-to-generic when no config file ──────────────────────────────────
def test_load_config_defaults_to_generic_when_absent():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with (
            mock.patch.object(wm, "VAULT_ROOT", root),
            mock.patch.object(wm, "MODE_PATH", root / ".vault-meta/mode.json"),
        ):
            cfg = wm.load_config()
            assert_eq("absent config → mode=generic", "generic", cfg["mode"])
            assert_eq("schema_version present", 1, cfg["schema_version"])
            assert_true(
                "all 4 mode configs present",
                set(cfg["config"].keys()) == {"lyt", "para", "zettelkasten", "generic"},
            )


# ─── Existing config load ────────────────────────────────────────────────────
def test_load_existing_config():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        mode_path = root / ".vault-meta/mode.json"
        mode_path.parent.mkdir()
        mode_path.write_text(
            json.dumps(
                {
                    "mode": "lyt",
                    "configured_at": "2026-05-17T00:00:00Z",
                    "config": {"zettelkasten": {"id_format": "YYYYMMDDHHMMSSffffff"}},
                }
            ),
            encoding="utf-8",
        )
        with (
            mock.patch.object(wm, "VAULT_ROOT", root),
            mock.patch.object(wm, "MODE_PATH", mode_path),
        ):
            cfg2 = wm.load_config()
            assert_eq("existing mode", "lyt", cfg2["mode"])
            assert_eq(
                "existing configured_at", "2026-05-17T00:00:00Z", cfg2["configured_at"]
            )
            assert_eq(
                "legacy zettel format reports the effective allocator",
                wm.ZETTEL_ID_FORMAT,
                cfg2["config"]["zettelkasten"]["id_format"],
            )


# ─── Existing corrupt mode.json fails closed ────────────────────────────────
def test_corrupted_config_fails_closed():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        mode_path = root / ".vault-meta/mode.json"
        mode_path.parent.mkdir()
        mode_path.write_text("{ this is not valid json", encoding="utf-8")
        with (
            mock.patch.object(wm, "VAULT_ROOT", root),
            mock.patch.object(wm, "MODE_PATH", mode_path),
        ):
            try:
                wm.load_config()
            except SystemExit as exc:
                assert_eq("corrupted config → exit 5", 5, exc.code)
            else:
                raise Fail("FAIL corrupt existing config must not select generic")


# ─── Mode=generic routing matches v1.7 conventions ──────────────────────────
def test_generic_routing():
    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "generic"
    assert_eq(
        "generic source",
        "wiki/sources/Karpathy-2025-essay.md",
        wm.route_path("generic", "source", "Karpathy 2025 essay", cfg),
    )
    assert_eq(
        "generic entity preserves case",
        "wiki/entities/Andrej Karpathy.md",
        wm.route_path("generic", "entity", "Andrej Karpathy", cfg),
    )
    assert_eq(
        "generic concept",
        "wiki/concepts/Compounding Vault.md",
        wm.route_path("generic", "concept", "Compounding Vault", cfg),
    )
    assert_eq(
        "generic session",
        "wiki/sessions/v1-8-launch-prep.md",
        wm.route_path("generic", "session", "v1.8 launch prep", cfg),
    )


# ─── Mode=lyt routing: all atomic notes flat under wiki/notes/ ──────────────
def test_lyt_routing():
    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "lyt"
    src = wm.route_path("lyt", "source", "Karpathy essay", cfg)
    ent = wm.route_path("lyt", "entity", "Andrej Karpathy", cfg)
    con = wm.route_path("lyt", "concept", "Compounding Vault", cfg)
    assert_true("lyt source goes to notes/", src.startswith("wiki/notes/"), hint=src)
    assert_true("lyt entity goes to notes/", ent.startswith("wiki/notes/"), hint=ent)
    assert_true("lyt concept goes to notes/", con.startswith("wiki/notes/"), hint=con)


# ─── Mode=para routing: actionability-based folders ─────────────────────────
def test_para_routing():
    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "para"
    src = wm.route_path("para", "source", "Karpathy essay", cfg)
    ent = wm.route_path("para", "entity", "Andrej Karpathy", cfg)
    sess = wm.route_path("para", "session", "v1.8 prep", cfg)
    res = wm.route_path("para", "research", "compounding-vault", cfg)
    assert_true(
        "para source → resources/incoming/",
        src.startswith("wiki/resources/incoming/"),
        hint=src,
    )
    assert_true(
        "para entity → resources/people/",
        ent.startswith("wiki/resources/people/"),
        hint=ent,
    )
    assert_true(
        "para session → projects/inbox/",
        sess.startswith("wiki/projects/inbox/"),
        hint=sess,
    )
    assert_true(
        "para research → resources/<topic>/",
        "wiki/resources/compounding-vault/" in res,
        hint=res,
    )


# ─── Mode=zettelkasten routing: flat, timestamp-prefixed ────────────────────
def test_zettelkasten_routing():
    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "zettelkasten"
    p = wm.route_path("zettelkasten", "source", "Karpathy essay", cfg)
    # Format: wiki/<20-digit-UTC-timestamp>-<UUIDv4-hex>-<slug>.md
    assert_true("zettel path starts with wiki/", p.startswith("wiki/"), hint=p)
    assert_true("zettel no subfolders", p.count("/") == 1, hint=p)
    fname = p.rsplit("/", 1)[1]
    assert_true(
        "zettel ID has timestamp and UUIDv4 nonce",
        re.fullmatch(r"\d{20}-[0-9a-f]{32}-Karpathy-essay\.md", fname) is not None,
        hint=fname,
    )


# ─── Zettel ID format ───────────────────────────────────────────────────────
def test_mint_zettel_id_format():
    zid = wm.mint_zettel_id()
    assert_true(
        "zettel ID is timestamp plus UUIDv4 hex",
        re.fullmatch(r"\d{20}-[0-9a-f]{32}", zid) is not None,
        hint=zid,
    )


def test_mint_zettel_id_collision_resistance():
    """A repeated wall-clock value must not make batch allocation flaky."""
    fixed = datetime(2026, 7, 11, 12, 34, 56, 123456, tzinfo=timezone.utc)

    class FrozenDateTime:
        @classmethod
        def now(cls, tz=None):
            assert tz is timezone.utc
            return fixed

    with mock.patch.object(wm, "datetime", FrozenDateTime):
        ids = [wm.mint_zettel_id() for _ in range(10_000)]

    assert_eq("zettel IDs all distinct with a frozen clock", 10_000, len(set(ids)))
    assert_true(
        "frozen-clock IDs retain one sortable timestamp prefix",
        all(value.startswith("20260711123456123456-") for value in ids),
    )


def test_slugify_extended_unicode():
    """v1.8.1 fix: explicit test coverage for CJK + Cyrillic (verifier LOW).
    The slugify function preserves any Unicode word character; only ASCII
    punctuation and emoji get stripped/converted.
    """
    assert_eq("CJK preserved", "日本語の文書", wm.slugify("日本語の文書"))
    assert_eq("Cyrillic with space", "Привет-мир", wm.slugify("Привет мир"))
    assert_eq("Mixed scripts", "Hello-мир-café", wm.slugify("Hello мир café"))
    # Emoji is stripped (not in \w); surrounding text joined by single hyphen
    assert_eq(
        "Emoji becomes single hyphen between words",
        "Test-emoji",
        wm.slugify("Test 🎉 emoji"),
    )


# ─── Slugify handles unicode + special chars ────────────────────────────────
def test_slugify():
    # Case is PRESERVED to match v1.7 entity/concept filing conventions.
    assert_eq("ascii slug", "Karpathy-2025-essay", wm.slugify("Karpathy 2025 essay"))
    assert_eq("unicode preserved", "café-résumé", wm.slugify("café résumé"))
    # Periods become hyphens (so v1.7 → v1-7, not v17)
    assert_eq(
        "dots become hyphens", "v1-7-launch-prep", wm.slugify("v1.7 launch! prep?")
    )
    assert_eq("empty → 'untitled'", "untitled", wm.slugify(""))


def test_routes_bound_portable_component_bytes():
    """Long ASCII and Unicode names must remain usable filesystem leaves."""
    generic = dict(wm.DEFAULT_CONFIG)
    generic["mode"] = "generic"
    zettel = dict(wm.DEFAULT_CONFIG)
    zettel["mode"] = "zettelkasten"

    ascii_a = "a" * 1_000
    ascii_b = "a" * 999 + "b"
    generic_a = wm.route_path("generic", "concept", ascii_a, generic)
    generic_b = wm.route_path("generic", "concept", ascii_b, generic)
    zettel_path = wm.route_path("zettelkasten", "source", ascii_a, zettel)
    unicode_path = wm.route_path("generic", "entity", "界" * 1_000, generic)

    paths = (generic_a, generic_b, zettel_path, unicode_path)
    leaves = [path.rsplit("/", 1)[1] for path in paths]
    byte_lengths = [len(leaf.encode("utf-8")) for leaf in leaves]
    assert_true(
        "all routed leaves fit the 255-byte portability floor",
        all(length <= 255 for length in byte_lengths),
        hint=repr(byte_lengths),
    )
    assert_true(
        "long same-prefix names retain distinct hash suffixes", generic_a != generic_b
    )
    assert_true(
        "long routes retain Markdown suffixes",
        all(leaf.endswith(".md") for leaf in leaves),
    )
    reserved_names = (
        "CON",
        "CON.txt",
        "prn.log",
        "AUX.any",
        "nul.data",
        "COM1.txt",
        "LPT9.log",
        "COM¹.txt",
        "LPT³.log",
        "CONIN$.txt",
        "CONOUT$.log",
        "CLOCK$.old",
    )
    reserved_paths = [
        wm.route_path("generic", "concept", name, generic) for name in reserved_names
    ]
    assert_true(
        "Windows reserved device stems and extensions are made portable",
        all(path.rsplit("/", 1)[1].startswith("_") for path in reserved_paths),
        hint=repr(reserved_paths),
    )


# ─── Path-traversal hardening (v1.8.2): entity/concept names cannot escape ──
def test_safe_name_strips_path_separators():
    """v1.8.2 fix: names that intentionally preserve case (entity, concept)
    must not allow path traversal via '../', leading '/', backslashes, NULs,
    or control characters. Spaces and case are still preserved.
    """
    assert_eq(
        "traversal '../' stripped", "etcpasswd", wm.safe_name("../../../etc/passwd")
    )
    assert_eq("leading '/' stripped", "etcpasswd", wm.safe_name("/etc/passwd"))
    assert_eq("backslash stripped", "etcpasswd", wm.safe_name("..\\..\\etc\\passwd"))
    assert_eq("NUL stripped", "foobar", wm.safe_name("foo\x00bar"))
    assert_eq("control chars stripped", "foobar", wm.safe_name("foo\x01\x02bar"))
    assert_eq(
        "leading dot stripped (no hidden files)", "hidden", wm.safe_name(".hidden")
    )
    assert_eq(
        "leading hyphen stripped (no flag escapes)", "flag", wm.safe_name("-flag")
    )
    assert_eq(
        "spaces + case preserved", "Andrej Karpathy", wm.safe_name("Andrej Karpathy")
    )
    assert_eq("empty after strip → 'untitled'", "untitled", wm.safe_name("/"))


def test_route_path_blocks_traversal_for_generic_entity_and_concept():
    """The end-to-end route must not allow the returned path to escape vault root."""
    import os

    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "generic"
    vault = os.path.abspath(".")
    for content_type, malicious in [
        ("entity", "../../../etc/passwd"),
        ("concept", "/etc/passwd"),
        ("entity", "..\\..\\..\\Windows\\System32"),
        ("research", "../escape"),
    ]:
        p = wm.route_path("generic", content_type, malicious, cfg)
        abs_p = os.path.abspath(p)
        assert_true(
            f"generic {content_type}({malicious!r}) stays inside vault",
            abs_p.startswith(vault + os.sep),
            hint=f"got {abs_p}",
        )


def test_route_path_blocks_traversal_for_para_entity_and_concept():
    import os

    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "para"
    vault = os.path.abspath(".")
    for content_type, malicious in [
        ("entity", "../../../etc/passwd"),
        ("concept", "/etc/shadow"),
    ]:
        p = wm.route_path("para", content_type, malicious, cfg)
        abs_p = os.path.abspath(p)
        assert_true(
            f"para {content_type}({malicious!r}) stays inside vault",
            abs_p.startswith(vault + os.sep),
            hint=f"got {abs_p}",
        )


def test_mode_folder_overrides_and_final_routes_are_confined_to_wiki():
    unsafe_folders = (
        "../../outside/",
        "/absolute/",
        "wiki/../outside/",
        "wiki\\outside/",
        "wiki//outside/",
        "wiki/outside",
    )
    for folder in unsafe_folders:
        cfg = wm.default_config()
        cfg["config"]["generic"]["entities_folder"] = folder
        try:
            wm.validate_mode_folders(cfg)
        except ValueError:
            pass
        else:
            raise Fail(f"FAIL unsafe mode folder accepted: {folder!r}")
        if folder.endswith("/"):
            try:
                wm.route_path("generic", "entity", "Escaped", cfg)
            except ValueError:
                pass
            else:
                raise Fail(f"FAIL unsafe final route accepted: {folder!r}")
    print("OK   unsafe mode folders and final routes rejected")


# ─── CLI --mode preview override (v1.8.2) ───────────────────────────────────
def test_cli_route_mode_override_previews_without_writing():
    """`route --mode lyt source X` must return an lyt path even when current
    mode is generic, and must NOT modify .vault-meta/mode.json."""
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        (vault / ".raw").mkdir()
        before = subprocess.run(
            [sys.executable, str(HELPER), "--vault", str(vault), "get"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--vault",
                str(vault),
                "route",
                "--mode",
                "lyt",
                "source",
                "Preview Test",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert_eq("cli route --mode rc=0", 0, result.returncode)
        path = result.stdout.strip()
        assert_true(
            "preview returns lyt notes/ path", path.startswith("wiki/notes/"), hint=path
        )
        after = subprocess.run(
            [sys.executable, str(HELPER), "--vault", str(vault), "get"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        assert_eq("current mode unchanged by preview", before, after)


def test_cli_route_mode_override_rejects_invalid():
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--vault",
                str(vault),
                "route",
                "--mode",
                "bogus",
                "source",
                "X",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert_true(
            "preview rejects bogus mode",
            result.returncode != 0,
            hint=f"rc={result.returncode}",
        )


# ─── Invalid content type raises ───────────────────────────────────────────
def test_invalid_content_type_raises():
    cfg = dict(wm.DEFAULT_CONFIG)
    try:
        wm.route_path("generic", "garbage", "x", cfg)
        raise Fail("expected SystemExit(4) for invalid type")
    except SystemExit as e:
        assert_eq("invalid type → exit 4", 4, e.code)


# ─── CLI subprocess: `wiki-mode.py get` returns mode string ─────────────────
def test_cli_get_returns_mode():
    """End-to-end CLI test via subprocess; uses the actual vault's mode (or generic if absent)."""
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        result = subprocess.run(
            [sys.executable, str(HELPER), "--vault", str(vault), "get"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert_eq("cli get rc=0", 0, result.returncode)
        mode = result.stdout.strip()
        assert_true(
            "cli get returns one of 4 modes",
            mode in ("generic", "lyt", "para", "zettelkasten"),
            hint=mode,
        )


def test_cli_get_rejects_existing_corrupt_config():
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        mode_path = vault / ".vault-meta/mode.json"
        mode_path.parent.mkdir()
        mode_path.write_text("{invalid", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HELPER), "--vault", str(vault), "get"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert_eq("cli corrupt config rc=5", 5, result.returncode)
        assert_eq("cli corrupt config emits no mode", "", result.stdout.strip())
        assert_true(
            "cli corrupt config explains fail-closed behavior",
            "repair it before routing" in result.stderr,
            hint=result.stderr,
        )


# ─── CLI subprocess: `wiki-mode.py id` returns a sortable nonce ID ───────
def test_cli_id_returns_timestamp():
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        result = subprocess.run(
            [sys.executable, str(HELPER), "--vault", str(vault), "id"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert_eq("cli id rc=0", 0, result.returncode)
        zid = result.stdout.strip()
        assert_true(
            "cli id is timestamp plus UUIDv4 hex",
            re.fullmatch(r"\d{20}-[0-9a-f]{32}", zid) is not None,
            hint=zid,
        )


# ─── CLI subprocess: `wiki-mode.py route source NAME` returns a path ────────
def test_cli_route_returns_path():
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--vault",
                str(vault),
                "route",
                "source",
                "Test Source",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert_eq("cli route rc=0", 0, result.returncode)
        path = result.stdout.strip()
        assert_true(
            "cli route returns wiki-rooted path", path.startswith("wiki/"), hint=path
        )
        assert_true("cli route returns .md path", path.endswith(".md"), hint=path)


# ─── CLI subprocess: invalid mode rejected ──────────────────────────────────
def test_cli_set_is_unavailable():
    result = subprocess.run(
        [sys.executable, str(HELPER), "set", "bogus"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert_true(
        "legacy cli set is unavailable",
        result.returncode != 0,
        hint=f"rc={result.returncode}",
    )


# ─── CLI subprocess: templates listing returns all 6 ───────────────────────
def test_cli_templates_lists_six():
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        result = subprocess.run(
            [sys.executable, str(HELPER), "--vault", str(vault), "templates"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert_eq("cli templates rc=0", 0, result.returncode)
        lines = [line for line in result.stdout.strip().split("\n") if line]
        assert_eq("cli templates returns 6 paths", 6, len(lines))


# ─── Single-source page vocabulary (claude_obsidian.page_schema) ─────────────
def test_routable_types_are_derived_not_restated():
    """Regression: VALID_TYPES was a fifth hand-maintained copy of the vocabulary.

    Four sources declared `type` differently — WIKI.md, the frontmatter reference,
    the save skill, and this router — with a union of twelve values and an
    intersection of two. The router must now read the one declaration.
    """
    from claude_obsidian.page_schema import LEGACY_TYPE_ALIASES, ROUTABLE_TYPES

    assert_eq(
        "VALID_TYPES derives from page_schema",
        set(ROUTABLE_TYPES) | set(LEGACY_TYPE_ALIASES),
        set(wm.VALID_TYPES),
    )


def test_question_is_routable_in_every_mode():
    """Regression: `question` is documented in WIKI.md and the root layout ships
    wiki/questions/, yet the router rejected it — so the save skill's own default
    note kind had no filing destination."""
    cfg = wm.default_config()
    for mode in ("generic", "lyt", "para", "zettelkasten"):
        path = wm.route_path(mode, "question", "an open question", cfg)
        assert_true(
            f"question routes under {mode}",
            path.startswith("wiki/") and path.endswith(".md"),
            hint=path,
        )


def test_unroutable_valid_type_is_distinguished_from_unknown_type():
    """Regression: both cases exited 4 with no message, so a typo and a valid
    page type that has no filing destination were indistinguishable."""
    from claude_obsidian.page_schema import route_rejection_reason

    for page_type in ("overview", "meta", "fold", "comparison"):
        reason = route_rejection_reason(page_type)
        assert_true(
            f"{page_type} is valid but not routable",
            reason is not None and "valid page type" in reason,
            hint=str(reason),
        )
    unknown = route_rejection_reason("garbage")
    assert_true(
        "unknown type says unknown",
        unknown is not None and "unknown type" in unknown,
        hint=str(unknown),
    )


def test_legacy_research_alias_keeps_its_exact_destinations():
    """`research` was accepted by the CLI and documented nowhere. It stays
    accepted, and its paths must not move: rewriting it as an alias of `concept`
    would silently relocate para-mode research folders."""
    cfg = wm.default_config()
    assert_eq(
        "generic research destination unchanged",
        "wiki/concepts/x.md",
        wm.route_path("generic", "research", "x", cfg),
    )
    assert_eq(
        "para research destination unchanged",
        "wiki/resources/x/x.md",
        wm.route_path("para", "research", "x", cfg),
    )


def test_legacy_mode_json_on_disk_routes_through_both_callers():
    """Regression: `questions_folder` is a folder key added after release, so no
    existing `mode.json` contains it. Both callers own a separate default document
    and merge the on-disk file onto it, so this must be exercised on the REAL path
    — through a file on disk — not by deleting a key from an in-memory default,
    which is a state neither caller can reach.
    """
    with tempfile.TemporaryDirectory() as directory:
        vault = Path(directory)
        (vault / "wiki").mkdir()
        meta = vault / ".vault-meta"
        meta.mkdir()
        legacy = {
            "schema_version": 1,
            "mode": "generic",
            "configured_at": "2026-06-09T14:38:44Z",
            "config": {
                "generic": {
                    "sources_folder": "wiki/sources/",
                    "entities_folder": "wiki/entities/",
                    "concepts_folder": "wiki/concepts/",
                    "sessions_folder": "wiki/sessions/",
                }
            },
        }
        (meta / "mode.json").write_text(json.dumps(legacy), encoding="utf-8")

        routed = subprocess.run(
            [sys.executable, str(HELPER), "route", "question", "x", "--vault", str(vault)],
            capture_output=True, text=True, timeout=10,
        )
        assert_eq("legacy mode.json routes question", 0, routed.returncode)
        assert_eq(
            "legacy mode.json gets the default questions_folder",
            "wiki/questions/x.md",
            routed.stdout.strip(),
        )

        core = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "claude-obsidian.py"),
             "mode", "get", "--vault", str(vault)],
            capture_output=True, text=True, timeout=15,
        )
        assert_eq("legacy mode.json loads through the core CLI", 0, core.returncode)


def test_page_vocabulary_matches_the_documented_table():
    """Anti-drift: the point of one declaration is that the docs stop restating
    it. WIKI.md's table is prose, so this asserts every documented type appears
    in the module, which is what a reader of either one relies on."""
    from claude_obsidian.page_schema import PAGE_TYPES

    documented = (ROOT / "WIKI.md").read_text(encoding="utf-8")
    for page_type in PAGE_TYPES:
        assert_true(
            f"WIKI.md documents type {page_type}",
            f"`{page_type}`" in documented,
            hint=page_type,
        )


def main():
    print("=== test_wiki_mode.py ===")
    test_load_config_defaults_to_generic_when_absent()
    test_load_existing_config()
    test_corrupted_config_fails_closed()
    test_generic_routing()
    test_lyt_routing()
    test_para_routing()
    test_zettelkasten_routing()
    test_mint_zettel_id_format()
    test_mint_zettel_id_collision_resistance()
    test_slugify()
    test_slugify_extended_unicode()
    test_routes_bound_portable_component_bytes()
    test_safe_name_strips_path_separators()
    test_route_path_blocks_traversal_for_generic_entity_and_concept()
    test_route_path_blocks_traversal_for_para_entity_and_concept()
    test_mode_folder_overrides_and_final_routes_are_confined_to_wiki()
    test_cli_route_mode_override_previews_without_writing()
    test_cli_route_mode_override_rejects_invalid()
    test_invalid_content_type_raises()
    test_cli_get_returns_mode()
    test_cli_get_rejects_existing_corrupt_config()
    test_cli_id_returns_timestamp()
    test_cli_route_returns_path()
    test_cli_set_is_unavailable()
    test_cli_templates_lists_six()
    test_routable_types_are_derived_not_restated()
    test_question_is_routable_in_every_mode()
    test_unroutable_valid_type_is_distinguished_from_unknown_type()
    test_legacy_research_alias_keeps_its_exact_destinations()
    test_legacy_mode_json_on_disk_routes_through_both_callers()
    test_page_vocabulary_matches_the_documented_table()
    print("\nAll wiki-mode tests passed.")


if __name__ == "__main__":
    main()
