# claude-obsidian — Claude + Obsidian Wiki Vault

This folder is both a Claude Code plugin and an Obsidian vault.

**Plugin name:** `claude-obsidian` (v1.7+ "Compound Vault" — see [docs/compound-vault-guide.md](docs/compound-vault-guide.md); v1.8+ adds methodology modes — see [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md); v2.0 adds Live Core — see [docs/live-core-guide.md](docs/live-core-guide.md))
**Skills:** `/wiki`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-cli` (v1.7), `/wiki-retrieve` (v1.7, opt-in), `/wiki-mode` (v1.8), `/core`, `/web-live`, `/browser`, `/wiki-workflow` (v2.0)
**Vault path:** This directory (open in Obsidian directly)

## What This Vault Is For

This vault demonstrates the LLM Wiki pattern — a persistent, compounding knowledge base for Claude + Obsidian. Drop any source, ask any question, and the wiki grows richer with every session.

## Vault Structure

```
.raw/           source documents — immutable, Claude reads but never modifies
wiki/           Claude-generated knowledge base
_templates/     Obsidian Templater templates
_attachments/   images and PDFs referenced by wiki pages
```

## How to Use

Drop a source file into `.raw/`, then tell Claude: "ingest [filename]".

Ask any question. Claude reads the index first, then drills into relevant pages.

Run `/wiki` to scaffold a new vault or check setup status.

Run "lint the wiki" every 10-15 ingests to catch orphans and gaps.

## Cross-Project Access

To reference this wiki from another Claude Code project, add to that project's CLAUDE.md:

```markdown
## Wiki Knowledge Base
Path: /path/to/this/vault

When you need context not already in this project:
1. Read wiki/hot.md first (recent context, ~500 words)
2. If not enough, read wiki/index.md
3. If you need domain specifics, read wiki/<domain>/_index.md
4. Only then read individual wiki pages

