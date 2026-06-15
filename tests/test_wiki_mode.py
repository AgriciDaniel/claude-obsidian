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
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "wiki-mode.py"

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
        with mock.patch.object(wm, "MODE_PATH", Path(tmp) / "nonexistent.json"):
            cfg = wm.load_config()
            assert_eq("absent config → mode=generic", "generic", cfg["mode"])
            assert_eq("schema_version present", 1, cfg["schema_version"])
            assert_true("all 4 mode configs present",
                        set(cfg["config"].keys()) == {"lyt", "para", "zettelkasten", "generic"})


# ─── Config save → load round-trip ───────────────────────────────────────────
def test_save_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        mode_path = Path(tmp) / "mode.json"
        with mock.patch.object(wm, "MODE_PATH", mode_path), \
             mock.patch.object(wm, "META_DIR", Path(tmp)):
            cfg = wm.load_config()
            cfg["mode"] = "lyt"
            cfg["configured_at"] = "2026-05-17T00:00:00Z"
            wm.save_config(cfg)
            assert_true("mode.json written", mode_path.is_file())
            cfg2 = wm.load_config()
            assert_eq("round-trip mode", "lyt", cfg2["mode"])
            assert_eq("round-trip configured_at", "2026-05-17T00:00:00Z", cfg2["configured_at"])


# ─── Corrupted mode.json falls back to generic with warning ──────────────────
def test_corrupted_config_falls_back_to_generic():
    with tempfile.TemporaryDirectory() as tmp:
        mode_path = Path(tmp) / "mode.json"
        mode_path.write_text("{ this is not valid json", encoding="utf-8")
        with mock.patch.object(wm, "MODE_PATH", mode_path):
            cfg = wm.load_config()
            assert_eq("corrupted config → mode=generic", "generic", cfg["mode"])


# ─── Mode=generic routing matches v1.7 conventions ──────────────────────────
def test_generic_routing():
    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "generic"
    assert_eq("generic source",
              "wiki/sources/Karpathy-2025-essay.md",
              wm.route_path("generic", "source", "Karpathy 2025 essay", cfg))
    assert_eq("generic entity preserves case",
              "wiki/entities/Andrej Karpathy.md",
              wm.route_path("generic", "entity", "Andrej Karpathy", cfg))
    assert_eq("generic concept",
              "wiki/concepts/Compounding Vault.md",
              wm.route_path("generic", "concept", "Compounding Vault", cfg))
    assert_eq("generic session",
              "wiki/sessions/v1-8-launch-prep.md",
              wm.route_path("generic", "session", "v1.8 launch prep", cfg))


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
    assert_true("para source → resources/incoming/", src.startswith("wiki/resources/incoming/"), hint=src)
    assert_true("para entity → resources/people/", ent.startswith("wiki/resources/people/"), hint=ent)
    assert_true("para session → projects/inbox/", sess.startswith("wiki/projects/inbox/"), hint=sess)
    assert_true("para research → resources/<topic>/", "wiki/resources/compounding-vault/" in res, hint=res)


# ─── Mode=zettelkasten routing: flat, timestamp-prefixed ────────────────────
def test_zettelkasten_routing():
    cfg = dict(wm.DEFAULT_CONFIG)
    cfg["mode"] = "zettelkasten"
    p = wm.route_path("zettelkasten", "source", "Karpathy essay", cfg)
    # Format: wiki/<20-digit-timestamp-with-microseconds>-<slug>.md
    assert_true("zettel path starts with wiki/", p.startswith("wiki/"), hint=p)
    assert_true("zettel no subfolders", p.count("/") == 1, hint=p)
    fname = p.rsplit("/", 1)[1]
    parts = fname.split("-", 1)
    # v1.8.1 fix: IDs are 20 digits (YYYYMMDDHHMMSSffffff) for collision resistance
    assert_true("zettel ID is 20 digits", parts[0].isdigit() and len(parts[0]) == 20, hint=fname)


# ─── Zettel ID format ───────────────────────────────────────────────────────
def test_mint_zettel_id_format():
    zid = wm.mint_zettel_id()
    # 14 (YYYYMMDDHHMMSS) + 6 (microseconds) = 20 digits
    assert_true("zettel ID is 20-digit string", len(zid) == 20 and zid.isdigit(), hint=zid)


