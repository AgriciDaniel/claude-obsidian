#!/usr/bin/env python3
"""test_core_introspect.py — hermetic tests for scripts/core-introspect.py.

Covers the three commands that matter and the property that makes each one
trustworthy rather than decorative:

  scan    discovery is read-only (`--peek` writes nothing) and every emitted
          capability carries the fields its kind promises.
  list    the human-readable surface, and that `--kind` actually filters
          rather than just relabeling.
  show    single-capability lookup, including the bogus-id failure path.
  check   the CI drift gate. It must fail when the manifest is stale (or it
          is not a gate), and it must NOT fail merely because `generated_at`
          differs between two honest scans (or it trains everyone to ignore
          it — see `_stable()` in the source).

Hermetic: a throwaway copy of core-introspect.py is placed in a tempdir's
scripts/, so its own VAULT_ROOT (computed from `__file__`) resolves inside
the tempdir. A minimal fake capability of every kind (skill, script,
workflow, rule, command, agent, hook, make, config) is planted alongside it.
The real repo, and the real .vault-meta/capabilities.json, are never
touched — asserted explicitly at the end.

No network, no third-party deps, stdlib only.

Usage:
  python3 tests/test_core_introspect.py
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts" / "core-introspect.py"
REAL_MANIFEST = ROOT / ".vault-meta" / "capabilities.json"

ALL_KINDS = ("skill", "script", "workflow", "rule", "command", "agent", "hook", "make", "config")

# Extra fields each kind's scan() entry adds on top of the common set below,
# read straight off scripts/core-introspect.py's scan().
COMMON_FIELDS = {"id", "kind", "name", "summary", "path", "invoke"}
EXTRA_FIELDS = {
    "skill": {"triggers", "tools"},
    "script": {"subcommands", "exit_codes", "executable", "verifiable"},
    "workflow": {"phases"},
    "rule": {"severity"},
    "command": set(),
    "agent": {"tools"},
    "hook": set(),
    "make": set(),
    # config deliberately carries NO existence flag: the manifest is source-derived and
    # must be identical on every machine, and whether .vault-meta/browser.json exists is
    # a property of the machine. `verify` checks that at run time instead.
    "config": set(),
}


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


# ─── sandbox construction ─────────────────────────────────────────────────────

def _build_sandbox(tmp: str) -> Path:
    """Plant a throwaway repo in tmp/: a copy of core-introspect.py under
    scripts/ (so VAULT_ROOT resolves inside tmp), plus exactly one fake
    capability of every kind scan() knows how to discover. Returns the CLI
    path. The real vault is never read or written by anything this builds."""
    root = Path(tmp)
    scripts = root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    cli = scripts / "core-introspect.py"
    shutil.copy2(HELPER, cli)

    # script — a second, minimal script (the copied core-introspect.py above
    # is itself also discovered as a script capability; that is correct and
    # matches production behavior, not a bug to work around).
    fake_script = scripts / "fake-script.py"
    fake_script.write_text(
        '#!/usr/bin/env python3\n'
        '"""fake-script.py — a fake script for core-introspect tests.\n'
        '\n'
        'Exit codes:\n'
        '  0 — success\n'
        '  2 — usage error\n'
        '"""\n'
        'import argparse\n'
        'import sys\n'
        '\n'
        '\n'
        'def main():\n'
        '    parser = argparse.ArgumentParser()\n'
        '    sub = parser.add_subparsers(dest="cmd")\n'
        '    sub.add_parser("foo")\n'
        '    sub.add_parser("bar")\n'
        '    args = parser.parse_args()\n'
        '    if not args.cmd:\n'
        '        parser.print_help()\n'
        '        return 2\n'
        '    print(args.cmd)\n'
        '    return 0\n'
        '\n'
        '\n'
        'if __name__ == "__main__":\n'
        '    sys.exit(main())\n',
        encoding="utf-8",
    )
    fake_script.chmod(0o755)

    # skill
    skill_dir = root / "skills" / "fake-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: fake-skill\n"
        "description: A fake skill for testing purposes. Triggers on: fake trigger one, fake trigger two.\n"
        "---\n"
        "\n"
        "# Fake Skill\n"
        "Body text.\n",
        encoding="utf-8",
    )

    # workflow
    workflows = root / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    (workflows / "fake-workflow.js").write_text(
        "export const meta = {\n"
        "  name: 'fake-workflow',\n"
        "  description: 'A fake workflow for testing.',\n"
        "  phases: [\n"
        "    { title: 'Phase One' },\n"
        "    { title: 'Phase Two' },\n"
        "  ],\n"
        "}\n",
        encoding="utf-8",
    )

    # rule
    rule_dir = root / "rules" / "test"
    rule_dir.mkdir(parents=True, exist_ok=True)
    (rule_dir / "fake-rule.md").write_text(
        "---\n"
        "id: test/fake-rule\n"
        "domain: test\n"
        "title: Fake Rule For Testing\n"
        "severity: medium\n"
        "applies_when: >\n"
        "  Testing core-introspect.\n"
        "---\n"
        "\n"
        "# Fake Rule For Testing\n"
        "\n"
        "Body.\n",
        encoding="utf-8",
    )

    # command
    commands = root / "commands"
    commands.mkdir(parents=True, exist_ok=True)
    (commands / "fake-command.md").write_text(
        "---\n"
        "description: A fake command for testing.\n"
        "---\n"
        "\n"
        "Body.\n",
        encoding="utf-8",
    )

    # agent
    agents = root / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    (agents / "fake-agent.md").write_text(
        "---\n"
        "name: fake-agent\n"
        "description: A fake agent for testing.\n"
        "tools: Read, Grep\n"
        "---\n"
        "\n"
        "Body.\n",
        encoding="utf-8",
    )

    # hook
    hooks = root / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    (hooks / "hooks.json").write_text(
        json.dumps({
            "hooks": {
                "FakeEvent": [
                    {"matcher": "test", "hooks": [{"type": "command", "command": "echo hi"}]}
                ]
            }
        }, indent=2),
        encoding="utf-8",
    )

    # make
    (root / "Makefile").write_text(
        ".PHONY: help fake-target\n"
        "\n"
        "help:\n"
        "\t@echo help\n"
        "\n"
        "fake-target:\n"
        "\t@echo fake\n",
        encoding="utf-8",
    )

    # config: no files needed. scan() emits a config/ capability for each of its 5
    # fixed filenames whether or not the file exists, and records nothing about
    # whether it does, so .vault-meta/ is deliberately left absent.

    return cli


