---
id: coding/no-hand-rolled-locks
domain: coding
title: Do not hand-roll a mutex
severity: high
applies_when: >
  You are about to write a lock, a mutex, a semaphore, a single-instance guard, or a "check the file exists, then create it" sequence, in shell or anywhere else.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Use a primitive the kernel or the runtime already gives you an atomic guarantee for. Never compose a lock out of a test and a separate write.

**Why.** `if [ ! -e "$LOCK" ]; then touch "$LOCK"; fi` is not a lock. Two processes pass the test before either does the write, and both proceed. The window is microseconds wide, so it passes every test you run and fails in production under load, intermittently, with corrupted state and no reproduction. The same trap appears as check-then-create on a file, read-modify-write on a counter, and "is the port free" before binding it. Hand-rolled locks also leak: the holder is killed, the stale lock file survives, and every later run hangs forever with no way out.

**How to apply.**

1. Use an operation that is atomic by construction: `mkdir` (fails if it exists), `open` with `O_EXCL`, `ln`, a database unique constraint, `flock` where it is available, a real mutex from the language runtime.
2. Store the holder's identity (pid, host, start time) in the lock so a stale lock is detectable rather than eternal.
3. Give every lock a stale-after timeout and a documented recovery path. A deadlock with no escape is worse than the race.
4. Release in a handler that runs on every exit path, including signals, not just the happy one.
5. Then prove it: run the contending processes concurrently, in a loop, and check the invariant. A concurrency fix you did not run under contention is not a fix. See `coding/verify-by-execution`.
