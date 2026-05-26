# WIKI.md — LLM Wiki Schema

> If you are using the agentic-knowledge-management plugin, the skills handle everything here automatically.
> This file is the reference document. Read it to understand how the system works.
> Based on Andrej Karpathy's LLM Wiki pattern.

---

## What This Is

You are maintaining a persistent, compounding wiki inside an Obsidian vault. You don't just answer questions. You build and maintain a structured knowledge base that gets richer with every source added and every question asked. The human curates sources and asks questions. You do all the writing, cross-referencing, filing, and maintenance.

The wiki is the product. Chat is just the interface.

The key difference from RAG: the wiki is a persistent artifact. Cross-references are already there. Contradictions have been flagged. Synthesis already reflects everything that was read. Knowledge compounds like interest.

---

## 0 — Bootstrap: First-Run Setup

On first run in any new project, execute these steps in order. Skip any step already done.

### 0.1 Check Obsidian Installation

```bash
# Linux: check flatpak first, then PATH
flatpak list 2>/dev/null | grep -i obsidian && echo "FOUND via flatpak" || \
which obsidian 2>/dev/null && echo "FOUND in PATH" || echo "NOT FOUND"

# macOS
ls /Applications/Obsidian.app 2>/dev/null && echo "FOUND" || echo "NOT FOUND"

# Windows (PowerShell)
Test-Path "$env:LOCALAPPDATA\Obsidian" && echo "FOUND" || echo "NOT FOUND"
```

If not installed:

```bash
# Linux (Flatpak)
flatpak install flathub md.obsidian.Obsidian

# macOS (Homebrew)
brew install --cask obsidian

# Windows (winget)
winget install Obsidian.Obsidian

# All platforms: https://obsidian.md/download
```

After installing: Obsidian > Manage Vaults > Open Folder as Vault > select vault directory.

If no package manager is available, tell the user: "Download Obsidian from https://obsidian.md — install it, create a vault, and tell me the path."

### 0.2 Vault Location

Ask for the vault path or use the default:

```
VAULT_PATH=~/Documents/Obsidian Vault
```

Verify: `ls "$VAULT_PATH/.obsidian" 2>/dev/null`

### 0.3 Install the Local REST API Plugin

Guide the user (you cannot do this programmatically):

1. Obsidian > Settings > Community Plugins > Turn off Restricted Mode
2. Browse > Search "Local REST API" > Install > Enable
3. Settings > Local REST API > Copy the API key
4. Plugin runs on `https://127.0.0.1:27124` (self-signed cert)

Test: `curl -sk -H "Authorization: Bearer <KEY>" https://127.0.0.1:27124/`

### 0.4 Configure MCP Server

**Option A: mcp-obsidian (REST API based, most popular)**

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "<KEY>",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

**Option B: MCPVault (filesystem based, no plugin needed)**

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "<VAULT_PATH>"]
}' --scope user
```

**Option C: Direct REST API via curl** — always works, no MCP needed. See Section 11.

Use `--scope user` so the vault is available across all projects.

**Verify:**

```bash
claude mcp list               # confirm server appears
claude mcp get obsidian-vault # confirm path is correct
```

In a Claude Code session, type `/mcp` to check connection status.

### 0.5 Recommended Plugins

Install via Settings > Community Plugins > Browse:

| Plugin | Why |
|--------|-----|
| **Dataview** | Query vault as a database. Powers dashboards. |
| **Templater** | Auto-populate frontmatter on note creation. |
| **Obsidian Git** | Auto-commit every 15 minutes. Protects against data loss. |
| **Iconize** | Visual folder icons. |
| **Minimal Theme** | Best dark theme for dense information display. |

Optional: Smart Connections (semantic search), QuickAdd (macros), Folder Notes (clickable folders).

Also install the **Obsidian Web Clipper** browser extension. It converts web articles to markdown and sends them to `.raw/` in one click. Available for Chrome, Firefox, and Safari.

---

## 1 — Architecture

```
vault/
├── .raw/                   # Layer 1: immutable source documents
│   ├── articles/
│   ├── transcripts/
│   ├── screenshots/
│   ├── data/
│   └── assets/
│
├── wiki/                   # Layer 2: LLM-generated knowledge base
│   ├── index.md            # master catalog of all wiki pages
│   ├── log.md              # chronological record of all operations
│   ├── hot.md              # hot cache: recent context summary (~500 words)
│   ├── overview.md         # executive summary of the entire wiki
│   ├── sources/            # one summary page per raw source
│   ├── entities/           # people, orgs, products, repos
│   │   └── _index.md
│   ├── concepts/           # ideas, patterns, frameworks
│   │   └── _index.md
│   ├── domains/            # top-level topic areas
│   │   └── _index.md
│   ├── comparisons/        # side-by-side analyses
│   ├── questions/          # filed answers to user queries
│   └── meta/               # dashboards, lint reports, conventions
│
├── _templates/             # Templater templates
├── _attachments/           # images and PDFs referenced by wiki pages
│
├── WIKI.md                 # Layer 3: this file
└── .obsidian/              # Obsidian config (auto-managed)
```

### Rules

- `.raw/` is read-only. Never modify source files.
- `wiki/` is yours. Create, update, rename, delete freely.
- Every wiki page has frontmatter. No exceptions.
- Wikilinks over paths. Use `[[Page Name]]` not `[text](path/to/file.md)`.
- Atomic notes. One concept per page. If it covers two things, split it.
- Update, don't duplicate. If a page exists, update it.

---

## 2 — Hot Cache

`wiki/hot.md` is a ~500-word summary of the most recent context. It exists so that other projects pointing at this vault can get recent context without crawling the full wiki.

Update hot.md after every ingest, after any significant query exchange, and at the end of every session.

Format:

```markdown
---
type: meta
title: "Hot Cache"
updated: 2026-04-07T14:30:00
---

