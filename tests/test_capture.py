#!/usr/bin/env python3
"""Hermetic capture, privacy, queue, and recovery tests."""

from __future__ import annotations

import errno
import hashlib
import json
import multiprocessing
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/capture"
sys.path.insert(0, str(ROOT))

import claude_obsidian.capture as capture_module
from claude_obsidian.capture import (
    CaptureBudget,
    CaptureBudgetExceeded,
    CaptureConfig,
    CaptureConflict,
    CaptureError,
    CaptureQueue,
    CaptureQueueLock,
    CaptureValidationError,
    capture_filesystem,
    capture_filesystem_batch,
    discover_files,
    load_adapter_manifest,
    plan_external_action,
    plan_filesystem_batch,
    propose_deletion,
    sniff_metadata,
    validate_https_url,
    validate_redirect_chain,
)
from claude_obsidian.transaction import (
    MutationLock,
    TransactionConflict,
    TransactionValidationError,
)
from claude_obsidian.cli import _json_object_argument


def make_vault(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / ".obsidian").mkdir()
    (root / "wiki").mkdir()
    (root / ".raw").mkdir()
    (root / "inbox").mkdir()
    # macOS exposes temporary directories through both /var and /private/var.
    # Return the canonical path so assertions use the same spelling as the
    # production path-safety helpers.
    return root.resolve(strict=True)


def copy_fixture(vault: Path, name: str = "sample.md") -> Path:
    target = vault / "inbox" / name
    shutil.copyfile(FIXTURES / name, target)
    return target


def expect_code(code: str, callback) -> None:
    try:
        callback()
    except CaptureValidationError as exc:
        assert exc.code == code, (exc.code, str(exc))
    else:
        raise AssertionError(f"expected {code}")


def test_adapter_claims_are_honest() -> None:
    manifest = load_adapter_manifest(ROOT / "config/adapters.json")
    adapters = {item["id"]: item for item in manifest["adapters"]}
    assert set(adapters) == {
        "filesystem",
        "url",
        "image",
        "pdf",
        "youtube",
        "epub",
        "ocr",
    }
    assert adapters["filesystem"]["maturity"] == "implemented"
    assert all(
        item["maturity"] != "implemented"
        for key, item in adapters.items()
        if key != "filesystem"
    )
    assert all(item["destructive"] is False for item in adapters.values())


def test_cli_queue_json_arguments_reject_duplicate_keys() -> None:
    expect_code(
        "JSON_INVALID",
        lambda: _json_object_argument('{"path":"one","path":"two"}', "result"),
    )


def test_visible_inbox_and_legacy_raw_compatibility() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / "inbox/.gitkeep").touch()
        visible = copy_fixture(vault)
        legacy = vault / ".raw/legacy.txt"
        legacy.write_text("already immutable\n", encoding="utf-8")
        discovered = [
            item.relative_to(vault).as_posix() for item in discover_files(vault)
        ]
        assert discovered == [".raw/legacy.txt", "inbox/sample.md"]

        captured = capture_filesystem(vault, visible)
        assert captured["changed"] is True
        assert (
            captured["source_identity"]
            == hashlib.sha256(visible.read_bytes()).hexdigest()
        )
        stored = vault / captured["stored_path"]
        assert stored.read_bytes() == visible.read_bytes()
        assert stored.parent == vault / ".raw/captured"
        assert visible.exists(), "capture must not delete the visible inbox source"

        unchanged = capture_filesystem(vault, visible)
        assert unchanged["changed"] is False
        assert unchanged["skip_reason"] == "content-unchanged"
        assert unchanged["stored_path"] == captured["stored_path"]

        legacy_result = capture_filesystem(vault, legacy)
        assert legacy_result["changed"] is False
        assert legacy_result["skip_reason"] == "legacy-raw-source"


def _tree_snapshot(root: Path) -> list[tuple[str, str, bytes | None]]:
    values: list[tuple[str, str, bytes | None]] = []
    for candidate in sorted(root.rglob("*")):
        relative = candidate.relative_to(root).as_posix()
        if candidate.is_symlink():
            values.append((relative, "symlink", os.readlink(candidate).encode()))
        elif candidate.is_dir():
            values.append((relative, "directory", None))
        else:
            values.append((relative, "file", candidate.read_bytes()))
    return values


def test_filesystem_plan_is_read_only_and_matches_capture_preflight() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        source = copy_fixture(vault)
        before = _tree_snapshot(vault)
        plan = plan_filesystem_batch(vault, [source])
        after = _tree_snapshot(vault)
        assert after == before
        assert plan[0]["execute"] is False
        assert plan[0]["would_change"] is True
        assert (
            plan[0]["source_identity"]
            == hashlib.sha256(source.read_bytes()).hexdigest()
        )
        assert plan[0]["stored_path"].startswith(".raw/captured/")

        captured = capture_filesystem(vault, source)
        before_second_plan = _tree_snapshot(vault)
        no_change = plan_filesystem_batch(vault, [source])
        assert _tree_snapshot(vault) == before_second_plan
        assert no_change[0]["would_change"] is False
        assert no_change[0]["stored_path"] == captured["stored_path"]


