#!/usr/bin/env python3
"""Hermetic tests for the deterministic Obsidian lint engine."""

from __future__ import annotations

import errno
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest
import unittest.mock
from datetime import date, datetime
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
ENGINE_PATH = ROOT / "claude_obsidian" / "lint_engine.py"
FIXTURE = ROOT / "tests" / "fixtures" / "lint" / "vault"

spec = importlib.util.spec_from_file_location(
    "claude_obsidian_lint_engine", ENGINE_PATH
)
lint_engine = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lint_engine
assert spec.loader is not None
spec.loader.exec_module(lint_engine)

from claude_obsidian.ledgers import stable_source_id
from claude_obsidian import transaction as transaction_module


def _snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def _mark_vault(vault: Path) -> None:
    """Declare a real vault so wiki-root linting may resolve parent targets."""
    (vault / ".claude-obsidian.json").write_text(
        json.dumps({"schema": "claude-obsidian.workspace.v1", "vault": "."}),
        encoding="utf-8",
    )


def _canonical_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class LintEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = lint_engine.lint_vault(FIXTURE)

    def test_report_schema_and_all_required_categories(self) -> None:
        self.assertEqual(1, self.report["version"])
        self.assertEqual("1.2.0", self.report["engine_version"])
        self.assertEqual(8, self.report["summary"]["pages_scanned"])
        self.assertEqual(18, self.report["summary"]["links_scanned"])
        for category in (
            "dead_links",
            "ambiguous_targets",
            "duplicate_basenames",
            "orphans",
            "missing_frontmatter",
            "empty_sections",
            "stale_index_entries",
            "read_errors",
            "configuration_errors",
            "provenance_errors",
        ):
            self.assertIn(category, self.report)
            self.assertEqual(
                len(self.report[category]),
                self.report["summary"]["category_counts"][category],
            )

    def test_wikilinks_embeds_aliases_paths_fragments_and_code_are_parsed(self) -> None:
        dead_targets = {
            (item["target"], item["reason"]) for item in self.report["dead_links"]
        }
        self.assertEqual(
            {
                ("Alpha#No such heading", "heading-not-found"),
                ("Alpha#^missing-block", "block-not-found"),
                ("Gone", "target-not-found"),
            },
            dead_targets,
        )

        # Each of these exercises a parser edge and must resolve without a
        # finding: path links, escaped-pipe aliases, frontmatter aliases,
        # existing heading/block fragments, and an attachment embed.
        all_reported_targets = {
            item.get("target", "")
            for category in ("dead_links", "ambiguous_targets", "stale_index_entries")
            for item in self.report[category]
        }
        for resolved in (
            "concepts/Alpha",
            "First Alpha",
            "A, Prime",
            "Alpha#Known heading",
            "Alpha#^alpha-block",
            "assets/picture.txt",
        ):
            self.assertNotIn(resolved, all_reported_targets)
        self.assertNotIn("Inline Code Ghost", all_reported_targets)
        self.assertNotIn("Fence Ghost", all_reported_targets)

    def test_ambiguous_basename_and_stale_index_entries(self) -> None:
        self.assertEqual(
            [
                {
                    "basename": "Shared",
                    "paths": ["wiki/concepts/Shared.md", "wiki/entities/Shared.md"],
                }
            ],
            self.report["duplicate_basenames"],
        )
        ambiguous = self.report["ambiguous_targets"]
        self.assertEqual(1, len(ambiguous))
        self.assertEqual("Shared", ambiguous[0]["target"])
        self.assertEqual(
            ["wiki/concepts/Shared.md", "wiki/entities/Shared.md"],
            ambiguous[0]["candidates"],
        )
        self.assertEqual(
            [("Shared", "ambiguous-target"), ("Gone", "target-not-found")],
            [
                (item["target"], item["reason"])
                for item in self.report["stale_index_entries"]
            ],
        )

    def test_extensionless_canvas_and_base_links_resolve_without_hiding_ambiguity(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "wiki/views").mkdir(parents=True)
            (root / "wiki/index.md").write_text(
                """---
title: Index
type: meta
status: evergreen
created: 2026-07-12
updated: 2026-07-12
tags:
  - meta
---

# Index

- [[Map]]
- [[views/Board]]
- [[Database]]
- [[Shared View]]
- [[Shared View.canvas]]
""",
                encoding="utf-8",
            )
            for relative in (
                "wiki/Map.canvas",
                "wiki/views/Board.canvas",
                "wiki/Database.base",
                "wiki/Shared View.base",
                "wiki/Shared View.canvas",
            ):
                (root / relative).write_text("{}\n", encoding="utf-8")

            report = lint_engine.lint_vault(root, as_of="2026-07-12")

        self.assertEqual([], report["dead_links"])
        self.assertEqual(
            [
                {
                    "source": "wiki/index.md",
                    "line": 16,
                    "target": "Shared View",
                    "syntax": "wikilink",
                    "candidates": ["wiki/Shared View.base", "wiki/Shared View.canvas"],
                }
            ],
            report["ambiguous_targets"],
        )
        self.assertEqual(
            [("Shared View", "ambiguous-target")],
            [
                (item["target"], item["reason"])
                for item in report["stale_index_entries"]
            ],
        )

    def test_directory_indexes_do_not_create_duplicate_noise(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ("wiki/concepts/_index.md", "wiki/entities/_index.md"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "---\n"
                    f"title: {path.parent.name.title()} Index\n"
                    "type: meta\nstatus: evergreen\ncreated: 2026-07-12\n"
                    "updated: 2026-07-12\ntags:\n  - meta\n---\n\n# Index\n",
                    encoding="utf-8",
                )
            (root / "wiki/index.md").write_text(
                "---\ntitle: Root Index\ntype: meta\nstatus: evergreen\n"
                "created: 2026-07-12\nupdated: 2026-07-12\ntags:\n  - meta\n---\n\n"
                "# Root Index\n\n- [[concepts/_index]]\n- [[entities/_index]]\n- [[_index]]\n",
                encoding="utf-8",
            )

            report = lint_engine.lint_vault(root, as_of="2026-07-12")

        self.assertEqual([], report["duplicate_basenames"])
        self.assertEqual(1, len(report["ambiguous_targets"]))
        self.assertEqual("_index", report["ambiguous_targets"][0]["target"])

    @staticmethod
    def _write_unicode_page(root: Path, relative: str, body: str = "") -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\ntitle: Page\ntype: concept\nstatus: evergreen\n"
            "created: 2026-07-12\nupdated: 2026-07-12\ntags:\n  - concept\n---\n\n"
            f"# Page\n\n{body}\n",
            encoding="utf-8",
        )

    def test_nfc_and_nfd_spellings_resolve_to_the_same_note(self) -> None:
        nfc_jeova = unicodedata.normalize("NFC", "Jeová")
        nfd_jeova = unicodedata.normalize("NFD", "Jeová")
        nfc_cafe = unicodedata.normalize("NFC", "Café")
        nfd_cafe = unicodedata.normalize("NFD", "Café")
        self.assertNotEqual(nfc_jeova, nfd_jeova)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Decomposed file names, as macOS and iCloud deliver them, linked
            # with composed text; and the reverse.
            self._write_unicode_page(root, f"wiki/concepts/Confiar em {nfd_jeova}.md")
            self._write_unicode_page(root, f"wiki/entities/{nfc_cafe}.md")
            self._write_unicode_page(
                root,
                "wiki/index.md",
                f"- [[Confiar em {nfc_jeova}]]\n"
                f"- [[concepts/Confiar em {nfc_jeova}]]\n"
                f"- [[wiki/concepts/Confiar em {nfc_jeova}.md]]\n"
                f"- [[{nfd_cafe}]]\n"
                f"- [[entities/{nfd_cafe}]]\n",
            )
            on_disk = sorted(
                path.relative_to(root).as_posix()
                for path in (root / "wiki").rglob("*.md")
                if path.name != "index.md"
            )

            report = lint_engine.lint_vault(root, as_of="2026-07-12")

        self.assertEqual([], report["dead_links"])
        self.assertEqual([], report["ambiguous_targets"])
        self.assertEqual([], report["duplicate_basenames"])
        self.assertEqual([], report["orphans"])
        # Reported paths keep the on-disk spelling.
        self.assertIn(f"wiki/concepts/Confiar em {nfd_jeova}.md", on_disk)
        self.assertIn(f"wiki/entities/{nfc_cafe}.md", on_disk)

    def test_unicode_normalization_keeps_real_duplicates_and_distinct_names(
        self,
    ) -> None:
        nfc_jeova = unicodedata.normalize("NFC", "Jeová")
        nfd_jeova = unicodedata.normalize("NFD", "Jeová")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # One name spelled in both forms in two folders is a real duplicate.
            self._write_unicode_page(root, f"wiki/concepts/{nfd_jeova}.md")
            self._write_unicode_page(root, f"wiki/entities/{nfc_jeova}.md")
            # An unaccented spelling is a different name and stays distinct.
            self._write_unicode_page(root, "wiki/sources/Jeova.md")
            self._write_unicode_page(
                root,
                "wiki/index.md",
                f"- [[{nfc_jeova}]]\n- [[Jeova]]\n- [[Jeovà]]\n",
            )

            report = lint_engine.lint_vault(root, as_of="2026-07-12")

        self.assertEqual(
            [
                {
                    "basename": nfd_jeova,
                    "paths": [
                        f"wiki/concepts/{nfd_jeova}.md",
                        f"wiki/entities/{nfc_jeova}.md",
                    ],
                }
            ],
            report["duplicate_basenames"],
        )
        self.assertEqual(
            [
                (
                    nfc_jeova,
                    [f"wiki/concepts/{nfd_jeova}.md", f"wiki/entities/{nfc_jeova}.md"],
                )
            ],
            [
                (item["target"], item["candidates"])
                for item in report["ambiguous_targets"]
            ],
        )
        self.assertEqual(
            [("Jeovà", "target-not-found")],
            [(item["target"], item["reason"]) for item in report["dead_links"]],
        )

    def test_orphans_frontmatter_empty_sections_and_allowlist(self) -> None:
        self.assertEqual([{"path": "wiki/concepts/Orphan.md"}], self.report["orphans"])
        self.assertEqual(1, len(self.report["missing_frontmatter"]))
        gap = self.report["missing_frontmatter"][0]
        self.assertEqual("wiki/concepts/Missing Frontmatter.md", gap["path"])
        self.assertFalse(gap["has_frontmatter"])
        self.assertEqual(
            ["title", "type", "status", "created", "updated", "tags"],
            gap["missing_fields"],
        )
        self.assertEqual(
            [
                {
                    "path": "wiki/concepts/Empty Section Page.md",
                    "line": 14,
                    "heading": "Empty",
                }
            ],
            self.report["empty_sections"],
        )
        self.assertEqual(1, len(self.report["allowlisted_dangling_links"]))
        self.assertEqual(
            "Allowed Future Page",
            self.report["allowlisted_dangling_links"][0]["target"],
        )
        self.assertNotIn(
            "Allowed Future Page",
            {item["target"] for item in self.report["dead_links"]},
        )

    def test_repeated_runs_and_different_checkout_paths_are_byte_identical(
        self,
    ) -> None:
        expected_json = _canonical_json(self.report)
        expected_markdown = lint_engine.render_markdown(self.report)
        for _ in range(4):
            repeated = lint_engine.lint_vault(FIXTURE)
            self.assertEqual(expected_json, _canonical_json(repeated))
            self.assertEqual(expected_markdown, lint_engine.render_markdown(repeated))

        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "relocated-vault"
            shutil.copytree(FIXTURE, copy)
            relocated = lint_engine.lint_vault(copy)
        self.assertEqual(expected_json, _canonical_json(relocated))
        self.assertEqual(expected_markdown, lint_engine.render_markdown(relocated))

    def test_lint_is_strictly_read_only(self) -> None:
        before = _snapshot(FIXTURE)
        lint_engine.lint_vault(FIXTURE)
        lint_engine.render_markdown(self.report)
        after = _snapshot(FIXTURE)
        self.assertEqual(before, after)

    def test_invalid_utf8_markdown_is_a_read_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            (vault / "wiki").mkdir(parents=True)
            (vault / "wiki/Broken.md").write_bytes(b"# Broken\n\xff\n")
            report = lint_engine.lint_vault(vault, as_of="2026-07-11")
        self.assertEqual(1, len(report["read_errors"]))
        self.assertEqual("wiki/Broken.md", report["read_errors"][0]["path"])
        self.assertIn("UnicodeDecodeError", report["read_errors"][0]["message"])

    def test_existing_names_refused_for_writes_are_still_linted(self) -> None:
        # macOS and vaults synced from it store decomposed (NFD) names; a POSIX
        # filename may hold a backslash. Writes refuse both, reads must not.
        import unicodedata

        names = [unicodedata.normalize("NFD", "Résumé")]
        if os.sep == "/":
            names.append("Back\\slash")
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            (vault / "wiki").mkdir(parents=True)
            _mark_vault(vault)
            (vault / "wiki/Target.md").write_text("# Target\n", encoding="utf-8")
            created = []
            for name in names:
                try:
                    (vault / "wiki" / f"{name}.md").write_text(
                        "# Note\n[[Target]]\n", encoding="utf-8"
                    )
                except OSError:
                    continue
                created.append(name)
            if not created:
                self.skipTest("filesystem rejects these filenames")
            report = lint_engine.lint_vault(vault, as_of="2026-10-20")
        self.assertEqual([], report["read_errors"])
        self.assertNotIn(
            "wiki/Target.md", {item["path"] for item in report["orphans"]}
        )

    def test_non_utf8_filename_is_escaped_in_json_and_markdown_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            (vault / ".obsidian").mkdir(parents=True)
            (vault / "wiki").mkdir()
            raw_path = os.fsencode(vault / "wiki") + b"/Bad-\xff.md"
            try:
                descriptor = os.open(
                    raw_path,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                )
            except OSError as exc:
                if exc.errno in {errno.EILSEQ, errno.EINVAL}:
                    self.skipTest(
                        "filesystem rejects filenames that are not valid UTF-8"
                    )
                raise
            try:
                os.write(descriptor, b"# Bad\n")
            finally:
                os.close(descriptor)
            (vault / "wiki" / r"Bad-\udcff.md").write_text(
                "# Literal escape\n", encoding="utf-8"
            )
            report = lint_engine.lint_vault(vault, as_of="2026-07-11")
            serialized = json.dumps(report, ensure_ascii=False)
            serialized.encode("utf-8", errors="strict")
            expected_paths = {
                r"wiki/Bad-\udcff.md",
                r"wiki/Bad-\\udcff.md",
            }
            self.assertTrue(
                expected_paths.issubset({item["path"] for item in report["orphans"]})
            )
            self.assertEqual([], report["read_errors"])

            commands = (
                [
                    sys.executable,
                    str(ENGINE_PATH),
                    str(vault),
                    "--format",
                    "json",
                    "--as-of",
                    "2026-07-11",
                ],
                [
                    sys.executable,
                    str(ENGINE_PATH),
                    str(vault),
                    "--format",
                    "markdown",
                    "--as-of",
                    "2026-07-11",
                ],
                [
                    sys.executable,
                    str(ROOT / "scripts/claude-obsidian.py"),
                    "lint",
                    "--vault",
                    str(vault),
                    "--format",
                    "json",
                    "--as-of",
                    "2026-07-11",
                ],
                [
                    sys.executable,
                    str(ROOT / "scripts/claude-obsidian.py"),
                    "lint",
                    "--vault",
                    str(vault),
                    "--format",
                    "markdown",
                    "--as-of",
                    "2026-07-11",
                ],
            )
            for command in commands:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    timeout=10,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                decoded = completed.stdout.decode("utf-8", errors="strict")
                if "json" in command:
                    parsed = json.loads(decoded)
                    self.assertTrue(
                        expected_paths.issubset(
                            {item["path"] for item in parsed["orphans"]}
                            | {item["path"] for item in parsed["read_errors"]}
                        )
                    )
                else:
                    for expected_path in expected_paths:
                        self.assertIn(expected_path, decoded)

    def test_markdown_and_cli_are_stable(self) -> None:
        markdown = lint_engine.render_markdown(self.report)
        self.assertTrue(markdown.endswith("\n"))
        self.assertIn("# Wiki Lint Report", markdown)
        self.assertIn("## Dead Links", markdown)
        self.assertIn("## Allowlisted Dangling Links", markdown)

        completed = subprocess.run(
            [sys.executable, str(ENGINE_PATH), str(FIXTURE), "--format", "json"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(self.report, json.loads(completed.stdout))
        self.assertEqual("", completed.stderr)

    def test_invalid_allowlist_is_reported_without_aborting_or_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            allowlist = copy / ".vault-meta" / "lint-allowlist.json"
            allowlist.write_text("{invalid", encoding="utf-8")
            before = _snapshot(copy)
            report = lint_engine.lint_vault(copy)
            after = _snapshot(copy)
        self.assertEqual(before, after)
        self.assertEqual(1, len(report["configuration_errors"]))
        self.assertIn(
            "invalid allowlist JSON", report["configuration_errors"][0]["message"]
        )
        self.assertIn(
            "Allowed Future Page",
            {item["target"] for item in report["dead_links"]},
        )

    def test_allowlist_json_rejects_duplicates_and_nonfinite_numbers(self) -> None:
        for content in (
            '{"dangling_links":[],"dangling_links":["Allowed Future Page"]}',
            '{"dangling_links":["Allowed Future Page"],"weight":1e999}',
        ):
            with (
                self.subTest(content=content),
                tempfile.TemporaryDirectory() as directory,
            ):
                copy = Path(directory) / "vault"
                shutil.copytree(FIXTURE, copy)
                (copy / ".vault-meta/lint-allowlist.json").write_text(
                    content, encoding="utf-8"
                )
                report = lint_engine.lint_vault(copy)
                self.assertTrue(report["configuration_errors"])
                self.assertIn(
                    "Allowed Future Page",
                    {item["target"] for item in report["dead_links"]},
                )

    def test_symlinked_allowlist_ancestor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            copy = base / "vault"
            shutil.copytree(FIXTURE, copy)
            shutil.rmtree(copy / ".vault-meta")
            outside = base / "outside-meta"
            outside.mkdir()
            (outside / "lint-allowlist.json").write_text(
                json.dumps(["Gone"]), encoding="utf-8"
            )
            (copy / ".vault-meta").symlink_to(outside, target_is_directory=True)
            report = lint_engine.lint_vault(copy, as_of="2026-07-11")
        self.assertTrue(report["configuration_errors"])
        self.assertIn("Gone", {item["target"] for item in report["dead_links"]})

    def test_invalid_provenance_is_reported_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            ledgers = copy / "wiki" / "meta" / "ledgers"
            ledgers.mkdir(parents=True)
            (ledgers / "source-ledger.json").write_text(
                json.dumps(
                    {
                        "schema": "claude-obsidian.source-ledger.v1",
                        "generated_at": "2026-07-11T00:00:00Z",
                        "sources": {},
                    }
                ),
                encoding="utf-8",
            )
            (ledgers / "claim-ledger.json").write_text(
                json.dumps(
                    {
                        "schema": "claude-obsidian.claim-ledger.v1",
                        "generated_at": "2026-07-11T00:00:00Z",
                        "claims": {
                            "clm-unsafe": {
                                "text": "An unsupported accepted claim.",
                                "risk": "normal",
                                "assessment": "accepted",
                                "confidence": "high",
                                "evidence": [],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            before = _snapshot(copy)
            report = lint_engine.lint_vault(copy)
            after = _snapshot(copy)
        self.assertEqual(before, after)
        self.assertTrue(report["provenance_errors"])
        self.assertIn(
            "accepted claims require fresh active support",
            {item["message"] for item in report["provenance_errors"]},
        )

    def test_duplicate_provenance_json_keys_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            ledgers = copy / "wiki/meta/ledgers"
            ledgers.mkdir(parents=True)
            duplicate = (
                '{"schema":"claude-obsidian.source-ledger.v1",'
                '"generated_at":"2026-07-11T00:00:00Z",'
                '"sources":{"src-a":{},"src-a":{}}}'
            )
            (ledgers / "source-ledger.json").write_text(duplicate, encoding="utf-8")
            report = lint_engine.lint_vault(copy, as_of="2026-07-11")
        self.assertTrue(report["provenance_errors"])
        self.assertTrue(
            any(
                "DuplicateJSONKeyError" in item["message"]
                for item in report["provenance_errors"]
            )
        )

    def test_oversized_ledger_error_names_the_code_and_capacity_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            ledgers = copy / "wiki/meta/ledgers"
            ledgers.mkdir(parents=True)
            with unittest.mock.patch.object(lint_engine, "MAX_CANONICAL_LEDGER_BYTES", 64):
                (ledgers / "source-ledger.json").write_text(
                    '{"schema":"claude-obsidian.source-ledger.v1",'
                    + '"generated_at":"2026-07-11T00:00:00Z","sources":{}}'
                    + " " * 64,
                    encoding="utf-8",
                )
                report = lint_engine.lint_vault(copy, as_of="2026-07-11")
        messages = [item["message"] for item in report["provenance_errors"]]
        self.assertTrue(
            any("VAULT_FILE_TOO_LARGE" in m and "capacity compact" in m for m in messages),
            messages,
        )

    def test_provenance_freshness_uses_declared_audit_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            ledgers = copy / "wiki/meta/ledgers"
            ledgers.mkdir(parents=True)
            source_id = stable_source_id("url", "https://example.com/old", None)
            source = {
                "schema": "claude-obsidian.source-ledger.v1",
                "generated_at": "2020-01-01T00:00:00Z",
                "sources": {
                    source_id: {
                        "origin": {"kind": "url", "locator": "https://example.com/old"},
                        "content_kind": "webpage",
                        "title": "Old source",
                        "authority": "official",
                        "content_sha256": None,
                        "ingested_at": None,
                        "retrieved_at": "2020-01-01",
                        "refresh_due": "2020-06-01",
                        "review_status": "active",
                        "independence_key": None,
                        "pages": ["wiki/concepts/Alpha.md"],
                        "supersedes": None,
                    }
                },
            }
            claim = {
                "schema": "claude-obsidian.claim-ledger.v1",
                "generated_at": "2020-01-01T00:00:00Z",
                "claims": {
                    "clm-old": {
                        "text": "A once-supported claim.",
                        "location": {"path": "wiki/concepts/Alpha.md", "anchor": None},
                        "risk": "normal",
                        "assessment": "accepted",
                        "confidence": "high",
                        "evidence": [
                            {
                                "source_id": source_id,
                                "relation": "supports",
                                "locator": None,
                            }
                        ],
                        "reviewed_at": "2020-01-01",
                    }
                },
            }
            (ledgers / "source-ledger.json").write_text(
                json.dumps(source), encoding="utf-8"
            )
            (ledgers / "claim-ledger.json").write_text(
                json.dumps(claim), encoding="utf-8"
            )
            fresh = lint_engine.lint_vault(copy, as_of=date(2020, 5, 1))
            stale = lint_engine.lint_vault(copy, as_of="2026-07-11")
        self.assertEqual("2020-05-01", fresh["as_of"])
        self.assertFalse(fresh["provenance_errors"])
        self.assertTrue(
            any(
                "fresh active support" in item["message"]
                for item in stale["provenance_errors"]
            )
        )

    def test_non_scalar_provenance_url_is_reported_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            ledgers = copy / "wiki/meta/ledgers"
            ledgers.mkdir(parents=True)
            locator = json.loads('"https://example.com/\\ud800"')
            source_id = stable_source_id("url", locator, None)
            document = {
                "schema": "claude-obsidian.source-ledger.v1",
                "generated_at": "2026-07-11T00:00:00Z",
                "sources": {
                    source_id: {
                        "origin": {"kind": "url", "locator": locator},
                        "content_kind": "webpage",
                        "title": "Invalid Unicode source",
                        "authority": "official",
                        "content_sha256": None,
                        "ingested_at": None,
                        "retrieved_at": "2026-07-01",
                        "refresh_due": "2027-01-01",
                        "review_status": "active",
                        "independence_key": None,
                        "pages": [],
                        "supersedes": None,
                    }
                },
            }
            (ledgers / "source-ledger.json").write_text(
                json.dumps(document), encoding="utf-8"
            )
            report = lint_engine.lint_vault(copy, as_of="2026-07-11")
        self.assertTrue(
            any(
                "Unicode scalar values" in item["message"]
                for item in report["provenance_errors"]
            )
        )

    def test_non_scalar_ledger_key_is_safely_reported_by_both_clis(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            ledgers = copy / "wiki/meta/ledgers"
            ledgers.mkdir(parents=True)
            source_id = json.loads('"src-\\ud800"')
            document = {
                "schema": "claude-obsidian.source-ledger.v1",
                "generated_at": "2026-07-11T00:00:00Z",
                "sources": {
                    source_id: {
                        "origin": {
                            "kind": "url",
                            "locator": "https://example.com/source",
                        },
                        "content_kind": "webpage",
                        "title": "Source",
                        "authority": "official",
                        "content_sha256": None,
                        "ingested_at": None,
                        "retrieved_at": "2026-07-01",
                        "refresh_due": "2027-01-01",
                        "review_status": "active",
                        "independence_key": None,
                        "pages": [],
                        "supersedes": None,
                    }
                },
            }
            (ledgers / "source-ledger.json").write_text(
                json.dumps(document), encoding="utf-8"
            )
            report = lint_engine.lint_vault(copy, as_of="2026-07-11")
            fields = {item["field"] for item in report["provenance_errors"]}
            self.assertTrue(any("\\ud800" in field for field in fields))
            for command in (
                [
                    sys.executable,
                    str(ENGINE_PATH),
                    str(copy),
                    "--format",
                    "json",
                    "--as-of",
                    "2026-07-11",
                ],
                [
                    sys.executable,
                    str(ROOT / "scripts/claude-obsidian.py"),
                    "lint",
                    "--vault",
                    str(copy),
                    "--format",
                    "json",
                    "--as-of",
                    "2026-07-11",
                ],
            ):
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertTrue(json.loads(completed.stdout)["provenance_errors"])

    def test_datetime_audit_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "date object"):
            lint_engine.lint_vault(FIXTURE, as_of=datetime(2026, 7, 11))

    def test_malformed_evidence_and_wiki_root_mode_report_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "vault"
            shutil.copytree(FIXTURE, copy)
            ledgers = copy / "wiki/meta/ledgers"
            ledgers.mkdir(parents=True)
            (ledgers / "source-ledger.json").write_text(
                json.dumps({"schema": "wrong", "sources": {}}), encoding="utf-8"
            )
            (ledgers / "claim-ledger.json").write_text(
                json.dumps(
                    {
                        "schema": "claude-obsidian.claim-ledger.v1",
                        "claims": {
                            "clm-bad": {
                                "text": "Bad evidence.",
                                "location": {
                                    "path": "wiki/concepts/Alpha.md",
                                    "anchor": None,
                                },
                                "risk": "normal",
                                "assessment": "accepted",
                                "confidence": "high",
                                "evidence": [{"source_id": [], "relation": []}],
                                "reviewed_at": "2026-07-11",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            report = lint_engine.lint_vault(copy / "wiki", as_of="2026-07-11")
        self.assertTrue(report["provenance_errors"])
        self.assertTrue(
            any(item.get("field") == "schema" for item in report["provenance_errors"])
        )


class ObsidianConformanceTests(unittest.TestCase):
    """Static syntax fixtures, not evidence from the native application."""

    FRONT = (
        "---\ntitle: Fixture\ntype: concept\nstatus: developing\n"
        "created: 2026-10-17\nupdated: 2026-10-17\ntags: []\n---\n"
    )

    def _lint(self, files: dict[str, str], **options) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, text in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            before = _snapshot(root)
            report = lint_engine.lint_vault(root, as_of="2026-10-17", **options)
            self.assertEqual(before, _snapshot(root))
            return report

    def test_protected_regions_do_not_emit_links_and_offsets_survive(self) -> None:
        protected = [
            "%% [[Hidden]] %%", "%%\n[[Hidden]]\n%%", "    [[Hidden]]",
            "\t[[Hidden]]", "    - [[Hidden]]", r"\[[Hidden]]", r"\[Hidden](Missing.md)",
            "`[[Hidden]]`", "`` [[Hidden]] ` literal ``", "$[[Hidden]]$",
            "$$\n[[Hidden]]\n$$", "<!-- [[Hidden]] -->",
            "````markdown\n```\n[[Hidden]]\n```\n````",
            "~~~markdown\n[[Hidden]]\n~~~", "- ```\n  [[Hidden]]\n  ```",
        ]
        for body in protected:
            with self.subTest(body=body):
                text = self.FRONT + "# Fixture\n\n" + body + "\n\n[[Visible]]\n"
                report = self._lint({"wiki/Fixture.md": text})
                self.assertEqual(["Visible"], [x["target"] for x in report["dead_links"]])
                self.assertEqual(text[:text.index("[[Visible]]")].count("\n") + 1,
                                 report["dead_links"][0]["line"])
                masked = lint_engine._mask_markdown_code(text)
                self.assertEqual(len(text), len(masked))
                self.assertEqual([i for i, c in enumerate(text) if c == "\n"],
                                 [i for i, c in enumerate(masked) if c == "\n"])

    def test_literal_comment_markers_in_code_do_not_hide_visible_links(self) -> None:
        for code in ("`<!--`", "`%%`", "```text\n<!--\n```", "    <!--"):
            with self.subTest(code=code):
                report = self._lint({"wiki/Fixture.md": self.FRONT + code + "\n\n[[Visible]]\n"})
                self.assertEqual(["Visible"], [x["target"] for x in report["dead_links"]])

    def test_nested_list_navigation_stays_visible_but_nested_code_does_not(self) -> None:
        text = ("- Parent\n    [[Visible]]\n    - Child\n        [Second](Second.md)\n\n"
                "          [[Hidden]]\n")
        report = self._lint({"wiki/Fixture.md": self.FRONT + text})
        self.assertEqual({"Visible", "Second.md"}, {x["target"] for x in report["dead_links"]})

    def test_list_fences_end_at_container_boundary_without_exposing_code(self) -> None:
        for visible in ('\n[Visible](Visible.md)\n', '- [Visible](Visible.md)\n'):
            with self.subTest(visible=visible):
                text = self.FRONT + '- ```\n  [[Hidden]]\n' + visible
                report = self._lint({"wiki/Fixture.md": text})
                self.assertEqual(["Visible.md"], [x["target"] for x in report["dead_links"]])
                masked = lint_engine._mask_markdown_code(text)
                self.assertEqual(len(text), len(masked))
                self.assertEqual(text.index('[Visible]'), masked.index('[Visible]'))
        for text in ('- ```\n  [[Hidden]]\n  - [Hidden](Hidden.md)\n',
                     '- ```\n  [[Hidden]]\n\n  [Hidden](Hidden.md)\n  ```\n',
                     '```\n[[Hidden]]\n\n[Hidden](Hidden.md)\n'):
            with self.subTest(text=text):
                report = self._lint({"wiki/Fixture.md": self.FRONT + text})
                self.assertEqual([], report["dead_links"])

    def test_markdown_destinations_preserve_literal_math_punctuation(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + '[A](Price$10$.md)\n[B](<Price$10$.md>)\n[[Price$10$]]\n'
                '`[Hidden](Price$10$.md)`\n%% [Hidden](Price$10$.md) %%\n',
            "wiki/Price$10$.md": self.FRONT + "Text.\n",
        })
        self.assertEqual([], report["dead_links"])
        self.assertEqual(3, report["summary"]["links_scanned"])

    def test_angled_and_titled_markdown_destinations_share_resolution(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + '[A](<Target (one).md> "A title")\n[B](Target.md (a title))\n',
            "wiki/Target (one).md": self.FRONT + "Text.\n",
            "wiki/Target.md": self.FRONT + "Text.\n",
        })
        self.assertEqual([], report["dead_links"])
        self.assertEqual(2, report["summary"]["links_scanned"])

    def test_balanced_markdown_labels_respect_escapes_and_code_spans(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[see [Target]](Target.md)\n"
                r"[escaped \] bracket](Escaped.md)" "\n"
                "[code `]` bracket](Code.md)\n"
            ),
            "wiki/Target.md": self.FRONT + "Content.\n",
            "wiki/Escaped.md": self.FRONT + "Content.\n",
            "wiki/Code.md": self.FRONT + "Content.\n",
        })
        self.assertEqual([], report["dead_links"])
        self.assertEqual([], report["orphans"])
        self.assertEqual(3, report["summary"]["links_scanned"])

    def test_large_malformed_bracket_run_emits_no_navigation(self) -> None:
        self.assertEqual([], list(lint_engine.iter_markdown_links("[" * 100_000)))

    def test_encoded_filename_is_split_before_one_decode(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[hash](dir%20%231/file.md#A%20heading)\n"
                "[literal percent](100%2523.md)\n"
                "[[dir%20%231/file#A heading]]\n"
                "[block](dir%20%231/file.md#%5Eblock)\n"
                "[missing](absent%23file.md)\n"
            ),
            "wiki/dir #1/file.md": self.FRONT + "# A heading\n\nText. ^block\n",
            "wiki/100%23.md": self.FRONT + "# Literal percent\n\nText.\n",
        })
        # Wikilink targets are literal text; only Markdown destinations decode.
        self.assertEqual([
            ("absent#file.md", "target-not-found"),
            ("dir%20%231/file#A heading", "target-not-found"),
        ], sorted(
            (entry["target"], entry["reason"]) for entry in report["dead_links"]
        ))

    def test_flat_vault_is_diagnosed_without_expanding_page_scope(self) -> None:
        report = self._lint({
            ".obsidian/app.json": "{}\n",
            "Note.md": "[[Missing]]\n",
        })
        self.assertEqual(0, report["summary"]["pages_scanned"])
        self.assertEqual(0, report["summary"]["links_scanned"])
        self.assertEqual("no-pages-in-scope", report["scope"]["coverage"])
        self.assertEqual(1, report["summary"]["markdown_files_outside_scope"])
        self.assertEqual("no-pages-in-scope", report["configuration_errors"][0]["reason"])
        self.assertEqual([], report["missing_frontmatter"])

    def test_empty_vault_is_distinct_from_unscanned_content(self) -> None:
        report = self._lint({".obsidian/app.json": "{}\n"})
        self.assertEqual("empty", report["scope"]["coverage"])
        self.assertEqual([], report["configuration_errors"])

    def test_coverage_accounts_for_outside_and_excluded_markdown(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + "Text.\n",
            "wiki/draft.md": "[[Missing]]\n",
            "Inbox.md": "[[Unscanned]]\n",
        }, exclude=["wiki/draft.md"])
        self.assertEqual(3, report["summary"]["markdown_files_discovered"])
        self.assertEqual(1, report["summary"]["markdown_files_excluded"])
        self.assertEqual(1, report["summary"]["markdown_files_outside_scope"])
        self.assertEqual("partial", report["scope"]["coverage"])

    @unittest.skipUnless(lint_engine._supports_hidden_checks(), "confined stat unavailable")
    def test_existing_hidden_source_and_missing_source_are_distinct(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[source](../.raw/capture/source.txt)\n"
                "[missing](../.raw/capture/missing.txt)\n"
                "[[source]]\n"
            ),
            ".raw/capture/source.txt": "Immutable source.\n",
            ".raw/capture/source.md": "[[Invisible ghost]]\n",
        })
        self.assertEqual(
            {"../.raw/capture/missing.txt", "source"},
            {entry["target"] for entry in report["dead_links"]},
        )
        self.assertEqual(1, len(report["hidden_target_links"]))
        self.assertEqual("hidden-target-exists-not-indexed", report["hidden_target_links"][0]["reason"])
        self.assertEqual(".raw/capture/source.txt", report["hidden_target_links"][0]["resolved_path"])
        self.assertEqual(1, report["summary"]["pages_scanned"])

    def test_hidden_target_status_is_explicit_when_confined_checks_are_unavailable(self) -> None:
        with mock.patch.object(lint_engine, "_supports_hidden_checks", return_value=False):
            report = self._lint({
                "wiki/index.md": self.FRONT + (
                    "[source](../.raw/source.txt)\n[missing](../.raw/missing.txt)\n"
                ),
                ".raw/source.txt": "Source.\n",
            })
        self.assertEqual([], report["dead_links"])
        self.assertEqual(["hidden-target-status-unverified"] * 2, [
            entry["reason"] for entry in report["hidden_target_links"]
        ])
        self.assertNotIn("existing hidden file", lint_engine.render_markdown(report))

    def test_hidden_source_checks_never_follow_symlinks_or_escape_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "vault"
            (root / "wiki").mkdir(parents=True)
            (root / ".raw").mkdir()
            external = Path(directory) / "outside.txt"
            external.write_text("Private.\n", encoding="utf-8")
            try:
                (root / ".raw/source.txt").symlink_to(external)
                (root / ".raw/ancestor").symlink_to(external.parent, target_is_directory=True)
            except OSError:
                self.skipTest("symlinks unavailable")
            (root / "wiki/index.md").write_text(self.FRONT + (
                "[link](../.raw/source.txt)\n"
                "[ancestor](../.raw/ancestor/outside.txt)\n"
                "[outside](../../outside.txt)\n"
            ), encoding="utf-8")
            report = lint_engine.lint_vault(root, as_of="2026-10-17")
        if lint_engine._supports_hidden_checks():
            self.assertEqual([], report["hidden_target_links"])
            self.assertEqual(3, len(report["dead_links"]))
        else:
            self.assertEqual(1, len(report["dead_links"]))
            self.assertEqual(["hidden-target-status-unverified"] * 2, [
                entry["reason"] for entry in report["hidden_target_links"]
            ])

    def test_nested_heading_paths_obey_parent_hierarchy(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[[Topic#Parent#Child]]\n"
                "[[Topic#Other#Child]]\n"
                "[[Topic#Parent#Leaf]]\n"
                "[encoded](Topic.md#Parent%23Child)\n"
                "[[Topic#Parent#Absent]]\n"
                "[[Topic#Other#Leaf]]\n"
            ),
            "wiki/Topic.md": self.FRONT + (
                "# Parent\n\nIntro.\n## **Child**\n\nContent.\n"
                "### Leaf\n\nContent.\n# Other\n\nIntro.\n## Child\n\nContent.\n"
            ),
        })
        self.assertEqual({"Topic#Parent#Absent", "Topic#Other#Leaf"}, {
            entry["target"] for entry in report["dead_links"]
        })

    def test_same_note_nested_heading_path_resolves(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            "[[#Parent#Child]]\n\n# Parent\n\nText.\n## Child\n\nText.\n"
        )})
        self.assertEqual([], report["dead_links"])

    def test_setext_headings_resolve_fragments_and_mixed_hierarchy(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[encoded](Topic.md#Parent%23Real%20heading)\n"
                "[[Topic#Parent#Real heading#Leaf]]\n"
                "[[Topic#Other#Child]]\n[[Topic#Parent#Child]]\n"
            ),
            "wiki/Topic.md": self.FRONT + (
                "Parent\n======\n\nIntro.\n\nReal heading\n------------\n\nContent.\n"
                "### Leaf\n\nContent.\n\nOther\n=====\n\nIntro.\n## Child\n\nContent.\n"
            ),
        })
        self.assertEqual(["Topic#Parent#Child"], [item['target'] for item in report['dead_links']])
        self.assertEqual([], report['empty_sections'])

    def test_multiline_setext_heading_uses_entire_paragraph(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[[Topic#First line second line]]\n[[Topic#second line]]\n"
                "[encoded](Topic.md#First%20line%20second%20line)\n"
            ),
            "wiki/Topic.md": self.FRONT + (
                "First line\nsecond line\n===========\n\nContent.\n"
            ),
        })
        self.assertEqual(['Topic#second line'], [item['target'] for item in report['dead_links']])

    def test_styled_setext_and_atx_headings_keep_visible_inline_text(self) -> None:
        for title, fragment in (
            ('Heading `code`', 'Heading code'),
            ('`Entire code title`', 'Entire code title'),
            ('Heading [link label](https://example.com/)', 'Heading link label'),
            ('Heading **strong** and *emphasis*', 'Heading strong and emphasis'),
            ('Heading [`code label`](https://example.com/)', 'Heading code label'),
        ):
            for heading in (title + '\n====\n', '# ' + title + '\n'):
                with self.subTest(title=title, heading=heading):
                    report = self._lint({'wiki/index.md': self.FRONT + (
                        f'[[#{fragment}]]\n[[#Heading]]\n\n' + heading + '\nContent.\n'
                    )})
                    self.assertEqual(['#Heading'], [item['target'] for item in report['dead_links']])
                    self.assertEqual([], report['empty_sections'])

    def test_heading_links_use_balanced_labels_and_visible_wikilink_aliases(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[[Heading#Docs]]\n[[Heading#Readable heading]]\n"
                "[literal](Heading.md#%5BDocs%5D%28folder_%28x%29.md%29)\n"
            ),
            "wiki/Heading.md": self.FRONT + (
                "# [Docs](folder_(x).md)\n\nContent.\n"
                "# [[Target|Readable heading]]\n\nContent.\n"
                "# `[Docs](folder_(x).md)`\n\nContent.\n"
            ),
            "wiki/folder_(x).md": self.FRONT + "# Destination\n\nContent.\n",
            "wiki/Target.md": self.FRONT + "# Target\n\nContent.\n",
        })
        self.assertEqual([], report["dead_links"])

    def test_wikilink_text_in_inline_code_remains_a_literal_heading(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "[literal](Heading.md#%5B%5BTarget%7CVisible%5D%5D)\n"
                "[alias only](Heading.md#Visible)\n"
            ),
            "wiki/Heading.md": self.FRONT + "# `[[Target|Visible]]`\n\nContent.\n",
        })
        self.assertEqual(
            ["Heading.md#Visible"], [entry["target"] for entry in report["dead_links"]]
        )

    def test_styled_multiline_setext_heading_keeps_inline_code_text(self) -> None:
        report = self._lint({'wiki/index.md': self.FRONT + (
            '[[#First code second label]]\n[[#First second label]]\n\n'
            'First `code`\nsecond **label**\n====\n\nContent.\n'
        )})
        self.assertEqual(['#First second label'], [item['target'] for item in report['dead_links']])

    def test_protected_styled_examples_cannot_create_heading_labels(self) -> None:
        for protected in (
            '```markdown\nFake `code`\n====\n# Fake `code`\n```',
            '    Fake `code`\n    ====\n    # Fake `code`',
            '<!--\nFake `code`\n====\n# Fake `code`\n-->',
            '%%\nFake `code`\n====\n# Fake `code`\n%%',
            '$$\nFake `code`\n====\n# Fake `code`\n$$',
        ):
            with self.subTest(protected=protected):
                report = self._lint({'wiki/index.md': self.FRONT + (
                    '[[#Fake code]]\n\n' + protected + '\n\n# Visible\n\nContent.\n'
                )})
                self.assertEqual(['#Fake code'], [item['target'] for item in report['dead_links']])

    def test_multiline_inline_code_cannot_manufacture_block_heading_markers(self) -> None:
        report = self._lint({'wiki/index.md': self.FRONT + (
            '[[#Fake setext]]\n[[#start]]\n[[#Visible code]]\n\n'
            '`start\nFake setext\n====`\nend`\n\n# Visible `code`\n\nContent.\n'
        )})
        self.assertEqual({'#Fake setext', '#start'}, {item['target'] for item in report['dead_links']})

    def test_inline_code_cannot_cross_a_paragraph_interrupting_heading(self) -> None:
        # CommonMark parses blocks first: the ATX line ends the paragraph, so
        # the unmatched backtick stays literal and the heading is real.
        report = self._lint({'wiki/index.md': self.FRONT + (
            '[[#Real atx]]\n[[#start]]\n\n`start\n# Real atx\n====\nend`\n\nContent.\n'
        )})
        self.assertEqual({'#start'}, {item['target'] for item in report['dead_links']})

    def test_inline_code_comment_and_math_markers_do_not_hide_following_headings(self) -> None:
        report = self._lint({'wiki/index.md': self.FRONT + (
            '[[#Literal <!-- marker]]\n[[#Literal $fake$ marker]]\n[[#Following]]\n\n'
            '# Literal `<!--` marker\n\nContent.\n\n'
            '# Literal `$fake$` marker\n\nContent.\n\n# Following\n\nContent.\n'
        )})
        self.assertEqual([], report['dead_links'])

    def test_raw_html_blocks_cannot_create_atx_or_setext_headings(self) -> None:
        for tag in ('div', 'script', 'pre', 'style', 'textarea', 'DIV'):
            with self.subTest(tag=tag):
                report = self._lint({'wiki/index.md': self.FRONT + (
                    f'[[#<{tag}> Fake]]\n[[#Fake atx]]\n[[#Real code]]\n\n'
                    f'<{tag}>\nFake\n====\n# Fake atx\n</{tag}>\n\n'
                    'Real `code`\n====\n\nContent.\n'
                )})
                self.assertEqual({f'#<{tag}> Fake', '#Fake atx'}, {
                    item['target'] for item in report['dead_links']
                })
                self.assertEqual([], report['empty_sections'])

    def test_raw_html_text_blocks_use_actual_closer_and_block_tags_use_blank_boundary(self) -> None:
        report = self._lint({'wiki/index.md': self.FRONT + (
            '[[#Visible]]\n[[#Script fake]]\n[[#Div fake]]\n\n'
            '<script>\n\n# Script fake\n`</script>`\n'
            '# Visible\n\nContent.\n\n'
            '<div>\n</div>\n# Div fake\n\nContent.\n'
        )})
        self.assertEqual({'#Script fake', '#Div fake'}, {item['target'] for item in report['dead_links']})

    def test_html_literals_in_inline_and_fenced_code_do_not_start_raw_blocks(self) -> None:
        report = self._lint({'wiki/index.md': self.FRONT + (
            '[[#Literal <div>]]\n[[#After sample]]\n\n'
            '# Literal `<div>`\n\nContent.\n\n'
            '```html\n<script>\n# Fake\n====\n```\n\n'
            '# After sample\n\nContent.\n'
        )})
        self.assertEqual([], report['dead_links'])

    def test_markdown_markers_inside_raw_html_do_not_swallow_following_headings(self) -> None:
        for marker in ('```', '`unclosed', '<!-- unclosed', '$$'):
            with self.subTest(marker=marker):
                report = self._lint({'wiki/index.md': self.FRONT + (
                    '[[#Following code]]\n\n<script>\n' + marker + '\n</script>\n\n'
                    '# Following `code`\n\nContent.\n'
                )})
                self.assertEqual([], report['dead_links'])

    def test_literal_markdown_in_raw_html_cannot_hide_later_html_block_openers(self) -> None:
        for marker in ('```', '<!-- unclosed', '`unclosed', '$$'):
            with self.subTest(marker=marker):
                report = self._lint({'wiki/index.md': self.FRONT + (
                    '[[#Hidden]]\n[[#<div> Hidden setext]]\n[[#Visible code]]\n\n'
                    '<script>\n' + marker + '\n</script>\n\n'
                    '<div>\n# Hidden\nHidden setext\n====\n</div>\n\n'
                    '# Visible `code`\n\nContent.\n'
                )})
                self.assertEqual({'#Hidden', '#<div> Hidden setext'}, {
                    item['target'] for item in report['dead_links']
                })
                self.assertEqual([], report['empty_sections'])

    def test_literal_html_in_code_cannot_open_a_block_before_later_visible_heading(self) -> None:
        for literal in ('`<script>`', '```html\n<script>\n<div>\n```',
                        '`start\n<div>\nend`'):
            with self.subTest(literal=literal):
                report = self._lint({'wiki/index.md': self.FRONT + (
                    '[[#Visible code]]\n\n' + literal + '\n\n'
                    '# Visible `code`\n\nContent.\n'
                )})
                self.assertEqual([], report['dead_links'])

    def test_setext_empty_sections_share_heading_boundaries_and_source_lines(self) -> None:
        body = ('Parent\n======\n\nEmpty child\n-----------\n\n'
                'Next\n====\n\nContent.\n\n# Atx empty\n')
        report = self._lint({'wiki/index.md': self.FRONT + body})
        self.assertEqual([
            {'path': 'wiki/index.md', 'line': 9, 'heading': 'Parent'},
            {'path': 'wiki/index.md', 'line': 12, 'heading': 'Empty child'},
            {'path': 'wiki/index.md', 'line': 20, 'heading': 'Atx empty'},
        ], report['empty_sections'])

    def test_setext_examples_inside_protected_regions_do_not_become_headings(self) -> None:
        for protected in (
            '```markdown\nFake\n====\n```', '~~~\nFake\n----\n~~~',
            '    Fake\n    ====', '\tFake\n\t====',
            '<!--\nFake\n====\n-->', '%%\nFake\n----\n%%',
            '`Fake\n====`', '$$\nFake\n====\n$$',
        ):
            with self.subTest(protected=protected):
                report = self._lint({'wiki/index.md': self.FRONT + (
                    '[[#Real]]\n[[#Fake]]\n\n' + protected + '\n\nReal\n====\n\nContent.\n'
                )})
                self.assertEqual(['#Fake'], [item['target'] for item in report['dead_links']])
                self.assertEqual([], report['empty_sections'])

    def test_frontmatter_and_block_markers_are_not_setext_titles(self) -> None:
        for candidate in ('# Fake', '- Fake', '> Fake', '***', '---', '    Fake'):
            with self.subTest(candidate=candidate):
                report = self._lint({'wiki/index.md': self.FRONT + (
                    '[[#Fake]]\n\n' + candidate + '\n====\n\nContent.\n'
                )})
                if candidate == '# Fake':
                    self.assertEqual([], report['dead_links'])
                else:
                    self.assertEqual(['#Fake'], [item['target'] for item in report['dead_links']])
        report = self._lint({'wiki/index.md': '---\ntitle: Fake\n===\n---\n\n[[#title: Fake]]\n'})
        self.assertEqual(['#title: Fake'], [item['target'] for item in report['dead_links']])

    def test_setext_section_with_fenced_content_is_not_empty(self) -> None:
        report = self._lint({'wiki/index.md': self.FRONT + (
            'Code sample\n===========\n\n```text\nExample\n=======\n```\n'
        )})
        self.assertEqual([], report['empty_sections'])

    def test_obsidian_comments_are_empty_but_comment_markers_in_code_are_content(self) -> None:
        body = (
            "# Inline hidden\n\n%% editorial note %%\n\n"
            "# Multiline hidden\n\n%%\neditorial note\n%%\n\n"
            "# Inline code\n\n`%% visible code %%`\n\n"
            "# Fenced code\n\n```text\n%% visible code %%\n```\n\n"
            "# Indented code\n\n    %% visible code %%\n"
        )
        report = self._lint({"wiki/index.md": self.FRONT + body})
        self.assertEqual(
            {"Inline hidden", "Multiline hidden"},
            {entry["heading"] for entry in report["empty_sections"]},
        )

    def test_dot_prefixed_files_and_directories_are_outside_visible_graph(self) -> None:
        report = self._lint({
            'wiki/index.md': self.FRONT + '[[Visible]]\n',
            'wiki/Visible.md': self.FRONT + '# Visible\n\nContent.\n',
            'wiki/.Hidden.md': '# Hidden\n[[Missing]]\n',
            'wiki/.hidden/Secret.md': '# Secret\n[[Missing]]\n',
        })
        self.assertEqual(2, report['summary']['markdown_files_discovered'])
        self.assertEqual([], report['dead_links'])
        self.assertEqual([], report['missing_frontmatter'])

    def test_pdf_options_are_syntax_checked_without_page_count_claim(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                "![[paper.pdf#page=3]]\n![[paper.pdf#height=400]]\n"
                "![[paper.pdf#page=999&height=400]]\n"
                "![[paper.pdf#page=0]]\n![[paper.pdf#height=-2]]\n"
                "![[paper.pdf#page=2&page=3]]\n![[paper.pdf#unknown=3]]\n"
                "![[missing.pdf#page=3]]\n"
            ),
            "wiki/paper.pdf": "Static placeholder, PDF contents are not parsed.\n",
        })
        self.assertEqual(5, len(report["dead_links"]))
        self.assertEqual(3, report["summary"]["pdf_fragments_syntax_checked"])
        self.assertIn("PDF page counts and rendering are not checked", report["scope"]["limitations"])

    def test_named_base_views_resolve_and_unknown_fields_remain_intact(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + (
                '![[Dashboard.base#Wiki pages]]\n![[Dashboard.base#Quoted: view]]\n'
                '![[Dashboard.base#Missing view]]\n'
            ),
            "wiki/Dashboard.base": (
                "filters:\n  and:\n    - file.ext == 'md'\n"
                "views:\n  - type: table\n    name: Wiki pages\n"
                "    futureOption:\n      preserve: [unknown, fields]\n"
                "  - name: 'Quoted: view'\n    type: kanban\n    groupOrder: []\n"
            ),
        })
        self.assertEqual(["base-view-not-found"], [entry["reason"] for entry in report["dead_links"]])
        self.assertEqual([], report["unsupported_fragments"])

    def test_complex_base_yaml_is_unsupported_instead_of_declared_broken(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + "![[Complex.base#Inherited]]\n",
            "wiki/Complex.base": "views:\n  - <<: *shared-view\n",
        })
        self.assertEqual([], report["dead_links"])
        self.assertEqual("base-view-semantics-unsupported", report["unsupported_fragments"][0]["reason"])

    def test_property_links_have_exact_lines_and_aliases_are_only_names(self) -> None:
        report = self._lint({
            "wiki/index.md": (
                '---\ntitle: Fixture\ntype: concept\nstatus: developing\n'
                'created: 2026-10-17\nupdated: 2026-10-17\ntags: []\n'
                'related: ["[[Existing]]", \'[[Missing inline]]\']\n'
                'sources:\n  - "[[Missing block]]"\n'
                'description: "Read [[Missing text]]" # [[Comment ghost]]\n'
                'aliases: ["[[Alias is a name]]"]\n'
                'unquoted: [[Unsupported property syntax]]\n'
                '---\n\n[[Existing]]\n`[[Code ghost]]`\n'
            ),
            "wiki/Existing.md": self.FRONT + "Content.\n",
        })
        self.assertEqual(
            [(8, "Missing inline"), (10, "Missing block"), (11, "Missing text")],
            [(entry["line"], entry["target"]) for entry in report["dead_links"]],
        )
        self.assertEqual(5, report["summary"]["links_scanned"])
        self.assertEqual(4, report["summary"]["property_links_scanned"])
        self.assertEqual([], report["orphans"])

    def test_aliases_share_flat_yaml_quote_list_and_comment_parsing(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT + "[[Doe, John]]\n[[Johnny]]\n",
            "wiki/Person.md": self.FRONT.replace(
                "tags: []", "tags: []\naliases: ['Doe, John']"
            ) + "# Person\n\nContent.\n",
            "wiki/Other.md": self.FRONT.replace(
                "tags: []", 'tags: []\naliases:\n  - "Johnny" # preferred'
            ) + "# Other\n\nContent.\n",
        })
        self.assertEqual([], report["dead_links"])
        self.assertEqual([], report["orphans"])

    def test_default_frontmatter_policy_preserves_adopted_vocabulary(self) -> None:
        report = self._lint({"wiki/index.md": (
            "---\ntitle: Custom\ntype: diary\nstatus: published\n"
            "created: yesterday\nupdated: sometime\ntags: custom\n---\nText.\n"
        )})
        self.assertEqual([], report["invalid_frontmatter"])
        self.assertEqual("presence", report["scope"]["frontmatter_policy"])

    def test_generated_policy_checks_type_status_dates_tags_and_blank_title(self) -> None:
        report = self._lint({"wiki/index.md": (
            '---\ntitle: ""\ntype: diary\nstatus: ""\n'
            'created: 2026-02-30\nupdated: 2026-10-17T12:00:00Z\n'
            'tags: ["2026", "has space", 42]\n---\nText.\n'
        )}, frontmatter_policy="generated")
        self.assertEqual({"title", "type", "status", "created", "updated", "tags"}, {
            entry["field"] for entry in report["invalid_frontmatter"]
        })

    def test_generated_policy_accepts_unicode_tags_and_preserves_custom_properties(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT.replace(
            "tags: []", 'tags: ["year/2026", "知識", "café", "under_score", "🚀", "👩‍💻", "café"]'
        ) + "Content.\n"}, frontmatter_policy="generated")
        self.assertEqual([], report["invalid_frontmatter"])

    def test_malformed_property_values_do_not_fabricate_links(self) -> None:
        report = self._lint({"wiki/index.md": (
            self.FRONT[:-4] +
            'broken: "[[Ghost]]" "extra"\n'
            'nested:\n  mapping: "[[Nested ghost]]"\n'
            'nested_list:\n  mapping:\n    - "[[Nested list ghost]]"\n'
            'unclosed: ["[[Unclosed ghost]]"\n'
            '---\nContent.\n'
        )})
        self.assertEqual([], report["dead_links"])
        self.assertEqual(0, report["summary"]["property_links_scanned"])

    def test_property_scalar_decoding_preserves_physical_line_numbers(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT[:-4] + (
                "related: # list comment\n"
                "- '[[O''Brien]]'\n"
                'description: "Text\\n[[Missing decoded text]]"\n'
                "---\nContent.\n"
            ),
            "wiki/O'Brien.md": self.FRONT + "Content.\n",
        })
        self.assertEqual([(10, "Missing decoded text")], [
            (entry["line"], entry["target"]) for entry in report["dead_links"]
        ])
        self.assertEqual(2, report["summary"]["property_links_scanned"])

    def test_huge_numeric_metadata_does_not_abort_adopted_schema_scan(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT[:-4] + (
            "count: " + "9" * 5000 + "\n---\nText.\n"
        )})
        self.assertEqual([], report["invalid_frontmatter"])
        self.assertEqual(1, report["summary"]["pages_scanned"])

    def test_generated_tags_reject_omitted_flow_list_entries(self) -> None:
        for value in ("[,valid]", "[valid,,also_valid]", "[valid,,]", "[,]"):
            with self.subTest(tags=value):
                report = self._lint({"wiki/index.md": self.FRONT.replace(
                    "tags: []", "tags: " + value
                ) + "Content.\n"}, frontmatter_policy="generated")
                self.assertEqual(["tags"], [entry["field"] for entry in report["invalid_frontmatter"]])

    def test_generated_tags_allow_empty_list_and_legal_trailing_comma(self) -> None:
        for value in ("[]", "[ ]", "[valid,]", "[valid, also_valid, ]"):
            with self.subTest(tags=value):
                report = self._lint({"wiki/index.md": self.FRONT.replace(
                    "tags: []", "tags: " + value
                ) + "Content.\n"}, frontmatter_policy="generated")
                self.assertEqual([], report["invalid_frontmatter"])

    def test_presence_profile_does_not_add_generated_value_validation(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT.replace(
            "tags: []", "tags: [valid,,also_valid]"
        ) + "Content.\n"})
        self.assertEqual([], report["invalid_frontmatter"])
        self.assertEqual(0, report["summary"]["issues_found"])

    def test_unknown_nested_property_reports_parser_scope_without_schema_judgment(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT[:-4] + (
            'custom:\n  nested:\n    - "[[Outside flat subset]]"\n'
            "---\nContent.\n"
        )})
        self.assertEqual([], report["invalid_frontmatter"])
        self.assertEqual([], report["dead_links"])
        self.assertEqual(0, report["summary"]["issues_found"])
        self.assertEqual("partial", report["scope"]["frontmatter_values_coverage"])
        self.assertEqual([{"path": "wiki/index.md", "field": "custom", "line": 8,
                           "reason": "outside-flat-parser-subset"}],
                         report["scope"]["unsupported_frontmatter_values"])

    def test_duplicate_required_property_is_rejected_only_by_generated_profile(self) -> None:
        files = {"wiki/index.md": self.FRONT[:-4] + "title: Duplicate\n---\nContent.\n"}
        adopted = self._lint(files)
        generated = self._lint(files, frontmatter_policy="generated")
        self.assertEqual([], adopted["invalid_frontmatter"])
        self.assertEqual([("title", "duplicate-property")], [
            (entry["field"], entry["reason"]) for entry in generated["invalid_frontmatter"]
        ])

    def test_generated_policy_can_be_selected_from_vault_config(self) -> None:
        report = self._lint({
            "wiki/index.md": self.FRONT.replace("type: concept", "type: unknown") + "Text.\n",
            ".vault-meta/lint.json": json.dumps({"frontmatter_policy": "generated"}),
        })
        self.assertEqual("generated", report["scope"]["frontmatter_policy"])
        self.assertEqual("type", report["invalid_frontmatter"][0]["field"])

    def test_invalid_frontmatter_policy_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "frontmatter_policy"):
            self._lint({"wiki/index.md": self.FRONT}, frontmatter_policy="unknown")

    def test_stray_backtick_cannot_hide_later_links_or_headings(self) -> None:
        report = self._lint({
            "wiki/stray.md": self.FRONT + (
                "Type a ` to start code.\n\n[[dead-after-stray]]\n\n"
                "```\nlet s = `x\n```\n\n[[dead-after-fence]]\n"
            ),
            "wiki/block.md": self.FRONT + (
                "Open ` here\n```\n[[Hidden]] `\n```\n[[dead-after-block]]\n"
            ),
            "wiki/span.md": self.FRONT + "A `code\nspan [[Hidden]]` [[dead-after-span]]\n",
            "wiki/target.md": self.FRONT + "Use `x here.\n\n# Second\n\nmore ` text\n",
            "wiki/headref.md": self.FRONT + "[[target#Second]]\n",
        })
        self.assertEqual(
            {"dead-after-stray", "dead-after-fence", "dead-after-block", "dead-after-span"},
            {entry["target"] for entry in report["dead_links"]},
        )

    def test_indented_lazy_continuation_is_paragraph_text_not_code(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            "Paragraph line\n    still paragraph [[dead-lazy]]\n\n"
            "- Item\n        still item [[dead-list-lazy]]\n\n"
            "> Quote\n    still quote [[dead-quote-lazy]]\n\n"
            "# Heading\n    [[Hidden]]\n\n    [[Hidden]]\n"
        )})
        self.assertEqual(
            {"dead-lazy", "dead-list-lazy", "dead-quote-lazy"},
            {entry["target"] for entry in report["dead_links"]},
        )

    def test_image_nested_in_link_label_checks_both_targets(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            "[![badge](dead-img.png)](dead-href.md)\n"
            "![alt [inner](not-navigation.md)](dead-alt-img.png)\n"
        )})
        self.assertEqual(
            {"dead-img.png", "dead-href.md", "dead-alt-img.png"},
            {entry["target"] for entry in report["dead_links"]},
        )
        self.assertEqual(
            "Badge ![b](i.png) title",
            lint_engine.markdown_visible_text("Badge [![b](i.png)](x.md) title"),
        )

    def test_fences_inside_blockquotes_and_callouts_are_code(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            "> [!note]\n> ~~~\n> [[in-callout-code]]\n> ~~~\n\n"
            "> ```\n> [[in-bq-code]]\n> ````\n> [[dead-after-long-close]]\n\n"
            "> > ```\n> > [[nested-code]]\n> > ```\n\n"
            "> ```\n> [[unclosed-quote-code]]\n\n[[dead-after-quote]]\n"
            ">     [[indented-quote-code]]\n"
        )})
        self.assertEqual(
            {"dead-after-long-close", "dead-after-quote"},
            {entry["target"] for entry in report["dead_links"]},
        )

    def test_obsidian_heading_link_normalization_matches_stripped_characters(self) -> None:
        report = self._lint({
            "wiki/heads.md": self.FRONT + (
                "# Step 1: Install\n\nx\n\n## Q&A | Notes\n\ny\n\n# :\n\nz\n"
            ),
            "wiki/user.md": self.FRONT + (
                "[[heads#Step 1 Install]] [[heads#Step 1: Install]]\n"
                "[[heads#Q&A Notes]] [x](heads.md#Step%201%20Install)\n"
                "[[heads#:]] [[heads#Step 2 Install]]\n"
            ),
        })
        self.assertEqual(
            [("heads#Step 2 Install", "heading-not-found")],
            [(entry["target"], entry["reason"]) for entry in report["dead_links"]],
        )

    def test_wikilink_targets_are_literal_but_markdown_destinations_decode(self) -> None:
        report = self._lint({
            "wiki/a%20b.md": self.FRONT + "Literal percent name.\n",
            "wiki/c d.md": self.FRONT + "Space name.\n",
            "wiki/user.md": self.FRONT + (
                "[[a%20b]] [[c%20d]] [[c d]]\n[m](c%20d.md) [n](a%2520b.md)\n"
            ),
        })
        self.assertEqual(
            [("c%20d", "target-not-found")],
            [(entry["target"], entry["reason"]) for entry in report["dead_links"]],
        )

    @unittest.skipUnless(lint_engine._supports_hidden_checks(), "confined stat unavailable")
    def test_hidden_leaf_file_is_classified_without_reading_payload(self) -> None:
        payload = b"Hidden leaf secret payload.\n"
        original_read = transaction_module.os.read
        payload_read = False

        def tracked_read(descriptor: int, size: int) -> bytes:
            nonlocal payload_read
            block = original_read(descriptor, size)
            payload_read = payload_read or payload in block
            return block

        with mock.patch.object(transaction_module.os, "read", tracked_read):
            report = self._lint({
                "wiki/.draft.md": payload.decode("utf-8"),
                "wiki/user.md": self.FRONT + "[[wiki/.draft]] [[.draft]] [[.absent]]\n",
            })
        self.assertFalse(payload_read)
        self.assertEqual([".absent"], [entry["target"] for entry in report["dead_links"]])
        self.assertEqual(
            [("wiki/.draft.md", "hidden-target-exists-not-indexed")] * 2,
            [(entry["resolved_path"], entry["reason"]) for entry in report["hidden_target_links"]],
        )
        with mock.patch.object(lint_engine, "_supports_hidden_checks", return_value=False):
            unverified = self._lint({"wiki/user.md": self.FRONT + "[[.draft]]\n"})
        self.assertEqual([], unverified["dead_links"])
        self.assertEqual(["hidden-target-status-unverified"], [
            entry["reason"] for entry in unverified["hidden_target_links"]
        ])

    def test_lazy_container_text_is_not_a_setext_heading(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            "[[#Heading?]]\n[[#Quoted?]]\n[[#Real]]\n\n"
            "- item\nHeading?\n---\n\n> quote\nQuoted?\n---\n\nReal\n---\n\nContent.\n"
        )})
        self.assertEqual(
            {"#Heading?", "#Quoted?"}, {entry["target"] for entry in report["dead_links"]}
        )

    def test_setext_heading_follows_container_lines_without_open_paragraph(self) -> None:
        # Each container line leaves no paragraph open, so the next line can
        # start a paragraph that a Setext underline turns into a heading.
        for body, title in (
            ("> quote\n>\nTitle\n=====", "Title"), (">\nAlpha\n---", "Alpha"),
            ("> # Delta\nAlpha\n===", "Alpha"), ("> ---\nAlpha\n---", "Alpha"),
            ("- # Delta\nAlpha\n===", "Alpha"), ("* <b>\nAlpha\n---", "Alpha"),
            (">1.\nh\n=", "h"), ("> <div>\nAlpha\n---", "Alpha"),
            (">     code\nAlpha\n---", "Alpha"), ("-     code\nAlpha\n---", "Alpha"),
        ):
            with self.subTest(body=body):
                report = self._lint({"wiki/index.md": self.FRONT + (
                    f"[[#{title}]]\n\n{body}\n\nContent.\n"
                )})
                self.assertEqual([], report["dead_links"])
        for body in ("> `code`\nAlpha\n---", "> ===\nAlpha\n---", "> a\n- b\nAlpha\n---"):
            with self.subTest(body=body):
                report = self._lint({"wiki/index.md": self.FRONT + (
                    f"[[#Alpha]]\n\n{body}\n\nContent.\n"
                )})
                self.assertEqual(["#Alpha"], [entry["target"] for entry in report["dead_links"]])

    def test_hash_followed_by_inline_code_is_paragraph_text(self) -> None:
        report = self._lint({
            "wiki/a.md": self.FRONT + "#`include` pulls in a header.\n\n[[#include pulls in a header]]\n",
            "wiki/b.md": self.FRONT + "#`include` pulls\n===\n\n[[#include pulls]]\n",
        })
        self.assertEqual(["#include pulls in a header"], [entry["target"] for entry in report["dead_links"]])
        self.assertEqual([], report["read_errors"])

    def test_inline_code_with_unicode_line_separators_keeps_headings_aligned(self) -> None:
        separators = "\x0b\x0c\x1c\x1d\x1e\x85  "
        report = self._lint({"wiki/index.md": self.FRONT + (
            f"Code `a{separators}b` here.\n\n# Real\n\nText.\n\n[[#Real]] [[#Missing]]\n"
        )})
        self.assertEqual(["#Missing"], [entry["target"] for entry in report["dead_links"]])

    def test_random_markdown_never_raises_in_scanners(self) -> None:
        import random

        from claude_obsidian import markdown_links

        alphabet = list("[]()!`~$%<>-=#*_\\|^: \t\na1") + [
            "\r\n", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", " ", " ",
            "[[", "]]", "```", "> ", "- ", "    ", "<!--", "-->", "%%", "$$", "<div>",
            "# ", "\n# ", "\n===\n", "\n---\n", "\n- ", "\n> ",
        ]
        generator = random.Random(20261018)
        for _ in range(1500):
            text = "".join(generator.choice(alphabet) for _ in range(generator.randint(1, 80)))
            with self.subTest(text=text):
                masked = markdown_links.mask_protected_regions(text)
                self.assertEqual(len(text), len(masked))
                markdown_links.markdown_visible_text(text)
                heading_masked = lint_engine._mask_heading_html(text, 0)
                labels = lint_engine._mask_heading_html(text, 0, preserve_inline_code=True)
                for _, _, _, heading in lint_engine._headings(heading_masked, labels):
                    lint_engine._normalize_heading(heading)
                lint_engine._parse_links(lint_engine._Page(
                    "wiki/p.md", Path("p.md"), text, masked,
                    lint_engine._parse_frontmatter(text), frozenset(), (), (),
                    frozenset(), True,
                ))

    def test_tab_indented_hash_is_not_an_atx_heading(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            "[[#h3]]\n\npara\n\t# h3\n\nContent.\n"
        )})
        self.assertEqual(["#h3"], [entry["target"] for entry in report["dead_links"]])

    def test_lazy_line_keeps_quote_paragraph_open(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            "> Quote starts\nlazy line\n>     [[dead-t1]] continues\n\n"
            "> - item\nlazy\n>       [[dead-t2]]\n\n"
            ">     [[Hidden]]\n"
        )})
        self.assertEqual(
            {"dead-t1", "dead-t2"}, {entry["target"] for entry in report["dead_links"]}
        )

    def test_lazy_equals_line_does_not_end_code_span(self) -> None:
        report = self._lint({"wiki/index.md": self.FRONT + (
            ">`\n=\n[[Hidden]]`\n\n- a `b\n=\n[[Hidden]] c`\n\n[[Visible]]\n"
        )})
        self.assertEqual(["Visible"], [entry["target"] for entry in report["dead_links"]])

    def test_provenance_ledger_read_uses_shared_capacity_constant(self) -> None:
        from claude_obsidian.limits import MAX_CANONICAL_LEDGER_BYTES

        self.assertEqual(MAX_CANONICAL_LEDGER_BYTES, lint_engine.MAX_CANONICAL_LEDGER_BYTES)
        with mock.patch.object(lint_engine, "MAX_CANONICAL_LEDGER_BYTES", 8):
            report = self._lint({
                "wiki/index.md": self.FRONT + "Text.\n",
                "wiki/meta/ledgers/source-ledger.json": json.dumps({"sources": {}}),
            })
        self.assertEqual(
            ["cannot read provenance ledger"],
            [entry["message"].split(":")[0] for entry in report["provenance_errors"]],
        )