# Recent Context

## Last Updated
2026-04-07 — Ingested 3 new YouTube transcripts

## Key Recent Facts
- [Most important recent takeaway]
- [Second most important]

## Recent Changes
- Created: [[New Page 1]], [[New Page 2]]
- Updated: [[Existing Page]] (added section on X)
- Flagged: Contradiction between [[Page A]] and [[Page B]] on topic Y

## Active Threads
- User is currently researching [topic]
- Open question: [thing still being investigated]
```

Keep it under 500 words. It is a cache, not a journal. Overwrite it completely each time.

---

## 3 — Frontmatter Schema

Every wiki page starts with flat YAML frontmatter. No nested objects. Obsidian's Properties UI doesn't support them.

### Universal fields (every page):

```yaml
---
type: <source|entity|concept|domain|comparison|question|overview|meta>
title: "Human-Readable Title"
created: 2026-04-07
updated: 2026-04-07
tags:
  - <domain-tag>
  - <type-tag>
status: <seed|developing|mature|evergreen>
related:
  - "[[Other Page]]"
sources:
  - "[[.raw/articles/source-file.md]]"
---
```

### Type-specific additions:

**source**: `source_type`, `author`, `date_published`, `url`, `confidence` (high|medium|low), `key_claims` (list)

**entity**: `entity_type` (person|organization|product|repository|place), `role`, `first_mentioned`

**concept**: `complexity` (basic|intermediate|advanced), `domain`, `aliases` (list)

**comparison**: `subjects` (list of wikilinks), `dimensions` (list), `verdict` (one line)

**question**: `question` (the original query), `answer_quality` (draft|solid|definitive)

---

## 4 — Operations

### 4.1 SCAFFOLD — First-Run Structure

Trigger: user describes what the vault is for.

1. Determine the wiki mode (see modes table below and full mode details in Section 4.1a).
2. Ask one question: "What is this vault for?"
3. Create full folder structure under `wiki/`.
4. Create a domain page + `_index.md` sub-index for each domain.
5. Create `wiki/overview.md`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`.
6. Create `_templates/` with templates for each note type.
7. Apply visual customization (Section 7). Create `.obsidian/snippets/vault-colors.css`.
8. Create vault CLAUDE.md (template in Section 4.1b).
9. Initialize git (Section 8).
10. Present the structure and ask: "Want to adjust anything before we start?"

**Mode selection:**

| User says | Best mode |
|-----------|----------|
| "my website", "sitemap", "content audit" | A: Website |
| "my repo", "codebase map", "architecture wiki" | B: GitHub |
| "my business", "project wiki", "competitive intel" | C: Business |
| "second brain", "goals", "journal", "my life" | D: Personal |
| "research topic", "papers", "deep dive" | E: Research |
| "book I'm reading", "course notes", "chapter tracker" | F: Book/Course |

You can combine modes. "GitHub repo + research on the AI approach" uses Mode B folders plus Mode E papers/ folder.

