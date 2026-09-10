#!/usr/bin/env python3
"""Hermetic operation-level transaction tests."""

from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
import socket
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import claude_obsidian.transaction as transaction_module
from claude_obsidian.transaction import (
    BUNDLE_SCHEMA,
    MutationLock,
    TransactionConflict,
    TransactionError,
    TransactionRecoveryError,
    TransactionValidationError,
    apply_bundle,
    inspect_bundle,
    recover_incomplete,
    sha256_file,
)


def make_vault(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / ".obsidian").mkdir()
    (root / "wiki").mkdir()
    (root / ".raw").mkdir()
    return root


def bundle(
    operation_id: str,
    writes: list[dict],
    expected: dict | None = None,
    *,
    operation_type: str = "generic",
) -> dict:
    preconditions = {write["path"]: None for write in writes}
    if expected is not None:
        preconditions.update(expected)
    return {
        "schema": BUNDLE_SCHEMA,
        "operation_id": operation_id,
        "operation_type": operation_type,
        "expected_hashes": preconditions,
        "writes": writes,
    }


def test_apply_and_idempotent_result() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        operation = bundle(
            "create-two",
            [
                {"path": "wiki/A.md", "mode": "create", "content": "# A\n"},
                {"path": "wiki/B.md", "mode": "create", "content": "# B\n"},
            ],
        )
        result = apply_bundle(vault, operation)
        assert result["changed_paths"] == ["wiki/A.md", "wiki/B.md"]
        assert (vault / "wiki/A.md").read_text() == "# A\n"
        assert apply_bundle(vault, operation) == result


def test_failure_rolls_back_every_write() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        a = vault / "wiki/A.md"
        a.write_text("old\n", encoding="utf-8")
        before = sha256_file(a)
        try:
            apply_bundle(
                vault,
                bundle(
                    "rollback",
                    [
                        {"path": "wiki/A.md", "mode": "replace", "content": "new\n"},
                        {"path": "wiki/B.md", "mode": "create", "content": "new B\n"},
                    ],
                    {"wiki/A.md": before},
                ),
                fail_after=2,
            )
        except RuntimeError as exc:
            assert "injected failure" in str(exc)
        else:
            raise AssertionError("failure injection must raise")
        assert sha256_file(a) == before
        assert not (vault / "wiki/B.md").exists()
        journal = json.loads(
            (vault / ".vault-meta/transactions/rollback/journal.json").read_text()
        )
        assert journal["state"] == "rolled-back"


def test_rolled_back_operation_can_be_retried() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        operation = bundle(
            "retry-after-rollback",
            [
                {"path": "wiki/A.md", "mode": "create", "content": "# A\n"},
                {"path": "wiki/B.md", "mode": "create", "content": "# B\n"},
            ],
        )
        try:
            apply_bundle(vault, operation, fail_after=1)
        except RuntimeError:
            pass
        else:
            raise AssertionError("failure injection must roll back")
        assert not (vault / "wiki/A.md").exists()
        assert not (vault / "wiki/B.md").exists()

        result = apply_bundle(vault, operation)
        assert result["status"] == "complete"
        assert (vault / "wiki/A.md").read_text(encoding="utf-8") == "# A\n"
        assert (vault / "wiki/B.md").read_text(encoding="utf-8") == "# B\n"


def test_expected_hash_conflict_changes_nothing() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        target = vault / "wiki/A.md"
        target.write_text("current\n", encoding="utf-8")
        try:
            apply_bundle(
                vault,
                bundle(
                    "conflict",
                    [{"path": "wiki/A.md", "mode": "replace", "content": "new\n"}],
                    {"wiki/A.md": "0" * 64},
                ),
            )
        except TransactionConflict as exc:
            assert exc.code == "EXPECTED_HASH_MISMATCH"
        else:
            raise AssertionError("hash conflict must fail")
        assert target.read_text() == "current\n"


def test_read_preconditions_are_bound_into_plan_approval() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        original = bundle(
            "read-precondition-approval",
            [{"path": "wiki/A.md", "mode": "create", "content": "# A\n"}],
        )
        reviewed = inspect_bundle(vault, original)
        with_probe = json.loads(json.dumps(original))
        with_probe["read_preconditions"] = {".raw/reviewed-input": None}
        probed = inspect_bundle(vault, with_probe)
        assert reviewed["changed_paths"] == probed["changed_paths"]
        assert reviewed["hashes"] == probed["hashes"]
        assert reviewed["modes"] == probed["modes"]
        assert reviewed["approval_sha256"] != probed["approval_sha256"]
        try:
            apply_bundle(
                vault,
                with_probe,
                approved_plan_sha256=reviewed["approval_sha256"],
            )
        except TransactionValidationError as exc:
            assert exc.code == "PLAN_CHANGED"
        else:
            raise AssertionError("read preconditions must be approval-bound")
        assert not (vault / "wiki/A.md").exists()


def test_every_write_requires_a_canonical_precondition() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        target = vault / "wiki/A.md"
        target.write_text("current\n", encoding="utf-8")
        missing = {
            "schema": BUNDLE_SCHEMA,
            "operation_id": "missing-precondition",
            "operation_type": "generic",
            "expected_hashes": {},
            "writes": [{"path": "wiki/A.md", "mode": "replace", "content": "new\n"}],
        }
        try:
            apply_bundle(vault, missing)
        except TransactionValidationError as exc:
            assert exc.code == "MISSING_EXPECTED_HASH"
        else:
            raise AssertionError("a missing write precondition must fail")
        assert target.read_text(encoding="utf-8") == "current\n"

        noncanonical = bundle(
            "noncanonical-precondition",
            [{"path": "wiki/A.md", "mode": "replace", "content": "new\n"}],
            {"wiki/A.md": sha256_file(target)},
        )
        noncanonical["expected_hashes"] = {"wiki/./A.md": sha256_file(target)}
        try:
            inspect_bundle(vault, noncanonical)
        except TransactionValidationError as exc:
            assert exc.code == "NONCANONICAL_WRITE_PATH"
        else:
            raise AssertionError("noncanonical expected paths must fail")

        alias = bundle(
            "noncanonical-write",
            [{"path": "wiki/../.raw/source.md", "mode": "create", "content": "one"}],
        )
        try:
            inspect_bundle(vault, alias)
        except TransactionValidationError as exc:
            assert exc.code == "INVALID_WRITE_PATH"
        else:
            raise AssertionError("noncanonical write aliases must fail")

        for unsafe_id in (".", "..", "../outside", "/absolute"):
            unsafe = bundle(
                unsafe_id,
                [{"path": "wiki/unsafe.md", "mode": "create", "content": "unsafe\n"}],
            )
            try:
                inspect_bundle(vault, unsafe)
            except TransactionValidationError as exc:
                assert exc.code == "INVALID_OPERATION_ID"
            else:
                raise AssertionError(f"unsafe operation ID must fail: {unsafe_id}")


def test_paths_require_nfc_and_file_bundles_reject_duplicate_json_keys() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        nfd_path = "wiki/Cafe\u0301.md"
        operation = bundle(
            "nfd-alias",
            [{"path": nfd_path, "mode": "create", "content": "# Alias\n"}],
        )
        try:
            inspect_bundle(vault, operation)
        except TransactionValidationError as exc:
            assert exc.code == "NONCANONICAL_UNICODE_PATH"
        else:
            raise AssertionError("NFD paths must fail before filesystem aliasing")
        assert not (vault / nfd_path).exists()

        nfc_path = "wiki/Caf\u00e9.md"
        valid = bundle(
            "nfc-path",
            [{"path": nfc_path, "mode": "create", "content": "# Canonical\n"}],
        )
        assert inspect_bundle(vault, valid)["changed_paths"] == [nfc_path]

        folded_collision = bundle(
            "post-casefold-unicode-collision",
            [
                {"path": "wiki/Ś.md", "mode": "create", "content": "# One\n"},
                {"path": "wiki/ſ́.md", "mode": "create", "content": "# Two\n"},
            ],
        )
        try:
            inspect_bundle(vault, folded_collision)
        except TransactionValidationError as exc:
            assert exc.code == "CASEFOLD_PATH_COLLISION"
        else:
            raise AssertionError("post-casefold canonical aliases must collide")

        overlong_path = "wiki/" + "/".join(["a" * 200] * 6) + ".md"
        try:
            inspect_bundle(
                vault,
                bundle(
                    "overlong-portable-path",
                    [{"path": overlong_path, "mode": "create", "content": ""}],
                ),
            )
        except TransactionValidationError as exc:
            assert exc.code == "WRITE_PATH_TOO_LONG"
        else:
            raise AssertionError("transaction paths must fit the portability envelope")

        bundle_path = base / "ambiguous.json"
        bundle_path.write_text(
            "{"
            '"schema":"claude-obsidian.transaction.v1",'
            '"operation_id":"duplicate-json",'
            '"operation_type":"generic",'
            '"expected_hashes":{"wiki/A.md":null},'
            '"writes":[{"path":"wiki/A.md","mode":"create",'
            '"content":"# Benign\\n","content":"# Replaced\\n"}]}',
            encoding="utf-8",
        )
        try:
            inspect_bundle(vault, bundle_path)
        except TransactionValidationError as exc:
            assert exc.code == "INVALID_BUNDLE"
            assert "duplicate JSON object key" in str(exc)
        else:
            raise AssertionError("duplicate bundle keys must fail closed")

        nonfinite_path = base / "nonfinite.json"
        for number in ("NaN", "1e999"):
            nonfinite_path.write_text(
                f'{{"schema":{number},"operation_id":"nonfinite"}}', encoding="utf-8"
            )
            try:
                inspect_bundle(vault, nonfinite_path)
            except TransactionValidationError as exc:
                assert exc.code == "INVALID_BUNDLE"
            else:
                raise AssertionError("non-finite JSON numbers must fail closed")

        for number in (float("nan"), float("inf"), float("-inf")):
            mapped = bundle(
                "mapped-nonfinite",
                [{"path": "wiki/mapped.md", "mode": "create", "content": "x\n"}],
            )
            mapped["metadata"] = {"number": number}
            try:
                inspect_bundle(vault, mapped)
            except TransactionValidationError as exc:
                assert exc.code == "INVALID_BUNDLE"
            else:
                raise AssertionError(
                    "Mapping bundles must stay in the finite JSON domain"
                )


def test_mapping_bundle_is_a_deep_snapshot_before_hash_and_apply() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        operation = bundle(
            "mapping-snapshot",
            [{"path": "wiki/snapshot.md", "mode": "create", "content": "reviewed\n"}],
        )
        original_hash = transaction_module._canonical_json_hash
        calls = 0

        def mutate_caller_after_hash(value: object) -> str:
            nonlocal calls
            result = original_hash(value)
            calls += 1
            if calls == 1:
                operation["writes"][0]["content"] = "caller mutation\n"
            return result

        transaction_module._canonical_json_hash = mutate_caller_after_hash
        try:
            apply_bundle(vault, operation)
        finally:
            transaction_module._canonical_json_hash = original_hash
        assert (vault / "wiki/snapshot.md").read_text(encoding="utf-8") == "reviewed\n"


