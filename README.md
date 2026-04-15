
# claude-obsidian

<p align="center">
  <img src="wiki/meta/claude-obsidian-gif-cover-16x9.gif" alt="claude-obsidian" width="100%" />
</p>

[![GitHub stars](https://img.shields.io/github/stars/AgriciDaniel/claude-obsidian?style=flat&color=e8734a)](https://github.com/AgriciDaniel/claude-obsidian/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-8B5CF6)](https://code.claude.com/docs/en/discover-plugins)
[![Blog Post](https://img.shields.io/badge/Deep_Dive-Blog_Post-22c55e)](https://agricidaniel.com/blog/claude-obsidian-ai-second-brain)

Claude + Obsidian knowledge companion. A running notetaker that builds and maintains a persistent, compounding wiki vault. Every source you add gets integrated. Every question you ask pulls from everything that has been read. Knowledge compounds like interest.

Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). **10 skills. Zero manual filing. Multi-agent support.**

---

## What It Does
### [Youtube Demo](https://www.youtube.com/watch?v=a2hgayvr-H4)
<p align="center">
  <img src="wiki/meta/welcome-canvas.gif" alt="Welcome canvas. Visual demo board" width="96%" />
</p>

You drop sources. Claude reads them, extracts entities and concepts, updates cross-references, and files everything into a structured Obsidian vault. The wiki gets richer with every ingest.

You ask questions. Claude reads the hot cache (recent context), scans the index, drills into relevant pages, and synthesizes an answer. It cites specific wiki pages, not training data.

You lint. Claude finds orphans, dead links, stale claims, and missing cross-references. Your wiki stays healthy without manual cleanup.

At the end of every session, Claude updates a hot cache. The next session starts with full recent context, no recap needed.

<p align="center">
  <img src="wiki/meta/image-example-graph-view.png" alt="Graph view. Color-coded wiki nodes" width="48%" />
  <img src="wiki/meta/image-example-wiki-map-view.png" alt="Wiki Map canvas" width="48%" />
</p>

---

## Why claude-obsidian?

Most Obsidian AI plugins are chat interfaces - they answer questions about your existing notes. claude-obsidian is a knowledge engine - it creates, organizes, maintains, and evolves your notes autonomously.

| Capability | claude-obsidian | Smart Connections | Copilot |
|---|---|---|---|
| **Auto-organize notes** | Creates entities, concepts, cross-references | No | No |
| **Contradiction flagging** | `[!contradiction]` callouts with sources | No | No |
| **Session memory** | Hot cache persists between conversations | No | No |
| **Vault maintenance** | 8-category lint (orphans, dead links, gaps) | No | No |
| **Autonomous research** | 3-round web research with gap-filling | No | No |
| **Multi-model support** | Claude, Gemini, Codex, Cursor, Windsurf | Claude only | Multiple |
| **Visual canvas** | Via [claude-canvas](https://github.com/AgriciDaniel/claude-canvas) companion | No | No |
| **Query with citations** | Cites specific wiki pages | Cites similar notes | Cites notes |
| **Batch ingestion** | Parallel agents for multiple sources | No | No |
| **Open source** | MIT | MIT | Freemium |

> **Deep dive:** [I Turned Obsidian Into a Self-Organizing AI Brain](https://agricidaniel.com/blog/claude-obsidian-ai-second-brain) - full breakdown with data visualizations, market context, and workflow demos.

---

## Quick Start

### Option 1: Clone as vault (recommended: full setup in 2 minutes)

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
```

Open the folder in Obsidian: **Manage Vaults → Open folder as vault → select `claude-obsidian/`**

Open Claude Code in the same folder. Type `/wiki`.

> `setup-vault.sh` configures `graph.json` (filter + colors), `app.json` (excludes plugin dirs), `appearance.json` (enables CSS), and symlinks the `skills/` and `commands/` directories to `.claude/` so Claude Code discovers them. Run it once before the first Obsidian open. You get the fully pre-configured graph view, color scheme, and wiki structure out of the box.
>
> *Note on updates: If you run `git pull` later to get new skills, the symlinks in `.claude/` will automatically point to the updated files on macOS/Linux. If the links ever break, run `bash bin/sync-claude.sh` to recreate them without overwriting your Obsidian settings.*

---

### Option 2: Install as Claude Code plugin

Plugin installation is a two-step process in Claude Code. First add the marketplace catalog, then install the plugin from it.

```bash
# Step 1: add the marketplace
claude plugin marketplace add AgriciDaniel/claude-obsidian

# Step 2: install the plugin
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

In any Claude Code session: `/wiki`. Claude walks you through vault setup.

To check it worked:
```bash
claude plugin list
```

---

### Option 3: Add to an existing vault

Copy `WIKI.md` into your vault root. Paste into Claude:

```
Read WIKI.md in this project. Then:
1. Check if Obsidian is installed. If not, install it.
2. Check if the Local REST API plugin is running on port 27124.
3. Configure the MCP server.
4. Ask me ONE question: "What is this vault for?"
Then scaffold the full wiki structure.
```

---

## Commands

| You say | Claude does |
|---------|------------|
| `/wiki` | Setup check, scaffold, or continue where you left off |
| `ingest [file]` | Read source, create 8-15 wiki pages, update index and log |
| `ingest all of these` | Batch process multiple sources, then cross-reference |
| `what do you know about X?` | Read index > relevant pages > synthesize answer |
| `/save` | File the current conversation as a wiki note |
| `/save [name]` | Save with a specific title (skips the naming question) |
| `/autoresearch [topic]` | Run the autonomous research loop: search, fetch, synthesize, file |
| `/canvas` | Open or create the visual canvas, list zones and nodes |
| `/canvas add image [path]` | Add an image (URL or local path) to the canvas with auto-layout |
| `/canvas add text [content]` | Add a markdown text card to the canvas |
| `/canvas add pdf [path]` | Add a PDF document as a rendered preview node |
| `/canvas add note [page]` | Pin a wiki page as a linked card on the canvas |
| `/canvas zone [name]` | Add a new labeled zone to organize visual content |
| `/canvas from banana` | Capture recently generated images onto the canvas |
| `lint the wiki` | Health check: orphans, dead links, gaps, suggestions |
| `update hot cache` | Refresh hot.md with latest context summary |

> **Want more?** [claude-canvas](https://github.com/AgriciDaniel/claude-canvas) adds 12 templates, 6 layout algorithms, AI image generation, presentations, and full canvas orchestration. Install both — they complement each other.

---

## Cross-Project Power Move

Point any Claude Code project at this vault. Add to that project's `CLAUDE.md`:

```markdown
## Wiki Knowledge Base
Path: ~/path/to/vault

When you need context not already in this project:
1. Read wiki/hot.md first (recent context cache)
2. If not enough, read wiki/index.md
3. If you need domain details, read the relevant domain sub-index
4. Only then drill into specific wiki pages

Do NOT read the wiki for general coding questions or tasks unrelated to [domain].
```

Your executive assistant, coding projects, and content workflows all draw from the same knowledge base.

---

## Six Wiki Modes

| Mode | Use when |
|------|---------|
| A: Website | Sitemap, content audit, SEO wiki |
| B: GitHub | Codebase map, architecture wiki |
| C: Business | Project wiki, competitive intelligence |
| D: Personal | Second brain, goals, journal synthesis |
| E: Research | Papers, concepts, thesis |
| F: Book/Course | Chapter tracker, course notes |

Modes can be combined.

---

## What Gets Created

A typical scaffold creates:
- Folder structure for your chosen mode
- `wiki/index.md`: master catalog
- `wiki/log.md`: append-only operation log
- `wiki/hot.md`: recent context cache
- `wiki/overview.md`: executive summary
- `wiki/meta/dashboard.base`: Bases dashboard (primary, native Obsidian)
- `wiki/meta/dashboard.md`: Legacy Dataview dashboard (optional fallback)
- `_templates/`: Obsidian Templater templates for each note type
- `.obsidian/snippets/vault-colors.css`: color-coded file explorer
- Vault `CLAUDE.md`: auto-loaded project instructions

---

## MCP Setup (Optional)

MCP lets Claude read and write vault notes directly without copy-paste.

Option A (REST API based):
1. Install the Local REST API plugin in Obsidian
2. Copy your API key
3. Run:
```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "your-key",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

Option B (filesystem based, no plugin needed):
```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "/path/to/your/vault"]
}' --scope user
```

---

## Plugins

### Core Plugins (built into Obsidian: no install needed)

| Plugin | Purpose |
|--------|---------|
| **Bases** | Powers `wiki/meta/dashboard.base`: native database views. Available since Obsidian v1.9.10 (August 2025). **Replaces Dataview for the primary dashboard.** |
| **Properties** | Visual frontmatter editor |
| **Backlinks**, **Outline**, **Graph view** | Standard navigation |

### Pre-installed Community Plugins (ship with this vault)

Enable in **Settings → Community Plugins → enable**:

| Plugin | Purpose | Notes |
|--------|---------|-------|
| **Calendar** | Right-sidebar calendar with word count + task dots | Pre-installed |
| **Thino** | Quick memo capture panel | Pre-installed |
| **Excalidraw** | Freehand drawing canvas, annotate images | Pre-installed* |
| **Banners** | Notion-style header image via `banner:` frontmatter | Pre-installed |

\* Excalidraw `main.js` (8MB) is downloaded automatically by `setup-vault.sh`. It is not tracked in git.

### Also install from Community Plugins (not pre-installed)

| Plugin | Purpose |
|--------|---------|
| **Templater** | Auto-fills frontmatter from `_templates/` |
| **Obsidian Git** | Auto-commits vault every 15 minutes |
| **Dataview** *(optional/legacy)* | Only needed for the legacy `wiki/meta/dashboard.md` queries. The primary dashboard now uses Bases. |

Also install the **[Obsidian Web Clipper](https://obsidian.md/clipper)** browser extension. Sends web pages to `.raw/` in one click.

---

## CSS Snippets (auto-enabled by setup-vault.sh)

Three snippets ship with the vault and are enabled automatically:

| Snippet | Effect |
|---------|--------|
| `vault-colors` | Color-codes `wiki/` folders by type in the file explorer (blue = concepts, green = sources, purple = entities) |
| `ITS-Dataview-Cards` | Turns Dataview `TABLE` queries into visual card grids: use ` ```dataviewjs ` with `.cards` class |
| `ITS-Image-Adjustments` | Fine-grained image sizing in notes: append `\|100` to any image embed |

---

## Banner Plugin

Add to any wiki page frontmatter:

```yaml
banner: "_attachments/images/your-image.png"
banner_icon: "🧠"
```

The page renders a full-width header image in Obsidian. Works great for hub pages and overviews.

---

## File Structure

```
claude-obsidian/
├── .claude-plugin/
│   ├── plugin.json              # manifest
│   └── marketplace.json         # distribution
├── skills/
│   ├── wiki/                    # orchestrator + references (7 ref files)
│   ├── wiki-ingest/             # INGEST operation
│   ├── wiki-query/              # QUERY operation
│   ├── wiki-lint/               # LINT operation
│   ├── save/                    # /save: file conversations to wiki
│   ├── autoresearch/            # /autoresearch: autonomous research loop
│   │   └── references/
│   │       └── program.md       # configurable research objectives
│   └── canvas/                  # /canvas: visual layer (images, PDFs, notes)
│       └── references/
│           └── canvas-spec.md   # Obsidian canvas JSON format reference
├── agents/
│   ├── wiki-ingest.md           # parallel ingestion agent
│   └── wiki-lint.md             # health check agent
├── commands/
│   ├── wiki.md                  # /wiki bootstrap command
│   ├── save.md                  # /save command
│   ├── autoresearch.md          # /autoresearch command
│   └── canvas.md                # /canvas visual layer command
├── hooks/
│   └── hooks.json               # SessionStart + Stop hot cache hooks
├── _templates/                  # Obsidian Templater templates
├── wiki/
│   ├── Wiki Map.canvas          # visual hub, central graph node
│   ├── canvases/                # welcome.canvas + main.canvas (visual demos)
│   ├── getting-started.md       # onboarding walkthrough (inside the vault)
│   ├── concepts/                # seeded: LLM Wiki Pattern, Hot Cache, Compounding Knowledge
│   ├── entities/                # seeded: Andrej Karpathy
│   ├── sources/                 # populated by your first ingest
│   └── meta/
│       ├── dashboard.base       # Bases dashboard (primary)
│       └── dashboard.md         # Legacy Dataview dashboard (optional)
├── .raw/                        # source documents (hidden in Obsidian)
├── .obsidian/snippets/          # vault-colors.css (3-color scheme)
├── WIKI.md                      # full schema reference
├── CLAUDE.md                    # project instructions
└── README.md                    # this file
```

---

## AutoResearch: program.md

The `/autoresearch` command is configurable. Edit `skills/autoresearch/references/program.md` to control:

- What sources to prefer (academic, official docs, news)
- Confidence scoring rules
- Max rounds and max pages per session
- Domain-specific constraints

The default program works for general research. Override it for your domain. A medical researcher would add "prefer PubMed". A business analyst would add "focus on market data and filings".

---

## Seed Vault

This repo ships with a seeded vault. Open it in Obsidian and you'll see:

- `wiki/concepts/`: LLM Wiki Pattern, Hot Cache, Compounding Knowledge
- `wiki/entities/`: Andrej Karpathy
- `wiki/sources/`: empty until your first ingest
- `wiki/meta/dashboard.base`: Bases dashboard (works in any Obsidian v1.9.10+)
- `wiki/meta/dashboard.md`: Legacy Dataview dashboard (optional fallback)

The graph view will show a connected cluster of 5 pages. This is what the wiki looks like after one ingest. Add more sources and it grows from there.

<p align="center">
  <img src="wiki/meta/wiki-graph-grow.gif" alt="Knowledge graph growing" width="48%" />
  <img src="wiki/meta/workflow-loop.gif" alt="Workflow loop" width="48%" />
</p>

---

## Companion: claude-canvas

For the visual layer, [claude-canvas](https://github.com/AgriciDaniel/claude-canvas) adds AI-orchestrated canvas creation - knowledge graphs, presentations, flowcharts, mood boards with 12 templates and 6 layout algorithms. Auto-detects claude-obsidian vaults.

```bash
claude plugin install AgriciDaniel/claude-canvas
```

---

## Community

- [Blog post](https://agricidaniel.com/blog/claude-obsidian-ai-second-brain) - deep dive with competitor analysis, data charts, and workflow demos
- [AI Marketing Hub](https://www.skool.com/ai-marketing-hub) - 2,800+ members, free community
- [YouTube](https://www.youtube.com/@AgriciDaniel) - tutorials and demos
- [All open-source tools](https://github.com/AgriciDaniel) - claude-seo, claude-ads, claude-blog, and more

---

*Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Built by [Agrici Daniel](https://agricidaniel.com/about).*