### 4.1a — The Six Wiki Modes

**Mode A: Website / Sitemap**

```
vault/
├── .raw/              # crawl exports, analytics, GSC data
├── wiki/
│   ├── pages/         # one note per URL
│   ├── structure/     # site architecture, nav hierarchy
│   ├── audits/        # content gaps, redirect needs
│   ├── keywords/      # keyword clusters, target page assignments
│   └── entities/      # brand, authors, topic hubs
```

Frontmatter for pages/: `url`, `status` (live|redirect|404|stub|no-index), `h1`, `meta_description`, `word_count`, `has_schema`, `indexed`, `canonical`, `internal_links_in`, `internal_links_out`, `last_crawled`

Key pages: `[[Site Overview]]`, `[[Navigation Structure]]`, `[[Content Gaps]]`, `[[Redirect Map]]`, `[[Keyword Clusters]]`

---

**Mode B: GitHub / Repository**

```
vault/
├── .raw/              # README, git log exports, code dumps
├── wiki/
│   ├── modules/       # one note per module / package / service
│   ├── components/    # reusable components
│   ├── decisions/     # Architecture Decision Records
│   ├── dependencies/  # external deps, versions, risk
│   └── flows/         # data flows, request paths, auth flows
```

Frontmatter for modules/: `path`, `status` (active|deprecated|experimental|planned), `language`, `purpose`, `maintainer`, `depends_on`, `used_by`, `linked_issues`

Key pages: `[[Architecture Overview]]`, `[[Data Flow]]`, `[[Tech Stack]]`, `[[Dependency Graph]]`, `[[Key Decisions]]`

---

**Mode C: Business / Project**

```
vault/
├── .raw/              # meeting transcripts, Slack exports, docs
├── wiki/
│   ├── stakeholders/  # people, companies, decision-makers
│   ├── decisions/     # key decisions with rationale and date
│   ├── deliverables/  # milestones, outputs, status
│   ├── intel/         # competitor analysis, market research
│   └── comms/         # synthesized meeting notes
```

Frontmatter for decisions/: `status` (active|pending|done|blocked|superseded), `priority` (1-5), `date`, `owner`, `due_date`, `context`

Key pages: `[[Project Overview]]`, `[[Stakeholder Map]]`, `[[Decision Log]]`, `[[Competitor Landscape]]`

---

**Mode D: Personal / Second Brain**

```
vault/
├── .raw/              # journal entries, articles, voice transcripts
├── wiki/
│   ├── goals/         # personal and professional goals
│   ├── learning/      # concepts being mastered
│   ├── people/        # relationships, shared context
│   ├── areas/         # life areas: health, finances, career
│   └── resources/     # books, courses, tools
├── _meta/
│   └── hot-cache.md   # ~500 words of active context
```

Frontmatter for goals/: `area` (health|career|finance|creative|relationships|growth), `priority`, `target_date`, `progress` (0-100)

Key pages: `[[North Star]]`, `[[Weekly Review Template]]`, `[[Annual Goals]]`

---

**Mode E: Research**

```
vault/
├── .raw/              # PDFs, web clips, raw notes
├── wiki/
│   ├── papers/        # paper summaries with key claims
│   ├── concepts/      # extracted concepts, models, frameworks
│   ├── entities/      # people, organizations, datasets
│   ├── thesis/        # evolving synthesis
│   └── gaps/          # open questions, contradictions
```

Frontmatter for papers/: `year`, `authors`, `venue`, `key_claim`, `methodology`, `contradicts`, `supports`

Key pages: `[[Research Overview]]`, `[[Key Claims Map]]`, `[[Open Questions]]`, `[[Methodology Comparison]]`

---

**Mode F: Book / Course**

```
vault/
├── .raw/              # chapter notes, highlights, exercises
├── wiki/
│   ├── characters/    # characters, personas, experts
│   ├── themes/        # major themes with evidence
│   ├── concepts/      # domain-specific terms
│   ├── timeline/      # structure, sequence, chapter map
│   └── synthesis/     # your own takeaways and applications
```

Frontmatter for concepts/: `source_chapters`, `first_appearance`

Key pages: `[[Book Overview]]`, `[[Theme Map]]`, `[[Character / Expert Index]]`, `[[My Takeaways]]`

### 4.1b — Vault CLAUDE.md Template

Create this in the vault root when scaffolding a new project vault:

```markdown
# [WIKI NAME] — LLM Wiki

Mode: [MODE A/B/C/D/E/F]
Purpose: [ONE SENTENCE]
Owner: [NAME]
Created: YYYY-MM-DD

## Structure

[PASTE THE FOLDER MAP FROM THE CHOSEN MODE]

## Conventions

- All notes use YAML frontmatter: type, status, created, updated, tags (minimum)
- Wikilinks use [[Note Name]] format — filenames are unique, no paths needed
- .raw/ contains source documents — never modify them
- wiki/index.md is the master catalog — update on every ingest
- wiki/log.md is append-only — new entries go at the TOP, never edit past entries

## Operations

- Ingest: drop source in .raw/, say "ingest [filename]"
- Query: ask any question — Claude reads index first, then drills in
- Lint: say "lint the wiki" to run a health check
```

### 4.2 INGEST — Single Source

Trigger: user drops a file into `.raw/` or pastes content.

1. Read the source completely.
2. Discuss key takeaways with the user. Skip if user says "just ingest it."
3. Create source summary in `wiki/sources/`.
4. Create or update entity pages for every person/org/product/repo mentioned.
5. Create or update concept pages for significant ideas.
6. Update relevant domain pages and their `_index.md` sub-indexes.
7. Update `wiki/overview.md` if the big picture changed.
8. Update `wiki/index.md`. Add entries for all new pages.
9. Update `wiki/hot.md` with this ingest's context.
10. Append to `wiki/log.md` (new entries at the TOP):
    ```markdown
    ## [2026-04-07] ingest | Source Title
    - Source: `.raw/articles/filename.md`
    - Summary: [[Source Title]]
    - Pages created: [[Page 1]], [[Page 2]]
    - Pages updated: [[Page 3]], [[Page 4]]
    - Key insight: One sentence on what is new.
    ```
11. Check for contradictions. Flag with `> [!contradiction]` callouts on both pages.

A single source typically touches 8-15 wiki pages.

### 4.3 INGEST — Batch Mode

Trigger: user drops multiple files or says "ingest all of these."

1. List all files to process. Confirm with user.
2. Process each source following the single ingest flow. Defer cross-referencing.
3. After all sources: cross-reference pass. Look for connections between new sources.
4. Update index, hot cache, and log once at the end, not per source.
5. Report: "Processed N sources. Created X pages, updated Y pages. Key connections: ..."

Batch ingest is less interactive. For 30+ sources, check in after every 10.

### 4.4 QUERY — Answering Questions

1. Read `wiki/hot.md` first. It may have the answer.
2. Read `wiki/index.md` to find relevant pages.
3. Read those pages (3-5 typically, 10+ is too many).
4. Synthesize the answer in chat. Cite with wikilinks.
5. Offer to file as a wiki page in `wiki/questions/`.
6. If the question reveals a gap: "I don't have enough on X. Want to find a source?"

### 4.5 LINT — Health Check

Trigger: user says "lint" or every 10-20 ingests.

Checks: orphan pages, dead links, stale claims, missing pages for mentioned concepts, missing cross-references, frontmatter gaps, empty sections.

Output: `wiki/meta/lint-report-YYYY-MM-DD.md`. Ask before auto-fixing.

---

## 5 — Index and Sub-Indexes

### wiki/index.md (Master)

```markdown
---
type: meta
title: "Wiki Index"
updated: 2026-04-07
---
# Wiki Index

## Domains
- [[Domain Name]] — description (N sources)

## Entities
- [[Entity Name]] — role (first: [[Source]])

## Concepts
- [[Concept Name]] — definition (status: developing)

## Sources
- [[Source Title]] — author, date, type

## Questions
- [[Question Title]] — answer summary
```

### Domain Sub-Indexes

Each domain folder gets a `_index.md` with a catalog of just that domain's pages.

```markdown
---
type: meta
title: "Entities Index"
updated: 2026-04-07
---
# Entities

## People
- [[Person Name]] — role, org

## Organizations
- [[Org Name]] — what they do
```

### wiki/log.md

Append-only. New entries go at the TOP. Each entry: `## [YYYY-MM-DD] operation | title`

Parse recent entries:
```bash
grep "^## \[" wiki/log.md | head -10
```

---

## 6 — Cross-Project Referencing

Any Claude Code project can read your wiki without duplicating context.

In another project's CLAUDE.md, add:

```markdown
## Wiki Knowledge Base
Path: ~/Documents/Obsidian Vault

When you need context not already in this project:
1. Read wiki/hot.md first (recent context, ~500 words)
2. If not enough, read wiki/index.md (full catalog)
3. If you need domain specifics, read wiki/<domain>/_index.md
4. Only then read individual wiki pages

Do NOT read the wiki for general coding questions, things already in this
project's context, or tasks unrelated to [your domain].
```

This keeps token usage low. Hot cache costs ~500 tokens. Index costs ~1000 tokens. Individual pages cost 100-300 tokens each.

---

## 7 — Visual Customization

Apply during scaffold. Create `.obsidian/snippets/vault-colors.css`:

```css
:root {
  --wiki-1: #4fc1ff;  --wiki-2: #c586c0;  --wiki-3: #dcdcaa;
  --wiki-4: #ce9178;  --wiki-5: #6a9955;  --wiki-6: #d16969;
  --wiki-7: #569cd6;
}

.nav-folder-title[data-path^="wiki/domains"]     { color: var(--wiki-1); }
.nav-folder-title[data-path^="wiki/entities"]    { color: var(--wiki-2); }
.nav-folder-title[data-path^="wiki/concepts"]    { color: var(--wiki-3); }
.nav-folder-title[data-path^="wiki/sources"]     { color: var(--wiki-4); }
.nav-folder-title[data-path^="wiki/questions"]   { color: var(--wiki-5); }
.nav-folder-title[data-path^="wiki/comparisons"] { color: var(--wiki-6); }
.nav-folder-title[data-path^="wiki/meta"]        { color: var(--wiki-7); }
.nav-folder-title[data-path=".raw"]              { color: #808080; opacity: 0.6; }

.callout[data-callout='contradiction'] { --callout-color: 209, 105, 105; --callout-icon: lucide-alert-triangle; }
.callout[data-callout='gap']           { --callout-color: 220, 220, 170; --callout-icon: lucide-help-circle; }
.callout[data-callout='key-insight']   { --callout-color: 79, 193, 255;  --callout-icon: lucide-lightbulb; }
.callout[data-callout='stale']         { --callout-color: 128, 128, 128; --callout-icon: lucide-clock; }
```

Enable: Settings > Appearance > CSS Snippets > refresh > toggle on.

### Graph View Groups

Set in Graph View settings:

| Query | Color |
|-------|-------|
| `path:wiki/domains` | Blue |
| `path:wiki/entities` | Purple |
| `path:wiki/concepts` | Yellow |
| `path:wiki/sources` | Orange |
| `path:wiki/questions` | Green |
| `path:.raw` | Gray (dimmed) |

---

## 8 — Git Setup

```bash
cd "$VAULT_PATH"
git init
cat > .gitignore << 'EOF'
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.smart-connections/
.obsidian-git-data
.trash/
.DS_Store
node_modules/
EOF
git add -A && git commit -m "Initial vault scaffold"
```

Enable Obsidian Git: Settings > Obsidian Git > Auto backup interval > 15 minutes.

---

## 9 — Dataview Dashboards

Create in `wiki/meta/dashboard.md` after scaffold:

````markdown
---
type: meta
title: "Dashboard"
---
# Wiki Dashboard

## Recent Activity
```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15
```

## Seed Pages (Need Development)
```dataview
LIST FROM "wiki" WHERE status = "seed" SORT updated ASC
```

## Entities Missing Sources
```dataview
LIST FROM "wiki/entities" WHERE !sources OR length(sources) = 0
```
````

---

## 10 — Context Window Management

Read the minimum needed:

- Read `hot.md` first. It may already have what you need.
- Read `index.md` second. Find relevant pages, don't scan everything.
- Read domain sub-indexes for focused lookups.
- Read only 3-5 pages per query. 10+ is too many.
- Use search for keyword lookups. Don't scan full pages looking for a word.
- Use PATCH for surgical edits. Never re-read and rewrite a whole file to change one field.
- Keep wiki pages short. 100-300 lines max. Split long pages.
- Don't paste wiki content into chat unless the user asks. Reference by wikilink.

---

## 11 — REST API Quick Reference

Set these before running any command:

```bash
API="https://127.0.0.1:27124"
KEY="your-api-key-here"
```

**Read a file:**
```bash
curl -sk -H "Authorization: Bearer $KEY" "$API/vault/wiki/index.md"
```

**Create or replace a file:**
```bash
curl -sk -X PUT \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: text/markdown" \
  --data-binary @file.md \
  "$API/vault/wiki/entities/Name.md"
```

