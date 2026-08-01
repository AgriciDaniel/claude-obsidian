"""Command-line interface for the portable claude-obsidian core."""

from __future__ import annotations

import argparse
import hmac
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from . import __version__
from .capture import (
    CaptureBudget,
    CaptureConfig,
    CaptureConflict,
    CaptureError,
    CaptureQueue,
    CaptureValidationError,
    discover_files,
    load_adapter_manifest,
    plan_external_action,
    plan_filesystem_batch,
)
from .checkpoint import checkpoint_operation
from .contracts import evaluate_capabilities, validate_contracts
from .extensions import dragonscale_bundle
from .gates import evaluate_release_gates
from .hook_adapter import emit_session_start, emit_stop_status
from .ledgers import LedgerValidationError, migration_bundle, strict_json_loads
from .lint_engine import lint_vault, render_markdown
from .mode_config import validate_mode_folders
from .package_validation import validate_package
from .paths import (
    VaultSelection,
    VaultSelectionError,
    assert_not_plugin_tree,
    resolve_vault_root,
)
from .release import audit_artifact, build_public_artifact
from .transaction import (
    MutationLock,
    TransactionError,
    TransactionValidationError,
    _require_write_platform,
    apply_bundle,
    inspect_bundle,
    read_vault_regular,
    recover_incomplete,
    sha256_bytes,
)
from .vault_ops import VaultOperationError, build_vault_bundle, scan_vault


PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def _emit(value: Any, *, pretty: bool = True) -> None:
    if isinstance(value, str):
        print(value)
        return
    print(
        json.dumps(
            value, indent=2 if pretty else None, sort_keys=True, ensure_ascii=False
        )
    )


def _approval_fields(
    vault_root: Path, operation: dict[str, Any], generated_at: str
) -> dict[str, str]:
    approval_hash = str(inspect_bundle(vault_root, operation)["approval_sha256"])
    return {
        "approved_plan_sha256": approval_hash,
        "generated_at": generated_at,
        "approval_hint": (
            "review the operation, then repeat the exact pinned command with "
            f"--approved-plan-sha256 {approval_hash} --apply"
        ),
    }


def _require_approved_plan(
    args: argparse.Namespace, vault_root: Path, operation: dict[str, Any]
) -> dict[str, Any]:
    plan = inspect_bundle(vault_root, operation)
    actual = str(plan["approval_sha256"])
    supplied = getattr(args, "approved_plan_sha256", None)
    if not supplied:
        raise TransactionValidationError(
            "PLAN_APPROVAL_REQUIRED",
            "--apply requires --approved-plan-sha256 from the reviewed dry-run",
        )
    if not hmac.compare_digest(supplied, actual):
        raise TransactionValidationError(
            "PLAN_CHANGED",
            "the regenerated transaction differs from the reviewed plan; run a new dry-run and pin its generated_at and operation_id",
        )
    return plan


def _require_approved_operation(
    args: argparse.Namespace, vault_root: Path, operation: dict[str, Any]
) -> str:
    return str(_require_approved_plan(args, vault_root, operation)["approval_sha256"])


def _add_vault_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--vault", help="Explicit user vault root")


def _add_approval_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--approved-plan-sha256",
        metavar="SHA256",
        help="Exact canonical hash emitted by the reviewed dry-run",
    )


def _selection(
    args: argparse.Namespace, *, allow_uninitialized: bool = False
) -> VaultSelection:
    return resolve_vault_root(
        args.vault,
        plugin_root=PLUGIN_ROOT,
        allow_uninitialized=allow_uninitialized,
        allow_plugin_root=False,
    )


def command_doctor(args: argparse.Namespace) -> int:
    selection = _selection(args)
    root = selection.root
    checks = {
        "vault_exists": root.is_dir(),
        "obsidian_config": (root / ".obsidian").is_dir(),
        "wiki": (root / "wiki").is_dir(),
        "raw": (root / ".raw").is_dir(),
        "meta_writable": (root / ".vault-meta").exists()
        or root.exists()
        and os_access_writable(root),
        "mutation_lock_held": (root / ".vault-meta" / "mutation.lock").exists(),
    }
    report = {
        "schema": "claude-obsidian.doctor.v1",
        "version": __version__,
        "vault_root": str(root),
        "selection_source": selection.source,
        "legacy_layout": selection.legacy,
        "checks": checks,
        "ok": all(
            value for key, value in checks.items() if key != "mutation_lock_held"
        ),
    }
    _emit(report)
    return 0 if report["ok"] else 1


def os_access_writable(path: Path) -> bool:
    import os

    return os.access(path, os.W_OK)


def command_transaction_apply(args: argparse.Namespace) -> int:
    selection = _selection(args)
    if not args.approved_plan_sha256:
        raise TransactionValidationError(
            "PLAN_APPROVAL_REQUIRED",
            "transaction apply requires --approved-plan-sha256 from transaction inspect",
        )
    result = apply_bundle(
        selection.root,
        args.bundle,
        timeout=args.timeout,
        stale_after=args.stale_after,
        approved_plan_sha256=args.approved_plan_sha256,
    )
    _emit(result)
    return 0


