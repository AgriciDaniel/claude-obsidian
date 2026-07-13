---
id: coding/verify-by-execution
domain: coding
title: Verify by execution, never by inspection
severity: blocker
applies_when: >
  You are about to say a change is done, fixed, working, or ready, and the strongest evidence you hold is that you read the code, reviewed the diff, or watched a tool report success.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Run it. Do not reason about it. Reading a diff is not evidence that the diff works.

**Why.** This is the single most expensive agent failure. An agent writes a plausible patch, re-reads it, finds it plausible, and reports "fixed." The human trusts the report, closes the loop, and discovers the breakage an hour or a week later, with the context gone. The cost is not the bug, it is the destroyed trust in every future "done." A tool returning exit 0 is also not evidence: `Edit` succeeding means bytes were written, not that behavior changed.

**How to apply.**

1. Before you claim any outcome, name the command that proves it. If you cannot name one, you do not have the outcome, you have a hypothesis. Say "hypothesis."
2. Execute that command and read its actual output. Not the exit code alone: the output.
3. Prove the negative too. Confirm the failure existed before your change, so a passing run after it means something.
4. Exercise the real entry point (the CLI, the endpoint, the UI action), not only the unit you touched. See `coding/green-gate-is-not-the-feature`.
5. When you genuinely cannot execute (no runtime, no credentials, destructive side effects), say so explicitly and state exactly what remains unverified. Never let an unverified change wear the word "working."