Do NOT read the wiki for general coding questions or things already in this project.
```

## Plugin Skills

| Skill | Trigger |
|-------|---------|
| `/wiki` | Setup, scaffold, route to sub-skills |
| `ingest [source]` | Single or batch source ingestion |
| `query: [question]` | Answer from wiki content |
| `lint the wiki` | Health check |
| `/save` | File the current conversation as a structured wiki note |
| `/autoresearch [topic]` | Autonomous research loop: search, fetch, synthesize, file |
| `/canvas` | Visual layer: add images, PDFs, notes to Obsidian canvas |
| `/wiki-cli` (v1.7) | Obsidian CLI transport wrapper; default mutation path on desktop |
| `/wiki-retrieve` (v1.7) | Hybrid contextual + BM25 + cosine-rerank retrieval (opt-in via `bash bin/setup-retrieve.sh`) |
| `/wiki-mode` (v1.8) | Methodology modes (LYT / PARA / Zettelkasten / Generic). Set via `bash bin/setup-mode.sh`; consumed by wiki-ingest / save / autoresearch for routing new pages |
| `/think` (v1.9) | The 10-principle thinking loop (OBSERVE-OBSERVE-LISTEN-THINK-CONNECT-CONNECT-FEEL-ACCEPT-CREATE-GROW) as an invocable workflow. Apply to architectural decisions, audits, post-mortems, ambiguous user requests. Every other skill has a "How to think" appendix mapping this framework to its specific work |
| `/core` (v2.0) | The plugin's knowledge of itself. Every endpoint, its flags, its exit codes, and whether it actually runs. Never answer a capability question about this plugin from memory or from a README; ask `scripts/core-introspect.py` |
| `/web-live` (v2.0) | Always-on internet. Inbound reads are free; egress asks. Every network call consults `scripts/net-policy.py` first |
| `/browser` (v2.0) | Browser automation for JS-rendered and login-gated pages, which `WebFetch` cannot see and fails silently on |
| `/wiki-workflow` (v2.0) | Fable-driven multi-agent fan-out: `research-sweep`, `deep-ingest`, `rules-audit`. Token-expensive, opt-in, asked for by name |

## Transport (v1.7+)

`scripts/detect-transport.sh` writes `.vault-meta/transport.json` on first run and refreshes weekly. Skills consult it before mutating the vault. Fallback chain: Obsidian CLI → mcp-obsidian → mcpvault → filesystem (always-available floor). Decision tree: [wiki/references/transport-fallback.md](wiki/references/transport-fallback.md).

## Concurrency (v1.7+)

`scripts/wiki-lock.sh` provides per-file advisory locks for safe multi-writer ingest. Every wiki page write should be guarded by `wiki-lock acquire`/`release`. Stale-after default is 60s; cross-process release allowed by design. The PostToolUse hook defers `git add` while locks are held. Closes the latent multi-writer corruption hole from v1.6.

## Methodology Modes (v1.8+)

Pick an organizational style for the vault via `bash bin/setup-mode.sh`. Four modes available: **generic** (v1.7 default — no opinion), **LYT** (Linking Your Thinking — MOCs + atomic notes), **PARA** (Projects/Areas/Resources/Archives), **Zettelkasten** (timestamped IDs, flat, dense linking). The mode is written to `.vault-meta/mode.json` (gitignored by default; `git add -f` to commit). `wiki-ingest`, `save`, and `autoresearch` consult `python3 scripts/wiki-mode.py route <type> "<name>"` before filing new pages — no special-casing needed in the consumer skills. Full guide: [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md). Closes priority gap 5 from the May 2026 compass artifact.

## Pre-commit verifier (v1.7.1+)

After staging changes for a non-trivial workstream but BEFORE running `git commit`, dispatch the `verifier` agent (`agents/verifier.md`). It reads `git diff --cached`, applies the /best-practices six-cut + agent kernel, and returns findings in four tiers (BLOCKER / HIGH / MEDIUM / LOW) with file:line citations. The agent has read-only tools (Read, Grep, Glob, Bash) — it can inspect but never modify, so its output is purely advisory. This closes the loop the v1.7 audit revealed: code went worker → commit with no separate verifier pass, which is how BLOCKER B1 (data-egress consent gap) slipped through. See `docs/audits/v1.7.0-audit-2026-05-17.md` §10 for the retrospective.

## Live Core (v2.0)

Four capabilities that open the vault up. Full guide: [docs/live-core-guide.md](docs/live-core-guide.md).
Set up with `bash bin/setup-live.sh` (`--check` for status only).

**Always-on internet.** The vault reads the web at will. It does NOT send vault content
anywhere without consent. Those are different acts and they get different defaults: inbound is
on, egress asks. Every network call consults `python3 scripts/net-policy.py check-fetch <url>`
(or `check-egress`) FIRST. Exit 0 allow, 1 deny, 3 ask. On `ask` you must prompt the human and
must not proceed on your own authority. An SSRF guard denies loopback, private, and
cloud-metadata addresses; secrets (`.env`, keys, `.aws/`, `.ssh/`) can never egress, even to an
allowlisted host. A corrupt policy file fails closed. This is the boundary the v1.7.0 audit's
BLOCKER B1 was about; turning the network on without re-deriving it would have reopened it.

**Browser.** `scripts/detect-browser.sh` writes `.vault-meta/browser.json`. Chain:
playwright (full interaction) → cdp (headless render, screenshot, dump-dom) → fetch (plain
HTTP, always available). Use it whenever a page is JS-rendered or login-gated: `WebFetch` is
blind to those and fails SILENTLY, returning the page shell while reporting success. The
browser does not bypass net-policy; navigation still checks first.

**Rule packs.** `rules/<domain>/<slug>.md` is the single source of truth; `scripts/render-rules.py`
compiles each rule into six agent dialects (Claude, Cursor, Windsurf, Copilot, Codex, Gemini).
Never hand-edit a rendered file (`.cursor/rules/*.mdc`, `.claude/rules/*.md`, the managed blocks
in `AGENTS.md` / `GEMINI.md`): edit `rules/` and re-render. `render-rules.py check` runs in CI and
goes red on drift. Ships 20 rules (10 coding, 10 finance; 6 blockers).

**Workflows.** `workflows/*.js` run through the Workflow tool: `research-sweep` (blind-angle web
sweep, adversarial verify, file), `deep-ingest` (lock-guarded parallel batch ingest, verify by
execution, lint once), `rules-audit` (one auditor per rule, refute before reporting). Fable is
the default fan-out model; verify stages escalate. Token-expensive and opt-in: only run one when
the user asks for it by name.

**Self-knowledge.** The plugin knows its own surface, and it does not learn it from prose.
`scripts/core-introspect.py` DISCOVERS every endpoint by walking the source (skills, scripts and
their subcommands and exit codes, workflows, rules, commands, agents, hooks, make targets,
configs) and VERIFIES it by EXECUTING each one. `list`, `show <id>`, `verify`, `check`. The
manifest lands in `.vault-meta/capabilities.json` and is committed, because unlike `net.json` and
`browser.json` it describes the source, not the machine. **Never answer a question about what this
plugin can do from memory, from this file, or from a README** — those are the stale-doc failure
mode, and they are the most convincing possible source of a wrong answer. Ask the manifest.
`make check-core` gates drift in CI; `make verify-core` proves the surface is real rather than
merely declared.

## MCP (Optional)

If you configured the MCP server, Claude can read and write vault notes directly.
See `skills/wiki/references/mcp-setup.md` for setup instructions.

## Release Blog Post

After cutting a new release (git tag + `gh release create`), run:

```
/release-blog
```

This generates a blog post on https://agricidaniel.com/blog/, handles cover image generation, SEO metadata, FAQ schema, internal linking, sitemap/llms.txt updates, Vercel deployment, and Google indexing.
