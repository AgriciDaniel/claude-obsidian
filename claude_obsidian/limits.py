"""Shared byte envelopes without importing the mutation engine."""

from __future__ import annotations

MAX_TRANSACTION_RUNTIME_JSON_BYTES = 8 * 1024 * 1024
MAX_CANONICAL_LEDGER_BYTES = 16 * 1024 * 1024
CANONICAL_LEDGER_PATHS = (
    "wiki/meta/ledgers/source-ledger.json",
    "wiki/meta/ledgers/claim-ledger.json",
)


def ledger_capacity_message(relative: str, size: int | str) -> str:
    return (
        f"{relative} has {size} bytes; canonical ledger capacity is "
        f"{MAX_CANONICAL_LEDGER_BYTES} bytes. Preserve the original bytes and "
        "prepare a reviewed capacity compaction or migration. Existing "
        "transaction backups remain recoverable within their original bounds."
    )
