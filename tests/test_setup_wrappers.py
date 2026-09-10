#!/usr/bin/env python3
"""Hermetic smoke tests for the thin transactional setup wrappers."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODE = ROOT / "scripts/setup-mode.sh"
DRAGONSCALE = ROOT / "scripts/setup-dragonscale.sh"
SETUP_VAULT = ROOT / "scripts/setup-vault.sh"


class SetupWrapperTests(unittest.TestCase):
    def vault(self, parent: Path) -> Path:
        vault = parent / "vault"
        (vault / ".obsidian").mkdir(parents=True)
        (vault / "wiki").mkdir()
        (vault / ".raw").mkdir()
        return vault

    def invoke(
        self, script: Path, vault: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(script), *arguments],
            cwd=vault,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def fake_core_invocation(
        self, parent: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        fake_bin = parent / "fake-bin"
        fake_bin.mkdir(exist_ok=True)
        fake_python = fake_bin / "python3"
        fake_python.write_text(
            "#!/bin/bash\nprintf '%s\\n' \"$@\"\n",
            encoding="utf-8",
        )
        fake_python.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = f"{fake_bin}{os.pathsep}{environment.get('PATH', '')}"
        return subprocess.run(
            ["bash", str(SETUP_VAULT), *arguments],
            cwd=parent,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_extension_help_documents_the_review_time_pin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.vault(Path(directory))
            for wrapper in (MODE, DRAGONSCALE):
                with self.subTest(wrapper=wrapper.name):
                    result = self.invoke(wrapper, vault, "--help")
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("--generated-at ISO-UTC", result.stdout)
                    self.assertIn("repeat that exact value", result.stdout)
                    self.assertIn("--approved-plan-sha256", result.stdout)

    def test_setup_vault_is_a_non_writing_core_dispatcher(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            missing = base / "new vault"
            preview = self.fake_core_invocation(
                base,
                "--dry-run",
                "--vault",
                str(missing),
                "--generated-at",
                "2026-07-11T12:00:00Z",
                "--operation-id",
                "wrapper-preview",
            )
            self.assertEqual(0, preview.returncode, preview.stderr)
            self.assertEqual("init", preview.stdout.splitlines()[1])
            self.assertFalse(missing.exists())

            existing = base / "existing vault"
            existing.mkdir()
            adopt = self.fake_core_invocation(base, "--vault", str(existing))
            self.assertEqual(0, adopt.returncode, adopt.stderr)
            self.assertEqual("adopt", adopt.stdout.splitlines()[1])

            check = self.fake_core_invocation(base, "--check", "--vault", str(existing))
            self.assertEqual(0, check.returncode, check.stderr)
            self.assertEqual(
                ["doctor", "--vault", str(existing)],
                check.stdout.splitlines()[1:],
            )

            applied = self.fake_core_invocation(
                base,
                "--apply",
                "--init",
                "--approved-plan-sha256",
                "a" * 64,
                "--vault",
                str(missing),
            )
            self.assertEqual(0, applied.returncode, applied.stderr)
            self.assertEqual("init", applied.stdout.splitlines()[1])
            self.assertEqual(
                ["--approved-plan-sha256", "a" * 64, "--apply"],
                applied.stdout.splitlines()[-3:],
            )
            self.assertFalse(missing.exists())

    def test_mode_uses_cwd_vault_without_empty_array_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.vault(Path(directory))
            result = self.invoke(
                MODE,
                vault,
                "--mode",
                "para",
                "--generated-at",
                "2026-07-11T12:00:00Z",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("dry-run", json.loads(result.stdout)["status"])
            self.assertFalse((vault / ".vault-meta").exists())

    def test_dragonscale_default_is_a_read_only_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.vault(Path(directory))
            result = self.invoke(
                DRAGONSCALE,
                vault,
                "--generated-at",
                "2026-07-11T12:00:00Z",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("dry-run", payload["status"])
            self.assertEqual(4, len(payload["plan"]["changed_paths"]))
            self.assertFalse((vault / ".vault-meta").exists())
            self.assertFalse((vault / ".raw/.manifest.json").exists())

    def test_dragonscale_check_reports_actual_extension_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.vault(Path(directory))
            missing = self.invoke(DRAGONSCALE, vault, "--check")
            self.assertEqual(1, missing.returncode, missing.stderr)
            missing_payload = json.loads(missing.stdout)
            self.assertFalse(missing_payload["ready"])
            self.assertEqual(4, len(missing_payload["missing_paths"]))
            self.assertFalse((vault / ".vault-meta").exists())

            common = ("--generated-at", "2026-07-11T12:00:00Z")
            preview = self.invoke(DRAGONSCALE, vault, *common)
            approval = json.loads(preview.stdout)["approved_plan_sha256"]
            applied = self.invoke(
                DRAGONSCALE,
                vault,
                *common,
                "--approved-plan-sha256",
                approval,
                "--apply",
            )
            self.assertEqual(0, applied.returncode, applied.stderr)
            ready = self.invoke(DRAGONSCALE, vault, "--check")
            self.assertEqual(0, ready.returncode, ready.stderr)
            self.assertTrue(json.loads(ready.stdout)["ready"])

    def test_mode_apply_forwards_exact_review_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = self.vault(Path(directory))
            common = (
                "--mode",
                "para",
                "--generated-at",
                "2026-07-11T12:00:00Z",
            )
            preview = self.invoke(MODE, vault, *common)
            self.assertEqual(0, preview.returncode, preview.stderr)
            approval = json.loads(preview.stdout)["approved_plan_sha256"]
            applied = self.invoke(
                MODE,
                vault,
                *common,
                "--approved-plan-sha256",
                approval,
                "--apply",
            )
            self.assertEqual(0, applied.returncode, applied.stderr)
            mode = json.loads(
                (vault / ".vault-meta/mode.json").read_text(encoding="utf-8")
            )
            self.assertEqual("para", mode["mode"])


if __name__ == "__main__":
    unittest.main()
