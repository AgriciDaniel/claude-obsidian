# Visual Customization

Apply during scaffold. This makes the file explorer color-coded by folder type and adds custom callout styles.

---

## CSS Snippet

Create this file at `.obsidian/snippets/vault-colors.css` inside the vault:

```css
:root {
  --wiki-1: #4fc1ff;
  --wiki-2: #c586c0;
  --wiki-3: #dcdcaa;
  --wiki-4: #ce9178;
  --wiki-5: #6a9955;
  --wiki-6: #d16969;
  --wiki-7: #569cd6;
}

/* Folder colors in file explorer */
.nav-folder-title[data-path^="wiki/domains"]     { color: var(--wiki-1); }
.nav-folder-title[data-path^="wiki/entities"]    { color: var(--wiki-2); }
.nav-folder-title[data-path^="wiki/concepts"]    { color: var(--wiki-3); }
.nav-folder-title[data-path^="wiki/sources"]     { color: var(--wiki-4); }
.nav-folder-title[data-path^="wiki/questions"]   { color: var(--wiki-5); }
.nav-folder-title[data-path^="wiki/comparisons"] { color: var(--wiki-6); }
.nav-folder-title[data-path^="wiki/meta"]        { color: var(--wiki-7); }
.nav-folder-title[data-path="raw"]               { color: #808080; opacity: 0.6; }

/* Custom callouts */
.callout[data-callout='contradiction'] {
  --callout-color: 209, 105, 105;
  --callout-icon: lucide-alert-triangle;
}
.callout[data-callout='gap'] {
  --callout-color: 220, 220, 170;
  --callout-icon: lucide-help-circle;
}
.callout[data-callout='key-insight'] {
  --callout-color: 79, 193, 255;
  --callout-icon: lucide-lightbulb;
}
.callout[data-callout='stale'] {
  --callout-color: 128, 128, 128;
  --callout-icon: lucide-clock;
}
```

---

## Enable the Snippet

Tell the user: Settings > Appearance > CSS Snippets > open folder > paste the file > click the refresh icon > toggle it on.

---

## Graph View Groups

Guide the user to set these in Graph View settings (click the settings icon in the graph view):

| Query | Color |
|-------|-------|
| `path:wiki/domains` | Blue (`#4fc1ff`) |
| `path:wiki/entities` | Purple (`#c586c0`) |
| `path:wiki/concepts` | Yellow (`#dcdcaa`) |
| `path:wiki/sources` | Orange (`#ce9178`) |
| `path:wiki/questions` | Green (`#6a9955`) |
| `path:raw` | Gray (dimmed) |

---

## Custom Callouts

This vault defines **four custom callout types** beyond Obsidian's built-in set (`note`, `tip`, `warning`, `info`, `todo`, `success`, `question`, `failure`, `danger`, `bug`, `example`, `quote`). They render correctly **only when `vault-colors.css` is enabled**. Without the snippet, they fall back to default callout styling (still readable, just plain).

| Custom callout | Color | Icon | Use for |
|---|---|---|---|
| `contradiction` | reddish-brown (rgb 209,105,105) | `lucide-alert-triangle` | New source conflicts with existing claim |
| `gap` | beige (rgb 220,220,170) | `lucide-help-circle` | Topic has no source yet |
| `key-insight` | bright blue (rgb 79,193,255) | `lucide-lightbulb` | Important takeaway worth highlighting |
| `stale` | gray (rgb 128,128,128) | `lucide-clock` | Claim may be outdated, source older than threshold |

### Usage

Use these in wiki pages to flag important states:

```markdown
> [!contradiction] Title
> [[Page A]] claims X. [[Page B]] says Y. Needs resolution.

> [!gap] Title
> This topic has no source yet. Consider finding one.

> [!key-insight] Title
> The most important takeaway from this section.

> [!stale] Title
> This claim may be outdated. Source was from 2022.
```

### Why custom callouts (vs built-in)

The four custom types map to wiki-specific concepts that don't fit cleanly into Obsidian's default set:

- `contradiction` is more specific than `warning`: it signals a **resolvable conflict** between two wiki pages, not a generic warning.
- `gap` is more specific than `question`: it signals a **missing source**, an actionable improvement.
- `key-insight` is more specific than `tip`: it marks **the** most important takeaway from a section, used sparingly.
- `stale` has no built-in equivalent: it signals time-based decay of a claim.

If you don't want custom callouts, replace them with built-ins:
- `[!contradiction]` → `[!warning] Contradiction`
- `[!gap]` → `[!question] Gap`
- `[!key-insight]` → `[!tip] Key insight`
- `[!stale]` → `[!warning] Stale`

---

## Minimal Theme (Recommended)

The color scheme looks best with the Minimal theme. Install via Settings > Appearance > Manage > search "Minimal".
