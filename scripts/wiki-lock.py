#!/usr/bin/env python3
"""wiki-lock.py — per-file advisory locking for safe multi-writer vault mutation.

Cross-platform port of the flock-based wiki-lock.sh internals (flock is absent
from Git Bash / MSYS2 on Windows). Same meta-lock technique as
allocate-address.py: msvcrt.locking on win32, fcntl.flock elsewhere.

Design (age-based, not flock-style):
  flock(2) advisory locks release when the holding process exits. That
  doesn't fit our model where `acquire` and `release` are SEPARATE
  invocations from the same skill (each Bash tool call is its own short-
  lived process — neither's PID survives long enough to mean anything).
  So we use atomic O_CREAT|O_EXCL lockfile creation plus epoch-timestamp
  AGE-based staleness detection.

  The PID written into the lockfile is informational only (helpful for
  `list` and debugging). The acquire decision considers AGE only:
    - If lockfile age <= STALE_AFTER_SEC → refuse (return 75 EX_TEMPFAIL)
    - If lockfile age >  STALE_AFTER_SEC → reap and acquire
  Default STALE_AFTER_SEC=60.

Semantics:
  acquire <vault-rel-path>
    - Computes lock_file = .vault-meta/locks/<sha1(path)>.lock
    - Atomically creates the lockfile with this process's PID + epoch
    - Returns 0 if acquired, 75 (EX_TEMPFAIL) if held and age < threshold
    - Auto-reaps locks older than STALE_AFTER_SEC
  release <vault-rel-path>
    - Removes the lockfile unconditionally. Idempotent.
    - Cross-process release IS allowed by design — acquire and release
      are typically separate invocations from the same skill, and
      PID-matching would never succeed.
  list
    - Prints currently-held lock records (one per line: pid age path).
  clear-stale [--max-age N]
    - Removes lockfiles whose PID is dead OR whose age > N seconds.
      Default N = 3600 (1h). Prints count removed.
  peek <vault-rel-path>
    - Prints holder info or "unheld"; exit 0; never mutates.

Age-threshold naming (v1.7.2; closes audit L6):
  - STALE_AFTER_SEC (default 60, --stale-after-sec N) is the PER-ACQUIRE
    threshold. Tuned for "single skill operation completes within 60s."
  - `clear-stale --max-age N` (default 3600) is the ADMIN reaper threshold.
  These are two distinct concerns; do not unify the defaults.

Usage:
  wiki-lock.py acquire wiki/concepts/Foo.md
  wiki-lock.py release wiki/concepts/Foo.md
  wiki-lock.py list
  wiki-lock.py clear-stale --max-age 1800
  wiki-lock.py peek wiki/concepts/Foo.md

Exit codes:
  0  — success
  1  — meta-lock acquisition failed (the wiki-lock.sh wrapper also exits 1
       when neither uv nor python3 is on PATH)
  2  — usage error
  75 — acquire failed (lock held and not stale)
  3  — vault-meta/locks dir creation failed
  4  — invalid vault-relative path (escape attempt)
"""

import hashlib
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    import ctypes
    import msvcrt

    def _lock_ex(fd):
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)

    def _lock_un(fd):
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

    def pid_alive(pid):
        # NEVER use os.kill(pid, 0) here: on Windows any signal other than
        # CTRL_C_EVENT/CTRL_BREAK_EVENT is routed to TerminateProcess, which
        # would KILL the probed process instead of probing it.
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        ERROR_ACCESS_DENIED = 5
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            # Access denied means the process exists but is inaccessible
            # (other user / elevated) — treat as alive, mirroring the POSIX
            # branch's PermissionError handling.
            return ctypes.get_last_error() == ERROR_ACCESS_DENIED
        try:
            code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(h, ctypes.byref(code)):
                return False
            return code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(h)
else:
    import fcntl

    def _lock_ex(fd):
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _lock_un(fd):
        fcntl.flock(fd, fcntl.LOCK_UN)

    def pid_alive(pid):
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True


EXIT_OK = 0
EXIT_META_LOCK = 1
EXIT_USAGE = 2
EXIT_LOCK_DIR = 3
EXIT_BAD_PATH = 4
EXIT_HELD = 75


def log(msg):
    print(msg, file=sys.stderr)


