#!/usr/bin/env python
"""test_allocate_address.py — smoke tests for scripts/allocate-address.py.

Runs in a throwaway temp vault so it never touches the real
.vault-meta/address-counter.txt. Exits non-zero on any failure.

Usage: python tests/test_allocate_address.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR.parent
ALLOC_SCRIPT = VAULT_ROOT / "scripts" / "allocate-address.py"
LOCK_MODULE = VAULT_ROOT / "scripts" / "_lock.py"

PASS = 0
FAIL = 0


def log_pass(label: str, detail: str = "") -> None:
    global PASS
    suffix = f" (got {detail})" if detail else ""
    print(f"OK   {label}{suffix}")
    PASS += 1


def log_fail(label: str, detail: str = "") -> None:
    global FAIL
    print(f"FAIL {label} {detail}")
    FAIL += 1


def assert_eq(label: str, expected: str, actual: str) -> None:
    if expected == actual:
        log_pass(label, actual)
    else:
        log_fail(label, f": expected '{expected}', got '{actual}'")


def run(tmp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run allocate-address.py in the temp vault directory."""
    return subprocess.run(
        [sys.executable, str(tmp / "scripts" / "allocate-address.py"), *args],
        capture_output=True,
        text=True,
        cwd=str(tmp),
    )


def main() -> int:
    global PASS, FAIL

    tmp = Path(tempfile.mkdtemp(prefix="ds-test-"))
    try:
        # Set up minimal vault structure
        (tmp / "scripts").mkdir()
        (tmp / "wiki").mkdir()
        shutil.copy2(str(ALLOC_SCRIPT), str(tmp / "scripts" / "allocate-address.py"))
        shutil.copy2(str(LOCK_MODULE), str(tmp / "scripts" / "_lock.py"))

        # --- Test 1: rebuild on empty vault = 1 ---
        r = run(tmp, "--rebuild")
        assert_eq("rebuild on empty vault", "Counter rebuilt: next = 1", r.stdout.strip())
        counter_val = (tmp / ".vault-meta" / "address-counter.txt").read_text().strip()
        assert_eq("counter file value", "1", counter_val)

        # --- Test 2: peek does not increment ---
        r1 = run(tmp, "--peek")
        r2 = run(tmp, "--peek")
        assert_eq("peek idempotent", r1.stdout.strip(), r2.stdout.strip())

        # --- Test 3: first alloc returns c-000001 and increments ---
        r = run(tmp)
        assert_eq("first alloc", "c-000001", r.stdout.strip())
        counter_val = (tmp / ".vault-meta" / "address-counter.txt").read_text().strip()
        assert_eq("counter after 1 alloc", "2", counter_val)

        # --- Test 4: monotonic sequence ---
        r2 = run(tmp)
        r3 = run(tmp)
        assert_eq("second alloc", "c-000002", r2.stdout.strip())
        assert_eq("third alloc", "c-000003", r3.stdout.strip())

        # --- Test 5: corrupt counter -> exit 3 ---
        (tmp / ".vault-meta" / "address-counter.txt").write_text("not-a-number")
        r = run(tmp)
        assert_eq("corrupt counter exit", "3", str(r.returncode))
        # Recover for subsequent tests
        run(tmp, "--rebuild")

        # --- Test 6: missing counter recovers from max observed address ---
        (tmp / ".vault-meta" / "address-counter.txt").unlink(missing_ok=True)
        (tmp / "wiki" / "fake.md").write_text(
            "---\ntype: concept\naddress: c-000500\n---\n"
        )
        r = run(tmp, "--peek")
        assert_eq("recovery from max observed", "501", r.stdout.strip())

        # --- Test 7: frontmatter-only scan ignores code-block examples ---
        (tmp / "wiki" / "fake.md").unlink()
        (tmp / ".vault-meta" / "address-counter.txt").write_text("1")
        (tmp / "wiki" / "doc.md").write_text(
            "---\ntype: concept\n---\n"
            "# Doc with a code-block example\n"
            "```yaml\naddress: c-999999\n```\n"
        )
        r = run(tmp, "--rebuild")
        assert_eq(
            "code-block ignored, rebuild to 1",
            "Counter rebuilt: next = 1",
            r.stdout.strip(),
        )

        # --- Summary ---
        print()
        print(f"Passed: {PASS}")
        print(f"Failed: {FAIL}")
        return 0 if FAIL == 0 else 1

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
