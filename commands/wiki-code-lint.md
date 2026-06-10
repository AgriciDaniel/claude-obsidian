---
description: Code-fidelity lint for a Mode B code wiki — checks drift, ingest staleness, coverage gaps, and Obsidian link resolution against the repo it was ingested from. Read-only; writes a dated report.
---

Read the `wiki-code-lint` skill. Then run the code-fidelity lint.

Usage:
- `/wiki-code-lint` — lint the current vault against `$CODE_REPO_ROOT` (the repo it was ingested from).
- `/wiki-code-lint <repo-path>` — lint against an explicit repo path.

If no vault is set up yet, say: "No wiki vault found. Run /wiki first to set one up."

This is the `wiki-code-*` counterpart to `/wiki-lint` (generic vault hygiene) — run both; they do not overlap.
It is read-only: it writes only `wiki/meta/code-lint-report-YYYY-MM-DD.md`. The fixes it points at are
`/wiki-code-ingest --sync` (drift / staleness), `/wiki-code-ingest <repo> <path>` (a coverage gap), or a safe
`aliases:` backfill (link resolution) — offered only after the report is shown and approved.

After linting, show the tiered summary (BLOCKER / HIGH / MEDIUM / LOW) and the report path, and name the single
next command that fixes the most findings.