def test_bundle_files_are_bounded_regular_and_no_follow() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        operation = bundle(
            "external-bundle",
            [{"path": "wiki/External.md", "mode": "create", "content": "# External\n"}],
        )
        regular = base / "bundle.json"
        regular.write_text(json.dumps(operation), encoding="utf-8")
        assert inspect_bundle(vault, regular)["valid"] is True

        symlink = base / "bundle-link.json"
        symlink.symlink_to(regular)
        for unsafe in (symlink, base):
            try:
                inspect_bundle(vault, unsafe)
            except TransactionValidationError as exc:
                assert exc.code == "INVALID_BUNDLE"
            else:
                raise AssertionError(f"nonregular bundle input must fail: {unsafe}")

        if hasattr(os, "mkfifo"):
            fifo = base / "bundle.fifo"
            os.mkfifo(fifo)
            try:
                inspect_bundle(vault, fifo)
            except TransactionValidationError as exc:
                assert exc.code == "INVALID_BUNDLE"
            else:
                raise AssertionError("FIFO bundle must fail without blocking")

        original_limit = transaction_module.MAX_TRANSACTION_BUNDLE_BYTES
        try:
            transaction_module.MAX_TRANSACTION_BUNDLE_BYTES = 128
            oversized = base / "oversized.json"
            oversized.write_bytes(b"{" + b" " * 128 + b"}")
            try:
                inspect_bundle(vault, oversized)
            except TransactionValidationError as exc:
                assert exc.code == "INVALID_BUNDLE"
                assert "limit" in str(exc)
            else:
                raise AssertionError("oversized bundle input must fail")
        finally:
            transaction_module.MAX_TRANSACTION_BUNDLE_BYTES = original_limit


def test_write_cardinality_and_runtime_json_share_one_recovery_envelope() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        too_many = [
            {"path": f"wiki/Batch-{index:04d}.md", "mode": "create", "content": ""}
            for index in range(transaction_module.MAX_TRANSACTION_WRITES + 1)
        ]
        try:
            inspect_bundle(vault, bundle("too-many-writes", too_many))
        except TransactionValidationError as exc:
            assert exc.code == "TRANSACTION_WRITE_LIMIT"
        else:
            raise AssertionError("write cardinality must be bounded before journaling")
        assert not (vault / ".vault-meta").exists()

    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        original_writes = transaction_module.MAX_TRANSACTION_WRITES
        original_runtime = transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES
        try:
            transaction_module.MAX_TRANSACTION_WRITES = 4
            transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES = 16 * 1024
            writes = [
                {"path": f"wiki/Recover-{index}.md", "mode": "create", "content": ""}
                for index in range(4)
            ]
            operation = bundle("bounded-cardinality-recovery", writes)
            try:
                apply_bundle(vault, operation, fail_after=2)
            except RuntimeError:
                pass
            else:
                raise AssertionError("injected failure must exercise rollback")
            journal_path = (
                vault
                / ".vault-meta/transactions/bounded-cardinality-recovery/journal.json"
            )
            assert (
                journal_path.stat().st_size
                <= transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES
            )
            assert (
                json.loads(journal_path.read_text(encoding="utf-8"))["state"]
                == "rolled-back"
            )
            assert apply_bundle(vault, operation)["status"] == "complete"
        finally:
            transaction_module.MAX_TRANSACTION_WRITES = original_writes
            transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES = original_runtime

    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        original_runtime = transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES
        original_bundle = transaction_module.MAX_TRANSACTION_BUNDLE_BYTES
        try:
            transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES = 2 * 1024
            transaction_module.MAX_TRANSACTION_BUNDLE_BYTES = 16 * 1024
            operation = bundle(
                "bundle-runtime-envelope",
                [
                    {
                        "path": "wiki/Large-inline.md",
                        "mode": "create",
                        "content": "# Bound bundle\n" + "x" * 4096,
                    }
                ],
            )
            encoded = transaction_module._json_bytes(operation)
            assert len(encoded) > transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES
            assert len(encoded) <= transaction_module.MAX_TRANSACTION_BUNDLE_BYTES
            assert apply_bundle(vault, operation)["status"] == "complete"
            runtime = vault / ".vault-meta/transactions/bundle-runtime-envelope"
            assert (runtime / "bundle.json").stat().st_size > 2 * 1024
            assert (runtime / "journal.json").stat().st_size <= 2 * 1024
            assert (runtime / "changed-paths.json").stat().st_size <= 2 * 1024
        finally:
            transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES = original_runtime
            transaction_module.MAX_TRANSACTION_BUNDLE_BYTES = original_bundle

    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        original_runtime = transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES
        try:
            transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES = 512
            rejected = bundle(
                "journal-preflight-reject",
                [{"path": "wiki/Preflight.md", "mode": "create", "content": ""}],
            )
            try:
                apply_bundle(vault, rejected)
            except TransactionValidationError as exc:
                assert exc.code == "TRANSACTION_RUNTIME_STATE_TOO_LARGE"
            else:
                raise AssertionError("journal envelope must be proven before mutation")
            assert not (vault / "wiki/Preflight.md").exists()
            assert not (
                vault / ".vault-meta/transactions/journal-preflight-reject"
            ).exists()
        finally:
            transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES = original_runtime


def test_runtime_symlinks_and_reserved_lock_descendants_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        outside = base / "outside"
        outside.mkdir()
        (vault / ".vault-meta").symlink_to(outside, target_is_directory=True)
        operation = bundle(
            "meta-escape", [{"path": "wiki/A.md", "mode": "create", "content": "# A\n"}]
        )
        try:
            apply_bundle(vault, operation)
        except TransactionValidationError as exc:
            assert exc.code in {"PATH_OUTSIDE_VAULT", "SYMLINK_WRITE_PATH"}
        else:
            raise AssertionError("symlinked runtime metadata must fail")
        assert list(outside.iterdir()) == []
        assert not (vault / "wiki/A.md").exists()

    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        reserved = bundle(
            "reserved-lock-child",
            [
                {
                    "path": ".vault-meta/mutation.lock/extra",
                    "mode": "create",
                    "content": "bad\n",
                }
            ],
        )
        try:
            apply_bundle(vault, reserved)
        except TransactionValidationError as exc:
            assert exc.code == "RESERVED_WRITE_PATH"
        else:
            raise AssertionError("lock namespace descendants must be reserved")


def test_all_runtime_lock_cache_and_temp_paths_are_reserved() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        protected = (
            ".vault-meta/.address.lock",
            ".vault-meta/.address.lock.d/owner",
            ".vault-meta/.bm25.lock",
            ".vault-meta/.embed-cache.lock",
            ".vault-meta/.tiling.lock",
            ".vault-meta/.transport.json.tmp.ABC123",
            ".vault-meta/.wiki-lock.meta",
            ".vault-meta/.wiki-lock.meta.d/owner",
            ".vault-meta/embed-cache.123.tmp",
            ".vault-meta/tiling-cache.json",
            ".vault-meta/tiling-cache.123.tmp",
            ".vault-meta/transport.123.tmp",
        )
        for index, relative in enumerate(protected):
            operation = bundle(
                f"reserved-runtime-{index}",
                [{"path": relative, "mode": "create", "content": "blocked\n"}],
            )
            try:
                inspect_bundle(vault, operation)
            except TransactionValidationError as exc:
                assert exc.code == "RESERVED_WRITE_PATH", (relative, exc.code)
            else:
                raise AssertionError(f"runtime-owned path must be reserved: {relative}")


def test_product_runtime_and_declared_operation_scopes_are_enforced() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / ".git").mkdir()
        git_config = vault / ".git/config"
        git_config.write_text("[core]\n", encoding="utf-8")
        cases = (
            (
                bundle(
                    "git-internals",
                    [
                        {
                            "path": ".git/config",
                            "mode": "replace",
                            "content": "changed\n",
                        }
                    ],
                    {".git/config": sha256_file(git_config)},
                ),
                "RESERVED_WRITE_PATH",
            ),
            (
                bundle(
                    "capture-runtime",
                    [
                        {
                            "path": ".vault-meta/capture/queue.json",
                            "mode": "create",
                            "content": "{}\n",
                        }
                    ],
                ),
                "RESERVED_WRITE_PATH",
            ),
            (
                {
                    **bundle(
                        "save-outside-wiki",
                        [
                            {
                                "path": ".obsidian/app.json",
                                "mode": "create",
                                "content": "{}\n",
                            }
                        ],
                    ),
                    "operation_type": "save",
                },
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                {
                    **bundle(
                        "configuration-outside-mode",
                        [
                            {
                                "path": "wiki/config.json",
                                "mode": "create",
                                "content": "{}\n",
                            }
                        ],
                    ),
                    "operation_type": "configuration",
                },
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                {
                    **bundle(
                        "base-outside-wiki",
                        [
                            {
                                "path": ".obsidian/dashboard.base",
                                "mode": "create",
                                "content": "views: []\n",
                            }
                        ],
                    ),
                    "operation_type": "base",
                },
                "WRITE_SCOPE_VIOLATION",
            ),
        )
        for operation, expected_code in cases:
            try:
                inspect_bundle(vault, operation)
            except TransactionValidationError as exc:
                assert exc.code == expected_code, (exc.code, str(exc))
            else:
                raise AssertionError(f"expected {expected_code}")
        assert git_config.read_text(encoding="utf-8") == "[core]\n"
        assert not (vault / ".vault-meta").exists()
        assert not (vault / ".obsidian/app.json").exists()

        configuration = {
            **bundle(
                "valid-configuration",
                [
                    {
                        "path": ".vault-meta/mode.json",
                        "mode": "create",
                        "content": '{"mode":"generic"}\n',
                    }
                ],
            ),
            "operation_type": "configuration",
        }
        base_operation = {
            **bundle(
                "valid-base",
                [
                    {
                        "path": "wiki/bases/dashboard.base",
                        "mode": "create",
                        "content": "views: []\n",
                    }
                ],
            ),
            "operation_type": "base",
        }
        assert inspect_bundle(vault, configuration)["valid"] is True
        assert inspect_bundle(vault, base_operation)["valid"] is True


