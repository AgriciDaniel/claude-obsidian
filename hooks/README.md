# Claude Code hooks

`hooks.json` is a thin Claude Code adapter around the portable core.

Hooks require a current Claude Code release: the exec-form `command` and
`args` hook shape and the `compact` `SessionStart` matcher used below need it
(see the [Claude Code hooks contract](https://code.claude.com/docs/en/hooks)).
Both hooks also need an interpreter reachable as `python3` on `PATH`; see the
[Windows and WSL guide](../docs/windows-wsl.md#claude-code-hooks-and-python3-on-windows)
for native Windows setup.

| Event | Matcher | Behavior |
|---|---|---|
| `SessionStart` | `startup|resume|clear|compact` | Silent by default. With `CLAUDE_OBSIDIAN_SESSION_CONTEXT=1`, resolves a real user vault and emits a bounded, sanitized `wiki/hot.md` data block. A workspace-configured vault outside that project also requires an exact `CLAUDE_OBSIDIAN_SESSION_CONTEXT_VAULT` path. |
| `Stop` | unsupported/omitted | Emits a bounded, aggregate JSON `systemMessage` when recovery is needed. It also emits one advisory line, after any recovery warnings, when `wiki/log.md` holds at least 85% of a wiki-fold batch (`2**k` entries, default `k=4`, override with `CLAUDE_OBSIDIAN_FOLD_BATCH_EXPONENT`) above its most recent `fold` marker. That check reads at most the first 512 KiB of the log, never recommends `transaction recover`, never runs wiki-fold, and never writes. It omits operation identifiers, paths, and note content; otherwise it is silent. |

Both are `command` hooks using an executable plus an argument array and
`${CLAUDE_PLUGIN_ROOT}` only to locate plugin code. They do not use the plugin
cache as a vault.

The response shapes follow the current [Claude Code hooks contract](https://code.claude.com/docs/en/hooks):
An opted-in SessionStart may add context through stdout, while Stop warnings use the
supported top-level `systemMessage` field. Stop has no matcher because that
event does not support one. Both readers reject symlinked paths and cap their
scan count and output bytes.

Hooks never write knowledge, update `wiki/hot.md`, stage files, commit Git, run
remote calls, or bypass transaction approval. The same workflows remain usable
on hosts that do not support Claude hooks.
