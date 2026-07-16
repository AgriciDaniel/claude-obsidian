#!/usr/bin/env python3
"""allocate-address.py — atomic creation-order address allocation for the vault.

Cross-platform port of allocate-address.sh (which required `flock`, absent
from Git Bash / MSYS2 on Windows). Same lock-file technique as bm25_index.py:
msvcrt.locking on win32, fcntl.flock elsewhere.

Reserves the next address of the form c-NNNNNN and increments the counter
under an exclusive lock. On missing counter file, recovers by scanning the
vault for the highest existing c-NNNNNN in page frontmatter and resuming from
max+1. Never silently resets to 1 in a non-empty vault.

Usage:
  ./scripts/allocate-address.py           # prints the reserved address (e.g. c-000042) to stdout
  ./scripts/allocate-address.py --peek    # prints the next value without incrementing
  ./scripts/allocate-address.py --rebuild # recomputes counter from max observed and exits

Exit codes:
  0 — success
  1 — lock acquisition failed (another writer is holding the lock)
  2 — vault-meta directory missing and cannot be created
  3 — counter value corrupt or non-numeric
"""

import os
import re
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    import msvcrt

    def _lock_ex(fd):
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)

    def _lock_un(fd):
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _lock_ex(fd): fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    def _lock_un(fd): fcntl.flock(fd, fcntl.LOCK_UN)

EXIT_OK = 0
EXIT_LOCK = 1
EXIT_META_DIR = 2
EXIT_CORRUPT = 3

ADDR_RE = re.compile(r"^address:\s+(c-[0-9]{6})\s*$")


def log(msg):
    print(msg, file=sys.stderr)


def resolve_vault_root() -> Path:
    env = os.environ.get("CO_VAULT_ROOT")
    if env:
        return Path(env).resolve()
    cwd = Path.cwd()
    if (cwd / ".vault-meta").is_dir() or (cwd / "wiki").is_dir():
        return cwd.resolve()
    return Path(__file__).resolve().parent.parent


VAULT_ROOT = resolve_vault_root()
COUNTER_FILE = VAULT_ROOT / ".vault-meta" / "address-counter.txt"
LOCK_FILE = VAULT_ROOT / ".vault-meta" / ".address.lock"
WIKI_DIR = VAULT_ROOT / "wiki"


def scan_max_c_address() -> int:
    """Largest NNNNNN from "address: c-NNNNNN" lines inside the FIRST YAML
    frontmatter block of each wiki .md file. Code-block examples and body
    prose are excluded. Returns 0 if none found."""
    if not WIKI_DIR.is_dir():
        return 0
    best = 0
    for path in WIKI_DIR.rglob("*.md"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        if not lines or lines[0] != "---":
            continue
        for line in lines[1:]:
            if line == "---":
                break
            m = ADDR_RE.match(line)
            if m:
                best = max(best, int(m.group(1)[2:]))
    return best


def acquire_lock(timeout=5.0):
    """Exclusive lock, retried for up to `timeout` seconds (matches the
    original `flock -x -w 5` semantics; both lock backends here are
    non-blocking only, so waiting is done via poll-and-retry)."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_WRONLY, 0o644)
    deadline = time.monotonic() + timeout
    while True:
        try:
            _lock_ex(fd)
            return fd
        except OSError:
            if time.monotonic() >= deadline:
                os.close(fd)
                log("ERR: could not acquire address allocator lock within 5s")
                sys.exit(EXIT_LOCK)
            time.sleep(0.05)


def release_lock(fd):
    try:
        _lock_un(fd)
    finally:
        os.close(fd)


def read_or_recover_counter() -> int:
    if not COUNTER_FILE.is_file():
        max_c = scan_max_c_address()
        COUNTER_FILE.write_text(f"{max_c + 1}\n", encoding="utf-8")
        log(f"INFO: counter file missing; recovered from vault scan, set to {max_c + 1}")
    raw = COUNTER_FILE.read_text(encoding="utf-8").strip()
    if not raw.isdigit():
        log(f"ERR: counter file content is not a positive integer: {raw}")
        sys.exit(EXIT_CORRUPT)
    return int(raw)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "allocate"

    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        log("ERR: cannot create .vault-meta/")
        sys.exit(EXIT_META_DIR)

    fd = acquire_lock()
    try:
        if mode == "--peek":
            print(read_or_recover_counter())
        elif mode == "--rebuild":
            max_c = scan_max_c_address()
            COUNTER_FILE.write_text(f"{max_c + 1}\n", encoding="utf-8")
            print(f"Counter rebuilt: next = {max_c + 1}")
        elif mode in ("allocate", ""):
            current = read_or_recover_counter()
            COUNTER_FILE.write_text(f"{current + 1}\n", encoding="utf-8")
            print(f"c-{current:06d}")
        else:
            log(f"ERR: unknown mode: {mode}")
            log(f"Usage: {sys.argv[0]} [allocate|--peek|--rebuild]")
            sys.exit(EXIT_CORRUPT)
    finally:
        release_lock(fd)

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
