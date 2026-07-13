---
id: coding/no-invented-causes
domain: coding
title: A fallback must never name a cause it did not verify
severity: blocker
applies_when: >
  You are about to write a `catch`, an `except`, a `rescue`, an `|| true`, a default branch, or any error message, log line, or comment that explains WHY something failed.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Report only what you observed. If the handler did not inspect the error, it does not get to say what caused it.

**Why.** `catch { print("network unavailable") }` is a lie whenever the real cause was a typo in the URL, an expired token, a JSON parse failure, or a permissions error. The lie is worse than silence, because it sends the next debugger (human or agent) to inspect the network for an hour while the real fault sits untouched. The same rot lives in comments ("we retry here because the API is flaky") and in fallbacks that swallow the signal: `|| true` converts a real failure into a green run, and the failure resurfaces later, further from its cause.

**How to apply.**

1. In every handler, either inspect the error and branch on what it actually is, or report the raw error verbatim. Never paraphrase it into a guess.
2. Write messages that say what happened and where, not why: "failed to write `<path>`: `<errno>`" beats "disk is full."
3. Do not use `|| true`, a bare `except:`, or an empty catch to make a step pass. If a failure is genuinely tolerable, say which specific failure is tolerable and let every other one through.
4. Preserve the original error when you wrap it. Chain it, do not replace it.
5. Apply the same rule to yourself. When you report to the user, distinguish what you observed from what you infer, and label the inference.
