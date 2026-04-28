"""Cross-platform exclusive file locking.

Uses fcntl.flock on Unix and msvcrt.locking on Windows.
Import and use as a context manager:

    from _lock import file_lock

    with file_lock(Path(".vault-meta/.my.lock")):
        # exclusive section
"""

from __future__ import annotations

import contextlib
import os
import sys
import time
from pathlib import Path
from typing import Generator

_IS_WINDOWS = sys.platform == "win32"


@contextlib.contextmanager
def file_lock(lock_path: Path, timeout: float = 5.0) -> Generator[None, None, None]:
    """Acquire an exclusive lock on *lock_path*, blocking up to *timeout* seconds.

    Creates the lock file and parent directories if they don't exist.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        if _IS_WINDOWS:
            import msvcrt
            deadline = time.monotonic() + timeout
            while True:
                try:
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(
                            f"could not acquire lock {lock_path} within {timeout}s"
                        )
                    time.sleep(0.05)
            try:
                yield
            finally:
                try:
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)
