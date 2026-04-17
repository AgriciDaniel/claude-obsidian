# claude-obsidian Hooks

Plugin hooks for the claude-obsidian wiki vault. All hooks are defined in `hooks.json`.

## Events

| Event | Type | Purpose |
|---|---|---|
| `SessionStart` | command | Injects `wiki/hot.md` into the model context by emitting the documented `hookSpecificOutput.additionalContext` JSON schema. Resolves the vault path via `${CLAUDE_PROJECT_DIR:-$PWD}/wiki/hot.md`, exits silently when the file is absent (non-vault sessions) or `jq` is not installed. Matcher: `startup\|resume`. |
| `PostToolUse` | command | Auto-commits any `wiki/` or `.raw/` changes after Write or Edit tool calls. Guarded by `[ -d .git ]` so it never errors in non-git directories, and by `git diff --cached --quiet` so it never creates empty commits. |
| `Stop` | command | Emits a `WIKI_CHANGED:` nudge when files under `wiki/` have changed this session, prompting Claude to refresh `wiki/hot.md`. Guarded by `[ -d wiki ]`, `[ -d .git ]`, and `grep -q '^wiki/'` so it stays silent otherwise (and avoids the infinite-loop regression caused by the earlier prompt-type version; see commit `e54b419`). |

## Why no `PostCompact` / `prompt`-type hooks

Claude Code's official [hooks reference](https://code.claude.com/docs/en/hooks) lists `PostCompact` under events with **"None" decision control** — it has no mechanism (no `additionalContext`, no prompt injection) to reach the model. Registering any hook there can only produce side effects (or errors). The earlier `prompt`-type hook on `PostCompact`/`SessionStart` failed with `Failed to run: ToolUseContext is required for prompt hook` because prompt hooks depend on a tool-use-scoped runtime that session lifecycle events do not provide. We therefore unregister `PostCompact` entirely and rely on the supported `SessionStart` JSON schema.

## Dependencies

The `SessionStart` hook uses `jq` to emit the JSON payload. The command is guarded by `command -v jq` and exits silently (`|| true`) when `jq` is missing, so the plugin stays safe to install globally — you simply lose hot-cache injection until `jq` is available (`brew install jq` on macOS).

## Non-Vault Sessions

The `SessionStart` hook's `[ -f "$HOT" ]` guard and trailing `|| true` ensure it always exits 0, even when no vault is present. This makes the plugin safe to install globally without breaking non-vault Claude Code sessions.

## Known Issue: Plugin Hooks STDOUT Bug

`anthropics/claude-code#10875` documents that **plugin hook STDOUT may not be captured** by Claude Code in some versions, while identical inline hooks in `settings.json` work correctly. If hot-cache injection fails to take effect after installing the plugin, copy the `SessionStart` hook from `hooks.json` into your user-level `~/.claude/settings.json` as a fallback.

**Test for the bug:** open a fresh Claude Code session in a directory with a populated `wiki/hot.md` and ask Claude "what's in the hot cache?". If Claude has no idea, the STDOUT bug is active in your version.
