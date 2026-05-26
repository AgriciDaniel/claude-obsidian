---
type: concept
title: "Applying Laba Brand Book to a New Product"
created: 2026-05-22
updated: 2026-05-22
status: current
tags:
  - concept
  - laba-mvp
  - design-system
  - tailwind
  - urbanist
related:
  - "[[Brand Book — Laba MVP]]"
  - "[[Brand Book — Researchius]]"
  - "[[SuperApp Access Control Model]]"
  - "[[Per-Workspace CSS via Data Attribute]]"
  - "[[laba-mvp-design plugin]]"
sources:
  - "[[Brand Book — Laba MVP]]"
---

# Applying Laba Brand Book to a New Product

The Laba MVP Brand Book v1.0 is a contract that every product in the family obeys: monochrome ink + lime accent, Urbanist everywhere, large radii, pill-shaped interactives, 1% lime per screen. This page captures the canonical recipe for **bolting that contract onto a Next.js product from scratch** — verified end-to-end on the Laba Production Super App (May 2026), including the dead end that wasted the first attempt.

If you start a new sibling product, read this before touching code.

---

## Stack that worked

| Layer | Choice |
|---|---|
| Next.js | App Router (any recent v14+; v14.2 verified) |
| Tailwind | **v3 (`tailwindcss@^3.4`)** + `postcss` + `autoprefixer` |
| Tokens | `tailwind.config.ts` extending `theme` |
| Font | **Urbanist** via `next/font/google`, weights 400/500/600/700/800, `subsets: ['latin', 'latin-ext']` only (Urbanist has no Cyrillic subset — brand is English-only anyway) |
| Components | hand-rolled with `class-variance-authority` + `clsx` + `tailwind-merge` (the `cn()` helper) |
| Icons | `lucide-react`, never mix with Heroicons / Phosphor |

Brand Book canonically points to `tailwind.config.ts` + `globals.css`, which is Tailwind v3 syntax.

---

## Stack that did NOT work (avoid)

**Tailwind v4 on Next 14.2** — the install completes, `next build` returns ✓ green, but several utility classes (`bg-surface`, `border-line`, `p-5`, `rounded-md`) never make it into the generated CSS. Pages render with text and CTAs but lose their cards, padding, borders, and table-column spacing. The result looks broken in production while passing every automated check.

Lesson: **`next build` is not enough** — verify visually before merge.

The second-order lesson: a typecheck-green PR on Tailwind v4 + Next 14 will still ship broken. If a brand application has to wait on Next 15 / React 19, defer it.

---

## Token file (paste-and-adjust)

```ts
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink:     "#191919",
        accent:  "#C1FC02",          // lime — the 1% moment
        page:    "#F2F2F2",
        surface: "#EFEFEF",
        card:    "#FFFFFF",
        line:    "#E3E3E3",
        n: { 50:"#FAFAFA", 100:"#F2F2F2", 200:"#EFEFEF", 300:"#E5E5E5",
             400:"#C9C9C9", 500:"#8E8E8E", 600:"#5A5A5A", 700:"#3A3A3A",
             800:"#2A2A2A", 900:"#191919" },
        success: "#4D8B5C",
        warning: "#D89E36",
        error:   "#D2453F",
        info:    "#5A7BAD",
      },
      fontFamily: { sans: ["var(--font-urbanist)", "ui-sans-serif", "system-ui", "sans-serif"] },
      fontSize: {
        eyebrow:  ["11px", { lineHeight: "14px", letterSpacing: "0.08em", fontWeight: "600" }],
        small:    ["14px", { lineHeight: "20px", fontWeight: "400" }],
        body:     ["16px", { lineHeight: "24px", fontWeight: "400" }],
        h3:       ["20px", { lineHeight: "26px", fontWeight: "600", letterSpacing: "-0.01em" }],
        subtitle: ["26px", { lineHeight: "32px", fontWeight: "500", letterSpacing: "-0.015em" }],
        h2:       ["32px", { lineHeight: "38px", fontWeight: "700", letterSpacing: "-0.02em" }],
        display:  ["40px", { lineHeight: "46px", fontWeight: "700", letterSpacing: "-0.02em" }],
        heading:  ["60px", { lineHeight: "64px", fontWeight: "800", letterSpacing: "-0.025em" }],
      },
      spacing: { "1":"4px", "2":"8px", "3":"12px", "4":"16px", "6":"24px",
                 "8":"32px", "12":"48px", "16":"64px", "24":"96px" },
      borderRadius: { sm:"8px", md:"12px", lg:"16px", "2xl":"24px", pill:"9999px" },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(25,25,25,0.04)",
        md: "0 4px 12px -2px rgba(25,25,25,0.06)",
        lg: "0 12px 32px -4px rgba(25,25,25,0.08)",
      },
      backgroundImage: {
        hatch: "repeating-linear-gradient(135deg, #191919 0 1px, transparent 1px 6px)",
      },
    },
  },
  plugins: [],
};
export default config;
```

`globals.css` keeps the Tailwind directives plus a tiny `@layer base` that sets `body` to `bg-page text-ink font-sans text-body` and emits the lime selection state. **Do not** put `html, body { height: 100% }` — it silently clips any page taller than the viewport. Use `min-h-screen` on body instead and let pages that need viewport-fill (a Shell with an iframe) set `h-screen` explicitly.

