# claude-obsidian — Install Guide

**Claude + Obsidian Knowledge Companion**
Version 1.6.0 · [github.com/AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)

> **Optional: DragonScale Memory extension.** If you want flat extractive log folds, deterministic page addresses, semantic tiling lint, and boundary-first autoresearch topic selection, run `bash bin/setup-dragonscale.sh` after the base install. Extra prerequisites beyond the base: `python3` (for the address allocator, tiling, and boundary helpers). Optional: `ollama` with `nomic-embed-text` pulled if you want the semantic tiling lint (Mechanism 3 only; it no-ops gracefully when ollama or the model is unavailable). The boundary-first scorer (Mechanism 4) needs only `python3`, no ollama. See [`docs/dragonscale-guide.md`](./dragonscale-guide.md) for the user-facing guide, `wiki/concepts/DragonScale Memory.md` for the full spec, and `CHANGELOG.md` for what shipped in 1.6.0.

---

## What is claude-obsidian?

claude-obsidian is a Claude Code plugin + Obsidian vault that builds and maintains a persistent, compounding knowledge base. Every source you add gets processed into cross-referenced wiki pages. Every question you ask pulls from everything that has been read. Knowledge compounds like interest.

Built on Andrej Karpathy's LLM Wiki pattern.

---

## Prerequisites

| Tool | How to get it | Notes |
|------|--------------|-------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | Free tier available |
| **Obsidian** | [obsidian.md](https://obsidian.md) | Free |
| **Git** | Pre-installed on most systems | For Option 1 |

---

## Installation

### Option 1 — Clone as vault (recommended)

Full setup in under 2 minutes.

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
```

Then in Obsidian: **Manage Vaults → Open folder as vault → select `claude-obsidian/`**

Open Claude Code in the same folder and type `/wiki`.

### Option 2: Install as Claude Code plugin

Plugin installation in Claude Code is a two-step process. First add the marketplace catalog, then install the plugin from it.

```bash
# Step 1: add the marketplace
claude plugin marketplace add AgriciDaniel/claude-obsidian

# Step 2: install the plugin
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

Verify the install:
```bash
claude plugin list
```

In any Claude Code session: type `/wiki` and Claude walks you through vault setup.

### Option 3 — Add to an existing vault

Copy `WIKI.md` from this repo into your vault root. Then paste into Claude:

```
Read WIKI.md in this project. Then:
1. Check if Obsidian is installed. If not, install it.
2. Check if the Local REST API plugin is running on port 27124.
3. Configure the MCP server.
4. Ask me ONE question: "What is this vault for?"
Then scaffold the full wiki structure.
```

---

## First Steps

### 1. Scaffold the vault

Type `/wiki` in Claude Code. Claude will:
- Detect your vault mode (website, GitHub, business, personal, research, or book/course)
- Create the folder structure and core wiki pages
- Set up `wiki/index.md`, `wiki/hot.md`, `wiki/log.md`, and `wiki/overview.md`

### 2. Drop your first source

Put any document into `.raw/`:
- PDFs, markdown files, transcripts, articles, URLs

Tell Claude: `ingest [filename]`

Claude reads the source and creates 8–15 cross-referenced wiki pages.

### 3. Ask questions

```
what do you know about [topic]?
```

Claude reads the hot cache, scans the index, drills into relevant pages, and gives a synthesized answer — citing specific wiki pages, not training data.

---

## Commands Reference

| Command | What Claude does |
|---------|-----------------|
| `/wiki` | Setup check, scaffold, or continue where you left off |
| `ingest [file]` | Read source, create 8–15 wiki pages, update index and log |
| `ingest all of these` | Batch process multiple sources, then cross-reference |
| `what do you know about X?` | Read index → relevant pages → synthesize answer |
| `/save` | File the current conversation as a wiki note |
| `/save [name]` | Save with a specific title |
| `/autoresearch [topic]` | Autonomous research loop: search, fetch, synthesize, file |
| `/canvas` | Open or create a visual canvas |
| `/canvas add image [path]` | Add an image to the canvas |
| `/canvas add text [content]` | Add a markdown text card |
| `/canvas add pdf [path]` | Add a PDF document |
| `/canvas add note [page]` | Pin a wiki page as a linked card |
| `lint the wiki` | Health check: orphans, dead links, gaps |
| `update hot cache` | Refresh `hot.md` with latest context summary |

---

## Plugins (pre-installed)

Enable in **Settings → Community Plugins**:

| Plugin | Purpose |
|--------|---------|
| **Calendar** | Right-sidebar calendar with word count and task dots |
| **Thino** | Quick memo capture panel |
| **Excalidraw** | Freehand drawing, image annotation |
| **Banners** | Header images via `banner:` frontmatter |

Also install from Community Plugins:

| Plugin | Purpose |
|--------|---------|
| **Dataview** | Powers the dashboard queries |
| **Templater** | Auto-fills frontmatter from templates |
| **Obsidian Git** | Auto-commits vault every 15 minutes |

---

## CSS Snippets

Three snippets are auto-enabled by `setup-vault.sh`:

| Snippet | Effect |
|---------|--------|
| `vault-colors` | Color-codes wiki folders in the file explorer |
| `ITS-Dataview-Cards` | Turns Dataview queries into visual card grids |
| `ITS-Image-Adjustments` | Fine-grained image sizing — append `\|100` to embeds |

---

## Six Wiki Modes

| Mode | Use when |
|------|---------|
| **A: Website** | Sitemap, content audit, SEO wiki |
| **B: GitHub** | Codebase map, architecture wiki |
| **C: Business** | Project wiki, competitive intelligence |
| **D: Personal** | Second brain, goals, journal synthesis |
| **E: Research** | Papers, concepts, thesis |
| **F: Book/Course** | Chapter tracker, course notes |

Modes can be combined.

---

## MCP Setup (Optional)

MCP lets Claude read and write vault notes directly without copy-paste.

**Option A — REST API:**

1. Install the **Local REST API** plugin in Obsidian
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

**Option B — Filesystem (no plugin needed):**

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "/path/to/your/vault"]
}' --scope user
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `/wiki` says "not found" | Make sure `claude-obsidian` plugin is enabled: `claude plugin list` |
| Graph colors reset after closing Obsidian | Open Graph view → gear → Color groups → re-add once. Permanent after that. |
| Excalidraw not loading | Run `bash bin/setup-vault.sh` to download `main.js` (8MB, not in git) |
| Dashboard shows no results | Install the **Dataview** plugin from Community Plugins |
| Hot cache not loading at session start | Check hooks: `claude hooks list` — SessionStart hook should be present |

---

## Cross-Project Power Move

Point any Claude Code project at this vault. Add to that project's `CLAUDE.md`:

```markdown
## Wiki Knowledge Base
Path: ~/path/to/claude-obsidian

When you need context not in this project:
1. Read wiki/hot.md first (recent context cache)
2. If not enough, read wiki/index.md
3. If you need domain details, read the relevant wiki page

Do NOT read the wiki for general coding questions.
```

Your executive assistant, coding projects, and content workflows all draw from the same knowledge base.

---

## Support

- **GitHub**: [github.com/AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- **Issues**: [github.com/AgriciDaniel/claude-obsidian/issues](https://github.com/AgriciDaniel/claude-obsidian/issues)
- **Community**: [AI Marketing Hub on Skool](https://skool.com)

---

*Built by [AgriciDaniel](https://github.com/AgriciDaniel) / AI Marketing Hub*
*Based on Andrej Karpathy's LLM Wiki pattern*
