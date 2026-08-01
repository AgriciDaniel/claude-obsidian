#!/usr/bin/env python3
"""Hermetic tests for the safe multi-host skill-link installer."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin/setup-multi-agent.sh"


class SetupMultiAgentTests(unittest.TestCase):
    def invoke(self, home: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment["HOME"] = str(home)
        return subprocess.run(
            ["bash", str(SCRIPT), *arguments],
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_default_is_no_write_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            result = self.invoke(home)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Dry run only", result.stdout)
            self.assertFalse((home / ".codex").exists())

    def test_apply_is_idempotent_for_global_hosts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            first = self.invoke(home, "--apply")
            self.assertEqual(0, first.returncode, first.stderr)
            roots = {
                "codex": home / ".agents/skills",
                "opencode": home / ".config/opencode/skills",
                "gemini": home / ".gemini/skills",
            }
            expected = sorted(
                path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")
            )
            self.assertEqual(15, len(expected))
            for host, skill_root in roots.items():
                discovered = sorted(
                    path.parent.name for path in skill_root.glob("*/SKILL.md")
                )
                self.assertEqual(expected, discovered, host)
                for skill_name in expected:
                    link = skill_root / skill_name
                    self.assertTrue(link.is_symlink(), (host, skill_name))
                    self.assertEqual(ROOT / "skills" / skill_name, link.resolve())
            self.assertFalse((home / ".opencode").exists())
            second = self.invoke(home, "--apply")
            self.assertEqual(0, second.returncode, second.stderr)
            self.assertEqual(45, second.stdout.count("READY"))

    def test_conflict_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            conflict = home / ".agents/skills/wiki"
            conflict.mkdir(parents=True)
            marker = conflict / "mine"
            marker.write_text("preserve", encoding="utf-8")
            result = self.invoke(home, "--apply", "--host", "codex")
            self.assertEqual(2, result.returncode)
            self.assertEqual("preserve", marker.read_text(encoding="utf-8"))
            self.assertTrue((home / ".agents/skills/save/SKILL.md").is_file())

    def test_zcode_host_installs_global_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            first = self.invoke(home, "--apply", "--host", "zcode")
            self.assertEqual(0, first.returncode, first.stderr)
            skill_root = home / ".zcode/skills"
            expected = sorted(
                path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")
            )
            self.assertEqual(15, len(expected))
            discovered = sorted(
                path.parent.name for path in skill_root.glob("*/SKILL.md")
            )
            self.assertEqual(expected, discovered)
            for skill_name in expected:
                link = skill_root / skill_name
                self.assertTrue(link.is_symlink(), skill_name)
                self.assertEqual(ROOT / "skills" / skill_name, link.resolve())
            # ZCode is opt-in: the default hosts are not installed alongside it.
            self.assertFalse((home / ".agents/skills").exists())
            second = self.invoke(home, "--apply", "--host", "zcode")
            self.assertEqual(0, second.returncode, second.stderr)
            self.assertEqual(15, second.stdout.count("READY"))

    def test_zcode_host_conflict_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            conflict = home / ".zcode/skills/wiki"
            conflict.mkdir(parents=True)
            marker = conflict / "mine"
            marker.write_text("preserve", encoding="utf-8")
            result = self.invoke(home, "--apply", "--host", "zcode")
            self.assertEqual(2, result.returncode)
            self.assertEqual("preserve", marker.read_text(encoding="utf-8"))
            self.assertTrue((home / ".zcode/skills/save/SKILL.md").is_file())

    def test_workspace_hosts_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            missing = self.invoke(base, "--host", "cursor")
            self.assertEqual(2, missing.returncode)
            workspace = base / "workspace"
            workspace.mkdir()
            applied = self.invoke(
                base,
                "--apply",
                "--host",
                "cursor",
                "--host",
                "windsurf",
                "--workspace",
                str(workspace),
            )
            self.assertEqual(0, applied.returncode, applied.stderr)
            for host in ("cursor", "windsurf"):
                skill_root = workspace / f".{host}/skills"
                self.assertEqual(
                    15,
                    len(list(skill_root.glob("*/SKILL.md"))),
                    host,
                )
                self.assertTrue((skill_root / "wiki").is_symlink())

    def test_workspace_parent_symlinks_cannot_redirect_apply(self) -> None:
        for symlink_component in (".cursor", ".cursor/skills"):
            with (
                self.subTest(component=symlink_component),
                tempfile.TemporaryDirectory() as directory,
            ):
                base = Path(directory)
                workspace = base / "workspace"
                outside = base / "outside"
                workspace.mkdir()
                outside.mkdir()
                link = workspace / symlink_component
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(outside, target_is_directory=True)
                preview = self.invoke(
                    base,
                    "--dry-run",
                    "--host",
                    "cursor",
                    "--workspace",
                    str(workspace),
                )
                self.assertEqual(2, preview.returncode)
                self.assertIn("parent is a symlink", preview.stderr)
                result = self.invoke(
                    base,
                    "--apply",
                    "--host",
                    "cursor",
                    "--workspace",
                    str(workspace),
                )
                self.assertEqual(2, result.returncode)
                self.assertIn("parent is a symlink", result.stderr)
                self.assertEqual([], list(outside.iterdir()))


if __name__ == "__main__":
    unittest.main()
