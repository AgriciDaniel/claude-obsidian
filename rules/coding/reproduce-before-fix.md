---
id: coding/reproduce-before-fix
domain: coding
title: Reproduce before you fix
severity: high
applies_when: >
  You have just been handed a bug, a stack trace, a flaky test, or a "this does not work," and your next action would be to edit source code.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Do not touch the source until you have a command that fails. Make it fail on demand, then make it pass, then confirm your change is what flipped it.

**Why.** Without a reproduction you are not fixing the bug, you are editing code near it. The usual result is a change that looks correct, ships, and leaves the report open, because the real fault was in the caller, the config, or the environment. The second result is worse: the symptom disappears for an unrelated reason (a cache cleared, a race lost differently) and you attribute the fix to your patch, so the same bug returns with your misleading commit message attached to it.

**How to apply.**

1. Reproduce first. A failing test is best, a failing command is fine, a logged failing input is the floor.
2. Confirm the reproduction fails for the reason you think. Read the actual error, not the one you expected.
3. Write the fix. Rerun the reproduction. It must go from red to green.
4. Revert your fix and confirm it goes back to red. That is the step that proves causation, and it is the step everyone skips.
5. Leave the reproduction behind as a regression test. A bug fixed without a test is a bug scheduled to return.
6. If you truly cannot reproduce it, say so and stop. Ship instrumentation, not a guess dressed as a fix.