def test_operation_types_enforce_least_privilege_path_contracts() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / ".raw/.manifest.json").write_text(
            json.dumps({"version": 1, "sources": {}, "address_map": {}}),
            encoding="utf-8",
        )
        manifest_hash = sha256_file(vault / ".raw/.manifest.json")
        cases = (
            (
                bundle(
                    "canvas-manifest",
                    [
                        {
                            "path": ".raw/.manifest.json",
                            "mode": "replace",
                            "content": "{}\n",
                        }
                    ],
                    {".raw/.manifest.json": manifest_hash},
                    operation_type="canvas",
                ),
                "MANAGED_METADATA_COLLISION",
            ),
            (
                bundle(
                    "canvas-note",
                    [
                        {
                            "path": "wiki/sources/NotACanvas.md",
                            "mode": "create",
                            "content": "# no\n",
                        }
                    ],
                    operation_type="canvas",
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                bundle(
                    "base-note",
                    [
                        {
                            "path": "wiki/concepts/NotABase.md",
                            "mode": "create",
                            "content": "# no\n",
                        }
                    ],
                    operation_type="base",
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                bundle(
                    "fold-note",
                    [
                        {
                            "path": "wiki/concepts/NotAFold.md",
                            "mode": "create",
                            "content": "# no\n",
                        }
                    ],
                    operation_type="fold",
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                bundle(
                    "generic-raw",
                    [
                        {
                            "path": ".raw/source.md",
                            "mode": "create",
                            "content": "source\n",
                        }
                    ],
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                {
                    **bundle(
                        "save-managed-request",
                        [
                            {
                                "path": "wiki/Page.md",
                                "mode": "create",
                                "content": "# Page\n",
                            }
                        ],
                        operation_type="save",
                    ),
                    "address_requests": [{"path": "wiki/Page.md", "prefix": "c"}],
                },
                "MANAGED_REQUEST_SCOPE_VIOLATION",
            ),
            (
                bundle(
                    "setup-arbitrary-root",
                    [
                        {
                            "path": "arbitrary-root.txt",
                            "mode": "create",
                            "content": "no\n",
                        }
                    ],
                    operation_type="setup",
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                bundle(
                    "migration-unscoped-plugin",
                    [
                        {
                            "path": ".obsidian/plugins/unscoped/main.js",
                            "mode": "create",
                            "content": "no\n",
                        }
                    ],
                    operation_type="migration",
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                bundle(
                    "setup-unscoped-wiki",
                    [
                        {
                            "path": "wiki/arbitrary.md",
                            "mode": "create",
                            "content": "# no\n",
                        }
                    ],
                    operation_type="setup",
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
            (
                bundle(
                    "migration-unscoped-meta",
                    [
                        {
                            "path": ".vault-meta/arbitrary.json",
                            "mode": "create",
                            "content": "{}\n",
                        }
                    ],
                    operation_type="migration",
                ),
                "WRITE_SCOPE_VIOLATION",
            ),
        )
        for operation, expected_code in cases:
            try:
                inspect_bundle(vault, operation)
            except TransactionValidationError as exc:
                assert exc.code == expected_code, (expected_code, exc.code, str(exc))
            else:
                raise AssertionError(
                    f"operation scope should reject {operation['operation_id']}"
                )

        (vault / "wiki/index.md").write_text("# Index\n", encoding="utf-8")
        (vault / "wiki/log.md").write_text("# Log\n", encoding="utf-8")
        fold = bundle(
            "valid-fold",
            [
                {
                    "path": "wiki/folds/fold-k1-from-a-to-b-n2.md",
                    "mode": "create",
                    "content": "# Fold\n",
                },
                {
                    "path": "wiki/index.md",
                    "mode": "replace",
                    "content": "# Index\n- Fold\n",
                },
                {
                    "path": "wiki/log.md",
                    "mode": "replace",
                    "content": "# Log\n- Fold\n",
                },
            ],
            {
                "wiki/index.md": sha256_file(vault / "wiki/index.md"),
                "wiki/log.md": sha256_file(vault / "wiki/log.md"),
            },
            operation_type="fold",
        )
        assert inspect_bundle(vault, fold)["valid"] is True

        incomplete_fold = dict(fold)
        incomplete_fold["operation_id"] = "incomplete-fold"
        incomplete_fold["writes"] = fold["writes"][:1]
        incomplete_fold["expected_hashes"] = {
            "wiki/folds/fold-k1-from-a-to-b-n2.md": None
        }
        try:
            inspect_bundle(vault, incomplete_fold)
        except TransactionValidationError as exc:
            assert exc.code == "WRITE_SCOPE_VIOLATION"
        else:
            raise AssertionError("fold must couple the fold page, index, and log")


def test_casefold_aliases_and_bundle_collisions_fail_portably() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        aliases = (
            ".GIT/config",
            ".VAULT-META/MUTATION.LOCK/owner.json",
            ".RAW/payload",
            "Wiki/Page.md",
        )
        for index, relative in enumerate(aliases):
            operation = {
                **bundle(
                    f"case-alias-{index}",
                    [{"path": relative, "mode": "create", "content": "blocked\n"}],
                ),
                "operation_type": "setup" if relative == ".RAW/payload" else "generic",
            }
            try:
                inspect_bundle(vault, operation)
            except TransactionValidationError as exc:
                assert exc.code in {"CASEFOLD_PATH_ALIAS", "RESERVED_WRITE_PATH"}, (
                    relative,
                    exc.code,
                )
            else:
                raise AssertionError(f"casefold policy alias must fail: {relative}")

        collision = bundle(
            "case-collision",
            [
                {"path": "wiki/Page.md", "mode": "create", "content": "one\n"},
                {"path": "wiki/page.md", "mode": "create", "content": "two\n"},
            ],
        )
        try:
            inspect_bundle(vault, collision)
        except TransactionValidationError as exc:
            assert exc.code == "CASEFOLD_PATH_COLLISION"
        else:
            raise AssertionError("case-colliding writes must fail on every platform")

        original_limit = transaction_module.MAX_PORTABLE_SIBLING_ENTRIES
        try:
            transaction_module.MAX_PORTABLE_SIBLING_ENTRIES = 1
            try:
                inspect_bundle(
                    vault,
                    bundle(
                        "bounded-sibling-enumeration",
                        [
                            {
                                "path": "wiki/new.md",
                                "mode": "create",
                                "content": "new\n",
                            }
                        ],
                    ),
                )
            except TransactionValidationError as exc:
                assert exc.code == "VAULT_DIRECTORY_LIMIT", (exc.code, str(exc))
            else:
                raise AssertionError("portable sibling enumeration must be bounded")
        finally:
            transaction_module.MAX_PORTABLE_SIBLING_ENTRIES = original_limit


def test_transaction_size_limits_match_recovery_and_reject_nonregular_content() -> None:
    names = (
        "MAX_TRANSACTION_FILE_BYTES",
        "MAX_TRANSACTION_TOTAL_BYTES",
        "MAX_RECOVERY_BACKUP_BYTES",
        "MAX_RECOVERY_TOTAL_BACKUP_BYTES",
    )
    original_limits = {name: getattr(transaction_module, name) for name in names}
    try:
        transaction_module.MAX_TRANSACTION_FILE_BYTES = 64
        transaction_module.MAX_TRANSACTION_TOTAL_BYTES = 128
        transaction_module.MAX_RECOVERY_BACKUP_BYTES = 64
        transaction_module.MAX_RECOVERY_TOTAL_BACKUP_BYTES = 128
        with tempfile.TemporaryDirectory() as td:
            vault = make_vault(Path(td) / "vault")
            oversized = vault / "wiki/Oversized.md"
            oversized.write_bytes(b"x" * 65)
            operation = bundle(
                "oversized-original",
                [
                    {
                        "path": "wiki/Oversized.md",
                        "mode": "replace",
                        "content": "small\n",
                    }
                ],
                {"wiki/Oversized.md": sha256_file(oversized)},
            )
            try:
                inspect_bundle(vault, operation)
            except TransactionValidationError as exc:
                assert exc.code == "TRANSACTION_FILE_TOO_LARGE"
            else:
                raise AssertionError(
                    "an unrecoverable oversized predecessor must be rejected"
                )
            assert oversized.read_bytes() == b"x" * 65
            assert not (vault / ".vault-meta").exists()

            inline = bundle(
                "oversized-inline",
                [{"path": "wiki/Inline.md", "mode": "create", "content": "y" * 65}],
            )
            try:
                inspect_bundle(vault, inline)
            except TransactionValidationError as exc:
                assert exc.code == "TRANSACTION_FILE_TOO_LARGE"
            else:
                raise AssertionError("oversized inline content must be rejected")

            content_directory = Path(td) / "content-directory"
            content_directory.mkdir()
            nonregular = bundle(
                "nonregular-content",
                [
                    {
                        "path": "wiki/Directory.md",
                        "mode": "create",
                        "content_file": str(content_directory),
                        "sha256": "0" * 64,
                    }
                ],
            )
            try:
                inspect_bundle(vault, nonregular)
            except TransactionValidationError as exc:
                assert exc.code == "CONTENT_FILE_NOT_REGULAR"
            else:
                raise AssertionError(
                    "non-regular content_file must fail before reading"
                )

        transaction_module.MAX_TRANSACTION_FILE_BYTES = 80
        transaction_module.MAX_TRANSACTION_TOTAL_BYTES = 100
        transaction_module.MAX_RECOVERY_BACKUP_BYTES = 80
        transaction_module.MAX_RECOVERY_TOTAL_BACKUP_BYTES = 100
        with tempfile.TemporaryDirectory() as td:
            vault = make_vault(Path(td) / "vault")
            aggregate = bundle(
                "oversized-total",
                [
                    {"path": "wiki/A.md", "mode": "create", "content": "a" * 60},
                    {"path": "wiki/B.md", "mode": "create", "content": "b" * 60},
                ],
            )
            try:
                inspect_bundle(vault, aggregate)
            except TransactionValidationError as exc:
                assert exc.code == "TRANSACTION_TOTAL_TOO_LARGE"
            else:
                raise AssertionError("aggregate transaction limit must be enforced")
            assert not (vault / "wiki/A.md").exists()
            assert not (vault / "wiki/B.md").exists()

        transaction_module.MAX_TRANSACTION_FILE_BYTES = 64
        transaction_module.MAX_TRANSACTION_TOTAL_BYTES = 128
        transaction_module.MAX_RECOVERY_BACKUP_BYTES = 64
        transaction_module.MAX_RECOVERY_TOTAL_BACKUP_BYTES = 128
        with tempfile.TemporaryDirectory() as td:
            vault = make_vault(Path(td) / "vault")
            target = vault / "wiki/Recoverable.md"
            target.write_bytes(b"o" * 64)
            operation = bundle(
                "limit-boundary-rollback",
                [
                    {
                        "path": "wiki/Recoverable.md",
                        "mode": "replace",
                        "content": "n" * 64,
                    }
                ],
                {"wiki/Recoverable.md": sha256_file(target)},
            )
            try:
                apply_bundle(vault, operation, fail_after=1)
            except RuntimeError as exc:
                assert "injected failure" in str(exc)
            else:
                raise AssertionError("boundary-sized failure injection must fire")
            assert target.read_bytes() == b"o" * 64
    finally:
        for name, value in original_limits.items():
            setattr(transaction_module, name, value)


def test_parent_swap_cannot_redirect_a_later_write() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        nested = vault / "wiki/nested"
        nested.mkdir()
        outside = base / "outside"
        outside.mkdir()
        operation = bundle(
            "parent-swap",
            [
                {"path": "wiki/A.md", "mode": "create", "content": "# A\n"},
                {"path": "wiki/nested/B.md", "mode": "create", "content": "# B\n"},
            ],
        )

        def swap_parent(_: str, index: int) -> None:
            if index == 1:
                nested.rename(vault / "wiki/nested-original")
                nested.symlink_to(outside, target_is_directory=True)

        try:
            apply_bundle(vault, operation, progress=swap_parent)
        except Exception:
            pass
        else:
            raise AssertionError("a parent swap must abort the operation")
        assert not (outside / "B.md").exists()
        assert not (vault / "wiki/A.md").exists()


def test_rollback_parent_swap_never_unlinks_outside_file() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        nested = vault / "wiki/nested"
        nested.mkdir()
        outside = base / "outside"
        outside.mkdir()
        payload = "# transaction file\n"
        operation = bundle(
            "rollback-parent-swap",
            [
                {
                    "path": "wiki/nested/A.md",
                    "mode": "create",
                    "content": payload,
                }
            ],
        )

        def swap_parent(_: str, __: int) -> None:
            nested.rename(vault / "wiki/nested-original")
            (outside / "A.md").write_text(payload, encoding="utf-8")
            nested.symlink_to(outside, target_is_directory=True)
            raise RuntimeError("injected after parent swap")

        try:
            apply_bundle(vault, operation, progress=swap_parent)
        except TransactionRecoveryError as exc:
            assert exc.code == "ROLLBACK_FAILED"
        else:
            raise AssertionError("unsafe parent swap must fail closed during rollback")
        assert (outside / "A.md").read_text(encoding="utf-8") == payload
        journal = json.loads(
            (
                vault / ".vault-meta/transactions/rollback-parent-swap/journal.json"
            ).read_text(encoding="utf-8")
        )
        assert journal["state"] == "rollback-failed"


def test_raw_payload_replace_rejected() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        source = vault / ".raw/source.md"
        source.write_text("source\n")
        try:
            apply_bundle(
                vault,
                bundle(
                    "raw-replace",
                    [
                        {
                            "path": ".raw/source.md",
                            "mode": "replace",
                            "content": "changed\n",
                        }
                    ],
                    operation_type="ingest",
                ),
            )
        except TransactionValidationError as exc:
            assert exc.code == "RAW_IS_CREATE_ONLY"
        else:
            raise AssertionError("raw replacement must fail")


def test_address_allocation_is_one_transaction() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / ".vault-meta").mkdir()
        (vault / ".vault-meta/address-counter.txt").write_text("1\n")
        (vault / ".raw/.manifest.json").write_text(
            json.dumps({"version": 1, "sources": {}, "address_map": {}})
        )
        result = apply_bundle(
            vault,
            {
                **bundle(
                    "addresses",
                    [
                        {
                            "path": "wiki/A.md",
                            "mode": "create",
                            "content": "---\ntype: concept\n---\n# A\n",
                        },
                        {
                            "path": "wiki/B.md",
                            "mode": "create",
                            "content": "---\ntype: concept\n---\n# B\n",
                        },
                    ],
                    operation_type="ingest",
                ),
                "address_requests": [
                    {"path": "wiki/A.md", "prefix": "c"},
                    {"path": "wiki/B.md", "prefix": "c"},
                ],
                "source_manifest_updates": {
                    ".raw/source.md": {"hash": "a" * 64, "pages_created": ["wiki/A.md"]}
                },
            },
        )
        assert result["changed_paths"] == [
            "wiki/A.md",
            "wiki/B.md",
            ".vault-meta/address-counter.txt",
            ".raw/.manifest.json",
        ]
        assert "address: c-000001" in (vault / "wiki/A.md").read_text()
        assert "address: c-000002" in (vault / "wiki/B.md").read_text()
        assert (vault / ".vault-meta/address-counter.txt").read_text() == "3\n"
        manifest = json.loads((vault / ".raw/.manifest.json").read_text())
        assert manifest["address_map"]["wiki/A.md"] == "c-000001"
        assert manifest["sources"][".raw/source.md"]["hash"] == "a" * 64


def test_address_detection_is_limited_to_frontmatter() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / ".vault-meta").mkdir()
        (vault / ".vault-meta/address-counter.txt").write_text("1\n", encoding="utf-8")
        (vault / ".raw/.manifest.json").write_text(
            json.dumps({"version": 1, "sources": {}, "address_map": {}}),
            encoding="utf-8",
        )
        apply_bundle(
            vault,
            {
                **bundle(
                    "body-address",
                    [
                        {
                            "path": "wiki/Body.md",
                            "mode": "create",
                            "content": (
                                "---\ntype: concept\n---\n\n"
                                "```yaml\naddress: c-999999\n```\n"
                            ),
                        }
                    ],
                    operation_type="ingest",
                ),
                "address_requests": [{"path": "wiki/Body.md", "prefix": "c"}],
            },
        )
        page = (vault / "wiki/Body.md").read_text(encoding="utf-8")
        assert page.startswith("---\naddress: c-000001\ntype: concept\n---\n")
        assert "```yaml\naddress: c-999999\n```" in page
        manifest = json.loads(
            (vault / ".raw/.manifest.json").read_text(encoding="utf-8")
        )
        assert manifest["address_map"]["wiki/Body.md"] == "c-000001"


def test_duplicate_or_unterminated_frontmatter_address_is_rejected() -> None:
    for operation_id, content, expected_code in (
        (
            "duplicate-address",
            "---\naddress: c-000001\naddress: c-000001\n---\n# Page\n",
            "DUPLICATE_ADDRESS",
        ),
        (
            "unterminated-address",
            "---\ntype: concept\n# Page\n",
            "ADDRESS_FRONTMATTER_UNTERMINATED",
        ),
    ):
        with tempfile.TemporaryDirectory() as td:
            vault = make_vault(Path(td) / "vault")
            (vault / ".vault-meta").mkdir()
            (vault / ".vault-meta/address-counter.txt").write_text(
                "1\n", encoding="utf-8"
            )
            (vault / ".raw/.manifest.json").write_text(
                json.dumps({"version": 1, "sources": {}, "address_map": {}}),
                encoding="utf-8",
            )
            operation = {
                **bundle(
                    operation_id,
                    [{"path": "wiki/Page.md", "mode": "create", "content": content}],
                    operation_type="ingest",
                ),
                "address_requests": [{"path": "wiki/Page.md", "prefix": "c"}],
            }
            try:
                apply_bundle(vault, operation)
            except TransactionValidationError as exc:
                assert exc.code == expected_code
            else:
                raise AssertionError(f"{expected_code} input must be rejected")
            assert not (vault / "wiki/Page.md").exists()
            assert (vault / ".vault-meta/address-counter.txt").read_text() == "1\n"


def test_corrupt_address_map_and_exhausted_counter_are_rejected() -> None:
    cases = (
        (
            {"wiki/Page.md": "c-000777\nstatus: compromised"},
            "1\n",
            "c",
            "INVALID_ADDRESS_MAP",
        ),
        ({"wiki/Page.md": "c-777"}, "1\n", "c", "INVALID_ADDRESS_MAP"),
        (
            {"wiki/Page.md": "c-000001", "wiki/Other.md": "c-000001"},
            "1\n",
            "c",
            "INVALID_ADDRESS_MAP",
        ),
        ({"wiki/Page.md": "l-000001"}, "1\n", "c", "ADDRESS_PREFIX_MISMATCH"),
        ({"../Page.md": "c-000001"}, "1\n", "c", "INVALID_ADDRESS_MAP"),
        ({"wiki/Other.md": "c-000001"}, "1\n", "c", "ADDRESS_COUNTER_COLLISION"),
        ({}, "1000000\n", "c", "ADDRESS_SPACE_EXHAUSTED"),
    )
    for index, (address_map, counter, prefix, expected_code) in enumerate(cases):
        with tempfile.TemporaryDirectory() as td:
            vault = make_vault(Path(td) / "vault")
            (vault / ".vault-meta").mkdir()
            (vault / ".vault-meta/address-counter.txt").write_text(
                counter, encoding="utf-8"
            )
            (vault / ".raw/.manifest.json").write_text(
                json.dumps({"version": 1, "sources": {}, "address_map": address_map}),
                encoding="utf-8",
            )
            operation = {
                **bundle(
                    f"corrupt-address-map-{index}",
                    [
                        {
                            "path": "wiki/Page.md",
                            "mode": "create",
                            "content": "---\ntype: concept\n---\n# Page\n",
                        }
                    ],
                    operation_type="ingest",
                ),
                "address_requests": [{"path": "wiki/Page.md", "prefix": prefix}],
            }
            try:
                inspect_bundle(vault, operation)
            except TransactionValidationError as exc:
                assert exc.code == expected_code, (exc.code, expected_code)
            else:
                raise AssertionError(f"{expected_code} input must be rejected")
            assert not (vault / "wiki/Page.md").exists()


def test_approved_expanded_plan_binds_managed_metadata() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / ".vault-meta").mkdir()
        counter = vault / ".vault-meta/address-counter.txt"
        counter.write_text("1\n", encoding="utf-8")
        (vault / ".raw/.manifest.json").write_text(
            json.dumps({"version": 1, "sources": {}, "address_map": {}}),
            encoding="utf-8",
        )
        operation = {
            **bundle(
                "approved-address",
                [
                    {
                        "path": "wiki/Approved.md",
                        "mode": "create",
                        "content": "---\ntitle: Approved\ntype: concept\n---\n# Approved\n",
                    }
                ],
                operation_type="ingest",
            ),
            "address_requests": [{"path": "wiki/Approved.md", "prefix": "c"}],
        }
        plan = inspect_bundle(vault, operation)
        counter.write_text("2\n", encoding="utf-8")
        try:
            apply_bundle(
                vault,
                operation,
                approved_plan_sha256=plan["approval_sha256"],
            )
        except TransactionValidationError as exc:
            assert exc.code == "PLAN_CHANGED"
        else:
            raise AssertionError("managed metadata drift must invalidate approval")
        assert not (vault / "wiki/Approved.md").exists()
        assert counter.read_text(encoding="utf-8") == "2\n"


def test_approval_is_bound_to_one_canonical_vault() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        reviewed_vault = make_vault(base / "reviewed")
        other_vault = make_vault(base / "other")
        operation = bundle(
            "vault-bound-plan",
            [{"path": "wiki/A.md", "mode": "create", "content": "# A\n"}],
        )
        approval = inspect_bundle(reviewed_vault, operation)["approval_sha256"]
        try:
            apply_bundle(
                other_vault,
                operation,
                approved_plan_sha256=approval,
            )
        except TransactionValidationError as exc:
            assert exc.code == "PLAN_CHANGED"
        else:
            raise AssertionError("an approval from another vault must fail")
        assert not (other_vault / "wiki/A.md").exists()
        assert not (other_vault / ".vault-meta").exists()


def test_approval_is_bound_to_the_reviewed_vault_directory_object() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        parked = base / "reviewed-vault"
        operation = bundle(
            "vault-object-bound-plan",
            [{"path": "wiki/A.md", "mode": "create", "content": "# A\n"}],
        )
        approval = inspect_bundle(vault, operation)["approval_sha256"]
        vault.rename(parked)
        replacement = make_vault(vault)
        try:
            apply_bundle(
                replacement,
                operation,
                approved_plan_sha256=approval,
            )
        except TransactionValidationError as exc:
            assert exc.code == "PLAN_CHANGED", (exc.code, str(exc))
        else:
            raise AssertionError(
                "a pathname-replacement vault must invalidate approval"
            )
        assert not (parked / "wiki/A.md").exists()
        assert not (replacement / "wiki/A.md").exists()
        assert not (replacement / ".vault-meta").exists()


def test_existing_vault_identity_cannot_use_the_init_transition_escape_hatch() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        parked = base / "reviewed-vault"
        operation = bundle(
            "vault-transition-bypass",
            [{"path": "wiki/A.md", "mode": "create", "content": "# A\n"}],
        )
        plan = inspect_bundle(vault, operation)
        vault.rename(parked)
        replacement = make_vault(vault)
        try:
            apply_bundle(
                replacement,
                operation,
                approved_plan_sha256=plan["approval_sha256"],
                reviewed_vault_identity=plan["vault_identity"],
            )
        except TransactionValidationError as exc:
            assert exc.code == "INVALID_VAULT_TRANSITION", (exc.code, str(exc))
        else:
            raise AssertionError(
                "existing-vault identities cannot request Init transition"
            )
        assert not (replacement / "wiki/A.md").exists()
        assert not (replacement / ".vault-meta").exists()


def test_absent_init_transition_is_bound_to_the_reviewed_parent_object() -> None:
    with tempfile.TemporaryDirectory() as td:
        outer = Path(td)
        parent = outer / "parent"
        parent.mkdir()
        vault = parent / "vault"
        operation = bundle(
            "absent-parent-transition",
            [
                {
                    "path": "wiki/index.md",
                    "mode": "create",
                    "content": "# Index\n",
                }
            ],
            operation_type="setup",
        )
        reviewed = inspect_bundle(vault, operation)
        parked = outer / "reviewed-parent"
        parent.rename(parked)
        parent.mkdir()
        replacement = make_vault(vault)
        current_identity = inspect_bundle(replacement, operation)["vault_identity"]
        try:
            apply_bundle(
                replacement,
                operation,
                approved_plan_sha256=reviewed["approval_sha256"],
                reviewed_vault_identity=reviewed["vault_identity"],
                expected_current_vault_identity=current_identity,
            )
        except TransactionValidationError as exc:
            assert exc.code == "PLAN_CHANGED", (exc.code, str(exc))
        else:
            raise AssertionError("Init transition escaped the reviewed parent object")
        assert not (replacement / "wiki/index.md").exists()
        assert not (replacement / ".vault-meta").exists()


def test_absent_vault_root_rejects_portable_sibling_aliases() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        for index, (sibling, requested) in enumerate((("Vault", "vault"), ("Ś", "ſ́"))):
            parent = base / f"parent-{index}"
            parent.mkdir()
            (parent / sibling).mkdir()
            operation = bundle(
                f"root-alias-{index}",
                [
                    {
                        "path": "wiki/index.md",
                        "mode": "create",
                        "content": "# Index\n",
                    }
                ],
                operation_type="setup",
            )
            try:
                inspect_bundle(parent / requested, operation)
            except TransactionValidationError as exc:
                assert exc.code == "CASEFOLD_PATH_ALIAS", (exc.code, str(exc))
            else:
                raise AssertionError(
                    "absent vault root accepted a portable sibling alias"
                )

        parent = base / "invalid-leaves"
        parent.mkdir()
        for requested in ("Cafe\u0301", "bad\nname", "bad\udcff"):
            operation = bundle(
                "invalid-root-leaf",
                [
                    {
                        "path": "wiki/index.md",
                        "mode": "create",
                        "content": "# Index\n",
                    }
                ],
                operation_type="setup",
            )
            try:
                inspect_bundle(parent / requested, operation)
            except TransactionValidationError as exc:
                assert exc.code == "INVALID_VAULT_ROOT_NAME", (exc.code, str(exc))
            else:
                raise AssertionError("vault root accepted a nonportable leaf name")


def test_sequential_transactions_reject_existing_unicode_portable_alias() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        first = bundle(
            "portable-alias-first",
            [{"path": "wiki/Ś.md", "mode": "create", "content": "# One\n"}],
        )
        second = bundle(
            "portable-alias-second",
            [{"path": "wiki/ſ́.md", "mode": "create", "content": "# Two\n"}],
        )
        apply_bundle(vault, first)
        try:
            apply_bundle(vault, second)
        except TransactionValidationError as exc:
            assert exc.code == "CASEFOLD_PATH_ALIAS", (exc.code, str(exc))
        else:
            raise AssertionError(
                "an existing NFC(casefold) alias must block publication"
            )
        assert (vault / "wiki/Ś.md").read_text(encoding="utf-8") == "# One\n"
        assert len(list((vault / "wiki").iterdir())) == 1


def test_approval_binds_existing_and_result_file_modes() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        target = vault / "wiki/A.md"
        target.write_text("before\n", encoding="utf-8")
        target.chmod(0o644)
        operation = bundle(
            "mode-bound-plan",
            [{"path": "wiki/A.md", "mode": "replace", "content": "after\n"}],
        )
        operation["expected_hashes"]["wiki/A.md"] = sha256_file(target)
        approval = inspect_bundle(vault, operation)["approval_sha256"]
        target.chmod(0o755)
        try:
            apply_bundle(vault, operation, approved_plan_sha256=approval)
        except TransactionValidationError as exc:
            assert exc.code == "PLAN_CHANGED"
        else:
            raise AssertionError("chmod after inspect must invalidate approval")
        assert target.read_text(encoding="utf-8") == "before\n"
        assert target.stat().st_mode & 0o777 == 0o755
        assert not (vault / ".vault-meta").exists()


def test_idempotent_replay_rejects_byte_and_mode_drift() -> None:
    for drift in ("bytes", "mode"):
        with tempfile.TemporaryDirectory() as td:
            vault = make_vault(Path(td) / "vault")
            operation = bundle(
                f"completed-{drift}",
                [{"path": "wiki/A.md", "mode": "create", "content": "created\n"}],
            )
            approval = inspect_bundle(vault, operation)["approval_sha256"]
            apply_bundle(vault, operation, approved_plan_sha256=approval)
            target = vault / "wiki/A.md"
            if drift == "bytes":
                target.write_text("later user edit\n", encoding="utf-8")
            else:
                target.chmod(0o755)
            try:
                apply_bundle(vault, operation, approved_plan_sha256=approval)
            except TransactionConflict as exc:
                assert exc.code == "OPERATION_RESULT_DRIFT"
            else:
                raise AssertionError(
                    f"completed-operation {drift} drift must not report success"
                )
            if drift == "bytes":
                assert target.read_text(encoding="utf-8") == "later user edit\n"
            else:
                assert target.stat().st_mode & 0o777 == 0o755


def test_completed_history_drift_does_not_block_unrelated_new_operation() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        first = bundle(
            "history-one",
            [{"path": "wiki/A.md", "mode": "create", "content": "first\n"}],
        )
        apply_bundle(vault, first)
        (vault / "wiki/A.md").write_text("manual Obsidian edit\n", encoding="utf-8")
        second = bundle(
            "history-two",
            [{"path": "wiki/B.md", "mode": "create", "content": "second\n"}],
        )
        apply_bundle(vault, second)
        assert (vault / "wiki/A.md").read_text() == "manual Obsidian edit\n"
        assert (vault / "wiki/B.md").read_text() == "second\n"


def test_operation_id_cannot_hide_different_bundle() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        first = bundle(
            "same-id", [{"path": "wiki/A.md", "mode": "create", "content": "# A\n"}]
        )
        apply_bundle(vault, first)
        second = bundle(
            "same-id", [{"path": "wiki/B.md", "mode": "create", "content": "# B\n"}]
        )
        try:
            apply_bundle(vault, second)
        except TransactionConflict as exc:
            assert exc.code == "OPERATION_ID_REUSED"
        else:
            raise AssertionError("operation ID reuse must fail")


def test_inspect_is_read_only() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        operation = bundle(
            "inspect", [{"path": "wiki/A.md", "mode": "create", "content": "# A\n"}]
        )
        before = sorted(path.relative_to(vault).as_posix() for path in vault.rglob("*"))
        plan = inspect_bundle(vault, operation)
        after = sorted(path.relative_to(vault).as_posix() for path in vault.rglob("*"))
        assert plan["changed_paths"] == ["wiki/A.md"]
        assert before == after


def test_binary_content_file_is_hash_checked_and_create_only() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        source = base / "source.bin"
        payload = b"\x00\xffbinary\n"
        source.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        operation = bundle(
            "binary-source",
            [
                {
                    "path": ".raw/captured/example.bin",
                    "mode": "create",
                    "content_file": str(source),
                    "sha256": digest,
                }
            ],
            operation_type="capture",
        )
        assert (
            inspect_bundle(vault, operation)["hashes"][".raw/captured/example.bin"]
            == digest
        )
        apply_bundle(vault, operation)
        assert (vault / ".raw/captured/example.bin").read_bytes() == payload

        unbound = bundle(
            "binary-unbound",
            [
                {
                    "path": ".raw/captured/unbound.bin",
                    "mode": "create",
                    "content_file": str(source),
                }
            ],
            operation_type="capture",
        )
        try:
            inspect_bundle(vault, unbound)
        except TransactionValidationError as exc:
            assert exc.code == "CONTENT_HASH_REQUIRED"
        else:
            raise AssertionError(
                "content_file bytes must be bound to the reviewed bundle"
            )

        changed = bundle(
            "binary-mismatch",
            [
                {
                    "path": ".raw/captured/changed.bin",
                    "mode": "create",
                    "content_file": str(source),
                    "sha256": digest,
                }
            ],
            operation_type="capture",
        )
        source.write_bytes(b"changed")
        try:
            apply_bundle(vault, changed)
        except TransactionValidationError as exc:
            assert exc.code == "CONTENT_HASH_MISMATCH"
        else:
            raise AssertionError("changed binary content must fail its declared hash")
        assert not (vault / ".raw/captured/changed.bin").exists()


def _hold_lock(
    vault: str, ready: multiprocessing.Event, release: multiprocessing.Event
) -> None:
    with MutationLock(Path(vault), timeout=1):
        ready.set()
        release.wait(5)


def _address_worker(vault: str, number: int, queue: multiprocessing.Queue) -> None:
    path = f"wiki/Page-{number}.md"
    operation = {
        **bundle(
            f"address-{number}",
            [
                {
                    "path": path,
                    "mode": "create",
                    "content": (
                        "---\ntype: concept\nstatus: developing\ncreated: 2026-01-01\n"
                        "updated: 2026-01-01\ntags: [test]\n---\n"
                        f"# Page {number}\n"
                    ),
                }
            ],
            operation_type="ingest",
        ),
        "address_requests": [{"path": path, "prefix": "c"}],
    }
    try:
        apply_bundle(Path(vault), operation, timeout=10)
    except Exception as exc:
        queue.put((number, False, repr(exc)))
    else:
        queue.put((number, True, ""))


def test_fresh_lock_survives_and_times_out() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        ready = multiprocessing.Event()
        release = multiprocessing.Event()
        process = multiprocessing.Process(
            target=_hold_lock, args=(str(vault), ready, release)
        )
        process.start()
        assert ready.wait(3)
        try:
            MutationLock(vault, timeout=0.1, stale_after=0).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError("live lock must survive cleanup")
        release.set()
        process.join(3)
        assert process.exitcode == 0


def test_explicit_recovery_can_reap_stale_pid_reuse_lock() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        lock = vault / ".vault-meta/mutation.lock"
        lock.mkdir(parents=True)
        (lock / "owner.json").write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.mutation-lock.v1",
                    "pid": os.getpid(),
                    "token": "stale-owner",
                    "host": socket.gethostname(),
                    "started_epoch": 0,
                }
            ),
            encoding="utf-8",
        )
        try:
            MutationLock(vault, timeout=0, stale_after=0).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError(
                "automatic recovery must not steal a possibly live lock"
            )
        assert lock.is_dir()

        with MutationLock(
            vault,
            timeout=0,
            stale_after=0,
            force_stale_lock=True,
        ):
            assert lock.is_dir()
        assert not lock.exists()


def test_force_stale_lock_reaps_dead_same_host_owner_before_stale_after() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        lock = vault / ".vault-meta/mutation.lock"
        lock.mkdir(parents=True)
        (lock / "owner.json").write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.mutation-lock.v1",
                    "pid": 999999,
                    "token": "dead-owner",
                    "host": socket.gethostname(),
                    "started_epoch": time.time() - 780,
                }
            ),
            encoding="utf-8",
        )
        original_alive = transaction_module._process_alive
        transaction_module._process_alive = lambda pid: False
        try:
            try:
                MutationLock(vault, timeout=0, stale_after=3600.0).acquire()
            except TransactionConflict as exc:
                assert exc.code == "LOCK_TIMEOUT"
            else:
                raise AssertionError("automatic recovery must not steal a young lock")
            assert lock.is_dir()

            with MutationLock(
                vault,
                timeout=0,
                stale_after=3600.0,
                force_stale_lock=True,
            ):
                assert lock.is_dir()
            assert not lock.exists()
        finally:
            transaction_module._process_alive = original_alive