def test_configurable_visible_inbox() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        (vault / "Capture").mkdir()
        source = vault / "Capture/note.txt"
        source.write_text("configured\n", encoding="utf-8")
        config = CaptureConfig(inbox="Capture", include_legacy_raw=False)
        assert discover_files(vault, config=config) == [source]
        expect_code(
            "INBOX_NOT_VISIBLE",
            lambda: CaptureConfig(inbox=".hidden", include_legacy_raw=False),
        )


def test_metadata_sniffing_is_bounded_and_deterministic() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        pdf = copy_fixture(vault, "sample.pdf")
        assert sniff_metadata(pdf)["kind"] == "pdf"
        png = vault / "inbox/pixel.png"
        png.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\x0dIHDR"
            b"\x00\x00\x00\x02\x00\x00\x00\x03"
            b"\x08\x06\x00\x00\x00"
        )
        metadata = sniff_metadata(png)
        assert metadata["kind"] == "image"
        assert (metadata["width"], metadata["height"]) == (2, 3)


def test_path_traversal_symlinks_and_malicious_names_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        outside = base / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        expect_code(
            "SOURCE_OUTSIDE_INBOX",
            lambda: capture_filesystem(vault, Path("../outside.md")),
        )

        link = vault / "inbox/link.md"
        link.symlink_to(outside)
        expect_code("SOURCE_OUTSIDE_INBOX", lambda: capture_filesystem(vault, link))
        link.unlink()
        inside = vault / "inbox/inside.md"
        inside.write_text("inside\n", encoding="utf-8")
        link.symlink_to(inside)
        expect_code("SOURCE_SYMLINK", lambda: capture_filesystem(vault, link))

        nested = vault / "inbox/nested"
        nested.mkdir()
        nested_link = vault / "inbox/alias"
        nested_link.symlink_to(nested, target_is_directory=True)
        aliased = nested_link / "note.md"
        (nested / "note.md").write_text("nested\n", encoding="utf-8")
        expect_code("SOURCE_SYMLINK", lambda: capture_filesystem(vault, aliased))

        malicious = vault / "inbox" / "bad\nname.md"
        malicious.write_text("bad\n", encoding="utf-8")
        expect_code("UNSAFE_FILENAME", lambda: capture_filesystem(vault, malicious))

        raw_capture = vault / ".raw/captured"
        raw_capture.symlink_to(base, target_is_directory=True)
        safe = copy_fixture(vault)
        expect_code("RAW_STORE_SYMLINK", lambda: capture_filesystem(vault, safe))


def test_batch_budgets_are_preflighted_before_copy() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        one = vault / "inbox/one.txt"
        two = vault / "inbox/two.txt"
        one.write_bytes(b"1" * 8)
        two.write_bytes(b"2" * 8)
        try:
            capture_filesystem_batch(
                vault,
                [one, two],
                budget=CaptureBudget(
                    max_items=2, max_file_bytes=10, max_total_bytes=12
                ),
            )
        except CaptureBudgetExceeded as exc:
            assert exc.code == "TOTAL_BUDGET_EXCEEDED"
        else:
            raise AssertionError("total budget must fail")
        assert not (vault / ".raw/captured").exists(), (
            "failed preflight must not copy partial input"
        )
        try:
            capture_filesystem_batch(
                vault,
                [one, two],
                budget=CaptureBudget(
                    max_items=1, max_file_bytes=10, max_total_bytes=10
                ),
            )
        except CaptureBudgetExceeded as exc:
            assert exc.code == "COUNT_BUDGET_EXCEEDED"
        else:
            raise AssertionError("count budget must fail")


def test_direct_batch_rolls_back_as_one_transaction() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        one = vault / "inbox/one.txt"
        two = vault / "inbox/two.txt"
        one.write_text("one\n", encoding="utf-8")
        two.write_text("two\n", encoding="utf-8")
        original_apply = capture_module.apply_bundle

        def fail_after_first(vault_root, bundle_or_path, **kwargs):
            return original_apply(vault_root, bundle_or_path, fail_after=1, **kwargs)

        capture_module.apply_bundle = fail_after_first
        try:
            try:
                capture_filesystem_batch(vault, [one, two])
            except RuntimeError as exc:
                assert "injected failure after write 1" in str(exc)
            else:
                raise AssertionError("the injected second-item failure must propagate")
        finally:
            capture_module.apply_bundle = original_apply

        captured = vault / ".raw/captured"
        assert not captured.exists() or list(captured.iterdir()) == []
        transaction_dirs = list((vault / ".vault-meta/transactions").iterdir())
        assert len(transaction_dirs) == 1
        journal = json.loads(
            (transaction_dirs[0] / "journal.json").read_text(encoding="utf-8")
        )
        assert journal["state"] == "rolled-back"
        assert one.exists() and two.exists()


