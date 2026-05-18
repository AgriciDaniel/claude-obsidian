---
type: concept
title: "SVG Diagram Style Guide"
created: 2026-04-14
updated: 2026-04-14
tags:
  - design
  - svg
  - brand
  - diagrams
status: evergreen
related:
  - "[[index]]"
sources:
  - "claude-ads/assets/diagrams/ (17 SVGs, v1.5.0)"
---

# SVG Diagram Style Guide

The canonical visual style for all diagrams across agricidaniel's Claude Code skill repos. Extracted from the 17 production SVGs in claude-ads. Use this as the reference when creating or updating diagrams for any skill repo.

## Font

```
font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif
```

Space Grotesk is the only typeface. No fallback to serif or monospace.

## Color Palette

### Core (use these in every diagram)

| Token | Hex | Role |
|-------|-----|------|
| bg | #0A0A0A | Canvas background (near-black) |
| card | #111111 | Card/container fill |
| card-inner | #1A1A1A | Nested element fill |
| border | #2D2D2D | Card borders, dividers |
| text-primary | #F5F5F0 | Headings, labels (off-white) |
| text-secondary | #888888 | Descriptions, captions |
| text-tertiary | #6a6a6a | De-emphasized metadata |
| accent | #E07850 | Primary accent, arrows, highlights (warm rust-orange) |
| accent-bright | #FF6B35 | Secondary accent, hover states (brighter orange) |

### Platform/Category Colors (use for variety within a diagram)

| Token | Hex | Typical use |
|-------|-----|-------------|
| blue | #60A5FA | Google, data, information |
| purple | #8b5cf6 | Meta, strategy, creative |
| cyan | #06b6d4 | LinkedIn, networking |
| green | #4ADE80 | Success, validation, TikTok |
| rose | #F43F5E | YouTube, alerts |
| orange | #FF6B35 | Microsoft, secondary accent |
| gray | #888888 | Neutral, generic platforms |

### Status Colors (for pass/warn/fail indicators)

| Token | Hex | Role |
|-------|-----|------|
| pass | #16a34a | Pass, success |
| warn | #f59e0b | Warning, attention |
| fail | #dc2626 | Fail, critical |

## Typography Scale

| Element | Size | Weight | Color | Extra |
|---------|------|--------|-------|-------|
| Diagram title | 16-17px | 700 | #F5F5F0 | text-anchor: middle |
| Subtitle | 11px | 400 | #888888 | text-anchor: middle |
| Section label | 13px | 700 | accent color | letter-spacing: 2 |
| Card heading | 12-15px | 600-700 | #F5F5F0 | text-anchor: middle |
| Card subtext | 9-11px | 400 | accent color | Skill/agent name |
| Body text | 10px | 400 | #888888 | Descriptions |
| Tiny label | 9px | 400 | #6a6a6a | Metadata, counts |

## Layout Primitives

### Outer Container
```xml
<rect width="800" height="500" fill="#0A0A0A"/>
```
Standard canvas is 800x500. Some diagrams use 900x250 or 900x350 depending on content.

### Card
```xml
<rect x="40" y="20" width="720" height="120" rx="16" fill="#111111" stroke="#2D2D2D" stroke-width="1.5"/>
```
- Corner radius: `rx="16"` for outer containers
- Border: `#2D2D2D`, `stroke-width="1.5"`

### Colored Top Bar (card accent)
```xml
<rect x="40" y="20" width="720" height="4" rx="2" fill="#E07850"/>
```
4px height, sits at the top edge of the card. Color indicates category.

### Inner Card (nested element)
```xml
<rect x="60" y="230" width="105" height="60" rx="6" fill="#1A1A1A" stroke="#2D2D2D" stroke-width="1"/>
```
- Corner radius: `rx="6"` for small inner cards, `rx="9"` for medium
- Fill: `#1A1A1A` (slightly lighter than parent card)

### Numbered Circle (for sequences)
```xml
<circle cx="138" cy="60" r="14" fill="#0A0A0A" stroke="#60A5FA" stroke-width="1.5"/>
<text x="138" y="60" font-size="12" fill="#60A5FA" text-anchor="middle" font-weight="bold" dominant-baseline="central">1</text>
```
Circle stroke color matches the step's category color.

### Arrow Connector
```xml
<line x1="400" y1="140" x2="400" y2="170" stroke="#E07850" stroke-width="1.5"/>
<polygon points="394,167 400,177 406,167" fill="#E07850"/>
```
Always `#E07850`. Vertical for flow-down, horizontal for left-to-right pipelines.

### Horizontal Divider (title underline)
```xml
<line x1="380" y1="36" x2="520" y2="36" stroke="#E07850" stroke-width="2.5" stroke-linecap="round"/>
```
Short centered line under diagram title. Always accent color.

## Diagram Types (from claude-ads)

| # | Name | Layout | Size |
|---|------|--------|------|
| 01 | Architecture | 3-layer vertical stack | 800x500 |
| 02 | Parallel Audit | Agent grid with flow | 800x500 |
| 04 | Platform Checks | Checklist columns | 800x500 |
| 05 | Quality Gates | Rule cards | 800x500 |
| 06 | How It Works | Step sequence | 900x250 |
| 07 | Data Flow | Horizontal pipeline | 900x250 |
| 08 | Industry Templates | Card grid | 900x350 |
| 10 | MCP Integration | Connection diagram | 800x500 |
| 12 | Privacy Flow | Vertical flow | 800x500 |
| 13 | Scoring Algorithm | Formula breakdown | 800x500 |
| 14 | Creative Pipeline | 5-step horizontal | 900x250 |
| 15 | Platform Grid | 2-row card grid | 900x350 |
| 16 | PDF Pipeline | Process flow | 900x250 |
| 17 | A/B Testing | Split comparison | 800x500 |
| 18 | PPC Calculators | Tool cards | 900x350 |
| 19 | Audit Lifecycle | Circular flow | 800x500 |
| 20 | Install Methods | Option cards | 900x250 |

## Rules

1. Always dark theme. Never white or light backgrounds.
2. Space Grotesk only. No other fonts.
3. #E07850 is the signature accent. Use it for arrows, highlights, and the primary visual element.
4. Cards always have #2D2D2D borders. Never borderless cards.
5. Colored top bars (4px) identify categories. One color per category, consistent across the diagram.
6. Text is always left-aligned or center-aligned. Never right-aligned.
7. No gradients, shadows, or blur filters. Flat design only.
8. Numbered circles for sequential steps. Color matches category.
9. Arrow connectors are always #E07850 with triangle tips.
10. File naming: zero-padded number prefix (01-, 02-, etc.) + kebab-case description.
