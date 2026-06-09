# Recall: Design System v2 — 2026-06-09

## Summary

Overhauled Recall design system. Linear/Raycast-inspired dark mode, Inter font, semantic CSS variable tokens, theme toggle.

## Changes

### tailwind.config.ts
- `darkMode: 'class'`
- **HSL channel format** for all semantic colors: `hsl(var(--ink) / <alpha-value>)` — Tailwind opacity variants work everywhere
- New tokens: `overlay`, `dim`, `brand`
- Shadow scale: `card`, `card-hover`, `panel`, `modal`, `glow-amber`
- Animation keyframes: `fade-in`, `slide-up`, `slide-down`, `scale-in`, `shimmer`, `pulse-soft`

### app/globals.css
- Full CSS variable token system — light in `:root`, dark in `.dark`
- Zinc-based palette (cooler, closer to Linear)
- Custom scrollbar, selection highlight, autofill fix
- Smooth 150ms theme transitions
- Component layer: `.btn-primary`, `.card-hover`, `.gradient-text`
- Utility layer: `.glass`, `.shimmer`, `.text-balance`

### app/layout.tsx
- Inter font via `next/font/google`
- Inline themeScript — restores localStorage preference before hydration (no flash)
- `suppressHydrationWarning` on `<html>`

### components/ThemeToggle.tsx (NEW)
- Sun/Moon toggle, persists to localStorage
- Reads system preference as default

### components/Sidebar.tsx
- ThemeToggle in header
- `hover:bg-overlay` (dark-safe hover)
- Active dot indicator on nav items

### components/SearchBar.tsx
- Search button: `text-panel` — correct on both light/dark ink backgrounds

### components/PostCard.tsx
- `text-muted/40` → `text-dim`
- `shadow-card-hover` tokens

### app/(marketing)/page.tsx
- Sticky glass nav, ambient glow, gradient-text headline
- Trust bar, polished CTAs, improved footer

## Design Token Reference

| Token | Light | Dark |
|-------|-------|------|
| `--surface` | zinc-50 | zinc-950 |
| `--panel` | white | zinc-900 |
| `--overlay` | zinc-100 | zinc-800 |
| `--ink` | zinc-950 | zinc-50 |
| `--muted` | zinc-500 | zinc-400 |
| `--dim` | zinc-400 | zinc-600 |
| `--line` | zinc-200 | ~zinc-800 |

## Commit
`2f933a0` — manazoid4/recall main
