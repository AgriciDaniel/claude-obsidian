"""Offline-first capture primitives for claude-obsidian.

Only local filesystem capture executes in this module. Network access, OCR,
transcription, and content extraction are represented as inert command plans
which require a separately configured runner and explicit user consent.
"""

from __future__ import annotations

import builtins
import errno
import hashlib
import ipaddress
import json
import math
import mimetypes
import os
import re
import socket
import stat
import struct
import time
import unicodedata
import uuid
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Mapping, Sequence, cast
from urllib.parse import urlsplit, urlunsplit

from .json_utils import parse_finite_json_float

from .paths import canonical, is_relative_to
from .transaction import (
    BUNDLE_SCHEMA,
    TransactionValidationError,
    _LockIdentityChanged,
    _PlatformConfinementUnavailable,
    _UNSUPPORTED_PLATFORM_MESSAGE,
    _lock_entry_matches,
    _open_lock_directory_at,
    _open_lock_parent_from_root_fd,
    _open_lock_root_fd,
    _read_lock_owner_at,
    _release_vault_advisory_lock,
    _remove_lock_directory_at,
    _try_vault_advisory_lock,
    _write_lock_owner_at,
    apply_bundle,
    read_vault_regular,
    sha256_bytes,
)
from .url_safety import url_credential_issue


ADAPTER_SCHEMA = "claude-obsidian.capture-adapters.v1"
CONFIG_SCHEMA = "claude-obsidian.capture-config.v1"
QUEUE_SCHEMA = "claude-obsidian.capture-queue.v1"
ACTION_SCHEMA = "claude-obsidian.capture-action.v1"
PROPOSAL_SCHEMA = "claude-obsidian.deletion-proposal.v1"

# The writer and reader share one exact durability envelope.  A queue accepted
# by a mutating operation must always remain readable by list/recover, including
# after canonical pretty-printing.  The entry count separately bounds validation
# and de-duplication work for adversarial but compact JSON documents.
MAX_QUEUE_BYTES = 8 * 1024 * 1024
MAX_QUEUE_ENTRIES = 4096

DEFAULT_INBOX = "inbox"
LEGACY_RAW = ".raw"
DEFAULT_ADAPTER_MANIFEST = (
    Path(__file__).resolve().parent.parent / "config/adapters.json"
)
QUEUE_STATES = frozenset({"queued", "claimed", "completed", "failed"})

_TEXT_EXTENSIONS = frozenset(
    {".md", ".markdown", ".txt", ".json", ".csv", ".yaml", ".yml", ".html"}
)
_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp"})
_MEDIA_EXTENSIONS = frozenset({".mp3", ".wav", ".m4a", ".mp4", ".mov", ".webm"})
_SAFE_CAPTURE_EXTENSIONS = (
    _TEXT_EXTENSIONS
    | _IMAGE_EXTENSIONS
    | _MEDIA_EXTENSIONS
    | {
        ".pdf",
        ".epub",
    }
)
_RESERVED_WINDOWS_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
)


