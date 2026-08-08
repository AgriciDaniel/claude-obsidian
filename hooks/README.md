# vault-os Hooks

Plugin hooks for the vault-os wiki vault. Two files live here:

- `hooks.json` — Claude Code hook config (uses Claude's event names + prompt-injection hook type).
- `cursor-hooks.json` — Cursor hook config (uses Cursor's event names; prompt-injection lives in `rules/vault-os.mdc` instead).

## Claude Code Events (`hooks.json`)

| Event | Type | Purpose |
|---|---|---|
| `SessionStart` | command + prompt | Runs `scripts/hot-sync.sh` when Ground Truth drifted, then `cat wiki/hot.md`. Also clears stale wiki locks. Prompt type asks the agent to silently treat hot.md as context. Matcher: `startup\|resume`. |
| `PostCompact` | prompt | Re-loads `wiki/hot.md` after context compaction. Hook-injected context does NOT survive compaction (only `CLAUDE.md` does). |
| `PostToolUse` | command | Auto-commits any wiki/ or .raw/ changes after Write or Edit tool calls. Guarded by `[ -d .git ]` and wiki-lock. |
| `Stop` | command | If `wiki/` changed, runs `scripts/hot-sync.sh` (deterministic). No LLM "please update hot.md" prompt. |

## Cursor Events (`cursor-hooks.json`)

Cursor doesn't support prompt-injection hooks; the equivalent guidance is folded into `rules/vault-os.mdc` (always-applied rule). Only command-type behaviors map here:

| Event | Purpose | Maps from |
|---|---|---|
| `sessionStart` | `hot-sync` (if drifted) then `cat wiki/hot.md` | Claude `SessionStart` |
| `afterFileEdit` | Auto-commits wiki/.raw/.vault-meta changes | Claude `PostToolUse` |
| `stop` | `hot-sync` when wiki/ has uncommitted changes | Claude `Stop` |

Note: per [forum.cursor.com](https://forum.cursor.com/t/cursor-cli-doesnt-send-all-events-defined-in-hooks/148316), `stop` fires in the Cursor IDE but is not reliably emitted in cloud agents. Acceptable for v1; the always-applied rule covers end-of-session behavior in environments where the hook doesn't fire.

## Known Issue: Plugin Hooks STDOUT Bug

`anthropics/claude-code#10875` documents that **plugin hook STDOUT may not be captured** by Claude Code, while identical inline hooks in `settings.json` work correctly.

**Impact**: If this bug is active in your Claude Code version, the prompt-type SessionStart and PostCompact hooks may not inject context as expected.

**Workaround**: The command-type SessionStart hook (`cat wiki/hot.md`) is the canonical safety check. It relies on STDOUT capture for context injection, so test against this issue if hot cache restoration fails. As a fallback, copy the hook config from `hooks.json` into your user-level `~/.claude/settings.json` instead of relying on plugin hooks.

**Test for the bug**: After installing the plugin, open a fresh Claude Code session in a directory containing a populated `wiki/hot.md`. Ask Claude "what's in the hot cache?". If Claude has no idea, the STDOUT bug is active in your version.

## Non-Vault Sessions

SessionStart commands exit 0 when `wiki/` or `scripts/hot-sync.sh` is missing, so the plugin stays safe to install globally.