def test_url_privacy_policy_has_no_network_dependency() -> None:
    original_socket = socket.socket

    class NoNetwork:
        def __init__(self, *args, **kwargs):
            raise AssertionError("capture validation attempted network access")

    socket.socket = NoNetwork
    try:
        assert (
            validate_https_url("https://example.com/page?q=offline")
            == "https://example.com/page?q=offline"
        )
        cases = {
            "URL_SCHEME_FORBIDDEN": "http://example.com/",
            "URL_PRIVATE_HOST": "https://127.0.0.1/",
            "URL_PRIVATE_HOST_2": "https://[::1]/",
            "URL_PRIVATE_HOST_3": "https://localhost/",
            "URL_USERINFO_FORBIDDEN": "https://user:pass@example.com/",
            "URL_SECRET_FORBIDDEN": "https://example.com/?token=secret",
        }
        for label, url in cases.items():
            expected = label.split("_2", 1)[0].split("_3", 1)[0]
            expect_code(expected, lambda url=url: validate_https_url(url))
        assert (
            validate_redirect_chain(
                "https://example.com/start",
                ["https://cdn.example.net/end"],
                approved_hosts=["cdn.example.net"],
            )[-1]
            == "https://cdn.example.net/end"
        )
        expect_code(
            "REDIRECT_HOST_FORBIDDEN",
            lambda: validate_redirect_chain(
                "https://example.com/start", ["https://attacker.example/end"]
            ),
        )
    finally:
        socket.socket = original_socket


def test_public_host_validation_rejects_alternate_loopback_spellings() -> None:
    must_block = {
        "hex_dotted": "https://0x7f.0.0.1/",
        "octal_dotted": "https://0177.0.0.1/",
        "short_form": "https://127.1/",
        "hex_all_labels": "https://0x7f.0x0.0x0.0x1/",
    }
    still_blocked = {
        "decimal_single_label": "https://2130706433/",
        "hex_single_label": "https://0x7f000001/",
        "ipv6_loopback": "https://[::1]/",
        "ipv4_mapped_ipv6": "https://[::ffff:127.0.0.1]/",
        "link_local_metadata": "https://169.254.169.254/",
        "trailing_dot_localhost": "https://localhost./",
    }
    for label, url in must_block.items():
        expect_code("URL_PRIVATE_HOST", lambda url=url: validate_https_url(url))
    for label, url in still_blocked.items():
        expect_code("URL_PRIVATE_HOST", lambda url=url: validate_https_url(url))


def test_aws_signed_urls_and_userinfo_are_rejected() -> None:
    expect_code(
        "URL_USERINFO_FORBIDDEN",
        lambda: validate_https_url("https://user:password@example.com/private"),
    )
    signed_urls = (
        "https://example.com/object?X-Amz-Signature=secret",
        "https://example.com/object?X-Amz-Credential=AKIAEXAMPLE",
        "https://example.com/object?X-Amz-Security-Token=secret",
        "https://example.com/object?AWSAccessKeyId=AKIAEXAMPLE",
        "https://example.com/object?X-Amz-%53ignature=secret",
    )
    for url in signed_urls:
        expect_code("URL_SECRET_FORBIDDEN", lambda url=url: validate_https_url(url))
    assert validate_https_url("https://example.com/object?monkey=banana").endswith(
        "?monkey=banana"
    )


def test_external_work_is_only_an_inert_plan() -> None:
    plan = plan_external_action("url", "https://example.com/article")
    assert plan["state"] == "planned"
    assert plan["execute"] is False
    assert plan["requires_explicit_consent"] is True
    assert plan["runner_placeholder"] is True
    assert plan["command"] == [
        "{external-runner}",
        "url",
        "--source",
        "https://example.com/article",
    ]
    local = plan_external_action("ocr", "inbox/scan.png", runner=["local-ocr"])
    assert local["privacy"]["network"] is False
    assert local["command"] == ["local-ocr", "ocr", "--source", "inbox/scan.png"]


def test_queue_lifecycle_is_idempotent() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        queue = CaptureQueue(vault)
        first = queue.enqueue("filesystem", "inbox/sample.md", source_sha256="a" * 64)
        duplicate = queue.enqueue("filesystem", "renamed.md", source_sha256="a" * 64)
        assert duplicate == first
        assert len(queue.list()) == 1

        claimed = queue.claim(worker="test")
        assert claimed is not None and claimed["state"] == "claimed"
        token = claimed["claim"]["token"]
        completed = queue.complete(
            first["id"], token, {"stored_path": ".raw/captured/a.md"}
        )
        assert completed["state"] == "completed"
        assert (
            queue.complete(first["id"], token, {"stored_path": ".raw/captured/a.md"})
            == completed
        )
        try:
            queue.complete(first["id"], token, {"stored_path": "different"})
        except CaptureConflict as exc:
            assert exc.code == "QUEUE_COMPLETION_CONFLICT"
        else:
            raise AssertionError("different repeated completion must conflict")
        assert queue.claim() is None

        url_plan = plan_external_action("url", "https://example.com/source")
        url_item = queue.enqueue(
            "url", "https://example.com/source", planned_action=url_plan
        )
        assert url_item["planned_action"]["execute"] is False
        expect_code(
            "EXTERNAL_ACTION_REQUIRED",
            lambda: queue.enqueue("url", "https://example.net/unplanned"),
        )


