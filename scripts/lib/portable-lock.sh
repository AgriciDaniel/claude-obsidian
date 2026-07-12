#!/usr/bin/env bash
# portable-lock.sh — exclusive advisory lock that works on macOS and Linux.
#
# WHY THIS EXISTS
#   `flock(1)` is a util-linux binary. It does not ship on macOS/BSD. Shell
#   scripts that called it directly failed with "flock: command not found" on
#   every Mac, which took 3 of 9 `make test` targets red on the maintainer's own
#   platform.
#
# CONTRACT
#   portable_lock_acquire <lockpath> [timeout_sec]
#     Blocks until the lock is held or timeout elapses.
#     Returns 0 when held, 1 on timeout, 2 if no locking backend is available.
#     The lock is released by the KERNEL when the calling shell or subshell
#     exits. There is no release function and nothing to clean up.
#     `allocate-address.sh` calls this at top level; `wiki-lock.sh` calls it
#     inside a subshell. Both are correct — see the fd-9 note below.
#
# HOW IT WORKS (both paths are the same lock, just reached differently)
#   The shell opens the lockfile on fd 9. Then flock(2) is taken on fd 9, either
#   by flock(1) where it exists, or by python3's fcntl.flock where it does not.
#
#   The python path works because flock(2) locks the *open file description*, not
#   the process. python3 inherits fd 9, locks it, and exits — but the shell still
#   holds fd 9 referring to the same description, so the lock persists. The kernel
#   drops it when the last fd on that description closes, i.e. when the shell
#   exits. This is precisely what flock(1) does; we are just reaching the same
#   syscall through an interpreter that macOS actually ships.
#
#   Consequences worth stating, because a previous hand-rolled mkdir-based
#   implementation got all three wrong:
#     - No stale locks. The kernel releases on process death, including SIGKILL.
#     - No reaping, no PID tracking, no owner tokens, no EXIT trap.
#     - No steal semantics, so no risk of one holder deleting another's lock.
#
#   One inherited-behavior caveat, identical to flock(1): a forked child inherits
#   fd 9 and therefore keeps the lock alive even if the holding shell dies. Short-
#   lived children in the critical section are fine; do not background a long-
#   running process while holding the lock and expect the lock to drop with its
#   parent.
#
#   Do not "optimize" this back into a mkdir/lockfile spin. Pure-shell mutual
#   exclusion on macOS is deceptively hard: bash 3.2 (what macOS ships) has no
#   BASHPID, so a subshell cannot even identify itself, and every reaping scheme
#   built on top of that leaks a way for two holders to enter at once. This was
#   demonstrated, not assumed — see tests/test_portable_lock.sh.

# PORTABLE_LOCK_FORCE_BACKEND=flock|python3 pins the backend instead of probing.
# This exists for CI: Linux runners always have flock(1), so without a way to force
# it, the python3 path — the entire reason this file exists, and the one that took
# three attempts to get right — would never be exercised by any automated check.
# Not for production use.
PORTABLE_LOCK_FORCE_BACKEND="${PORTABLE_LOCK_FORCE_BACKEND:-}"

# Acquire an exclusive lock. See CONTRACT above.
portable_lock_acquire() {
  local lockpath="$1"
  local timeout="${2:-5}"

  # Guard against fd 9 already being in use. Two locks in one shell scope would
  # silently drop the first when fd 9 is reopened — a silent lock loss, which is
  # exactly the failure class this file has already shipped twice. Fail loudly.
  if { true >&9; } 2>/dev/null; then
    echo "ERR: fd 9 is already in use — portable_lock_acquire does not nest." >&2
    echo "     Hold at most one portable lock per shell or subshell scope." >&2
    return 2
  fi

  # fd 9 is the lock handle. It must stay open for as long as the lock is held,
  # which is why this is `exec` and not a scoped redirect.
  exec 9>"$lockpath" || return 1

  local backend="$PORTABLE_LOCK_FORCE_BACKEND"
  if [ -z "$backend" ]; then
    if command -v flock >/dev/null 2>&1; then
      backend=flock
    else
      backend=python3
    fi
  fi

  # Report the backend actually taken. Without this a caller (notably the CI step
  # that forces python3) cannot tell which path really ran, and a forced-backend
  # check that silently falls back to flock is worse than no check at all.
  PORTABLE_LOCK_LAST_BACKEND="$backend"

  if [ "$backend" = flock ]; then
    command -v flock >/dev/null 2>&1 || {
      echo "ERR: backend 'flock' forced but flock(1) is not installed." >&2
      return 2
    }
    flock -x -w "$timeout" 9 || return 1
    return 0
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    echo "ERR: no locking backend: neither flock(1) nor python3 is available." >&2
    echo "     Install one, or run on a host that has them." >&2
    return 2
  fi

  # Lock the INHERITED fd 9 (see HOW IT WORKS). Poll rather than block so the
  # timeout is honored; fcntl.flock has no timed variant.
  #
  # Narrow known window: if python3 is killed between flock() succeeding and
  # sys.exit(0), we return 1 while the lock IS actually held on fd 9. That is a
  # false negative, never a false positive, so it cannot admit two holders — the
  # caller treats it as failure and exits, closing fd 9 and releasing the lock.
  python3 - "$timeout" <<'PY' || return 1
import fcntl, sys, time

timeout = float(sys.argv[1])
deadline = time.monotonic() + timeout

while True:
    try:
        fcntl.flock(9, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sys.exit(0)
    except BlockingIOError:
        if time.monotonic() >= deadline:
            sys.exit(1)
        time.sleep(0.02)
    except OSError as e:
        print(f"ERR: flock on fd 9 failed: {e}", file=sys.stderr)
        sys.exit(1)
PY

  return 0
}