class ParserScalingTests(unittest.TestCase):
    """Generous wall-clock bounds that only catch superlinear scanner behavior.

    Each input takes well under a second with linear scanning and tens of
    seconds with the quadratic rescans these tests guard against.
    """

    BOUND_SECONDS = 5.0

    def _assert_fast(self, label: str, action) -> None:
        import time

        started = time.perf_counter()
        action()
        elapsed = time.perf_counter() - started
        self.assertLess(elapsed, self.BOUND_SECONDS, f"{label} took {elapsed:.2f}s")

    def test_large_prose_page_lints_quickly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "wiki").mkdir()
            (vault / "wiki/Page.md").write_text(
                "plain line of prose here\n" * 80_000, encoding="utf-8"
            )
            self._assert_fast(
                "2 MB prose", lambda: lint_engine.lint_vault(vault, as_of="2026-10-18")
            )

    def test_adversarial_markdown_scans_are_linear(self) -> None:
        from claude_obsidian import markdown_links

        def page_scan(text: str) -> None:
            masked = markdown_links.mask_protected_regions(text)
            list(markdown_links.iter_markdown_links(masked))
            lint_engine._parse_links(lint_engine._Page(
                "wiki/p.md", Path("p.md"), text, masked,
                lint_engine._parse_frontmatter(text), frozenset(), (), (),
                frozenset(), True,
            ))
            heading_masked = lint_engine._mask_heading_html(text, 0)
            labels = lint_engine._mask_heading_html(text, 0, preserve_inline_code=True)
            for _, _, _, heading in lint_engine._headings(heading_masked, labels):
                lint_engine._normalize_heading(heading)

        mask = markdown_links.mask_protected_regions
        labels = markdown_links._balanced_label_ends
        cases = {
            "unclosed destinations": (page_scan, "[a](" * 20_000 + "\n"),
            "unclosed angled destinations": (page_scan, "[a](<" * 20_000 + "\n"),
            "quoted destinations": (
                page_scan, " '[a](' " * 20_000 + ' "' + "x" * 1000 + "\n"
            ),
            "badge links on one line": (page_scan, "[![b](i.png)](x.md) " * 10_000 + "\n"),
            "unclosed wikilinks": (page_scan, "[[" * 20_000 + "\n"),
            "inline math": (page_scan, "$a " * 20_000 + "\n"),
            "atx trailing space": (page_scan, "# a" + " " * 40_000 + "x\n"),
            "heading closing run": (page_scan, "# a" + " " * 40_000 + "x #\n"),
            "stray backticks": (mask, "a ` b\n" * 200_000),
            "mixed backtick runs": (mask, "a `` b ` c\n" * 120_000),
            "carriage returns": (labels, "line [x]\r" * 400_000),
        }
        for label, (scan, text) in cases.items():
            with self.subTest(label=label):
                self._assert_fast(label, lambda: scan(text))


