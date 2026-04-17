# claude-obsidian Hooks

Plugin hooks for the claude-obsidian wiki vault. All hooks are defined in `hooks.json`.

## Events

| Event | Type | Purpose |
|---|---|---|
| `SessionStart` | command | Loads `wiki/hot.md` into context via `[ -f wiki/hot.md ] && cat wiki/hot.md` (works for non-vault sessions without erroring). Matcher: `startup\|resume`. |
| `PostCompact` | command | Re-loads `wiki/hot.md` via `cat` after context compaction. Hook-injected context does NOT survive compaction (only `CLAUDE.md` does), so this hook restores the hot cache mid-session. |
| `PostToolUse` | command | Auto-commits any wiki/ or .raw/ changes after Write or Edit tool calls. Guarded by `[ -d .git ]` so it never errors in non-git directories, and by `git diff --cached --quiet` so it never creates empty commits. |
| `Stop` | prompt | Updates `wiki/hot.md` at the end of every Claude response with a brief summary of what changed. |

## Known Issue: Plugin Hooks STDOUT Bug

`anthropics/claude-code#10875` documents that **plugin hook STDOUT may not be captured** by Claude Code, while identical inline hooks in `settings.json` work correctly.

**Impact**: If this bug is active in your Claude Code version, the command-type SessionStart and PostCompact hooks may not inject `wiki/hot.md` into context as expected.

**Workaround**: Both hooks run `cat wiki/hot.md` and rely on STDOUT capture for context injection. If hot cache restoration fails, copy the hook config from `hooks.json` into your user-level `~/.claude/settings.json` instead of relying on plugin hooks.

**Test for the bug**: After installing the plugin, open a fresh Claude Code session in a directory containing a populated `wiki/hot.md`. Ask Claude "what's in the hot cache?". If Claude has no idea, the STDOUT bug is active in your version.

## Non-Vault Sessions

The SessionStart command hook uses `[ -f wiki/hot.md ] && cat wiki/hot.md || true` so it always exits 0, even when no vault is present. This makes the plugin safe to install globally without breaking non-vault Claude Code sessions.