def test_force_stale_lock_does_not_reap_a_live_same_host_owner() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        lock = vault / ".vault-meta/mutation.lock"
        lock.mkdir(parents=True)
        (lock / "owner.json").write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.mutation-lock.v1",
                    "pid": os.getpid(),
                    "token": "live-owner",
                    "host": socket.gethostname(),
                    "started_epoch": time.time() - 780,
                }
            ),
            encoding="utf-8",
        )
        try:
            MutationLock(
                vault,
                timeout=0,
                stale_after=3600.0,
                force_stale_lock=True,
            ).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError("force must never reap a live same-host owner")
        assert lock.is_dir()
        assert (lock / "owner.json").is_file()


def test_force_stale_lock_keeps_the_age_gate_for_a_foreign_host_owner() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        lock = vault / ".vault-meta/mutation.lock"
        lock.mkdir(parents=True)
        (lock / "owner.json").write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.mutation-lock.v1",
                    "pid": 999999,
                    "token": "foreign-owner",
                    "host": f"not-{socket.gethostname()}",
                    "started_epoch": time.time() - 780,
                }
            ),
            encoding="utf-8",
        )
        try:
            MutationLock(
                vault,
                timeout=0,
                stale_after=3600.0,
                force_stale_lock=True,
            ).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError("force must keep the age gate off this host")
        assert lock.is_dir()
        assert (lock / "owner.json").is_file()