def test_queue_failure_resume_and_crash_recovery() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        queue = CaptureQueue(vault)
        item = queue.enqueue(
            "filesystem", "inbox/failure.md", idempotency_key="failure"
        )
        claimed = queue.claim(item["id"])
        assert claimed is not None
        failed = queue.fail(
            item["id"], claimed["claim"]["token"], "deterministic failure"
        )
        assert failed["state"] == "failed"
        resumed = queue.resume(item["id"])
        assert len(resumed) == 1 and resumed[0]["state"] == "queued"

        claimed_again = queue.claim(item["id"])
        assert claimed_again is not None
        document = json.loads(queue.path.read_text(encoding="utf-8"))
        entry = next(
            value for value in document["entries"] if value["id"] == item["id"]
        )
        entry["claim"]["pid"] = 99999999
        entry["claim"]["host"] = socket.gethostname()
        entry["claim"]["claimed_epoch"] = 0
        queue.path.write_text(json.dumps(document), encoding="utf-8")
        resumed_dead = queue.resume(item["id"], stale_after=0)
        assert len(resumed_dead) == 1 and resumed_dead[0]["state"] == "queued"

        # Make a valid backup, then prove a malformed primary recovers from it.
        queue.claim(item["id"])
        assert queue.backup_path.exists()
        queue.path.write_text("{partial", encoding="utf-8")
        recovered = queue.recover()
        assert recovered["schema"] == "claude-obsidian.capture-queue.v1"
        assert json.loads(queue.path.read_text(encoding="utf-8")) == recovered


def test_queue_rejects_malformed_entries_and_mismatched_actions() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        queue = CaptureQueue(vault)
        now = "2026-07-12T00:00:00Z"
        malformed = {
            "schema": "claude-obsidian.capture-queue.v1",
            "revision": 1,
            "entries": [
                {
                    "id": "a" * 24,
                    "idempotency_key": "malformed-claim",
                    "adapter": "filesystem",
                    "source": "inbox/source.md",
                    "source_sha256": None,
                    "state": "claimed",
                    "attempts": 1,
                    "created_at": now,
                    "updated_at": now,
                    "claim": "not-an-object",
                    "planned_action": None,
                    "metadata": {},
                    "result": None,
                    "error": None,
                }
            ],
        }
        queue.path.write_text(json.dumps(malformed), encoding="utf-8")
        expect_code("QUEUE_INVALID", queue.list)

        queue.path.write_text(
            '{"schema":"claude-obsidian.capture-queue.v1",'
            '"revision":0,"revision":1,"entries":[]}',
            encoding="utf-8",
        )
        expect_code("QUEUE_INVALID", queue.list)

        queue.path.unlink()
        wrong_source = plan_external_action("url", "https://example.net/wrong")
        expect_code(
            "QUEUE_ACTION_INVALID",
            lambda: queue.enqueue(
                "url",
                "https://example.com/right",
                planned_action=wrong_source,
                idempotency_key="wrong-source",
            ),
        )
        wrong_privacy = plan_external_action("url", "https://example.com/right")
        wrong_privacy["privacy"]["network"] = False
        expect_code(
            "QUEUE_ACTION_INVALID",
            lambda: queue.enqueue(
                "url",
                "https://example.com/right",
                planned_action=wrong_privacy,
                idempotency_key="wrong-privacy",
            ),
        )


def _hold_queue_lock(
    vault: str, ready: multiprocessing.Event, release: multiprocessing.Event
) -> None:
    with CaptureQueueLock(Path(vault), timeout=1):
        ready.set()
        release.wait(5)


def _hold_mutation_lock(
    vault: str,
    ready: multiprocessing.Event,
    release: multiprocessing.Event,
) -> None:
    with MutationLock(Path(vault), timeout=1):
        ready.set()
        release.wait(5)


def _enqueue_queue_worker(
    vault: str,
    index: int,
    start: multiprocessing.Event,
    outcomes: multiprocessing.Queue,
) -> None:
    start.wait(5)
    try:
        CaptureQueue(Path(vault), timeout=5).enqueue(
            "filesystem",
            f"inbox/concurrent-{index}.md",
            idempotency_key=f"concurrent-{index}",
        )
    except BaseException as exc:
        outcomes.put((index, False, repr(exc)))
    else:
        outcomes.put((index, True, ""))


def test_queue_lock_is_process_held() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        ready = multiprocessing.Event()
        release = multiprocessing.Event()
        process = multiprocessing.Process(
            target=_hold_queue_lock, args=(str(vault), ready, release)
        )
        process.start()
        assert ready.wait(3)
        try:
            CaptureQueueLock(vault, timeout=0.05, stale_after=0).acquire()
        except CaptureConflict as exc:
            assert exc.code == "QUEUE_LOCK_TIMEOUT"
        else:
            raise AssertionError("live process-held queue lock must not be reaped")
        release.set()
        process.join(3)
        assert process.exitcode == 0