def _run(cli: Path, *args, timeout=10):
    return subprocess.run([sys.executable, str(cli), *args],
                          capture_output=True, text=True, timeout=timeout)


def _list_ids(list_output: str):
    """Recover the ids `list` printed. Format is `  {id:<44} {summary}`, two
    leading spaces, no spaces inside an id; header lines start with '── '."""
    return set(re.findall(r'^  (\S+)', list_output, re.MULTILINE))


def _stable(payload: str) -> str:
    """The manifest minus the one field that is *expected* to vary between runs."""
    d = json.loads(payload)
    d.pop("generated_at", None)
    return json.dumps(d, sort_keys=True)


# ─── scan ──────────────────────────────────────────────────────────────────────

def test_manifest_does_not_depend_on_machine_state():
    """capabilities.json is committed, so it MUST be byte-identical on every machine
    at a given commit. It once was not: config entries carried a `present` flag, so a
    developer with a browser.json produced a different manifest than CI, which has
    none, and `core-introspect check` went red in CI for that reason alone. Scanning
    the same source with and without the runtime configs on disk must agree."""
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        meta = Path(tmp) / ".vault-meta"

        bare = _run(cli, "scan", "--peek")
        assert_eq("scan --peek rc=0 with no runtime configs", 0, bare.returncode)

        # Now litter the sandbox with exactly the machine-specific state CI lacks.
        meta.mkdir(parents=True, exist_ok=True)
        (meta / "browser.json").write_text('{"preferred": "cdp"}', encoding="utf-8")
        (meta / "net.json").write_text('{"mode": "live"}', encoding="utf-8")
        (meta / "mode.json").write_text('{"mode": "para"}', encoding="utf-8")
        (meta / "capabilities.json").write_text("{}", encoding="utf-8")

        littered = _run(cli, "scan", "--peek")
        assert_eq("scan --peek rc=0 with runtime configs present", 0, littered.returncode)

        assert_eq("manifest is identical with and without machine state",
                  _stable(bare.stdout), _stable(littered.stdout))


def test_scan_peek_emits_json_and_writes_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        manifest = Path(tmp) / ".vault-meta" / "capabilities.json"

        r = _run(cli, "scan", "--peek")
        assert_eq("scan --peek rc=0", 0, r.returncode)
        data = json.loads(r.stdout)
        assert_true("scan --peek emits a capabilities list",
                    isinstance(data.get("capabilities"), list) and data["capabilities"])
        assert_true("scan --peek writes no manifest file", not manifest.exists())
        assert_true("scan --peek creates no .vault-meta/ dir at all",
                    not (Path(tmp) / ".vault-meta").exists())


