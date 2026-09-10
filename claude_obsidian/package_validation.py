"""Deterministic validation for the distributable plugin package.

The validator intentionally uses only the standard library. Agent Skills
frontmatter is constrained to two single-line scalar fields; the parser accepts
JSON-compatible double-quoted strings, YAML single-quoted strings, and the safe
plain-scalar subset. This keeps the package dependency-free while rejecting
plain-scalar forms that a conforming YAML parser would reinterpret or reject.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .json_utils import strict_json_loads


ALLOWED_HOOK_EVENTS = {
    "SessionStart",
    "Stop",
    "PreToolUse",
    "PostToolUse",
    "PreCompact",
    "PostCompact",
    "UserPromptSubmit",
}
ALLOWED_HOOK_TYPES = {"command", "prompt", "http", "mcp_tool", "agent"}
SESSION_START_HOOK_TYPES = {"command", "mcp_tool"}
SESSION_START_MATCHERS = {"startup", "resume", "clear", "compact"}
PORTABLE_SKILL_KEYS = ("name", "description")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKETPLACE_TEMPLATE = "config/public-marketplace.json"
MARKETPLACE_PATH = ".claude-plugin/marketplace.json"
YAML_PLAIN_FORBIDDEN_START = frozenset("-?:,[]{}#&*!|>'\"%@`")


def _finding(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _load_json(root: Path, relative: str) -> tuple[Any | None, list[dict[str, str]]]:
    path = root / relative
    try:
        return strict_json_loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [_finding("missing_file", relative, "required file is missing")]
    except (json.JSONDecodeError, ValueError) as exc:
        detail = (
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
            if isinstance(exc, json.JSONDecodeError)
            else str(exc)
        )
        return None, [
            _finding(
                "invalid_json",
                relative,
                detail,
            )
        ]


def _frontmatter_scalar(
    raw: str, relative: str, number: int
) -> tuple[str | None, list[dict[str, str]]]:
    """Parse the deliberately small, single-line YAML scalar subset we ship."""

    if not raw:
        return "", []
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            return None, [
                _finding(
                    "invalid_yaml_scalar",
                    relative,
                    f"line {number} has an invalid double-quoted scalar: {exc.msg}",
                )
            ]
        if not isinstance(value, str):
            return None, [
                _finding(
                    "invalid_yaml_scalar",
                    relative,
                    f"line {number} must contain a string scalar",
                )
            ]
        return value, []
    if raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            return None, [
                _finding(
                    "invalid_yaml_scalar",
                    relative,
                    f"line {number} has an unterminated single-quoted scalar",
                )
            ]
        inner = raw[1:-1]
        index = 0
        while index < len(inner):
            if inner[index] != "'":
                index += 1
                continue
            if index + 1 >= len(inner) or inner[index + 1] != "'":
                return None, [
                    _finding(
                        "invalid_yaml_scalar",
                        relative,
                        f"line {number} has an unescaped quote in a single-quoted scalar",
                    )
                ]
            index += 2
        return inner.replace("''", "'"), []

    # YAML plain scalars cannot begin with an indicator and cannot contain a
    # colon followed by whitespace/end or a comment marker after whitespace.
    # These are the forms most likely to pass a naive split parser while
    # failing the official Agent Skills YAML validator.
    if (
        raw[0] in YAML_PLAIN_FORBIDDEN_START
        or re.search(r":(?:[ \t]|$)", raw)
        or re.search(r"(?:^|[ \t])#", raw)
        or "\t" in raw
    ):
        return None, [
            _finding(
                "invalid_yaml_scalar",
                relative,
                f"line {number} is not a safe YAML plain scalar; quote the complete value",
            )
        ]
    return raw, []


def _frontmatter(
    path: Path, relative: str
) -> tuple[dict[str, str], list[dict[str, str]]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError) as exc:
        return {}, [_finding("unreadable_skill", relative, str(exc))]
    if not text.startswith("---\n"):
        return {}, [_finding("missing_frontmatter", relative, "must begin with ---")]
    marker = text.find("\n---\n", 4)
    if marker < 0:
        return {}, [_finding("invalid_frontmatter", relative, "closing --- is missing")]

    values: dict[str, str] = {}
    errors: list[dict[str, str]] = []
    for number, raw in enumerate(text[4:marker].splitlines(), start=2):
        if not raw.strip():
            continue
        if raw[:1].isspace() or ":" not in raw:
            errors.append(
                _finding(
                    "nonportable_frontmatter",
                    relative,
                    f"line {number} must be a single-line key: value pair",
                )
            )
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        parsed_value, scalar_errors = _frontmatter_scalar(
            value.strip(), relative, number
        )
        errors.extend(scalar_errors)
        if parsed_value is None:
            continue
        if key in values:
            errors.append(_finding("duplicate_frontmatter_key", relative, key))
        values[key] = parsed_value
    return values, errors


def _validate_skills(root: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    skills_root = root / "skills"
    paths = sorted(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    if not paths:
        return [_finding("missing_skills", "skills", "no skills were discovered")]

    seen: set[str] = set()
    for path in paths:
        relative = path.relative_to(root).as_posix()
        values, parse_errors = _frontmatter(path, relative)
        errors.extend(parse_errors)
        keys = tuple(values)
        if keys != PORTABLE_SKILL_KEYS:
            errors.append(
                _finding(
                    "noncanonical_frontmatter",
                    relative,
                    "frontmatter keys must be exactly name, description in that order",
                )
            )
        name = values.get("name", "")
        description = values.get("description", "")
        if name != path.parent.name or NAME_RE.fullmatch(name) is None:
            errors.append(
                _finding(
                    "invalid_skill_name",
                    relative,
                    "name must match its kebab-case directory",
                )
            )
        if name in seen:
            errors.append(_finding("duplicate_skill_name", relative, name))
        seen.add(name)
        if not description or len(description) > 1024:
            errors.append(
                _finding(
                    "invalid_description",
                    relative,
                    "description must contain 1-1024 characters",
                )
            )
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        in_code_fence = False
        for index, line in enumerate(lines):
            if line.lstrip().startswith("```"):
                in_code_fence = not in_code_fence
                continue
            if not in_code_fence or "transaction apply" not in line:
                continue
            command_window = " ".join(lines[index : index + 3])
            if "--approved-plan-sha256" not in command_window:
                errors.append(
                    _finding(
                        "unapproved_apply_example",
                        relative,
                        f"line {index + 1} transaction apply omits --approved-plan-sha256",
                    )
                )

    command_markdown = (
        sorted((root / "commands").glob("*.md")) if (root / "commands").is_dir() else []
    )
    for path in command_markdown:
        errors.append(
            _finding(
                "duplicate_discovery_surface",
                path.relative_to(root).as_posix(),
                "slash-command mirrors are not shipped; the skill is the canonical surface",
            )
        )
    return errors


def _validate_documented_apply_examples(root: Path) -> list[dict[str, str]]:
    """Keep current user-facing core apply examples on the approval workflow."""

    paths = [root / name for name in ("README.md", "CLAUDE.md", "WIKI.md")]
    paths.extend(sorted((root / "docs").glob("*.md")))
    paths.extend(sorted((root / "skills").glob("**/*.md")))
    findings: list[dict[str, str]] = []
    mutation = re.compile(
        r"claude-obsidian\.py\s+(?:init|adopt|migrate|mode\s+set|extension\s+dragonscale|capture\s+apply)\b"
    )
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for block in re.finditer(
            r"```(?:bash|sh|shell)?\s*\n(.*?)```", text, re.DOTALL
        ):
            logical = block.group(1).replace("\\\n", " ")
            for line in logical.splitlines():
                if (
                    mutation.search(line)
                    and "--apply" in line
                    and "--approved-plan-sha256" not in line
                ):
                    findings.append(
                        _finding(
                            "unapproved_mutation_example",
                            path.relative_to(root).as_posix(),
                            "documented core --apply example omits --approved-plan-sha256",
                        )
                    )
    return findings


def _validate_skill_helper_paths(root: Path) -> list[dict[str, str]]:
    """Executable prompts must not resolve product helpers from a user-vault cwd."""

    findings: list[dict[str, str]] = []
    unresolved = re.compile(r"(?:python3|bash)\s+[\"']?(?:scripts|bin)/")
    prompt_paths = list((root / "skills").glob("**/*.md"))
    prompt_paths.extend((root / "agents").glob("*.md"))
    for path in sorted(prompt_paths):
        text = path.read_text(encoding="utf-8")
        match = unresolved.search(text)
        if match is None:
            continue
        line = text.count("\n", 0, match.start()) + 1
        findings.append(
            _finding(
                "cwd_relative_product_helper",
                path.relative_to(root).as_posix(),
                f"line {line} must resolve the installed product root and invoke an absolute helper path",
            )
        )
    return findings


def _validate_wiki_reference_link_anchors(root: Path) -> list[dict[str, str]]:
    """A ../wiki/references/ link must state its skill-relative resolution root."""

    findings: list[dict[str, str]] = []
    link_pattern = re.compile(r"\.\./wiki/references/")
    anchor_phrase = "relative to this skill's own directory under `$PRODUCT_ROOT`"
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        if not link_pattern.search(text):
            continue
        normalized = " ".join(text.split())
        if anchor_phrase not in normalized:
            findings.append(
                _finding(
                    "unanchored_wiki_reference_link",
                    path.relative_to(root).as_posix(),
                    "a ../wiki/references/ link needs the skill-relative resolution sentence",
                )
            )
    return findings


def _validate_no_legacy_bin_directory(root: Path) -> list[dict[str, str]]:
    """claude.ai rejects a plugin distributing a top-level bin/ directory."""

    if (root / "bin").exists():
        return [
            _finding(
                "top_level_bin_directory",
                "bin",
                "top-level bin/ is rejected by claude.ai plugin distribution; "
                "use scripts/ instead",
            )
        ]
    return []


def _validate_hooks(root: Path) -> list[dict[str, str]]:
    document, errors = _load_json(root, "hooks/hooks.json")
    if errors:
        return errors
    if not isinstance(document, dict) or not isinstance(document.get("hooks"), dict):
        return [
            _finding("invalid_hooks", "hooks/hooks.json", "hooks must be an object")
        ]

    findings: list[dict[str, str]] = []
    for event, groups in document["hooks"].items():
        if event not in ALLOWED_HOOK_EVENTS:
            findings.append(_finding("unknown_hook_event", "hooks/hooks.json", event))
        if not isinstance(groups, list):
            findings.append(_finding("invalid_hook_groups", "hooks/hooks.json", event))
            continue
        for group_index, group in enumerate(groups):
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                findings.append(
                    _finding(
                        "invalid_hook_group",
                        "hooks/hooks.json",
                        f"{event}[{group_index}]",
                    )
                )
                continue
            if event == "SessionStart" and "matcher" in group:
                matcher = group.get("matcher")
                matcher_parts = matcher.split("|") if isinstance(matcher, str) else []
                if (
                    not matcher_parts
                    or any(part not in SESSION_START_MATCHERS for part in matcher_parts)
                    or len(set(matcher_parts)) != len(matcher_parts)
                ):
                    findings.append(
                        _finding(
                            "invalid_session_start_matcher",
                            "hooks/hooks.json",
                            f"{event}[{group_index}]",
                        )
                    )
            for hook_index, hook in enumerate(group["hooks"]):
                location = f"{event}[{group_index}].hooks[{hook_index}]"
                if (
                    not isinstance(hook, dict)
                    or hook.get("type") not in ALLOWED_HOOK_TYPES
                ):
                    findings.append(
                        _finding("invalid_hook_type", "hooks/hooks.json", location)
                    )
                    continue
                hook_type = hook["type"]
                if (
                    event == "SessionStart"
                    and hook_type not in SESSION_START_HOOK_TYPES
                ):
                    findings.append(
                        _finding(
                            "unsupported_session_start_hook_type",
                            "hooks/hooks.json",
                            location,
                        )
                    )
                if hook_type == "command":
                    if not isinstance(hook.get("command"), str) or not hook["command"]:
                        findings.append(
                            _finding(
                                "missing_hook_command", "hooks/hooks.json", location
                            )
                        )
                    args = hook.get("args", [])
                    if "args" in hook and (
                        not isinstance(args, list)
                        or not all(isinstance(value, str) for value in args)
                    ):
                        findings.append(
                            _finding("invalid_hook_args", "hooks/hooks.json", location)
                        )
                elif hook_type == "http":
                    if not isinstance(hook.get("url"), str) or not hook["url"]:
                        findings.append(
                            _finding("missing_hook_url", "hooks/hooks.json", location)
                        )
                elif hook_type == "mcp_tool":
                    if not isinstance(hook.get("server"), str) or not hook["server"]:
                        findings.append(
                            _finding(
                                "missing_hook_server", "hooks/hooks.json", location
                            )
                        )
                    if not isinstance(hook.get("tool"), str) or not hook["tool"]:
                        findings.append(
                            _finding("missing_hook_tool", "hooks/hooks.json", location)
                        )
                    if "input" in hook and not isinstance(hook.get("input"), dict):
                        findings.append(
                            _finding("invalid_hook_input", "hooks/hooks.json", location)
                        )
                elif hook_type in {"prompt", "agent"}:
                    if not isinstance(hook.get("prompt"), str) or not hook["prompt"]:
                        findings.append(
                            _finding(
                                "missing_hook_prompt", "hooks/hooks.json", location
                            )
                        )
    return findings


def _validate_versions(root: Path) -> list[dict[str, str]]:
    plugin, errors = _load_json(root, ".claude-plugin/plugin.json")
    marketplace, marketplace_errors = _load_json(root, MARKETPLACE_TEMPLATE)
    errors.extend(marketplace_errors)
    if errors:
        return errors
    findings: list[dict[str, str]] = []
    plugin_name = plugin.get("name") if isinstance(plugin, dict) else None
    plugin_version = plugin.get("version") if isinstance(plugin, dict) else None
    entries = marketplace.get("plugins") if isinstance(marketplace, dict) else None
    entry = entries[0] if isinstance(entries, list) and len(entries) == 1 else None
    marketplace_version = (
        marketplace.get("version") if isinstance(marketplace, dict) else None
    )
    if not isinstance(plugin_name, str) or NAME_RE.fullmatch(plugin_name) is None:
        findings.append(
            _finding("invalid_plugin_name", ".claude-plugin/plugin.json", "name")
        )
    if not isinstance(plugin_version, str) or not plugin_version:
        findings.append(
            _finding("missing_version", ".claude-plugin/plugin.json", "version")
        )
    elif marketplace_version != plugin_version:
        findings.append(
            _finding(
                "version_drift",
                MARKETPLACE_TEMPLATE,
                "plugin and public marketplace versions must match",
            )
        )
    if not isinstance(entry, dict):
        findings.append(
            _finding(
                "invalid_marketplace",
                MARKETPLACE_TEMPLATE,
                "exactly one plugin entry is required",
            )
        )
    else:
        if entry.get("name") != plugin_name:
            findings.append(
                _finding(
                    "marketplace_name_drift",
                    MARKETPLACE_TEMPLATE,
                    "plugin names must match",
                )
            )
        if entry.get("source") != "./":
            findings.append(
                _finding(
                    "unsafe_marketplace_source",
                    MARKETPLACE_TEMPLATE,
                    "the generated public marketplace must use its audited artifact root",
                )
            )
        if "version" in entry:
            findings.append(
                _finding(
                    "duplicate_version_authority",
                    MARKETPLACE_TEMPLATE,
                    "plugin.json is the sole plugin-version authority",
                )
            )

    installed_manifest = root / MARKETPLACE_PATH
    if installed_manifest.is_symlink():
        findings.append(
            _finding(
                "unsafe_marketplace_manifest",
                MARKETPLACE_PATH,
                "distribution manifest cannot be a symlink",
            )
        )
    elif installed_manifest.exists():
        installed, installed_errors = _load_json(root, MARKETPLACE_PATH)
        findings.extend(installed_errors)
        if installed != marketplace:
            findings.append(
                _finding(
                    "marketplace_template_drift",
                    MARKETPLACE_PATH,
                    "distribution manifest must exactly match the reviewed template",
                )
            )
        live_roots = [
            path for path in (".raw", ".vault-meta", "wiki") if (root / path).exists()
        ]
        if live_roots:
            findings.append(
                _finding(
                    "unsafe_marketplace_root",
                    MARKETPLACE_PATH,
                    "marketplace root contains contributor/live-vault state: "
                    + ", ".join(live_roots),
                )
            )
    return findings


def validate_package(root: Path) -> dict[str, Any]:
    """Return a stable package-validation report without mutating the repository."""

    root = Path(root).resolve(strict=True)
    findings = [
        *_validate_skills(root),
        *_validate_documented_apply_examples(root),
        *_validate_skill_helper_paths(root),
        *_validate_wiki_reference_link_anchors(root),
        *_validate_no_legacy_bin_directory(root),
        *_validate_hooks(root),
        *_validate_versions(root),
    ]
    findings = sorted(
        {
            (
                finding["path"],
                finding["code"],
                finding["message"],
            ): finding
            for finding in findings
        }.values(),
        key=lambda finding: (finding["path"], finding["code"], finding["message"]),
    )
    return {
        "schema": "claude-obsidian.package-validation.v1",
        "ok": not findings,
        "skills": len(list((root / "skills").glob("*/SKILL.md"))),
        "findings": findings,
    }
