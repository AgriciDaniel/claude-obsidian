---
description: Watch a code repo for commits and keep its Mode B wiki in sync. Installs a git hook that enqueues changed paths; choose in-session (default) or autonomous headless drain.
---

Read the `wiki-code-ingest` skill (for `--sync` behavior), then set up commit-triggered sync.

Usage:
- `/wiki-code-watch <repo-path>` — install the git hooks (in-session sync, the safe default).
- `/wiki-code-watch <repo-path> --autonomous` — opt into detached headless `claude -p` sync on commit (needs `ANTHROPIC_API_KEY`; debounced + single-flight; degrades to enqueue-only when the key is absent).
- `/wiki-code-watch --status` — show watched repos and last-synced commits.
- `/wiki-code-watch <repo-path> --unwatch` — remove the installed git hooks.

Run the installer:

```bash
bash bin/setup-code-watch.sh <repo-path> [--autonomous] [--status] [--unwatch]
```

What it does:
- Refuses to watch a repo whose path is the vault's own git repo (prevents a commit→sync→commit loop).
- Installs `post-commit` / `post-merge` / `post-rewrite` hooks into `<repo>/.git/hooks/` (chaining any existing hook). On each commit they cheaply append the changed paths + new HEAD to the vault's `.vault-meta/code-sync-queue.jsonl` — no LLM, never blocking the commit.
- Records the watch in `.vault-meta/code-sync-state.json`.

Drain:
- **in-session (default):** the plugin's `SessionStart` hook runs `scripts/code-sync-check.py`, which surfaces "N modules drifted since last sync — run `/wiki-code-ingest --sync`". You then sync in-session. Surfaced paths are sanitized (control chars stripped) before they enter session context.
- **autonomous (opt-in):** the git hook also calls `bin/code-sync-launch.sh`, which debounces and launches a detached headless sync.

> **Trust boundary (autonomous mode):** the headless run reads commit-derived data (changed paths, commit messages) and the repo's files, and acts on them with an LLM. The launch prompt instructs the agent to treat that data as untrusted and to stay within the repo + vault, but you should only enable `--autonomous` for repositories you trust. In-session mode keeps a human in the loop and is the safe default.

Tell the user which drain mode is active and how to switch.
