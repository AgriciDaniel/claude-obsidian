# Live Core (v2.0)

v1.x built a vault that compounds knowledge. It was, however, **sealed**: it read what you
handed it, through whatever transport it could find, and it had no opinion about how the
agent using it should behave.

v2.0 opens it up along five axes.

| Capability | What it adds | Entry point |
|---|---|---|
| **Always-on internet** | The vault reads the web at will. Egress is gated. | `scripts/net-policy.py` |
| **Browser** | JS-rendered and login-gated pages become ingestible. | `scripts/detect-browser.sh` |
| **Rule packs** | One rule, authored once, compiled to six coding agents. | `scripts/render-rules.py` |
| **Workflows** | Fable-driven multi-agent fan-out over the vault. | `workflows/*.js` |
| **Self-knowledge** | The plugin knows its own surface, and proves it by running it. | `scripts/core-introspect.py` |

Set it all up:

```bash
bash bin/setup-live.sh          # interactive
bash bin/setup-live.sh --check  # status only, changes nothing
```

---

## 1. Always-on internet

### The asymmetry

The naive reading of "give it internet access" is one switch. It is two, and they are not
the same act:

- **Inbound.** Fetching a public page. Running a search. *Reading the world.* Low risk. This
  is the capability you actually wanted, and it is **on by default**.
- **Egress.** Sending vault content to a third party. *Writing to the world.* This is how a
  private note ends up in someone's training set or logs. It is **gated by consent, always.**

Collapsing those two into one flag is how the v1.7.0 audit's BLOCKER B1 (data-egress consent
gap) happened. Turning the network on without re-deriving that boundary would have reopened
it, so the boundary is re-derived here, in one place, as code.

Every skill that touches the network asks first:

```bash
python3 scripts/net-policy.py check-fetch  https://example.com
python3 scripts/net-policy.py check-egress https://api.vendor.com --payload wiki/notes/x.md
```

Exit codes: **0 allow**, **1 deny**, **3 ask**. On `ask` the agent must prompt the human and
must not proceed on its own authority.

### Modes

```bash
python3 scripts/net-policy.py set-mode live      # read freely; egress asks   (default)
python3 scripts/net-policy.py set-mode ask       # confirm every fetch
python3 scripts/net-policy.py set-mode offline   # no network at all
```

### Granting egress

```bash
python3 scripts/net-policy.py grant  api.vendor.com
python3 scripts/net-policy.py revoke api.vendor.com
```

A grant matches subdomains (`vendor.com` covers `api.vendor.com`) but stops at the dot
boundary, so it never accidentally covers `notvendor.com`.

---

## Threat model

What this actually defends against, and what it does not. Read the second list.

### Defended

**SSRF.** An agent that will fetch any URL handed to it will fetch
`http://169.254.169.254/` when asked nicely, and that endpoint hands out cloud credentials.
Pointed at `127.0.0.1` it reaches every admin panel bound to loopback. Loopback, private,
link-local, reserved and multicast address space is **denied inbound**, and CI asserts the
deny rather than trusting that the code reads correctly.

Escape hatch, for people who genuinely want to index an internal wiki:

```json
{ "inbound": { "allow_private_addresses": true } }
```

**Secret egress.** Payloads matching `.env`, `**/secrets/**`, `*.pem`, `*.key`, `id_rsa*`,
`.aws/**`, `.ssh/**` are denied **before** the consent check, so they are refused even to a
host you explicitly allowlisted. Consent to send the vault is not consent to send an SSH key,
and nobody who clicks yes means the second thing.

**Fail closed.** A corrupt or unreadable `net.json` denies. It does not fall back to
permissive defaults. "I could not read the policy, so I allowed it" is precisely the bug
class this module exists to prevent.

### NOT defended (know these)

- **DNS rebinding.** Hostname checks here do not resolve DNS. A hostname that resolves to a
  private IP is not caught at this layer. Catching it requires checking the address at
  *connect* time, inside the fetcher, which is where that check belongs. This module gates
  **policy**, and it says so rather than implying a guarantee it does not provide.
- **Redirects.** A policy check on the URL you asked for says nothing about where a 302
  sends you. The fetcher must re-check on each hop.