def die(msg, code=EXIT_USAGE):
    log(f"ERR: {msg}")
    sys.exit(code)


def resolve_vault_root() -> Path:
    # WIKI_LOCK_VAULT (tests / non-default roots) wins over CO_VAULT_ROOT,
    # matching the bash original where it was applied last.
    env = os.environ.get("WIKI_LOCK_VAULT") or os.environ.get("CO_VAULT_ROOT")
    if env:
        return Path(env)
    cwd = Path.cwd()
    if (cwd / ".vault-meta").is_dir() or (cwd / "wiki").is_dir():
        return cwd
    return Path(__file__).resolve().parent.parent


VAULT_ROOT = resolve_vault_root()
META_DIR = VAULT_ROOT / ".vault-meta"
LOCK_DIR = META_DIR / "locks"
META_LOCK = META_DIR / ".wiki-lock.meta"
STALE_AFTER_SEC = 60


def sha1_of(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def ensure_dirs():
    try:
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        die(f"cannot create {LOCK_DIR}", EXIT_LOCK_DIR)


def validate_path(p: str):
    # Reject empty, absolute, escape, or newline-bearing paths to prevent
    # lock-namespace pollution (audit M4: newlines would break the lockfile
    # line format). Symlink escapes outside VAULT_ROOT are path traversal
    # (audit M3).
    if not p:
        die("path cannot be empty", EXIT_BAD_PATH)
    if p.startswith("/") or (len(p) > 1 and p[1] == ":"):
        die(f"path must be vault-relative, not absolute: {p}", EXIT_BAD_PATH)
    if ".." in p:
        die(f"path may not contain '..': {p}", EXIT_BAD_PATH)
    if "\n" in p:
        die(
            "path may not contain newlines (lockfile format would break)", EXIT_BAD_PATH
        )
    if "\r" in p:
        die("path may not contain carriage returns", EXIT_BAD_PATH)
    root = os.path.realpath(VAULT_ROOT)
    target = os.path.realpath(os.path.join(root, p))
    try:
        inside = os.path.commonpath([root, target]) == root
    except ValueError:
        inside = False
    if not inside:
        die(f"path resolves outside vault via symlink: {p}", EXIT_BAD_PATH)


def lockfile_for(path: str) -> Path:
    return LOCK_DIR / f"{sha1_of(path)}.lock"


def read_lockfile(lf: Path) -> str:
    try:
        with open(lf, "r", encoding="utf-8") as f:
            return f.readline().rstrip("\n")
    except OSError:
        return ""


def try_create(lf: Path, path: str) -> bool:
    # O_CREAT|O_EXCL is the atomic equivalent of bash's noclobber write.
    try:
        fd = os.open(str(lf), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except OSError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(f"{os.getpid()} {int(time.time())} {path}\n")
    return True


def acquire_meta_lock(timeout=5.0):
    # Serializes acquire/release/clear-stale against each other, matching the
    # original `flock -x -w 5` semantics via poll-and-retry (both lock
    # backends here are non-blocking only).
    ensure_dirs()
    fd = os.open(str(META_LOCK), os.O_CREAT | os.O_WRONLY, 0o644)
    deadline = time.monotonic() + timeout
    while True:
        try:
            _lock_ex(fd)
            return fd
        except OSError:
            if time.monotonic() >= deadline:
                os.close(fd)
                die("could not acquire meta-lock within 5s", EXIT_META_LOCK)
            time.sleep(0.05)


def release_meta_lock(fd):
    try:
        _lock_un(fd)
    finally:
        os.close(fd)


# ── commands ─────────────────────────────────────────────────────────────────
def cmd_acquire(path: str) -> int:
    validate_path(path)
    lf = lockfile_for(path)

    if try_create(lf, path):
        return EXIT_OK

    existing = read_lockfile(lf)
    if not existing:
        # Empty/unreadable; treat as stale, clean and retry once
        lf.unlink(missing_ok=True)
        return EXIT_OK if try_create(lf, path) else EXIT_HELD

    fields = existing.split()
    epoch = fields[1] if len(fields) > 1 else ""
    if not epoch.isdigit():
        # Corrupt lockfile → treat as stale
        lf.unlink(missing_ok=True)
        return EXIT_OK if try_create(lf, path) else EXIT_HELD

    age = int(time.time()) - int(epoch)
    if age > STALE_AFTER_SEC:
        # Age exceeds threshold → reap and re-acquire (regardless of holder PID)
        lf.unlink(missing_ok=True)
        return EXIT_OK if try_create(lf, path) else EXIT_HELD

    # Held and not yet stale by age — refuse
    return EXIT_HELD


def cmd_release(path: str) -> int:
    validate_path(path)
    # Unconditional remove — cross-process release is allowed by design.
    lockfile_for(path).unlink(missing_ok=True)
    return EXIT_OK


def iter_lockfiles():
    for lf in sorted(LOCK_DIR.glob("*.lock")):
        if lf.is_file():
            yield lf


def cmd_list() -> int:
    now = int(time.time())
    for lf in iter_lockfiles():
        rec = read_lockfile(lf)
        if not rec:
            continue
        fields = rec.split(" ", 2)
        pid = fields[0] if len(fields) > 0 else ""
        epoch = fields[1] if len(fields) > 1 else "0"
        path = fields[2] if len(fields) > 2 else ""
        age = now - int(epoch) if epoch.isdigit() else 0
        print(f"pid={pid} age={age}s path={path}")
    return EXIT_OK


def cmd_clear_stale(max_age: int) -> int:
    removed = 0
    now = int(time.time())
    for lf in iter_lockfiles():
        rec = read_lockfile(lf)
        if not rec:
            lf.unlink(missing_ok=True)
            removed += 1
            continue
        fields = rec.split()
        pid = fields[0] if len(fields) > 0 else ""
        epoch = fields[1] if len(fields) > 1 else "0"
        age = now - int(epoch) if epoch.isdigit() else max_age + 1
        dead = not (pid.isdigit() and pid_alive(int(pid)))
        if dead or age > max_age:
            lf.unlink(missing_ok=True)
            removed += 1
    print(removed)
    return EXIT_OK


def cmd_peek(path: str) -> int:
    validate_path(path)
    lf = lockfile_for(path)
    if not lf.is_file():
        print("unheld")
        return EXIT_OK
    print(read_lockfile(lf))
    return EXIT_OK


def usage():
    print(__doc__.strip())


# ── arg parsing (flags accepted in any position) ─────────────────────────────
def main():
    global STALE_AFTER_SEC

    argv = sys.argv[1:]
    if not argv:
        usage()
        return EXIT_USAGE

    cmd = None
    args = []
    max_age_override = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--stale-after-sec":
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                die("--stale-after-sec needs a numeric value")
            STALE_AFTER_SEC = int(argv[i + 1])
            i += 2
        elif a == "--max-age":
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                die("--max-age needs a numeric value")
            max_age_override = int(argv[i + 1])
            i += 2
        elif a in ("-h", "--help"):
            usage()
            return EXIT_OK
        elif a == "--":
            args.extend(argv[i + 1 :])
            break
        elif a.startswith("-"):
            die(f"unknown flag: {a}")
        else:
            if cmd is None:
                cmd = a
            else:
                args.append(a)
            i += 1

    if cmd is None:
        die("no command given")

    if cmd == "acquire":
        if not args:
            die("acquire needs a path")
        rc = with_meta_lock(cmd_acquire, args[0])
    elif cmd == "release":
        if not args:
            die("release needs a path")
        rc = with_meta_lock(cmd_release, args[0])
    elif cmd == "list":
        rc = with_meta_lock(cmd_list)
    elif cmd == "clear-stale":
        if max_age_override is not None:
            max_age = max_age_override
        elif args:
            if not args[0].isdigit():
                die(f"clear-stale max-age must be numeric: {args[0]}")
            max_age = int(args[0])
        else:
            max_age = 3600
        rc = with_meta_lock(cmd_clear_stale, max_age)
    elif cmd == "peek":
        if not args:
            die("peek needs a path")
        rc = with_meta_lock(cmd_peek, args[0])
    else:
        die(f"unknown command: {cmd} (try acquire|release|list|clear-stale|peek)")
    return rc


def with_meta_lock(fn, *fn_args):
    fd = acquire_meta_lock()
    try:
        return fn(*fn_args)
    finally:
        release_meta_lock(fd)


if __name__ == "__main__":
    sys.exit(main())
