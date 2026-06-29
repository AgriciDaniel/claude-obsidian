# Obsidian Canvas JSON Specification

Canvas files are JSON with two top-level keys: `nodes` (array) and `edges` (array).
Obsidian reads and writes them as UTF-8 JSON files with `.canvas` extension.

This reference aligns with the [JSON Canvas 1.0 open specification](https://jsoncanvas.org/spec/1.0/). All structures support arbitrary additional fields (`[key: string]: any`) for forward compatibility. Obsidian will preserve unknown fields when reading and writing canvas files.

**ID format**: The JSON Canvas 1.0 spec recommends 16-character lowercase hexadecimal IDs (e.g., `"a1b2c3d4e5f67890"`). Obsidian itself generates IDs in this format. The descriptive ID examples in this reference (`"text-title-4821"`, `"img-cover-7823"`) are an alternative naming convention that this plugin uses for human readability. Both are valid JSON Canvas. Use whichever fits your workflow.

---

## Coordinate System

```
        x increases →
   ┌─────────────────────────────────
   │  (-920, -2400)      (0, -2400)
   │
y  │  (-920, 0)          (0, 0) ← origin
↓  │
   │  (-920, 540)        (500, 540)
```

- **Origin** (0, 0) is the center of the canvas viewport.
- **x increases rightward.** Negative x = left of center.
- **y increases downward.** Negative y = above center.
- Node `x` and `y` are the **top-left corner** of the node, not the center.
- Obsidian pans to fit all nodes on first open.

---

## Node Types

### Text node

Renders markdown content as a styled card.

```json
{
  "id": "text-title-4821",
  "type": "text",
  "text": "# Heading\n\nParagraph with **bold** and `code`.",
  "x": -400,
  "y": -300,
  "width": 400,
  "height": 120,
  "color": "6"
}
```

- `text`: markdown string. Use `\n` for newlines.
- Minimum readable size: width ≥ 200, height ≥ 60.
- `color` is optional. Omit for default (no color).

---

### File node

Renders an image, PDF, markdown note, or other vault file inline.

```json
{
  "id": "img-cover-7823",
  "type": "file",
  "file": "_attachments/images/example.png",
  "x": -900,
  "y": -100,
  "width": 420,
  "height": 236
}
```

- `file`: **vault-relative path** (not absolute, not `~/`).
- Supported: `.png` `.jpg` `.webp` `.gif` `.pdf` `.md` `.canvas`
- For `.md` files: renders as a preview card.
- For `.pdf` files: renders the first page as preview.
- No `color` field for file nodes: color is ignored.

---

### Group node (Zone)

A labeled rectangular region. Does not clip or contain nodes. It's a visual guide.
Nodes placed "inside" a group are just positioned within its bounding box.

```json
{
  "id": "zone-branding-3391",
  "type": "group",
  "label": "Brand Identity",
  "x": -920,
  "y": -880,
  "width": 1060,
  "height": 290,
  "color": "6",
  "background": "_attachments/images/grid-bg.png",
  "backgroundStyle": "cover"
}
```

- `label`: shown at the top of the group box.
- `color`: colors the group border and label.
- `background` *(optional)*: vault-relative path to a background image for the group.
- `backgroundStyle` *(optional)*: how the background is rendered.
  - `"cover"`: fills the group, cropping if needed (default-ish behavior)
  - `"ratio"`: preserves aspect ratio, fits inside the group
  - `"repeat"`: tiles the image
- Groups do not affect auto-layout: they are purely visual containers.

---

### Link node

Renders a web URL as an embedded preview card.

```json
{
  "id": "link-karpathy-2233",
  "type": "link",
  "url": "https://github.com/karpathy",
  "x": 200,
  "y": -300,
  "width": 400,
  "height": 120
}
```

- `url`: must be a valid `https://` URL.
- Obsidian fetches the Open Graph preview (title, description, thumbnail).

---

## Edges

Connections between nodes. Usually empty for mood boards.

```json
{
  "id": "e-hub-cidx",
  "fromNode": "hub",
  "fromSide": "right",
  "fromEnd": "none",
  "toNode": "c-idx",
  "toSide": "left",
  "toEnd": "arrow",
  "label": "concepts",
  "color": "5"
}
```

**Required fields**: `id`, `fromNode`, `toNode`. Everything else is optional.

- `fromNode` / `toNode`: IDs of the source and target nodes.
- `fromSide` / `toSide` *(optional)*: `"top"` `"bottom"` `"left"` `"right"`. If omitted, Obsidian auto-calculates the best side based on relative node positions.
- `fromEnd` *(optional)*: end-cap on the source side. Defaults to `"none"`. Values: `"none"` | `"arrow"`.
- `toEnd` *(optional)*: end-cap on the target side. **Defaults to `"arrow"`**: note the asymmetric default vs `fromEnd`. Values: `"none"` | `"arrow"`.
- `label` *(optional)*: text shown on the edge.
- `color` *(optional)*: same color palette as nodes (`"1"`–`"6"` or hex).

Most edges represent directed relationships, so the asymmetric defaults (`fromEnd: "none"`, `toEnd: "arrow"`) produce a single arrow pointing from source to target without specifying anything explicitly.

---

## Color Reference

| Code | Color | Hex (approx) | Use case |
|------|-------|-------------|----------|
| `"1"` | Red / Tomato | #e03e3e | Warnings, archive |
| `"2"` | Orange | #d09035 | Active work |
| `"3"` | Yellow / Gold | #d0a023 | WIP, notes |
| `"4"` | Green / Teal | #448361 | Content, sources |
| `"5"` | Blue / Cyan | #3ea7d3 | Navigation, info |
| `"6"` | Purple / Violet | #9063d2 | Title, identity |

Omit `color` entirely for the default (no border color, transparent label).

---

## Image Sizing Guidelines

Calculate from actual image dimensions using PIL or `identify`:

```bash
python3 -c "from PIL import Image; img=Image.open('path.png'); print(img.width, img.height)"
# or
identify -format '%w %h' path.png
```

| Aspect ratio     | Condition     | Canvas width | Canvas height |
| ---------------- | ------------- | ------------ | ------------- |
| 16:9 (wide)      | ratio 1.6–2.0 | 420          | 236           |
| 2:1 (ultra wide) | ratio > 2.0   | 440          | 220           |
| 4:3              | ratio 1.2–1.6 | 380          | 285           |
| 1:1 (square)     | ratio 0.9–1.1 | 280          | 280           |
| 3:4              | ratio 0.6–0.9 | 240          | 320           |
| 9:16 (portrait)  | ratio < 0.6   | 200          | 356           |
| PDF              | any           | 400          | 520           |
| Unknown          | fallback      | 320          | 240           |

---

## Auto-Positioning Pseudocode

```
function place_node(canvas, zone_label, new_w, new_h):
  zone = find group node where label == zone_label
  padding = 20

  if zone not found:
    max_y = max(n.y + n.height for n in canvas.nodes) + 60
    return (-400, max_y)

  # Nodes visually inside zone
  inside = [n for n in canvas.nodes
            if n.type != 'group'
            and zone.x <= n.x < zone.x + zone.width
            and zone.y <= n.y < zone.y + zone.height]

  if inside is empty:
    return (zone.x + padding, zone.y + padding)

  # Rightmost point in zone
  rightmost = max(n.x + n.width for n in inside)
  next_x = rightmost + 40

  if next_x + new_w > zone.x + zone.width - padding:
    # Overflow → new row
    bottom_of_row = max(n.y + n.height for n in inside)
    return (zone.x + padding, bottom_of_row + padding)

  # Same row
  row_y = min(n.y for n in inside)  # align to top of existing row
  return (next_x, row_y)
```

---

## Full Example: Two-Zone Canvas

```json
{
  "nodes": [
    {
      "id": "title-0001",
      "type": "text",
      "text": "# Brand Reference\n\n**AI Marketing Hub** visual assets",
      "x": -920, "y": -2440, "width": 560, "height": 180, "color": "6"
    },
    {
      "id": "zone-logos",
      "type": "group",
      "label": "Logos & Icons",
      "x": -920, "y": -2200, "width": 1800, "height": 320, "color": "6"
    },
    {
      "id": "img-logo-pro",
      "type": "file",
      "file": "_attachments/images/example.png",
      "x": -900, "y": -2180, "width": 420, "height": 236
    },
    {
      "id": "img-icon-free",
      "type": "file",
      "file": "_attachments/images/example-icon.png",
      "x": -440, "y": -2180, "width": 280, "height": 280
    },
    {
      "id": "zone-covers",
      "type": "group",
      "label": "Skill Covers",
      "x": -920, "y": -1820, "width": 1800, "height": 340, "color": "3"
    },
    {
      "id": "img-seo",
      "type": "file",
      "file": "_attachments/images/example-cover.png",
      "x": -900, "y": -1800, "width": 420, "height": 236
    }
  ],
  "edges": []
}
```

---

## Common Mistakes

- **Wrong path format**: use `_attachments/images/file.png` not `/home/user/...` or `~/...`
- **ID collision**: always read existing IDs before generating a new one
- **Negative y confusion**: `y: -2400` is ABOVE `y: -1000` (more negative = higher up)
- **Group does not clip**: placing a node "inside" a group is just positioning it within the group's bounding box: there is no parent-child relationship in the JSON
- **Missing height on text nodes**: Obsidian will render the text but may clip it if height is too small. Use height ≥ content-lines × 24.