def test_ownerless_mutation_lock_requires_explicit_force() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        lock_path = vault / ".vault-meta/mutation.lock"
        lock_path.mkdir(parents=True)
        os.utime(lock_path, (0, 0))
        try:
            MutationLock(vault, timeout=0, stale_after=0).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError("ownerless lock must not be stolen without force")
        assert lock_path.is_dir()

        with MutationLock(
            vault,
            timeout=0,
            stale_after=0,
            force_stale_lock=True,
        ):
            assert (lock_path / "owner.json").is_file()
        assert not lock_path.exists()


def test_mutation_lock_release_and_reaping_ignore_replaced_external_alias() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        lock = MutationLock(vault, timeout=0)
        lock.acquire()

        displaced = lock.path.with_name("mutation.lock.displaced")
        os.rename(lock.path, displaced)
        outside = base / "outside-mutation-lock"
        outside.mkdir()
        outside_owner = outside / "owner.json"
        outside_owner.write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.mutation-lock.v1",
                    "pid": os.getpid(),
                    "token": lock.token,
                    "host": socket.gethostname(),
                    "started_epoch": 0,
                    "external_marker": "must-survive",
                }
            ),
            encoding="utf-8",
        )
        before = outside_owner.read_bytes()
        lock.path.symlink_to(outside, target_is_directory=True)

        try:
            lock.release()
        except TransactionError as exc:
            assert exc.code == "LOCK_OWNERSHIP_LOST"
        else:
            raise AssertionError("a replaced mutation lock path must fail closed")
        assert lock.path.is_symlink()
        assert outside_owner.read_bytes() == before
        assert (displaced / "owner.json").is_file()

        try:
            MutationLock(
                vault,
                timeout=0,
                stale_after=0,
                force_stale_lock=True,
            ).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError(
                "forced reaping must not follow an external lock alias"
            )
        assert lock.path.is_symlink()
        assert outside_owner.read_bytes() == before


