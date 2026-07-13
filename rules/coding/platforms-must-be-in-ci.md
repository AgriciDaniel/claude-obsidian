---
id: coding/platforms-must-be-in-ci
domain: coding
title: A platform you do not test is a platform you do not support
severity: high
applies_when: >
  You are about to add a platform, runtime, or version to a support matrix, README, or `engines` field, or you are about to reach for `flock`, `timeout`, `realpath`, `readlink -f`, a bash associative array, or a GNU-only flag of `sed`, `date`, `grep`, `wc`, or `stat`.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Support is a CI job, not a sentence in a README. If macOS, Windows, or an old runtime is not in the matrix, do not claim it, and do not assume your code runs there.

**Why.** A green Linux-only pipeline is structurally incapable of seeing a macOS bug, and the gaps sit exactly in the utilities an agent reaches for first. BSD `sed` needs an argument to `-i` where GNU does not. BSD `date` cannot parse `-d`. `readlink -f` and `realpath` are absent from a stock macOS. `flock` does not exist there. Bash 3.2 ships as `/bin/bash` on macOS and has no associative arrays. Each of these is a script that works perfectly in CI and dies on the first user's laptop, and the failure lands on them, not on you.

**How to apply.**

1. Before writing shell, assume the target is POSIX `sh` on BSD userland unless CI proves otherwise. Prefer portable constructs over clever ones.
2. When you must use a non-portable tool, feature-detect it and provide a real path for its absence. Do not silently degrade.
3. To add a platform to the support matrix, add the CI job in the same change. No job, no claim.
4. When CI cannot cover a target (a paid runner, an unavailable OS), write the limitation into the README explicitly: "untested on X." An honest gap beats a false promise.
