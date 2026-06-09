# claude-obsidian Hooks

Plugin hooks for the claude-obsidian wiki vault. All hooks are defined in `hooks.json`.

## Events

| Event | Type | Purpose |
|---|---|---|
| `SessionStart` | command + prompt | Loads `wiki/hot.md` into context. Command type runs `[ -f wiki/hot.md ] && cat wiki/hot.md` as the canonical safety check (works for non-vault sessions without erroring). A second command runs `scripts/code-sync-check.py` **only if** `.vault-meta/code-sync-queue.jsonl` exists, surfacing a `[code-sync]` drift summary when a watched code repo has new commits. Prompt type complements with semantic context restoration and offers `/wiki-code-ingest --sync` when drift is present. Matcher: `startup\|resume`. |
| `PostCompact` | prompt | Re-loads `wiki/hot.md` after context compaction. Hook-injected context does NOT survive compaction (only `CLAUDE.md` does), so this hook restores the hot cache mid-session. |
| `PostToolUse` | command | Auto-commits any wiki/ or .raw/ changes after Write or Edit tool calls. Guarded by `[ -d .git ]` so it never errors in non-git directories, and by `git diff --cached --quiet` so it never creates empty commits. |
| `Stop` | prompt | Updates `wiki/hot.md` at the end of every Claude response with a brief summary of what changed. |

## Known Issue: Plugin Hooks STDOUT Bug

`anthropics/claude-code#10875` documents that **plugin hook STDOUT may not be captured** by Claude Code, while identical inline hooks in `settings.json` work correctly.

**Impact**: If this bug is active in your Claude Code version, the prompt-type SessionStart and PostCompact hooks may not inject context as expected.

**Workaround**: The command-type SessionStart hook (`cat wiki/hot.md`) is the canonical safety check. It relies on STDOUT capture for context injection, so test against this issue if hot cache restoration fails. As a fallback, copy the hook config from `hooks.json` into your user-level `~/.claude/settings.json` instead of relying on plugin hooks.

**Test for the bug**: After installing the plugin, open a fresh Claude Code session in a directory containing a populated `wiki/hot.md`. Ask Claude "what's in the hot cache?". If Claude has no idea, the STDOUT bug is active in your version.

## Non-Vault Sessions

The SessionStart command hook uses `[ -f wiki/hot.md ] && cat wiki/hot.md || true` so it always exits 0, even when no vault is present. This makes the plugin safe to install globally without breaking non-vault Claude Code sessions.

## Code-Watch (Mode B auto-sync)

There are **two** hook systems involved in keeping a Mode B codebase wiki in sync, and they are different things:

- **Claude Code plugin hooks** (this `hooks.json`) ship with the plugin and fire on Claude lifecycle events. The `SessionStart` `code-sync-check.py` command above is the **in-session drain trigger**: it reads `.vault-meta/code-sync-queue.jsonl` and surfaces pending drift so you can run `/wiki-code-ingest --sync`.
- **Git hooks** (installed by `bin/setup-code-watch.sh` into a *watched code repo's* `.git/hooks/`) are the **detector**. Plugins are declarative and cannot install git hooks at install time and don't know which repo you'll map — so you run `/wiki-code-watch <repo>` once per repo. The git hook is enqueue-only: on each `post-commit` / `post-merge` / `post-rewrite` it appends the changed paths + new HEAD to the vault's queue. It never blocks the commit and runs no LLM.

Drain modes (per repo, stored in `.vault-meta/code-sync-state.json`):

- **in-session** (default): the SessionStart hook surfaces drift; you sync in-session.
- **autonomous** (opt-in, `--autonomous`): the git hook also kicks `bin/code-sync-launch.sh`, which debounces, single-flights, and launches a detached headless `claude -p` sync. Requires `ANTHROPIC_API_KEY` in the commit environment; without it, the commit still enqueues and you drain in-session.

Loop safety: `setup-code-watch.sh` refuses to watch the vault's own git repo, and the git hook only ever writes to the vault's queue — so the existing `PostToolUse` vault auto-commit cannot re-trigger the code repo's hooks.
