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
import unittest
from datetime import date, datetime
from pathlib import Path


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


def _snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def _canonical_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class LintEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = lint_engine.lint_vault(FIXTURE)

    def test_report_schema_and_all_required_categories(self) -> None:
        self.assertEqual(1, self.report["version"])
        self.assertEqual("1.1.1", self.report["engine_version"])
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
