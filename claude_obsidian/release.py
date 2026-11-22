"""Deterministic, fail-closed public release artifacts.

This module deliberately has no publishing or Git-mutation capability.  A
build reads a clean Git worktree, selects tracked files through an explicit
allowlist, scans the selected bytes, writes a deterministic ZIP, and audits
that ZIP before making it visible at the requested output path.
"""

from __future__ import annotations

import fnmatch
import hashlib
import hmac
import html
import io
import json
import os
import re
import stat
import struct
import subprocess
import tempfile
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from .json_utils import parse_finite_json_float
from .package_validation import CODEX_HOOKS, CODEX_MANIFEST, validate_codex_manifest

SCHEMA_VERSION = 1
CONFIG_PATH = PurePosixPath("config/release-allowlist.json")
MANIFEST_NAME = "RELEASE_MANIFEST.json"
CHECKSUMS_NAME = "SHA256SUMS"
GENERATED_NAMES = frozenset({MANIFEST_NAME, CHECKSUMS_NAME})
PUBLIC_MARKETPLACE_PATH = ".claude-plugin/marketplace.json"
PUBLIC_MARKETPLACE_TEMPLATE = "config/public-marketplace.json"

# ZIP dates cannot represent earlier or later instants.  Requiring rather than
# silently clamping avoids two different SOURCE_DATE_EPOCH values producing
# misleading metadata.
MIN_ZIP_EPOCH = 315532800  # 1980-01-01T00:00:00Z
MAX_ZIP_EPOCH = 4354819198  # 2107-12-31T23:59:58Z

DEFAULT_LIMITS: Mapping[str, int] = {
    "max_archive_bytes": 100 * 1024 * 1024,
    "max_file_bytes": 10 * 1024 * 1024,
    "max_total_bytes": 50 * 1024 * 1024,
    "max_files": 5000,
    "max_compression_ratio": 20,
}

_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_ABSOLUTE_HOME_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_.-])/(?:var/)?home/[A-Za-z0-9._-]+(?:/|$)"),
    re.compile(r"(?<![A-Za-z0-9_.-])/Users/[A-Za-z0-9._-]+(?:/|$)"),
    re.compile(r"(?i)(?<![A-Za-z0-9_.-])[A-Z]:\\Users\\[A-Za-z0-9._-]+(?:\\|$)"),
)
_TOKEN_PATTERNS = (
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\b(?:sk-ant-|sk-proj-|sk-)[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)"
        r"\s*[:=]\s*[\"']?([A-Za-z0-9_./+=-]{16,})"
    ),
    re.compile(r"(?i)\b(?:cookie|set-cookie)\s*:\s*[^\r\n]{12,}"),
)
# This is intentionally a conservative privacy detector rather than an email
# validator. It recognizes ordinary and quoted local parts, Unicode/EAI names,
# dotted internationalized domains, and address literals. HTML entities are
# decoded before matching so rendered ``&#64;``/``&commat;`` forms cannot hide
# a personal contact address from the release gate.
_EMAIL_DOMAIN_LABEL = r"[^\W_](?:(?:[^\W_]|-){0,61}[^\W_])?"
_EMAIL_TLD_LABEL = r"[^\W\d_](?:(?:[^\W_]|-){0,61}[^\W_])?"
_EMAIL_ADDRESS_RE = re.compile(
    r"(?iu)(?<![\w.!#$%&'*+/=?^`{|}~-])"
    r"(?:\"(?:[^\"\\\r\n]|\\.){1,128}\"|[\w.!#$%&'*+/=?^`{|}~-]+)@"
    rf"(?:(?:{_EMAIL_DOMAIN_LABEL}\.)+{_EMAIL_TLD_LABEL}"
    r"|\[(?:IPv6:)?[0-9A-F:.]+\])"
    r"(?![\w-])"
)
_RELEASE_SAFE_EMAIL_DOMAINS = frozenset(
    {
        "example.com",
        "example.invalid",
        "example.net",
        "example.org",
        "users.noreply.github.com",
    }
)
_RELEASE_SAFE_EMAIL_ADDRESSES = frozenset({"noreply@github.com"})
_SECRET_FILE_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx", ".jks"})
_SECRET_FILE_NAMES = frozenset(
    {
        "auth.json",
        "cookies.txt",
        "credentials",
        "credentials.json",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "id_rsa",
        ".netrc",
        ".npmrc",
        ".pypirc",
    }
)
_PLACEHOLDER_VALUES = frozenset(
    {
        "changeme",
        "dummy",
        "example",
        "placeholder",
        "redacted",
        "replace-me",
        "test-value",
        "your-api-key",
        "your-token-here",
    }
)


Error = dict[str, str]


def _error(code: str, path: str, message: str) -> Error:
    return {"code": code, "path": path, "message": message}


def _sorted_errors(errors: Iterable[Error]) -> list[Error]:
    unique = {
        (item.get("path", ""), item.get("code", ""), item.get("message", "")): {
            "code": item.get("code", "error"),
            "path": item.get("path", ""),
            "message": item.get("message", "release safety check failed"),
        }
        for item in errors
    }
    return [unique[key] for key in sorted(unique)]


def _failure(kind: str, errors: Iterable[Error], **details: Any) -> dict[str, Any]:
    ordered = _sorted_errors(errors)
    report: dict[str, Any] = {
        "ok": False,
        "kind": kind,
        "errors": ordered,
        "summary": {"error_count": len(ordered)},
    }
    report.update(details)
    return report


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_oid(data: bytes, expected_oid: str) -> str:
    """Hash bytes exactly as the repository's SHA-1 or SHA-256 object format."""

    if len(expected_oid) == 40:
        # This is Git object-format compatibility, not a security primitive.
        # ``usedforsecurity=False`` also keeps SHA-1 repositories auditable on
        # FIPS-constrained Python builds.
        digest = hashlib.sha1(usedforsecurity=False)
    elif len(expected_oid) == 64:
        digest = hashlib.sha256()
    else:
        return ""
    digest.update(f"blob {len(data)}\0".encode("ascii"))
    digest.update(data)
    return digest.hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _safe_relative_path(value: Any, *, location: str) -> tuple[str | None, list[Error]]:
    if not isinstance(value, str) or not value:
        return None, [
            _error("invalid_path", location, "path must be a non-empty string")
        ]
    if unicodedata.normalize("NFC", value) != value:
        return None, [
            _error("noncanonical_path", location, "path must use NFC Unicode")
        ]
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        return None, [
            _error("invalid_path", location, "path contains a control character")
        ]
    if "\\" in value or value.startswith("/") or _WINDOWS_DRIVE_RE.match(value):
        return None, [
            _error("path_escape", location, "path must be relative POSIX syntax")
        ]
    parsed = PurePosixPath(value)
    if value in {".", ".."} or ".." in parsed.parts or parsed.as_posix() != value:
        return None, [
            _error("path_escape", location, "path is not canonical or escapes root")
        ]
    if any(part in {"", ".", ".."} for part in value.split("/")):
        return None, [
            _error("noncanonical_path", location, "path has an empty or dot segment")
        ]
    return value, []


def _portable_path_key(value: str) -> str:
    """Return the cross-platform identity used for archive path collisions."""

    return unicodedata.normalize("NFC", value.casefold())


def _strict_json_loads(value: str) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key: {key}")
            result[key] = item
        return result

    def reject_constant(constant: str) -> None:
        raise ValueError(f"non-finite JSON number is not permitted: {constant}")

    return json.loads(
        value,
        object_pairs_hook=reject_duplicates,
        parse_constant=reject_constant,
        parse_float=parse_finite_json_float,
    )


def _hard_path_errors(path: str) -> list[Error]:
    """Enforce exclusions that configuration is never allowed to weaken."""

    checked, errors = _safe_relative_path(path, location=path)
    if errors or checked is None:
        return errors
    parts = PurePosixPath(checked).parts
    lower_parts = tuple(_portable_path_key(part) for part in parts)
    lower = _portable_path_key(checked)
    basename = lower_parts[-1]

    if lower_parts[0] == ".git":
        errors.append(
            _error("hard_excluded", checked, "Git internals cannot be released")
        )
    if lower_parts[0] == ".raw":
        errors.append(
            _error(
                "raw_source", checked, "root .raw source payloads cannot be released"
            )
        )
    if lower_parts[0] == ".vault-meta":
        errors.append(
            _error(
                "live_vault_state", checked, "live .vault-meta state cannot be released"
            )
        )
    if lower in {"wiki/hot.md", "wiki/log.md"}:
        errors.append(
            _error("live_vault_state", checked, "live hot/log state cannot be released")
        )
    if (
        basename.startswith("workspace") or basename.startswith("recent")
    ) and PurePosixPath(basename).suffix == ".json":
        errors.append(
            _error(
                "workspace_state",
                checked,
                "Obsidian workspace/recent state cannot be released",
            )
        )
    if basename == ".env" or basename.startswith(".env."):
        errors.append(
            _error("secret_file", checked, "environment files cannot be released")
        )
    if (
        basename in _SECRET_FILE_NAMES
        or PurePosixPath(basename).suffix in _SECRET_FILE_SUFFIXES
    ):
        errors.append(
            _error(
                "secret_file", checked, "credential/private-key file cannot be released"
            )
        )
    return errors