def test_queue_and_mutation_locks_share_the_vault_advisory_lock() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        CaptureQueue(vault)

        ready = multiprocessing.Event()
        release = multiprocessing.Event()
        mutation = multiprocessing.Process(
            target=_hold_mutation_lock,
            args=(str(vault), ready, release),
        )
        mutation.start()
        assert ready.wait(3)
        try:
            CaptureQueueLock(vault, timeout=0.05).acquire()
        except CaptureConflict as exc:
            assert exc.code == "QUEUE_LOCK_TIMEOUT"
        else:
            raise AssertionError(
                "capture writes must serialize behind a vault mutation"
            )
        release.set()
        mutation.join(3)
        assert mutation.exitcode == 0

        ready = multiprocessing.Event()
        release = multiprocessing.Event()
        capture = multiprocessing.Process(
            target=_hold_queue_lock,
            args=(str(vault), ready, release),
        )
        capture.start()
        assert ready.wait(3)
        try:
            MutationLock(vault, timeout=0.05).acquire()
        except TransactionConflict as exc:
            assert exc.code == "LOCK_TIMEOUT"
        else:
            raise AssertionError("vault mutations must serialize behind capture writes")
        release.set()
        capture.join(3)
        assert capture.exitcode == 0


def test_nested_queue_lock_attempt_fails_promptly_without_leaking() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        outer = CaptureQueueLock(vault, timeout=1)
        with outer:
            started = time.monotonic()
            try:
                CaptureQueueLock(vault, timeout=0).acquire()
            except CaptureConflict as exc:
                assert exc.code == "QUEUE_LOCK_TIMEOUT"
            else:
                raise AssertionError("a nested queue lock must not silently deadlock")
            assert time.monotonic() - started < 1
        assert outer._root_fd is None
        assert outer._parent_fd is None
        assert outer._lock_fd is None


def test_queue_lock_maps_advisory_lock_platform_errors() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        original = capture_module._try_vault_advisory_lock

        def unsupported(_descriptor: int) -> bool:
            raise OSError(errno.ENOLCK, "advisory locking unavailable")

        capture_module._try_vault_advisory_lock = unsupported
        try:
            try:
                CaptureQueueLock(vault, timeout=0).acquire()
            except CaptureError as exc:
                assert exc.code == "QUEUE_LOCK_FAILED"
            else:
                raise AssertionError(
                    "platform lock errors must use the stable queue code"
                )
        finally:
            capture_module._try_vault_advisory_lock = original


def test_concurrent_queue_writers_are_lossless_and_serialized() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        CaptureQueue(vault)
        start = multiprocessing.Event()
        outcomes: multiprocessing.Queue = multiprocessing.Queue()
        workers = [
            multiprocessing.Process(
                target=_enqueue_queue_worker,
                args=(str(vault), index, start, outcomes),
            )
            for index in range(8)
        ]
        for worker in workers:
            worker.start()
        start.set()
        results = [outcomes.get(timeout=10) for _ in workers]
        for worker in workers:
            worker.join(10)
            assert worker.exitcode == 0
        assert all(success for _index, success, _error in results), results
        entries = CaptureQueue(vault).list()
        assert {entry["idempotency_key"] for entry in entries} == {
            f"concurrent-{index}" for index in range(len(workers))
        }


def test_explicit_queue_recovery_can_reap_stale_pid_reuse_lock() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        seeded = CaptureQueueLock(vault)
        seeded.path.mkdir()
        seeded.owner_path.write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.capture-lock.v1",
                    "pid": os.getpid(),
                    "host": socket.gethostname(),
                    "token": "reused-pid",
                    "started_epoch": 0,
                }
            ),
            encoding="utf-8",
        )
        try:
            CaptureQueueLock(vault, timeout=0, stale_after=0).acquire()
        except CaptureConflict as exc:
            assert exc.code == "QUEUE_LOCK_TIMEOUT"
        else:
            raise AssertionError(
                "automatic recovery must not steal a possibly live queue lock"
            )

        recovered = CaptureQueue(
            vault,
            timeout=0,
            stale_after=0,
            force_stale_lock=True,
        ).recover()
        assert recovered["schema"] == "claude-obsidian.capture-queue.v1"
        assert not seeded.path.exists()


def test_ownerless_queue_lock_requires_explicit_force() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        seeded = CaptureQueueLock(vault, timeout=0, stale_after=0)
        seeded.path.mkdir()
        os.utime(seeded.path, (0, 0))
        try:
            CaptureQueueLock(vault, timeout=0, stale_after=0).acquire()
        except CaptureConflict as exc:
            assert exc.code == "QUEUE_LOCK_TIMEOUT"
        else:
            raise AssertionError(
                "ownerless queue lock must not be stolen without force"
            )
        assert seeded.path.is_dir()

        with CaptureQueueLock(
            vault,
            timeout=0,
            stale_after=0,
            force_stale_lock=True,
        ):
            assert seeded.owner_path.is_file()
        assert not seeded.path.exists()


