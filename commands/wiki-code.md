---
description: The /wiki for codebases. Code-wiki status dashboard, Mode B architecture mapping, drift checks, and routing to the code sub-skills (ingest, sync, watch, lint).
---

Read the `wiki-code` skill. Then route based on what the user wants.

Usage:
- `/wiki-code` — code-wiki **status dashboard** (vault, code pages, watched repos, pending drift) + next-step offers. Read-only.
- `/wiki-code <repo-path>` — set up (if needed) and **map** a repository as a Mode B architecture wiki.
- `/wiki-code-ingest <repo> [subpath]` — ingest a whole repo or a single module.
- `/wiki-code-ingest --sync` — drain `.vault-meta/code-sync-queue.jsonl` and re-ingest only changed paths.
- `/wiki-code-lint` — code-fidelity health check (drift, staleness, coverage, link resolution).
- `/wiki-code-watch <repo>` — set up commit-triggered auto-sync.

If no vault exists, scaffold a minimal Mode B vault first (`bash bin/setup-vault.sh`), then hand off to `wiki-code-ingest` — honoring its scope + module-list checkpoints before mass-creating pages.

`/wiki-code` dispatches to the engines; it never re-implements ingest, signal-gathering, or page synthesis. It coexists with `/wiki` (which keeps its natural-language code routing) as the explicit, status-aware code entry point.
