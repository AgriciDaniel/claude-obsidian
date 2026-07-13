---
id: coding/green-gate-is-not-the-feature
domain: coding
title: A green gate can be fully satisfied by an invisible feature
severity: high
applies_when: >
  You are about to call a feature done because the tests passed, CI went green, the typecheck cleared, or the build succeeded.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Passing the gate proves the gate passed. It does not prove the user can reach the feature. Trace the path from the user's first keystroke to your new code, and confirm every hop exists.

**Why.** The classic shape: the function is written, the unit test imports it directly and passes, CI is green, the agent reports the feature shipped. But the flag was never registered with the parser, the route was never added to the router, the command was never exported, the button was never rendered. Every gate is satisfied and the feature is unreachable. Tests written by the same agent in the same session are especially prone to this, because they test the code that was written rather than the behavior that was requested.

**How to apply.**

1. Name the user's entry point out loud: which command, endpoint, menu item, or import gives them this.
2. Follow the wiring from that entry point to your code. Registration, export, route table, plugin manifest, dependency injection, feature flag default. Each hop is a place the feature can silently fail to exist.
3. Invoke it the way a user would, from a clean process. Not the test harness.
4. Ask what would still pass if your feature were deleted. If the answer is "everything," your tests test nothing.
5. Check discoverability as part of done: help text, docs, and defaults. A feature nobody can find has not shipped.
