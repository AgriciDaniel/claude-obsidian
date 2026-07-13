---
id: coding/smallest-diff-that-solves-it
domain: coding
title: Prefer deleting to adding
severity: medium
applies_when: >
  You are about to add a file, a class, an abstraction layer, a config flag, a compatibility shim, or a helper, in order to solve the problem in front of you.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Solve it with the fewest lines that fully solve it. Before you add, look for the thing to remove. New code is the expensive answer, and it is the one an agent reaches for first.

**Why.** Agents add. Asked to fix a path bug, an agent will write a `PathResolver` class rather than change one string. Asked to handle a new case, it adds a flag rather than deleting the branch that made the case special. Each addition is permanent: it must be read, tested, kept working on every platform, and understood by everyone who comes after. Two code paths where one would do is not flexibility, it is a permanent obligation to keep both correct, and the one nobody exercises is where the next bug lives.

**How to apply.**

1. Grep for the abstraction before you write it. It usually exists, one directory over, under a name you did not guess.
2. Ask whether the fix is a deletion: an unreachable branch, a flag with one live value, a shim for a version nobody runs, a special case that stops being special if you change the caller.
3. Do not add a config option to avoid a decision. An option is a decision you have delegated to every future user, forever.
4. When you replace an old path, delete the old path in the same change. A migration that leaves both alive has not migrated anything.
5. Do not introduce an abstraction on its first use. Wait for the second, or the third. A wrong abstraction costs more than the duplication it prevented.