def test_mutation_lock_serializes_across_meta_directory_replacement() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        first = MutationLock(vault, timeout=0)
        first.acquire()

        held_meta = vault / ".vault-meta-held"
        os.rename(vault / ".vault-meta", held_meta)
        replacement_meta = vault / ".vault-meta"
        replacement_lock = replacement_meta / "mutation.lock"
        replacement_lock.mkdir(parents=True)
        replacement_owner = replacement_lock / "owner.json"
        replacement_owner.write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.mutation-lock.v1",
                    "pid": 999999,
                    "token": first.token,
                    "host": socket.gethostname(),
                    "started_epoch": 0,
                    "replacement_marker": "must-survive",
                }
            ),
            encoding="utf-8",
        )
        before = replacement_owner.read_bytes()

        try:
            MutationLock(
                vault,
                timeout=0,
                stale_after=0,
                force_stale_lock=True,
            ).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError("vault advisory lock must span metadata replacement")
        assert replacement_owner.read_bytes() == before
        assert (held_meta / "mutation.lock/owner.json").is_file()

        first.release()
        assert not (held_meta / "mutation.lock").exists()
        assert replacement_owner.read_bytes() == before


def test_apply_runtime_namespaces_are_descriptor_anchored() -> None:
    for variant in ("root", "meta", "transactions", "operation", "backups"):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            vault = make_vault(base / "vault")
            victim = vault / "wiki/A.md"
            victim.write_text("old\n", encoding="utf-8")
            operation_id = f"namespace-{variant}"
            operation = bundle(
                operation_id,
                [{"path": "wiki/A.md", "mode": "replace", "content": "new\n"}],
                {"wiki/A.md": sha256_file(victim)},
            )
            external = base / f"external-{variant}"
            external.mkdir()
            sentinel = external / "sentinel.bin"
            sentinel.write_bytes(b"external-must-not-change\x00")
            parked: Path | None = None

            def swap_namespace(_relative: str, _index: int) -> None:
                nonlocal parked
                if variant == "root":
                    selected = vault
                    parked = base / "vault-held"
                elif variant == "meta":
                    selected = vault / ".vault-meta"
                    parked = vault / ".vault-meta-held"
                elif variant == "transactions":
                    selected = vault / ".vault-meta/transactions"
                    parked = selected.with_name("transactions-held")
                elif variant == "operation":
                    selected = vault / f".vault-meta/transactions/{operation_id}"
                    parked = selected.with_name(f"{operation_id}-held")
                else:
                    selected = (
                        vault / f".vault-meta/transactions/{operation_id}/backups"
                    )
                    parked = selected.with_name("backups-held")
                selected.rename(parked)
                selected.symlink_to(external, target_is_directory=True)

            try:
                apply_bundle(vault, operation, progress=swap_namespace)
            except TransactionError as exc:
                assert exc.code in {
                    "VAULT_NAMESPACE_CHANGED",
                    "RUNTIME_NAMESPACE_CHANGED",
                }, (variant, exc.code, str(exc))
            else:
                raise AssertionError(f"{variant} runtime replacement must fail closed")

            assert sentinel.read_bytes() == b"external-must-not-change\x00"
            assert sorted(path.name for path in external.iterdir()) == ["sentinel.bin"]
            assert parked is not None
            restored = parked / "wiki/A.md" if variant == "root" else victim
            assert restored.read_text(encoding="utf-8") == "old\n"


def test_meta_managed_targets_rollback_inside_pinned_namespace() -> None:
    cases = (
        (
            "configuration",
            ".vault-meta/mode.json",
            '{"schema":"claude-obsidian.vault-mode.v1","mode":"generic"}\n',
            '{"schema":"claude-obsidian.vault-mode.v1","mode":"para"}\n',
        ),
        ("setup", ".vault-meta/address-counter.txt", "1\n", "2\n"),
    )
    for operation_type, relative, old_content, new_content in cases:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            vault = make_vault(base / "vault")
            target = vault / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(old_content, encoding="utf-8")
            operation = bundle(
                f"meta-target-{operation_type}",
                [{"path": relative, "mode": "replace", "content": new_content}],
                {relative: sha256_file(target)},
                operation_type=operation_type,
            )
            external_meta = base / f"external-meta-{operation_type}"
            external_meta.mkdir()
            external_target = external_meta / Path(relative).name
            external_target.write_bytes(b"external-meta-sentinel\n")
            external_before = external_target.read_bytes()
            held_meta = vault / f".vault-meta-held-{operation_type}"

            def swap_meta(_relative: str, _index: int) -> None:
                (vault / ".vault-meta").rename(held_meta)
                (vault / ".vault-meta").symlink_to(
                    external_meta, target_is_directory=True
                )

            try:
                apply_bundle(vault, operation, progress=swap_meta)
            except TransactionError as exc:
                assert exc.code == "RUNTIME_NAMESPACE_CHANGED"
            else:
                raise AssertionError(
                    "metadata replacement must roll back the pinned target"
                )
            assert (held_meta / Path(relative).name).read_text(
                encoding="utf-8"
            ) == old_content
            assert external_target.read_bytes() == external_before
            assert sorted(path.name for path in external_meta.iterdir()) == [
                Path(relative).name
            ]


