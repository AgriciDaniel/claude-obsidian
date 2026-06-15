---
type: raw-research
title: "Claude + Obsidian Ecosystem Research"
date: 2026-04-08
queries:
  - "claude obsidian plugin github 2025 2026"
  - "obsidian MCP server claude anthropic"
  - "claudesidian obsidian plugin github"
  - "obsidian smart connections copilot AI plugin"
  - "claude code obsidian workflow LLM wiki"
sources:
  - github.com
  - awesome.ecosyste.ms
  - obsidianstats.com
  - effortlessacademic.com
---

# Claude + Obsidian Ecosystem Research
> Researched: 2026-04-08 | Goal: survey the Claude + Obsidian ecosystem and identify strong patterns and prior art relevant to claude-obsidian.

---

## Summary

16+ active projects found combining Claude/AI with Obsidian. Organized into 4 categories:
1. **LLM Wiki Pattern plugins** (Claude Code skill-based, closest in approach)
2. **Native Obsidian plugins** (TypeScript, embedded UI)
3. **MCP servers** (bridge protocols)
4. **In-vault AI plugins** (traditional Obsidian community plugins)

---

## Category 1: LLM Wiki Pattern (Claude Code Plugins)

### AgriciDaniel/claude-obsidian (this project)
- URL: https://github.com/AgriciDaniel/claude-obsidian
- Version: 1.2.0
- Skills: /wiki, /wiki-ingest, /wiki-query, /wiki-lint, /save, /autoresearch, /canvas
- Approach: Hot cache + compounding wiki + Claude Code skills

### heyitsnoah/claudesidian
- URL: https://github.com/heyitsnoah/claudesidian
- Approach: Pre-configured Obsidian vault + PARA method
- Key features:
  - `/init-bootstrap` — interactive setup wizard that analyzes existing vault
  - Vault import: safely imports existing vault to `OLD_VAULT/`
  - Research public work to personalize context
  - Thinking Mode vs Writing Mode distinction
  - Pre-configured commands: `/thinking-partner`, `/daily-review`, `/research-assistant`, `/weekly-synthesis`, `/inbox-processor`
  - PARA folder structure: 00_Inbox, 01_Projects, 02_Areas, 03_Resources, 04_Archive
  - Optional: Gemini Vision for image/video, Firecrawl for web research
- Stars: Not tracked (pre-release kit)

### rvk7895/llm-knowledge-bases
- URL: https://github.com/rvk7895/llm-knowledge-bases
- Install: `/plugin marketplace add rvk7895/llm-knowledge-bases`
- Key features:
  - 3-depth query system: Quick (indexes only), Standard (wiki + web search), Deep (multi-agent parallel web search)
  - `/research` and `/research-deep` — parallel agents for deep research
  - Output formats: Markdown reports, Marp slides, matplotlib charts → `output/`
  - X/Twitter ingestion via Smaug tool
  - `/kb-init`, `/kb compile`, `/kb query`, `/kb lint`, `/kb evolve`
- Attribution: Built on Karpathy pattern + Weizhena's Deep Research skills

### ekadetov/llm-wiki
- URL: https://github.com/ekadetov/llm-wiki
- Key features:
  - qmd hybrid search (BM25 + vector) — auto-installed via SessionStart hook
  - Multi-wiki support: `/llm-wiki:wiki init <topic-name>` creates isolated wiki
  - URL ingestion: pass `https://` URLs directly to ingest command
  - Auto-commit on every ingest via git
  - Marp presentation output
  - `/llm-wiki:wiki remove <topic>` — clean removal
  - Prerequisite: Node 18+, Git, Obsidian vault at `~/ObsidianVault/`

### Ar9av/obsidian-wiki
- URL: https://github.com/Ar9av/obsidian-wiki
- Key features:
  - Multi-agent compatibility: Claude Code, Cursor, Windsurf, Codex, Gemini CLI, OpenClaw, GitHub Copilot
  - `setup.sh` auto-configures all agents simultaneously via symlinks
  - Delta tracking manifest (`.manifest.json`) — only ingests new/changed files
  - Vision support: ingest images, screenshots, whiteboard photos (requires vision model)
  - 4-stage pipeline: Ingest → Extract → Resolve → Schema
  - Schema emerges from sources (not fixed upfront)
  - Each page gets `summary:` frontmatter for preview without opening
  - Multi-format: PDFs (with page ranges), JSONL, conversation exports, transcripts

