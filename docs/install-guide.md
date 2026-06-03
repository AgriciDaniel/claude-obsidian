# Compound Vault: Install Guide

**Agent-maintained Markdown wiki for Codex + Obsidian**
Version 1.9.2 · public canonical: [github.com/AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)

> The GitHub repository still uses the historical `claude-obsidian` slug for continuity. The public project name is **Compound Vault**.

> **Optional: DragonScale Memory extension.** If you want flat extractive log folds, deterministic page addresses, semantic tiling lint, and boundary-first autoresearch topic selection, run `bash bin/setup-dragonscale.sh` after the base install. Extra prerequisites beyond the base: `flock` (standard on Linux; available via `util-linux` on macOS) and `python3` (for the tiling and boundary helpers). Optional: `ollama` with `nomic-embed-text` pulled if you want the semantic tiling lint (Mechanism 3 only; it no-ops gracefully when ollama or the model is unavailable). The boundary-first scorer (Mechanism 4) needs only `python3`, no ollama. See [`docs/dragonscale-guide.md`](./dragonscale-guide.md) for the user-facing guide, `wiki/concepts/DragonScale Memory.md` for the full spec, and `CHANGELOG.md` for what shipped in 1.6.0.

---

## What is Compound Vault?

Compound Vault is a Codex skill package and Obsidian-compatible vault scaffold that builds and maintains a persistent, compounding Markdown knowledge base. Every source you add gets processed into cross-referenced wiki pages. Every question you ask can pull from what has already been read. Knowledge compounds because the vault itself improves between sessions.

Built on Andrej Karpathy's LLM Wiki pattern.

---

## Prerequisites

| Tool | How to get it | Notes |
|------|--------------|-------|
| **Codex or compatible agent CLI** | Install from your agent provider | Used to run the skills and slash-command workflow |
| **Obsidian** | [obsidian.md](https://obsidian.md) | Free |
| **Git** | Pre-installed on most systems | For Option 1 |

---

## Installation

### Option 1: Clone as vault (recommended)

Full setup in under 2 minutes.

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
```

Then in Obsidian: **Manage Vaults → Open folder as vault → select the cloned folder**

Open Codex in the same folder and type `/wiki`.

### Option 2: Legacy Claude Code plugin install

The repository also contains legacy Claude Code plugin metadata. If you use Claude Code, plugin installation is a two-step process: add the marketplace catalog, then install the plugin from it.

```bash
# Step 1: add the marketplace
claude plugin marketplace add AgriciDaniel/claude-obsidian

# Step 2: install the plugin
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
```

Verify the install:
```bash
claude plugin list
```

In any compatible agent session: type `/wiki` and the agent walks you through vault setup.

### Option 3: Add to an existing vault

Copy `WIKI.md` from this repo into your vault root. Then paste into your agent:

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

Type `/wiki` in Codex or your compatible agent. The agent will:
- Detect your vault mode (website, GitHub, business, personal, research, or book/course)
- Create the folder structure and core wiki pages
- Set up `wiki/index.md`, `wiki/hot.md`, `wiki/log.md`, and `wiki/overview.md`

### 2. Drop your first source

Put any document into `.raw/`:
- PDFs, markdown files, transcripts, articles, URLs

Tell the agent: `ingest [filename]`

The agent reads the source and creates 8-15 cross-referenced wiki pages.

### 3. Ask questions

```
what do you know about [topic]?
```

The agent reads the hot cache, scans the index, drills into relevant pages, and gives a synthesized answer, citing specific wiki pages rather than training data.

---

## Commands Reference

| Command | What the agent does |
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
| `ITS-Image-Adjustments` | Fine-grained image sizing; append `\|100` to embeds |

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

MCP lets compatible agents read and write vault notes directly without copy-paste.

The examples below use Claude Code's MCP command syntax. Use the equivalent setup path for your agent runtime if it differs.

**Option A: REST API**

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

**Option B: Filesystem (no plugin needed)**

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
| `/wiki` says "not found" | Confirm the skills directory is linked or the legacy plugin is enabled. For Claude Code, check `claude plugin list`. |
| Graph colors reset after closing Obsidian | Open Graph view → gear → Color groups → re-add once. Permanent after that. |
| Excalidraw not loading | Run `bash bin/setup-vault.sh` to download `main.js` (8MB, not in git) |
| Dashboard shows no results | Install the **Dataview** plugin from Community Plugins |
| Hot cache not loading at session start | Check hooks: `claude hooks list`; SessionStart hook should be present |

---

## Cross-Project Use

Point any agent project at this vault. Add a short project instruction like this:

```markdown
## Wiki Knowledge Base
Path: ~/path/to/compound-vault

When you need context not in this project:
1. Read wiki/hot.md first (recent context cache)
2. If not enough, read wiki/index.md
3. If you need domain details, read the relevant wiki page

Do NOT read the wiki for general coding questions.
```

Your executive assistant, coding projects, and content workflows all draw from the same knowledge base.

---

## Support

- **GitHub (public canonical)**: [github.com/AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- **Issues**: [github.com/AgriciDaniel/claude-obsidian/issues](https://github.com/AgriciDaniel/claude-obsidian/issues)

---

*Built by [AgriciDaniel](https://github.com/AgriciDaniel)*
*Based on Andrej Karpathy's LLM Wiki pattern*
