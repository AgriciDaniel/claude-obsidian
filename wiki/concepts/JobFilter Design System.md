---
type: concept
title: "JobFilter Design System"
domain: "design"
aliases: ["jobfilter design", "jobfilter v3", "design system", "design tokens"]
created: 2026-05-03
updated: 2026-05-03
tags:
  - concept
  - jobfilter
  - design
  - reference
status: current
related:
  - "[[JobFilter Product overview]]"
  - "[[JobFilter Status]]"
  - "[[Intake Engine]]"
  - "[[Vantage]]"
  - "[[Vicinity]]"
  - "[[Codex]]"
  - "[[Free Tools]]"
sources:
  - "FinalDesignJobFilter/JobFilter Site V3.html"
---

# JobFilter Design System

**Canonical source:** `FinalDesignJobFilter/JobFilter Site V3.html`
This is the approved reference design. All build agents must match this system.
V2.html, Wireframes.html, styles.css are superseded — ignore them.

---

## Colour Tokens

| Token | Hex | Use |
|---|---|---|
| `--navy` | `#0E1A2B` | Primary bg, borders, text |
| `--navy-2` | `#142336` | Panel bg on dark sections |
| `--navy-3` | `#1c3149` | Input bg on dark sections |
| `--paper` | `#ffffff` | Default section background |
| `--offwhite` | `#F5F4EF` | Alternating section background |
| `--rule` | `#E6E4DD` | Dividers |
| `--rule-2` | `#D6D3CA` | Subtle dividers |
| `--muted` | `#5E6A78` | Secondary text |
| `--muted-2` | `#8A95A2` | Tertiary / disabled text |
| `--yellow` | `#F8D31A` | PRIMARY ACCENT — CTAs, highlights, drop shadows |
| `--yellow-2` | `#FFDC36` | Yellow hover state |
| `--red` | `#C84A3C` | Error, bad, rejected |
| `--green` | `#2C8A52` | Success, approved |

**Rule:** Yellow is the only accent. One or two elements per section max. Not every heading.

---

## Typography

| Role | Font | Size | Weight |
|---|---|---|---|
| H1 Display | Barlow Condensed | clamp(44px, 7vw, 92px) | 800, uppercase |
| H2 Section | Barlow Condensed | clamp(28px, 3.6vw, 42px) | 700, uppercase |
| H3 Card | Barlow | 18px | 600 |
| Body | Barlow | 16px | 400, line-height 1.6 |
| Lead text | Barlow | 17px | 500, line-height 1.55 |
| Label | Barlow Condensed | 12px | 700, uppercase, letter-spacing 0.14em |
| Numbers/mono | JetBrains Mono | varies | 600–700 |
| Big result nums | Barlow Condensed | clamp(34px–52px) | 800, yellow |

**Critical rule:** Only H1 hero gets max size + extrabold. Everything else recedes. If everything is bold, nothing is bold.

### Google Fonts load string
```
Barlow Condensed: 500,600,700,800,900
Barlow: 400,500,600,700,800
JetBrains Mono: 400,500,700
```

---

## Spacing

- Section padding: `96px 0` desktop / `64px 0` mobile (≤720px)
- Max content width: `min(1180px, calc(100vw - 40px))`
- Section header max-width: `720px`

---

## Border + Shadow System

All components: `2px solid var(--navy)`, `border-radius: 3–4px`, hard offset drop shadow (no blur).

| Component | Shadow |
|---|---|
| Panel / card | `8px 8px 0 var(--yellow)` |
| Buttons | `4px 4px 0 var(--navy)` |
| Featured pricing plan | `8px 8px 0 var(--navy)` |
| Steps grid | `8px 8px 0 var(--yellow)` |
| Trust stats | `8px 8px 0 var(--yellow)` |

---

## Button System

| Class | Style |
|---|---|
| `.btn` | Yellow bg, navy border, 4px hard shadow |
| `.btn-ghost` | Paper bg, navy border, 4px hard shadow |
| `.btn-quiet` | No bg/border/shadow — text link with arrow |
| `.btn-lg` | Larger padding (16px 26px) |
| `.btn-block` | Full width |