def command_transaction_recover(args: argparse.Namespace) -> int:
    selection = _selection(args)
    with MutationLock(
        selection.root,
        timeout=args.timeout,
        stale_after=args.stale_after,
        force_stale_lock=args.force_stale_lock,
    ) as mutation_lock:
        recovered = recover_incomplete(selection.root, mutation_lock=mutation_lock)
    _emit(
        {
            "schema": "claude-obsidian.transaction-recovery.v1",
            "recovered": recovered,
            "forced_stale_lock": bool(args.force_stale_lock),
        }
    )
    return 0


def command_transaction_inspect(args: argparse.Namespace) -> int:
    selection = _selection(args)
    _emit(inspect_bundle(selection.root, args.bundle))
    return 0


def command_hook_session_start(args: argparse.Namespace) -> int:
    return emit_session_start(plugin_root=PLUGIN_ROOT)


def command_hook_stop(args: argparse.Namespace) -> int:
    return emit_stop_status(plugin_root=PLUGIN_ROOT)


def command_lint(args: argparse.Namespace) -> int:
    selection = _selection(args)
    report = lint_vault(selection.root, as_of=args.as_of)
    if args.format == "markdown":
        sys.stdout.write(render_markdown(report))
    else:
        _emit(report)
    return 1 if args.strict and report["summary"]["issues_found"] else 0


def command_contracts(args: argparse.Namespace) -> int:
    if args.check_only:
        errors = validate_contracts(PLUGIN_ROOT)
        payload = {
            "schema_version": 1,
            "valid": not errors,
            "errors": errors,
        }
        _emit(payload)
        return 0 if not errors else 2
    vault_root = None
    try:
        vault_root = _selection(args).root
    except VaultSelectionError as exc:
        implicit_absence = (
            args.vault is None
            and not os.environ.get("CLAUDE_OBSIDIAN_VAULT")
            and exc.code in {"VAULT_NOT_FOUND", "PLUGIN_ROOT_IS_NOT_VAULT"}
        )
        if not implicit_absence:
            raise
    report = evaluate_capabilities(
        PLUGIN_ROOT, vault_root=vault_root, verify=args.verify
    )
    if args.capability:
        selected = [
            item for item in report["capabilities"] if item["id"] == args.capability
        ]
        if not selected:
            report["errors"] = [
                *report["errors"],
                {
                    "code": "unknown_capability",
                    "location": "capabilities",
                    "message": f"unknown capability: {args.capability}",
                },
            ]
            report["ok"] = False
            report["valid"] = False
        report["capabilities"] = selected
    _emit(report)
    return 0 if report["ok"] else 1


def command_package_validate(args: argparse.Namespace) -> int:
    report = validate_package(PLUGIN_ROOT)
    _emit(report)
    return 0 if report["ok"] else 1


