# vault-os Hooks

Plugin hooks for the vault-os wiki vault. Two files live here:

- `hooks.json` — Claude Code hook config (uses Claude's event names + prompt-injection hook type).
- `cursor-hooks.json` — Cursor hook config (uses Cursor's event names; prompt-injection lives in `rules/vault-os.mdc` instead).

## Claude Code Events (`hooks.json`)

| Event | Type | Purpose |
|---|---|---|
| `SessionStart` | command + prompt | Loads `wiki/hot.md` into context. Command type runs `[ -f wiki/hot.md ] && cat wiki/hot.md` as the canonical safety check (works for non-vault sessions without erroring). Prompt type complements with semantic context restoration. Matcher: `startup\|resume`. |
| `PostCompact` | prompt | Re-loads `wiki/hot.md` after context compaction. Hook-injected context does NOT survive compaction (only `CLAUDE.md` does), so this hook restores the hot cache mid-session. |
| `PostToolUse` | command | Auto-commits any wiki/ or .raw/ changes after Write or Edit tool calls. Guarded by `[ -d .git ]` so it never errors in non-git directories, and by `git diff --cached --quiet` so it never creates empty commits. |
| `Stop` | prompt | Updates `wiki/hot.md` at the end of every Claude response with a brief summary of what changed. |

## Cursor Events (`cursor-hooks.json`)

Cursor doesn't support prompt-injection hooks; the equivalent guidance is folded into `rules/vault-os.mdc` (always-applied rule). Only command-type behaviors map here:

| Event | Purpose | Maps from |
|---|---|---|
| `sessionStart` | `cat wiki/hot.md` if present (safe in non-vault sessions). | Claude `SessionStart` command hook |
| `afterFileEdit` | Auto-commits wiki/.raw/.vault-meta changes. Same one-liner as Claude. | Claude `PostToolUse` (Write\|Edit) |
| `stop` | Emits `WIKI_CHANGED:` reminder when wiki/ has uncommitted changes so the agent updates `wiki/hot.md`. | Claude `Stop` prompt hook |

Note: per [forum.cursor.com](https://forum.cursor.com/t/cursor-cli-doesnt-send-all-events-defined-in-hooks/148316), `stop` fires in the Cursor IDE but is not reliably emitted in cloud agents. Acceptable for v1; the always-applied rule covers end-of-session behavior in environments where the hook doesn't fire.

## Known Issue: Plugin Hooks STDOUT Bug

`anthropics/claude-code#10875` documents that **plugin hook STDOUT may not be captured** by Claude Code, while identical inline hooks in `settings.json` work correctly.

**Impact**: If this bug is active in your Claude Code version, the prompt-type SessionStart and PostCompact hooks may not inject context as expected.

**Workaround**: The command-type SessionStart hook (`cat wiki/hot.md`) is the canonical safety check. It relies on STDOUT capture for context injection, so test against this issue if hot cache restoration fails. As a fallback, copy the hook config from `hooks.json` into your user-level `~/.claude/settings.json` instead of relying on plugin hooks.

**Test for the bug**: After installing the plugin, open a fresh Claude Code session in a directory containing a populated `wiki/hot.md`. Ask Claude "what's in the hot cache?". If Claude has no idea, the STDOUT bug is active in your version.

## Non-Vault Sessions

The SessionStart command hook uses `[ -f wiki/hot.md ] && cat wiki/hot.md || true` so it always exits 0, even when no vault is present. This makes the plugin safe to install globally without breaking non-vault Claude Code sessions.