Hover: `translate(-1px, -1px)` + shadow +1px
Active: `translate(2px, 2px)` + shadow −2px

---

## Section Pattern

Alternating backgrounds: paper → offwhite → paper → offwhite
Dark override: `section.on-navy` — navy bg, text to paper/yellow

Every section starts with:
```html
<div class="sec-head">
  <span class="label">Section name</span>
  <h2 class="section-h">Main heading</h2>
  <p class="lead">Subtext optional</p>
</div>
```

---

## Page Structure (canonical V3 order)

| # | Section | ID | Background |
|---|---|---|---|
| 1 | Top Banner — Founding 30 urgency | — | yellow |
| 2 | Nav — sticky, minimal | — | paper |
| 3 | Hero — pain headline + CTA | — | paper |
| 4 | Why JobFilter — bad/good split grid | `#why` | offwhite |
| 5 | What We Do — product stack | `#what` | paper |
| 6 | ROI Calculator | — | offwhite |
| 7 | How It Works — 3 steps | `#how` | paper |
| 8 | Intake Engine Demo | `#intake` | offwhite |
| 9 | Free Tools — calculator grid | `#tools` | paper |
| 10 | For Your Trade — tabbed | `#trades` | offwhite |
| 11 | News | `#news` | paper |
| 12 | Pricing — 3 tiers | `#pricing` | navy (on-navy) |
| 13 | Trust / Social Proof | — | paper |
| 14 | Footer | — | paper |

---

## Nav (canonical)

```
Why JobFilter | What We Do | Free Tools | For Your Trade | News | Pricing | [Join the Waitlist →]
```

- Sticky, `border-bottom: 2px solid var(--navy)`
- Links: 13px, weight 500, no decoration
- CTA button: yellow, 2px navy border, hard shadow
- Collapses to hamburger at ≤1020px

---

## Key Copy

**Hero headline:** "Stop quoting for tyre-kickers."
**Primary CTA:** "See the Intake Engine →"
**Quiet CTA:** "Or try the free tools →"
**Paywall:** "Unlock all leads"
**Banner:** "Founding 30: first 30 tradesmen lock £22/mo forever."

**Use:** tyre-kickers, cowboys, race to the bottom, on the tools, site visits, dead leads, your evenings back
**Never:** optimise, synergize, empower, lead generation, omnichannel

---

## Design Reference Assets (uploads folder)

| File | What it shows |
|---|---|
| `LandingPageImprovements1–5.png` | Landing page iteration screenshots |
| `BluePrintImprovement1.png` | Blueprint/how-it-works section design |
| `Invoice_Gen_Tool.png` | Invoice generator tool UI |
| `Onboarding improvement 1–3.png` | Onboarding flow screens |

Path: `FinalDesignJobFilter/uploads/`

---

## Theme Note

V3 is **light theme** (paper/navy/yellow). App.tsx currently uses dark Tailwind theme (`bg-deep-slate`, `high-vis-orange`). V3 is approved direction — App.tsx needs migrating to match V3 tokens.

---

## What's Good in V3

- Typography hierarchy is clean and calm — only H1 screams
- Yellow accent disciplined — not overused
- Hard drop shadows give craft/tool-belt feel without being gimmicky
- Pain-first page order (Why → How → Demo → Tools → Price) is correct sales flow
- "For Your Trade" tabbed section = SEO + personalisation in one
- News grid layout strong — feature card + 2 small cards
- Paywall design (dashed border + lock icon) is subtle, not aggressive
- ROI calculator has 3 sliders (quotes/week, wasted miles, evening hours) — more complete than App.tsx version

## What's Missing / Weak in V3

- Static HTML only — no React logic wired
- No Firebase / waitlist form wired
- Product definitions (Vantage/Vicinity/Codex) diverge from Obsidian canon (V3 redefines them)
- Trust section has placeholder stats — needs real numbers or honest estimates
- News articles are placeholder copy
- No actual tool interactivity (tool grid renders via JS but logic is stub)
