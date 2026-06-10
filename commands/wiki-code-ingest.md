---
description: Ingest a code repository (or sub-path) into the wiki as a Mode B architecture map. Gathers deterministic signals, then synthesizes module/flow/dependency/decision pages with drift anchors.
---

Read the `wiki-code-ingest` skill. Then ingest the code.

Usage:
- `/wiki-code-ingest <repo-path>` — map a whole repository.
- `/wiki-code-ingest <repo-path> <subpath>` — map a single module/package (e.g. `app/workers/crawler`).
- `/wiki-code-ingest --sync` — drain `.vault-meta/code-sync-queue.jsonl` and re-ingest only the changed paths.

If no vault is set up yet, say: "No wiki vault found. Run /wiki first to set one up."

Always honor the gitignore guarantee — the signal scripts already exclude ignored files; never index them.

For a large repo with many modules, run the signal scripts once and fan out the `wiki-code-ingest` sub-agent (one per module). Confirm scope and the proposed module list with the user before mass-creating pages.

After ingest, update wiki/index.md, wiki/log.md, and wiki/hot.md, and report how many pages were created/updated and the key architectural insight.
