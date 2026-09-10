#!/usr/bin/env python3
"""Hermetic tests for the non-destructive vault initializer."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin" / "setup-vault.sh"
FIXTURES = ROOT / "tests" / "fixtures" / "setup"
_OPERATION_COUNTER = itertools.count(1)
_GENERATED_AT = "2026-07-11T12:00:00Z"


def _run(*arguments: str, cwd: Path | None = None, env: dict[str, str] | None = None):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["bash", str(SCRIPT), *arguments],
        cwd=cwd or ROOT,
        env=merged,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def _reviewed_apply(
    *arguments: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
):
    pinned = list(arguments)
    if "--generated-at" not in pinned:
        pinned.extend(("--generated-at", _GENERATED_AT))
    if "--operation-id" not in pinned:
        pinned.extend(("--operation-id", f"setup-wrapper-{next(_OPERATION_COUNTER)}"))
    preview_arguments = tuple(argument for argument in pinned if argument != "--apply")
    preview = _run("--dry-run", *preview_arguments, cwd=cwd, env=env)
    if preview.returncode != 0:
        raise AssertionError(f"setup preview failed: {preview.stderr}")
    payload = json.loads(preview.stdout)
    approval = payload.get("approved_plan_sha256")
    if not approval:
        raise AssertionError(
            f"setup preview emitted no approval hash: {preview.stdout}"
        )
    return _run(
        *pinned,
        "--approved-plan-sha256",
        approval,
        cwd=cwd,
        env=env,
    )


def _snapshot(root: Path) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    if not root.exists():
        return snapshot
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[relative] = ("directory", "")
        elif path.is_file():
            snapshot[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        elif path.is_symlink():
            snapshot[relative] = ("symlink", os.readlink(path))
    return snapshot


class SetupVaultTests(unittest.TestCase):
    def test_default_and_explicit_dry_run_are_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            vault = parent / "My Vault ü"
            result = _run("--vault", str(vault))
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(
                "claude-obsidian.initialization-plan.v1", payload["schema"]
            )
            self.assertEqual("dry-run", payload["status"])
            self.assertFalse(vault.exists())

            # With no path, the caller's working directory is the vault. The
            # existing directory itself must still remain byte-for-byte intact.
            marker = parent / "marker.txt"
            marker.write_text("untouched", encoding="utf-8")
            before = _snapshot(parent)
            result = _run("--dry-run", cwd=parent, env={"PWD": str(parent)})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                "claude-obsidian.adoption-plan.v1", json.loads(result.stdout)["schema"]
            )
            self.assertEqual(before, _snapshot(parent))

    def test_check_is_read_only_and_has_meaningful_exit_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "not-created"
            result = _run("--check", "--vault", str(vault))
            self.assertEqual(2, result.returncode)
            self.assertIn("VAULT_MISSING", result.stderr)
            self.assertFalse(vault.exists())

            applied = _reviewed_apply("--apply", "--init", "--vault", str(vault))
            self.assertEqual(0, applied.returncode, applied.stderr)
            before = _snapshot(vault)
            result = _run("--check", "--vault", str(vault))
            self.assertEqual(0, result.returncode, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual("claude-obsidian.doctor.v1", report["schema"])
            self.assertTrue(report["ok"])
            self.assertEqual(before, _snapshot(vault))

    def test_init_sets_absolute_new_link_format(self) -> None:
        # Obsidian's "New link format" setting defaults to "shortest path
        # when possible" when unset. Every other link-touching part of the
        # product (worksync-style resync scripts, the terminology linker,
        # lint's dead/ambiguous-link detection) resolves wikilinks by exact
        # vault-relative path with no fuzzy or duplicate-basename resolution,
        # so a link Obsidian's own UI inserts under the default setting can
        # resolve fine inside Obsidian while being unresolvable — or silently
        # wrong once a second file shares a basename — to every other tool
        # in the pipeline. The scaffolded vault must pin the setting to
        # "absolute" so links created through Obsidian's own UI are already
        # in the form the rest of the product expects.
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            result = _reviewed_apply("--apply", "--init", "--vault", str(vault))
            self.assertEqual(0, result.returncode, result.stderr)
            app_json = json.loads(
                (vault / ".obsidian" / "app.json").read_text(encoding="utf-8")
            )
            self.assertEqual("absolute", app_json.get("newLinkFormat"))

    def test_apply_supports_legacy_positional_unicode_path_and_is_idempotent(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "Vault with spaces Ω"
            result = _reviewed_apply("--apply", "--init", str(vault))
            self.assertEqual(0, result.returncode, result.stderr)
            for relative in (
                ".obsidian/snippets",
                ".raw",
                "inbox",
                "wiki/meta/ledgers",
            ):
                self.assertTrue((vault / relative).is_dir(), relative)
            for name in ("graph.json", "app.json", "appearance.json"):
                path = vault / ".obsidian" / name
                self.assertTrue(path.is_file())
                self.assertIsInstance(
                    json.loads(path.read_text(encoding="utf-8")), dict
                )

            first = _snapshot(vault)
            result = _run(
                "--dry-run",
                "--adopt",
                "--generated-at",
                _GENERATED_AT,
                "--operation-id",
                "setup-wrapper-noop",
                str(vault),
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("noop", json.loads(result.stdout)["status"])
            self.assertEqual(first, _snapshot(vault))

    def test_existing_obsidian_json_is_preserved_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            obsidian = vault / ".obsidian"
            obsidian.mkdir(parents=True)
            custom = json.loads(
                (FIXTURES / "custom-app.json").read_text(encoding="utf-8")
            )
            for name in ("graph.json", "app.json", "appearance.json"):
                content = json.dumps({**custom, "managed_file": name}, indent=2).encode(
                    "utf-8"
                )
                (obsidian / name).write_bytes(content)
            before = {
                name: (obsidian / name).read_bytes()
                for name in ("graph.json", "app.json", "appearance.json")
            }

            result = _reviewed_apply("--apply", "--adopt", "--vault", str(vault))
            self.assertEqual(0, result.returncode, result.stderr)
            changed = set(json.loads(result.stdout)["changed_paths"])
            for name, content in before.items():
                self.assertEqual(content, (obsidian / name).read_bytes())
                self.assertNotIn(f".obsidian/{name}", changed)

    def test_force_is_previewed_and_applied_by_the_transactional_core(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            initial = _reviewed_apply("--apply", "--init", "--vault", str(vault))
            self.assertEqual(0, initial.returncode, initial.stderr)
            obsidian = vault / ".obsidian"
            custom = json.loads(
                (FIXTURES / "custom-app.json").read_text(encoding="utf-8")
            )
            originals: dict[str, bytes] = {}
            for name in ("graph.json", "app.json", "appearance.json"):
                content = json.dumps({**custom, "managed_file": name}, indent=2).encode(
                    "utf-8"
                )
                (obsidian / name).write_bytes(content)
                originals[name] = content

            result = _reviewed_apply(
                "--apply", "--force", "--adopt", "--vault", str(vault)
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("complete", payload["status"])
            for name, content in originals.items():
                self.assertNotEqual(content, (obsidian / name).read_bytes())
                json.loads((obsidian / name).read_text(encoding="utf-8"))
                self.assertIn(f".obsidian/{name}", payload["changed_paths"])

    def test_unverified_optional_download_is_skipped_with_actionable_guidance(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            vault = base / "vault"
            plugin = vault / ".obsidian" / "plugins" / "obsidian-excalidraw-plugin"
            plugin.mkdir(parents=True)
            shutil.copyfile(
                FIXTURES / "excalidraw-manifest.json", plugin / "manifest.json"
            )

            fake_bin = base / "fake bin"
            fake_bin.mkdir()
            marker = base / "curl-was-called"
            curl = fake_bin / "curl"
            curl.write_text(
                '#!/usr/bin/env bash\nprintf called > "$CURL_MARKER"\nexit 99\n',
                encoding="utf-8",
            )
            curl.chmod(curl.stat().st_mode | stat.S_IXUSR)
            env = {
                "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
                "CURL_MARKER": str(marker),
            }
            result = _reviewed_apply(
                "--apply", "--adopt", "--vault", str(vault), env=env
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse(marker.exists())
            self.assertFalse((plugin / "main.js").exists())

    def test_conflicting_modes_and_unsafe_managed_paths_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            result = _run("--check", "--apply", "--vault", str(base / "vault"))
            self.assertEqual(2, result.returncode)
            self.assertIn("choose exactly one", result.stderr)

            missing_approval = _run(
                "--apply",
                "--init",
                "--generated-at",
                _GENERATED_AT,
                "--operation-id",
                "missing-approval",
                "--vault",
                str(base / "missing-approval"),
            )
            self.assertEqual(2, missing_approval.returncode)
            self.assertIn(
                "--apply requires --approved-plan-sha256", missing_approval.stderr
            )

            vault = base / "unsafe"
            vault.mkdir()
            (vault / ".obsidian").write_text("not a directory", encoding="utf-8")
            result = _run("--adopt", "--vault", str(vault))
            self.assertEqual(2, result.returncode)
            self.assertIn("UNSAFE_VAULT_PATH", result.stderr)
            self.assertEqual(
                "not a directory", (vault / ".obsidian").read_text(encoding="utf-8")
            )
            self.assertFalse((vault / "wiki").exists())

    def test_product_root_is_never_a_setup_destination(self) -> None:
        metadata_existed = (ROOT / ".vault-meta").exists()
        result = _run("--check", "--vault", str(ROOT))
        self.assertEqual(2, result.returncode)
        self.assertRegex(
            result.stderr,
            r"(PLUGIN_ROOT_IS_NOT_VAULT|VAULT_SENTINEL_MISSING)",
        )
        self.assertEqual(metadata_existed, (ROOT / ".vault-meta").exists())

        descendant = _run("--check", "--vault", str(ROOT / "templates" / "vault"))
        self.assertEqual(2, descendant.returncode)
        self.assertIn("PLUGIN_TREE_IS_NOT_VAULT", descendant.stderr)

    def test_explicit_init_and_adopt_override_automatic_selection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            existing = base / "existing"
            existing.mkdir()
            automatic = _run("--dry-run", "--vault", str(existing))
            explicit = _run("--dry-run", "--init", "--vault", str(existing))
            self.assertEqual(
                "claude-obsidian.adoption-plan.v1",
                json.loads(automatic.stdout)["schema"],
            )
            self.assertEqual(
                "claude-obsidian.initialization-plan.v1",
                json.loads(explicit.stdout)["schema"],
            )

    def test_apply_refuses_state_changed_after_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            (vault / ".obsidian").mkdir(parents=True)
            common = (
                "--adopt",
                "--generated-at",
                _GENERATED_AT,
                "--operation-id",
                "state-changed-after-review",
                "--vault",
                str(vault),
            )
            preview = _run("--dry-run", *common)
            approval = json.loads(preview.stdout)["approved_plan_sha256"]
            marker_file = vault / "wiki/index.md"
            marker_file.parent.mkdir()
            marker_file.write_text("user-created\n", encoding="utf-8")
            applied = _run(
                "--apply",
                *common,
                "--approved-plan-sha256",
                approval,
            )
            self.assertEqual(2, applied.returncode)
            self.assertIn("PLAN_CHANGED", applied.stderr)
            self.assertEqual("user-created\n", marker_file.read_text(encoding="utf-8"))
            self.assertFalse((vault / ".claude-obsidian.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