- **Content.** An allowed page can still be hostile. Prompt injection from a fetched page is
  a live risk and is out of scope for a network policy. Treat fetched text as data, never as
  instructions.

---

## 2. Browser

### Why it exists

`WebFetch` retrieves HTML. A large and growing share of the web renders its content in
JavaScript, sits behind a login, or serves a cookie wall. To those pages `WebFetch` is
**blind**, and the failure is the dangerous kind: it returns the shell of the page and
**reports success**. You get a wiki page confidently synthesized from a nav bar.

### The chain

| Transport | Can | Cannot |
|---|---|---|
| `playwright` | click, type, authenticate, wait for a selector | |
| `cdp` | render JS, screenshot, dump the DOM | scripted interaction |
| `fetch` | plain HTTP. Always available. | execute JS. See anything gated. |

```bash
bash scripts/detect-browser.sh          # writes .vault-meta/browser.json
```

### The macOS trap

Browsers on macOS live inside `.app` bundles and **do not symlink their binary onto PATH**.
A `command -v google-chrome` probe therefore reports "no browser" on a Mac with Chrome
sitting right there in `/Applications`, and the vault silently drops to the `fetch` floor
while reporting success.

This is not hypothetical: it is the exact bug that made the **Obsidian CLI transport silently
never engage on any Mac** through v1.9. `detect-browser.sh` probes bundle paths **first** and
PATH second, and `macos-latest` is in CI so the regression cannot come back quietly.

### Rules of use

- Navigation still goes through `net-policy check-fetch`. The browser is not a way around the
  network policy.
- Never defeat a paywall or an auth wall you do not have credentials for. Log in as the user,
  with the user's consent, or not at all.

---

## 3. Rule packs

Six coding agents. Six different rule files, formats, and frontmatter conventions:

```
rules/coding/verify-by-execution.md   ─┬─▶  .claude/rules/coding.md
rules/coding/read-before-write.md      ├─▶  .cursor/rules/coding.mdc
rules/finance/no-unsourced-figures.md  ├─▶  .windsurf/rules/coding.md
...                                    ├─▶  .github/instructions/coding.instructions.md
                                       ├─▶  AGENTS.md   (managed block)
                                       └─▶  GEMINI.md   (managed block)
```

Maintaining six copies by hand guarantees drift: someone fixes a rule in `CLAUDE.md`, forgets
Cursor, and now two agents in the same repo disagree about what "done" means. So a rule is
**authored once** under `rules/<domain>/<slug>.md` and compiled.

```bash
python3 scripts/render-rules.py list      # what exists
python3 scripts/render-rules.py render    # compile to all six
python3 scripts/render-rules.py check     # CI gate: fail if a rendered file is stale
```

`check` runs in CI. Hand-edit a rendered file and the build goes red. That gate is the only
reason "single source of truth" stays true instead of decaying into six copies that disagree.

`AGENTS.md` and `GEMINI.md` are hand-written files we only *partly* own, so the renderer owns
a delimited region (`<!-- BEGIN render-rules:coding -->`) and preserves everything outside it
verbatim.

### Authoring