class CaptureError(RuntimeError):
    """Base error with a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class CaptureValidationError(CaptureError):
    """The requested capture violates a deterministic input policy."""


class CaptureConflict(CaptureError):
    """The queue, lock, or immutable source state changed concurrently."""


class CaptureBudgetExceeded(CaptureValidationError):
    """A bounded capture budget would be exceeded."""


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


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


def _json_object(value: Mapping[str, Any] | None, *, field: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise CaptureValidationError(
            "QUEUE_VALUE_INVALID", f"{field} must be an object"
        )
    try:
        cloned = json.loads(json.dumps(dict(value), ensure_ascii=False))
    except (TypeError, ValueError) as exc:
        raise CaptureValidationError(
            "QUEUE_VALUE_INVALID", f"{field} must be JSON serializable"
        ) from exc
    if not isinstance(cloned, dict):
        raise CaptureValidationError(
            "QUEUE_VALUE_INVALID", f"{field} must be an object"
        )
    return cloned


def _process_alive(pid: int) -> bool | None:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return None
    return True


def _safe_runtime_dir(vault_root: Path) -> Path:
    """Create the capture runtime through a no-follow vault descriptor."""

    root = canonical(vault_root)
    if not root.is_dir():
        raise CaptureValidationError(
            "VAULT_MISSING", f"vault is not a directory: {root}"
        )
    root_fd = -1
    runtime_fd = -1
    try:
        root_fd = _open_lock_root_fd(root)
        runtime_fd = _open_lock_parent_from_root_fd(
            root_fd,
            (".vault-meta", "capture"),
            create=True,
        )
    except OSError as exc:
        if isinstance(exc, _PlatformConfinementUnavailable):
            raise CaptureValidationError(
                "UNSUPPORTED_PLATFORM", _UNSUPPORTED_PLATFORM_MESSAGE
            ) from exc
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise CaptureValidationError(
                "RUNTIME_SYMLINK",
                f"capture runtime path must be a confined directory: {exc}",
            ) from exc
        raise CaptureValidationError(
            "QUEUE_LOCK_UNSUPPORTED",
            f"cannot create a confined capture runtime: {exc}",
        ) from exc
    finally:
        if runtime_fd >= 0:
            os.close(runtime_fd)
        if root_fd >= 0:
            os.close(root_fd)
    return root / ".vault-meta" / "capture"


def _runtime_entry_exists(runtime_fd: int, name: str) -> bool:
    """Inspect one fixed runtime leaf without following an alias."""

    try:
        os.stat(name, dir_fd=runtime_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise TransactionValidationError(
            "UNSAFE_VAULT_PATH",
            f"cannot inspect .vault-meta/capture/{name}: {exc}",
        ) from exc
    return True


def _read_runtime_regular(
    runtime_fd: int,
    name: str,
    *,
    limit: int,
    missing_ok: bool,
) -> bytes | None:
    """Read a bounded regular runtime leaf from the pinned capture directory."""

    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise TransactionValidationError(
            "INVALID_READ_LIMIT", "read limit must be positive"
        )
    try:
        metadata = os.stat(name, dir_fd=runtime_fd, follow_symlinks=False)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise TransactionValidationError(
            "VAULT_FILE_MISSING",
            f"vault file is missing: .vault-meta/capture/{name}",
        ) from None
    except OSError as exc:
        raise TransactionValidationError(
            "UNSAFE_VAULT_PATH",
            f"cannot inspect .vault-meta/capture/{name}: {exc}",
        ) from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise TransactionValidationError(
            "SYMLINK_WRITE_PATH",
            f"vault file may not be a symlink: .vault-meta/capture/{name}",
        )
    if not stat.S_ISREG(metadata.st_mode):
        raise TransactionValidationError(
            "UNSAFE_VAULT_PATH",
            f"vault file is not regular: .vault-meta/capture/{name}",
        )
    if metadata.st_size > limit:
        raise TransactionValidationError(
            "VAULT_FILE_TOO_LARGE",
            f"vault file exceeds read limit: .vault-meta/capture/{name}",
        )

    descriptor = -1
    try:
        flags = (
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        try:
            descriptor = os.open(name, flags, dir_fd=runtime_fd)
        except FileNotFoundError:
            if missing_ok:
                return None
            raise TransactionValidationError(
                "VAULT_FILE_MISSING",
                f"vault file is missing: .vault-meta/capture/{name}",
            ) from None
        except OSError as exc:
            raise TransactionValidationError(
                "UNSAFE_VAULT_PATH",
                f"cannot open .vault-meta/capture/{name}: {exc}",
            ) from exc
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
            metadata.st_dev,
            metadata.st_ino,
        ):
            raise TransactionValidationError(
                "UNSAFE_VAULT_PATH",
                f"vault file changed or is not regular: .vault-meta/capture/{name}",
            )
        if opened.st_size > limit:
            raise TransactionValidationError(
                "VAULT_FILE_TOO_LARGE",
                f"vault file exceeds read limit: .vault-meta/capture/{name}",
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            block = os.read(descriptor, min(1024 * 1024, limit + 1 - total))
            if not block:
                break
            chunks.append(block)
            total += len(block)
            if total > limit:
                raise TransactionValidationError(
                    "VAULT_FILE_TOO_LARGE",
                    f"vault file exceeds read limit: .vault-meta/capture/{name}",
                )
        after = os.fstat(descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_mode")
        if any(
            getattr(opened, field) != getattr(after, field) for field in stable_fields
        ):
            raise TransactionValidationError(
                "UNSAFE_VAULT_PATH",
                f"vault file changed while read: .vault-meta/capture/{name}",
            )
        return b"".join(chunks)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _atomic_runtime_write(runtime_fd: int, name: str, data: bytes) -> None:
    """Atomically replace one queue leaf through the pinned runtime directory."""

    temporary = f".{name}.capture-{os.getpid()}-{uuid.uuid4().hex}"
    descriptor = -1
    try:
        descriptor = os.open(
            temporary,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=runtime_fd,
        )
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(
            temporary,
            name,
            src_dir_fd=runtime_fd,
            dst_dir_fd=runtime_fd,
        )
        os.fsync(runtime_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            os.unlink(temporary, dir_fd=runtime_fd)
        except FileNotFoundError:
            pass


def _validate_relative_directory(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise CaptureValidationError(
            "INVALID_CONFIG_PATH", f"{field} must be a relative POSIX path"
        )
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or value in {".", ".."} or ".." in parsed.parts:
        raise CaptureValidationError(
            "INVALID_CONFIG_PATH", f"{field} escapes the vault"
        )
    if any(not part or part in {".", ".."} for part in parsed.parts):
        raise CaptureValidationError(
            "INVALID_CONFIG_PATH", f"{field} is not normalized"
        )
    return parsed.as_posix()


@dataclass(frozen=True)
class CaptureBudget:
    """Hard limits applied before a batch mutates the vault."""

    max_items: int = 100
    max_total_bytes: int = 256 * 1024 * 1024
    max_file_bytes: int = 64 * 1024 * 1024

    def __post_init__(self) -> None:
        for name, value in (
            ("max_items", self.max_items),
            ("max_total_bytes", self.max_total_bytes),
            ("max_file_bytes", self.max_file_bytes),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise CaptureValidationError(
                    "INVALID_BUDGET", f"{name} must be a positive integer"
                )
        if self.max_file_bytes > self.max_total_bytes:
            raise CaptureValidationError(
                "INVALID_BUDGET", "max_file_bytes cannot exceed max_total_bytes"
            )


@dataclass(frozen=True)
class CaptureConfig:
    """Vault capture locations without conflating the visible inbox and raw store."""

    inbox: str = DEFAULT_INBOX
    raw_store: str = LEGACY_RAW
    include_legacy_raw: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "inbox", _validate_relative_directory(self.inbox, field="inbox")
        )
        object.__setattr__(
            self,
            "raw_store",
            _validate_relative_directory(self.raw_store, field="raw_store"),
        )
        if not isinstance(self.include_legacy_raw, bool):
            raise CaptureValidationError(
                "INVALID_CONFIG", "include_legacy_raw must be boolean"
            )
        if self.inbox.startswith("."):
            raise CaptureValidationError(
                "INBOX_NOT_VISIBLE", "the primary inbox must be visible"
            )

    @classmethod
    def load(cls, vault_root: Path, *, inbox: str | None = None) -> "CaptureConfig":
        """Load optional local config; an explicit inbox wins without writing state."""

        root = canonical(vault_root)
        values: dict[str, Any] = {}
        raw_bytes = read_vault_regular(
            root,
            ".vault-meta/capture/config.json",
            limit=1024 * 1024,
        )
        if raw_bytes is not None:
            try:
                raw = _strict_json_loads(raw_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                raise CaptureValidationError(
                    "INVALID_CONFIG", f"cannot read capture config: {exc}"
                ) from exc
            if not isinstance(raw, dict) or raw.get("schema") != CONFIG_SCHEMA:
                raise CaptureValidationError(
                    "INVALID_CONFIG", f"capture config must use {CONFIG_SCHEMA}"
                )
            values = raw
        return cls(
            inbox=inbox if inbox is not None else values.get("inbox", DEFAULT_INBOX),
            raw_store=values.get("raw_store", LEGACY_RAW),
            include_legacy_raw=values.get("include_legacy_raw", True),
        )

    def source_roots(self, vault_root: Path) -> tuple[Path, ...]:
        root = canonical(vault_root)
        values = [root / self.inbox]
        raw = root / self.raw_store
        if self.include_legacy_raw and raw != values[0]:
            values.append(raw)
        return tuple(values)


def load_adapter_manifest(path: Path | None = None) -> dict[str, Any]:
    """Load and minimally validate the declarative adapter registry."""

    location = DEFAULT_ADAPTER_MANIFEST if path is None else Path(path)
    try:
        value = _strict_json_loads(location.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise CaptureValidationError(
            "INVALID_ADAPTER_MANIFEST", f"cannot read adapters: {exc}"
        ) from exc
    if not isinstance(value, dict) or value.get("schema") != ADAPTER_SCHEMA:
        raise CaptureValidationError(
            "INVALID_ADAPTER_MANIFEST", f"adapters must use {ADAPTER_SCHEMA}"
        )
    adapters = value.get("adapters")
    if not isinstance(adapters, list):
        raise CaptureValidationError(
            "INVALID_ADAPTER_MANIFEST", "adapters must be an array"
        )
    seen: set[str] = set()
    allowed_maturity = {"implemented", "metadata-only", "external-runner-required"}
    for raw in adapters:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            raise CaptureValidationError(
                "INVALID_ADAPTER_MANIFEST", "every adapter needs an id"
            )
        adapter_id = raw["id"]
        if adapter_id in seen or raw.get("maturity") not in allowed_maturity:
            raise CaptureValidationError(
                "INVALID_ADAPTER_MANIFEST", f"invalid adapter: {adapter_id}"
            )
        if raw.get("execution") == "internal" and raw.get("maturity") != "implemented":
            raise CaptureValidationError(
                "INVALID_ADAPTER_MANIFEST",
                f"internal adapter is not implemented: {adapter_id}",
            )
        if raw.get("destructive") is not False:
            raise CaptureValidationError(
                "INVALID_ADAPTER_MANIFEST",
                f"adapter may not be destructive: {adapter_id}",
            )
        seen.add(adapter_id)
    expected = {"filesystem", "url", "image", "pdf", "youtube", "epub", "ocr"}
    if seen != expected:
        raise CaptureValidationError(
            "INVALID_ADAPTER_MANIFEST",
            "adapter ids must be exactly: " + ", ".join(sorted(expected)),
        )
    return value


def _adapter(
    adapter_id: str, manifest: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    loaded = load_adapter_manifest() if manifest is None else dict(manifest)
    for raw in loaded.get("adapters", []):
        if isinstance(raw, dict) and raw.get("id") == adapter_id:
            return dict(raw)
    raise CaptureValidationError(
        "UNKNOWN_ADAPTER", f"unknown capture adapter: {adapter_id}"
    )


def _validate_filename(path: Path) -> None:
    name = path.name
    if name in {"", ".", "..", ".manifest.json"}:
        raise CaptureValidationError(
            "UNSAFE_FILENAME", f"reserved source filename: {name!r}"
        )
    if name != unicodedata.normalize("NFC", name):
        raise CaptureValidationError(
            "UNSAFE_FILENAME", "source filename must use NFC normalization"
        )
    if name != name.strip() or len(name.encode("utf-8")) > 240:
        raise CaptureValidationError(
            "UNSAFE_FILENAME", "source filename has unsafe spacing or length"
        )
    if any(unicodedata.category(char).startswith("C") for char in name):
        raise CaptureValidationError(
            "UNSAFE_FILENAME", "source filename contains control or format characters"
        )
    if (
        name.endswith((".", " "))
        or name.split(".", 1)[0].upper() in _RESERVED_WINDOWS_NAMES
    ):
        raise CaptureValidationError(
            "UNSAFE_FILENAME", f"source filename is not portable: {name!r}"
        )


def _allowed_source_path(vault_root: Path, source: Path, config: CaptureConfig) -> Path:
    root = canonical(vault_root)
    raw_source = Path(source).expanduser()
    candidate = raw_source if raw_source.is_absolute() else root / raw_source
    lexical_candidate = Path(os.path.abspath(candidate))
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise CaptureValidationError(
            "SOURCE_MISSING", f"cannot resolve source: {source}"
        ) from exc
    if not resolved.is_file():
        raise CaptureValidationError(
            "SOURCE_NOT_FILE", f"capture source is not a regular file: {source}"
        )
    allowed = False
    for configured_root in config.source_roots(root):
        if configured_root.is_symlink():
            raise CaptureValidationError(
                "SOURCE_ROOT_SYMLINK", f"source root is a symlink: {configured_root}"
            )
        configured_resolved = configured_root.resolve(strict=False)
        if is_relative_to(resolved, configured_resolved):
            allowed = True
            lexical_root = Path(os.path.abspath(configured_root))
            try:
                relative = lexical_candidate.relative_to(lexical_root)
            except ValueError:
                raise CaptureValidationError(
                    "SOURCE_OUTSIDE_INBOX",
                    "source path enters the inbox through an external alias",
                )
            current = lexical_root
            for part in relative.parts:
                current = current / part
                if current.is_symlink():
                    raise CaptureValidationError(
                        "SOURCE_SYMLINK", f"symlink sources are forbidden: {source}"
                    )
            break
    if not allowed:
        raise CaptureValidationError(
            "SOURCE_OUTSIDE_INBOX", "source is outside the configured inbox roots"
        )
    _validate_filename(resolved)
    mode = resolved.stat().st_mode
    if not stat.S_ISREG(mode):
        raise CaptureValidationError(
            "SOURCE_NOT_FILE", "capture source must be a regular file"
        )
    return resolved


def source_identity(path: Path, *, max_bytes: int | None = None) -> str:
    """Return the SHA-256 identity of a local source without following a leaf symlink."""

    source = Path(path)
    if source.is_symlink():
        raise CaptureValidationError("SOURCE_SYMLINK", "symlink sources are forbidden")
    try:
        before = source.stat()
    except OSError as exc:
        raise CaptureValidationError(
            "SOURCE_MISSING", f"cannot stat source: {source}"
        ) from exc
    if not stat.S_ISREG(before.st_mode):
        raise CaptureValidationError("SOURCE_NOT_FILE", "source must be a regular file")
    if max_bytes is not None and before.st_size > max_bytes:
        raise CaptureBudgetExceeded(
            "FILE_BUDGET_EXCEEDED", f"source exceeds {max_bytes} bytes"
        )
    digest = hashlib.sha256()
    total = 0
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = -1
    try:
        descriptor = os.open(source, flags)
    except OSError as exc:
        raise CaptureValidationError(
            "SOURCE_OPEN_FAILED", f"cannot safely open source: {source}"
        ) from exc
    try:
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            while True:
                block = handle.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if max_bytes is not None and total > max_bytes:
                    raise CaptureBudgetExceeded(
                        "FILE_BUDGET_EXCEEDED", f"source exceeds {max_bytes} bytes"
                    )
                digest.update(block)
            after_fd = os.fstat(handle.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    after_path = source.stat()
    signature_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    signature_after = (
        after_path.st_dev,
        after_path.st_ino,
        after_path.st_size,
        after_path.st_mtime_ns,
    )
    if signature_before != signature_after or (after_fd.st_dev, after_fd.st_ino) != (
        before.st_dev,
        before.st_ino,
    ):
        raise CaptureConflict(
            "SOURCE_CHANGED", "source changed while its identity was computed"
        )
    return digest.hexdigest()


def _png_dimensions(sample: bytes) -> tuple[int, int] | None:
    if len(sample) >= 24 and sample.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", sample[16:24])
    return None


def _gif_dimensions(sample: bytes) -> tuple[int, int] | None:
    if len(sample) >= 10 and sample[:6] in {b"GIF87a", b"GIF89a"}:
        return struct.unpack("<HH", sample[6:10])
    return None


def sniff_metadata(path: Path, *, digest: str | None = None) -> dict[str, Any]:
    """Identify common local formats from bounded bytes, without content extraction."""

    source = Path(path)
    if source.is_symlink():
        raise CaptureValidationError("SOURCE_SYMLINK", "symlink sources are forbidden")
    _validate_filename(source)
    size = source.stat().st_size
    with source.open("rb") as handle:
        sample = handle.read(64 * 1024)
    suffix = source.suffix.lower()
    kind = "binary"
    media_type = "application/octet-stream"
    detected_by = "fallback"
    dimensions: tuple[int, int] | None = None
    if sample.startswith(b"%PDF-"):
        kind, media_type, detected_by = "pdf", "application/pdf", "magic"
    elif (dimensions := _png_dimensions(sample)) is not None:
        kind, media_type, detected_by = "image", "image/png", "magic"
    elif sample.startswith(b"\xff\xd8\xff"):
        kind, media_type, detected_by = "image", "image/jpeg", "magic"
    elif (dimensions := _gif_dimensions(sample)) is not None:
        kind, media_type, detected_by = "image", "image/gif", "magic"
    elif sample.startswith((b"RIFF",)) and sample[8:12] == b"WEBP":
        kind, media_type, detected_by = "image", "image/webp", "magic"
    elif suffix == ".epub" and zipfile.is_zipfile(source):
        try:
            with zipfile.ZipFile(source) as archive:
                info = archive.getinfo("mimetype")
                marker = archive.read(info) if info.file_size <= 64 else b""
            if marker == b"application/epub+zip":
                kind, media_type, detected_by = (
                    "epub",
                    "application/epub+zip",
                    "container",
                )
        except (KeyError, OSError, zipfile.BadZipFile):
            pass
    elif suffix in _TEXT_EXTENSIONS:
        try:
            sample.decode("utf-8")
        except UnicodeDecodeError:
            pass
        else:
            kind = "text"
            media_type = mimetypes.types_map.get(suffix, "text/plain")
            detected_by = "utf-8"
    elif suffix in _MEDIA_EXTENSIONS:
        kind = "media"
        media_type = mimetypes.types_map.get(suffix, "application/octet-stream")
        detected_by = "extension"
    result: dict[str, Any] = {
        "name": source.name,
        "extension": suffix,
        "size_bytes": size,
        "sha256": digest or source_identity(source),
        "kind": kind,
        "media_type": media_type,
        "detected_by": detected_by,
    }
    if dimensions is not None:
        result["width"], result["height"] = dimensions
    return result


def _preflight_sources(
    vault_root: Path,
    sources: Iterable[Path],
    *,
    config: CaptureConfig,
    budget: CaptureBudget,
) -> list[Path]:
    materialized = list(sources)
    if len(materialized) > budget.max_items:
        raise CaptureBudgetExceeded(
            "COUNT_BUDGET_EXCEEDED", f"capture exceeds {budget.max_items} items"
        )
    checked: list[Path] = []
    total = 0
    seen: set[Path] = set()
    for raw in materialized:
        source = _allowed_source_path(vault_root, raw, config)
        if source in seen:
            continue
        seen.add(source)
        size = source.stat().st_size
        if size > budget.max_file_bytes:
            raise CaptureBudgetExceeded(
                "FILE_BUDGET_EXCEEDED",
                f"{source.name} exceeds {budget.max_file_bytes} bytes",
            )
        total += size
        if total > budget.max_total_bytes:
            raise CaptureBudgetExceeded(
                "TOTAL_BUDGET_EXCEEDED",
                f"capture exceeds {budget.max_total_bytes} bytes",
            )
        checked.append(source)
    return checked


def discover_files(
    vault_root: Path,
    *,
    config: CaptureConfig | None = None,
    budget: CaptureBudget | None = None,
) -> list[Path]:
    """Discover regular files in the visible inbox and optional legacy ``.raw``."""

    root = canonical(vault_root)
    selected = config or CaptureConfig.load(root)
    limits = budget or CaptureBudget()
    candidates: list[Path] = []
    for source_root in selected.source_roots(root):
        if not source_root.exists():
            continue
        if source_root.is_symlink() or not source_root.is_dir():
            raise CaptureValidationError(
                "SOURCE_ROOT_SYMLINK", f"unsafe source root: {source_root}"
            )
        for directory, names, filenames in os.walk(source_root, followlinks=False):
            current = Path(directory)
            if source_root == root / selected.raw_store and current == source_root:
                # Content-addressed copies are outputs, not new legacy inputs.
                names[:] = [name for name in names if name != "captured"]
            for name in list(names):
                if (current / name).is_symlink():
                    raise CaptureValidationError(
                        "SOURCE_SYMLINK", f"symlink in inbox: {current / name}"
                    )
            for name in filenames:
                if name == ".manifest.json" or (
                    source_root == root / selected.inbox and name == ".gitkeep"
                ):
                    continue
                candidate = current / name
                if candidate.is_symlink():
                    raise CaptureValidationError(
                        "SOURCE_SYMLINK", f"symlink in inbox: {candidate}"
                    )
                candidates.append(candidate)
    candidates.sort(key=lambda item: item.relative_to(root).as_posix())
    return _preflight_sources(root, candidates, config=selected, budget=limits)


def _planned_destination(
    vault_root: Path, digest: str, source: Path, config: CaptureConfig
) -> Path:
    """Calculate a raw destination without creating directories."""

    root = canonical(vault_root)
    raw_root = root / config.raw_store
    captured = raw_root / "captured"
    for candidate in (raw_root, captured):
        if candidate.is_symlink():
            raise CaptureValidationError(
                "RAW_STORE_SYMLINK", "raw source store must not be a symlink"
            )
        if candidate.exists() and not is_relative_to(
            candidate.resolve(strict=True), root
        ):
            raise CaptureValidationError(
                "PATH_OUTSIDE_VAULT", "raw source store escapes the vault"
            )
    suffix = (
        source.suffix.lower()
        if source.suffix.lower() in _SAFE_CAPTURE_EXTENSIONS
        else ".bin"
    )
    return captured / f"{digest}{suffix}"


def _find_existing_capture(destination: Path, digest: str) -> Path | None:
    for candidate in sorted(destination.parent.glob(f"{digest}.*")):
        if candidate.is_symlink():
            raise CaptureValidationError(
                "RAW_STORE_SYMLINK", f"captured source is a symlink: {candidate}"
            )
        if candidate.is_file():
            if source_identity(candidate) != digest:
                raise CaptureConflict(
                    "IMMUTABLE_SOURCE_CONFLICT",
                    f"content-addressed source has unexpected bytes: {candidate}",
                )
            return candidate
    return None


def plan_filesystem_batch(
    vault_root: Path,
    sources: Iterable[Path],
    *,
    config: CaptureConfig | None = None,
    budget: CaptureBudget | None = None,
) -> list[dict[str, Any]]:
    """Build a read-only local capture plan with the full security preflight."""

    root = canonical(vault_root)
    selected = config or CaptureConfig.load(root)
    limits = budget or CaptureBudget()
    checked = _preflight_sources(root, sources, config=selected, budget=limits)
    raw_root = (root / selected.raw_store).resolve(strict=False)
    plans: list[dict[str, Any]] = []
    planned_captures: dict[str, Path] = {}
    for source in checked:
        digest = source_identity(source, max_bytes=limits.max_file_bytes)
        metadata = sniff_metadata(source, digest=digest)
        if is_relative_to(source, raw_root):
            stored = source
            changed = False
            skip_reason = "legacy-raw-source"
        else:
            destination = _planned_destination(root, digest, source, selected)
            existing = _find_existing_capture(destination, digest)
            prior = planned_captures.get(digest)
            if existing is not None:
                stored = existing
                changed = False
                skip_reason = "content-unchanged"
            elif prior is not None:
                stored = prior
                changed = False
                skip_reason = "content-unchanged"
            else:
                stored = destination
                planned_captures[digest] = destination
                changed = True
                skip_reason = None
        plans.append(
            {
                "schema": "claude-obsidian.filesystem-capture-plan.v1",
                "adapter": "filesystem",
                "source_identity": digest,
                "source": source.relative_to(root).as_posix(),
                "stored_path": stored.relative_to(root).as_posix(),
                "would_change": changed,
                "skip_reason": skip_reason,
                "execute": False,
                "metadata": metadata,
            }
        )
    return plans


def capture_filesystem_batch(
    vault_root: Path,
    sources: Iterable[Path],
    *,
    config: CaptureConfig | None = None,
    budget: CaptureBudget | None = None,
) -> list[dict[str, Any]]:
    """Capture a bounded local batch into the immutable raw store.

    Sources already inside the legacy raw store are indexed in place. The
    function commits all new payloads through one recoverable transaction and
    never removes an inbox file; callers may request a review proposal after
    successful capture.
    """

    root = canonical(vault_root)
    selected = config or CaptureConfig.load(root)
    limits = budget or CaptureBudget()
    plans = plan_filesystem_batch(root, sources, config=selected, budget=limits)
    writes: list[dict[str, Any]] = []
    expected_hashes: dict[str, None] = {}
    for item in plans:
        if not item["would_change"]:
            continue
        relative = item["stored_path"]
        expected_hashes[relative] = None
        writes.append(
            {
                "path": relative,
                "mode": "create",
                "content_file": str((root / item["source"]).resolve(strict=True)),
                "sha256": item["source_identity"],
            }
        )
    if writes:
        identity = sha256_bytes(
            json.dumps(
                writes,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )[:24]
        apply_bundle(
            root,
            {
                "schema": BUNDLE_SCHEMA,
                "operation_id": f"capture-direct-{identity}",
                "operation_type": "capture",
                "expected_hashes": expected_hashes,
                "writes": writes,
                "address_requests": [],
                "source_manifest_updates": {},
            },
        )
    return [
        {
            "schema": "claude-obsidian.filesystem-capture.v1",
            "source_identity": item["source_identity"],
            "source": item["source"],
            "stored_path": item["stored_path"],
            "changed": bool(item["would_change"]),
            "skip_reason": item["skip_reason"],
            "metadata": item["metadata"],
        }
        for item in plans
    ]


def capture_filesystem(
    vault_root: Path,
    source: Path,
    *,
    config: CaptureConfig | None = None,
    budget: CaptureBudget | None = None,
) -> dict[str, Any]:
    return capture_filesystem_batch(vault_root, [source], config=config, budget=budget)[
        0
    ]


def _normalize_host(host: str) -> str:
    candidate = host.rstrip(".").lower()
    try:
        return candidate.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise CaptureValidationError(
            "URL_HOST_INVALID", "URL host cannot be normalized"
        ) from exc


# Every dot-label is a bare decimal or 0x-hex numeral: this is never a real
# public DNS name (numeric-only TLDs do not exist) and is instead an
# alternate spelling of an IP address that ipaddress.ip_address() does not
# parse, for example "0x7f.0.0.1", "0177.0.0.1", "127.1", "0x7f.0x0.0x0.0x1".
# Mirrors the equivalent check in ledgers.py::_canonical_url_host. Wildcard
# DNS services that map a name to loopback (for example 127.0.0.1.nip.io)
# are a known residual gap and are deliberately not blocklisted here.
_NUMERIC_OR_HEX_LABEL = re.compile(r"(?:[0-9]+|0x[0-9a-f]+)")


def _validate_public_host(host: str) -> str:
    normalized = _normalize_host(host)
    if normalized == "localhost" or normalized.endswith(
        (".localhost", ".local", ".internal", ".lan", ".home", ".test", ".invalid")
    ):
        raise CaptureValidationError(
            "URL_PRIVATE_HOST", f"local URL host is forbidden: {normalized}"
        )
    unbracketed = normalized.strip("[]")
    try:
        address = ipaddress.ip_address(unbracketed)
    except ValueError:
        labels = normalized.split(".")
        if len(labels) < 2:
            raise CaptureValidationError(
                "URL_PRIVATE_HOST", "single-label URL hosts are forbidden"
            )
        if all(_NUMERIC_OR_HEX_LABEL.fullmatch(label) for label in labels):
            raise CaptureValidationError(
                "URL_PRIVATE_HOST",
                "numeric or hex-encoded URL hosts are forbidden",
            )
    else:
        if not address.is_global:
            raise CaptureValidationError(
                "URL_PRIVATE_HOST", f"non-public IP is forbidden: {address}"
            )
    return normalized


def validate_https_url(url: str) -> str:
    """Validate and normalize an HTTPS URL without DNS or network access."""

    if not isinstance(url, str) or not url or len(url) > 8192:
        raise CaptureValidationError(
            "URL_INVALID", "URL must be a non-empty bounded string"
        )
    if any(
        char.isspace() or unicodedata.category(char).startswith("C") for char in url
    ):
        raise CaptureValidationError(
            "URL_INVALID", "URL contains whitespace or control characters"
        )
    if "\\" in url:
        raise CaptureValidationError("URL_INVALID", "URL contains a backslash")
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise CaptureValidationError("URL_INVALID", f"invalid URL: {exc}") from exc
    if parsed.scheme.lower() != "https":
        raise CaptureValidationError(
            "URL_SCHEME_FORBIDDEN", "only HTTPS capture URLs are accepted"
        )
    credential_issue = url_credential_issue(parsed)
    if credential_issue is not None:
        code = (
            "URL_USERINFO_FORBIDDEN"
            if credential_issue.kind == "userinfo"
            else "URL_SECRET_FORBIDDEN"
        )
        raise CaptureValidationError(code, credential_issue.message)
    if not parsed.hostname:
        raise CaptureValidationError("URL_HOST_MISSING", "URL has no host")
    host = _validate_public_host(parsed.hostname)
    if port is not None and not 1 <= port <= 65535:
        raise CaptureValidationError("URL_PORT_INVALID", "URL port is outside 1..65535")
    if parsed.fragment:
        raise CaptureValidationError(
            "URL_FRAGMENT_FORBIDDEN", "capture URLs must not contain fragments"
        )
    host_display = f"[{host}]" if ":" in host else host
    netloc = host_display if port in {None, 443} else f"{host_display}:{port}"
    path = parsed.path or "/"
    return urlunsplit(("https", netloc, path, parsed.query, ""))


def validate_redirect_chain(
    origin: str,
    redirects: Sequence[str],
    *,
    approved_hosts: Iterable[str] = (),
) -> list[str]:
    """Validate a completed redirect chain against an explicit host allowlist."""

    normalized_origin = validate_https_url(origin)
    origin_host = _normalize_host(urlsplit(normalized_origin).hostname or "")
    allowed = {origin_host}
    for raw in approved_hosts:
        allowed.add(_validate_public_host(raw))
    result = [normalized_origin]
    for raw in redirects:
        normalized = validate_https_url(raw)
        host = _normalize_host(urlsplit(normalized).hostname or "")
        if host not in allowed:
            raise CaptureValidationError(
                "REDIRECT_HOST_FORBIDDEN", f"redirect host is not approved: {host}"
            )
        result.append(normalized)
    return result


def plan_external_action(
    adapter_id: str,
    source: str,
    *,
    runner: Sequence[str] | None = None,
    approved_hosts: Iterable[str] = (),
    manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return an inert argv plan. This function never imports a network client or runs a process."""

    adapter = _adapter(adapter_id, manifest)
    if adapter_id == "filesystem":
        raise CaptureValidationError(
            "INTERNAL_ADAPTER", "filesystem capture does not need an external runner"
        )
    if (
        not isinstance(source, str)
        or not source
        or len(source) > 8192
        or any(unicodedata.category(char).startswith("C") for char in source)
    ):
        raise CaptureValidationError(
            "ACTION_SOURCE_INVALID", "action source must be a bounded string"
        )
    normalized_source = source
    if adapter.get("input") == "https-url":
        normalized_source = validate_https_url(source)
        host = _normalize_host(urlsplit(normalized_source).hostname or "")
        declared = {_normalize_host(item) for item in adapter.get("approved_hosts", [])}
        explicit = {_normalize_host(item) for item in approved_hosts}
        if declared and host not in declared | explicit:
            raise CaptureValidationError(
                "URL_HOST_FORBIDDEN", f"host is not approved for {adapter_id}: {host}"
            )
    argv: list[str]
    placeholder = runner is None
    if runner is None:
        argv = ["{external-runner}", adapter_id, "--source", normalized_source]
    else:
        if not runner or any(
            not isinstance(token, str)
            or not token
            or any(unicodedata.category(char).startswith("C") for char in token)
            for token in runner
        ):
            raise CaptureValidationError(
                "RUNNER_INVALID", "runner must be a non-empty argv sequence"
            )
        argv = [*runner, adapter_id, "--source", normalized_source]
    return {
        "schema": ACTION_SCHEMA,
        "adapter": adapter_id,
        "source": normalized_source,
        "state": "planned",
        "execute": False,
        "requires_explicit_consent": True,
        "runner_placeholder": placeholder,
        "command": argv,
        "privacy": {
            "network": bool(adapter.get("network")),
            "llm": bool(adapter.get("llm")),
            "redirect_policy": "origin-and-approved-hosts-only"
            if adapter.get("network")
            else None,
            "resolved_addresses_must_be_public": bool(adapter.get("network")),
        },
    }