def test_scan_writes_manifest_with_expected_top_level_keys():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        manifest = Path(tmp) / ".vault-meta" / "capabilities.json"

        r = _run(cli, "scan")
        assert_eq("scan rc=0", 0, r.returncode)
        assert_true("scan writes the manifest file", manifest.is_file())

        data = json.loads(manifest.read_text())
        expected_keys = {"schema_version", "generated_by", "warning", "counts",
                          "total", "capabilities", "generated_at"}
        assert_eq("manifest top-level keys", expected_keys, set(data.keys()))
        assert_eq("manifest total matches capabilities length",
                  data["total"], len(data["capabilities"]))
        assert_eq("manifest counts sum to total",
                  data["total"], sum(data["counts"].values()))


def test_every_capability_has_required_fields():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        r = _run(cli, "scan", "--peek")
        assert_eq("scan --peek rc=0 (for field check)", 0, r.returncode)
        data = json.loads(r.stdout)

        seen_kinds = set()
        for cap in data["capabilities"]:
            seen_kinds.add(cap["kind"])
            missing_common = COMMON_FIELDS - set(cap.keys())
            assert_true(f"{cap.get('id')}: has common fields", not missing_common,
                        hint=f"missing {missing_common}")
            extra = EXTRA_FIELDS.get(cap["kind"])
            assert_true(f"{cap.get('id')}: kind {cap['kind']!r} is known",
                        extra is not None, hint=cap["kind"])
            missing_extra = extra - set(cap.keys())
            assert_true(f"{cap.get('id')}: has kind-specific fields", not missing_extra,
                        hint=f"missing {missing_extra}")

        # The sandbox plants exactly one fake capability per kind, and config
        # is always emitted regardless of what's on disk, so every kind
        # scan() knows about should have been exercised at least once.
        assert_eq("every known kind was discovered", set(ALL_KINDS), seen_kinds)


# ─── list ──────────────────────────────────────────────────────────────────────

def test_list_and_kind_filter():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)

        r_all = _run(cli, "list")
        assert_eq("list rc=0", 0, r_all.returncode)
        all_ids = _list_ids(r_all.stdout)
        assert_true("list produced ids", len(all_ids) > 0)

        r_script = _run(cli, "list", "--kind", "script")
        assert_eq("list --kind script rc=0", 0, r_script.returncode)
        script_ids = _list_ids(r_script.stdout)
        assert_true("list --kind script produced ids", len(script_ids) > 0)
        assert_true("every filtered id is kind script",
                    all(i.startswith("script/") for i in script_ids), hint=str(script_ids))
        assert_true("filtered list is a strict subset of the full list",
                    script_ids < all_ids, hint=f"{script_ids} vs {all_ids}")


# ─── show ──────────────────────────────────────────────────────────────────────

def test_show_real_id_and_bogus_id():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)

        r = _run(cli, "show", "command/fake-command")
        assert_eq("show real id rc=0", 0, r.returncode)
        shown = json.loads(r.stdout)
        assert_eq("show real id returns matching id", "command/fake-command", shown["id"])

        # Suffix lookup: `show` also matches on `id.endswith("/" + args.id)`.
        r_suffix = _run(cli, "show", "fake-command")
        assert_eq("show suffix-only id rc=0", 0, r_suffix.returncode)
        assert_eq("show suffix-only id resolves the same capability",
                  "command/fake-command", json.loads(r_suffix.stdout)["id"])

        r_bad = _run(cli, "show", "totally-bogus-id-xyz")
        assert_true("show bogus id exits nonzero", r_bad.returncode != 0,
                    hint=f"rc={r_bad.returncode}")
        assert_true("show bogus id reports no capability",
                    "no capability" in r_bad.stderr, hint=r_bad.stderr)


# ─── check: the drift gate ──────────────────────────────────────────────────────

def test_check_passes_when_manifest_is_current():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        # Scan twice: the manifest's own config/capabilities.json entry
        # records whether the manifest file existed AT SCAN TIME, so the
        # very first scan (before the file exists) legitimately differs from
        # a fresh rescan of a repo where it now does. Settle that before
        # asserting "current".
        assert_eq("first scan rc=0", 0, _run(cli, "scan").returncode)
        assert_eq("second scan rc=0", 0, _run(cli, "scan").returncode)

        r = _run(cli, "check")
        assert_eq("check rc=0 on current manifest", 0, r.returncode)
        assert_true("check reports current", "is current" in r.stdout, hint=r.stdout)


