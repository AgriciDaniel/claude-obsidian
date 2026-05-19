# Obsidian Setup

---

## Install Obsidian

### Linux (Flatpak: recommended)

Check if installed:
```bash
flatpak list 2>/dev/null | grep -i obsidian && echo "FOUND via flatpak" || \
which obsidian 2>/dev/null && echo "FOUND in PATH" || echo "NOT FOUND"
```

Install if not found:
```bash
flatpak install flathub md.obsidian.Obsidian
```

### macOS

```bash
ls /Applications/Obsidian.app 2>/dev/null && echo "FOUND" || brew install --cask obsidian
```

### Windows

```powershell
Test-Path "$env:LOCALAPPDATA\Obsidian" && echo "FOUND" || winget install Obsidian.Obsidian
```

### All platforms: direct download

https://obsidian.md/download

---

## Open the Vault

After installing: Obsidian > Manage Vaults > Open Folder as Vault > select your vault directory.

---

## Core Plugins (Built-in: No Install Required)

These ship with Obsidian. Enable them in Settings > Core Plugins:

| Plugin | Purpose |
|--------|---------|
| **Bases** | Native database-like views for `.base` files. Powers `wiki/meta/dashboard.base`. Available since Obsidian v1.9.10 (August 2025). **Replaces Dataview for most wiki use cases.** |
| **Properties** | Visual frontmatter editor. Always enabled. |
| **Backlinks** | Outgoing/incoming links pane. |
| **Outline** | Document heading navigation. |

## Recommended Community Plugins

Install via Settings > Community Plugins > Turn off Restricted Mode > Browse.

| Plugin | Purpose |
|--------|---------|
| **Templater** | Auto-populate frontmatter on note creation from `_templates/`. |
| **Obsidian Git** | Auto-commit every 15 minutes. Protects against bad writes. |
| **Calendar** | Right-sidebar calendar with word count, task, and link indicators. Pre-installed in this vault via `.obsidian/plugins/calendar/`. |
| **Thino** | Quick memo capture panel in right sidebar. Pre-installed via `.obsidian/plugins/thino/`. |
| **Iconize** | Visual folder icons for navigation. |
| **Minimal Theme** | Best dark theme for dense information display. |
| **Dataview** *(optional/legacy)* | Only needed if you're on Obsidian < 1.9.10 or want to use the legacy `dashboard.md` queries. The primary dashboard now uses Bases. |

**Calendar and Thino are pre-installed**. They ship with this vault. Enable them in Settings → Community Plugins → toggle on. No download needed.

If installing in a different vault: download `main.js` + `manifest.json` from their GitHub releases into `.obsidian/plugins/calendar/` and `.obsidian/plugins/thino/` respectively.

Optional additions:
- **Smart Connections**: semantic search across all notes
- **QuickAdd**: macros for fast note creation
- **Folder Notes**: click a folder to open an overview note

---

## Web Clipper

The Obsidian Web Clipper browser extension converts web articles to markdown and sends them to `raw/` in one click.

Install for Chrome, Firefox, or Safari from the Obsidian website.

Set the default folder to `raw/` in the extension settings.

---

## After Installing Plugins

1. Enable Bases: Settings > Core Plugins > toggle on (already on by default in Obsidian v1.9.10+)
2. Enable Templater: Settings > Templater > set template folder to `_templates`
3. Enable Obsidian Git: Settings > Obsidian Git > Auto backup interval: 15 minutes
4. Enable the CSS snippet: Settings > Appearance > CSS Snippets > toggle on `vault-colors`
5. *(Optional)* Enable Dataview only if you want the legacy `wiki/meta/dashboard.md` queries to work alongside the primary `dashboard.base`
