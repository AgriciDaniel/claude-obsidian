#!/usr/bin/env python3
"""Hermetic adversarial tests for deterministic public artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import claude_obsidian.release as release_module
from claude_obsidian.release import (
    _load_config,
    _selected,
    audit_artifact,
    build_public_artifact,
)


EPOCH = 1_700_000_000
FIXTURE = ROOT / "tests" / "fixtures" / "release" / "public" / "README.md"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _configure_fixture_git(repository: Path, *, name: str, email: str) -> None:
    no_hooks = repository / ".git" / "no-hooks"
    no_hooks.mkdir()
    for key, value in (
        ("core.hooksPath", ".git/no-hooks"),
        ("commit.gpgsign", "false"),
        ("user.email", email),
        ("user.name", name),
    ):
        subprocess.run(
            ["git", "-C", str(repository), "config", key, value],
            check=True,
            timeout=10,
        )


def _codes(report: dict) -> set[str]:
    return {item["code"] for item in report["errors"]}


class CanonicalReleasePolicyTests(unittest.TestCase):
    def test_distribution_excludes_tests_for_excluded_historical_helpers(self) -> None:
        config, errors = _load_config(ROOT)
        self.assertEqual([], errors)
        assert config is not None
        for name in ("scripts/baseline-v16.py", "scripts/benchmark-runner.py", "tests/test_benchmark_tools.py"):
            self.assertFalse(_selected(name, config), name)
        self.assertTrue(_selected("tests/test_retrieval_eval.py", config))

    def test_public_policy_never_selects_root_contributor_vault_state(self) -> None:
        config, errors = _load_config(ROOT)
        self.assertEqual([], errors)
        self.assertIsNotNone(config)
        assert config is not None
        selectors = [
            *config["include_files"],
            *config["include_globs"],
            *config["include_roots"],
        ]
        forbidden = (".obsidian", ".raw", ".vault-meta", "wiki")
        self.assertEqual(
            [],
            sorted(
                selector
                for selector in selectors
                if any(
                    selector == root or selector.startswith(root + "/")
                    for root in forbidden
                )
            ),
        )
        self.assertEqual(
            {".claude-plugin/marketplace.json": "config/public-marketplace.json"},
            config["archive_overlays"],
        )


class ReleaseRepo(unittest.TestCase):
    def setUp(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is required")
        self._temporary = tempfile.TemporaryDirectory()
        self.home = Path(self._temporary.name)
        self.repo = self.home / "repo"
        self.repo.mkdir()
        self.output = self.home / "artifact.zip"
        (self.repo / "README.md").write_bytes(FIXTURE.read_bytes())
        (self.repo / "ATTRIBUTION.md").write_text(
            "Approved private mirror disclosure: https://github.com/"
            "AI-Marketing-Hub/claude-obsidian\n",
            encoding="utf-8",
        )
        (self.repo / "src").mkdir()
        tool = self.repo / "src" / "tool.py"
        tool.write_text("print('safe')\n", encoding="utf-8")
        tool.chmod(0o755)
        (self.repo / "docs" / "private").mkdir(parents=True)
        (self.repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        (self.repo / "docs" / "private" / "notes.md").write_text(
            "excluded\n", encoding="utf-8"
        )
        self.config = {
            "approved_private_url_disclosures": ["ATTRIBUTION.md"],
            "archive_format": "zip",
            "compression": "stored",
            "exclude_globs": ["docs/private/**"],
            "include_files": ["ATTRIBUTION.md", "README.md"],
            "include_globs": ["docs/*.md"],
            "include_roots": ["config", "src"],
            "limits": {
                "max_archive_bytes": 10_000_000,
                "max_compression_ratio": 20,
                "max_file_bytes": 1_000_000,
                "max_files": 100,
                "max_total_bytes": 5_000_000,
            },
            "reviewed_binaries": {},
            "schema_version": 1,
        }
        _write_json(self.repo / "config" / "release-allowlist.json", self.config)
        self.git("init", "-q")
        _configure_fixture_git(
            self.repo,
            name="Release Tests",
            email="release-tests@example.invalid",
        )
        self.commit("fixture")

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(self.repo), *arguments],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return completed.stdout

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def write_config(self) -> None:
        _write_json(self.repo / "config" / "release-allowlist.json", self.config)

    def build(self, output: Path | None = None) -> dict:
        return build_public_artifact(self.repo, output or self.output, EPOCH)


class BuildTests(ReleaseRepo):
    def test_release_authority_json_rejects_duplicate_keys(self) -> None:
        raw = json.dumps(self.config, sort_keys=True)
        duplicate = raw[:-1] + ', "include_roots": ["docs"]}'
        (self.repo / "config/release-allowlist.json").write_text(
            duplicate,
            encoding="utf-8",
        )
        self.commit("duplicate release authority")

        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("invalid_config", _codes(report))
        self.assertFalse(self.output.exists())

    def test_release_authority_json_rejects_nonfinite_numbers(self) -> None:
        for number in ("NaN", "1e999"):
            with self.subTest(number=number):
                raw = json.dumps(self.config, sort_keys=True)
                nonfinite = raw.replace(
                    '"schema_version": 1', f'"schema_version": {number}'
                )
                (self.repo / "config/release-allowlist.json").write_text(
                    nonfinite,
                    encoding="utf-8",
                )
                self.commit(f"non-finite release authority {number}")
                report = self.build()
                self.assertFalse(report["ok"])
                self.assertIn("invalid_config", _codes(report))

    def test_release_authority_rejects_unknown_keys(self) -> None:
        cases = (("unknown_top", 1), ("limits", {"max_fiels": 1}))
        for field, value in cases:
            with self.subTest(field=field):
                document = dict(self.config)
                if field == "limits":
                    document["limits"] = {**self.config["limits"], **value}
                else:
                    document[field] = value
                _write_json(self.repo / "config/release-allowlist.json", document)
                self.commit(f"unknown release authority {field}")
                report = self.build()
                self.assertFalse(report["ok"])
                self.assertIn("invalid_config", _codes(report))

    def test_portable_unicode_path_collision_is_rejected_before_build(self) -> None:
        first = self.repo / "docs" / "Ś.md"
        second = self.repo / "docs" / "ſ́.md"
        first.write_text("one\n", encoding="utf-8")
        second.write_text("two\n", encoding="utf-8")
        if first.samefile(second):
            self.skipTest(
                "filesystem normalizes the two Unicode collision fixtures "
                "to one directory entry"
            )
        self.commit("portable collision")

        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("duplicate_entry", _codes(report))
        self.assertFalse(self.output.exists())

    def test_two_builds_are_byte_identical_and_self_auditing(self) -> None:
        first_path = self.home / "first.zip"
        second_path = self.home / "second.zip"
        first = self.build(first_path)
        second = self.build(second_path)
        self.assertTrue(first["ok"], first)
        self.assertTrue(second["ok"], second)
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first_path.read_bytes(), second_path.read_bytes())

        audit = audit_artifact(first_path)
        self.assertTrue(audit["ok"], audit)
        with zipfile.ZipFile(first_path) as archive:
            names = archive.namelist()
            self.assertEqual(sorted(names), names)
            self.assertIn("RELEASE_MANIFEST.json", names)
            self.assertIn("SHA256SUMS", names)
            self.assertIn("docs/guide.md", names)
            self.assertNotIn("docs/private/notes.md", names)
            manifest = json.loads(archive.read("RELEASE_MANIFEST.json"))
            self.assertEqual(EPOCH, manifest["source_date_epoch"])
            modes = {
                info.filename: info.external_attr >> 16 for info in archive.infolist()
            }
            self.assertEqual(stat.S_IFREG | 0o755, modes["src/tool.py"])
            self.assertEqual(stat.S_IFREG | 0o644, modes["README.md"])
            self.assertEqual(stat.S_IFREG | 0o644, modes["RELEASE_MANIFEST.json"])
            manifest_modes = {item["path"]: item["mode"] for item in manifest["files"]}
            self.assertEqual("0755", manifest_modes["src/tool.py"])
            self.assertEqual("0644", manifest_modes["README.md"])
            self.assertEqual(
                sorted(item["path"] for item in manifest["files"]),
                [item["path"] for item in manifest["files"]],
            )

    def test_public_marketplace_is_injected_only_into_the_audited_artifact(
        self,
    ) -> None:
        plugin = {"name": "sample-plugin", "version": "1.0.0"}
        marketplace = {
            "plugins": [{"name": "sample-plugin", "source": "./"}],
            "version": "1.0.0",
        }
        required = {
            ".claude-plugin/plugin.json": json.dumps(plugin).encode(),
            ".codex-plugin/plugin.json": json.dumps({**plugin, "hooks": "./hooks/codex.json"}).encode(),
            "claude_obsidian/__init__.py": b"\n",
            "config/capabilities.json": b"{}\n",
            "config/public-marketplace.json": json.dumps(marketplace).encode(),
            "hooks/hooks.json": b'{"hooks":{}}\n',
            "hooks/codex.json": b'{"hooks":{}}\n',
            "scripts/claude-obsidian.py": b"#!/usr/bin/env python3\n",
            "skills/wiki/SKILL.md": b"---\nname: wiki\ndescription: Wiki.\n---\n",
            "templates/vault/.gitignore": b".vault-meta/\n",
        }
        for relative, data in required.items():
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        self.config["archive_overlays"] = {
            ".claude-plugin/marketplace.json": "config/public-marketplace.json"
        }
        self.config["include_roots"] = sorted(
            set(self.config["include_roots"])
            | {
                ".claude-plugin",
                ".codex-plugin",
                "claude_obsidian",
                "hooks",
                "scripts",
                "skills",
                "templates",
            }
        )
        self.write_config()
        self.commit("artifact-only marketplace")

        self.assertFalse((self.repo / ".claude-plugin/marketplace.json").exists())
        report = self.build()
        self.assertTrue(report["ok"], report)
        with zipfile.ZipFile(self.output) as archive:
            for path in (".codex-plugin/plugin.json", "hooks/codex.json"):
                self.assertEqual(archive.read(path), required[path])
            self.assertEqual(
                archive.read("config/public-marketplace.json"),
                archive.read(".claude-plugin/marketplace.json"),
            )
            manifest = json.loads(archive.read("RELEASE_MANIFEST.json"))
            self.assertEqual(
                {".claude-plugin/marketplace.json": "config/public-marketplace.json"},
                manifest["policy"]["archive_overlays"],
            )

            distribution = self.home / "distribution"
            archive.extractall(distribution)
        subprocess.run(["git", "init", "-q", str(distribution)], check=True, timeout=10)
        _configure_fixture_git(
            distribution,
            name="Distribution Test",
            email="dist@example.invalid",
        )
        subprocess.run(
            ["git", "-C", str(distribution), "add", "-f", "-A"], check=True, timeout=10
        )
        subprocess.run(
            ["git", "-C", str(distribution), "commit", "-q", "-m", "distribution"],
            check=True,
            timeout=10,
        )
        rebuilt = build_public_artifact(
            distribution, self.home / "distribution-rebuilt.zip", EPOCH
        )
        self.assertTrue(rebuilt["ok"], rebuilt)

    def test_dirty_and_untracked_worktrees_are_rejected_without_output(self) -> None:
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        dirty = self.build()
        self.assertFalse(dirty["ok"])
        self.assertIn("dirty_repository", _codes(dirty))
        self.assertFalse(self.output.exists())

        self.git("restore", "README.md")
        (self.repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        untracked = self.build()
        self.assertFalse(untracked["ok"])
        self.assertIn("dirty_repository", _codes(untracked))
        self.assertFalse(self.output.exists())

    def test_tracked_symlink_is_rejected(self) -> None:
        try:
            os.symlink("tool.py", self.repo / "src" / "alias.py")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable")
        self.commit("symlink")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("symlink", _codes(report))

    def test_root_raw_and_live_vault_state_are_hard_rejected(self) -> None:
        (self.repo / ".raw").mkdir()
        (self.repo / ".raw" / "private.md").write_text("private\n", encoding="utf-8")
        self.config["include_roots"] = [".raw", "config", "src"]
        self.write_config()
        self.commit("unsafe raw selector")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("raw_source", _codes(report))

    def test_secret_token_is_rejected(self) -> None:
        token = "ghp_" + "A" * 36
        (self.repo / "src" / "credentials.txt").write_text(
            f"token={token}\n", encoding="utf-8"
        )
        self.commit("seed token")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("secret_material", _codes(report))

    def test_private_repo_url_needs_named_disclosure(self) -> None:
        private_url = "https://github.com/" + "AI-Marketing-Hub/claude-obsidian"
        (self.repo / "docs" / "guide.md").write_text(
            private_url + "\n", encoding="utf-8"
        )
        self.commit("seed private URL")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("private_repository_url", _codes(report))

    def test_absolute_home_path_is_rejected(self) -> None:
        home_path = "/var/" + "home/alice/private-vault"
        (self.repo / "src" / "path.txt").write_text(home_path + "\n", encoding="utf-8")
        self.commit("seed path")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("absolute_home_path", _codes(report))

    def test_personal_email_address_is_rejected(self) -> None:
        personal_email = "alice@" + "gmail.com"
        (self.repo / "docs" / "guide.md").write_text(
            f"Contact {personal_email}\n", encoding="utf-8"
        )
        self.commit("seed personal email")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("personal_email_address", _codes(report))

    def test_quoted_unicode_literal_and_encoded_email_forms_are_rejected(self) -> None:
        quoted = '"alice"' + "@gmail.com"
        internationalized = "алиса" + "@" + "пример.рф"
        encoded = "alice&" + "#64;gmail.com"
        address_literal = "alice@" + "[127.0.0.1]"
        (self.repo / "docs" / "guide.md").write_text(
            "\n".join((quoted, internationalized, encoded, address_literal)) + "\n",
            encoding="utf-8",
        )
        self.commit("seed alternate personal email forms")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("personal_email_address", _codes(report))

    def test_release_safe_email_addresses_are_accepted(self) -> None:
        (self.repo / "docs" / "guide.md").write_text(
            "Fixtures: author@example.com, release-tests@example.invalid\n"
            "Automation: 41898282+github-actions@users.noreply.github.com, "
            "noreply@github.com\n",
            encoding="utf-8",
        )
        self.commit("seed release-safe email addresses")
        report = self.build()
        self.assertTrue(report["ok"], report)

    def test_non_email_at_sign_forms_are_accepted(self) -> None:
        (self.repo / "docs" / "guide.md").write_text(
            "Clone: git@github.com:owner/repository.git\n"
            "Dependency: package@1.2.3\n",
            encoding="utf-8",
        )
        self.commit("seed non-email at-sign forms")
        report = self.build()
        self.assertTrue(report["ok"], report)

    def test_release_safe_domains_require_an_exact_match(self) -> None:
        subdomain = "person@" + "sub.example.com"
        suffix_attack = "person@" + "users.noreply.github.com.evil"
        (self.repo / "docs" / "guide.md").write_text(
            f"{subdomain}\n{suffix_attack}\n", encoding="utf-8"
        )
        self.commit("seed email allowlist lookalikes")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("personal_email_address", _codes(report))

    def test_unreviewed_binary_is_rejected(self) -> None:
        (self.repo / "src" / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00binary")
        self.commit("seed binary")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertIn("unreviewed_binary", _codes(report))

    def test_missing_config_and_non_zip_output_fail_closed(self) -> None:
        self.git("rm", "config/release-allowlist.json")
        self.git("commit", "-q", "-m", "remove config")
        missing = self.build()
        self.assertFalse(missing["ok"])
        self.assertIn("missing_config", _codes(missing))
        wrong_type = build_public_artifact(self.repo, self.home / "artifact.tar", EPOCH)
        self.assertFalse(wrong_type["ok"])
        self.assertIn("unsupported_archive_type", _codes(wrong_type))

    def test_failed_build_does_not_replace_existing_artifact(self) -> None:
        self.output.write_bytes(b"previous artifact")
        (self.repo / "README.md").write_text("dirty\n", encoding="utf-8")
        report = self.build()
        self.assertFalse(report["ok"])
        self.assertEqual(b"previous artifact", self.output.read_bytes())

    def test_collected_bytes_must_match_the_clean_git_blob(self) -> None:
        original_read = release_module._read_source_file

        def substitute_bytes(candidate, before, *, path, limit):
            data, error = original_read(candidate, before, path=path, limit=limit)
            if path == "README.md" and error is None:
                return b"transient bytes not present in HEAD\n", None
            return data, error

        release_module._read_source_file = substitute_bytes
        try:
            report = self.build()
        finally:
            release_module._read_source_file = original_read
        self.assertFalse(report["ok"])
        self.assertIn("source_blob_mismatch", _codes(report))
        self.assertFalse(self.output.exists())

    def test_git_environment_cannot_redirect_release_provenance(self) -> None:
        other = self.home / "other"
        other.mkdir()
        subprocess.run(["git", "-C", str(other), "init", "-q"], check=True)
        _configure_fixture_git(
            other,
            name="Other",
            email="other@example.invalid",
        )
        (other / "foreign.txt").write_text("foreign\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(other), "add", "foreign.txt"], check=True)
        subprocess.run(
            ["git", "-C", str(other), "commit", "-qm", "foreign"], check=True
        )
        expected = self.git("rev-parse", "HEAD").strip()
        foreign = subprocess.run(
            ["git", "-C", str(other), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertNotEqual(expected, foreign)

        names = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
        prior = {name: os.environ.get(name) for name in names}
        os.environ["GIT_DIR"] = str(other / ".git")
        os.environ["GIT_WORK_TREE"] = str(self.repo)
        os.environ["GIT_INDEX_FILE"] = str(other / ".git" / "index")
        try:
            report = self.build()
        finally:
            for name, value in prior.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
        self.assertTrue(report["ok"], report)
        with zipfile.ZipFile(self.output) as archive:
            manifest = json.loads(archive.read("RELEASE_MANIFEST.json"))
        self.assertEqual(expected, manifest["source_commit"])

    def test_build_does_not_refresh_or_mutate_the_real_git_index(self) -> None:
        index = self.repo / ".git" / "index"
        before = index.read_bytes()
        before_metadata = index.stat()
        readme = self.repo / "README.md"
        metadata = readme.stat()
        os.utime(
            readme,
            ns=(metadata.st_atime_ns, metadata.st_mtime_ns + 5_000_000_000),
        )

        previous = os.environ.get("GIT_OPTIONAL_LOCKS")
        os.environ["GIT_OPTIONAL_LOCKS"] = "1"
        try:
            report = self.build()
        finally:
            if previous is None:
                os.environ.pop("GIT_OPTIONAL_LOCKS", None)
            else:
                os.environ["GIT_OPTIONAL_LOCKS"] = previous

        self.assertTrue(report["ok"], report)
        self.assertEqual(before, index.read_bytes())
        after_metadata = index.stat()
        self.assertEqual(before_metadata.st_mtime_ns, after_metadata.st_mtime_ns)
        self.assertEqual(before_metadata.st_ctime_ns, after_metadata.st_ctime_ns)
        self.assertFalse((self.repo / ".git" / "index.lock").exists())
        audited = audit_artifact(self.output)
        self.assertTrue(audited["ok"], audited)
        self.assertEqual(before, index.read_bytes())


class CanonicalPolicyTests(unittest.TestCase):
    def test_release_version_and_date_surfaces_are_coordinated(self) -> None:
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (ROOT / "config" / "public-marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        package_source = (ROOT / "claude_obsidian" / "__init__.py").read_text(
            encoding="utf-8"
        )
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        version = plugin["version"]
        package_match = re.search(r'^__version__ = "([^"]+)"$', package_source, re.M)
        citation_version = re.search(r"^version: ([^\s]+)$", citation, re.M)
        citation_date = re.search(r"^date-released: '([^']+)'$", citation, re.M)
        self.assertIsNotNone(package_match)
        self.assertIsNotNone(citation_version)
        self.assertIsNotNone(citation_date)
        assert package_match is not None
        assert citation_version is not None
        assert citation_date is not None

        self.assertEqual(version, marketplace["version"])
        self.assertEqual(version, package_match.group(1))
        self.assertEqual(version, citation_version.group(1))
        self.assertIn(
            f"## [{version}] - {citation_date.group(1)}",
            changelog,
        )
        self.assertIn(f"release-v{version}-", readme)
        self.assertIn(f'alt="Release v{version}"', readme)

    def test_repository_allowlist_is_canonical_and_valid(self) -> None:
        config, errors = _load_config(ROOT)
        self.assertEqual([], errors)
        self.assertIsNotNone(config)
        self.assertEqual(["ATTRIBUTION.md"], config["approved_private_url_disclosures"])
        reviewed = config["reviewed_binaries"]
        expected_binaries = [
            "assets/cover.png",
            "assets/screenshots/graph-view.png",
            "assets/screenshots/wiki-map-view.png",
            "tests/fixtures/capture/sample.pdf",
        ]
        self.assertEqual(expected_binaries, list(reviewed))
        for path in expected_binaries:
            self.assertEqual(
                hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                reviewed[path],
            )
        self.assertIn("assets", config["include_roots"])
        for path in expected_binaries[:3]:
            self.assertTrue(_selected(path, config))
        self.assertNotIn("_templates", config["include_roots"])
        self.assertFalse((ROOT / "_templates").exists())
        self.assertFalse((ROOT / "docs/install-guide.pdf").exists())
        self.assertFalse(_selected("docs/install-guide.pdf", config))
        self.assertFalse(_selected("docs/releases/v1.6.0.md", config))
        self.assertFalse(_selected("scripts/baseline-v16.py", config))
        self.assertFalse(_selected("scripts/benchmark-runner.py", config))
        self.assertFalse(_selected("claude_obsidian/__pycache__/release.pyc", config))


class AuditTests(ReleaseRepo):
    def _write_zip(
        self, path: Path, entries: list[tuple[zipfile.ZipInfo | str, bytes]]
    ) -> None:
        with zipfile.ZipFile(path, "w", allowZip64=False) as archive:
            for name, data in entries:
                archive.writestr(name, data)

    def test_traversal_entry_is_rejected_without_extraction(self) -> None:
        malicious = self.home / "traversal.zip"
        self._write_zip(malicious, [("../outside.txt", b"owned")])
        report = audit_artifact(malicious)
        self.assertFalse(report["ok"])
        self.assertIn("path_escape", _codes(report))
        self.assertFalse((self.home / "outside.txt").exists())

    def test_archive_symlink_and_special_entry_are_rejected(self) -> None:
        malicious = self.home / "symlink.zip"
        link = zipfile.ZipInfo("link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self._write_zip(malicious, [(link, b"../../outside")])
        report = audit_artifact(malicious)
        self.assertFalse(report["ok"])
        self.assertIn("symlink", _codes(report))

    def test_compressed_bomb_is_rejected_before_expansion(self) -> None:
        malicious = self.home / "bomb.zip"
        with zipfile.ZipFile(
            malicious, "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            archive.writestr("huge.txt", b"0" * 1_000_000)
        report = audit_artifact(malicious)
        self.assertFalse(report["ok"])
        self.assertTrue(
            {"unsupported_compression", "compression_bomb"}.issubset(_codes(report))
        )

    def test_live_state_and_secret_filename_are_rejected(self) -> None:
        malicious = self.home / "state.zip"
        self._write_zip(
            malicious,
            [
                (".raw/private.md", b"private"),
                ("wiki/hot.md", b"session"),
                (".vault-meta/cache.json", b"{}"),
                (".env", b"TOKEN=secret"),
            ],
        )
        report = audit_artifact(malicious)
        self.assertFalse(report["ok"])
        self.assertTrue(
            {"raw_source", "live_vault_state", "secret_file"}.issubset(_codes(report)),
            report,
        )

    def test_archive_with_personal_email_address_is_rejected(self) -> None:
        valid = self.build()
        self.assertTrue(valid["ok"], valid)
        personal_email = "alice@" + "gmail.com"
        with zipfile.ZipFile(self.output, "r") as source:
            records = [(info, source.read(info.filename)) for info in source.infolist()]
        with zipfile.ZipFile(
            self.output, "w", compression=zipfile.ZIP_STORED
        ) as destination:
            for info, data in records:
                if info.filename == "docs/guide.md":
                    data += f"Contact {personal_email}\n".encode()
                destination.writestr(info, data)
        report = audit_artifact(self.output)
        self.assertFalse(report["ok"])
        self.assertIn("personal_email_address", _codes(report))

    def test_tampered_valid_artifact_fails_manifest_and_checksums(self) -> None:
        valid = self.build()
        self.assertTrue(valid["ok"], valid)
        with zipfile.ZipFile(self.output, "r") as source:
            records = [(info, source.read(info.filename)) for info in source.infolist()]
        with zipfile.ZipFile(
            self.output, "w", compression=zipfile.ZIP_STORED
        ) as destination:
            for info, data in records:
                if info.filename == "README.md":
                    data += b"tampered\n"
                destination.writestr(info, data)
        report = audit_artifact(self.output)
        self.assertFalse(report["ok"])
        self.assertTrue(
            {"manifest_mismatch", "checksum_mismatch"}.issubset(_codes(report)), report
        )

    def test_mode_tampering_is_rejected_against_manifest(self) -> None:
        valid = self.build()
        self.assertTrue(valid["ok"], valid)
        with zipfile.ZipFile(self.output, "r") as source:
            records = [(info, source.read(info.filename)) for info in source.infolist()]
        with zipfile.ZipFile(
            self.output, "w", compression=zipfile.ZIP_STORED
        ) as destination:
            for info, data in records:
                if info.filename == "src/tool.py":
                    info.external_attr = (stat.S_IFREG | 0o644) << 16
                destination.writestr(info, data)
        report = audit_artifact(self.output)
        self.assertFalse(report["ok"])
        self.assertIn("permission_mismatch", _codes(report))

    def test_local_header_timestamp_must_match_central_directory(self) -> None:
        valid = self.build()
        self.assertTrue(valid["ok"], valid)
        raw = bytearray(self.output.read_bytes())
        with zipfile.ZipFile(self.output, "r") as archive:
            info = archive.getinfo("README.md")
        local_time, local_date = struct.unpack_from("<HH", raw, info.header_offset + 10)
        struct.pack_into(
            "<HH",
            raw,
            info.header_offset + 10,
            local_time ^ 0x20,
            local_date,
        )
        self.output.write_bytes(raw)

        report = audit_artifact(self.output)
        self.assertFalse(report["ok"])
        self.assertIn("timestamp_mismatch", _codes(report))

    def test_alternate_valid_zip_header_encoding_is_noncanonical(self) -> None:
        valid = self.build()
        self.assertTrue(valid["ok"], valid)
        raw = bytearray(self.output.read_bytes())
        with zipfile.ZipFile(self.output, "r") as archive:
            infos = archive.infolist()
            central_offset = archive.start_dir
        for info in infos:
            flags = struct.unpack_from("<H", raw, info.header_offset + 6)[0]
            struct.pack_into("<H", raw, info.header_offset + 6, flags ^ 0x800)
        cursor = central_offset
        for _info in infos:
            self.assertEqual(b"PK\x01\x02", raw[cursor : cursor + 4])
            flags = struct.unpack_from("<H", raw, cursor + 8)[0]
            struct.pack_into("<H", raw, cursor + 8, flags ^ 0x800)
            name_length, extra_length, comment_length = struct.unpack_from(
                "<HHH", raw, cursor + 28
            )
            cursor += 46 + name_length + extra_length + comment_length
        self.output.write_bytes(raw)
        report = audit_artifact(self.output)
        self.assertFalse(report["ok"])
        self.assertIn("noncanonical_archive", _codes(report))

    def test_audit_snapshot_rejects_artifact_path_replacement(self) -> None:
        valid = self.build()
        self.assertTrue(valid["ok"], valid)
        parked = self.output.with_name("parked.zip")
        original = release_module._preflight_zip_structure
        swapped = False

        def swap_after_snapshot(data: bytes, *, label: str) -> list[dict[str, str]]:
            nonlocal swapped
            if not swapped:
                swapped = True
                self.output.rename(parked)
                self.output.write_bytes(parked.read_bytes())
            return original(data, label=label)

        with mock.patch.object(
            release_module, "_preflight_zip_structure", swap_after_snapshot
        ):
            report = audit_artifact(self.output)
        self.assertTrue(swapped)
        self.assertFalse(report["ok"])
        self.assertIn("artifact_identity_changed", _codes(report))

    def test_unreferenced_bytes_between_records_and_directory_are_rejected(
        self,
    ) -> None:
        valid = self.build()
        self.assertTrue(valid["ok"], valid)
        raw = bytearray(self.output.read_bytes())
        eocd = raw.rfind(b"PK\x05\x06")
        self.assertGreaterEqual(eocd, 0)
        central_offset = struct.unpack_from("<L", raw, eocd + 16)[0]
        hidden = b"HIDDEN-UNREFERENCED-BYTES"
        tampered = raw[:central_offset] + hidden + raw[central_offset:]
        new_eocd = eocd + len(hidden)
        struct.pack_into("<L", tampered, new_eocd + 16, central_offset + len(hidden))
        self.output.write_bytes(tampered)
        report = audit_artifact(self.output)
        self.assertFalse(report["ok"])
        self.assertIn("noncanonical_archive", _codes(report))

    def test_duplicate_case_collision_and_wrong_archive_type_are_rejected(self) -> None:
        collision = self.home / "collision.zip"
        self._write_zip(collision, [("Readme.md", b"one"), ("README.md", b"two")])
        report = audit_artifact(collision)
        self.assertFalse(report["ok"])
        self.assertIn("duplicate_entry", _codes(report))

        unicode_collision = self.home / "unicode-collision.zip"
        self._write_zip(
            unicode_collision,
            [("docs/Ś.md", b"one"), ("docs/ſ́.md", b"two")],
        )
        unicode_report = audit_artifact(unicode_collision)
        self.assertFalse(unicode_report["ok"])
        self.assertIn("duplicate_entry", _codes(unicode_report))

        tar = self.home / "artifact.tar"
        tar.write_bytes(b"not a zip")
        wrong = audit_artifact(tar)
        self.assertFalse(wrong["ok"])
        self.assertIn("unsupported_archive_type", _codes(wrong))

    def test_artifact_path_symlink_is_rejected(self) -> None:
        target = self.home / "target.zip"
        target.write_bytes(b"not a zip")
        link = self.home / "link.zip"
        try:
            os.symlink(target, link)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable")
        report = audit_artifact(link)
        self.assertFalse(report["ok"])
        self.assertIn("symlink", _codes(report))


if __name__ == "__main__":
    unittest.main()