---

## Surfaces — the rules you cannot break

1. **White card on `bg-page`, always.** Never grey-on-grey for the primary block. A row of grey-filled tiles reads as a spreadsheet — opposite of the brand.
2. **One step of nesting max.** `bg-page → card → inset` is fine. Another inset inside that is wrong.
3. **Border, not shadow,** for separation. 1px `border-line` is the default. Shadow appears on hover only.
4. **Card padding** — 20-24px for data cards, 28-32px for hero. Generous, not tight.

The Brand Book calls the violation explicitly: "boxy grey rectangles" = anti-pattern.

---

## Composition recipes by surface

### Brand-surface (login, signup, denied)
Centered column on `bg-page`. **No card, no border, no shadow.** The wordmark IS the composition.

```tsx
<div className="min-h-screen flex items-center justify-center bg-page px-4">
  <div className="w-full max-w-md flex flex-col items-center text-center">
    <p className="text-eyebrow text-n-500 uppercase">Welcome back</p>
    <h1 className="text-[48px] leading-none font-extrabold tracking-tight text-ink mt-2">
      Product Name
    </h1>
    <p className="text-small text-n-500 mt-3">Sign in to continue.</p>
    {/* form below */}
  </div>
</div>
```

### Function-surface (shell, admin)
White card on page background. Generous padding. Borders, no shadows at rest.

```tsx
<div className="bg-card border border-line rounded-lg overflow-hidden">
  {/* sections */}
</div>
```

### Top navigation with active stage
Symmetric grid so the tab block sits at **true viewport centre**, regardless of left/right element widths. The active tab is the screen's lime moment.

```tsx
<header className="h-14 bg-card border-b border-line grid grid-cols-[1fr_auto_1fr] items-center px-6 gap-6">
  <Link className="justify-self-start text-body font-extrabold tracking-tight text-ink">L</Link>
  <nav className="overflow-x-auto">
    <div className="inline-flex gap-0.5 bg-page rounded-pill p-0.5">
      {stages.map(s => (
        <button key={s.id}
          className={cn("px-3 h-6 rounded-pill text-[11px] font-medium",
            active ? "bg-accent text-ink" : "text-n-600 hover:text-ink")}>
          {s.label}
        </button>
      ))}
    </div>
  </nav>
  <div className="justify-self-end">{/* avatar */}</div>
</header>
```

### Sub-nav under top tabs
Same height (`h-6`), monochrome pills (NOT lime — main row already owns the lime moment).

```tsx
<button className={cn("px-3 h-6 text-[11px] font-medium rounded-pill",
  active ? "bg-ink text-card" : "text-n-600 hover:text-ink hover:bg-page")}>
  {label}
</button>
```

---

## Component conventions

| Element | Tokens |
|---|---|
| Primary CTA (new flow) | `bg-ink hover:bg-n-800 text-card h-10 px-4 rounded-pill text-small font-medium` |
| Secondary / row action | `border border-line hover:border-ink bg-card text-ink h-9 px-3 rounded-pill text-small font-medium` |
| Destructive ghost | `text-n-500 hover:text-error hover:bg-error/10 h-9 px-3 rounded-pill text-small` (hover-reveal) |
| Input | `text-small border border-line rounded-pill h-9 px-4 bg-card text-ink placeholder:text-n-500 focus:border-ink` |
| Status text in table | Plain text in semantic colour; no pill background; `text-small` weight 400. Lime is reserved for the active stage tab. |

When two controls must look identical (e.g. a segmented role toggle next to an `Add product` button), spell sizes literally as `text-[14px] font-medium`. `text-small` ships with `fontWeight: 400` baked in via the tuple in `tailwind.config`, so order with `font-medium` overrides can be confusing under fast iteration.

---

## The "1% lime" rule in practice

Lime (`#C1FC02`) is the only attention moment. Everything else is monochrome + semantic.

Where to put it on a chrome page:
- Shell top-nav: active stage tab.
- That's it. Sub-nav active stays ink. Pills, badges, buttons stay monochrome. Status cells use semantic colours (success / warning / error), never lime.

When the Brand Book says "1 lime per screen" it's literal. Two limes = visual violation.

---

## Validation workflow

The first design migration shipped broken because verification stopped at `next build`. The second one used this loop:

1. Implement one logical block (e.g. login splash).
2. `npm run dev` locally.
3. Open the page in a browser, take a screenshot, **send it to Vlad before merge**.
4. Only then commit, open PR, merge.

For server-only pages that need auth (Shell, admin), temporarily add a `/preview-*-tmp` route that renders the component with mock data, plus a one-line allowance in `middleware.ts`. Delete both before commit. The preview route is throwaway — never lands in `main`.

---

## When the brand evolves

The Brand Book is the source of truth. If a token changes there, the change flows to:
1. `tailwind.config.ts` in every Laba product.
2. Any product-specific `globals.css` overrides.

Until there is a shared `@laba/design-tokens` package, the propagation is manual. Be deliberate about it — the brand book itself says "the brand book is the contract; the code reads it directly".