def test_queue_lock_release_and_reaping_ignore_replaced_external_alias() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        lock = CaptureQueueLock(vault, timeout=0)
        lock.acquire()

        displaced = lock.path.with_name("queue.lock.displaced")
        os.rename(lock.path, displaced)
        outside = base / "outside-capture-lock"
        outside.mkdir()
        outside_owner = outside / "owner.json"
        outside_owner.write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.capture-lock.v1",
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
        except CaptureConflict as exc:
            assert exc.code == "QUEUE_LOCK_OWNERSHIP_LOST"
        else:
            raise AssertionError("a replaced capture lock path must fail closed")
        assert lock.path.is_symlink()
        assert outside_owner.read_bytes() == before
        assert (displaced / "owner.json").is_file()

        try:
            CaptureQueueLock(
                vault,
                timeout=0,
                stale_after=0,
                force_stale_lock=True,
            ).acquire()
        except CaptureConflict as exc:
            assert exc.code == "QUEUE_LOCK_TIMEOUT"
        else:
            raise AssertionError(
                "forced reaping must not follow an external queue-lock alias"
            )
        assert lock.path.is_symlink()
        assert outside_owner.read_bytes() == before


def _replace_runtime_boundary(
    base: Path,
    vault: Path,
    boundary: str,
) -> tuple[Path, Path]:
    """Replace one public directory entry and return pinned/external runtimes."""

    outside = base / f"outside-{boundary}"
    if boundary == "vault":
        selected = base / "selected-vault"
        os.rename(vault, selected)
        outside.mkdir()
        external_runtime = outside / ".vault-meta/capture"
        external_runtime.mkdir(parents=True)
        vault.symlink_to(outside, target_is_directory=True)
        return selected / ".vault-meta/capture", external_runtime
    if boundary == "metadata":
        selected = vault / ".vault-meta.selected"
        os.rename(vault / ".vault-meta", selected)
        outside.mkdir()
        external_runtime = outside / "capture"
        external_runtime.mkdir()
        (vault / ".vault-meta").symlink_to(outside, target_is_directory=True)
        return selected / "capture", external_runtime
    if boundary == "capture":
        selected = vault / ".vault-meta/capture.selected"
        os.rename(vault / ".vault-meta/capture", selected)
        outside.mkdir()
        (vault / ".vault-meta/capture").symlink_to(outside, target_is_directory=True)
        return selected, outside
    raise AssertionError(f"unknown boundary: {boundary}")


def test_queue_io_stays_on_pinned_runtime_across_directory_replacement() -> None:
    for boundary in ("vault", "metadata", "capture"):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            vault = make_vault(base / "vault")
            queue = CaptureQueue(vault)
            queue.enqueue("filesystem", "inbox/seed.md", idempotency_key="seed")
            original_primary = queue.path.read_bytes()

            lock = queue.lock()
            lock.acquire()
            runtime_fd = lock.duplicate_runtime_fd()
            try:
                selected_runtime, external_runtime = _replace_runtime_boundary(
                    base,
                    vault,
                    boundary,
                )
                external_primary = external_runtime / "queue.json"
                external_backup = external_runtime / "queue.previous.json"
                external_primary.write_bytes(b"external-primary\n")
                external_backup.write_bytes(b"external-backup\n")
                before_external = (
                    external_primary.read_bytes(),
                    external_backup.read_bytes(),
                )

                document = queue._load_locked(runtime_fd, recover=True)
                document["revision"] += 1
                queue._save_locked(runtime_fd, document)
            finally:
                os.close(runtime_fd)
                lock.release()

            selected_document = json.loads(
                (selected_runtime / "queue.json").read_text(encoding="utf-8")
            )
            assert selected_document["revision"] == 2
            assert (
                selected_runtime / "queue.previous.json"
            ).read_bytes() == original_primary
            assert (
                external_primary.read_bytes(),
                external_backup.read_bytes(),
            ) == before_external


class _ReplacingQueueFile(CaptureQueue):
    def __init__(self, vault_root: Path):
        super().__init__(vault_root)
        self._replacement_name: str | None = None
        self._replacement_target: Path | None = None
        self._replacement_displaced: Path | None = None

    def arm_replacement(self, name: str, target: Path, displaced: Path) -> None:
        self._replacement_name = name
        self._replacement_target = target
        self._replacement_displaced = displaced

    def _write_runtime(self, runtime_fd: int, name: str, data: bytes) -> None:
        if name == self._replacement_name:
            target = self._replacement_target
            displaced = self._replacement_displaced
            assert target is not None and displaced is not None
            public = self.runtime / name
            if public.exists() or public.is_symlink():
                os.rename(public, displaced)
            public.symlink_to(target)
            self._replacement_name = None
        super()._write_runtime(runtime_fd, name, data)