def test_recovery_never_reads_a_replaced_external_operation() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        victim = vault / "wiki/victim.md"
        victim.write_text("victim-safe\n", encoding="utf-8")
        operation_id = "recovery-operation-swap"
        transaction = vault / f".vault-meta/transactions/{operation_id}"
        (transaction / "backups").mkdir(parents=True)
        benign = {
            "schema": "claude-obsidian.transaction-journal.v1",
            "operation_id": operation_id,
            "operation_type": "generic",
            "state": "applying",
            "writes": [
                {
                    "path": "wiki/victim.md",
                    "mode": "create",
                    "new_sha256": sha256_file(victim),
                    "original_sha256": None,
                    "original_mode": None,
                    "new_mode": 0o644,
                    "backup": "0000.original",
                }
            ],
            "applied": [],
        }
        (transaction / "journal.json").write_text(json.dumps(benign), encoding="utf-8")
        external = base / "external-recovery-operation"
        external.mkdir()
        external_journal = external / "journal.json"
        external_journal.write_bytes(b"external-journal-must-survive\n")
        external_before = external_journal.read_bytes()
        parked = transaction.with_name(f"{operation_id}-held")
        original_read = transaction_module._read_runtime_json_at
        swapped = False

        def swapping_read(
            directory_fd,
            name,
            *,
            label,
            limit=transaction_module.MAX_TRANSACTION_RUNTIME_JSON_BYTES,
        ):
            nonlocal swapped
            if name == "journal.json" and not swapped:
                swapped = True
                transaction.rename(parked)
                transaction.symlink_to(external, target_is_directory=True)
            return original_read(directory_fd, name, label=label, limit=limit)

        transaction_module._read_runtime_json_at = swapping_read
        try:
            with MutationLock(vault) as mutation_lock:
                try:
                    recover_incomplete(vault, mutation_lock=mutation_lock)
                except TransactionError as exc:
                    assert exc.code == "RUNTIME_NAMESPACE_CHANGED"
                else:
                    raise AssertionError(
                        "recovery operation replacement must fail closed"
                    )
        finally:
            transaction_module._read_runtime_json_at = original_read
        assert victim.read_text(encoding="utf-8") == "victim-safe\n"
        assert external_journal.read_bytes() == external_before
        assert sorted(path.name for path in external.iterdir()) == ["journal.json"]


def _seed_runtime_read_probe(base: Path) -> tuple[Path, bytes]:
    """Write one bounded runtime file used by the stability read probes."""

    target = base / "runtime-file.json"
    payload = b'{"schema": "claude-obsidian.runtime-read-probe.v1"}\n'
    target.write_bytes(payload)
    return target, payload