def _is_disclosure_path(path: str) -> bool:
    stem = _portable_path_key(PurePosixPath(path).stem)
    return "attribution" in stem or "disclosure" in stem


def _looks_binary(path: str, data: bytes) -> bool:
    if b"\x00" in data[:8192]:
        return True
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def _scan_content(
    path: str,
    data: bytes,
    *,
    approved_private_urls: frozenset[str],
    reviewed_binaries: Mapping[str, str],
) -> list[Error]:
    errors: list[Error] = []
    digest = _sha256(data)
    if _looks_binary(path, data):
        if reviewed_binaries.get(path) != digest:
            errors.append(
                _error(
                    "unreviewed_binary",
                    path,
                    "binary content requires an explicitly reviewed SHA-256",
                )
            )
        return errors

    text = data.decode("utf-8")
    for pattern in _ABSOLUTE_HOME_PATTERNS:
        if pattern.search(text):
            errors.append(
                _error(
                    "absolute_home_path",
                    path,
                    "content contains an absolute user-home path",
                )
            )
            break

    # Keep this sensitive fragment split so the scanner can safely package its
    # own implementation without whitelisting source code.
    private_repo_fragment = ("github.com/" + "AI-Marketing-Hub").casefold()
    if private_repo_fragment in text.casefold() and path not in approved_private_urls:
        errors.append(
            _error(
                "private_repository_url",
                path,
                "private AI Marketing Hub repository URL is allowed only in an approved disclosure",
            )
        )

    decoded_text = html.unescape(text)
    for email_match in _EMAIL_ADDRESS_RE.finditer(decoded_text):
        address = email_match.group(0).casefold()
        domain = address.rpartition("@")[2]
        # ``git@host:owner/repository`` is an SSH/scp clone locator, not an
        # email address. Keep the exception narrow so other local parts and
        # ordinary address punctuation remain subject to the privacy gate.
        if (
            address.startswith("git@")
            and email_match.end() < len(decoded_text)
            and decoded_text[email_match.end()] == ":"
            and re.match(r"[^\s/:]+/[^\s]+", decoded_text[email_match.end() + 1 :])
        ):
            continue
        if (
            address in _RELEASE_SAFE_EMAIL_ADDRESSES
            or domain in _RELEASE_SAFE_EMAIL_DOMAINS
        ):
            continue
        errors.append(
            _error(
                "personal_email_address",
                path,
                "content contains an email address outside the release-safe placeholder/noreply allowlist",
            )
        )
        break

    for pattern in _TOKEN_PATTERNS:
        match = pattern.search(text)
        if match is None:
            continue
        captured = match.group(1).casefold() if match.lastindex else ""
        if captured in _PLACEHOLDER_VALUES or any(
            word in captured for word in ("example", "placeholder", "redacted", "your-")
        ):
            continue
        errors.append(
            _error(
                "secret_material", path, "content matches a credential/secret pattern"
            )
        )
        break
    return errors


def _validate_limits(value: Any, *, path: str) -> tuple[dict[str, int], list[Error]]:
    if not isinstance(value, dict):
        return dict(DEFAULT_LIMITS), [
            _error("invalid_config", path, "limits must be an object")
        ]
    limits: dict[str, int] = {}
    errors: list[Error] = []
    for name in sorted(set(value) - set(DEFAULT_LIMITS)):
        errors.append(_error("invalid_config", f"{path}.{name}", "unknown limit key"))
    for name, default in DEFAULT_LIMITS.items():
        supplied = value.get(name, default)
        if not isinstance(supplied, int) or isinstance(supplied, bool) or supplied <= 0:
            errors.append(
                _error(
                    "invalid_config",
                    f"{path}.{name}",
                    "limit must be a positive integer",
                )
            )
            limits[name] = default
        else:
            limits[name] = supplied
    if (
        limits["max_total_bytes"]
        > limits["max_archive_bytes"] * limits["max_compression_ratio"]
    ):
        errors.append(
            _error(
                "invalid_config",
                path,
                "total-size policy exceeds the archive/ratio safety envelope",
            )
        )
    return limits, errors


def _validate_pattern(value: Any, location: str) -> tuple[str | None, list[Error]]:
    path, errors = _safe_relative_path(value, location=location)
    if errors:
        return None, errors
    assert path is not None
    if path.startswith("!"):
        return None, [
            _error("invalid_config", location, "negated patterns are not supported")
        ]
    return path, []


def _load_config(repo_root: Path) -> tuple[dict[str, Any] | None, list[Error]]:
    config_path = repo_root / CONFIG_PATH
    try:
        if config_path.is_symlink():
            return None, [
                _error(
                    "symlink",
                    str(CONFIG_PATH),
                    "release configuration cannot be a symlink",
                )
            ]
        raw = config_path.read_bytes()
    except OSError:
        return None, [
            _error(
                "missing_config",
                str(CONFIG_PATH),
                "release allowlist is missing or unreadable",
            )
        ]
    if len(raw) > 1024 * 1024:
        return None, [
            _error("invalid_config", str(CONFIG_PATH), "release allowlist is too large")
        ]
    try:
        document = _strict_json_loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None, [
            _error(
                "invalid_config",
                str(CONFIG_PATH),
                "release allowlist is not valid UTF-8 JSON",
            )
        ]
    if (
        not isinstance(document, dict)
        or document.get("schema_version") != SCHEMA_VERSION
    ):
        return None, [
            _error("invalid_config", str(CONFIG_PATH), "schema_version must be 1")
        ]
    if (
        document.get("archive_format") != "zip"
        or document.get("compression") != "stored"
    ):
        return None, [
            _error(
                "invalid_config",
                str(CONFIG_PATH),
                "only deterministic stored ZIP artifacts are supported",
            )
        ]

    errors: list[Error] = []
    allowed_keys = {
        "schema_version",
        "archive_format",
        "compression",
        "include_files",
        "include_roots",
        "include_globs",
        "exclude_globs",
        "archive_overlays",
        "approved_private_url_disclosures",
        "reviewed_binaries",
        "limits",
    }
    for field in sorted(set(document) - allowed_keys):
        errors.append(_error("invalid_config", field, "unknown top-level key"))
    normalized: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "archive_format": "zip",
        "compression": "stored",
    }
    for field in ("include_files", "include_roots", "include_globs", "exclude_globs"):
        values = document.get(field)
        if not isinstance(values, list):
            errors.append(_error("invalid_config", field, "must be an array"))
            normalized[field] = []
            continue
        parsed: list[str] = []
        for index, item in enumerate(values):
            candidate, item_errors = _validate_pattern(item, f"{field}[{index}]")
            errors.extend(item_errors)
            if candidate is not None:
                parsed.append(
                    candidate.rstrip("/") if field == "include_roots" else candidate
                )
        if parsed != sorted(set(parsed)):
            errors.append(
                _error("invalid_config", field, "values must be unique and sorted")
            )
        normalized[field] = parsed

    if (
        not normalized["include_files"]
        and not normalized["include_roots"]
        and not normalized["include_globs"]
    ):
        errors.append(
            _error(
                "invalid_config",
                "include",
                "at least one allowlist selector is required",
            )
        )

    overlays = document.get("archive_overlays", {})
    parsed_overlays: dict[str, str] = {}
    if not isinstance(overlays, dict):
        errors.append(
            _error(
                "invalid_config", "archive_overlays", "must be a path-to-path object"
            )
        )
    else:
        folded_destinations: set[str] = set()
        for supplied_destination, supplied_source in overlays.items():
            destination, destination_errors = _safe_relative_path(
                supplied_destination,
                location=f"archive_overlays.{supplied_destination}",
            )
            source, source_errors = _safe_relative_path(
                supplied_source,
                location=f"archive_overlays.{supplied_destination}",
            )
            errors.extend(destination_errors)
            errors.extend(source_errors)
            if destination is None or source is None:
                continue
            if destination in GENERATED_NAMES or destination == source:
                errors.append(
                    _error(
                        "invalid_config",
                        f"archive_overlays.{destination}",
                        "overlay destination must be distinct from source and control files",
                    )
                )
            errors.extend(_hard_path_errors(destination))
            folded = _portable_path_key(destination)
            if folded in folded_destinations:
                errors.append(
                    _error(
                        "invalid_config",
                        f"archive_overlays.{destination}",
                        "overlay destinations must not case-collide",
                    )
                )
            folded_destinations.add(folded)
            parsed_overlays[destination] = source
        if list(overlays) != sorted(overlays):
            errors.append(
                _error(
                    "invalid_config", "archive_overlays", "destinations must be sorted"
                )
            )
    normalized["archive_overlays"] = dict(sorted(parsed_overlays.items()))

    disclosures = document.get("approved_private_url_disclosures", [])
    if not isinstance(disclosures, list):
        errors.append(
            _error(
                "invalid_config", "approved_private_url_disclosures", "must be an array"
            )
        )
        disclosures = []
    parsed_disclosures: list[str] = []
    for index, item in enumerate(disclosures):
        candidate, item_errors = _safe_relative_path(
            item, location=f"approved_private_url_disclosures[{index}]"
        )
        errors.extend(item_errors)
        if candidate is not None:
            if not _is_disclosure_path(candidate):
                errors.append(
                    _error(
                        "invalid_config",
                        f"approved_private_url_disclosures[{index}]",
                        "approved file name must identify an attribution or disclosure",
                    )
                )
            parsed_disclosures.append(candidate)
    if parsed_disclosures != sorted(set(parsed_disclosures)):
        errors.append(
            _error(
                "invalid_config",
                "approved_private_url_disclosures",
                "values must be unique and sorted",
            )
        )
    normalized["approved_private_url_disclosures"] = parsed_disclosures

    binaries = document.get("reviewed_binaries", {})
    parsed_binaries: dict[str, str] = {}
    if not isinstance(binaries, dict):
        errors.append(
            _error(
                "invalid_config",
                "reviewed_binaries",
                "must be a path-to-SHA-256 object",
            )
        )
    else:
        for supplied_path, digest in binaries.items():
            candidate, item_errors = _safe_relative_path(
                supplied_path, location=f"reviewed_binaries.{supplied_path}"
            )
            errors.extend(item_errors)
            if (
                not isinstance(digest, str)
                or re.fullmatch(r"[0-9a-f]{64}", digest) is None
            ):
                errors.append(
                    _error(
                        "invalid_config",
                        f"reviewed_binaries.{supplied_path}",
                        "reviewed binary digest must be lowercase SHA-256",
                    )
                )
            elif candidate is not None:
                parsed_binaries[candidate] = digest
    normalized["reviewed_binaries"] = dict(sorted(parsed_binaries.items()))

    limits, limit_errors = _validate_limits(document.get("limits", {}), path="limits")
    errors.extend(limit_errors)
    normalized["limits"] = limits
    return (normalized if not errors else None), _sorted_errors(errors)


