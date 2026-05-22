# claude-obsidian — Claude + Obsidian Wiki Vault

This folder is both a Claude Code plugin and an Obsidian vault.

**Plugin name:** `claude-obsidian`
**Skills:** `/wiki`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`
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

## MCP (Optional)

If you configured the MCP server, Claude can read and write vault notes directly.
See `skills/wiki/references/mcp-setup.md` for setup instructions.

---

## CLAUDE.md Best Practices Reference

**Sources:** [Article by @0xDepressionn](https://x.com/0xDepressionn/status/2055999112470839383) · [21-rule reference card](https://x.com/0xDepressionn/status/2057115586480513376/photo/1)

Karpathy's method: 65% → 94% coding accuracy. One plain text file. 21 rules. 2-hour setup. ~$975/week saved per developer.

### Karpathy's 4 core rules

1. **Ask, don't assume** — Unclear? Ask before writing a single line. Never assume intent.
2. **Simplest first** — No abstractions or flexibility not explicitly requested.
3. **Don't touch unrelated** — Not part of the task? Don't touch it. Even if it seems like a good idea.
4. **Flag uncertainty** — Not confident? Say it before proceeding. Always.

### Full 21-rule framework

**DEFAULTS (1–7)** — eliminate repeated context
1. Kill filler — No "Great question!" — start with the answer.
2. Match length — Short for simple. Full for complex. No padding.
3. Show options — 2–3 approaches first. Wait for choice.
4. Admit gaps — Not sure? Say it before including it.
5. Who I am — Name / Role / Strong in / Still learning.
6. Project context — Goal / Stack / Audience / What to avoid.
7. Lock voice — Style + words I use / words I never use.

**BEHAVIOR (8–14)** — prevent unauthorized changes
8. Stay in scope — Touch only what's asked. Note the rest.
9. Ask first — Describe the change. Wait for yes.
10. Confirm destruct — Deleting? List what's affected. Wait.
11. Hard stops — Deploy / migrate / send = explicit yes.
12. Show changes — Files touched / modified / untouched / next.
13. No acting alone — Never send/post/publish without yes.
14. Think first — Reason step by step before coding.

**MEMORY + STACK (15–21)** — prevent forgotten decisions
15. MEMORY.md — Log: what / why / what was rejected.
16. Session end — Summary: done / in progress / next.
17. ERRORS.md — Log failures. Check before suggesting.
18. Permanent facts — Always-true rules. Flag any conflict.
19. Lock stack — Define tech stack. Never switch without asking.
20. Think deep — Architecture = extended thinking. Always.
21. Karpathy's 4 — See above. The rules that went viral.