**Append to a file:**
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: text/markdown" \
  --data "- New item" \
  "$API/vault/wiki/log.md"
```

**Patch a frontmatter field:**
```bash
curl -sk -X PATCH \
  -H "Authorization: Bearer $KEY" \
  -H "Operation: replace" -H "Target-Type: frontmatter" \
  -H "Target: status" -H "Content-Type: application/json" \
  --data '"mature"' \
  "$API/vault/wiki/concepts/Name.md"
```

**Append under a heading:**
```bash
curl -sk -X PATCH \
  -H "Authorization: Bearer $KEY" \
  -H "Operation: append" -H "Target-Type: heading" \
  -H "Target: Connections" -H "Content-Type: text/markdown" \
  --data "- [[New Page]]" \
  "$API/vault/wiki/entities/Name.md"
```

**Search:**
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  "$API/search/simple/?query=machine+learning"
```

**Dataview query:**
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
  --data 'TABLE status FROM "wiki" WHERE status = "seed"' \
  "$API/search/"
```

---

## 12 — Vault CLAUDE.md Template

When creating a wiki for a new project (not this plugin), create a CLAUDE.md at the vault root:

```markdown
# [WIKI NAME] — LLM Wiki

Mode: [MODE A/B/C/D/E/F]
Purpose: [ONE SENTENCE]
Owner: [NAME]
Created: YYYY-MM-DD

## Structure

[PASTE THE FOLDER MAP FROM THE CHOSEN MODE]

## Conventions

- All notes use YAML frontmatter: type, status, created, updated, tags (minimum)
- Wikilinks use [[Note Name]] format
- .raw/ contains source documents — never modify them
- wiki/index.md is the master catalog — update on every ingest
- wiki/log.md is append-only — new entries go at the TOP

## Operations

- Ingest: drop source in .raw/, say "ingest [filename]"
- Query: ask any question
- Lint: say "lint the wiki"
```

---

## 13 — Conventions

### Naming

- **Filenames**: Title Case with spaces (`Machine Learning.md`)
- **Folders**: lowercase with dashes (`wiki/data-models/`)
- **Tags**: lowercase, hierarchical (`#domain/architecture`)
- **Unique filenames** so wikilinks work without paths

### Writing Style

- Declarative, present tense. "X uses Y" not "X basically does Y."
- Link liberally. Every mention of a wiki page gets a wikilink.
- Cite sources: `(Source: [[Page]])`.
- Flag uncertainty: `> [!gap] This needs more evidence.`
- Flag contradictions: `> [!contradiction] [[Page A]] claims X, but [[Page B]] says Y.`

### Cross-referencing

When updating Page A to mention Page B, check if Page B should link back. Bidirectional links make the graph view useful.

---

## 14 — Canvas Maps

Create `.canvas` files for visual overviews:

```json
{
  "nodes": [
    {"id": "1", "type": "file", "file": "wiki/domains/Architecture.md",
     "x": 0, "y": 0, "width": 250, "height": 120, "color": "4"},
    {"id": "2", "type": "file", "file": "wiki/domains/APIs.md",
     "x": 300, "y": 0, "width": 250, "height": 120, "color": "5"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "1", "fromSide": "right",
     "toNode": "2", "toSide": "left", "toEnd": "arrow"}
  ]
}
```

Canvas node colors (Obsidian canvas color codes): 1=red, 2=orange, 3=yellow, 4=green, 5=cyan, 6=purple.
Note: these differ from the wiki graph CSS color scheme. See `skills/canvas/references/canvas-spec.md` for the full canvas color table.

Create a domain relationship canvas during scaffold. Update as the wiki grows.

---

## Summary

Your job as the LLM:
1. Set up the vault (once)
2. Scaffold wiki structure from user's domain description
3. Ingest sources: read, summarize, cross-reference, file
4. Maintain hot cache after every operation
5. Answer questions using index > relevant pages > synthesis
6. File good answers back into the wiki
7. Lint periodically: find and fix health issues
8. Never modify .raw/ sources
9. Always update index, sub-indexes, log, and hot cache
10. Always use frontmatter and wikilinks

The human's job: curate sources, ask good questions, think about what it means. Everything else is on you.

---

*Based on Andrej Karpathy's LLM Wiki pattern. Plugin: claude-obsidian by AgriciDaniel / AI Marketing Hub.*
