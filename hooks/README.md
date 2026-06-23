# claude-obsidian Hooks

Plugin hooks for the claude-obsidian wiki vault. All hooks are defined in `hooks.json`.

## Events

| Event | Type | Purpose |
|---|---|---|
| `SessionStart` | command | Loads `wiki/hot.md` into context via `[ -f wiki/hot.md ] && cat wiki/hot.md` (the canonical safety check; works for non-vault sessions without erroring). Matcher: `startup\|resume`. Note: `SessionStart` runs before any conversation exists, so prompt-type hooks are not valid for this event — see below. |
| `PostCompact` | command | Re-loads `wiki/hot.md` after context compaction via `[ -f wiki/hot.md ] && cat wiki/hot.md`. Hook-injected context does NOT survive compaction (only `CLAUDE.md` does), so this hook restores the hot cache mid-session. Must be a command hook — see below. |
| `PostToolUse` | command | Auto-commits any wiki/ or .raw/ changes after Write or Edit tool calls. Guarded by `[ -d .git ]` so it never errors in non-git directories, and by `git diff --cached --quiet` so it never creates empty commits. |
| `Stop` | prompt | Updates `wiki/hot.md` at the end of every Claude response with a brief summary of what changed. |

## Why `SessionStart` and `PostCompact` use command hooks, not prompt hooks

Neither lifecycle event supports prompt-type hooks in current Claude Code, but they fail in two *different* ways:

- **`SessionStart`** is dispatched by the in-REPL hook runner, which requires a conversation context (`toolUseContext`) for prompt hooks. `SessionStart` fires before any conversation exists, so the runner throws — a visible error banner on **every** startup/resume:

  ```
  SessionStart:startup hook error
  Failed to run: prompt-type hooks are not supported for SessionStart events
  (no conversation context is available). Use a command-type hook instead.
  ```

- **`PostCompact`** is dispatched by `executeHooksOutsideREPL`, which supports only `command`/`callback`/`mcp_tool` hooks. A prompt hook there returns `succeeded: false` ("Prompt … hooks are not yet supported outside REPL") and the result is silently dropped — **no error, but no effect either**. The previous prompt-type `PostCompact` hook never actually restored the hot cache.

The fix for both is the same: use the `command` hook `[ -f wiki/hot.md ] && cat wiki/hot.md`, whose STDOUT is injected into context. For `SessionStart` this was already covered by an existing command hook (the prompt entry was redundant and is removed); for `PostCompact` the prompt entry is **converted** to the command form so post-compaction restoration works for the first time.

## Known Issue: Plugin Hooks STDOUT Bug

`anthropics/claude-code#10875` documents that **plugin hook STDOUT may not be captured** by Claude Code, while identical inline hooks in `settings.json` work correctly.

**Impact**: If this bug is active in your Claude Code version, the SessionStart and PostCompact command hooks (which restore the hot cache via STDOUT) may not inject context as expected.

**Workaround**: The command-type SessionStart hook (`cat wiki/hot.md`) is the canonical safety check. It relies on STDOUT capture for context injection, so test against this issue if hot cache restoration fails. As a fallback, copy the hook config from `hooks.json` into your user-level `~/.claude/settings.json` instead of relying on plugin hooks.

**Test for the bug**: After installing the plugin, open a fresh Claude Code session in a directory containing a populated `wiki/hot.md`. Ask Claude "what's in the hot cache?". If Claude has no idea, the STDOUT bug is active in your version.

## Non-Vault Sessions

The SessionStart command hook uses `[ -f wiki/hot.md ] && cat wiki/hot.md || true` so it always exits 0, even when no vault is present. This makes the plugin safe to install globally without breaking non-vault Claude Code sessions.