def _run_git(
    repo_root: Path, arguments: Sequence[str]
) -> subprocess.CompletedProcess[bytes]:
    environment = dict(os.environ)
    exact_overrides = {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_GLOBAL",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_CONFIG_SYSTEM",
        "GIT_DIR",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_GRAFT_FILE",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_REPLACE_REF_BASE",
        "GIT_SHALLOW_FILE",
        "GIT_WORK_TREE",
    }
    for name in list(environment):
        if name in exact_overrides or name.startswith(
            ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
        ):
            environment.pop(name, None)
    # Release provenance is derived only from the selected repository. Host
    # configuration must not redirect Git or inject an alternate object store.
    environment["GIT_LITERAL_PATHSPECS"] = "1"
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    # `git status` ordinarily refreshes cached stat data in the real index.
    # Release inspection is read-only, so prohibit optional Git writes even
    # when the caller explicitly enabled them in its environment.
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(
        ["git", "-C", str(repo_root), *arguments],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )


def _git_snapshot(repo_root: Path) -> tuple[dict[str, Any] | None, list[Error]]:
    try:
        top = _run_git(repo_root, ["rev-parse", "--show-toplevel"])
    except (OSError, subprocess.TimeoutExpired):
        return None, [_error("git_unavailable", ".", "Git is unavailable or timed out")]
    if top.returncode != 0:
        return None, [
            _error("not_git_repository", ".", "release root must be a Git worktree")
        ]
    try:
        discovered = Path(os.fsdecode(top.stdout.strip())).resolve(strict=True)
        expected = repo_root.resolve(strict=True)
    except OSError:
        return None, [
            _error("not_git_repository", ".", "release root cannot be resolved")
        ]
    if discovered != expected:
        return None, [
            _error("wrong_git_root", ".", "repo_root must be the Git worktree root")
        ]

    status = _run_git(
        repo_root,
        [
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignore-submodules=none",
        ],
    )
    if status.returncode != 0:
        return None, [
            _error("git_status_failed", ".", "Git status could not be evaluated")
        ]
    if status.stdout:
        entries = [item for item in status.stdout.split(b"\x00") if item]
        paths: list[str] = []
        for entry in entries[:20]:
            decoded = os.fsdecode(entry)
            paths.append(decoded[3:] if len(decoded) > 3 else decoded)
        suffix = "" if len(entries) <= 20 else f" (+{len(entries) - 20} more)"
        return None, [
            _error(
                "dirty_repository",
                ".",
                "tracked/untracked changes must be resolved before release: "
                + ", ".join(paths)
                + suffix,
            )
        ]

    head = _run_git(repo_root, ["rev-parse", "HEAD"])
    tracked = _run_git(repo_root, ["ls-files", "--stage", "-z"])
    if head.returncode != 0 or tracked.returncode != 0:
        return None, [
            _error(
                "git_snapshot_failed", ".", "Git HEAD/tracked files could not be read"
            )
        ]
    commit = head.stdout.decode("ascii", "strict").strip().lower()
    if re.fullmatch(r"[0-9a-f]{40,64}", commit) is None:
        return None, [
            _error("git_snapshot_failed", ".", "Git HEAD is not a recognized object ID")
        ]
    tracked_modes: dict[str, str] = {}
    tracked_oids: dict[str, str] = {}
    for record in tracked.stdout.split(b"\x00"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            raw_mode, raw_object_id, raw_stage = header.split(b" ")
            mode = raw_mode.decode("ascii")
            object_id = raw_object_id.decode("ascii").lower()
            stage = raw_stage.decode("ascii")
            path = os.fsdecode(raw_path)
        except (ValueError, UnicodeDecodeError):
            return None, [
                _error(
                    "git_snapshot_failed", ".", "Git index metadata could not be parsed"
                )
            ]
        if stage != "0" or path in tracked_modes:
            return None, [
                _error(
                    "git_snapshot_failed",
                    path,
                    "Git index contains an unmerged or duplicate path",
                )
            ]
        if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", object_id) is None:
            return None, [
                _error("git_snapshot_failed", path, "Git index blob ID is invalid")
            ]
        tracked_modes[path] = mode
        tracked_oids[path] = object_id
    return {
        "commit": commit,
        "tracked_paths": sorted(tracked_modes),
        "tracked_modes": dict(sorted(tracked_modes.items())),
        "tracked_oids": dict(sorted(tracked_oids.items())),
    }, []


def _matches(path: str, patterns: Sequence[str]) -> bool:
    for pattern in patterns:
        variants = {pattern}
        pending = [pattern]
        while pending:
            candidate = pending.pop()
            offset = 0
            while True:
                index = candidate.find("**/", offset)
                if index < 0:
                    break
                shortened = candidate[:index] + candidate[index + 3 :]
                if shortened not in variants:
                    variants.add(shortened)
                    pending.append(shortened)
                offset = index + 3
        if any(fnmatch.fnmatchcase(path, candidate) for candidate in variants):
            return True
    return False


def _selected(path: str, config: Mapping[str, Any]) -> bool:
    included = path in config["include_files"]
    included = included or any(
        path == root or path.startswith(root + "/") for root in config["include_roots"]
    )
    included = included or _matches(path, config["include_globs"])
    return included and not _matches(path, config["exclude_globs"])


def _read_source_file(
    candidate: Path, before: os.stat_result, *, path: str, limit: int
) -> tuple[bytes | None, Error | None]:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(candidate, flags)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            return None, _error(
                "special_file", path, "opened source is not a regular file"
            )
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            return None, _error(
                "source_changed", path, "file identity changed while opening"
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                return None, _error(
                    "file_size_limit", path, "file exceeds configured per-file limit"
                )
        data = b"".join(chunks)
    except OSError:
        return None, _error(
            "unreadable_file",
            path,
            "tracked file cannot be read without following links",
        )
    finally:
        if descriptor is not None:
            os.close(descriptor)
    try:
        after = candidate.lstat()
    except OSError:
        return None, _error("source_changed", path, "file disappeared while being read")
    stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
        return None, _error(
            "source_changed", path, "file metadata changed while being read"
        )
    if len(data) != before.st_size:
        return None, _error(
            "source_changed", path, "file size changed while being read"
        )
    return data, None


def _collect_payload(
    repo_root: Path,
    config: Mapping[str, Any],
    tracked_paths: Sequence[str],
    tracked_modes: Mapping[str, str],
    tracked_oids: Mapping[str, str],
) -> tuple[dict[str, bytes] | None, dict[str, int] | None, list[Error]]:
    errors: list[Error] = []
    payload: dict[str, bytes] = {}
    archive_modes: dict[str, int] = {}
    limits = config["limits"]
    selected_paths = [path for path in tracked_paths if _selected(path, config)]
    if not selected_paths:
        errors.append(
            _error("empty_artifact", ".", "allowlist selected no tracked files")
        )
    if len(selected_paths) > limits["max_files"]:
        errors.append(
            _error(
                "file_count_limit", ".", "selected file count exceeds configured limit"
            )
        )
        return None, None, errors

    total = 0
    root = repo_root.resolve(strict=True)
    approvals = frozenset(config["approved_private_url_disclosures"])
    reviewed = config["reviewed_binaries"]
    portable_paths: dict[str, str] = {}
    for raw_path in selected_paths:
        path, path_errors = _safe_relative_path(raw_path, location=raw_path)
        errors.extend(path_errors)
        if path is None:
            continue
        portable_key = _portable_path_key(path)
        prior_path = portable_paths.get(portable_key)
        if prior_path is not None:
            errors.append(
                _error(
                    "duplicate_entry",
                    path,
                    f"release path collides with {prior_path} after portable normalization",
                )
            )
            continue
        portable_paths[portable_key] = path
        errors.extend(_hard_path_errors(path))
        candidate = repo_root / path
        try:
            metadata = candidate.lstat()
        except OSError:
            errors.append(
                _error("unreadable_file", path, "tracked file cannot be inspected")
            )
            continue
        if stat.S_ISLNK(metadata.st_mode):
            errors.append(
                _error("symlink", path, "symlinks cannot enter a release artifact")
            )
            continue
        if not stat.S_ISREG(metadata.st_mode):
            errors.append(
                _error(
                    "special_file",
                    path,
                    "device, directory, and special files are rejected",
                )
            )
            continue
        git_mode = tracked_modes.get(path)
        if git_mode == "100644":
            archive_modes[path] = 0o644
        elif git_mode == "100755":
            archive_modes[path] = 0o755
        else:
            errors.append(
                _error(
                    "unsupported_git_mode",
                    path,
                    "release files must be regular Git blobs with mode 100644 or 100755",
                )
            )
            continue
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(root)
        except (OSError, ValueError):
            errors.append(
                _error("path_escape", path, "file resolves outside the release root")
            )
            continue
        if metadata.st_size > limits["max_file_bytes"]:
            errors.append(
                _error(
                    "file_size_limit", path, "file exceeds configured per-file limit"
                )
            )
            continue
        data, read_error = _read_source_file(
            candidate,
            metadata,
            path=path,
            limit=limits["max_file_bytes"],
        )
        if read_error is not None:
            errors.append(read_error)
            continue
        assert data is not None
        expected_oid = tracked_oids.get(path, "")
        if _git_blob_oid(data, expected_oid) != expected_oid:
            errors.append(
                _error(
                    "source_blob_mismatch",
                    path,
                    "worktree bytes do not match the clean Git index blob",
                )
            )
            continue
        total += len(data)
        if total > limits["max_total_bytes"]:
            errors.append(
                _error(
                    "total_size_limit",
                    ".",
                    "selected bytes exceed configured total limit",
                )
            )
            break
        errors.extend(
            _scan_content(
                path,
                data,
                approved_private_urls=approvals,
                reviewed_binaries=reviewed,
            )
        )
        payload[path] = data

    missing_disclosures = approvals.difference(payload)
    for path in sorted(missing_disclosures):
        errors.append(
            _error(
                "invalid_config",
                path,
                "approved disclosure is not selected into the artifact",
            )
        )
    missing_binaries = set(reviewed).difference(payload)
    for path in sorted(missing_binaries):
        errors.append(
            _error(
                "invalid_config",
                path,
                "reviewed binary is not selected into the artifact",
            )
        )
    if errors:
        return None, None, _sorted_errors(errors)
    return payload, archive_modes, []


def _apply_archive_overlays(
    payload: Mapping[str, bytes],
    modes: Mapping[str, int],
    config: Mapping[str, Any],
) -> tuple[dict[str, bytes] | None, dict[str, int] | None, list[Error]]:
    """Materialize reviewed Git-bound files at distribution-only archive paths."""

    expanded = dict(payload)
    expanded_modes = dict(modes)
    errors: list[Error] = []
    folded = {_portable_path_key(path) for path in expanded}
    approvals = frozenset(config["approved_private_url_disclosures"])
    reviewed = config["reviewed_binaries"]
    for destination, source in config["archive_overlays"].items():
        data = payload.get(source)
        source_mode = modes.get(source)
        if data is None or source_mode not in {0o644, 0o755}:
            errors.append(
                _error(
                    "invalid_config",
                    destination,
                    f"overlay source is not selected as a regular release file: {source}",
                )
            )
            continue
        if destination in expanded:
            if (
                expanded[destination] != data
                or expanded_modes.get(destination) != source_mode
            ):
                errors.append(
                    _error(
                        "overlay_drift",
                        destination,
                        "existing distribution file differs from its reviewed overlay source",
                    )
                )
            continue
        if _portable_path_key(destination) in folded:
            errors.append(
                _error(
                    "duplicate_entry",
                    destination,
                    "overlay case-collides with a selected archive path",
                )
            )
            continue
        errors.extend(_hard_path_errors(destination))
        errors.extend(
            _scan_content(
                destination,
                data,
                approved_private_urls=approvals,
                reviewed_binaries=reviewed,
            )
        )
        expanded[destination] = data
        expanded_modes[destination] = source_mode
        folded.add(_portable_path_key(destination))

    limits = config["limits"]
    if len(expanded) > limits["max_files"]:
        errors.append(
            _error("file_count_limit", ".", "overlay-expanded file count exceeds limit")
        )
    if sum(len(data) for data in expanded.values()) > limits["max_total_bytes"]:
        errors.append(
            _error("total_size_limit", ".", "overlay-expanded bytes exceed limit")
        )
    if errors:
        return None, None, _sorted_errors(errors)
    return expanded, expanded_modes, []


def _zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    moment = datetime.fromtimestamp(epoch, timezone.utc)
    return (
        moment.year,
        moment.month,
        moment.day,
        moment.hour,
        moment.minute,
        moment.second // 2 * 2,
    )


def _zip_dos_timestamp(
    value: tuple[int, int, int, int, int, int],
) -> tuple[int, int]:
    year, month, day, hour, minute, second = value
    dos_time = (hour << 11) | (minute << 5) | (second // 2)
    dos_date = ((year - 1980) << 9) | (month << 5) | day
    return dos_time, dos_date


def _zip_info(path: str, epoch: int, mode: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, _zip_datetime(epoch))
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.flag_bits = 0
    info.extra = b""
    info.comment = b""
    return info


def _artifact_bytes(
    payload: Mapping[str, bytes],
    *,
    modes: Mapping[str, int],
    commit: str,
    source_date_epoch: int,
    config: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    files = [
        {
            "mode": f"{modes[path]:04o}",
            "path": path,
            "sha256": _sha256(data),
            "size": len(data),
        }
        for path, data in sorted(payload.items())
    ]
    manifest = {
        "artifact_format": "zip",
        "files": files,
        "policy": {
            "approved_private_url_disclosures": config[
                "approved_private_url_disclosures"
            ],
            "archive_overlays": config["archive_overlays"],
            "reviewed_binaries": config["reviewed_binaries"],
        },
        "schema_version": SCHEMA_VERSION,
        "source_commit": commit,
        "source_date_epoch": source_date_epoch,
    }
    manifest_bytes = _canonical_json(manifest)
    sums = {path: _sha256(data) for path, data in payload.items()}
    sums[MANIFEST_NAME] = _sha256(manifest_bytes)
    checksum_bytes = "".join(
        f"{digest}  {path}\n" for path, digest in sorted(sums.items())
    ).encode("utf-8")
    all_files = dict(payload)
    all_files[MANIFEST_NAME] = manifest_bytes
    all_files[CHECKSUMS_NAME] = checksum_bytes

    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer, mode="w", compression=zipfile.ZIP_STORED, allowZip64=False
    ) as archive:
        archive.comment = b""
        for path, data in sorted(all_files.items()):
            mode = modes[path] if path in modes else 0o644
            archive.writestr(_zip_info(path, source_date_epoch, mode), data)
    return buffer.getvalue(), manifest


def _preflight_zip_structure(data: bytes, *, label: str) -> list[Error]:
    """Bound the central directory before ``zipfile`` allocates entry objects."""

    size = len(data)
    if size < 22:
        return [_error("invalid_archive", label, "ZIP is shorter than its end record")]
    magic = data[:4]
    tail_offset = max(0, size - 65557)
    tail = data[tail_offset:]
    if magic != b"PK\x03\x04":
        return [
            _error(
                "invalid_archive",
                label,
                "self-extracting/noncanonical ZIP prefix is rejected",
            )
        ]
    marker = tail.rfind(b"PK\x05\x06")
    if marker < 0 or marker + 22 > len(tail):
        return [_error("invalid_archive", label, "ZIP end record is missing")]
    try:
        (
            _signature,
            disk_number,
            central_disk,
            disk_entries,
            total_entries,
            central_size,
            central_offset,
            comment_size,
        ) = struct.unpack_from("<4s4H2LH", tail, marker)
    except struct.error:
        return [_error("invalid_archive", label, "ZIP end record is malformed")]
    eocd_offset = tail_offset + marker
    errors: list[Error] = []
    if marker + 22 + comment_size != len(tail):
        errors.append(
            _error("noncanonical_archive", label, "ZIP has a comment or trailing bytes")
        )
    if disk_number or central_disk or disk_entries != total_entries:
        errors.append(
            _error("unsupported_archive_type", label, "multi-disk ZIP is rejected")
        )
    if (
        total_entries in {0, 0xFFFF}
        or central_size == 0xFFFFFFFF
        or central_offset == 0xFFFFFFFF
    ):
        errors.append(
            _error(
                "unsupported_archive_type", label, "empty/ZIP64 artifact is rejected"
            )
        )
    if total_entries > DEFAULT_LIMITS["max_files"] + len(GENERATED_NAMES):
        errors.append(
            _error(
                "file_count_limit", label, "central-directory entry count exceeds limit"
            )
        )
    if central_offset + central_size != eocd_offset:
        errors.append(
            _error(
                "noncanonical_archive",
                label,
                "central directory bounds are inconsistent",
            )
        )
    return _sorted_errors(errors)


def _read_member_limited(
    archive: zipfile.ZipFile, info: zipfile.ZipInfo, *, limit: int
) -> tuple[bytes | None, Error | None]:
    chunks: list[bytes] = []
    total = 0
    try:
        with archive.open(info, "r") as source:
            while True:
                chunk = source.read(min(65536, limit + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > limit:
                    return None, _error(
                        "file_size_limit",
                        info.filename,
                        "expanded member exceeds limit",
                    )
    except (OSError, RuntimeError, zipfile.BadZipFile):
        return None, _error(
            "corrupt_member", info.filename, "archive member cannot be read safely"
        )
    return b"".join(chunks), None


def _validate_local_layout(
    artifact_bytes: bytes,
    infos: Sequence[zipfile.ZipInfo],
    *,
    central_offset: int,
    label: str,
) -> list[Error]:
    """Reject hidden gaps, overlapping records, and local/central disagreement."""

    errors: list[Error] = []
    expected_offset = 0
    try:
        with io.BytesIO(artifact_bytes) as source:
            for info in infos:
                if info.header_offset != expected_offset:
                    errors.append(
                        _error(
                            "noncanonical_archive",
                            info.filename,
                            "local file records have a gap, overlap, or reordered offset",
                        )
                    )
                    expected_offset = info.header_offset
                source.seek(info.header_offset)
                header = source.read(30)
                if len(header) != 30:
                    errors.append(
                        _error(
                            "invalid_archive",
                            info.filename,
                            "local header is truncated",
                        )
                    )
                    continue
                try:
                    (
                        signature,
                        _version,
                        flags,
                        compression,
                        local_time,
                        local_date,
                        crc,
                        compressed_size,
                        file_size,
                        name_size,
                        extra_size,
                    ) = struct.unpack("<4s5H3L2H", header)
                except struct.error:
                    errors.append(
                        _error(
                            "invalid_archive",
                            info.filename,
                            "local header is malformed",
                        )
                    )
                    continue
                raw_name = source.read(name_size)
                extra = source.read(extra_size)
                encoding = "utf-8" if flags & 0x800 else "cp437"
                try:
                    local_name = raw_name.decode(encoding)
                except UnicodeDecodeError:
                    local_name = ""
                if signature != b"PK\x03\x04" or local_name != info.filename:
                    errors.append(
                        _error(
                            "noncanonical_archive",
                            info.filename,
                            "local and central names/signatures differ",
                        )
                    )
                if extra or extra_size:
                    errors.append(
                        _error(
                            "noncanonical_archive",
                            info.filename,
                            "local extra data is rejected",
                        )
                    )
                central_time, central_date = _zip_dos_timestamp(info.date_time)
                if (local_time, local_date) != (central_time, central_date):
                    errors.append(
                        _error(
                            "timestamp_mismatch",
                            info.filename,
                            "local-header timestamp differs from the central directory",
                        )
                    )
                if (
                    flags != info.flag_bits
                    or compression != info.compress_type
                    or crc != info.CRC
                    or compressed_size != info.compress_size
                    or file_size != info.file_size
                ):
                    errors.append(
                        _error(
                            "noncanonical_archive",
                            info.filename,
                            "local and central metadata differ",
                        )
                    )
                expected_offset = (
                    info.header_offset + 30 + name_size + extra_size + compressed_size
                )
    except (OSError, ValueError):
        return [_error("unreadable_artifact", label, "local ZIP layout cannot be read")]
    if expected_offset != central_offset:
        errors.append(
            _error(
                "noncanonical_archive",
                label,
                "unreferenced bytes exist between local records and central directory",
            )
        )
    return _sorted_errors(errors)


def _parse_policy(
    manifest: Any,
) -> tuple[frozenset[str], dict[str, str], dict[str, str], list[Error]]:
    errors: list[Error] = []
    policy = manifest.get("policy") if isinstance(manifest, dict) else None
    if not isinstance(policy, dict):
        return (
            frozenset(),
            {},
            {},
            [_error("invalid_manifest", MANIFEST_NAME, "policy must be an object")],
        )
    approvals = policy.get("approved_private_url_disclosures")
    if not isinstance(approvals, list):
        errors.append(
            _error(
                "invalid_manifest", MANIFEST_NAME, "disclosure policy must be an array"
            )
        )
        approvals = []
    parsed_approvals: list[str] = []
    for item in approvals:
        path, path_errors = _safe_relative_path(item, location=MANIFEST_NAME)
        errors.extend(path_errors)
        if path is not None:
            if not _is_disclosure_path(path):
                errors.append(
                    _error(
                        "invalid_manifest",
                        path,
                        "approved URL exception is not a disclosure file",
                    )
                )
            parsed_approvals.append(path)
    if parsed_approvals != sorted(set(parsed_approvals)):
        errors.append(
            _error(
                "invalid_manifest",
                MANIFEST_NAME,
                "disclosure policy must be sorted and unique",
            )
        )

    binaries = policy.get("reviewed_binaries")
    if not isinstance(binaries, dict):
        errors.append(
            _error(
                "invalid_manifest", MANIFEST_NAME, "reviewed_binaries must be an object"
            )
        )
        binaries = {}
    parsed_binaries: dict[str, str] = {}
    for supplied_path, digest in binaries.items():
        path, path_errors = _safe_relative_path(supplied_path, location=MANIFEST_NAME)
        errors.extend(path_errors)
        if (
            path is not None
            and isinstance(digest, str)
            and re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            parsed_binaries[path] = digest
        else:
            errors.append(
                _error(
                    "invalid_manifest",
                    str(supplied_path),
                    "invalid reviewed binary record",
                )
            )
    if list(binaries) != sorted(binaries):
        errors.append(
            _error(
                "invalid_manifest", MANIFEST_NAME, "reviewed binaries must be sorted"
            )
        )

    overlays = policy.get("archive_overlays")
    if not isinstance(overlays, dict):
        errors.append(
            _error(
                "invalid_manifest", MANIFEST_NAME, "archive_overlays must be an object"
            )
        )
        overlays = {}
    parsed_overlays: dict[str, str] = {}
    folded: set[str] = set()
    for supplied_destination, supplied_source in overlays.items():
        destination, destination_errors = _safe_relative_path(
            supplied_destination, location=MANIFEST_NAME
        )
        source, source_errors = _safe_relative_path(
            supplied_source, location=MANIFEST_NAME
        )
        errors.extend(destination_errors)
        errors.extend(source_errors)
        if destination is None or source is None:
            continue
        if destination in GENERATED_NAMES or destination == source:
            errors.append(
                _error("invalid_manifest", destination, "invalid archive overlay")
            )
        if _portable_path_key(destination) in folded:
            errors.append(
                _error(
                    "duplicate_entry", destination, "overlay destinations case-collide"
                )
            )
        folded.add(_portable_path_key(destination))
        parsed_overlays[destination] = source
    if list(overlays) != sorted(overlays):
        errors.append(
            _error("invalid_manifest", MANIFEST_NAME, "archive overlays must be sorted")
        )
    return frozenset(parsed_approvals), parsed_binaries, parsed_overlays, errors


def _validate_manifest(
    manifest_bytes: bytes, payload: Mapping[str, bytes]
) -> tuple[
    dict[str, Any] | None,
    frozenset[str],
    dict[str, str],
    dict[str, str],
    list[Error],
]:
    errors: list[Error] = []
    try:
        manifest = _strict_json_loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return (
            None,
            frozenset(),
            {},
            {},
            [
                _error(
                    "invalid_manifest",
                    MANIFEST_NAME,
                    "manifest is not valid UTF-8 JSON",
                )
            ],
        )
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != SCHEMA_VERSION
    ):
        return (
            None,
            frozenset(),
            {},
            {},
            [
                _error(
                    "invalid_manifest",
                    MANIFEST_NAME,
                    "manifest schema_version must be 1",
                )
            ],
        )
    if _canonical_json(manifest) != manifest_bytes:
        errors.append(
            _error(
                "noncanonical_manifest", MANIFEST_NAME, "manifest JSON is not canonical"
            )
        )
    if manifest.get("artifact_format") != "zip":
        errors.append(
            _error("invalid_manifest", MANIFEST_NAME, "artifact_format must be zip")
        )
    commit = manifest.get("source_commit")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40,64}", commit) is None:
        errors.append(
            _error("invalid_manifest", MANIFEST_NAME, "source_commit is invalid")
        )
    epoch = manifest.get("source_date_epoch")
    if (
        not isinstance(epoch, int)
        or isinstance(epoch, bool)
        or epoch < MIN_ZIP_EPOCH
        or epoch > MAX_ZIP_EPOCH
    ):
        errors.append(
            _error(
                "invalid_manifest",
                MANIFEST_NAME,
                "source_date_epoch is outside ZIP range",
            )
        )

    files = manifest.get("files")
    records: dict[str, tuple[int, str, int]] = {}
    if not isinstance(files, list):
        errors.append(
            _error("invalid_manifest", MANIFEST_NAME, "files must be an array")
        )
        files = []
    encountered: list[str] = []
    for record in files:
        if not isinstance(record, dict) or set(record) != {
            "mode",
            "path",
            "sha256",
            "size",
        }:
            errors.append(
                _error(
                    "invalid_manifest", MANIFEST_NAME, "file record shape is invalid"
                )
            )
            continue
        path, path_errors = _safe_relative_path(
            record.get("path"), location=MANIFEST_NAME
        )
        errors.extend(path_errors)
        size = record.get("size")
        digest = record.get("sha256")
        raw_mode = record.get("mode")
        if path is None:
            continue
        if path in GENERATED_NAMES:
            errors.append(
                _error(
                    "invalid_manifest",
                    path,
                    "generated control files cannot list themselves",
                )
            )
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            errors.append(_error("invalid_manifest", path, "manifest size is invalid"))
            continue
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            errors.append(
                _error("invalid_manifest", path, "manifest SHA-256 is invalid")
            )
            continue
        if raw_mode not in {"0644", "0755"}:
            errors.append(
                _error("invalid_manifest", path, "manifest mode must be 0644 or 0755")
            )
            continue
        if path in records:
            errors.append(
                _error("duplicate_entry", path, "manifest path appears more than once")
            )
        records[path] = (size, digest, int(raw_mode, 8))
        encountered.append(path)
    if encountered != sorted(encountered):
        errors.append(
            _error(
                "noncanonical_manifest", MANIFEST_NAME, "file records must be sorted"
            )
        )
    actual_names = set(payload).difference(GENERATED_NAMES)
    if set(records) != actual_names:
        errors.append(
            _error(
                "manifest_mismatch",
                MANIFEST_NAME,
                "manifest paths do not match payload",
            )
        )
    for path, (size, digest, _mode) in records.items():
        data = payload.get(path)
        if data is not None and (len(data) != size or _sha256(data) != digest):
            errors.append(
                _error(
                    "manifest_mismatch",
                    path,
                    "payload does not match manifest size/SHA-256",
                )
            )

    approvals, binaries, overlays, policy_errors = _parse_policy(manifest)
    errors.extend(policy_errors)
    if not approvals.issubset(actual_names):
        errors.append(
            _error(
                "invalid_manifest",
                MANIFEST_NAME,
                "approved disclosure is absent from payload",
            )
        )
    if not set(binaries).issubset(actual_names):
        errors.append(
            _error(
                "invalid_manifest",
                MANIFEST_NAME,
                "reviewed binary is absent from payload",
            )
        )
    for path, digest in binaries.items():
        if path in payload and _sha256(payload[path]) != digest:
            errors.append(
                _error(
                    "manifest_mismatch",
                    path,
                    "reviewed binary digest does not match payload",
                )
            )
    for destination, source in overlays.items():
        if destination not in actual_names or source not in actual_names:
            errors.append(
                _error(
                    "invalid_manifest",
                    destination,
                    "archive overlay paths are absent from payload",
                )
            )
        elif payload[destination] != payload[source]:
            errors.append(
                _error(
                    "manifest_mismatch",
                    destination,
                    "archive overlay differs from its Git-bound source",
                )
            )
    return manifest, approvals, binaries, overlays, _sorted_errors(errors)


def _validate_checksums(
    checksum_bytes: bytes, payload: Mapping[str, bytes]
) -> list[Error]:
    try:
        text = checksum_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return [
            _error("invalid_checksums", CHECKSUMS_NAME, "checksum file is not UTF-8")
        ]
    parsed: dict[str, str] = {}
    errors: list[Error] = []
    lines = text.splitlines(keepends=True)
    if text and (not lines or not lines[-1].endswith("\n")):
        errors.append(
            _error(
                "invalid_checksums",
                CHECKSUMS_NAME,
                "checksum file needs a final newline",
            )
        )
    encountered: list[str] = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)\n", line)
        if match is None:
            errors.append(
                _error("invalid_checksums", CHECKSUMS_NAME, "malformed checksum line")
            )
            continue
        digest, raw_path = match.groups()
        path, path_errors = _safe_relative_path(raw_path, location=CHECKSUMS_NAME)
        errors.extend(path_errors)
        if path is None:
            continue
        if path == CHECKSUMS_NAME or path in parsed:
            errors.append(
                _error(
                    "invalid_checksums",
                    path,
                    "checksum target is self-referential or duplicate",
                )
            )
        parsed[path] = digest
        encountered.append(path)
    expected_names = set(payload).difference({CHECKSUMS_NAME})
    if set(parsed) != expected_names:
        errors.append(
            _error(
                "checksum_mismatch",
                CHECKSUMS_NAME,
                "checksum paths do not match archive",
            )
        )
    if encountered != sorted(encountered):
        errors.append(
            _error("invalid_checksums", CHECKSUMS_NAME, "checksum lines must be sorted")
        )
    for path, digest in parsed.items():
        data = payload.get(path)
        if data is not None and _sha256(data) != digest:
            errors.append(
                _error(
                    "checksum_mismatch", path, "archive member SHA-256 does not match"
                )
            )
    return _sorted_errors(errors)


def _validate_public_marketplace(
    payload: Mapping[str, bytes], overlays: Mapping[str, str]
) -> list[Error]:
    """Prove that an injected marketplace root contains only the audited distribution."""

    if (
        PUBLIC_MARKETPLACE_PATH not in payload
        and PUBLIC_MARKETPLACE_PATH not in overlays
    ):
        return []
    errors: list[Error] = []
    if overlays.get(PUBLIC_MARKETPLACE_PATH) != PUBLIC_MARKETPLACE_TEMPLATE:
        errors.append(
            _error(
                "unsafe_marketplace_source",
                PUBLIC_MARKETPLACE_PATH,
                "public marketplace manifest must be injected from its reviewed template",
            )
        )
    template = payload.get(PUBLIC_MARKETPLACE_TEMPLATE)
    marketplace_bytes = payload.get(PUBLIC_MARKETPLACE_PATH)
    plugin_bytes = payload.get(".claude-plugin/plugin.json")
    if template is None or marketplace_bytes is None or plugin_bytes is None:
        errors.append(
            _error(
                "incomplete_marketplace",
                PUBLIC_MARKETPLACE_PATH,
                "marketplace, template, and plugin manifest must all be present",
            )
        )
        return _sorted_errors(errors)
    if marketplace_bytes != template:
        errors.append(
            _error(
                "marketplace_template_drift",
                PUBLIC_MARKETPLACE_PATH,
                "marketplace bytes differ from the reviewed Git-bound template",
            )
        )
    try:
        marketplace = _strict_json_loads(marketplace_bytes.decode("utf-8"))
        plugin = _strict_json_loads(plugin_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        errors.append(
            _error(
                "invalid_marketplace",
                PUBLIC_MARKETPLACE_PATH,
                "marketplace metadata is invalid",
            )
        )
        return _sorted_errors(errors)
    entries = marketplace.get("plugins") if isinstance(marketplace, dict) else None
    entry = entries[0] if isinstance(entries, list) and len(entries) == 1 else None
    plugin_name = plugin.get("name") if isinstance(plugin, dict) else None
    plugin_version = plugin.get("version") if isinstance(plugin, dict) else None
    marketplace_version = (
        marketplace.get("version") if isinstance(marketplace, dict) else None
    )
    if not isinstance(entry, dict):
        errors.append(
            _error(
                "invalid_marketplace",
                PUBLIC_MARKETPLACE_PATH,
                "exactly one plugin is required",
            )
        )
    else:
        if entry.get("source") != "./":
            errors.append(
                _error(
                    "unsafe_marketplace_source",
                    PUBLIC_MARKETPLACE_PATH,
                    "artifact marketplace plugin source must be the audited artifact root",
                )
            )
        if entry.get("name") != plugin_name:
            errors.append(
                _error(
                    "marketplace_name_drift",
                    PUBLIC_MARKETPLACE_PATH,
                    "plugin names differ",
                )
            )
        if "version" in entry:
            errors.append(
                _error(
                    "duplicate_version_authority",
                    PUBLIC_MARKETPLACE_PATH,
                    "plugin.json must be the sole plugin-version authority",
                )
            )
    if (
        not isinstance(plugin_name, str)
        or not plugin_name
        or not isinstance(plugin_version, str)
        or not plugin_version
        or marketplace_version != plugin_version
    ):
        errors.append(
            _error(
                "version_drift",
                PUBLIC_MARKETPLACE_PATH,
                "marketplace and plugin metadata differ",
            )
        )
    live_paths = sorted(
        name
        for name in payload
        if name == "wiki"
        or name.startswith("wiki/")
        or name == ".raw"
        or name.startswith(".raw/")
        or name == ".vault-meta"
        or name.startswith(".vault-meta/")
    )
    if live_paths:
        errors.append(
            _error(
                "unsafe_marketplace_root",
                PUBLIC_MARKETPLACE_PATH,
                "artifact marketplace contains contributor/live-vault state",
            )
        )
    required = {
        ".claude-plugin/plugin.json",
        "claude_obsidian/__init__.py",
        "config/capabilities.json",
        "hooks/hooks.json",
        "scripts/claude-obsidian.py",
        "skills/wiki/SKILL.md",
        "templates/vault/.gitignore",
    }
    if CODEX_MANIFEST in payload or CODEX_HOOKS in payload:
        required.update((CODEX_MANIFEST, CODEX_HOOKS))
        if CODEX_MANIFEST in payload:
            try:
                codex = _strict_json_loads(payload[CODEX_MANIFEST].decode("utf-8"))
            except (UnicodeDecodeError, ValueError):
                codex = None
            errors.extend(validate_codex_manifest(codex, plugin))
    for missing in sorted(required.difference(payload)):
        errors.append(
            _error(
                "incomplete_marketplace",
                missing,
                "required plugin runtime file is absent",
            )
        )
    return _sorted_errors(errors)


def audit_artifact(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Audit an artifact without extracting it or trusting archive paths.

    Invalid or unsafe artifacts return ``ok: false`` with stable error codes;
    callers never need to catch malformed-archive exceptions.
    """

    artifact = Path(path)
    label = artifact.name or "artifact"
    errors: list[Error] = []
    try:
        metadata = artifact.lstat()
    except OSError:
        return _failure(
            "artifact_audit",
            [_error("missing_artifact", label, "artifact is missing")],
            artifact=label,
        )
    if stat.S_ISLNK(metadata.st_mode):
        return _failure(
            "artifact_audit",
            [_error("symlink", label, "artifact path cannot be a symlink")],
            artifact=label,
        )
    if not stat.S_ISREG(metadata.st_mode):
        return _failure(
            "artifact_audit",
            [_error("special_file", label, "artifact must be a regular file")],
            artifact=label,
        )
    if artifact.suffix.casefold() != ".zip":
        return _failure(
            "artifact_audit",
            [
                _error(
                    "unsupported_archive_type",
                    label,
                    "only .zip artifacts are supported",
                )
            ],
            artifact=label,
        )
    if metadata.st_size > DEFAULT_LIMITS["max_archive_bytes"]:
        return _failure(
            "artifact_audit",
            [_error("archive_size_limit", label, "archive exceeds safety limit")],
            artifact=label,
        )

    descriptor = -1
    try:
        descriptor = os.open(
            artifact,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
            metadata.st_dev,
            metadata.st_ino,
        ):
            raise OSError("artifact identity changed before snapshot")
        chunks: list[bytes] = []
        remaining = DEFAULT_LIMITS["max_archive_bytes"] + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        artifact_bytes = b"".join(chunks)
        after = os.fstat(descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_mode")
        if any(
            getattr(opened, field) != getattr(after, field) for field in stable_fields
        ):
            raise OSError("artifact changed while snapshot was read")
    except OSError:
        return _failure(
            "artifact_audit",
            [_error("unreadable_artifact", label, "artifact cannot be read")],
            artifact=label,
        )
    finally:
        if descriptor >= 0:
            os.close(descriptor)

    artifact_hash = hashlib.sha256(artifact_bytes)

    structure_errors = _preflight_zip_structure(artifact_bytes, label=label)
    if structure_errors:
        return _failure(
            "artifact_audit",
            structure_errors,
            artifact=label,
            sha256=artifact_hash.hexdigest(),
        )

    payload: dict[str, bytes] = {}
    infos: list[zipfile.ZipInfo] = []
    try:
        with zipfile.ZipFile(io.BytesIO(artifact_bytes), "r") as archive:
            if archive.comment:
                errors.append(
                    _error("noncanonical_archive", label, "ZIP comment must be empty")
                )
            infos = archive.infolist()
            if len(infos) > DEFAULT_LIMITS["max_files"] + len(GENERATED_NAMES):
                errors.append(
                    _error(
                        "file_count_limit", label, "archive entry count exceeds limit"
                    )
                )
            seen: set[str] = set()
            folded: set[str] = set()
            declared_total = 0
            for info in infos:
                name, path_errors = _safe_relative_path(
                    info.filename, location=info.filename
                )
                errors.extend(path_errors)
                if name is None:
                    continue
                if name in seen or _portable_path_key(name) in folded:
                    errors.append(
                        _error(
                            "duplicate_entry",
                            name,
                            "duplicate or case-colliding archive path",
                        )
                    )
                seen.add(name)
                folded.add(_portable_path_key(name))
                errors.extend(_hard_path_errors(name))
                if info.is_dir() or name.endswith("/"):
                    errors.append(
                        _error(
                            "special_file", name, "directory entries are not permitted"
                        )
                    )
                mode = info.external_attr >> 16
                file_type = stat.S_IFMT(mode)
                if file_type == stat.S_IFLNK:
                    errors.append(
                        _error("symlink", name, "archive symlinks are rejected")
                    )
                elif file_type not in {0, stat.S_IFREG}:
                    errors.append(
                        _error(
                            "special_file",
                            name,
                            "archive device/special entry is rejected",
                        )
                    )
                if info.flag_bits & 0x1:
                    errors.append(
                        _error(
                            "encrypted_entry",
                            name,
                            "encrypted ZIP entries are rejected",
                        )
                    )
                if info.flag_bits & ~0x800:
                    errors.append(
                        _error(
                            "noncanonical_archive",
                            name,
                            "unsupported ZIP general-purpose flags",
                        )
                    )
                if info.compress_type != zipfile.ZIP_STORED:
                    errors.append(
                        _error(
                            "unsupported_compression",
                            name,
                            "only stored entries are accepted",
                        )
                    )
                if info.extra or info.comment:
                    errors.append(
                        _error(
                            "noncanonical_archive",
                            name,
                            "entry extra/comment metadata must be empty",
                        )
                    )
                if info.file_size > DEFAULT_LIMITS["max_file_bytes"]:
                    errors.append(
                        _error("file_size_limit", name, "expanded member exceeds limit")
                    )
                declared_total += info.file_size
                if info.compress_size == 0 and info.file_size > 0:
                    errors.append(
                        _error(
                            "compression_bomb",
                            name,
                            "non-empty member has zero compressed size",
                        )
                    )
                elif (
                    info.compress_size
                    and info.file_size / info.compress_size
                    > DEFAULT_LIMITS["max_compression_ratio"]
                ):
                    errors.append(
                        _error(
                            "compression_bomb",
                            name,
                            "member compression ratio exceeds limit",
                        )
                    )
            if declared_total > DEFAULT_LIMITS["max_total_bytes"]:
                errors.append(
                    _error(
                        "total_size_limit",
                        label,
                        "expanded archive exceeds total limit",
                    )
                )

            errors.extend(
                _validate_local_layout(
                    artifact_bytes,
                    infos,
                    central_offset=archive.start_dir,
                    label=label,
                )
            )

            if not errors:
                actual_total = 0
                for info in infos:
                    data, read_error = _read_member_limited(
                        archive, info, limit=DEFAULT_LIMITS["max_file_bytes"]
                    )
                    if read_error is not None:
                        errors.append(read_error)
                        continue
                    assert data is not None
                    actual_total += len(data)
                    if actual_total > DEFAULT_LIMITS["max_total_bytes"]:
                        errors.append(
                            _error(
                                "total_size_limit",
                                label,
                                "expanded archive exceeds total limit",
                            )
                        )
                        break
                    payload[info.filename] = data
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile):
        errors.append(
            _error("invalid_archive", label, "file is not a valid bounded ZIP artifact")
        )

    if errors:
        return _failure(
            "artifact_audit",
            errors,
            artifact=label,
            sha256=artifact_hash.hexdigest(),
        )
    if set(GENERATED_NAMES).difference(payload):
        return _failure(
            "artifact_audit",
            [
                _error(
                    "missing_control_file",
                    label,
                    "manifest and checksum files are required",
                )
            ],
            artifact=label,
            sha256=artifact_hash.hexdigest(),
        )

    manifest, approvals, binaries, overlays, manifest_errors = _validate_manifest(
        payload[MANIFEST_NAME], payload
    )
    errors.extend(manifest_errors)
    errors.extend(_validate_checksums(payload[CHECKSUMS_NAME], payload))
    errors.extend(_validate_public_marketplace(payload, overlays))
    for name, data in payload.items():
        errors.extend(_hard_path_errors(name))
        errors.extend(
            _scan_content(
                name,
                data,
                approved_private_urls=approvals,
                reviewed_binaries=binaries,
            )
        )

    if manifest is not None and isinstance(manifest.get("source_date_epoch"), int):
        manifest_modes = {
            record["path"]: int(record["mode"], 8)
            for record in manifest.get("files", [])
            if isinstance(record, dict)
            and isinstance(record.get("path"), str)
            and record.get("mode") in {"0644", "0755"}
        }
        try:
            expected_time = _zip_datetime(manifest["source_date_epoch"])
        except (OverflowError, OSError, ValueError):
            expected_time = None
        if expected_time is not None:
            for info in infos:
                if info.date_time != expected_time:
                    errors.append(
                        _error(
                            "timestamp_mismatch",
                            info.filename,
                            "entry timestamp differs from manifest epoch",
                        )
                    )
                expected_mode = (
                    0o644
                    if info.filename in GENERATED_NAMES
                    else manifest_modes.get(info.filename)
                )
                if (
                    expected_mode is None
                    or info.create_system != 3
                    or (info.external_attr >> 16) != (stat.S_IFREG | expected_mode)
                ):
                    errors.append(
                        _error(
                            "permission_mismatch",
                            info.filename,
                            "entry Unix mode must exactly match its release manifest",
                        )
                    )
    if [info.filename for info in infos] != sorted(info.filename for info in infos):
        errors.append(
            _error("noncanonical_archive", label, "archive entries must be sorted")
        )

    if not errors and manifest is not None:
        manifest_modes = {
            record["path"]: int(record["mode"], 8) for record in manifest["files"]
        }
        policy = manifest["policy"]
        reconstructed, _ = _artifact_bytes(
            {
                name: data
                for name, data in payload.items()
                if name not in GENERATED_NAMES
            },
            modes=manifest_modes,
            commit=manifest["source_commit"],
            source_date_epoch=manifest["source_date_epoch"],
            config={
                "approved_private_url_disclosures": policy[
                    "approved_private_url_disclosures"
                ],
                "archive_overlays": policy["archive_overlays"],
                "reviewed_binaries": policy["reviewed_binaries"],
            },
        )
        try:
            current = artifact.lstat()
            identity_changed = (current.st_dev, current.st_ino) != (
                opened.st_dev,
                opened.st_ino,
            )
        except OSError:
            identity_changed = True
        if identity_changed:
            errors.append(
                _error(
                    "artifact_identity_changed",
                    label,
                    "artifact path changed during audit",
                )
            )
        if not hmac.compare_digest(reconstructed, artifact_bytes):
            errors.append(
                _error(
                    "noncanonical_archive",
                    label,
                    "archive bytes differ from the canonical deterministic encoding",
                )
            )

    if errors:
        return _failure(
            "artifact_audit",
            errors,
            artifact=label,
            sha256=artifact_hash.hexdigest(),
        )
    assert manifest is not None
    return {
        "ok": True,
        "kind": "artifact_audit",
        "artifact": label,
        "sha256": artifact_hash.hexdigest(),
        "source_commit": manifest["source_commit"],
        "source_date_epoch": manifest["source_date_epoch"],
        "summary": {
            "archive_bytes": len(artifact_bytes),
            "file_count": len(manifest["files"]),
            "payload_bytes": sum(record["size"] for record in manifest["files"]),
        },
        "errors": [],
    }


def build_public_artifact(
    repo_root: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    source_date_epoch: int,
) -> dict[str, Any]:
    """Build and preflight a deterministic public ZIP from a clean worktree.

    The function never stages, commits, tags, pushes, or publishes.  Failure is
    reported structurally and leaves ``output_path`` untouched.
    """

    root = Path(repo_root)
    output = Path(output_path)
    output_label = output.name or "artifact"
    if not isinstance(source_date_epoch, int) or isinstance(source_date_epoch, bool):
        return _failure(
            "artifact_build",
            [
                _error(
                    "invalid_epoch",
                    output_label,
                    "source_date_epoch must be an integer",
                )
            ],
            artifact=output_label,
        )
    if source_date_epoch < MIN_ZIP_EPOCH or source_date_epoch > MAX_ZIP_EPOCH:
        return _failure(
            "artifact_build",
            [
                _error(
                    "invalid_epoch",
                    output_label,
                    "source_date_epoch is outside ZIP range",
                )
            ],
            artifact=output_label,
        )
    if output.suffix.casefold() != ".zip":
        return _failure(
            "artifact_build",
            [
                _error(
                    "unsupported_archive_type",
                    output_label,
                    "output path must end in .zip",
                )
            ],
            artifact=output_label,
        )
    if output.is_symlink():
        return _failure(
            "artifact_build",
            [_error("symlink", output_label, "output path cannot be a symlink")],
            artifact=output_label,
        )
    try:
        root = root.resolve(strict=True)
    except OSError:
        return _failure(
            "artifact_build",
            [_error("missing_repository", ".", "repository root does not exist")],
            artifact=output_label,
        )
    if not root.is_dir():
        return _failure(
            "artifact_build",
            [_error("missing_repository", ".", "repository root is not a directory")],
            artifact=output_label,
        )

    config, config_errors = _load_config(root)
    if config_errors or config is None:
        return _failure("artifact_build", config_errors, artifact=output_label)
    first_snapshot, git_errors = _git_snapshot(root)
    if git_errors or first_snapshot is None:
        return _failure("artifact_build", git_errors, artifact=output_label)
    payload, archive_modes, payload_errors = _collect_payload(
        root,
        config,
        first_snapshot["tracked_paths"],
        first_snapshot["tracked_modes"],
        first_snapshot["tracked_oids"],
    )
    if payload_errors or payload is None or archive_modes is None:
        return _failure("artifact_build", payload_errors, artifact=output_label)
    payload, archive_modes, overlay_errors = _apply_archive_overlays(
        payload, archive_modes, config
    )
    if overlay_errors or payload is None or archive_modes is None:
        return _failure("artifact_build", overlay_errors, artifact=output_label)

    archive_bytes, manifest = _artifact_bytes(
        payload,
        modes=archive_modes,
        commit=first_snapshot["commit"],
        source_date_epoch=source_date_epoch,
        config=config,
    )
    if len(archive_bytes) > config["limits"]["max_archive_bytes"]:
        return _failure(
            "artifact_build",
            [
                _error(
                    "archive_size_limit",
                    output_label,
                    "built archive exceeds configured limit",
                )
            ],
            artifact=output_label,
        )

    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="claude-obsidian-release-", suffix=".zip"
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(archive_bytes)
            temporary.flush()
            os.fsync(temporary.fileno())
        audit = audit_artifact(temporary_path)
        if not audit["ok"]:
            return _failure(
                "artifact_build",
                audit["errors"],
                artifact=output_label,
                preflight=audit,
            )

        second_snapshot, second_errors = _git_snapshot(root)
        if second_errors or second_snapshot is None:
            return _failure("artifact_build", second_errors, artifact=output_label)
        if second_snapshot != first_snapshot:
            return _failure(
                "artifact_build",
                [
                    _error(
                        "source_changed",
                        ".",
                        "Git snapshot changed during artifact construction",
                    )
                ],
                artifact=output_label,
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, staged_name = tempfile.mkstemp(
            prefix=f".{output.name}.", dir=output.parent
        )
        staged = Path(staged_name)
        try:
            with os.fdopen(descriptor, "wb") as destination:
                destination.write(archive_bytes)
                destination.flush()
                os.fsync(destination.fileno())
            os.replace(staged, output)
        finally:
            try:
                staged.unlink()
            except FileNotFoundError:
                pass
    except OSError:
        return _failure(
            "artifact_build",
            [
                _error(
                    "write_failed",
                    output_label,
                    "artifact could not be written atomically",
                )
            ],
            artifact=output_label,
        )
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass

    digest = _sha256(archive_bytes)
    return {
        "ok": True,
        "kind": "artifact_build",
        "artifact": output_label,
        "sha256": digest,
        "source_commit": first_snapshot["commit"],
        "source_date_epoch": source_date_epoch,
        "manifest_sha256": _sha256(_canonical_json(manifest)),
        "summary": {
            "archive_bytes": len(archive_bytes),
            "file_count": len(payload),
            "payload_bytes": sum(len(data) for data in payload.values()),
        },
        "errors": [],
    }


__all__ = ["audit_artifact", "build_public_artifact"]
