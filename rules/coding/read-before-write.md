---
id: coding/read-before-write
domain: coding
title: Read the file before you write it, and trust code over docs
severity: blocker
applies_when: >
  You are about to edit, patch, or overwrite a file you have not read in this session, or you are about to state how the system works on the authority of a README, a comment, or a doc.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "Distilled from recurring agent failure modes in production coding sessions"
---

Read the target file, in full or at least the region you are touching, before you modify it. When a document and the code disagree, the code is the truth and the document is a bug.

**Why.** A blind edit silently destroys work: it clobbers the handler someone added last week, re-introduces a bug that was already fixed, or duplicates a helper that exists forty lines above. And a fact taken from a README ages badly. The doc describes the flag that was renamed, the script that was deleted, the default that changed two releases ago. An agent that builds a plan on stale prose builds a plan that cannot run, then burns the session discovering that one call at a time.

**How to apply.**

1. Never call `Write` on an existing path you have not read. Prefer a targeted edit over a full overwrite: an overwrite discards everything you did not know was there.
2. Read enough context to see the local conventions, the imports already available, and whether the thing you are about to add already exists.
3. Before you rely on any claim from a README, a CHANGELOG, a docstring, or a code comment, verify it against the source: does that file still exist, does that flag still parse, does that function still take those arguments?
4. When docs and code disagree, follow the code, then fix the doc in the same change. A doc you knew was wrong and left in place is a trap you set for the next reader.
