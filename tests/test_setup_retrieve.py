#!/usr/bin/env python3
"""Hermetic tests for the vault-scoped retrieval bootstrap."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/setup-retrieve.sh"


class SetupRetrieveTests(unittest.TestCase):
    def make_vault(self, parent: Path) -> Path:
        vault = parent / "vault with ünicode"
        page = vault / "wiki/concepts/example.md"
        page.parent.mkdir(parents=True)
        (vault / ".raw").mkdir()
        page.write_text(
            "---\ntype: concept\ntitle: Example\ncreated: 2026-07-11\nupdated: 2026-07-11\naddress: c-000001\n---\n\n# Example\n\nLocal retrieval content.\n",
            encoding="utf-8",
        )
        return vault

    def invoke(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPT), *arguments],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=20,
        )

    def test_default_preview_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.make_vault(Path(directory))
            result = self.invoke("--vault", str(vault), "--no-llm")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Dry run only", result.stdout)
            self.assertFalse((vault / ".vault-meta").exists())

    def test_offline_apply_builds_only_selected_vault(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.make_vault(Path(directory))
            result = self.invoke("--vault", str(vault), "--no-llm", "--apply")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((vault / ".vault-meta/bm25/index.json").is_file())
            self.assertFalse((ROOT / ".vault-meta/bm25/index.json").exists())

    def test_product_root_is_rejected_even_when_explicit(self) -> None:
        metadata_existed = (ROOT / ".vault-meta").exists()
        result = self.invoke("--vault", str(ROOT), "--no-llm")
        self.assertEqual(2, result.returncode)
        self.assertRegex(
            result.stderr,
            r"(PLUGIN_ROOT_IS_NOT_VAULT|VAULT_SENTINEL_MISSING)",
        )
        self.assertEqual(metadata_existed, (ROOT / ".vault-meta").exists())

    def test_egress_flags_are_mutually_exclusive(self) -> None:
        result = self.invoke("--no-llm", "--allow-egress")
        self.assertEqual(2, result.returncode)


if __name__ == "__main__":
    unittest.main()