def test_queue_atomic_file_replacement_never_writes_through_external_aliases() -> None:
    for name in ("queue.json", "queue.previous.json"):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            vault = make_vault(base / "vault")
            queue = _ReplacingQueueFile(vault)
            queue.enqueue("filesystem", "inbox/seed.md", idempotency_key="seed")
            outside = base / f"outside-{name}"
            outside.write_bytes(b"external-must-survive\n")
            displaced = queue.runtime / f"{name}.displaced"
            queue.arm_replacement(name, outside, displaced)

            queue.enqueue("filesystem", "inbox/next.md", idempotency_key="next")

            assert outside.read_bytes() == b"external-must-survive\n"
            written = queue.runtime / name
            assert written.is_file() and not written.is_symlink()
            assert (
                displaced.is_file() if name == "queue.json" else not displaced.exists()
            )
            assert len(queue.list()) == 2


def test_queue_operations_do_not_leak_runtime_descriptors() -> None:
    descriptor_directory = Path("/proc/self/fd")
    if not descriptor_directory.is_dir():
        return
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        queue = CaptureQueue(vault)
        queue.enqueue("filesystem", "inbox/seed.md", idempotency_key="seed")
        before = len(list(descriptor_directory.iterdir()))
        for _index in range(50):
            assert len(queue.list()) == 1
        after = len(list(descriptor_directory.iterdir()))
        assert after == before

        lock = queue.lock()
        try:
            lock.duplicate_runtime_fd()
        except CaptureError as exc:
            assert exc.code == "QUEUE_LOCK_NOT_HELD"
        else:
            raise AssertionError(
                "runtime descriptors must only be duplicated while held"
            )


def test_queue_primary_and_backup_symlinks_are_never_read() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vault = make_vault(base / "vault")
        queue = CaptureQueue(vault)
        outside = base / "outside.json"
        outside.write_text(
            json.dumps(
                {
                    "schema": "claude-obsidian.capture-queue.v1",
                    "revision": 0,
                    "entries": [],
                }
            ),
            encoding="utf-8",
        )
        queue.path.symlink_to(outside)
        try:
            queue.list()
        except TransactionValidationError as exc:
            assert exc.code in {"PATH_OUTSIDE_VAULT", "SYMLINK_WRITE_PATH"}
        else:
            raise AssertionError("queue primary symlink must fail closed")
        queue.path.unlink()
        queue.path.write_text("{invalid", encoding="utf-8")
        queue.backup_path.symlink_to(outside)
        try:
            queue.recover()
        except TransactionValidationError as exc:
            assert exc.code in {"PATH_OUTSIDE_VAULT", "SYMLINK_WRITE_PATH"}
        else:
            raise AssertionError("queue backup symlink must fail closed")


def test_queue_write_and_read_limits_are_one_durable_contract() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        queue = CaptureQueue(vault)
        queue.enqueue("filesystem", "inbox/seed.md", idempotency_key="seed")

        original_bytes = queue.path.read_bytes()
        original_limit = capture_module.MAX_QUEUE_BYTES
        try:
            capture_module.MAX_QUEUE_BYTES = max(len(original_bytes) + 256, 1024)
            oversized_metadata = "x" * (capture_module.MAX_QUEUE_BYTES * 2)
            expect_code(
                "QUEUE_SIZE_LIMIT",
                lambda: queue.enqueue(
                    "filesystem",
                    "inbox/oversized.md",
                    idempotency_key="oversized",
                    metadata={"payload": oversized_metadata},
                ),
            )
            assert queue.path.read_bytes() == original_bytes
            assert [item["idempotency_key"] for item in queue.list()] == ["seed"]

            # Repeated individually-small entries must stop before the durable
            # file envelope and leave the last accepted document readable.
            last_good = queue.path.read_bytes()
            rejected = False
            for index in range(100):
                try:
                    queue.enqueue(
                        "filesystem",
                        f"inbox/item-{index}.md",
                        idempotency_key=f"item-{index}",
                        metadata={"label": "bounded"},
                    )
                except CaptureValidationError as exc:
                    assert exc.code == "QUEUE_SIZE_LIMIT"
                    rejected = True
                    assert queue.path.read_bytes() == last_good
                    break
                last_good = queue.path.read_bytes()
            assert rejected, "the reduced queue limit must eventually reject growth"
            assert queue.list()
        finally:
            capture_module.MAX_QUEUE_BYTES = original_limit


def test_oversized_queue_primary_recovers_from_bounded_backup() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        queue = CaptureQueue(vault)
        item = queue.enqueue("filesystem", "inbox/source.md", idempotency_key="source")
        claimed = queue.claim(item["id"])
        assert claimed is not None and queue.backup_path.is_file()

        backup = queue.backup_path.read_bytes()
        original_limit = capture_module.MAX_QUEUE_BYTES
        try:
            capture_module.MAX_QUEUE_BYTES = max(len(backup) + 128, 1024)
            queue.path.write_bytes(b"{" + b" " * capture_module.MAX_QUEUE_BYTES + b"}")
            recovered = queue.recover()
            assert recovered["entries"][0]["state"] == "queued"
            assert len(queue.path.read_bytes()) <= capture_module.MAX_QUEUE_BYTES
            assert queue.list()[0]["idempotency_key"] == "source"
        finally:
            capture_module.MAX_QUEUE_BYTES = original_limit