### ballred/obsidian-claude-pkm
- URL: https://github.com/ballred/obsidian-claude-pkm
- Key features:
  - Goal cascade: 3-Year Vision → Yearly Goals → Projects → Monthly Goals → Weekly Review → Daily Tasks
  - `/daily`, `/weekly`, `/monthly` review skills
  - `/project new` — creates project linked to a goal
  - `/adopt` command — imports existing vault structure, detects PARA/Zettelkasten/LYT, maps folders
  - 4 specialized agents: goal-aligner, weekly-reviewer, note-organizer, inbox-processor
  - `memory: project` for cross-session agent learning
  - Auto-commit via PostToolUse hook on every file write/edit
  - Productivity Coach output style
  - Path-specific rules loaded contextually
  - Zero dependencies (bash + markdown only)
  - `/onboard` — personalized vault setup (name, review day, goal areas)
  - Version: 3.1

### kepano/obsidian-skills
- URL: https://github.com/kepano/obsidian-skills
- Author: **Linus Kepano** (creator of Obsidian + Minimal theme)
- Install: `/plugin marketplace add kepano/obsidian-skills`
- Key skills:
  - `obsidian-markdown` — full Obsidian Flavored Markdown (callouts, embeds, wikilinks, properties)
  - `obsidian-bases` — Obsidian Bases (.base files, views, filters, formulas)
  - `json-canvas` — JSON Canvas spec for .canvas files
  - `obsidian-cli` — vault management via Obsidian CLI
  - `defuddle` — extract clean markdown from web pages (removes clutter, saves tokens)
- Multi-platform: Claude Code, Codex CLI, OpenCode

### ussumant/llm-wiki-compiler
- URL: https://github.com/ussumant/llm-wiki-compiler
- Approach: Single-purpose Claude Code plugin — compiles markdown files into topic wiki
- Key features: Topic-based compilation, implements Karpathy pattern in minimal form

---

## Category 2: Native Obsidian Plugins (Embedded UI)