def test_mint_zettel_id_collision_resistance():
    """v1.8.1 fix: rapid back-to-back mint calls produce DIFFERENT IDs.
    Microsecond suffix ensures two calls within the same second are distinct.
    """
    ids = [wm.mint_zettel_id() for _ in range(10)]
    assert_eq("zettel IDs all distinct (10 rapid calls)", 10, len(set(ids)))


def test_slugify_extended_unicode():
    """v1.8.1 fix: explicit test coverage for CJK + Cyrillic (verifier LOW).
    The slugify function preserves any Unicode word character; only ASCII
    punctuation and emoji get stripped/converted.
    """
    assert_eq("CJK preserved", "日本語の文書", wm.slugify("日本語の文書"))
    assert_eq("Cyrillic with space", "Привет-мир", wm.slugify("Привет мир"))
    assert_eq("Mixed scripts", "Hello-мир-café", wm.slugify("Hello мир café"))
    # Emoji is stripped (not in \w); surrounding text joined by single hyphen
    assert_eq("Emoji becomes single hyphen between words", "Test-emoji",
              wm.slugify("Test 🎉 emoji"))


# ─── Slugify handles unicode + special chars ────────────────────────────────
def test_slugify():
    # Case is PRESERVED to match v1.7 entity/concept filing conventions.
    assert_eq("ascii slug", "Karpathy-2025-essay", wm.slugify("Karpathy 2025 essay"))
    assert_eq("unicode preserved", "café-résumé", wm.slugify("café résumé"))
    # Periods become hyphens (so v1.7 → v1-7, not v17)
    assert_eq("dots become hyphens", "v1-7-launch-prep", wm.slugify("v1.7 launch! prep?"))
    assert_eq("empty → 'untitled'", "untitled", wm.slugify(""))


# ─── Path-traversal hardening (v1.8.2): entity/concept names cannot escape ──
def test_safe_name_strips_path_separators():
    """v1.8.2 fix: names that intentionally preserve case (entity, concept)
    must not allow path traversal via '../', leading '/', backslashes, NULs,
    or control characters. Spaces and case are still preserved.
    """
    assert_eq("traversal '../' stripped", "etcpasswd", wm.safe_name("../../../etc/passwd"))
    assert_eq("leading '/' stripped", "etcpasswd", wm.safe_name("/etc/passwd"))
    assert_eq("backslash stripped", "etcpasswd", wm.safe_name("..\\..\\etc\\passwd"))
    assert_eq("NUL stripped", "foobar", wm.safe_name("foo\x00bar"))
    assert_eq("control chars stripped", "foobar", wm.safe_name("foo\x01\x02bar"))
    assert_eq("leading dot stripped (no hidden files)", "hidden", wm.safe_name(".hidden"))
    assert_eq("leading hyphen stripped (no flag escapes)", "flag", wm.safe_name("-flag"))
    assert_eq("spaces + case preserved", "Andrej Karpathy", wm.safe_name("Andrej Karpathy"))
    assert_eq("empty after strip → 'untitled'", "untitled", wm.safe_name("/"))


def test_route_path_blocks_traversal_for_generic_entity_and_concept():
    """The end-to-end route must not allow the returned path to escape vault root."""
    import os
    cfg = dict(wm.DEFAULT_CONFIG); cfg["mode"] = "generic"
    vault = os.path.abspath(".")
    for content_type, malicious in [
        ("entity",  "../../../etc/passwd"),
        ("concept", "/etc/passwd"),
        ("entity",  "..\\..\\..\\Windows\\System32"),
        ("research","../escape"),
    ]:
        p = wm.route_path("generic", content_type, malicious, cfg)
        abs_p = os.path.abspath(p)
        assert_true(f"generic {content_type}({malicious!r}) stays inside vault",
                    abs_p.startswith(vault + os.sep), hint=f"got {abs_p}")


def test_route_path_blocks_traversal_for_para_entity_and_concept():
    import os
    cfg = dict(wm.DEFAULT_CONFIG); cfg["mode"] = "para"
    vault = os.path.abspath(".")
    for content_type, malicious in [
        ("entity",  "../../../etc/passwd"),
        ("concept", "/etc/shadow"),
    ]:
        p = wm.route_path("para", content_type, malicious, cfg)
        abs_p = os.path.abspath(p)
        assert_true(f"para {content_type}({malicious!r}) stays inside vault",
                    abs_p.startswith(vault + os.sep), hint=f"got {abs_p}")