def test_check_fails_when_manifest_is_stale():
    """The drift gate has to be able to go red, or it is not a gate. Mutate
    the on-disk manifest (not the source tree) so it disagrees with a fresh
    scan, and confirm `check` catches it."""
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        assert_eq("scan rc=0", 0, _run(cli, "scan").returncode)
        assert_eq("rescan rc=0", 0, _run(cli, "scan").returncode)
        manifest = Path(tmp) / ".vault-meta" / "capabilities.json"

        data = json.loads(manifest.read_text())
        assert_true("sandbox manifest has capabilities to tamper with",
                    len(data["capabilities"]) > 0)
        data["capabilities"][0]["summary"] = "TAMPERED-FOR-DRIFT-TEST"
        manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")

        r = _run(cli, "check")
        assert_true("check exits nonzero on a stale manifest", r.returncode != 0,
                    hint=f"rc={r.returncode}")
        assert_true("check reports staleness", "stale" in r.stderr, hint=r.stderr)


def test_check_ignores_generated_at_only_diff():
    """Regression guard for `_stable()`: two honest scans of an unchanged
    source tree must not be reported as drift merely because their
    `generated_at` timestamps differ. Force that exact scenario
    deterministically by editing only the timestamp on disk, rather than
    hoping two real scans land in different wall-clock seconds."""
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        assert_eq("scan rc=0", 0, _run(cli, "scan").returncode)
        assert_eq("rescan rc=0", 0, _run(cli, "scan").returncode)
        manifest = Path(tmp) / ".vault-meta" / "capabilities.json"

        data = json.loads(manifest.read_text())
        original_ts = data["generated_at"]
        data["generated_at"] = "2000-01-01T00:00:00Z"
        assert_true("test actually changes the timestamp",
                    data["generated_at"] != original_ts)
        manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")

        r = _run(cli, "check")
        assert_eq("check rc=0 despite differing generated_at only", 0, r.returncode)
        assert_true("check still reports current", "is current" in r.stdout, hint=r.stdout)


# ─── verify: scoped to a cheap kind, not the fleet ──────────────────────────────

def test_verify_scoped_to_rule_kind_is_cheap_and_ok():
    """verify() on kind=rule never spawns a subprocess (it falls through to
    the generic 'present' branch), so this is fast and safe to run for real,
    unlike verifying scripts/skills/etc against the whole fleet."""
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        r = _run(cli, "verify", "--kind", "rule")
        assert_eq("verify --kind rule rc=0", 0, r.returncode)
        assert_true("verify --kind rule reports 1 reachable, 0 broken",
                    "1 reachable, 0 skipped, 0 BROKEN" in r.stdout, hint=r.stdout)


# ─── bad usage ──────────────────────────────────────────────────────────────────

def test_no_subcommand_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        r = _run(cli)
        assert_eq("no subcommand → exit 2", 2, r.returncode)


def test_unknown_subcommand_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _build_sandbox(tmp)
        r = _run(cli, "bogus-subcommand")
        assert_true("unknown subcommand exits nonzero", r.returncode != 0,
                    hint=f"rc={r.returncode}")


# ─── hermeticity ────────────────────────────────────────────────────────────────

def _hash_or_none(path: Path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


_REAL_MANIFEST_HASH_BEFORE = _hash_or_none(REAL_MANIFEST)
_REAL_VAULT_META_TMPS_BEFORE = sorted(p.name for p in (ROOT / ".vault-meta").glob("*.tmp*")) \
    if (ROOT / ".vault-meta").exists() else []


def test_real_manifest_and_vault_meta_untouched():
    """Every test above ran against a throwaway copy of core-introspect.py
    whose VAULT_ROOT resolves inside a tempdir. Prove it: the real repo's
    .vault-meta/capabilities.json (and any stray temp files) must be
    byte-for-byte unchanged from before this suite ran."""
    after = _hash_or_none(REAL_MANIFEST)
    assert_eq("real .vault-meta/capabilities.json unchanged", _REAL_MANIFEST_HASH_BEFORE, after)

    tmps_after = sorted(p.name for p in (ROOT / ".vault-meta").glob("*.tmp*")) \
        if (ROOT / ".vault-meta").exists() else []
    assert_eq("no stray .tmp files left in real .vault-meta/",
              _REAL_VAULT_META_TMPS_BEFORE, tmps_after)


def main():
    print("=== test_core_introspect.py ===")
    test_manifest_does_not_depend_on_machine_state()
    test_scan_peek_emits_json_and_writes_nothing()
    test_scan_writes_manifest_with_expected_top_level_keys()
    test_every_capability_has_required_fields()
    test_list_and_kind_filter()
    test_show_real_id_and_bogus_id()
    test_check_passes_when_manifest_is_current()
    test_check_fails_when_manifest_is_stale()
    test_check_ignores_generated_at_only_diff()
    test_verify_scoped_to_rule_kind_is_cheap_and_ok()
    test_no_subcommand_exits_nonzero()
    test_unknown_subcommand_exits_nonzero()
    test_real_manifest_and_vault_meta_untouched()
    print("\nAll core-introspect tests passed.")


if __name__ == "__main__":
    main()