class WalkScopeTests(unittest.TestCase):
    def test_raw_claude_and_trash_captures_are_not_walked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            concepts = vault / "wiki" / "concepts"
            concepts.mkdir(parents=True)
            (concepts / "Thing.md").write_text(
                "---\ntitle: Thing\ntype: concept\nstatus: draft\ncreated: "
                "2026-07-01\nupdated: 2026-07-01\ntags: []\n---\n\nThe thing.\n",
                encoding="utf-8",
            )
            (vault / "wiki" / "Note.md").write_text(
                "---\ntitle: Note\ntype: note\nstatus: draft\ncreated: "
                "2026-07-01\nupdated: 2026-07-01\ntags: []\n---\n\n"
                "See [[Thing]].\n",
                encoding="utf-8",
            )
            for hidden in (
                vault / ".raw" / "captures",
                vault / ".claude" / "worktrees" / "example" / "wiki" / "concepts",
                vault / ".trash",
            ):
                hidden.mkdir(parents=True)
                (hidden / "Thing.md").write_text(
                    "---\ntitle: Thing\ntype: concept\nstatus: draft\ncreated: "
                    "2026-07-01\nupdated: 2026-07-01\ntags: []\n---\n\n"
                    "A duplicated capture.\n",
                    encoding="utf-8",
                )
            report = lint_engine.lint_vault(vault)
        self.assertEqual([], report["ambiguous_targets"])
        self.assertEqual([], report["dead_links"])
        self.assertEqual(2, report["summary"]["pages_scanned"])

    def test_exclude_param_and_vault_config_scope_out_pages_and_orphans(self) -> None:
        def build_vault(directory: Path) -> Path:
            vault = directory / "vault"
            scratchpad = vault / "wiki" / "scratchpad"
            scratchpad.mkdir(parents=True)
            (scratchpad / "Draft.md").write_text("Unfinished draft.\n", encoding="utf-8")
            (vault / "wiki" / "index.md").write_text(
                "---\ntitle: Index\ntype: index\nstatus: draft\ncreated: "
                "2026-07-01\nupdated: 2026-07-01\ntags: []\n---\n\nIndex.\n",
                encoding="utf-8",
            )
            return vault

        draft_path = "wiki/scratchpad/Draft.md"

        with tempfile.TemporaryDirectory() as directory:
            vault = build_vault(Path(directory))
            report = lint_engine.lint_vault(vault)
        self.assertIn(draft_path, {item["path"] for item in report["orphans"]})
        self.assertEqual(0, report["summary"]["excluded_paths"])

        with tempfile.TemporaryDirectory() as directory:
            vault = build_vault(Path(directory))
            report = lint_engine.lint_vault(vault, exclude=["wiki/scratchpad/*"])
        self.assertNotIn(draft_path, {item["path"] for item in report["orphans"]})
        self.assertNotIn(
            draft_path, {item["path"] for item in report["missing_frontmatter"]}
        )
        self.assertEqual(1, report["summary"]["excluded_paths"])

        with tempfile.TemporaryDirectory() as directory:
            vault = build_vault(Path(directory))
            meta = vault / ".vault-meta"
            meta.mkdir(parents=True, exist_ok=True)
            (meta / "lint.json").write_text(
                json.dumps({"exclude": ["wiki/scratchpad/*"]}), encoding="utf-8"
            )
            report = lint_engine.lint_vault(vault)
        self.assertNotIn(draft_path, {item["path"] for item in report["orphans"]})
        self.assertNotIn(
            draft_path, {item["path"] for item in report["missing_frontmatter"]}
        )
        self.assertEqual(1, report["summary"]["excluded_paths"])

    def test_cli_exclude_flag_matches_engine_parameter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            scratchpad = vault / "wiki" / "scratchpad"
            scratchpad.mkdir(parents=True)
            (scratchpad / "Draft.md").write_text("Unfinished draft.\n", encoding="utf-8")
            (vault / "wiki" / "index.md").write_text(
                "---\ntitle: Index\ntype: index\nstatus: draft\ncreated: "
                "2026-07-01\nupdated: 2026-07-01\ntags: []\n---\n\nIndex.\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "claude-obsidian.py"),
                    "lint",
                    "--vault",
                    str(vault),
                    "--format",
                    "json",
                    "--exclude",
                    "wiki/scratchpad/*",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        self.assertEqual(0, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertNotIn(
            "wiki/scratchpad/Draft.md", {item["path"] for item in report["orphans"]}
        )


class WikiEntrypointResolutionTests(unittest.TestCase):
    FRONT = (
        "---\ntitle: Page\ntype: concept\nstatus: active\n"
        "created: 2026-10-18\nupdated: 2026-10-18\ntags: []\n---\n"
    )

    def test_parent_targets_resolve_without_expanding_report_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            wiki = vault / "wiki"
            (vault / "assets").mkdir(parents=True)
            (vault / "assets/plot.png").write_bytes(b"plot")
            (vault / "Reference.md").write_text("# Known heading\n", encoding="utf-8")
            (vault / "Dashboard.base").write_text(
                "views:\n  - name: Wiki pages\n", encoding="utf-8"
            )
            wiki.mkdir()
            _mark_vault(vault)
            (wiki / "Page.md").write_text(
                self.FRONT
                + "![plot](../assets/plot.png)\n"
                + "[reference](../Reference.md#Known%20heading)\n"
                + "![[../Dashboard.base#Wiki pages]]\n",
                encoding="utf-8",
            )

            via_vault = lint_engine.lint_vault(vault, as_of="2026-10-18")
            via_wiki = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertEqual([], via_vault["dead_links"])
        self.assertEqual([], via_wiki["dead_links"])
        self.assertEqual(1, via_wiki["summary"]["pages_scanned"])
        self.assertEqual(1, via_wiki["summary"]["markdown_files_discovered"])
        self.assertEqual(1, via_wiki["summary"]["link_targets_indexed"])
        self.assertEqual("complete", via_wiki["scope"]["coverage"])
        self.assertEqual([], via_wiki["missing_frontmatter"])
        self.assertEqual([{"path": "Page.md"}], via_wiki["orphans"])

    def test_non_vault_parent_is_not_a_resolution_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory) / "projects"
            wiki = parent / "wiki"
            wiki.mkdir(parents=True)
            (parent / "other-project").mkdir()
            sibling_payload = b"# Private Heading\n"
            (parent / "other-project/secret.md").write_bytes(sibling_payload)
            (parent / "plot.png").write_bytes(b"plot")
            (parent / ".cache").mkdir()
            (parent / ".cache/state.txt").write_bytes(b"state")
            (wiki / "Page.md").write_text(
                self.FRONT + "[[secret#Private Heading]]\n![plot](../plot.png)\n"
                "[state](../.cache/state.txt)\n",
                encoding="utf-8",
            )
            original_read = transaction_module.os.read
            sibling_read = False

            def tracked_read(descriptor: int, size: int) -> bytes:
                nonlocal sibling_read
                block = original_read(descriptor, size)
                sibling_read = sibling_read or sibling_payload in block
                return block

            with mock.patch.object(transaction_module.os, "read", tracked_read):
                outside = lint_engine.lint_vault(wiki, as_of="2026-10-18")
            self.assertFalse(sibling_read)
            _mark_vault(parent)
            inside = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertEqual(
            [("../.cache/state.txt", "target-not-found"), ("../plot.png", "target-not-found"),
             ("secret#Private Heading", "target-not-found")],
            sorted((entry["target"], entry["reason"]) for entry in outside["dead_links"]),
        )
        self.assertEqual([], outside["hidden_target_links"])
        self.assertEqual([], inside["dead_links"])
        if lint_engine._supports_hidden_checks():
            self.assertEqual([".cache/state.txt"], [
                entry["resolved_path"] for entry in inside["hidden_target_links"]
            ])
        for report in (outside, inside):
            self.assertEqual(1, report["summary"]["pages_scanned"])
            self.assertEqual(1, report["summary"]["link_targets_indexed"])
            self.assertEqual(".", report["scope"]["page_root"])

    def test_confined_markdown_read_preserves_bom_and_newline_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            wiki = vault / "wiki"
            wiki.mkdir(parents=True)
            _mark_vault(vault)
            page = wiki / "Page.md"
            logical = self.FRONT + "# Heading\n\n[[Missing target]]\n"
            page.write_text(logical, encoding="utf-8")
            lf_report = lint_engine.lint_vault(wiki, as_of="2026-10-18")

            mixed_newlines = "".join(
                line + ("\r\n" if index % 2 == 0 else "\r")
                for index, line in enumerate(logical.splitlines())
            )
            page.write_bytes(b"\xef\xbb\xbf" + mixed_newlines.encode("utf-8"))
            mixed_report = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertEqual(lf_report, mixed_report)

    def test_wiki_relative_exclude_does_not_hide_parent_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            wiki = vault / "wiki"
            (vault / "assets").mkdir(parents=True)
            wiki.mkdir()
            _mark_vault(vault)
            (vault / "assets/plot.png").write_bytes(b"plot")
            (wiki / "Page.md").write_text(
                self.FRONT + "![plot](../assets/plot.png)\n", encoding="utf-8"
            )
            report = lint_engine.lint_vault(
                wiki, as_of="2026-10-18", exclude=["assets/*"]
            )

        self.assertEqual([], report["dead_links"])
        self.assertEqual(0, report["summary"]["excluded_paths"])

    def test_source_relative_target_wins_before_parent_vault_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            wiki = vault / "wiki"
            wiki.mkdir(parents=True)
            _mark_vault(vault)
            (wiki / "Reference.md").write_text(
                self.FRONT + "# Local heading\n", encoding="utf-8"
            )
            (vault / "Reference.md").write_text("# Parent heading\n", encoding="utf-8")
            (wiki / "Page.md").write_text(
                self.FRONT
                + "[local](Reference.md#Local%20heading)\n"
                + "[parent](../Reference.md#Parent%20heading)\n",
                encoding="utf-8",
            )
            report = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertEqual([], report["dead_links"])
        self.assertEqual([], report["ambiguous_targets"])

    def test_parent_gitignore_filters_ambiguity_by_canonical_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            wiki = vault / "wiki"
            (vault / "build").mkdir(parents=True)
            (vault / "docs").mkdir()
            wiki.mkdir()
            _mark_vault(vault)
            (vault / ".gitignore").write_text("/build/\n", encoding="utf-8")
            (vault / "build/Thing").write_text("artifact\n", encoding="utf-8")
            (vault / "docs/Thing.md").write_text("# Thing\n", encoding="utf-8")
            (wiki / "Page.md").write_text(self.FRONT + "[[Thing]]\n", encoding="utf-8")
            report = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertEqual([], report["dead_links"])
        self.assertEqual([], report["ambiguous_targets"])

    def test_parent_symlinks_and_outside_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            vault = base / "vault"
            wiki = vault / "wiki"
            outside = base / "outside"
            wiki.mkdir(parents=True)
            _mark_vault(vault)
            outside.mkdir()
            (outside / "plot.png").write_bytes(b"plot")
            (outside / "Reference.md").write_text("# Outside\n", encoding="utf-8")
            try:
                (vault / "assets").symlink_to(outside, target_is_directory=True)
                (vault / "Reference.md").symlink_to(outside / "Reference.md")
            except OSError:
                self.skipTest("symlinks unavailable")
            (wiki / "Page.md").write_text(
                self.FRONT
                + "![ancestor](../assets/plot.png)\n"
                + "[file](../Reference.md#Outside)\n"
                + "[escape](../../outside/Reference.md#Outside)\n",
                encoding="utf-8",
            )
            report = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertEqual(3, len(report["dead_links"]))
        self.assertEqual(
            ["../../outside/Reference.md#Outside", "../Reference.md#Outside", "../assets/plot.png"],
            sorted(item["target"] for item in report["dead_links"]),
        )

    def test_parent_junction_surrogate_is_not_traversed_or_read(self) -> None:
        self._assert_parent_junction_surrogate_is_not_traversed_or_read()

    def test_parent_junction_surrogate_with_aliased_temporary_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            actual = base / "actual"
            alias = base / "alias"
            actual.mkdir()
            try:
                alias.symlink_to(actual, target_is_directory=True)
            except OSError:
                self.skipTest("symlinks unavailable")
            original_temporary_directory = tempfile.TemporaryDirectory

            def aliased_temporary_directory(*args: object, **kwargs: object):
                kwargs["dir"] = alias
                return original_temporary_directory(*args, **kwargs)

            with mock.patch.object(
                tempfile, "TemporaryDirectory", aliased_temporary_directory
            ):
                self._assert_parent_junction_surrogate_is_not_traversed_or_read()

    def _assert_parent_junction_surrogate_is_not_traversed_or_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory).resolve() / "vault"
            wiki = vault / "wiki"
            junction = vault / "junction"
            wiki.mkdir(parents=True)
            _mark_vault(vault)
            junction.mkdir()
            target = junction / "Reference.md"
            target_payload = b"# Junction secret heading\n"
            target.write_bytes(target_payload)
            (wiki / "Page.md").write_text(
                self.FRONT + "[outside](../junction/Reference.md#Outside)\n",
                encoding="utf-8",
            )
            original_lstat = Path.lstat
            original_read_text = Path.read_text
            original_read = transaction_module.os.read
            surrogate_observed = False
            target_payload_read = False

            def junction_lstat(path: Path):
                nonlocal surrogate_observed
                metadata = original_lstat(path)
                if path == junction:
                    surrogate_observed = True
                    return mock.Mock(
                        st_mode=metadata.st_mode,
                        st_reparse_tag=0xA0000003,
                    )
                return metadata

            def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
                if path == target:
                    raise AssertionError("junction target must not be read")
                return original_read_text(path, *args, **kwargs)

            def tracked_read(descriptor: int, size: int) -> bytes:
                # Confined vault reads use descriptors, not Path.read_text.
                nonlocal target_payload_read
                block = original_read(descriptor, size)
                target_payload_read = target_payload_read or target_payload in block
                return block

            with (
                mock.patch.object(Path, "lstat", junction_lstat),
                mock.patch.object(Path, "read_text", guarded_read_text),
                mock.patch.object(transaction_module.os, "read", tracked_read),
            ):
                report = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertTrue(surrogate_observed)
        self.assertFalse(target_payload_read)
        self.assertEqual(1, len(report["dead_links"]))
        self.assertEqual("target-not-found", report["dead_links"][0]["reason"])

    def test_scanned_markdown_file_swap_is_rejected_at_confined_open(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            vault = base / "vault"
            wiki = vault / "wiki"
            wiki.mkdir(parents=True)
            _mark_vault(vault)
            page = wiki / "Page.md"
            outside = base / "outside.md"
            page.write_text(self.FRONT + "# Safe\n", encoding="utf-8")
            outside_payload = (self.FRONT + "# Outside secret\n").encode("utf-8")
            outside.write_bytes(outside_payload)
            original_open_parent = transaction_module._open_parent_directory
            original_read = transaction_module.os.read
            original_read_text = Path.read_text
            swap_exercised = False
            outside_payload_read = False

            def perform_swap() -> None:
                nonlocal swap_exercised
                swap_exercised = True
                page.unlink()
                page.symlink_to(outside)

            def swap_parent_open(*args: object, **kwargs: object) -> tuple[int, str]:
                descriptor, leaf = original_open_parent(*args, **kwargs)
                relative = args[1] if len(args) > 1 else kwargs.get("relative")
                if relative == "wiki/Page.md" and not swap_exercised:
                    perform_swap()
                return descriptor, leaf

            def legacy_swap_read_text(
                path: Path, *args: object, **kwargs: object
            ) -> str:
                nonlocal outside_payload_read
                if path == page and not swap_exercised:
                    perform_swap()
                text = original_read_text(path, *args, **kwargs)
                outside_payload_read = outside_payload_read or "Outside secret" in text
                return text

            def tracked_read(descriptor: int, size: int) -> bytes:
                nonlocal outside_payload_read
                block = original_read(descriptor, size)
                outside_payload_read = outside_payload_read or outside_payload in block
                return block

            with (
                mock.patch.object(
                    transaction_module, "_open_parent_directory", swap_parent_open
                ),
                mock.patch.object(transaction_module.os, "read", tracked_read),
                mock.patch.object(Path, "read_text", legacy_swap_read_text),
            ):
                report = lint_engine.lint_vault(wiki, as_of="2026-10-18")
            page_is_symlink = page.is_symlink()

        self.assertTrue(swap_exercised)
        self.assertTrue(page_is_symlink)
        self.assertFalse(outside_payload_read)
        self.assertEqual(1, len(report["read_errors"]))
        self.assertEqual("Page.md", report["read_errors"][0]["path"])
        self.assertEqual(0, report["summary"]["pages_scanned"])

    def test_parent_markdown_file_swap_is_a_controlled_fragment_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            vault = base / "vault"
            wiki = vault / "wiki"
            wiki.mkdir(parents=True)
            _mark_vault(vault)
            parent = vault / "Reference.md"
            outside = base / "outside.md"
            parent.write_text("# Safe\n", encoding="utf-8")
            outside_payload = b"# Outside secret heading\n"
            outside.write_bytes(outside_payload)
            (wiki / "Page.md").write_text(
                self.FRONT + "[probe](../Reference.md#Outside%20secret%20heading)\n",
                encoding="utf-8",
            )
            original_open_parent = transaction_module._open_parent_directory
            original_read = transaction_module.os.read
            swap_exercised = False
            outside_payload_read = False

            def swap_parent_open(*args: object, **kwargs: object) -> tuple[int, str]:
                nonlocal swap_exercised
                descriptor, leaf = original_open_parent(*args, **kwargs)
                relative = args[1] if len(args) > 1 else kwargs.get("relative")
                if relative == "Reference.md" and not swap_exercised:
                    swap_exercised = True
                    parent.unlink()
                    parent.symlink_to(outside)
                return descriptor, leaf

            def tracked_read(descriptor: int, size: int) -> bytes:
                nonlocal outside_payload_read
                block = original_read(descriptor, size)
                outside_payload_read = outside_payload_read or outside_payload in block
                return block

            with (
                mock.patch.object(
                    transaction_module, "_open_parent_directory", swap_parent_open
                ),
                mock.patch.object(transaction_module.os, "read", tracked_read),
            ):
                report = lint_engine.lint_vault(wiki, as_of="2026-10-18")
            parent_is_symlink = parent.is_symlink()

        self.assertTrue(swap_exercised)
        self.assertTrue(parent_is_symlink)
        self.assertFalse(outside_payload_read)
        self.assertEqual([], report["read_errors"])
        self.assertEqual(1, len(report["dead_links"]))
        self.assertEqual(
            "fragment-on-non-markdown-target", report["dead_links"][0]["reason"]
        )

    def test_parent_markdown_ancestor_swap_cannot_supply_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            vault = base / "vault"
            wiki = vault / "wiki"
            parent_directory = vault / "docs"
            outside_directory = base / "outside"
            wiki.mkdir(parents=True)
            _mark_vault(vault)
            parent_directory.mkdir()
            outside_directory.mkdir()
            parent = parent_directory / "Reference.md"
            safe_directory = vault / "docs-safe"
            parent.write_text("# Safe\n", encoding="utf-8")
            outside_payload = b"# Outside secret heading\n"
            (outside_directory / "Reference.md").write_bytes(outside_payload)
            (wiki / "Page.md").write_text(
                self.FRONT + "[probe](../docs/Reference.md#Outside%20secret%20heading)\n",
                encoding="utf-8",
            )
            original_open_parent = transaction_module._open_parent_directory
            original_read = transaction_module.os.read
            original_read_text = Path.read_text
            swap_exercised = False
            outside_payload_read = False

            def perform_swap() -> None:
                nonlocal swap_exercised
                swap_exercised = True
                parent_directory.rename(safe_directory)
                parent_directory.symlink_to(outside_directory, target_is_directory=True)

            def swap_parent_open(*args: object, **kwargs: object) -> tuple[int, str]:
                descriptor, leaf = original_open_parent(*args, **kwargs)
                relative = args[1] if len(args) > 1 else kwargs.get("relative")
                if relative == "docs/Reference.md" and not swap_exercised:
                    perform_swap()
                return descriptor, leaf

            def legacy_swap_read_text(
                path: Path, *args: object, **kwargs: object
            ) -> str:
                nonlocal outside_payload_read
                if path == parent and not swap_exercised:
                    perform_swap()
                text = original_read_text(path, *args, **kwargs)
                outside_payload_read = outside_payload_read or "Outside secret heading" in text
                return text

            def tracked_read(descriptor: int, size: int) -> bytes:
                nonlocal outside_payload_read
                block = original_read(descriptor, size)
                outside_payload_read = outside_payload_read or outside_payload in block
                return block

            with (
                mock.patch.object(
                    transaction_module, "_open_parent_directory", swap_parent_open
                ),
                mock.patch.object(transaction_module.os, "read", tracked_read),
                mock.patch.object(Path, "read_text", legacy_swap_read_text),
            ):
                report = lint_engine.lint_vault(wiki, as_of="2026-10-18")
            parent_is_symlink = parent_directory.is_symlink()

        self.assertTrue(swap_exercised)
        self.assertTrue(parent_is_symlink)
        self.assertFalse(outside_payload_read)
        self.assertEqual(1, len(report["dead_links"]))

    def test_parent_hidden_target_keeps_hidden_classification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            wiki = vault / "wiki"
            (vault / ".raw").mkdir(parents=True)
            wiki.mkdir()
            _mark_vault(vault)
            (vault / ".raw/source.txt").write_text("source\n", encoding="utf-8")
            (wiki / "Page.md").write_text(
                self.FRONT + "[source](../.raw/source.txt)\n", encoding="utf-8"
            )
            report = lint_engine.lint_vault(wiki, as_of="2026-10-18")

        self.assertEqual([], report["dead_links"])
        self.assertEqual(1, len(report["hidden_target_links"]))
        self.assertEqual(
            "hidden-target-exists-not-indexed",
            report["hidden_target_links"][0]["reason"],
        )
        self.assertEqual(".raw/source.txt", report["hidden_target_links"][0]["resolved_path"])

    def test_vault_root_exclusions_still_remove_resolution_targets(self) -> None:
        def lint_with_config(config: dict[str, object] | None = None, **options: object) -> dict:
            with tempfile.TemporaryDirectory() as directory:
                vault = Path(directory) / "vault"
                (vault / "wiki/scratchpad").mkdir(parents=True)
                (vault / "wiki/Page.md").write_text(
                    self.FRONT + "[[Draft]]\n", encoding="utf-8"
                )
                (vault / "wiki/scratchpad/Draft.md").write_text(
                    self.FRONT + "Draft.\n", encoding="utf-8"
                )
                if config is not None:
                    (vault / ".vault-meta").mkdir()
                    (vault / ".vault-meta/lint.json").write_text(
                        json.dumps(config), encoding="utf-8"
                    )
                return lint_engine.lint_vault(vault, as_of="2026-10-18", **options)

        direct = lint_with_config(exclude=["wiki/scratchpad/*"])
        configured = lint_with_config({"exclude": ["wiki/scratchpad/*"]})
        for report in (direct, configured):
            self.assertEqual(1, len(report["dead_links"]))
            self.assertEqual(1, report["summary"]["excluded_paths"])
            self.assertEqual(1, report["summary"]["markdown_files_excluded"])


class GitignoreDisambiguationTests(unittest.TestCase):
    """Gitignored files must not shadow pages into ambiguity findings."""

    def _lint(self, files: dict[str, str]) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "vault"
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            return lint_engine.lint_vault(root)

    def test_gitignored_shadow_candidate_is_dropped(self) -> None:
        report = self._lint(
            {
                ".gitignore": "/bin/\n",
                "bin/Thing": "binary artifact\n",
                "wiki/concepts/Thing.md": "# Thing\n",
                "wiki/Note.md": "[[Thing]]\n",
            }
        )
        self.assertEqual([], report["ambiguous_targets"])
        self.assertEqual([], report["dead_links"])

    def test_same_shadow_without_gitignore_stays_ambiguous(self) -> None:
        report = self._lint(
            {
                "bin/Thing": "binary artifact\n",
                "wiki/concepts/Thing.md": "# Thing\n",
                "wiki/Note.md": "[[Thing]]\n",
            }
        )
        self.assertEqual(1, len(report["ambiguous_targets"]))
        self.assertEqual(
            ["bin/Thing", "wiki/concepts/Thing.md"],
            report["ambiguous_targets"][0]["candidates"],
        )

    def test_ambiguity_between_only_ignored_candidates_is_still_reported(self) -> None:
        report = self._lint(
            {
                ".gitignore": "out/\n",
                "out/a/Thing": "one\n",
                "out/b/Thing": "two\n",
                "wiki/Note.md": "[[Thing]]\n",
            }
        )
        self.assertEqual(1, len(report["ambiguous_targets"]))
        self.assertEqual(
            ["out/a/Thing", "out/b/Thing"],
            report["ambiguous_targets"][0]["candidates"],
        )

    def test_link_whose_only_candidate_is_ignored_still_resolves(self) -> None:
        report = self._lint(
            {
                ".gitignore": "/bin/\n",
                "bin/OnlyIgnored": "artifact\n",
                "wiki/Note.md": "[[OnlyIgnored]]\n",
            }
        )
        self.assertEqual([], report["ambiguous_targets"])
        self.assertEqual([], report["dead_links"])

    def test_index_shadow_no_longer_reports_stale_entry(self) -> None:
        report = self._lint(
            {
                ".gitignore": "artifacts/\n",
                "artifacts/Thing": "binary\n",
                "wiki/concepts/Thing.md": "# Thing\n",
                "wiki/index.md": "[[Thing]]\n",
            }
        )
        self.assertEqual([], report["ambiguous_targets"])
        self.assertEqual([], report["stale_index_entries"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