def _queue_text(
    value: Any, *, field: str, limit: int, allow_none: bool = False
) -> str | None:
    if value is None and allow_none:
        return None
    if (
        not isinstance(value, str)
        or not value
        or len(value) > limit
        or any(unicodedata.category(character).startswith("C") for character in value)
    ):
        raise CaptureValidationError(
            "QUEUE_INVALID", f"queue {field} must be bounded text"
        )
    return value


def _queue_sha256(value: Any, *, field: str, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise CaptureValidationError(
            "QUEUE_INVALID", f"queue {field} must be lowercase SHA-256"
        )
    return value


def _validate_planned_action(
    adapter_id: str,
    source: str,
    action: Mapping[str, Any],
) -> None:
    try:
        adapter = _adapter(adapter_id)
    except CaptureValidationError as exc:
        raise CaptureValidationError(
            "QUEUE_INVALID", f"queue adapter is invalid: {adapter_id}"
        ) from exc
    if (
        action.get("schema") != ACTION_SCHEMA
        or action.get("adapter") != adapter_id
        or action.get("source") != source
        or action.get("state") != "planned"
        or action.get("execute") is not False
        or action.get("requires_explicit_consent") is not True
        or not isinstance(action.get("runner_placeholder"), bool)
    ):
        raise CaptureValidationError(
            "QUEUE_ACTION_INVALID",
            "planned_action must be an inert plan for the same adapter and source",
        )

    command = action.get("command")
    if (
        not isinstance(command, list)
        or not command
        or len(command) > 64
        or any(
            not isinstance(token, str)
            or not token
            or len(token) > 8192
            or any(
                unicodedata.category(character).startswith("C") for character in token
            )
            for token in command
        )
    ):
        raise CaptureValidationError(
            "QUEUE_ACTION_INVALID", "planned_action command is invalid"
        )
    expected_tail = [adapter_id, "--source", source]
    if action["runner_placeholder"]:
        if command != ["{external-runner}", *expected_tail]:
            raise CaptureValidationError(
                "QUEUE_ACTION_INVALID",
                "placeholder action command does not match its source",
            )
    elif len(command) < 4 or command[-3:] != expected_tail:
        raise CaptureValidationError(
            "QUEUE_ACTION_INVALID", "runner action command does not match its source"
        )

    privacy = action.get("privacy")
    network = bool(adapter.get("network"))
    expected_privacy = {
        "network": network,
        "llm": bool(adapter.get("llm")),
        "redirect_policy": "origin-and-approved-hosts-only" if network else None,
        "resolved_addresses_must_be_public": network,
    }
    if privacy != expected_privacy:
        raise CaptureValidationError(
            "QUEUE_ACTION_INVALID", "planned_action privacy does not match its adapter"
        )


def _validate_queue_claim(value: Any) -> None:
    if not isinstance(value, dict):
        raise CaptureValidationError(
            "QUEUE_INVALID", "claimed queue entry has no claim object"
        )
    token = value.get("token")
    if (
        not isinstance(token, str)
        or len(token) != 32
        or any(character not in "0123456789abcdef" for character in token)
    ):
        raise CaptureValidationError("QUEUE_INVALID", "queue claim token is invalid")
    pid = value.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        raise CaptureValidationError("QUEUE_INVALID", "queue claim pid is invalid")
    _queue_text(value.get("host"), field="claim host", limit=255)
    _queue_text(value.get("worker"), field="claim worker", limit=256, allow_none=True)
    _queue_text(value.get("claimed_at"), field="claim timestamp", limit=64)
    claimed_epoch = value.get("claimed_epoch")
    if (
        not isinstance(claimed_epoch, (int, float))
        or isinstance(claimed_epoch, bool)
        or not math.isfinite(claimed_epoch)
        or claimed_epoch < 0
    ):
        raise CaptureValidationError("QUEUE_INVALID", "queue claim epoch is invalid")


def _validate_queue_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise CaptureValidationError("QUEUE_INVALID", "queue entries must be objects")
    item_id = entry.get("id")
    if (
        not isinstance(item_id, str)
        or len(item_id) != 24
        or any(character not in "0123456789abcdef" for character in item_id)
    ):
        raise CaptureValidationError("QUEUE_INVALID", "queue entry id is invalid")
    key = entry.get("idempotency_key")
    if not isinstance(key, str) or not key or len(key) > 512 or "\x00" in key:
        raise CaptureValidationError(
            "QUEUE_INVALID", "queue idempotency key is invalid"
        )
    adapter_id = _queue_text(entry.get("adapter"), field="adapter", limit=64)
    if adapter_id is None:  # narrowed for static analyzers; allow_none is false above
        raise CaptureValidationError("QUEUE_INVALID", "queue adapter is missing")
    try:
        adapter = _adapter(adapter_id)
    except CaptureValidationError as exc:
        raise CaptureValidationError(
            "QUEUE_INVALID", f"queue adapter is invalid: {adapter_id}"
        ) from exc
    source = _queue_text(entry.get("source"), field="source", limit=8192)
    if source is None:  # narrowed for static analyzers; allow_none is false above
        raise CaptureValidationError("QUEUE_INVALID", "queue source is missing")
    if adapter.get("input") == "https-url" and validate_https_url(source) != source:
        raise CaptureValidationError(
            "QUEUE_INVALID", "queue URL source is not canonical"
        )
    _queue_sha256(entry.get("source_sha256"), field="source identity", allow_none=True)

    state = entry.get("state")
    if state not in QUEUE_STATES:
        raise CaptureValidationError(
            "QUEUE_INVALID", f"invalid queue state for {item_id}"
        )
    attempts = entry.get("attempts")
    if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 0:
        raise CaptureValidationError(
            "QUEUE_INVALID", "queue attempts must be a non-negative integer"
        )
    _queue_text(entry.get("created_at"), field="created timestamp", limit=64)
    _queue_text(entry.get("updated_at"), field="updated timestamp", limit=64)
    if not isinstance(entry.get("metadata"), dict):
        raise CaptureValidationError(
            "QUEUE_INVALID", "queue metadata must be an object"
        )

    claim = entry.get("claim")
    if state == "queued":
        if claim is not None:
            raise CaptureValidationError(
                "QUEUE_INVALID", "queued entry must not retain a claim"
            )
    else:
        _validate_queue_claim(claim)

    result = entry.get("result")
    if state == "completed":
        if not isinstance(result, dict):
            raise CaptureValidationError(
                "QUEUE_INVALID", "completed entry requires a result object"
            )
    elif result is not None:
        raise CaptureValidationError(
            "QUEUE_INVALID", "non-completed entry must not contain a result"
        )

    error = entry.get("error")
    if error is not None:
        if not isinstance(error, dict) or not isinstance(error.get("retryable"), bool):
            raise CaptureValidationError(
                "QUEUE_INVALID", "queue error object is invalid"
            )
        _queue_text(error.get("message"), field="error message", limit=4096)
    if state == "failed" and error is None:
        raise CaptureValidationError(
            "QUEUE_INVALID", "failed entry requires an error object"
        )
    if state in {"claimed", "completed"} and error is not None:
        raise CaptureValidationError(
            "QUEUE_INVALID", f"{state} entry must not contain an error"
        )

    action = entry.get("planned_action")
    if adapter_id == "filesystem":
        if action is not None:
            raise CaptureValidationError(
                "QUEUE_INVALID", "filesystem entry must not contain an action"
            )
    else:
        if not isinstance(action, dict):
            raise CaptureValidationError(
                "QUEUE_INVALID", "external entry requires a planned action"
            )
        _validate_planned_action(adapter_id, source, action)
    return entry


@dataclass
class CaptureQueueLock:
    """Atomic directory lock held by the process for one complete queue operation."""

    vault_root: Path
    timeout: float = 10.0
    stale_after: float = 3600.0
    poll_interval: float = 0.05
    force_stale_lock: bool = False

    def __post_init__(self) -> None:
        self.vault_root = canonical(self.vault_root)
        self.runtime = _safe_runtime_dir(self.vault_root)
        self.path = self.runtime / "queue.lock"
        self.owner_path = self.path / "owner.json"
        self.token = uuid.uuid4().hex
        self.acquired = False
        self._root_fd: int | None = None
        self._parent_fd: int | None = None
        self._lock_fd: int | None = None
        self._advisory_locked = False

    def _owner(self, lock_fd: int) -> dict[str, Any] | None:
        return _read_lock_owner_at(lock_fd)

    def _may_reap(self, now: float, lock_fd: int) -> bool:
        owner = self._owner(lock_fd)
        if owner is None:
            # The lock creator may still be between mkdir() and the owner write.
            # Unknown ownership therefore requires the explicit recovery flag.
            if not self.force_stale_lock:
                return False
            try:
                return now - os.fstat(lock_fd).st_mtime > self.stale_after
            except OSError:
                return False
        pid, started = owner.get("pid"), owner.get("started_epoch")
        if not isinstance(pid, int) or not isinstance(started, (int, float)):
            return False
        if now - float(started) <= self.stale_after:
            return False
        if self.force_stale_lock:
            return True
        return (
            owner.get("host") == socket.gethostname() and _process_alive(pid) is False
        )

    def acquire(self) -> None:
        if self.acquired:
            return
        deadline = time.monotonic() + max(0.0, self.timeout)
        try:
            root_fd = _open_lock_root_fd(self.vault_root)
        except OSError as exc:
            if isinstance(exc, _PlatformConfinementUnavailable):
                raise CaptureValidationError(
                    "UNSUPPORTED_PLATFORM", _UNSUPPORTED_PLATFORM_MESSAGE
                ) from exc
            raise CaptureError(
                "QUEUE_LOCK_FAILED", f"cannot pin capture vault root: {exc}"
            ) from exc
        self._root_fd = root_fd
        try:
            while True:
                try:
                    advisory_acquired = _try_vault_advisory_lock(root_fd)
                except OSError as exc:
                    raise CaptureError(
                        "QUEUE_LOCK_FAILED",
                        f"cannot acquire capture advisory lock: {exc}",
                    ) from exc
                if advisory_acquired:
                    break
                if time.monotonic() >= deadline:
                    raise CaptureConflict(
                        "QUEUE_LOCK_TIMEOUT",
                        "capture queue is locked by pid=unknown",
                    )
                time.sleep(self.poll_interval)
            self._advisory_locked = True
            try:
                parent_fd = _open_lock_parent_from_root_fd(
                    root_fd,
                    (".vault-meta", "capture"),
                    create=True,
                )
            except OSError as exc:
                raise CaptureError(
                    "QUEUE_LOCK_FAILED", f"cannot pin capture lock parent: {exc}"
                ) from exc
            self._parent_fd = parent_fd
            while True:
                try:
                    os.mkdir("queue.lock", mode=0o700, dir_fd=parent_fd)
                    try:
                        os.fsync(parent_fd)
                    except OSError:
                        pass
                except FileExistsError:
                    observed_owner: dict[str, Any] = {}
                    try:
                        existing_fd = _open_lock_directory_at(parent_fd, "queue.lock")
                    except FileNotFoundError:
                        continue
                    except OSError:
                        existing_fd = None
                    if existing_fd is not None:
                        try:
                            observed_owner = self._owner(existing_fd) or {}
                            if self._may_reap(time.time(), existing_fd):
                                if not _lock_entry_matches(
                                    parent_fd, "queue.lock", existing_fd
                                ):
                                    raise CaptureConflict(
                                        "QUEUE_LOCK_OWNERSHIP_LOST",
                                        "capture queue lock changed during stale-lock inspection",
                                    )
                                quarantine_name = f"queue.lock.reaping-{os.getpid()}-{uuid.uuid4().hex}"
                                os.rename(
                                    "queue.lock",
                                    quarantine_name,
                                    src_dir_fd=parent_fd,
                                    dst_dir_fd=parent_fd,
                                )
                                if not _lock_entry_matches(
                                    parent_fd, quarantine_name, existing_fd
                                ):
                                    raise CaptureConflict(
                                        "QUEUE_LOCK_OWNERSHIP_LOST",
                                        "capture queue lock changed during stale-lock quarantine",
                                    )
                                try:
                                    _remove_lock_directory_at(
                                        parent_fd, quarantine_name, existing_fd
                                    )
                                except _LockIdentityChanged as exc:
                                    raise CaptureConflict(
                                        "QUEUE_LOCK_OWNERSHIP_LOST",
                                        "capture lock quarantine changed before removal",
                                    ) from exc
                                except OSError:
                                    # Unknown entries remain in a confined, unique
                                    # quarantine; no recursive path walk is allowed.
                                    pass
                                continue
                        finally:
                            os.close(existing_fd)
                    if time.monotonic() >= deadline:
                        raise CaptureConflict(
                            "QUEUE_LOCK_TIMEOUT",
                            "capture queue is locked by "
                            f"pid={observed_owner.get('pid', 'unknown')}",
                        )
                    time.sleep(self.poll_interval)
                    continue
                except OSError as exc:
                    raise CaptureError(
                        "QUEUE_LOCK_FAILED", f"cannot acquire queue lock: {exc}"
                    ) from exc

                try:
                    lock_fd = _open_lock_directory_at(parent_fd, "queue.lock")
                except OSError as exc:
                    raise CaptureError(
                        "QUEUE_LOCK_FAILED",
                        f"cannot pin newly created capture lock: {exc}",
                    ) from exc
                self._lock_fd = lock_fd
                if not _lock_entry_matches(parent_fd, "queue.lock", lock_fd):
                    raise CaptureConflict(
                        "QUEUE_LOCK_OWNERSHIP_LOST",
                        "new capture queue lock was concurrently replaced",
                    )
                owner = {
                    "schema": "claude-obsidian.capture-lock.v1",
                    "pid": os.getpid(),
                    "host": socket.gethostname(),
                    "token": self.token,
                    "started_epoch": time.time(),
                }
                try:
                    _write_lock_owner_at(lock_fd, owner)
                except Exception as exc:
                    try:
                        _remove_lock_directory_at(parent_fd, "queue.lock", lock_fd)
                    except (OSError, _LockIdentityChanged):
                        pass
                    raise CaptureError(
                        "QUEUE_LOCK_FAILED", f"cannot write capture lock owner: {exc}"
                    ) from exc
                self.acquired = True
                return
        except BaseException:
            if not self.acquired:
                self._close_descriptors()
            raise

    def duplicate_runtime_fd(self) -> int:
        """Duplicate the exact capture directory held for this queue operation."""

        if not self.acquired or self._parent_fd is None:
            raise CaptureError(
                "QUEUE_LOCK_NOT_HELD",
                "capture runtime is unavailable outside a held queue lock",
            )
        return os.dup(self._parent_fd)

    def _close_descriptors(self) -> None:
        if self._lock_fd is not None:
            os.close(self._lock_fd)
            self._lock_fd = None
        if self._parent_fd is not None:
            os.close(self._parent_fd)
            self._parent_fd = None
        if self._root_fd is not None:
            if self._advisory_locked:
                _release_vault_advisory_lock(self._root_fd)
                self._advisory_locked = False
            os.close(self._root_fd)
            self._root_fd = None

    def release(self) -> None:
        if not self.acquired:
            return
        parent_fd, lock_fd = self._parent_fd, self._lock_fd
        try:
            if parent_fd is None or lock_fd is None:
                raise CaptureConflict(
                    "QUEUE_LOCK_OWNERSHIP_LOST",
                    "capture queue lock descriptors were lost",
                )
            owner = self._owner(lock_fd)
            if owner is None or owner.get("token") != self.token:
                raise CaptureConflict(
                    "QUEUE_LOCK_OWNERSHIP_LOST", "capture queue lock owner changed"
                )
            try:
                _remove_lock_directory_at(parent_fd, "queue.lock", lock_fd)
            except _LockIdentityChanged as exc:
                raise CaptureConflict(
                    "QUEUE_LOCK_OWNERSHIP_LOST",
                    "capture queue lock path changed before release",
                ) from exc
            except OSError as exc:
                raise CaptureError(
                    "QUEUE_LOCK_RELEASE_FAILED", f"cannot release queue lock: {exc}"
                ) from exc
        finally:
            self.acquired = False
            self._close_descriptors()

    def __enter__(self) -> "CaptureQueueLock":
        self.acquire()
        return self

    def __exit__(self, _exc_type: Any, _exc: Any, _traceback: Any) -> None:
        self.release()


class CaptureQueue:
    """Durable, idempotent JSON queue scoped to one vault."""

    def __init__(
        self,
        vault_root: Path,
        *,
        timeout: float = 10.0,
        stale_after: float = 3600.0,
        force_stale_lock: bool = False,
    ):
        self.vault_root = canonical(vault_root)
        self.runtime = _safe_runtime_dir(self.vault_root)
        self.path = self.runtime / "queue.json"
        self.backup_path = self.runtime / "queue.previous.json"
        self.timeout = timeout
        self.stale_after = stale_after
        self.force_stale_lock = force_stale_lock

    @staticmethod
    def _empty() -> dict[str, Any]:
        return {"schema": QUEUE_SCHEMA, "revision": 0, "entries": []}

    def lock(self) -> CaptureQueueLock:
        return CaptureQueueLock(
            self.vault_root,
            timeout=self.timeout,
            stale_after=self.stale_after,
            force_stale_lock=self.force_stale_lock,
        )

    @contextmanager
    def _locked_runtime(self) -> Iterator[int]:
        """Yield one duplicate of the runtime selected by the held queue lock."""

        with self.lock() as lock:
            runtime_fd = lock.duplicate_runtime_fd()
            try:
                yield runtime_fd
            finally:
                os.close(runtime_fd)

    @staticmethod
    def _validate_document(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict) or value.get("schema") != QUEUE_SCHEMA:
            raise CaptureValidationError(
                "QUEUE_INVALID", f"capture queue must use {QUEUE_SCHEMA}"
            )
        revision = value.get("revision")
        if (
            not isinstance(revision, int)
            or isinstance(revision, bool)
            or revision < 0
            or not isinstance(value.get("entries"), list)
        ):
            raise CaptureValidationError(
                "QUEUE_INVALID", "capture queue has invalid revision or entries"
            )
        if len(value["entries"]) > MAX_QUEUE_ENTRIES:
            raise CaptureValidationError(
                "QUEUE_ENTRY_LIMIT",
                f"capture queue exceeds the {MAX_QUEUE_ENTRIES}-entry limit",
            )
        ids: set[str] = set()
        keys: set[str] = set()
        for raw_entry in value["entries"]:
            entry = _validate_queue_entry(raw_entry)
            key = entry["idempotency_key"]
            if entry["id"] in ids or key in keys:
                raise CaptureValidationError(
                    "QUEUE_INVALID", "duplicate queue id or idempotency key"
                )
            ids.add(entry["id"])
            keys.add(key)
        return value

    def _read_document(self, runtime_fd: int, name: str) -> dict[str, Any]:
        try:
            raw = _read_runtime_regular(
                runtime_fd,
                name,
                limit=MAX_QUEUE_BYTES,
                missing_ok=False,
            )
            assert raw is not None
            value = _strict_json_loads(raw.decode("utf-8"))
        except TransactionValidationError as exc:
            # An oversized regular queue is recoverable corruption when a
            # bounded predecessor exists.  Unsafe paths (including symlinks)
            # remain hard failures and are never hidden by a backup.
            if exc.code != "VAULT_FILE_TOO_LARGE":
                raise
            raise CaptureValidationError(
                "QUEUE_SIZE_LIMIT",
                f"capture queue exceeds the {MAX_QUEUE_BYTES}-byte limit",
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise CaptureValidationError(
                "QUEUE_INVALID", f"cannot read capture queue: {exc}"
            ) from exc
        document = self._validate_document(value)
        if len(_json_bytes(document)) > MAX_QUEUE_BYTES:
            raise CaptureValidationError(
                "QUEUE_SIZE_LIMIT",
                "capture queue exceeds the canonical serialized-size limit",
            )
        return document

    def _load_locked(self, runtime_fd: int, *, recover: bool) -> dict[str, Any]:
        if not _runtime_entry_exists(runtime_fd, "queue.json"):
            return self._empty()
        try:
            return self._read_document(runtime_fd, "queue.json")
        except CaptureValidationError:
            backup_exists = _runtime_entry_exists(runtime_fd, "queue.previous.json")
            if not recover or not backup_exists:
                raise
            recovered = self._read_document(runtime_fd, "queue.previous.json")
            self._write_runtime(runtime_fd, "queue.json", _json_bytes(recovered))
            return recovered

    def _write_runtime(self, runtime_fd: int, name: str, data: bytes) -> None:
        _atomic_runtime_write(runtime_fd, name, data)

    def _save_locked(self, runtime_fd: int, value: dict[str, Any]) -> None:
        document = self._validate_document(value)
        serialized = _json_bytes(document)
        if len(serialized) > MAX_QUEUE_BYTES:
            raise CaptureValidationError(
                "QUEUE_SIZE_LIMIT",
                f"capture queue exceeds the {MAX_QUEUE_BYTES}-byte limit",
            )
        # Complete every new-state bound check before rotating the known-good
        # predecessor.  A rejected mutation therefore changes neither file.
        if _runtime_entry_exists(runtime_fd, "queue.json"):
            # Only preserve a known-good predecessor. A corrupt primary never
            # replaces the recovery copy.
            current = _read_runtime_regular(
                runtime_fd,
                "queue.json",
                limit=MAX_QUEUE_BYTES,
                missing_ok=False,
            )
            assert current is not None
        else:
            current = None
        if current is not None:
            try:
                self._validate_document(_strict_json_loads(current.decode("utf-8")))
            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
                ValueError,
                CaptureValidationError,
            ):
                pass
            else:
                self._write_runtime(runtime_fd, "queue.previous.json", current)
        self._write_runtime(runtime_fd, "queue.json", serialized)

    def list(self, *, state: str | None = None) -> list[dict[str, Any]]:
        if state is not None and state not in QUEUE_STATES:
            raise CaptureValidationError(
                "QUEUE_STATE_INVALID", f"unknown queue state: {state}"
            )
        with self._locked_runtime() as runtime_fd:
            document = self._load_locked(runtime_fd, recover=True)
            values = [
                entry
                for entry in document["entries"]
                if state is None or entry["state"] == state
            ]
            return cast(list[dict[str, Any]], json.loads(json.dumps(values)))

    def enqueue(
        self,
        adapter: str,
        source: str,
        *,
        source_sha256: str | None = None,
        planned_action: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        _adapter(adapter)
        if (
            not isinstance(source, str)
            or not source
            or len(source) > 8192
            or any(unicodedata.category(char).startswith("C") for char in source)
        ):
            raise CaptureValidationError(
                "QUEUE_SOURCE_INVALID", "queue source must be a bounded string"
            )
        if source_sha256 is not None and (
            len(source_sha256) != 64
            or any(char not in "0123456789abcdef" for char in source_sha256)
        ):
            raise CaptureValidationError(
                "SOURCE_IDENTITY_INVALID", "source SHA-256 must be lowercase hex"
            )
        if adapter in {"url", "youtube"}:
            source = validate_https_url(source)
        metadata_value = _json_object(metadata, field="metadata")
        planned_value = _json_object(planned_action, field="planned_action")
        if adapter == "filesystem" and planned_value:
            raise CaptureValidationError(
                "QUEUE_ACTION_INVALID",
                "filesystem queue items must not contain an external action",
            )
        if adapter != "filesystem" and not planned_value:
            raise CaptureValidationError(
                "EXTERNAL_ACTION_REQUIRED",
                "non-filesystem queue items require an explicit inert action plan",
            )
        if planned_value:
            _validate_planned_action(adapter, source, planned_value)
        canonical_payload = {
            "adapter": adapter,
            "source": source,
            "source_sha256": source_sha256,
            "metadata": metadata_value,
        }
        key = (
            idempotency_key
            or source_sha256
            or sha256_bytes(
                json.dumps(
                    canonical_payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
            )
        )
        if not isinstance(key, str) or not key or len(key) > 512 or "\x00" in key:
            raise CaptureValidationError(
                "IDEMPOTENCY_KEY_INVALID", "invalid idempotency key"
            )
        with self._locked_runtime() as runtime_fd:
            document = self._load_locked(runtime_fd, recover=True)
            for entry in document["entries"]:
                if entry["idempotency_key"] == key:
                    return cast(dict[str, Any], json.loads(json.dumps(entry)))
            now = _utc_now()
            item_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
            entry = {
                "id": item_id,
                "idempotency_key": key,
                "adapter": adapter,
                "source": source,
                "source_sha256": source_sha256,
                "state": "queued",
                "attempts": 0,
                "created_at": now,
                "updated_at": now,
                "claim": None,
                "planned_action": planned_value or None,
                "metadata": metadata_value,
                "result": None,
                "error": None,
            }
            document["entries"].append(entry)
            document["revision"] += 1
            self._save_locked(runtime_fd, document)
            return cast(dict[str, Any], json.loads(json.dumps(entry)))

    @staticmethod
    def _entry(document: dict[str, Any], item_id: str) -> dict[str, Any]:
        for entry in document["entries"]:
            if entry["id"] == item_id:
                return cast(dict[str, Any], entry)
        raise CaptureValidationError(
            "QUEUE_ITEM_MISSING", f"queue item does not exist: {item_id}"
        )

    def claim(
        self, item_id: str | None = None, *, worker: str | None = None
    ) -> dict[str, Any] | None:
        if worker is not None and (
            not isinstance(worker, str)
            or not worker
            or len(worker) > 256
            or any(unicodedata.category(char).startswith("C") for char in worker)
        ):
            raise CaptureValidationError(
                "QUEUE_WORKER_INVALID", "worker must be a bounded string"
            )
        with self._locked_runtime() as runtime_fd:
            document = self._load_locked(runtime_fd, recover=True)
            entry = None
            if item_id is None:
                entry = next(
                    (item for item in document["entries"] if item["state"] == "queued"),
                    None,
                )
                if entry is None:
                    return None
            else:
                entry = self._entry(document, item_id)
                if entry["state"] != "queued":
                    raise CaptureConflict(
                        "QUEUE_ITEM_NOT_QUEUED", f"queue item is {entry['state']}"
                    )
            now = _utc_now()
            entry["state"] = "claimed"
            entry["attempts"] += 1
            entry["updated_at"] = now
            entry["claim"] = {
                "token": uuid.uuid4().hex,
                "pid": os.getpid(),
                "host": socket.gethostname(),
                "worker": worker,
                "claimed_at": now,
                "claimed_epoch": time.time(),
            }
            entry["error"] = None
            document["revision"] += 1
            self._save_locked(runtime_fd, document)
            return cast(dict[str, Any], json.loads(json.dumps(entry)))

    @staticmethod
    def _assert_claim(entry: dict[str, Any], token: str) -> None:
        claim = entry.get("claim")
        if not isinstance(claim, dict) or claim.get("token") != token:
            raise CaptureConflict(
                "QUEUE_CLAIM_MISMATCH", "queue claim token does not match"
            )

    def complete(
        self, item_id: str, token: str, result: Mapping[str, Any]
    ) -> dict[str, Any]:
        desired = _json_object(result, field="result")
        with self._locked_runtime() as runtime_fd:
            document = self._load_locked(runtime_fd, recover=True)
            entry = self._entry(document, item_id)
            self._assert_claim(entry, token)
            if entry["state"] == "completed":
                if entry.get("result") != desired:
                    raise CaptureConflict(
                        "QUEUE_COMPLETION_CONFLICT", "completed result differs"
                    )
                return cast(dict[str, Any], json.loads(json.dumps(entry)))
            if entry["state"] != "claimed":
                raise CaptureConflict(
                    "QUEUE_ITEM_NOT_CLAIMED", f"queue item is {entry['state']}"
                )
            entry["state"] = "completed"
            entry["result"] = desired
            entry["error"] = None
            entry["updated_at"] = _utc_now()
            document["revision"] += 1
            self._save_locked(runtime_fd, document)
            return cast(dict[str, Any], json.loads(json.dumps(entry)))

    def fail(
        self,
        item_id: str,
        token: str,
        error: str,
        *,
        retryable: bool = True,
    ) -> dict[str, Any]:
        if not isinstance(error, str) or not error or len(error) > 4096:
            raise CaptureValidationError(
                "QUEUE_ERROR_INVALID", "error must be a bounded non-empty string"
            )
        with self._locked_runtime() as runtime_fd:
            document = self._load_locked(runtime_fd, recover=True)
            entry = self._entry(document, item_id)
            self._assert_claim(entry, token)
            desired = {"message": error, "retryable": bool(retryable)}
            if entry["state"] == "failed":
                if entry.get("error") != desired:
                    raise CaptureConflict(
                        "QUEUE_FAILURE_CONFLICT", "failed result differs"
                    )
                return cast(dict[str, Any], json.loads(json.dumps(entry)))
            if entry["state"] != "claimed":
                raise CaptureConflict(
                    "QUEUE_ITEM_NOT_CLAIMED", f"queue item is {entry['state']}"
                )
            entry["state"] = "failed"
            entry["error"] = desired
            entry["updated_at"] = _utc_now()
            document["revision"] += 1
            self._save_locked(runtime_fd, document)
            return cast(dict[str, Any], json.loads(json.dumps(entry)))

    def resume(
        self,
        item_id: str | None = None,
        *,
        include_failed: bool = True,
        stale_after: float = 3600.0,
        force: bool = False,
    ) -> builtins.list[dict[str, Any]]:
        """Requeue failed work and abandoned claims, never stealing a live claim by default."""

        if stale_after < 0:
            raise CaptureValidationError(
                "RESUME_POLICY_INVALID", "stale_after cannot be negative"
            )
        with self._locked_runtime() as runtime_fd:
            document = self._load_locked(runtime_fd, recover=True)
            candidates = (
                [self._entry(document, item_id)]
                if item_id is not None
                else document["entries"]
            )
            resumed: list[dict[str, Any]] = []
            now_epoch = time.time()
            for entry in candidates:
                resumable = (
                    entry["state"] == "failed"
                    and include_failed
                    and (force or bool((entry.get("error") or {}).get("retryable")))
                )
                if entry["state"] == "claimed":
                    claim = entry.get("claim") or {}
                    same_host = claim.get("host") == socket.gethostname()
                    pid = claim.get("pid")
                    claimed_epoch = claim.get("claimed_epoch")
                    dead_and_stale = (
                        same_host
                        and isinstance(pid, int)
                        and isinstance(claimed_epoch, (int, float))
                        and now_epoch - float(claimed_epoch) >= stale_after
                        and _process_alive(pid) is False
                    )
                    resumable = force or dead_and_stale
                if not resumable:
                    continue
                entry["state"] = "queued"
                entry["claim"] = None
                entry["result"] = None
                entry["updated_at"] = _utc_now()
                resumed.append(json.loads(json.dumps(entry)))
            if resumed:
                document["revision"] += 1
                self._save_locked(runtime_fd, document)
            return resumed

    def recover(self) -> dict[str, Any]:
        """Restore a malformed primary queue from its last valid predecessor."""

        with self._locked_runtime() as runtime_fd:
            return cast(
                dict[str, Any],
                json.loads(json.dumps(self._load_locked(runtime_fd, recover=True))),
            )


def propose_deletion(
    vault_root: Path, candidate: Path, *, reason: str
) -> dict[str, Any]:
    """Create a review-only deletion proposal. This function never unlinks anything."""

    root = canonical(vault_root)
    raw = Path(candidate).expanduser()
    joined = raw if raw.is_absolute() else root / raw
    lexical = Path(os.path.abspath(joined))
    try:
        relative_lexical = lexical.relative_to(root)
    except ValueError:
        raise CaptureValidationError(
            "PATH_OUTSIDE_VAULT", "deletion candidate escapes the vault"
        )
    current = root
    for part in relative_lexical.parts:
        current = current / part
        if current.is_symlink():
            raise CaptureValidationError(
                "DELETE_CANDIDATE_INVALID", "deletion candidate uses a symlink"
            )
    resolved = joined.resolve(strict=True)
    if not is_relative_to(resolved, root):
        raise CaptureValidationError(
            "PATH_OUTSIDE_VAULT", "deletion candidate escapes the vault"
        )
    if resolved.is_symlink() or not resolved.is_file():
        raise CaptureValidationError(
            "DELETE_CANDIDATE_INVALID", "deletion candidate must be a regular file"
        )
    if not isinstance(reason, str) or not reason.strip():
        raise CaptureValidationError(
            "DELETE_REASON_REQUIRED", "deletion proposal requires a reason"
        )
    return {
        "schema": PROPOSAL_SCHEMA,
        "id": hashlib.sha256(
            f"{resolved.relative_to(root).as_posix()}\0{reason}".encode("utf-8")
        ).hexdigest()[:24],
        "action": "delete",
        "path": resolved.relative_to(root).as_posix(),
        "source_sha256": source_identity(resolved),
        "reason": reason.strip(),
        "state": "review-required",
        "execute": False,
        "created_at": _utc_now(),
    }


__all__ = [
    "CaptureBudget",
    "CaptureBudgetExceeded",
    "CaptureConfig",
    "CaptureConflict",
    "CaptureError",
    "CaptureQueue",
    "CaptureQueueLock",
    "CaptureValidationError",
    "capture_filesystem",
    "capture_filesystem_batch",
    "discover_files",
    "load_adapter_manifest",
    "plan_filesystem_batch",
    "plan_external_action",
    "propose_deletion",
    "sniff_metadata",
    "source_identity",
    "validate_https_url",
    "validate_redirect_chain",
]
