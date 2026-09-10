#!/usr/bin/env python3
"""Acceptance tests for the read-only installed-product boundary."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_LAUNCHERS = tuple(sorted((ROOT / "scripts").glob("*.py")))
SETUP_SCRIPT_NAMES = frozenset(
    {
        "setup-dragonscale.sh",
        "setup-mode.sh",
        "setup-multi-agent.sh",
        "setup-retrieve.sh",
        "setup-vault.sh",
    }
)
SHELL_LAUNCHERS = tuple(
    sorted(
        path
        for path in (ROOT / "scripts").glob("*.sh")
        if path.name in SETUP_SCRIPT_NAMES
        or "python3" in path.read_text(encoding="utf-8")
    )
)
PRODUCT_DIRS = (
    ".claude-plugin",
    "agents",
    "claude_obsidian",
    "config",
    "hooks",
    "scripts",
    "skills",
    "templates",
)


def copy_product(destination: Path) -> None:
    for relative in PRODUCT_DIRS:
        source = ROOT / relative
        if source.is_dir():
            shutil.copytree(
                source,
                destination / relative,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )


def fingerprint(root: Path) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", "")
        elif path.is_file():
            result[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        else:
            result[relative] = ("other", "")
    return result


class InstalledTreeBoundaryTests(unittest.TestCase):
    def test_make_test_disables_bytecode_for_imported_test_modules(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("export PYTHONDONTWRITEBYTECODE := 1", makefile)

    def test_every_python_launcher_disables_bytecode_before_local_imports(self) -> None:
        self.assertTrue(PYTHON_LAUNCHERS)
        for launcher in PYTHON_LAUNCHERS:
            with self.subTest(launcher=launcher.name):
                source = launcher.read_text(encoding="utf-8")
                guard = source.find("sys.dont_write_bytecode = True")
                self.assertGreaterEqual(guard, 0)
                local_imports = [
                    position
                    for marker in (
                        "from claude_obsidian",
                        "import claude_obsidian",
                        "spec.loader.exec_module",
                    )
                    if (position := source.find(marker)) >= 0
                ]
                self.assertTrue(
                    local_imports, f"no local import surface found in {launcher}"
                )
                self.assertLess(guard, min(local_imports))

    def test_shell_launchers_export_the_bytecode_policy(self) -> None:
        self.assertTrue(SHELL_LAUNCHERS)
        for launcher in SHELL_LAUNCHERS:
            with self.subTest(launcher=launcher.relative_to(ROOT).as_posix()):
                source = launcher.read_text(encoding="utf-8")
                export = source.find("export PYTHONDONTWRITEBYTECODE=1")
                first_python = source.find("python3")
                self.assertGreaterEqual(export, 0)
                if first_python >= 0:
                    self.assertLess(export, first_python)

    def test_normal_installed_commands_leave_the_product_tree_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            installed = temporary / "installed product"
            installed.mkdir()
            copy_product(installed)

            vault = temporary / "user vault"
            (vault / "wiki").mkdir(parents=True)
            (vault / ".raw").mkdir()
            (vault / "wiki" / "Page.md").write_text(
                "---\ntitle: Page\naddress: c-000001\n---\n\nA page about durable memory.\n",
                encoding="utf-8",
            )

            home = temporary / "home"
            home.mkdir()
            environment = os.environ.copy()
            environment.pop("PYTHONDONTWRITEBYTECODE", None)
            environment.pop("PYTHONPYCACHEPREFIX", None)
            environment.pop("PYTHONPATH", None)
            environment["HOME"] = str(home)
            environment["CLAUDE_PLUGIN_ROOT"] = str(installed)
            environment["CLAUDE_OBSIDIAN_VAULT"] = str(vault)

            before = fingerprint(installed)

            commands: list[tuple[list[str], set[int]]] = []
            for launcher in sorted((installed / "scripts").glob("*.py")):
                commands.append(([sys.executable, str(launcher), "--help"], {0}))
            commands.extend(
                (
                    (
                        [
                            "bash",
                            str(installed / "scripts/setup-dragonscale.sh"),
                            "--vault",
                            str(vault),
                            "--check",
                        ],
                        {0, 1},
                    ),
                    (
                        [
                            "bash",
                            str(installed / "scripts/setup-mode.sh"),
                            "--vault",
                            str(vault),
                            "--check",
                        ],
                        {0},
                    ),
                    (
                        [
                            "bash",
                            str(installed / "scripts/setup-multi-agent.sh"),
                            "--dry-run",
                            "--host",
                            "codex",
                        ],
                        {0},
                    ),
                    (
                        [
                            "bash",
                            str(installed / "scripts/setup-retrieve.sh"),
                            "--vault",
                            str(vault),
                            "--check",
                        ],
                        {0},
                    ),
                    (
                        [
                            "bash",
                            str(installed / "scripts/setup-vault.sh"),
                            "--vault",
                            str(vault),
                            "--check",
                        ],
                        {0, 1},
                    ),
                    (
                        [
                            "bash",
                            str(installed / "scripts/allocate-address.sh"),
                            "--vault",
                            str(vault),
                            "--peek",
                        ],
                        {0},
                    ),
                    (
                        [
                            "bash",
                            str(installed / "scripts/detect-transport.sh"),
                            "--vault",
                            str(vault),
                            "--peek",
                            "--quiet",
                        ],
                        {0},
                    ),
                    (
                        [
                            "bash",
                            str(installed / "scripts/wiki-lock.sh"),
                            "peek",
                            "wiki/Page.md",
                        ],
                        {0},
                    ),
                    (
                        [
                            sys.executable,
                            str(installed / "scripts/claude-obsidian.py"),
                            "hook",
                            "stop",
                        ],
                        {0},
                    ),
                    (
                        [
                            sys.executable,
                            str(installed / "scripts/contextual-prefix.py"),
                            "--vault",
                            str(vault),
                            "--all",
                            "--no-llm",
                        ],
                        {0},
                    ),
                    (
                        [
                            sys.executable,
                            str(installed / "scripts/bm25-index.py"),
                            "--vault",
                            str(vault),
                            "build",
                        ],
                        {0},
                    ),
                    (
                        [
                            sys.executable,
                            str(installed / "scripts/retrieve.py"),
                            "--vault",
                            str(vault),
                            "durable memory",
                            "--top",
                            "1",
                            "--no-rerank",
                        ],
                        {0},
                    ),
                )
            )

            for command, accepted in commands:
                with self.subTest(command=command):
                    completed = subprocess.run(
                        command,
                        cwd=installed,
                        env=environment,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                        timeout=20,
                    )
                    self.assertIn(
                        completed.returncode,
                        accepted,
                        f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
                    )

            after = fingerprint(installed)
            self.assertEqual(before, after)
            self.assertFalse(
                any(
                    path.name == "__pycache__"
                    for path in installed.rglob("__pycache__")
                )
            )
            self.assertFalse(any(installed.rglob("*.py[co]")))


if __name__ == "__main__":
    unittest.main()
