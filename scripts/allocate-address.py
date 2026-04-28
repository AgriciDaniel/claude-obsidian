#!/usr/bin/env python
"""allocate-address.py — atomic creation-order address allocation for the vault.

Reserves the next address of the form c-NNNNNN and increments the counter
under an exclusive file lock. On missing counter file, recovers by scanning
the vault for the highest existing c-NNNNNN in page frontmatter and resuming
from max+1. Never silently resets to 1 in a non-empty vault.

Cross-platform: uses fcntl on Unix, msvcrt on Windows (via _lock.py).

Usage:
  python scripts/allocate-address.py           # prints reserved address (e.g. c-000042)
  python scripts/allocate-address.py --peek    # prints next value without incrementing
  python scripts/allocate-address.py --rebuild # recomputes counter from max observed

Exit codes:
  0 — success
  1 — lock acquisition failed
  2 — vault-meta directory missing and cannot be created
  3 — counter value corrupt or non-numeric
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
COUNTER_FILE = VAULT_ROOT / ".vault-meta" / "address-counter.txt"
LOCK_FILE = VAULT_ROOT / ".vault-meta" / ".address.lock"
WIKI_DIR = VAULT_ROOT / "wiki"

# Match "address: c-NNNNNN" only inside the first YAML frontmatter block.
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
ADDRESS_RE = re.compile(r"^address:\s+(c-[0-9]{6})\s*$", re.MULTILINE)

# Import the cross-platform lock from the same scripts/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lock import file_lock


def scan_max_c_address() -> int:
    """Return the largest NNNNNN from address: c-NNNNNN in frontmatter, or 0."""
    if not WIKI_DIR.is_dir():
        return 0
    max_n = 0
    for md in WIKI_DIR.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = FRONTMATTER_RE.match(text)
        if not m:
            continue
        fm_block = m.group(1)
        for am in ADDRESS_RE.finditer(fm_block):
            n = int(am.group(1)[2:])  # strip "c-" prefix
            if n > max_n:
                max_n = n
    return max_n


def read_or_recover_counter() -> int:
    """Read counter from file, or recover from vault scan if missing."""
    if not COUNTER_FILE.exists():
        max_c = scan_max_c_address()
        COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        COUNTER_FILE.write_text(str(max_c + 1), encoding="utf-8")
        print(f"INFO: counter file missing; recovered from vault scan, set to {max_c + 1}",
              file=sys.stderr)
    raw = COUNTER_FILE.read_text(encoding="utf-8").strip()
    if not raw.isdigit():
        print(f"ERR: counter file content is not a positive integer: {raw}",
              file=sys.stderr)
        sys.exit(3)
    return int(raw)


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(prog="allocate-address")
    p.add_argument("--peek", action="store_true", help="print next value without incrementing")
    p.add_argument("--rebuild", action="store_true", help="recompute counter from max observed")
    args = p.parse_args()
    if args.peek:
        mode = "--peek"
    elif args.rebuild:
        mode = "--rebuild"
    else:
        mode = "allocate"

    try:
        COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"ERR: cannot create .vault-meta/: {e}", file=sys.stderr)
        return 2

    try:
        with file_lock(LOCK_FILE, timeout=5.0):
            if mode == "--peek":
                val = read_or_recover_counter()
                print(val)
            elif mode == "--rebuild":
                max_c = scan_max_c_address()
                COUNTER_FILE.write_text(str(max_c + 1), encoding="utf-8")
                print(f"Counter rebuilt: next = {max_c + 1}")
            else:
                current = read_or_recover_counter()
                COUNTER_FILE.write_text(str(current + 1), encoding="utf-8")
                print(f"c-{current:06d}")
    except TimeoutError:
        print("ERR: could not acquire address allocator lock within 5s",
              file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
