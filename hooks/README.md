# Claude Code hooks

`hooks.json` is a thin Claude Code adapter around the portable core.

| Event | Matcher | Behavior |
|---|---|---|
| `SessionStart` | `startup|resume|clear|compact` | Silent by default. With `CLAUDE_OBSIDIAN_SESSION_CONTEXT=1`, resolves a real user vault and emits a bounded, sanitized `wiki/hot.md` data block. A workspace-configured vault outside that project also requires an exact `CLAUDE_OBSIDIAN_SESSION_CONTEXT_VAULT` path. |
| `Stop` | unsupported/omitted | Emits a bounded, aggregate JSON `systemMessage` when recovery is needed, or when `wiki/log.md` has accumulated at or above 85% of the wiki-fold batch size (`2**k`, default `k=4`, override with `CLAUDE_OBSIDIAN_FOLD_BATCH_EXPONENT`) worth of entries since the last fold. The fold warning is advisory only: it never runs wiki-fold or mutates the vault, and folding stays human-invoked. It omits operation identifiers, paths, and note content; otherwise it is silent. |

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