### YishenTu/claudian
- URL: https://github.com/YishenTu/claudian
- Approach: Embeds Claude Code/Codex CLI directly inside Obsidian as sidebar chat
- Key features:
  - **Inline Edit** — select text + hotkey → word-level diff preview → apply
  - **Plan Mode** (Shift+Tab) — agent plans before implementing
  - **@mention** — reference vault files, subagents, MCP servers, external files
  - **Slash commands & Skills** — user- and vault-level skill scopes
  - **Instruction Mode (#)** — add instructions from chat input
  - **MCP Servers** — stdio, SSE, HTTP connections
  - **Multi-tab conversations** — fork, resume, compact
  - Privacy: no telemetry, stores in vault/.claudian/
  - Requires BRAT or manual install (not yet in community store)

### ProfSynapse/claudesidian-mcp (now: Nexus)
- URL: https://github.com/ProfSynapse/claudesidian-mcp
- Current name: Nexus MCP for Obsidian
- Approach: Full Obsidian plugin with both native chat AND MCP bridge
- Key features:
  - Native chat inside Obsidian (any provider via settings)
  - MCP bridge for: Claude Desktop, Claude Code, Codex CLI, Gemini CLI, Cursor, Cline
  - **Workspace memory** — persistent context across sessions (JSONL, Obsidian Sync compatible)
  - **Task management** — projects, tasks, blockers, dependencies
  - **Semantic search** — search notes + past conversations by meaning
  - **Inline editing** — edit selected text in notes
  - PDF + audio → Markdown conversion (right-click or auto-on-add)
  - Web page → Markdown/PNG/PDF capture
  - Merge PDFs, concat markdown, mix audio tracks
  - Mobile support (native chat)
  - Storage: JSONL files in `.obsidian/plugins/nexus/data/` (included in Obsidian Sync)
  - Two-tool architecture (see docs)

---

## Category 3: MCP Servers

### jacksteamdev/obsidian-mcp-tools
- URL: https://github.com/jacksteamdev/obsidian-mcp-tools
- Key features:
  - Vault access via Local REST API plugin
  - **Semantic search** via Smart Connections integration
  - **Templater execution** — run templates from AI with dynamic params
  - SLSA Level 3 binary attestation (reproducible, signed builds)
  - Requires: Local REST API + Smart Connections + Templater
  - Status: Seeking maintainers (open until Sep 2025)

### YuNaga224/obsidian-memory-mcp
- URL: https://github.com/YuNaga224/obsidian-memory-mcp
- Key features:
  - Fork of Anthropic's official memory MCP server
  - Stores AI memories as individual Markdown files (not JSON)
  - Uses `[[link]]` syntax → entities appear in Obsidian graph view
  - YAML frontmatter: entityType, created, updated
  - Sections: Observations + Relations per entity
  - Tools: create_entities, create_relations, add_observations, search_nodes, read_graph
  - Configure via MEMORY_DIR env var pointing to vault folder

### iansinnott/obsidian-claude-code-mcp
- URL: https://github.com/iansinnott/obsidian-claude-code-mcp
- Key features: WebSocket-based MCP, auto-discovers Obsidian vaults via Claude Code

### administrativetrick/obsidian-mcp
- URL: https://github.com/administrativetrick/obsidian-mcp
- Minimal MCP server for Claude Desktop vault access

### dbmcco/obsidian-mcp
- URL: https://github.com/dbmcco/obsidian-mcp
- TDD-developed MCP server for Obsidian

### MarkusPfundstein/mcp-obsidian
- URL: https://github.com/MarkusPfundstein/mcp-obsidian
- Interacts via Obsidian REST API community plugin

---

## Category 4: Traditional In-Vault AI Plugins (Stars)

| Plugin | Stars | Feature |
|--------|-------|---------|
| logancyang/obsidian-copilot | 5,776 | Multi-provider AI chat with vault context |
| brianpetro/obsidian-smart-connections | 4,357 | Vector embeddings, semantic search, local models, Claude support |
| nhaouari/obsidian-textgenerator-plugin | 1,837 | Text generation |
| bramses/chatgpt-md | 1,229 | Chat in markdown |
| pfrankov/obsidian-local-gpt | 569 | Local LLM integration |
| infiolab/infio-copilot | unknown | Cursor-inspired: autocomplete, inline edit, workspaces, Insights, dataview queries |
| solderneer/obsidian-ai-tools | 272 | Semantic search via Supabase + OpenAI |

---

## Ecosystem Stats (danielrosehill/Awesome-Obsidian-AI-Tools)
- 86 plugins total, 19,737 combined stars
- 17 categories
- Last updated: 2025-12-15

---

## Key Design Patterns Across Ecosystem

### Pattern 1: Delta Tracking
Most mature projects (Ar9av/obsidian-wiki) use a `.manifest.json` to track ingested sources — hash, timestamp, which pages produced. Re-ingest only processes changed/new files. Claude-obsidian currently has no delta tracking.

### Pattern 2: Multi-Depth Queries
rvk7895 implements 3 tiers: Quick (index only), Standard (wiki + web), Deep (parallel agents). Current claude-obsidian has one depth level in wiki-query.

### Pattern 3: Goal Cascade Integration
ballred's project connects personal productivity (daily/weekly reviews) with the knowledge base. No PKM projects do this today in claude-obsidian.

### Pattern 4: Auto-Commit Hooks
ballred uses PostToolUse hooks for auto-git-commit on every file change. This keeps the vault in version control automatically.

### Pattern 5: Multi-Agent Compatibility
Ar9av's setup.sh deploys skills to Claude Code + Cursor + Windsurf + Codex + Gemini CLI simultaneously. claude-obsidian is Claude Code only.

### Pattern 6: Hybrid Search
ekadetov uses qmd (BM25 + vector) instead of simple keyword/index search. Big quality improvement for large vaults.

### Pattern 7: Emerging Schema
Ar9av's wiki has no fixed structure upfront — it emerges from the content. Claude-obsidian has a predefined structure.

### Pattern 8: Vision Ingestion
Ar9av supports images/screenshots/whiteboards as ingestable sources (vision model required). Claude-obsidian has no image ingestion.

### Pattern 9: Output Formats
rvk7895 and ekadetov export to Marp slides and matplotlib charts. Claude-obsidian outputs only Markdown.

### Pattern 10: Vault Adoption
Both claudesidian and ballred/pkm can be adopted onto existing vaults without destroying structure. Claude-obsidian requires starting fresh.

---

## Notable Quotes / Signal

From rvk7895 README:
> "The LLM owns the wiki. You rarely edit it manually — just explore in Obsidian and keep feeding it raw data."

From Ar9av README:
> "You write skills once, every agent can use them."
> "The wiki schema isn't fixed upfront. It emerges from your sources."

From kepano/obsidian-skills (Obsidian creator):
> Uses exact Agent Skills specification format — validates that AgriciDaniel's approach is on spec.

---

## Sources

- https://github.com/AgriciDaniel/claude-obsidian
- https://github.com/heyitsnoah/claudesidian
- https://github.com/ProfSynapse/claudesidian-mcp
- https://github.com/YishenTu/claudian
- https://github.com/kepano/obsidian-skills
- https://github.com/danielrosehill/Awesome-Obsidian-AI-Tools
- https://github.com/Ar9av/obsidian-wiki
- https://github.com/ekadetov/llm-wiki
- https://github.com/rvk7895/llm-knowledge-bases
- https://github.com/jacksteamdev/obsidian-mcp-tools
- https://github.com/ballred/obsidian-claude-pkm
- https://github.com/infiolab/infio-copilot
- https://github.com/YuNaga224/obsidian-memory-mcp
- https://github.com/iansinnott/obsidian-claude-code-mcp
- https://github.com/ussumant/llm-wiki-compiler
- https://github.com/logancyang/obsidian-copilot
- https://github.com/brianpetro/obsidian-smart-connections
- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
