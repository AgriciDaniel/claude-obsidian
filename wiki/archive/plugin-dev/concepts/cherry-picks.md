---
type: concept
title: "Cherry-Picks: Feature Backlog from Ecosystem Research"
created: 2026-04-08
updated: 2026-04-08
tags:
  - backlog
  - cherry-picks
  - product-roadmap
  - claude-obsidian
status: current
related:
  - "[[claude-obsidian-ecosystem]]"
  - "[[LLM Wiki Pattern]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Cherry-Picks: Feature Backlog

> Sourced from ecosystem research 2026-04-08 | 16+ projects analyzed
> Prioritized by: impact × implementation ease × uniqueness

---

## Tier 1 — Quick Wins (High Impact, Low Effort)

### 1. URL Ingestion in /wiki-ingest
**Source**: ekadetov/llm-wiki, Ar9av/obsidian-wiki
**What it is**: Pass a URL directly to ingest instead of a file path. Agent fetches the page, cleans it, saves to `.raw/`, then ingests.
**Current state**: Users must manually copy-paste web content.
**How to add**: Detect `https://` prefix in ingest skill → WebFetch → save to `.raw/articles/` → proceed with normal ingest.
**Bonus**: Pair with **defuddle** (kepano's web cleaner) for clean token-efficient extraction.

### 2. Auto-Commit PostToolUse Hook
**Source**: ballred/obsidian-claude-pkm, ekadetov/llm-wiki
**What it is**: Every Write/Edit tool call in the vault triggers `git add -A && git commit -m "auto: [filename] [timestamp]"`.
**Current state**: No auto-commit. Users must manually push.
**How to add**: PostToolUse hook in hooks.json targeting Write + Edit tools, scoped to wiki/ directory.
**Note**: Makes vault a proper version-controlled knowledge base automatically.

### 3. defuddle Web Cleaning Skill
**Source**: kepano/obsidian-skills
**What it is**: A skill that wraps `defuddle-cli` — strips ads, nav, clutter from web pages before ingest. Reduces token usage ~40-60% on typical web articles.
**How to add**: New `defuddle` sub-skill or reference in wiki-ingest. Requires `defuddle-cli` npm package.

---

## Tier 2 — Medium Effort, High Value

### 4. Delta Tracking Manifest
**Source**: Ar9av/obsidian-wiki
**What it is**: `.raw/.manifest.json` tracking every ingested source — path, hash, timestamp, which wiki pages it produced. Re-ingest only processes new/changed files.
**Current state**: Every `/wiki-ingest` call re-processes everything.
**How to add**:
  - On ingest: compute MD5 hash of source → check manifest → skip if unchanged
  - On ingest: record `{path, hash, ingested_at, pages_created}` in manifest
  - On update: re-process if hash changed, merge changes into existing pages

### 5. Multi-Depth Query Modes
**Source**: rvk7895/llm-knowledge-bases
**What it is**: 3 query tiers in `/wiki-query`:
  - **Quick** — hot.md + index.md only (~3 pages read)
  - **Standard** — full wiki cross-reference + optional web search supplement
  - **Deep** — parallel sub-agents, each researching a different angle
**Current state**: One depth level.
**How to add**: `/wiki-query quick <question>`, `/wiki-query deep <question>` flags in SKILL.md.

### 6. /wiki-ingest Vision Support
**Source**: Ar9av/obsidian-wiki
**What it is**: Ingest images, screenshots, whiteboard photos by passing the image to a vision-capable model.
**How to add**: Detect image extension → read as base64 → pass to Claude with vision prompt asking for transcription/description → treat result as text source → standard ingest pipeline.
**Useful for**: Whiteboard photos from meetings, screenshots of web content, diagrams.

---

## Tier 3 — Bigger Features Worth Planning

### 7. /adopt — Import Existing Vault
**Source**: heyitsnoah/claudesidian, ballred/obsidian-claude-pkm
**What it is**: `/adopt` analyzes an existing Obsidian vault, detects its organization method (PARA, Zettelkasten, LYT, plain), and wraps the LLM Wiki pattern around it without destroying existing structure.
**Why it matters**: Currently, users must start fresh. This unlocks adoption by people with existing vaults.
**Implementation**: Scan folder structure → classify patterns → generate CLAUDE.md mapping existing folders to wiki roles → non-destructive.

### 8. Productivity Wrapper (Daily/Weekly Reviews)
**Source**: ballred/obsidian-claude-pkm
**What it is**: Optional `/daily` and `/weekly` skills that connect goal tracking to the knowledge base.
**Could be a separate plugin** rather than bundled into claude-obsidian.
**Goal cascade**: 3-Year Vision → Yearly Goals → Projects → Weekly → Daily.

### 9. Multi-Agent Compatibility (Cursor, Windsurf, Codex)
**Source**: Ar9av/obsidian-wiki, kepano/obsidian-skills
**What it is**: A `setup.sh` or `/wiki-convert` command that generates `.cursor/rules/`, `AGENTS.md`, `GEMINI.md` equivalents so the wiki skills work in other coding agents.
**Note**: kepano already published skills in Agent Skills format — claude-obsidian is already in that format. Just needs the adapter files.

### 10. Marp Presentation Output
**Source**: rvk7895/llm-knowledge-bases, ekadetov/llm-wiki
**What it is**: `/wiki-query --slides <topic>` generates a Marp presentation from wiki content, saved to `output/`.
**Requires**: `marp-cli` npm package.

---

## Tier 4 — Research / Ecosystem Plays

### 11. obsidian-memory-mcp Integration
**Source**: YuNaga224/obsidian-memory-mcp
**What it is**: Connect the MCP server that stores Claude's memories as Markdown entities with `[[wikilinks]]` → they appear in Obsidian graph view automatically.
**How to add**: Point MEMORY_DIR to the wiki/entities/ directory — entity memory pages become proper wiki pages.

### 12. obsidian-bases Skill (from kepano)
**Source**: kepano/obsidian-skills
**What it is**: Teach Claude how to create and edit Obsidian Bases (.base files) for dynamic tables, views, and filters.
**Why**: Obsidian Bases is a new core feature — no other LLM Wiki project teaches Claude about it yet.

### 13. Schema-Emergent Vault Mode
**Source**: Ar9av/obsidian-wiki
**What it is**: Alternative /wiki mode where the vault structure is not scaffolded upfront but emerges from ingested content. Good for exploratory knowledge building vs. structured domains.
**How**: Skip the scaffold step; let wiki-ingest create folders/categories organically based on source content.

---

## Competitive Positioning

After this research, claude-obsidian's unique advantages remain:
- **Hot cache** — no one else has this session context mechanism
- **Canvas visual layer** — unique in the LLM Wiki category
- **/save conversation** — filing chat → wiki is a distinct workflow
- **Marketplace polish** — best install experience in category
- **Community distribution** (avalonreset-pro)

The ecosystem is maturing fast. Tier 1 items (URL ingest, auto-commit, defuddle) should ship in v1.3.0 to stay ahead.

---

## Implementation Priority

```
v1.3.0 (quick wins):
  - URL ingestion (#1)
  - Auto-commit hook (#2)
  - defuddle integration (#3)

v1.4.0 (quality):
  - Delta tracking (#4)
  - Multi-depth query (#5)

v1.5.0 (expansion):
  - Vision ingest (#6)
  - /adopt command (#7)
  - Multi-agent compat (#9)

Future:
  - Productivity wrapper (#8)
  - Marp output (#10)
  - Memory MCP integration (#11)
```