def _release_epoch(supplied: int | None) -> int:
    if supplied is not None:
        return supplied
    environment = os.environ.get("SOURCE_DATE_EPOCH")
    if environment is not None:
        try:
            return int(environment)
        except ValueError as exc:
            raise VaultOperationError("SOURCE_DATE_EPOCH must be an integer") from exc
    completed = subprocess.run(
        ["git", "-C", str(PLUGIN_ROOT), "show", "-s", "--format=%ct", "HEAD"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=10,
    )
    if completed.returncode != 0:
        raise VaultOperationError("cannot derive SOURCE_DATE_EPOCH from Git HEAD")
    try:
        return int(completed.stdout.strip())
    except ValueError as exc:
        raise VaultOperationError("Git HEAD has no valid commit timestamp") from exc


def command_release_build(args: argparse.Namespace) -> int:
    report = build_public_artifact(
        PLUGIN_ROOT,
        Path(args.output),
        _release_epoch(args.source_date_epoch),
    )
    _emit(report)
    return 0 if report["ok"] else 1


def command_release_audit(args: argparse.Namespace) -> int:
    report = audit_artifact(Path(args.artifact))
    _emit(report)
    return 0 if report["ok"] else 1


def command_release_gates(args: argparse.Namespace) -> int:
    report = evaluate_release_gates(
        PLUGIN_ROOT,
        execute=args.execute,
        selected=args.gate,
        timeout=args.timeout,
    )
    _emit(report)
    if not report["ok"]:
        return 1
    return 0 if not args.execute or report["ready"] else 1


def _capture_inputs(
    args: argparse.Namespace,
) -> tuple[Path, CaptureConfig, CaptureBudget, list[Path]]:
    root = _selection(args).root
    config = CaptureConfig.load(root, inbox=args.inbox)
    budget = CaptureBudget(
        max_items=args.max_items,
        max_total_bytes=args.max_total_bytes,
        max_file_bytes=args.max_file_bytes,
    )
    sources = [Path(value) for value in args.sources]
    if not sources:
        sources = discover_files(root, config=config, budget=budget)
    return root, config, budget, sources


def command_capture_adapters(args: argparse.Namespace) -> int:
    _emit(load_adapter_manifest())
    return 0


def command_capture_plan(args: argparse.Namespace) -> int:
    root, config, budget, sources = _capture_inputs(args)
    plans = plan_filesystem_batch(root, sources, config=config, budget=budget)
    _emit(
        {
            "schema": "claude-obsidian.capture-plan.v1",
            "status": "dry-run",
            "items": plans,
            "summary": {
                "items": len(plans),
                "would_change": sum(bool(item["would_change"]) for item in plans),
            },
        }
    )
    return 0


def command_capture_apply(args: argparse.Namespace) -> int:
    root, config, budget, sources = _capture_inputs(args)
    plans = plan_filesystem_batch(root, sources, config=config, budget=budget)
    timestamp = _timestamp_argument(args)
    writes = []
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
    operation = {
        "schema": "claude-obsidian.transaction.v1",
        "operation_id": _operation_id("capture", timestamp, args.operation_id),
        "operation_type": "capture",
        "expected_hashes": expected_hashes,
        "writes": writes,
        "address_requests": [],
        "source_manifest_updates": {},
    }
    if not args.apply:
        payload = {
            "schema": "claude-obsidian.capture-plan.v1",
            "status": "dry-run" if writes else "noop",
            "items": plans,
            "operation": operation,
        }
        if writes:
            payload.update(_approval_fields(root, operation, timestamp))
        _emit(payload)
        return 0
    if writes:
        approval = _require_approved_operation(args, root, operation)
        transaction_result = apply_bundle(
            root, operation, approved_plan_sha256=approval
        )
    else:
        transaction_result = None
    results = [
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
    _emit(
        {
            "schema": "claude-obsidian.capture-result.v1",
            "status": "applied",
            "items": results,
            "transaction": transaction_result,
            "summary": {
                "items": len(results),
                "changed": sum(bool(item["changed"]) for item in results),
            },
        }
    )
    return 0


def command_capture_external_plan(args: argparse.Namespace) -> int:
    _emit(
        plan_external_action(
            args.adapter,
            args.source,
            approved_hosts=args.approved_host,
        )
    )
    return 0


def _capture_queue(args: argparse.Namespace) -> CaptureQueue:
    return CaptureQueue(
        _selection(args).root,
        timeout=args.timeout,
        stale_after=args.lock_stale_after,
        force_stale_lock=bool(getattr(args, "force_stale_lock", False)),
    )


def command_capture_queue_list(args: argparse.Namespace) -> int:
    _emit(
        {
            "schema": "claude-obsidian.capture-queue-list.v1",
            "entries": _capture_queue(args).list(state=args.state),
        }
    )
    return 0


def command_capture_queue_enqueue(args: argparse.Namespace) -> int:
    action = None
    if args.adapter != "filesystem":
        action = plan_external_action(
            args.adapter,
            args.source,
            approved_hosts=args.approved_host,
        )
    entry = _capture_queue(args).enqueue(
        args.adapter,
        args.source,
        source_sha256=args.source_sha256,
        planned_action=action,
        idempotency_key=args.idempotency_key,
    )
    _emit(entry)
    return 0


def command_capture_queue_claim(args: argparse.Namespace) -> int:
    _emit(_capture_queue(args).claim(args.item_id, worker=args.worker))
    return 0


def _json_object_argument(value: str, label: str) -> dict[str, Any]:
    try:
        decoded = strict_json_loads(value)
    except (json.JSONDecodeError, ValueError) as exc:
        raise CaptureValidationError(
            "JSON_INVALID", f"{label} is not valid JSON: {exc}"
        ) from exc
    if not isinstance(decoded, dict):
        raise CaptureValidationError("JSON_INVALID", f"{label} must be a JSON object")
    return decoded


def command_capture_queue_complete(args: argparse.Namespace) -> int:
    result = _json_object_argument(args.result, "result")
    _emit(_capture_queue(args).complete(args.item_id, args.token, result))
    return 0


def command_capture_queue_fail(args: argparse.Namespace) -> int:
    _emit(
        _capture_queue(args).fail(
            args.item_id,
            args.token,
            args.error,
            retryable=not args.permanent,
        )
    )
    return 0


def command_capture_queue_resume(args: argparse.Namespace) -> int:
    entries = _capture_queue(args).resume(
        args.item_id,
        include_failed=not args.claimed_only,
        stale_after=args.stale_after,
        force=args.force,
    )
    _emit({"schema": "claude-obsidian.capture-queue-resume.v1", "entries": entries})
    return 0


def command_capture_queue_recover(args: argparse.Namespace) -> int:
    _emit(_capture_queue(args).recover())
    return 0


MODE_NAMES = ("generic", "lyt", "para", "zettelkasten")
ZETTEL_ID_FORMAT = "YYYYMMDDHHMMSSffffff-UUID4HEX"
DEFAULT_MODE_CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "mode": "generic",
    "configured_at": None,
    "config": {
        "lyt": {"moc_folder": "wiki/mocs/", "notes_folder": "wiki/notes/"},
        "para": {
            "projects_folder": "wiki/projects/",
            "areas_folder": "wiki/areas/",
            "resources_folder": "wiki/resources/",
            "archives_folder": "wiki/archives/",
        },
        "zettelkasten": {
            "id_format": ZETTEL_ID_FORMAT,
            "no_folders": True,
            "root_folder": "wiki/",
        },
        "generic": {
            "sources_folder": "wiki/sources/",
            "entities_folder": "wiki/entities/",
            "concepts_folder": "wiki/concepts/",
            "sessions_folder": "wiki/sessions/",
            "questions_folder": "wiki/questions/",
        },
    },
}


def _load_mode_document(root: Path) -> tuple[dict[str, Any], str | None]:
    raw = read_vault_regular(root, ".vault-meta/mode.json", limit=1024 * 1024)
    if raw is None:
        return json.loads(json.dumps(DEFAULT_MODE_CONFIG)), None
    try:
        value = strict_json_loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise VaultOperationError(f"cannot read existing mode config: {exc}") from exc
    digest = sha256_bytes(raw)
    if not isinstance(value, dict) or value.get("mode") not in MODE_NAMES:
        raise VaultOperationError(
            "existing mode config is invalid; repair it before changing mode"
        )
    merged = json.loads(json.dumps(DEFAULT_MODE_CONFIG))
    for key, item in value.items():
        if key != "config":
            merged[key] = item
    supplied_config = value.get("config", {})
    if not isinstance(supplied_config, dict):
        raise VaultOperationError("existing mode config has no configuration object")
    for mode_name, settings in supplied_config.items():
        if isinstance(settings, dict) and isinstance(
            merged["config"].get(mode_name), dict
        ):
            merged["config"][mode_name].update(settings)
        else:
            merged["config"][mode_name] = settings
    zettel = merged["config"].get("zettelkasten")
    if not isinstance(zettel, dict):
        raise VaultOperationError("existing Zettelkasten mode configuration is invalid")
    # Normalize the formerly descriptive legacy field to the one allocator
    # format the compatibility router actually implements. Reads stay
    # non-mutating; a reviewed mode-set transaction persists the upgrade.
    zettel["id_format"] = ZETTEL_ID_FORMAT
    try:
        validate_mode_folders(merged)
    except ValueError as exc:
        raise VaultOperationError(
            f"existing mode configuration is unsafe: {exc}"
        ) from exc
    return merged, digest


def command_mode_get(args: argparse.Namespace) -> int:
    root = _selection(args).root
    document, _ = _load_mode_document(root)
    _emit(document)
    return 0


def command_mode_set(args: argparse.Namespace) -> int:
    root = _selection(args).root
    document, expected = _load_mode_document(root)
    timestamp = _timestamp_argument(args)
    document["schema_version"] = 1
    document["mode"] = args.mode
    document["configured_at"] = timestamp
    content = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    operation = {
        "schema": "claude-obsidian.transaction.v1",
        "operation_id": _operation_id("mode", timestamp, args.operation_id),
        "operation_type": "configuration",
        "expected_hashes": {".vault-meta/mode.json": expected},
        "writes": [
            {
                "path": ".vault-meta/mode.json",
                "mode": "create" if expected is None else "replace",
                "content": content,
                "sha256": sha256_bytes(content.encode("utf-8")),
            }
        ],
        "address_requests": [],
        "source_manifest_updates": {},
    }
    plan = inspect_bundle(root, operation)
    if not args.apply:
        _emit(
            {
                "schema": "claude-obsidian.mode-plan.v1",
                "status": "dry-run",
                "mode": args.mode,
                "plan": plan,
                "operation": operation,
                **_approval_fields(root, operation, timestamp),
            }
        )
        return 0
    approval = _require_approved_operation(args, root, operation)
    _emit(apply_bundle(root, operation, approved_plan_sha256=approval))
    return 0


def command_extension_dragonscale(args: argparse.Namespace) -> int:
    root = _selection(args).root
    timestamp = _timestamp_argument(args)
    operation = dragonscale_bundle(
        root,
        operation_id=_operation_id("dragonscale", timestamp, args.operation_id),
        generated_at=timestamp,
    )
    if args.check:
        missing = [write["path"] for write in operation["writes"]]
        _emit(
            {
                "schema": "claude-obsidian.extension-check.v1",
                "extension": "dragonscale",
                "status": "ready" if not missing else "incomplete",
                "ready": not missing,
                "missing_paths": missing,
            }
        )
        return 0 if not missing else 1
    if not operation["writes"]:
        _emit(
            {
                "schema": "claude-obsidian.extension-plan.v1",
                "extension": "dragonscale",
                "status": "noop",
                "changed_paths": [],
            }
        )
        return 0
    plan = inspect_bundle(root, operation)
    if not args.apply:
        _emit(
            {
                "schema": "claude-obsidian.extension-plan.v1",
                "extension": "dragonscale",
                "status": "dry-run",
                "plan": plan,
                "operation": operation,
                **_approval_fields(root, operation, timestamp),
            }
        )
        return 0
    approval = _require_approved_operation(args, root, operation)
    _emit(apply_bundle(root, operation, approved_plan_sha256=approval))
    return 0


def _add_capture_budget_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--inbox")
    parser.add_argument("--max-items", type=int, default=100)
    parser.add_argument("--max-total-bytes", type=int, default=256 * 1024 * 1024)
    parser.add_argument("--max-file-bytes", type=int, default=64 * 1024 * 1024)


def _add_capture_queue_arguments(parser: argparse.ArgumentParser) -> None:
    _add_vault_argument(parser)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--lock-stale-after", type=float, default=3600.0)


def command_migrate(args: argparse.Namespace) -> int:
    selection = _selection(args)
    generated_at = args.generated_at or datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    operation_id = args.operation_id or (
        "migration-" + generated_at.replace(":", "").replace("-", "").replace("+", "")
    )
    operation = migration_bundle(
        selection.root,
        operation_id=operation_id,
        generated_at=generated_at,
    )
    if not operation["writes"]:
        _emit(
            {
                "schema": "claude-obsidian.migration-plan.v1",
                "status": "noop",
                "vault_layout": "v1",
                "changed_paths": [],
            }
        )
        return 0
    if not args.apply:
        _emit(
            {
                "schema": "claude-obsidian.migration-plan.v1",
                "status": "dry-run",
                "operation": operation,
                "changed_paths": [write["path"] for write in operation["writes"]],
                **_approval_fields(selection.root, operation, generated_at),
            }
        )
        return 0
    approval = _require_approved_operation(args, selection.root, operation)
    result = apply_bundle(selection.root, operation, approved_plan_sha256=approval)
    _emit(result)
    return 0


def _timestamp_argument(args: argparse.Namespace) -> str:
    return args.generated_at or datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")


def _operation_id(prefix: str, timestamp: str, supplied: str | None) -> str:
    return supplied or (
        prefix + "-" + timestamp.replace(":", "").replace("-", "").replace("+", "")
    )


def command_init(args: argparse.Namespace) -> int:
    destination = Path(args.path).expanduser().resolve(strict=False)
    assert_not_plugin_tree(destination, PLUGIN_ROOT)
    generated_at = _timestamp_argument(args)
    operation = build_vault_bundle(
        destination,
        operation_id=_operation_id("init", generated_at, args.operation_id),
        operation_type="setup",
        generated_at=generated_at,
        adopt=False,
        force=args.force,
    )
    scan = scan_vault(destination)
    if not operation["writes"]:
        _emit(
            {
                "schema": "claude-obsidian.initialization-plan.v1",
                "status": "noop",
                "scan": scan,
                "changed_paths": [],
            }
        )
        return 0
    if not args.apply:
        _emit(
            {
                "schema": "claude-obsidian.initialization-plan.v1",
                "status": "dry-run",
                "scan": scan,
                "changed_paths": [write["path"] for write in operation["writes"]],
                "operation": operation,
                **_approval_fields(destination, operation, generated_at),
            }
        )
        return 0
    # Refuse unsupported write platforms before creating the destination
    # directory: a failed Init root is never path-deleted (see below), so the
    # check must precede the mkdir rather than surface later in apply_bundle.
    _require_write_platform()
    reviewed_plan = _require_approved_plan(args, destination, operation)
    approval = str(reviewed_plan["approval_sha256"])
    created = False
    reviewed_identity = reviewed_plan["vault_identity"]
    reviewed_absent = reviewed_identity.get("state") == "absent"
    if reviewed_absent:
        if destination.exists():
            raise TransactionValidationError(
                "PLAN_CHANGED",
                "the reviewed absent initialization root now exists",
            )
        try:
            destination.mkdir(parents=False)
        except FileExistsError as exc:
            raise TransactionValidationError(
                "PLAN_CHANGED",
                "the reviewed absent initialization root appeared before creation",
            ) from exc
        created = True
    elif not destination.is_dir():
        raise TransactionValidationError(
            "PLAN_CHANGED", "the reviewed initialization vault no longer exists"
        )
    # Never path-delete a failed Init root: a concurrent namespace replacement
    # could make cleanup remove someone else's empty directory. The transaction
    # itself rolls back content; an empty created root may remain for inspection.
    if created:
        current_identity = inspect_bundle(destination, operation)["vault_identity"]
        result = apply_bundle(
            destination,
            operation,
            approved_plan_sha256=approval,
            reviewed_vault_identity=reviewed_identity,
            expected_current_vault_identity=current_identity,
        )
    else:
        result = apply_bundle(
            destination,
            operation,
            approved_plan_sha256=approval,
        )
    _emit(result)
    return 0


def command_adopt(args: argparse.Namespace) -> int:
    destination = Path(args.path).expanduser().resolve(strict=True)
    assert_not_plugin_tree(destination, PLUGIN_ROOT)
    if not destination.is_dir():
        raise VaultOperationError(f"not a directory: {destination}")
    generated_at = _timestamp_argument(args)
    operation = build_vault_bundle(
        destination,
        operation_id=_operation_id("adopt", generated_at, args.operation_id),
        operation_type="migration",
        generated_at=generated_at,
        adopt=True,
        force=args.force,
    )
    if not operation["writes"]:
        _emit(
            {
                "schema": "claude-obsidian.adoption-plan.v1",
                "status": "noop",
                "scan": scan_vault(destination),
                "changed_paths": [],
            }
        )
        return 0
    if not args.apply:
        _emit(
            {
                "schema": "claude-obsidian.adoption-plan.v1",
                "status": "dry-run",
                "scan": scan_vault(destination),
                "changed_paths": [write["path"] for write in operation["writes"]],
                "operation": operation,
                **_approval_fields(destination, operation, generated_at),
            }
        )
        return 0
    approval = _require_approved_operation(args, destination, operation)
    result = apply_bundle(destination, operation, approved_plan_sha256=approval)
    _emit(result)
    return 0


def command_checkpoint(args: argparse.Namespace) -> int:
    selection = _selection(args)
    result = checkpoint_operation(
        selection.root,
        args.operation_id,
        message=args.message,
        include_raw=args.include_raw,
        run_lint=not args.skip_lint,
        as_of=args.as_of,
    )
    _emit(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claude-obsidian")
    parser.add_argument("--version", action="version", version=__version__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    doctor = subcommands.add_parser(
        "doctor", help="Inspect vault selection and core readiness"
    )
    _add_vault_argument(doctor)
    doctor.set_defaults(handler=command_doctor)

    transaction = subcommands.add_parser(
        "transaction", help="Apply or recover vault transactions"
    )
    transaction_commands = transaction.add_subparsers(
        dest="transaction_command", required=True
    )
    apply_command = transaction_commands.add_parser(
        "apply", help="Apply a versioned transaction bundle"
    )
    _add_vault_argument(apply_command)
    apply_command.add_argument("bundle", type=Path)
    apply_command.add_argument("--timeout", type=float, default=10.0)
    apply_command.add_argument("--stale-after", type=float, default=3600.0)
    _add_approval_argument(apply_command)
    apply_command.set_defaults(handler=command_transaction_apply)

    recover = transaction_commands.add_parser(
        "recover", help="Roll back interrupted operations"
    )
    _add_vault_argument(recover)
    recover.add_argument("--timeout", type=float, default=10.0)
    recover.add_argument("--stale-after", type=float, default=3600.0)
    recover.add_argument(
        "--force-stale-lock",
        action="store_true",
        help=(
            "Reap an old lock even when its host/PID identity cannot be disproved; "
            "use only after confirming no writer is active"
        ),
    )
    recover.set_defaults(handler=command_transaction_recover)
    inspect = transaction_commands.add_parser(
        "inspect", help="Validate a bundle without writing"
    )
    _add_vault_argument(inspect)
    inspect.add_argument("bundle", type=Path)
    inspect.set_defaults(handler=command_transaction_inspect)

    hook = subcommands.add_parser("hook", help="Host lifecycle adapter")
    hook_commands = hook.add_subparsers(dest="hook_command", required=True)
    session_start = hook_commands.add_parser("session-start")
    session_start.set_defaults(handler=command_hook_session_start)
    stop = hook_commands.add_parser("stop")
    stop.set_defaults(handler=command_hook_stop)

    lint = subcommands.add_parser(
        "lint", help="Deterministically inspect an Obsidian vault"
    )
    _add_vault_argument(lint)
    lint.add_argument("--format", choices=("json", "markdown"), default="json")
    lint.add_argument("--as-of", help="ISO YYYY-MM-DD provenance freshness date")
    lint.add_argument(
        "--strict", action="store_true", help="Exit 1 when findings exist"
    )
    lint.set_defaults(handler=command_lint)

    contracts = subcommands.add_parser(
        "contracts", help="Validate capability and product contracts"
    )
    _add_vault_argument(contracts)
    contracts.add_argument("--verify", action="store_true")
    contracts.add_argument("--check-only", action="store_true")
    contracts.add_argument("--capability")
    contracts.set_defaults(handler=command_contracts)

    package = subcommands.add_parser(
        "package", help="Validate distributable package metadata"
    )
    package_commands = package.add_subparsers(dest="package_command", required=True)
    package_validate = package_commands.add_parser(
        "validate", help="Validate skills, hooks, and manifest coherence"
    )
    package_validate.set_defaults(handler=command_package_validate)

    release = subcommands.add_parser(
        "release",
        help="Build or audit a deterministic public artifact without publishing",
    )
    release_commands = release.add_subparsers(dest="release_command", required=True)
    release_build = release_commands.add_parser(
        "build", help="Build and self-audit a ZIP"
    )
    release_build.add_argument("--output", required=True)
    release_build.add_argument("--source-date-epoch", type=int)
    release_build.set_defaults(handler=command_release_build)
    release_audit = release_commands.add_parser(
        "audit", help="Audit a ZIP without extracting it"
    )
    release_audit.add_argument("artifact")
    release_audit.set_defaults(handler=command_release_audit)
    release_gates = release_commands.add_parser(
        "gates", help="Plan or execute declared release gates without publishing"
    )
    release_gates.add_argument("--execute", action="store_true")
    release_gates.add_argument("--gate", action="append", default=[])
    release_gates.add_argument("--timeout", type=int, default=300)
    release_gates.set_defaults(handler=command_release_gates)

    capture = subcommands.add_parser(
        "capture", help="Plan and run offline-first source capture"
    )
    capture_commands = capture.add_subparsers(dest="capture_command", required=True)
    capture_adapters = capture_commands.add_parser(
        "adapters", help="Show honest adapter maturity"
    )
    capture_adapters.set_defaults(handler=command_capture_adapters)
    capture_plan = capture_commands.add_parser(
        "plan", help="Preflight local capture without writes"
    )
    _add_vault_argument(capture_plan)
    _add_capture_budget_arguments(capture_plan)
    capture_plan.add_argument("sources", nargs="*")
    capture_plan.set_defaults(handler=command_capture_plan)
    capture_apply = capture_commands.add_parser(
        "apply", help="Copy local sources into immutable raw storage"
    )
    _add_vault_argument(capture_apply)
    _add_capture_budget_arguments(capture_apply)
    capture_apply.add_argument(
        "--apply", action="store_true", help="Perform copies; default is dry-run"
    )
    capture_apply.add_argument("--operation-id")
    capture_apply.add_argument("--generated-at")
    _add_approval_argument(capture_apply)
    capture_apply.add_argument("sources", nargs="*")
    capture_apply.set_defaults(handler=command_capture_apply)
    capture_external = capture_commands.add_parser(
        "external-plan", help="Create an inert, consent-gated external adapter plan"
    )
    capture_external.add_argument(
        "adapter", choices=("url", "image", "pdf", "youtube", "epub", "ocr")
    )
    capture_external.add_argument("source")
    capture_external.add_argument("--approved-host", action="append", default=[])
    capture_external.set_defaults(handler=command_capture_external_plan)

    capture_queue = capture_commands.add_parser(
        "queue", help="Operate the durable capture queue"
    )
    queue_commands = capture_queue.add_subparsers(dest="queue_command", required=True)
    queue_list = queue_commands.add_parser("list")
    _add_capture_queue_arguments(queue_list)
    queue_list.add_argument(
        "--state", choices=("queued", "claimed", "completed", "failed")
    )
    queue_list.set_defaults(handler=command_capture_queue_list)
    queue_enqueue = queue_commands.add_parser("enqueue")
    _add_capture_queue_arguments(queue_enqueue)
    queue_enqueue.add_argument(
        "adapter",
        choices=("filesystem", "url", "image", "pdf", "youtube", "epub", "ocr"),
    )
    queue_enqueue.add_argument("source")
    queue_enqueue.add_argument("--source-sha256")
    queue_enqueue.add_argument("--idempotency-key")
    queue_enqueue.add_argument("--approved-host", action="append", default=[])
    queue_enqueue.set_defaults(handler=command_capture_queue_enqueue)
    queue_claim = queue_commands.add_parser("claim")
    _add_capture_queue_arguments(queue_claim)
    queue_claim.add_argument("item_id", nargs="?")
    queue_claim.add_argument("--worker")
    queue_claim.set_defaults(handler=command_capture_queue_claim)
    queue_complete = queue_commands.add_parser("complete")
    _add_capture_queue_arguments(queue_complete)
    queue_complete.add_argument("item_id")
    queue_complete.add_argument("token")
    queue_complete.add_argument("result", help="JSON object")
    queue_complete.set_defaults(handler=command_capture_queue_complete)
    queue_fail = queue_commands.add_parser("fail")
    _add_capture_queue_arguments(queue_fail)
    queue_fail.add_argument("item_id")
    queue_fail.add_argument("token")
    queue_fail.add_argument("error")
    queue_fail.add_argument("--permanent", action="store_true")
    queue_fail.set_defaults(handler=command_capture_queue_fail)
    queue_resume = queue_commands.add_parser("resume")
    _add_capture_queue_arguments(queue_resume)
    queue_resume.add_argument("item_id", nargs="?")
    queue_resume.add_argument("--stale-after", type=float, default=3600.0)
    queue_resume.add_argument("--claimed-only", action="store_true")
    queue_resume.add_argument("--force", action="store_true")
    queue_resume.set_defaults(handler=command_capture_queue_resume)
    queue_recover = queue_commands.add_parser("recover")
    _add_capture_queue_arguments(queue_recover)
    queue_recover.add_argument(
        "--force-stale-lock",
        action="store_true",
        help=(
            "Reap an old queue lock even when its host/PID identity cannot be disproved; "
            "use only after confirming no queue worker is active"
        ),
    )
    queue_recover.set_defaults(handler=command_capture_queue_recover)

    mode = subcommands.add_parser(
        "mode", help="Read or transactionally configure vault methodology"
    )
    mode_commands = mode.add_subparsers(dest="mode_command", required=True)
    mode_get = mode_commands.add_parser("get")
    _add_vault_argument(mode_get)
    mode_get.set_defaults(handler=command_mode_get)
    mode_set = mode_commands.add_parser("set")
    _add_vault_argument(mode_set)
    mode_set.add_argument("mode", choices=MODE_NAMES)
    mode_set.add_argument(
        "--apply", action="store_true", help="Apply; default is dry-run"
    )
    mode_set.add_argument("--operation-id")
    mode_set.add_argument("--generated-at")
    _add_approval_argument(mode_set)
    mode_set.set_defaults(handler=command_mode_set)

    extension = subcommands.add_parser(
        "extension", help="Plan optional vault extensions"
    )
    extension_commands = extension.add_subparsers(
        dest="extension_command", required=True
    )
    dragonscale = extension_commands.add_parser(
        "dragonscale", help="Create missing DragonScale compatibility state"
    )
    _add_vault_argument(dragonscale)
    dragonscale.add_argument(
        "--check", action="store_true", help="Report whether all extension state exists"
    )
    dragonscale.add_argument(
        "--apply", action="store_true", help="Apply; default is dry-run"
    )
    dragonscale.add_argument("--operation-id")
    dragonscale.add_argument("--generated-at")
    _add_approval_argument(dragonscale)
    dragonscale.set_defaults(handler=command_extension_dragonscale)

    migrate = subcommands.add_parser(
        "migrate", help="Plan or apply a backward-compatible vault migration"
    )
    _add_vault_argument(migrate)
    migrate.add_argument(
        "--apply", action="store_true", help="Apply the plan; default is dry-run"
    )
    migrate.add_argument("--operation-id")
    migrate.add_argument(
        "--generated-at", help="Pinned ISO timestamp for reproducible migrations"
    )
    _add_approval_argument(migrate)
    migrate.set_defaults(handler=command_migrate)

    init = subcommands.add_parser(
        "init", help="Plan or initialize a separate user vault"
    )
    init.add_argument("path")
    init.add_argument(
        "--apply", action="store_true", help="Apply the plan; default is dry-run"
    )
    init.add_argument(
        "--force",
        action="store_true",
        help="Replace conflicting generated files transactionally",
    )
    init.add_argument("--operation-id")
    init.add_argument("--generated-at")
    _add_approval_argument(init)
    init.set_defaults(handler=command_init)

    adopt = subcommands.add_parser(
        "adopt", help="Plan or adopt an existing Obsidian vault"
    )
    adopt.add_argument("path")
    adopt.add_argument(
        "--apply", action="store_true", help="Apply the plan; default is dry-run"
    )
    adopt.add_argument(
        "--force",
        action="store_true",
        help="Replace conflicting generated files transactionally",
    )
    adopt.add_argument("--operation-id")
    adopt.add_argument("--generated-at")
    _add_approval_argument(adopt)
    adopt.set_defaults(handler=command_adopt)

    checkpoint = subcommands.add_parser(
        "checkpoint", help="Explicitly commit one completed vault operation"
    )
    _add_vault_argument(checkpoint)
    checkpoint.add_argument("operation_id")
    checkpoint.add_argument("--message")
    checkpoint.add_argument("--include-raw", action="store_true")
    checkpoint.add_argument("--skip-lint", action="store_true")
    checkpoint.add_argument(
        "--as-of", help="Pin provenance freshness audit date (YYYY-MM-DD)"
    )
    checkpoint.set_defaults(handler=command_checkpoint)
    return parser


def _force_utf8_stdio() -> None:
    """Emit UTF-8 regardless of the console code page.

    On Windows, redirected stdout/stderr default to the locale encoding
    (cp1252), so any non-ASCII page title crashes ``_emit``'s
    ``ensure_ascii=False`` output.  ``newline=""`` keeps JSON output
    byte-identical across platforms.
    """

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", newline="")
        except (OSError, ValueError):
            pass


def main(argv: Sequence[str] | None = None) -> int:
    _force_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except VaultSelectionError as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        return 2
    except TransactionError as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        return exc.exit_code
    except CaptureConflict as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        return 75
    except CaptureValidationError as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        return 2
    except CaptureError as exc:
        print(f"ERR {exc.code}: {exc}", file=sys.stderr)
        return 1
    except VaultOperationError as exc:
        print(f"ERR VAULT_OPERATION: {exc}", file=sys.stderr)
        return 2
    except LedgerValidationError as exc:
        print(f"ERR INVALID_PROVENANCE_LEDGER: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERR OS: {exc}", file=sys.stderr)
        return 2
