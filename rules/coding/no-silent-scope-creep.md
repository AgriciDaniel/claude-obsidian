---
id: coding/no-silent-scope-creep
domain: coding
title: Do the task asked, surface the rest
severity: high
applies_when: >
  You are inside a task and you notice something else worth fixing: a bug nearby, a bad name, a missing test, a dependency to upgrade, a refactor that would make your change cleaner.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Finish the task you were given. Report the adjacent thing you found. Do not fix it uninvited.

**Why.** An agent that quietly reformats a file, renames a variable "for clarity," or bumps a dependency while fixing a typo produces a diff its reviewer cannot read. The one line that mattered is buried in ninety lines that did not, so the review degrades to a rubber stamp and the real defect walks straight through. Worse, the unrequested change is the one that breaks production, and now the bisect points at a commit whose message says "fix typo." Scope creep does not just cost review time, it destroys the diff as an instrument of trust.

**How to apply.**

1. Keep the diff to the change that was asked for. Nothing you did not need to touch appears in it.
2. Do not reformat, reorder imports, or restyle code you happened to open. If a formatter runs, run it as its own commit.
3. When the requested change genuinely requires a refactor first, do the refactor as a separate, behavior-preserving commit, and say so.
4. Collect what you noticed and hand it back in your final report: file, line, what is wrong, what you would do. Let the human choose.
5. The exception is a live security hole or data-loss bug. Say it immediately and prominently instead of quietly patching it.
