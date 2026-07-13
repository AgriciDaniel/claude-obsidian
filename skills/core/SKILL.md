---
name: core
description: "The plugin's knowledge of itself (v2.0 'Live Core'). Answers what claude-obsidian can do, what every skill/script/workflow/rule/hook/make-target is, what flags and subcommands and exit codes each exposes, and whether each one actually works. Backed by `scripts/core-introspect.py`, which DISCOVERS the surface by walking the source and VERIFIES it by executing every entry point. Never answer a question about this plugin's capabilities from memory or from a README. Triggers on: core, what can you do, what are your capabilities, what skills do you have, what does this plugin do, list the scripts, what commands exist, what flags does X take, how do I invoke X, is X broken, does X still work, what endpoints are there, self-introspection, capabilities, capability manifest, show me the surface, what workflows exist, what rules are loaded."
allowed-tools: Read, Bash, Grep, Glob
---

# core: The Plugin's Knowledge of Itself

A hand-written feature list is a **liability**. It is written once, believed forever, and it starts rotting the day after it is written: a flag gets renamed, a script gets deleted, a skill gets added, and the list says nothing. An agent that reads that list then confidently describes a plugin that no longer exists.

So the capability surface is **never authored**. It is:

1. **Discovered**, by walking the source tree.
2. **Verified**, by executing every entry point it claims exists.

Both halves matter, and they catch different failures. Discovery alone gives you a manifest that agrees with the source and is still entirely wrong about whether anything *works*. Execution is what turns "declared" into "real".

## The one rule

**Never answer a question about this plugin's own capabilities from memory, from `CLAUDE.md`, from a README, or from a docstring.** Ask the manifest. Those documents are exactly the stale-prose failure this skill exists to replace, and they are the most convincing possible source of a wrong answer, because they were true once.

```bash
python3 scripts/core-introspect.py list              # the whole surface
python3 scripts/core-introspect.py list --kind script
python3 scripts/core-introspect.py show script/net-policy.py
```

## Subcommands

| Command | Does | Exit |
|---|---|---|
| `scan` | Walk the source, write `.vault-meta/capabilities.json` | 0 |
| `scan --peek` | Same, to stdout, writing nothing | 0 |
| `list [--kind K]` | Human-readable surface | 0 |
| `show <id>` | Everything known about one endpoint | 0, 1 if unknown |
| `verify [--kind K]` | **Execute** every entry point | 1 if anything is BROKEN |
| `check` | Manifest on disk matches source | 1 on drift |

Kinds: `skill`, `script`, `workflow`, `rule`, `command`, `agent`, `hook`, `make`, `config`.

## What it knows about each endpoint

Not just that a thing exists. For a script it recovers the **subcommands** (parsed out of `add_parser(...)` for Python, out of the `--flag)` case arms for shell) and the **exit codes** the source can actually return. For a skill, its frontmatter and triggers. For a make target, its recipe. `show` prints all of it.

That is the difference between "there is a script called `net-policy.py`" and "`net-policy.py check-fetch <url>` returns 0 allow, 1 deny, 3 ask", which is the thing you actually needed to know before calling it.

## When to use this

- The user asks what the plugin can do, or what a specific endpoint takes.
- **Before you invoke any script in this repo.** `show` the endpoint rather than guessing its flags. A guessed flag is a silent wrong result.
- After adding or removing anything: run `scan`, or `make check-core` goes red in CI.
- When something seems broken: `verify --kind script` executes them and tells you which one actually is, instead of you reading code and forming an opinion.

## Verify is not a formality

`verify` runs `--help` against every script, `make -n` against every target, parses every skill's frontmatter, and checks every workflow exports a `meta` block. It reports **OK / SKIP / BROKEN** and exits 1 on any BROKEN.

A handful of endpoints are **SKIP**ped by design, never executed: `wiki-lock.sh` (it takes locks), the `setup-*.sh` scripts (they mutate the vault), and runtime configs that do not exist until first use. A verifier that fires on those is a verifier that cries wolf, and people learn to ignore it.

## How to think

The trap this skill exists to close is `coding/read-before-write`'s second half: **when docs and code disagree, the code is the truth and the doc is a bug**. Everything here is generated from the code, so it cannot disagree with it. The moment you answer a capability question from prose instead, you have reintroduced the exact defect.

And `coding/verify-by-execution`: a manifest that says an endpoint exists is an inspection. `verify` is the execution. Do not report that the plugin's surface is healthy on the strength of `check` passing; `check` only proves the JSON matches the source. Run `verify`.