def test_read_runtime_bytes_tolerates_a_single_external_mtime_touch() -> None:
    if not transaction_module._supports_confined_dirfd():
        return
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        target, payload = _seed_runtime_read_probe(base)
        directory_fd = os.open(base, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        original_fstat = os.fstat
        calls = 0

        def counting_fstat(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                stamp = original_fstat(descriptor).st_mtime_ns + 5_000_000_000
                os.utime(target, ns=(stamp, stamp))
            return original_fstat(descriptor)

        os.fstat = counting_fstat
        try:
            read = transaction_module._read_runtime_bytes_at(
                directory_fd,
                "runtime-file.json",
                label="runtime read probe",
                limit=1024,
            )
        finally:
            os.fstat = original_fstat
            os.close(directory_fd)
        assert read == payload
        assert calls >= 3


def test_read_runtime_bytes_fails_closed_on_a_genuine_size_change() -> None:
    if not transaction_module._supports_confined_dirfd():
        return
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        target, payload = _seed_runtime_read_probe(base)
        directory_fd = os.open(base, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        original_fstat = os.fstat
        calls = 0

        def counting_fstat(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                target.write_bytes(payload + b"external-append-must-fail-closed\n")
            return original_fstat(descriptor)

        os.fstat = counting_fstat
        try:
            transaction_module._read_runtime_bytes_at(
                directory_fd,
                "runtime-file.json",
                label="runtime read probe",
                limit=1024,
            )
        except TransactionRecoveryError as exc:
            assert exc.code == "CORRUPT_RUNTIME_STATE"
        else:
            raise AssertionError("a genuine runtime size change must fail closed")
        finally:
            os.fstat = original_fstat
            os.close(directory_fd)


def test_runtime_directory_cardinality_and_removal_are_bounded() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        transactions = vault / ".vault-meta/transactions"
        for name in ("one", "two", "three"):
            (transactions / name).mkdir(parents=True)
        original_entries = transaction_module.MAX_TRANSACTION_RUNTIME_ENTRIES
        try:
            transaction_module.MAX_TRANSACTION_RUNTIME_ENTRIES = 2
            try:
                recover_incomplete(vault)
            except TransactionRecoveryError as exc:
                assert exc.code == "CORRUPT_RUNTIME_STATE"
                assert "entry safety limit" in str(exc)
            else:
                raise AssertionError("transactions enumeration must be bounded")
            assert sorted(path.name for path in transactions.iterdir()) == [
                "one",
                "three",
                "two",
            ]
        finally:
            transaction_module.MAX_TRANSACTION_RUNTIME_ENTRIES = original_entries

    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        orphan = vault / ".vault-meta/transactions/orphan-budget"
        orphan.mkdir(parents=True)
        (orphan / "one.tmp").write_text("one", encoding="utf-8")
        (orphan / "two.tmp").write_text("two", encoding="utf-8")
        original_tree = transaction_module.MAX_TRANSACTION_RUNTIME_TREE_ENTRIES
        try:
            transaction_module.MAX_TRANSACTION_RUNTIME_TREE_ENTRIES = 1
            try:
                recover_incomplete(vault)
            except TransactionRecoveryError as exc:
                assert exc.code == "CORRUPT_RUNTIME_STATE"
                assert "entry safety limit" in str(exc)
            else:
                raise AssertionError("runtime removal traversal must be bounded")
            assert sorted(path.name for path in orphan.iterdir()) == [
                "one.tmp",
                "two.tmp",
            ]
        finally:
            transaction_module.MAX_TRANSACTION_RUNTIME_TREE_ENTRIES = original_tree


def test_runtime_removal_enumerates_through_a_fresh_descriptor() -> None:
    if not transaction_module._supports_confined_dirfd():
        return
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        transactions = vault / ".vault-meta/transactions"
        operation = transactions / "cursor-at-end"
        backups = operation / "backups"
        backups.mkdir(parents=True)
        (operation / "bundle.json").write_text("{}\n", encoding="utf-8")
        (backups / "original.bin").write_bytes(b"original\n")

        parent_fd = os.open(
            transactions,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0),
        )
        operation_fd = transaction_module._open_runtime_directory_at(
            parent_fd, "cursor-at-end", create=False
        )
        try:
            try:
                os.lseek(operation_fd, 0, os.SEEK_END)
            except OSError:
                return
            transaction_module._remove_pinned_runtime_tree_at(
                parent_fd, "cursor-at-end", operation_fd
            )
        finally:
            os.close(operation_fd)
            os.close(parent_fd)
        assert not operation.exists()


def test_mutation_and_runtime_descriptors_do_not_leak() -> None:
    descriptor_directory = next(
        (path for path in (Path("/proc/self/fd"), Path("/dev/fd")) if path.is_dir()),
        None,
    )
    if descriptor_directory is None:
        return
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        baseline = len(os.listdir(descriptor_directory))
        for _ in range(100):
            with MutationLock(vault) as mutation_lock:
                root_fd = mutation_lock.duplicate_root_fd()
                parent_fd = mutation_lock.duplicate_parent_fd()
                transactions_fd = mutation_lock.open_metadata_dir_fd(
                    "transactions", create=True
                )
                os.close(transactions_fd)
                os.close(parent_fd)
                os.close(root_fd)
        for index in range(20):
            assert (
                apply_bundle(
                    vault,
                    bundle(
                        f"fd-stress-{index}",
                        [
                            {
                                "path": f"wiki/FD-{index}.md",
                                "mode": "create",
                                "content": f"# FD {index}\n",
                            }
                        ],
                    ),
                )["status"]
                == "complete"
            )
        assert len(os.listdir(descriptor_directory)) == baseline


def test_recover_interrupted_journal() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        original = vault / "wiki/A.md"
        original.write_text("old\n")
        tx = vault / ".vault-meta/transactions/crashed"
        backups = tx / "backups"
        backups.mkdir(parents=True)
        (backups / "0000.original").write_text("old\n")
        original.write_text("new\n")
        journal = {
            "schema": "claude-obsidian.transaction-journal.v1",
            "operation_id": "crashed",
            "operation_type": "generic",
            "state": "applying",
            "writes": [
                {
                    "path": "wiki/A.md",
                    "mode": "replace",
                    "new_sha256": sha256_file(original),
                    "original_sha256": sha256_file(backups / "0000.original"),
                    "original_mode": 0o644,
                    "new_mode": 0o644,
                    "backup": "0000.original",
                }
            ],
            "applied": [],
        }
        (tx / "journal.json").write_text(json.dumps(journal))
        with MutationLock(vault) as mutation_lock:
            assert recover_incomplete(vault, mutation_lock=mutation_lock) == ["crashed"]
        assert original.read_text() == "old\n"


def test_recovery_rejects_unbound_or_indirect_backups_before_any_write() -> None:
    attacks = ("absolute", "traversal", "symlink", "wrong-index")
    for attack in attacks:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            vault = make_vault(base / "vault")
            first = vault / "wiki/A.md"
            second = vault / "wiki/B.md"
            first.write_text("new A\n", encoding="utf-8")
            second.write_text("new B\n", encoding="utf-8")
            tx = vault / f".vault-meta/transactions/recovery-{attack}"
            backups = tx / "backups"
            backups.mkdir(parents=True)
            old_a = b"old A\n"
            old_b = b"old B\n"
            outside = base / "outside-secret"
            outside.write_bytes(old_a)
            (backups / "0001.original").write_bytes(old_b)

            backup_value = "0000.original"
            if attack == "absolute":
                backup_value = str(outside)
            elif attack == "traversal":
                backup_value = "../outside-secret"
            elif attack == "symlink":
                (backups / "0000.original").symlink_to(outside)
            elif attack == "wrong-index":
                (backups / "0000.original").write_bytes(old_a)
                backup_value = "0001.original"

            journal = {
                "schema": "claude-obsidian.transaction-journal.v1",
                "operation_id": f"recovery-{attack}",
                "operation_type": "generic",
                "state": "applying",
                "writes": [
                    {
                        "path": "wiki/A.md",
                        "mode": "replace",
                        "new_sha256": sha256_file(first),
                        "original_sha256": hashlib.sha256(old_a).hexdigest(),
                        "original_mode": 0o644,
                        "new_mode": 0o644,
                        "backup": backup_value,
                    },
                    {
                        "path": "wiki/B.md",
                        "mode": "replace",
                        "new_sha256": sha256_file(second),
                        "original_sha256": hashlib.sha256(old_b).hexdigest(),
                        "original_mode": 0o644,
                        "new_mode": 0o644,
                        "backup": "0001.original",
                    },
                ],
                "applied": ["wiki/A.md", "wiki/B.md"],
            }
            (tx / "journal.json").write_text(json.dumps(journal), encoding="utf-8")
            try:
                with MutationLock(vault) as mutation_lock:
                    recover_incomplete(vault, mutation_lock=mutation_lock)
            except TransactionRecoveryError as exc:
                assert exc.code == "CORRUPT_JOURNAL", (attack, exc.code, str(exc))
            else:
                raise AssertionError(f"unsafe recovery backup must fail: {attack}")
            assert first.read_text(encoding="utf-8") == "new A\n"
            assert second.read_text(encoding="utf-8") == "new B\n"
            assert outside.read_bytes() == old_a


def test_recovery_covers_orphan_and_finalization_windows() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        transactions = vault / ".vault-meta/transactions"
        orphan = transactions / "orphan-window"
        orphan.mkdir(parents=True)
        operation = bundle(
            "orphan-window",
            [{"path": "wiki/orphan.md", "mode": "create", "content": "recovered\n"}],
        )
        result = apply_bundle(vault, operation)
        assert result["status"] == "complete"
        assert (vault / "wiki/orphan.md").read_text(encoding="utf-8") == "recovered\n"

        transaction = transactions / "orphan-window"
        journal_path = transaction / "journal.json"
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
        journal["state"] = "applying"
        journal_path.write_text(json.dumps(journal), encoding="utf-8")
        with MutationLock(vault) as mutation_lock:
            assert recover_incomplete(vault, mutation_lock=mutation_lock) == [
                "orphan-window"
            ]
        finalized = json.loads(journal_path.read_text(encoding="utf-8"))
        assert finalized["state"] == "complete"

        result_path = transaction / "changed-paths.json"
        result_path.unlink()
        with MutationLock(vault) as mutation_lock:
            assert recover_incomplete(vault, mutation_lock=mutation_lock) == [
                "orphan-window"
            ]
        reconstructed = json.loads(result_path.read_text(encoding="utf-8"))
        assert reconstructed["status"] == "complete"
        assert reconstructed["hashes"]["wiki/orphan.md"] == sha256_file(
            vault / "wiki/orphan.md"
        )


def test_complete_result_reconstruction_uses_bounded_journal_validation() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        operation_id = "complete-over-limit"
        result = apply_bundle(
            vault,
            bundle(
                operation_id,
                [
                    {
                        "path": "wiki/one.md",
                        "mode": "create",
                        "content": "one\n",
                    },
                    {
                        "path": "wiki/two.md",
                        "mode": "create",
                        "content": "two\n",
                    },
                ],
            ),
        )
        transaction = vault / ".vault-meta/transactions" / operation_id
        (transaction / "changed-paths.json").unlink()
        original_limit = transaction_module.MAX_TRANSACTION_WRITES
        try:
            transaction_module.MAX_TRANSACTION_WRITES = 1
            try:
                recover_incomplete(vault)
            except TransactionRecoveryError as exc:
                assert exc.code == "CORRUPT_JOURNAL", (exc.code, str(exc))
                assert "write-count limit" in str(exc)
            else:
                raise AssertionError(
                    "complete-result reconstruction must enforce the journal write cap"
                )
        finally:
            transaction_module.MAX_TRANSACTION_WRITES = original_limit
        assert not (transaction / "changed-paths.json").exists()
        assert (vault / "wiki/one.md").read_text(encoding="utf-8") == "one\n"
        assert (vault / "wiki/two.md").read_text(encoding="utf-8") == "two\n"
        assert result["changed_paths"] == ["wiki/one.md", "wiki/two.md"]


def test_complete_result_reconstruction_rejects_existing_portable_alias() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        operation_id = "complete-portable-alias"
        apply_bundle(
            vault,
            bundle(
                operation_id,
                [{"path": "wiki/Ś.md", "mode": "create", "content": "one\n"}],
            ),
        )
        transaction = vault / ".vault-meta/transactions" / operation_id
        result_path = transaction / "changed-paths.json"
        result_path.unlink()
        canonical_path = vault / "wiki/Ś.md"
        alias_path = vault / "wiki/ſ́.md"
        alias_path.write_text("outside alias\n", encoding="utf-8")
        if canonical_path.samefile(alias_path):
            assert len(list((vault / "wiki").iterdir())) == 1
            return
        try:
            recover_incomplete(vault)
        except TransactionRecoveryError as exc:
            assert exc.code == "CORRUPT_JOURNAL", (exc.code, str(exc))
        else:
            raise AssertionError("recovery must not certify a portable path alias")
        assert not result_path.exists()


def test_recovery_always_correlates_and_validates_existing_results() -> None:
    for drift in ("complete-hash", "incomplete-correlation"):
        with tempfile.TemporaryDirectory() as td:
            vault = make_vault(Path(td) / "vault")
            operation_id = f"result-{drift}"
            apply_bundle(
                vault,
                bundle(
                    operation_id,
                    [
                        {
                            "path": "wiki/result.md",
                            "mode": "create",
                            "content": "ok\n",
                        }
                    ],
                ),
            )
            transaction = vault / ".vault-meta/transactions" / operation_id
            result_path = transaction / "changed-paths.json"
            journal_path = transaction / "journal.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if drift == "complete-hash":
                result["hashes"]["wiki/result.md"] = "0" * 64
            else:
                journal = json.loads(journal_path.read_text(encoding="utf-8"))
                journal["state"] = "applying"
                journal_path.write_text(json.dumps(journal), encoding="utf-8")
                result["approval_sha256"] = "0" * 64
            result_path.write_text(json.dumps(result), encoding="utf-8")
            try:
                recover_incomplete(vault)
            except TransactionRecoveryError as exc:
                assert exc.code == "CORRUPT_RESULT", (exc.code, str(exc))
            else:
                raise AssertionError(f"recovery accepted result drift: {drift}")


def test_ten_concurrent_address_transactions_remain_consistent() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / ".vault-meta").mkdir()
        (vault / ".vault-meta/address-counter.txt").write_text("1\n")
        (vault / ".raw/.manifest.json").write_text(
            json.dumps({"version": 1, "sources": {}, "address_map": {}})
        )
        queue: multiprocessing.Queue = multiprocessing.Queue()
        workers = [
            multiprocessing.Process(
                target=_address_worker, args=(str(vault), number, queue)
            )
            for number in range(10)
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(15)
            assert worker.exitcode == 0
        outcomes = [queue.get(timeout=2) for _ in workers]
        assert all(ok for _, ok, _ in outcomes), outcomes
        manifest = json.loads((vault / ".raw/.manifest.json").read_text())
        addresses = list(manifest["address_map"].values())
        assert len(addresses) == 10
        assert len(set(addresses)) == 10
        assert (vault / ".vault-meta/address-counter.txt").read_text() == "11\n"
        for number in range(10):
            page = (vault / f"wiki/Page-{number}.md").read_text()
            address = manifest["address_map"][f"wiki/Page-{number}.md"]
            assert f"address: {address}" in page


def main() -> None:
    multiprocessing.set_start_method("fork" if os.name != "nt" else "spawn", force=True)
    test_apply_and_idempotent_result()
    test_failure_rolls_back_every_write()
    test_rolled_back_operation_can_be_retried()
    test_expected_hash_conflict_changes_nothing()
    test_read_preconditions_are_bound_into_plan_approval()
    test_every_write_requires_a_canonical_precondition()
    test_paths_require_nfc_and_file_bundles_reject_duplicate_json_keys()
    test_mapping_bundle_is_a_deep_snapshot_before_hash_and_apply()
    test_bundle_files_are_bounded_regular_and_no_follow()
    test_write_cardinality_and_runtime_json_share_one_recovery_envelope()
    test_runtime_symlinks_and_reserved_lock_descendants_fail_closed()
    test_all_runtime_lock_cache_and_temp_paths_are_reserved()
    test_product_runtime_and_declared_operation_scopes_are_enforced()
    test_operation_types_enforce_least_privilege_path_contracts()
    test_casefold_aliases_and_bundle_collisions_fail_portably()
    test_transaction_size_limits_match_recovery_and_reject_nonregular_content()
    test_parent_swap_cannot_redirect_a_later_write()
    test_rollback_parent_swap_never_unlinks_outside_file()
    test_raw_payload_replace_rejected()
    test_address_allocation_is_one_transaction()
    test_address_detection_is_limited_to_frontmatter()
    test_duplicate_or_unterminated_frontmatter_address_is_rejected()
    test_corrupt_address_map_and_exhausted_counter_are_rejected()
    test_approved_expanded_plan_binds_managed_metadata()
    test_approval_is_bound_to_one_canonical_vault()
    test_approval_is_bound_to_the_reviewed_vault_directory_object()
    test_existing_vault_identity_cannot_use_the_init_transition_escape_hatch()
    test_absent_init_transition_is_bound_to_the_reviewed_parent_object()
    test_absent_vault_root_rejects_portable_sibling_aliases()
    test_sequential_transactions_reject_existing_unicode_portable_alias()
    test_approval_binds_existing_and_result_file_modes()
    test_idempotent_replay_rejects_byte_and_mode_drift()
    test_completed_history_drift_does_not_block_unrelated_new_operation()
    test_operation_id_cannot_hide_different_bundle()
    test_inspect_is_read_only()
    test_binary_content_file_is_hash_checked_and_create_only()
    test_fresh_lock_survives_and_times_out()
    test_explicit_recovery_can_reap_stale_pid_reuse_lock()
    test_force_stale_lock_reaps_dead_same_host_owner_before_stale_after()
    test_force_stale_lock_does_not_reap_a_live_same_host_owner()
    test_force_stale_lock_keeps_the_age_gate_for_a_foreign_host_owner()
    test_ownerless_mutation_lock_requires_explicit_force()
    test_mutation_lock_release_and_reaping_ignore_replaced_external_alias()
    test_mutation_lock_serializes_across_meta_directory_replacement()
    test_apply_runtime_namespaces_are_descriptor_anchored()
    test_meta_managed_targets_rollback_inside_pinned_namespace()
    test_recovery_never_reads_a_replaced_external_operation()
    test_read_runtime_bytes_tolerates_a_single_external_mtime_touch()
    test_read_runtime_bytes_fails_closed_on_a_genuine_size_change()
    test_runtime_directory_cardinality_and_removal_are_bounded()
    test_runtime_removal_enumerates_through_a_fresh_descriptor()
    test_mutation_and_runtime_descriptors_do_not_leak()
    test_recover_interrupted_journal()
    test_recovery_rejects_unbound_or_indirect_backups_before_any_write()
    test_recovery_covers_orphan_and_finalization_windows()
    test_complete_result_reconstruction_uses_bounded_journal_validation()
    test_complete_result_reconstruction_rejects_existing_portable_alias()
    test_recovery_always_correlates_and_validates_existing_results()
    test_ten_concurrent_address_transactions_remain_consistent()
    print("All transaction tests passed.")


if __name__ == "__main__":
    main()