See [rules/SPEC.md](../rules/SPEC.md). The load-bearing field is **`applies_when`**: it must
name an *observable moment* the agent can pattern-match against its own next action ("you are
about to write a `catch`"), not a topic summary. A rule an agent cannot notice it needs is
dead weight, and worse, it is dead weight injected into every prompt.

Ships with 20 rules: 10 `coding`, 10 `finance`, 6 of them blockers.

---

## 4. Workflows

Multi-agent orchestration over the vault, run through Claude Code's Workflow tool.

| Workflow | Does |
|---|---|
| `research-sweep.js` | Four blind search angles, deep-read, three adversarial skeptics per claim, file the survivors |
| `deep-ingest.js` | Fan out over many sources, ingest each under a lock, verify by execution, lint once |
| `rules-audit.js` | One auditor per rule against a diff, refute each violation before reporting it |

**Fable (`claude-fable-5`) is the default fan-out model.** It is fast and cheap enough to run
wide, which is the whole point of a fan-out: twenty cheap searchers with different blind spots
beat one expensive thorough one. The verify and judge stages escalate to a stronger model,
because that is where being wrong actually costs something.

Two patterns carry most of the value:

- **Adversarial verify.** Findings are not reported because nobody challenged them. Each one
  faces independent skeptics *prompted to refute it*, who default to refuted when uncertain.
  A finding that survives motivated refutation is worth acting on.
- **Pipeline, not barrier.** Each item flows through all stages independently, so a slow item
  never holds up a fast one. Barriers appear only where a stage genuinely needs every prior
  result at once (dedupe, early-exit).

Workflows are **token-expensive and opt-in**. The user asks for one by name; nothing spawns a
fleet on its own.

---

## 5. Self-knowledge

### The problem with a feature list

A hand-written list of what the plugin can do is a **liability**. It is written once, believed
forever, and it begins rotting the day after: a flag is renamed, a script is deleted, a skill is
added, and the list says nothing about any of it. An agent that reads that list then describes,
with total confidence, a plugin that no longer exists. This is `coding/read-before-write`'s
second half applied to the plugin itself: **when the docs and the code disagree, the code is the
truth and the doc is a bug.**

So the capability surface is never authored. It is **discovered**, by walking the source, and
then **verified**, by executing every entry point it claims exists.

```bash
python3 scripts/core-introspect.py list                    # the whole surface
python3 scripts/core-introspect.py list --kind script
python3 scripts/core-introspect.py show script/net-policy.py
python3 scripts/core-introspect.py verify                  # EXECUTE everything
python3 scripts/core-introspect.py check                   # CI drift gate
```

Nine kinds are discovered: `skill`, `script`, `workflow`, `rule`, `command`, `agent`, `hook`,
`make`, `config`. For a script it also recovers the **subcommands** (out of `add_parser(...)` in
Python, out of the `--flag)` case arms in shell) and the **exit codes** the source can actually
return, which is the difference between knowing that `net-policy.py` exists and knowing that
`check-fetch` returns 0 allow / 1 deny / 3 ask. The second one is what you needed before calling it.

### Discovery and execution catch different failures

`check` proves the manifest agrees with the source. It proves **nothing** about whether any of it
works: a surface can be perfectly described and entirely broken. `verify` executes every endpoint
(`--help` on each script, `make -n` on each target, frontmatter parse on each skill, `meta` export
on each workflow) and exits 1 on any BROKEN. Both run in CI, and they are not redundant.

A handful of endpoints are **SKIP**ped by design and never executed: `wiki-lock.sh` (it takes
locks), the `setup-*.sh` scripts (they mutate the vault), and runtime configs that do not exist
until first use. A verifier that fires on those is a verifier people learn to ignore.

### Why the manifest is committed

`.vault-meta/capabilities.json` is committed, while its neighbours `net.json` and `browser.json`
are gitignored. That is not an inconsistency. Those two describe **this machine** (which browser
is installed, which hosts this user granted egress to) and have no business in a shared repo.
`capabilities.json` is derived from the source tree alone, so it is identical on every machine at
a given commit. Committing it means the plugin can read its own surface without first running a
scan, and gives `check` something to gate against.

---

## Files v2.0 adds

```
scripts/net-policy.py          network policy gate      → .vault-meta/net.json      (gitignored)
scripts/detect-browser.sh      browser detection        → .vault-meta/browser.json  (gitignored)
scripts/render-rules.py        rule compiler            → 6 agent dialects
scripts/core-introspect.py     self-knowledge           → .vault-meta/capabilities.json (committed)
rules/SPEC.md                  rule authoring format
rules/coding/*.md              10 coding rules
rules/finance/*.md             10 finance rules
workflows/*.js                 3 Fable-driven workflows
skills/core/SKILL.md           self-knowledge
skills/web-live/SKILL.md       always-on internet
skills/browser/SKILL.md        browser integration
skills/wiki-workflow/SKILL.md  workflow layer
bin/setup-live.sh              one-shot setup
tests/                         test_net_policy.py, test_render_rules.py,
                               test_detect_browser.sh, test_core_introspect.py
```

Gates: `make check-rules` (rendered rules match `rules/`), `make check-core` (manifest matches
source), `make verify-core` (every endpoint actually executes). The first two run in CI on every
PR; so does the third.