# ─── CLI --mode preview override (v1.8.2) ───────────────────────────────────
def test_cli_route_mode_override_previews_without_writing():
    """`route --mode lyt source X` must return an lyt path even when current
    mode is generic, and must NOT modify .vault-meta/mode.json."""
    before = subprocess.run([sys.executable, str(HELPER), "get"],
                            capture_output=True, text=True, timeout=5).stdout.strip()
    result = subprocess.run(
        [sys.executable, str(HELPER), "route", "--mode", "lyt", "source", "Preview Test"],
        capture_output=True, text=True, timeout=5,
    )
    assert_eq("cli route --mode rc=0", 0, result.returncode)
    path = result.stdout.strip()
    assert_true("preview returns lyt notes/ path",
                path.startswith("wiki/notes/"), hint=path)
    after = subprocess.run([sys.executable, str(HELPER), "get"],
                           capture_output=True, text=True, timeout=5).stdout.strip()
    assert_eq("current mode unchanged by preview", before, after)


def test_cli_route_mode_override_rejects_invalid():
    result = subprocess.run(
        [sys.executable, str(HELPER), "route", "--mode", "bogus", "source", "X"],
        capture_output=True, text=True, timeout=5,
    )
    assert_true("preview rejects bogus mode", result.returncode != 0,
                hint=f"rc={result.returncode}")


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
    result = subprocess.run(
        [sys.executable, str(HELPER), "get"],
        capture_output=True, text=True, timeout=5,
    )
    assert_eq("cli get rc=0", 0, result.returncode)
    mode = result.stdout.strip()
    assert_true("cli get returns one of 4 modes",
                mode in ("generic", "lyt", "para", "zettelkasten"), hint=mode)


# ─── CLI subprocess: `wiki-mode.py id` returns 14-digit timestamp ───────────
def test_cli_id_returns_timestamp():
    result = subprocess.run(
        [sys.executable, str(HELPER), "id"],
        capture_output=True, text=True, timeout=5,
    )
    assert_eq("cli id rc=0", 0, result.returncode)
    zid = result.stdout.strip()
    assert_true("cli id is 20-digit", len(zid) == 20 and zid.isdigit(), hint=zid)


# ─── CLI subprocess: `wiki-mode.py route source NAME` returns a path ────────
def test_cli_route_returns_path():
    result = subprocess.run(
        [sys.executable, str(HELPER), "route", "source", "Test Source"],
        capture_output=True, text=True, timeout=5,
    )
    assert_eq("cli route rc=0", 0, result.returncode)
    path = result.stdout.strip()
    assert_true("cli route returns wiki-rooted path",
                path.startswith("wiki/"), hint=path)
    assert_true("cli route returns .md path", path.endswith(".md"), hint=path)


# ─── CLI subprocess: invalid mode rejected ──────────────────────────────────
def test_cli_set_rejects_invalid_mode():
    result = subprocess.run(
        [sys.executable, str(HELPER), "set", "bogus"],
        capture_output=True, text=True, timeout=5,
    )
    assert_true("cli set rejects invalid mode", result.returncode != 0,
                hint=f"rc={result.returncode}")


# ─── CLI subprocess: templates listing returns all 6 ───────────────────────
def test_cli_templates_lists_six():
    result = subprocess.run(
        [sys.executable, str(HELPER), "templates"],
        capture_output=True, text=True, timeout=5,
    )
    assert_eq("cli templates rc=0", 0, result.returncode)
    lines = [l for l in result.stdout.strip().split("\n") if l]
    assert_eq("cli templates returns 6 paths", 6, len(lines))


def main():
    print("=== test_wiki_mode.py ===")
    test_load_config_defaults_to_generic_when_absent()
    test_save_load_roundtrip()
    test_corrupted_config_falls_back_to_generic()
    test_generic_routing()
    test_lyt_routing()
    test_para_routing()
    test_zettelkasten_routing()
    test_mint_zettel_id_format()
    test_mint_zettel_id_collision_resistance()
    test_slugify()
    test_slugify_extended_unicode()
    test_safe_name_strips_path_separators()
    test_route_path_blocks_traversal_for_generic_entity_and_concept()
    test_route_path_blocks_traversal_for_para_entity_and_concept()
    test_cli_route_mode_override_previews_without_writing()
    test_cli_route_mode_override_rejects_invalid()
    test_invalid_content_type_raises()
    test_cli_get_returns_mode()
    test_cli_id_returns_timestamp()
    test_cli_route_returns_path()
    test_cli_set_rejects_invalid_mode()
    test_cli_templates_lists_six()
    print("\nAll wiki-mode tests passed.")


if __name__ == "__main__":
    main()
