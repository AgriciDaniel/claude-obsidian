#!/usr/bin/env python3
"""Tests for portable package validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from claude_obsidian.package_validation import validate_package


class PackageValidationTests(unittest.TestCase):
    def fixture(self, root: Path, *, frontmatter: str) -> None:
        (root / "skills" / "sample").mkdir(parents=True)
        (root / "skills" / "sample" / "SKILL.md").write_text(
            frontmatter + "\n# Sample\n", encoding="utf-8"
        )
        (root / "hooks").mkdir()
        (root / "hooks" / "hooks.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "Stop": [
                            {
                                "matcher": "",
                                "hooks": [{"type": "command", "command": "true"}],
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )
        (root / ".claude-plugin").mkdir()
        (root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "sample", "version": "1.0.0"}), encoding="utf-8"
        )
        (root / "config").mkdir()
        (root / "config" / "public-marketplace.json").write_text(
            json.dumps(
                {
                    "plugins": [{"name": "sample", "source": "./"}],
                    "version": "1.0.0",
                }
            ),
            encoding="utf-8",
        )

    def test_minimal_portable_package_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root,
                frontmatter="---\nname: sample\ndescription: Portable sample skill.\n---",
            )
            self.assertTrue(validate_package(root)["ok"])

    def test_reserved_host_identity_is_rejected_before_distribution(self) -> None:
        # claude-obsidian is the owner-approved published identity, so a
        # near miss stands in for it here.
        names = ("claude-notes", "claude-obsidian-wiki", "anthropic-notes", "anthropics-wiki", "cc-plugin-notes", "claude")
        for name in names:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root, frontmatter="---\nname: sample\ndescription: Sample.\n---")
                plugin_path = root / ".claude-plugin/plugin.json"
                plugin = json.loads(plugin_path.read_text())
                plugin["name"] = name
                plugin_path.write_text(json.dumps(plugin))
                marketplace_path = root / "config/public-marketplace.json"
                marketplace = json.loads(marketplace_path.read_text())
                marketplace["plugins"][0]["name"] = name
                marketplace_path.write_text(json.dumps(marketplace))
                codes = {item["code"] for item in validate_package(root)["findings"]}
                self.assertIn("reserved_plugin_name", codes)
                plugin["name"] = "claude-obsidian"
                marketplace["plugins"][0]["name"] = plugin["name"]
                plugin_path.write_text(json.dumps(plugin))
                marketplace_path.write_text(json.dumps(marketplace))
                self.assertTrue(validate_package(root)["ok"])

    def test_duplicate_package_authority_keys_are_rejected(self) -> None:
        cases = {
            "hooks/hooks.json": '{"hooks":{},"hooks":{}}',
            ".claude-plugin/plugin.json": (
                '{"name":"sample","version":"1.0.0","version":"1.0.0"}'
            ),
            "config/public-marketplace.json": (
                '{"plugins":[],"plugins":[],"version":"1.0.0"}'
            ),
        }
        for relative, content in cases.items():
            with (
                self.subTest(relative=relative),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                self.fixture(
                    root,
                    frontmatter="---\nname: sample\ndescription: Sample.\n---",
                )
                (root / relative).write_text(content, encoding="utf-8")
                findings = validate_package(root)["findings"]
                self.assertTrue(
                    any(
                        item["code"] == "invalid_json" and item["path"] == relative
                        for item in findings
                    ),
                    findings,
                )

    def test_extra_frontmatter_and_command_mirror_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root,
                frontmatter="---\nname: sample\ndescription: Sample.\nallowed-tools: Read\n---",
            )
            (root / "commands").mkdir()
            (root / "commands" / "sample.md").write_text("duplicate", encoding="utf-8")
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("noncanonical_frontmatter", codes)
            self.assertIn("duplicate_discovery_surface", codes)

    def test_yaml_unsafe_plain_description_is_rejected_and_quoted_form_passes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root,
                frontmatter=(
                    "---\n"
                    "name: sample\n"
                    "description: Explain this syntax: properties and wikilinks.\n"
                    "---"
                ),
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("invalid_yaml_scalar", codes)

            skill = root / "skills/sample/SKILL.md"
            skill.write_text(
                "---\n"
                "name: sample\n"
                'description: "Explain this syntax: properties and wikilinks."\n'
                "---\n"
                "\n# Sample\n",
                encoding="utf-8",
            )
            self.assertTrue(validate_package(root)["ok"])

            skill.write_text(
                "---\n"
                "name: sample\n"
                "description: 'This isn't valid YAML single-quoted text.'\n"
                "---\n",
                encoding="utf-8",
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("invalid_yaml_scalar", codes)

    def test_invalid_hook_and_version_drift_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            (root / "hooks" / "hooks.json").write_text(
                json.dumps({"hooks": {"MadeUp": [{"hooks": [{"type": "magic"}]}]}}),
                encoding="utf-8",
            )
            (root / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"version": "2.0.0"}), encoding="utf-8"
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("unknown_hook_event", codes)
            self.assertIn("invalid_hook_type", codes)
            self.assertIn("version_drift", codes)

    def test_codex_adapter_checks_metadata_and_referenced_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, frontmatter="---\nname: sample\ndescription: Sample.\n---")
            manifest = root / ".codex-plugin/plugin.json"
            manifest.parent.mkdir()
            plugin = {"name": "sample", "version": "1.0.0", "hooks": "./hooks/codex.json"}
            manifest.write_text(json.dumps(plugin), encoding="utf-8")
            commands = root / "hooks/codex.json"
            self.assertIn("missing_file", {f["code"] for f in validate_package(root)["findings"]})
            hook = {"type": "command", "command": "true", "commandWindows": "cmd /c exit 0"}
            hooks = {"hooks": {"Stop": [{"hooks": [hook]}]}}
            commands.write_text(json.dumps(hooks), encoding="utf-8")
            self.assertTrue(validate_package(root)["ok"])
            hooks["hooks"]["Stop"][0]["hooks"].append({"type": "http", "url": "https://example.invalid"})
            manifest.write_text(
                json.dumps({**plugin, "version": "2.0.0", "hooks": "../other.json"}), encoding="utf-8"
            )
            hook["args"] = ["stop"]
            commands.write_text(json.dumps(hooks), encoding="utf-8")
            codes = {f["code"] for f in validate_package(root)["findings"]}
            self.assertTrue({"codex_manifest_drift", "invalid_codex_hooks_path", "invalid_codex_hook_command"} <= codes)
            self.assertIn("invalid_hook_type", codes)

    def test_mcp_hook_fields_and_session_start_restrictions_match_official_schema(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            hook_path = root / "hooks/hooks.json"
            hook_path.write_text(
                json.dumps(
                    {
                        "hooks": {
                            "SessionStart": [
                                {
                                    "matcher": "startup|resume|clear|compact|fork",
                                    "hooks": [
                                        {
                                            "type": "mcp_tool",
                                            "server": "memory",
                                            "tool": "restore_context",
                                            "input": {"project": "${cwd}"},
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertTrue(validate_package(root)["ok"])

            hook_path.write_text(
                json.dumps(
                    {
                        "hooks": {
                            "SessionStart": [
                                {
                                    "matcher": "startup|unsupported",
                                    "hooks": [
                                        {
                                            "type": "prompt",
                                            "prompt": "Review $ARGUMENTS",
                                        }
                                    ],
                                },
                                {
                                    "hooks": [{"type": "mcp_tool", "server": "memory"}],
                                },
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("invalid_session_start_matcher", codes)
            self.assertIn("unsupported_session_start_hook_type", codes)
            self.assertIn("missing_hook_tool", codes)

    def test_transaction_apply_examples_require_reviewed_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            skill = root / "skills/sample/SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8")
                + "\n```bash\nclaude-obsidian transaction apply bundle.json --vault vault\n```\n",
                encoding="utf-8",
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("unapproved_apply_example", codes)

            skill.write_text(
                "---\nname: sample\ndescription: Mentions transaction apply as prose.\n---\n",
                encoding="utf-8",
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertNotIn("unapproved_apply_example", codes)

    def test_user_facing_core_apply_examples_require_reviewed_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            (root / "CLAUDE.md").write_text(
                "```bash\npython3 scripts/claude-obsidian.py init /tmp/v --apply\n```\n",
                encoding="utf-8",
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("unapproved_mutation_example", codes)

    def test_workflow_apply_examples_require_reviewed_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, frontmatter='---\nname: sample\ndescription: Sample.\n---')
            path = root / 'skills/sample/SKILL.md'
            initial = path.read_text()
            path.write_text(initial + '\n```bash\npython3 "$CORE" workflow apply "$BUNDLE" --vault "$VAULT"\n```\n')
            self.assertIn('unapproved_apply_example', {x['code'] for x in validate_package(root)['findings']})
            path.write_text(initial + '\n```bash\npython3 "$CORE" workflow apply "$BUNDLE" --vault "$VAULT" --approved-plan-sha256 "$HASH"\n```\n')
            self.assertNotIn('unapproved_apply_example', {x['code'] for x in validate_package(root)['findings']})

    def test_marketplace_manifest_requires_a_distribution_clean_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            (root / ".claude-plugin" / "marketplace.json").write_bytes(
                (root / "config" / "public-marketplace.json").read_bytes()
            )
            self.assertTrue(validate_package(root)["ok"])
            (root / ".raw").mkdir()
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("unsafe_marketplace_root", codes)

    def test_plugin_json_is_the_only_plugin_version_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            marketplace = json.loads(
                (root / "config" / "public-marketplace.json").read_text(
                    encoding="utf-8"
                )
            )
            marketplace["plugins"][0]["version"] = "1.0.0"
            (root / "config" / "public-marketplace.json").write_text(
                json.dumps(marketplace), encoding="utf-8"
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("duplicate_version_authority", codes)

    def test_marketplace_renames_must_resolve_to_a_listed_plugin_or_null(
        self,
    ) -> None:
        cases = {
            "valid": ({"old-sample": "sample"}, True),
            "removed": ({"gone": None}, True),
            "chained": ({"oldest": "old", "old": "sample"}, True),
            "missing-target": ({"old-sample": "absent"}, False),
            "cycle": ({"a": "b", "b": "a"}, False),
            "listed-key": ({"sample": "other"}, False),
            "not-object": (["old-sample"], False),
            "bad-name": ({"Old Sample": "sample"}, False),
        }
        for label, (renames, ok) in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(
                    root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
                )
                path = root / "config" / "public-marketplace.json"
                marketplace = json.loads(path.read_text(encoding="utf-8"))
                marketplace["renames"] = renames
                path.write_text(json.dumps(marketplace), encoding="utf-8")
                result = validate_package(root)
                codes = {item["code"] for item in result["findings"]}
                self.assertEqual(ok, result["ok"], result["findings"])
                if not ok:
                    self.assertIn("invalid_marketplace_renames", codes)

    def test_reserved_names_match_the_host_separator_rules(self) -> None:
        for name, reserved in (
            ("official-claude-tools", True),
            ("anthropic-official", True),
            ("notes-official-claude", True),
            ("official-notes", False),
            ("notes-claude-and-official", False),
            ("officialclaudex", True),
            ("xclaude-official", True),
            ("claudecode", True),
            ("ccplugin-notes", True),
            ("claudenotes", False),
            ("ccpluginnotes", False),
        ):
            with self.subTest(name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(
                    root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
                )
                for relative in (
                    ".claude-plugin/plugin.json",
                    "config/public-marketplace.json",
                ):
                    path = root / relative
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if "plugins" in data:
                        data["plugins"][0]["name"] = name
                    else:
                        data["name"] = name
                    path.write_text(json.dumps(data), encoding="utf-8")
                codes = {item["code"] for item in validate_package(root)["findings"]}
                self.assertEqual(reserved, "reserved_plugin_name" in codes)

    def test_published_marketplace_migrates_the_former_plugin_identity(self) -> None:
        # 3.0.0 shipped as agricidaniel-obsidian; 3.0.1 restores claude-obsidian.
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual("claude-obsidian", plugin["name"])
        for relative in (".claude-plugin/marketplace.json", "config/public-marketplace.json"):
            with self.subTest(relative):
                marketplace = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertEqual(
                    {"agricidaniel-obsidian": plugin["name"]}, marketplace.get("renames")
                )

    def test_skills_cannot_invoke_product_helpers_relative_to_the_vault_cwd(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            reference = root / "skills/sample/references/workflow.md"
            reference.parent.mkdir()
            reference.write_text(
                '```bash\npython3 scripts/claude-obsidian.py lint --vault "$VAULT"\n```\n',
                encoding="utf-8",
            )
            findings = validate_package(root)["findings"]
            codes = {item["code"] for item in findings}
            self.assertIn("cwd_relative_product_helper", codes)
            self.assertTrue(
                any(
                    item["path"] == "skills/sample/references/workflow.md"
                    for item in findings
                )
            )

            (root / "agents").mkdir()
            (root / "agents" / "reviewer.md").write_text(
                "Run `python3 scripts/claude-obsidian.py lint --vault .`.\n",
                encoding="utf-8",
            )
            findings = validate_package(root)["findings"]
            self.assertTrue(
                any(
                    item["code"] == "cwd_relative_product_helper"
                    and item["path"] == "agents/reviewer.md"
                    for item in findings
                )
            )

    def test_wiki_reference_links_require_the_skill_relative_anchor_sentence(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            skill = root / "skills/sample/SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8")
                + "\nRead [the transaction contract]"
                "(../wiki/references/operation-transactions.md).\n",
                encoding="utf-8",
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertIn("unanchored_wiki_reference_link", codes)

            skill.write_text(
                skill.read_text(encoding="utf-8")
                + "\nEvery `../wiki/references/` link in this file resolves the"
                " same way, relative to this skill's own directory under"
                " `$PRODUCT_ROOT`, never relative to the selected vault's"
                " `wiki/` directory.\n",
                encoding="utf-8",
            )
            codes = {item["code"] for item in validate_package(root)["findings"]}
            self.assertNotIn("unanchored_wiki_reference_link", codes)

    def test_top_level_bin_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(
                root, frontmatter="---\nname: sample\ndescription: Sample.\n---"
            )
            (root / "bin").mkdir()
            (root / "bin" / "setup-example.sh").write_text(
                "#!/usr/bin/env bash\n", encoding="utf-8"
            )
            findings = validate_package(root)["findings"]
            codes = {item["code"] for item in findings}
            self.assertIn("top_level_bin_directory", codes)


if __name__ == "__main__":
    unittest.main()