def test_queue_entry_count_is_bounded_before_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        queue = CaptureQueue(vault)
        original_limit = capture_module.MAX_QUEUE_ENTRIES
        try:
            capture_module.MAX_QUEUE_ENTRIES = 1
            queue.enqueue("filesystem", "inbox/one.md", idempotency_key="one")
            before = queue.path.read_bytes()
            expect_code(
                "QUEUE_ENTRY_LIMIT",
                lambda: queue.enqueue(
                    "filesystem", "inbox/two.md", idempotency_key="two"
                ),
            )
            assert queue.path.read_bytes() == before
            assert len(queue.list()) == 1
        finally:
            capture_module.MAX_QUEUE_ENTRIES = original_limit


def test_deletion_is_review_only() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        source = copy_fixture(vault)
        proposal = propose_deletion(vault, source, reason="captured successfully")
        assert proposal["state"] == "review-required"
        assert proposal["execute"] is False
        assert proposal["action"] == "delete"
        assert source.exists()


def test_cli_capture_uses_one_recoverable_binary_transaction() -> None:
    with tempfile.TemporaryDirectory() as td:
        vault = make_vault(Path(td) / "vault")
        source = vault / "inbox/payload.pdf"
        payload = b"%PDF-1.4\n\x00binary fixture\n"
        source.write_bytes(payload)
        common = [
            sys.executable,
            str(ROOT / "scripts/claude-obsidian.py"),
            "capture",
            "apply",
            "--vault",
            str(vault),
            "--operation-id",
            "capture-cli-test",
            "--generated-at",
            "2026-07-11T12:00:00Z",
            "inbox/payload.pdf",
        ]
        planned = subprocess.run(common, capture_output=True, text=True, check=False)
        assert planned.returncode == 0, planned.stderr
        plan = json.loads(planned.stdout)
        assert plan["status"] == "dry-run"
        assert not (vault / ".raw/captured").exists()
        assert not (vault / ".vault-meta").exists()

        applied = subprocess.run(
            [
                *common,
                "--approved-plan-sha256",
                plan["approved_plan_sha256"],
                "--apply",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert applied.returncode == 0, applied.stderr
        result = json.loads(applied.stdout)
        assert result["transaction"]["operation_id"] == "capture-cli-test"
        stored = vault / result["items"][0]["stored_path"]
        assert stored.read_bytes() == payload
        assert result["transaction"]["changed_paths"] == [
            stored.relative_to(vault).as_posix()
        ]


def main() -> None:
    multiprocessing.set_start_method("fork" if os.name != "nt" else "spawn", force=True)
    test_adapter_claims_are_honest()
    test_cli_queue_json_arguments_reject_duplicate_keys()
    test_visible_inbox_and_legacy_raw_compatibility()
    test_filesystem_plan_is_read_only_and_matches_capture_preflight()
    test_configurable_visible_inbox()
    test_metadata_sniffing_is_bounded_and_deterministic()
    test_path_traversal_symlinks_and_malicious_names_fail_closed()
    test_batch_budgets_are_preflighted_before_copy()
    test_direct_batch_rolls_back_as_one_transaction()
    test_url_privacy_policy_has_no_network_dependency()
    test_public_host_validation_rejects_alternate_loopback_spellings()
    test_aws_signed_urls_and_userinfo_are_rejected()
    test_external_work_is_only_an_inert_plan()
    test_queue_lifecycle_is_idempotent()
    test_queue_failure_resume_and_crash_recovery()
    test_queue_rejects_malformed_entries_and_mismatched_actions()
    test_queue_lock_is_process_held()
    test_queue_and_mutation_locks_share_the_vault_advisory_lock()
    test_nested_queue_lock_attempt_fails_promptly_without_leaking()
    test_queue_lock_maps_advisory_lock_platform_errors()
    test_concurrent_queue_writers_are_lossless_and_serialized()
    test_explicit_queue_recovery_can_reap_stale_pid_reuse_lock()
    test_ownerless_queue_lock_requires_explicit_force()
    test_queue_lock_release_and_reaping_ignore_replaced_external_alias()
    test_queue_io_stays_on_pinned_runtime_across_directory_replacement()
    test_queue_atomic_file_replacement_never_writes_through_external_aliases()
    test_queue_operations_do_not_leak_runtime_descriptors()
    test_queue_primary_and_backup_symlinks_are_never_read()
    test_queue_write_and_read_limits_are_one_durable_contract()
    test_oversized_queue_primary_recovers_from_bounded_backup()
    test_queue_entry_count_is_bounded_before_mutation()
    test_deletion_is_review_only()
    test_cli_capture_uses_one_recoverable_binary_transaction()
    print("All capture tests passed.")


if __name__ == "__main__":
    main()
