---
type: session
title: "claude-obsidian v1.2.0 Release Session"
created: 2026-04-07
updated: 2026-04-07
tags:
  - session
  - release
  - plugin
  - github
status: evergreen
related:
  - "[[getting-started]]"
  - "[[index]]"
  - "[[overview]]"
  - "[[LLM Wiki Pattern]]"
---

# claude-obsidian v1.2.0 Release Session

Full build, audit, polish, and community release of the claude-obsidian plugin + vault kit. Previously named `cosmic-brain`.

---

## What Was Built

### Phase 1 — Critical Fixes
- `marketplace.json`: version corrected `1.0.0→1.2.0`, owner metadata updated
- `main.canvas`: removed 5 broken file node references (gitignored files that don't exist for community users)
- `community-plugins.json`: deduplicated from 6→4 canonical entries: `[excalidraw, banners, calendar, thino]`

### Phase 2 — Vault Onboarding
- `wiki/getting-started.md`: new onboarding page inside the vault (3-step quick start, hot cache explanation, command reference, navigation links)
- `wiki/index.md`: Entities, Questions, Comparisons sections populated with existing seed pages
- `wiki/meta/dashboard.md`: Dataview queries fixed — was querying `answer_quality` and `confidence` fields that don't exist in seed pages; replaced with `status` and `updated`
- `CLAUDE.md`: placeholder text replaced with actual vault description
- `wiki/canvases/welcome.canvas`: CTA node added pointing to getting-started and `/wiki`

### Phase 3 — README + Docs
- README: complete pre-installed plugins table, CSS snippets section, Banner usage section, file structure updated
- `bin/setup-vault.sh`: success message now lists all 4 pre-installed plugins and 3 CSS snippets

### Phase 4 — PDF Install Guide
- `docs/install-guide.md`: full printable install guide (prerequisites, 3 install options, first steps, command reference, plugin guide, MCP setup, troubleshooting)
- `docs/install-guide.pdf`: 159KB, generated via `npx md-to-pdf`

### Phase 5 — Version Bump
- `plugin.json` and `marketplace.json` bumped to `1.2.0`

---

## Rename: cosmic-brain → claude-obsidian

Full project rename executed:
- GitHub repos renamed: `AgriciDaniel/cosmic-brain` → `AgriciDaniel/claude-obsidian` (public), `avalonreset-pro/cosmic-brain` → `avalonreset-pro/claude-obsidian` (private)
- Local directory: `~/cosmic-brain/` → `~/claude-obsidian/`
- All text references updated across 14 files via sed
- `wiki/meta/cosmic-brain-cover.gif` renamed to `wiki/meta/claude-obsidian-cover.gif`

---

## Legal & Security

### Security Audit
- No API keys, tokens, or secrets found in any tracked file
- No private keys or certificates
- All credential references in docs are placeholder values
- Excalidraw `main.js` correctly NOT tracked despite audit agent claiming otherwise

### Legal Fixes
- `LICENSE`: MIT license file created (was declared in plugin.json but file was missing)
- `ITS-Dataview-Cards.css` + `ITS-Image-Adjustments.css`: GPL-2.0 attribution headers added

### .gitignore Tightened
Added rules to prevent future accidental commits of: video files (`*.mkv`, `*.mp4`), transcripts, scratch canvases (`Untitled *.canvas`, `*Images.canvas`), and personal images in vault root.

---

## Visual / README

### GIFs and Images
- New Claude Obsidian branded assets added (16x9 cover GIF, 1x1 GIF, static PNGs)
- Compressed: `gif-cover-16x9.gif` 2.6MB→1.3MB (50%), `gif-1x1.gif` 2.6MB→848KB (68%) — via FFmpeg palette optimization, scaled to 960px/640px, 15fps, 128-color palette
- Example screenshots added: `image-example-graph-view.png`, `image-example-wiki-map-view.png`

### README Structure (top to bottom)
1. `claude-obsidian-gif-cover-16x9.gif` — header
2. Description text
3. `welcome-canvas.gif` — What It Does demo (full width)
4. Descriptive paragraphs
5. `image-example-graph-view.png` + `image-example-wiki-map-view.png` — side by side screenshots
6. Quick Start → Commands → Cross-Project → Six Modes → What Gets Created → MCP → Plugins → CSS Snippets → Banner → File Structure → AutoResearch → Seed Vault
7. `wiki-graph-grow.gif` + `workflow-loop.gif` — bottom of Seed Vault section

---

## Repository State

| Repo | Visibility | URL |
|------|-----------|-----|
| AgriciDaniel/claude-obsidian | Public | https://github.com/AgriciDaniel/claude-obsidian |
| avalonreset-pro/claude-obsidian | Private | https://github.com/avalonreset-pro/claude-obsidian |

Community install command: `claude plugin install github:AgriciDaniel/claude-obsidian`

Future updates: `git push origin main && git push community main`

---

## Key Decisions

- **Rename to claude-obsidian**: clearer branding, immediately communicates the Claude + Obsidian pairing
- **avalonreset-pro repo is private**: community members only, not public
- **Excalidraw main.js excluded from git**: 8MB downloaded by `setup-vault.sh` at setup time
- **Bundled plugin redistribution**: acceptable — all 4 plugins are publicly distributed through Obsidian's community plugin system
- **GIF compression strategy**: palette reduction (256→128 colors) + resolution scaling gives 50-68% savings with no visible quality loss at GitHub's rendering width
