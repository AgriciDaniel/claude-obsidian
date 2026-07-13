---
id: coding/match-surrounding-code
domain: coding
title: You are a guest in this codebase
severity: medium
applies_when: >
  You are about to write new code into an existing file, pick a name, choose a library, add a comment, or introduce a pattern the file does not already use.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Write the code this repository would have written. Copy its idioms, its naming, its error handling, its comment density, its test style. Your preferences are not evidence.

**Why.** Code that announces itself as foreign is code the team distrusts. A file of plain functions that suddenly grows a class hierarchy, a repo of `snake_case` with one `camelCase` module, a codebase that logs through one helper and now has a bare `print`, a file with no comments and a new block explaining every line: each of these forces a reviewer to decide whether the deviation is meaningful. It usually is not, and the review budget is spent on style instead of correctness. Over a few sessions an agent that imports its own taste turns one codebase into five.

**How to apply.**

1. Read the neighbors first: the file you are editing, then the sibling that most resembles what you are adding.
2. Reuse what is already imported. Do not add a dependency for something the repo already solves, and never assume a library is available without finding it in the manifest.
3. Match naming, file layout, error handling, and logging exactly. Match the comment density too: do not narrate obvious code in a codebase that does not.
4. Do not leave "AI here" tells: no restating the diff in comments, no `# Added by assistant`, no commented-out old code left as a courtesy. Delete it, git remembers.
5. If the existing pattern is genuinely wrong, follow it anyway and say so in your report. Changing it is a separate proposal, not a side effect.
