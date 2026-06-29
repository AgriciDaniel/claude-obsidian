# claude-obsidian — Claude + Obsidian Wiki Vault

This folder is both a Claude Code plugin and an Obsidian vault.

**Plugin name:** `claude-obsidian` (v1.7+ "Compound Vault" — see [docs/compound-vault-guide.md](docs/compound-vault-guide.md); v1.8+ adds methodology modes — see [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md))
**Skills:** `/wiki`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-cli` (v1.7), `/wiki-retrieve` (v1.7, opt-in), `/wiki-mode` (v1.8)
**Vault path:** This directory (open in Obsidian directly)

## What This Vault Is For

This vault demonstrates the LLM Wiki pattern — a persistent, compounding knowledge base for Claude + Obsidian. Drop any source, ask any question, and the wiki grows richer with every session.

## Operating Principles (general — how to work, not what to build)

These govern *method*, not subject matter, and apply to every task. They exist because in
the SEC/EDGAR research a blocked primary source (sec.gov returned HTTP 403) was routed
around with weaker secondary sources instead of being fixed at the source. The real cause
was a missing `User-Agent` header — a one-line fix that went unmade for hours. Don't repeat
that pattern:

1. **Diagnose before detour.** When a tool call or fetch fails or returns a blocked / empty
   / error result (403, 401, 429, 5xx, empty body, truncated output), do NOT silently fall
   back to an inferior source or approach. First read the actual error, form a hypothesis
   about the cause, and try to fix the access itself (User-Agent / headers, auth, rate,
   endpoint, or a different tool). Only fall back if the fix genuinely fails.
2. **A blocked primary source is a bug, not a fact.** The more authoritative/valuable the
   source, the more it's worth fixing access rather than approximating around it.
3. **Say so when you fall back.** If you do use a lesser source after a block, state plainly
   that you did, why, and what's therefore unverified. Never present a workaround as if it
   were the primary source.
4. **Capture the fix.** When you discover a workaround or technique, persist it to durable
   memory (this file, a script, or a wiki/doc) and tell the user where you put it, so it is
   not rediscovered from scratch next time.
5. **Escalate, don't quietly degrade.** When you cannot fix an obstacle, surface it to the
   user instead of silently lowering quality.

## Product Context (what this research is FOR)

The SEC/EDGAR research in this vault is not academic. It serves a product: a
**counsel-ready, drift-monitored compliance layer for securities offerings** -
"Vanta-for-securities-counsel." The product makes an issuer counsel-ready and monitors for
drift; **the lawyer still opines.** It assembles and flags; **it never opines.** Outputs
resolve to `satisfied + evidence` / `open` / `escalate to counsel` - never to a legal
conclusion ("compliant", "exemption available"). That discipline is the defensible,
non-malpractice position; honor it in anything built here.

The SEC wiki = the controls framework. `scripts/sec-fetch.sh` + data.sec.gov = the
verification/monitoring/precedent layer. The autoresearch loop = the regulatory-drift
monitor prototype. Full thesis (living): [docs/product-thesis.md](docs/product-thesis.md).

**Standing directive (do this without being asked):** treat the thesis as THE goal. When
product-relevant, read it first; and when any work, research, data pull, or remark sharpens,
contradicts, or answers something in it, **update the doc and bump its Revision Log as part
of the work** - do not wait to be prompted. Point the autoresearch backlog at the doc's Open
Questions so each pass retires one. See the doc's "Self-Refinement Protocol" for the full
rule and the honest boundary (persistence is external memory reloaded per session, not
autonomous cognition). This is the capture-the-fix Operating Principle applied to the goal.

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

## Transport (v1.7+)

`scripts/detect-transport.sh` writes `.vault-meta/transport.json` on first run and refreshes weekly. Skills consult it before mutating the vault. Fallback chain: Obsidian CLI → mcp-obsidian → mcpvault → filesystem (always-available floor). Decision tree: [wiki/references/transport-fallback.md](wiki/references/transport-fallback.md).

## Concurrency (v1.7+)

`scripts/wiki-lock.sh` provides per-file advisory locks for safe multi-writer ingest. Every wiki page write should be guarded by `wiki-lock acquire`/`release`. Stale-after default is 60s; cross-process release allowed by design. The PostToolUse hook defers `git add` while locks are held. Closes the latent multi-writer corruption hole from v1.6.

## Methodology Modes (v1.8+)

Pick an organizational style for the vault via `bash bin/setup-mode.sh`. Four modes available: **generic** (v1.7 default — no opinion), **LYT** (Linking Your Thinking — MOCs + atomic notes), **PARA** (Projects/Areas/Resources/Archives), **Zettelkasten** (timestamped IDs, flat, dense linking). The mode is written to `.vault-meta/mode.json` (gitignored by default; `git add -f` to commit). `wiki-ingest`, `save`, and `autoresearch` consult `python3 scripts/wiki-mode.py route <type> "<name>"` before filing new pages — no special-casing needed in the consumer skills. Full guide: [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md). Closes priority gap 5 from the May 2026 compass artifact.

## Pre-commit verifier (v1.7.1+)

After staging changes for a non-trivial workstream but BEFORE running `git commit`, dispatch the `verifier` agent (`agents/verifier.md`). It reads `git diff --cached`, applies the /best-practices six-cut + agent kernel, and returns findings in four tiers (BLOCKER / HIGH / MEDIUM / LOW) with file:line citations. The agent has read-only tools (Read, Grep, Glob, Bash) — it can inspect but never modify, so its output is purely advisory. This closes the loop the v1.7 audit revealed: code went worker → commit with no separate verifier pass, which is how BLOCKER B1 (data-egress consent gap) slipped through. See `docs/audits/v1.7.0-audit-2026-05-17.md` §10 for the retrospective.

## SEC / EDGAR Primary-Source Access (IMPORTANT — read before fetching sec.gov)

**The `WebFetch` tool gets HTTP 403 from sec.gov.** This is NOT a hard block — SEC's
fair-access policy simply *requires* a declared `User-Agent` (with contact info) and
caps traffic at **10 requests/second**. A request *with* that header returns HTTP 200,
for both sec.gov HTML pages (server-rendered, no JS) and the `data.sec.gov` JSON APIs.

**Do not use `WebFetch` for sec.gov. Use the wrapper instead:**

```bash
export SEC_CONTACT_EMAIL="you@example.com"        # SEC expects a real contact
bash scripts/sec-fetch.sh "https://www.sec.gov/<path>"                 # raw HTML/JSON
bash scripts/sec-fetch.sh --text "https://www.sec.gov/<path>"          # HTML -> plain text
bash scripts/sec-fetch.sh "https://data.sec.gov/submissions/CIK##########.json"
```

High-value `data.sec.gov` endpoints (no API key needed): `submissions/CIK##########.json`
(all of a filer's filings), `api/xbrl/companyfacts/CIK##########.json` (all XBRL facts),
`api/xbrl/companyconcept/...`, `api/xbrl/frames/...`. CIK is the permanent 10-digit filer
ID (zero-padded in API paths). Full method + identifiers: [[EDGAR Data Access]],
[[EDGAR APIs]], [[EDGAR Bulk Data]] in the wiki. (Established 2026-06-29 after WebFetch
403s blocked SEC primary sources during the SEC/EDGAR autoresearch.)

## MCP (Optional)

If you configured the MCP server, Claude can read and write vault notes directly.
See `skills/wiki/references/mcp-setup.md` for setup instructions.

## Release Blog Post

After cutting a new release (git tag + `gh release create`), run:

```
/release-blog
```

This generates a blog post on https://agricidaniel.com/blog/, handles cover image generation, SEO metadata, FAQ schema, internal linking, sitemap/llms.txt updates, Vercel deployment, and Google indexing.
