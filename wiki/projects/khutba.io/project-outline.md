---
type: concept
title: "khutba.io Project Outline"
complexity: basic
domain: product
aliases: ["khutba outline"]
created: 2026-05-01
updated: 2026-05-01
tags:
  - concept
  - khutba
  - product
status: current
related:
  - "[[khutba.io Product Overview]]"
  - "[[khutba.io APIs]]"
sources: []
---

# khutba.io — Project Outline

## Phase 1 — MVP (weeks 1–3)

| Task | Detail |
|---|---|
| Live speech capture | Browser mic → WebSocket stream |
| Speech-to-text | Deepgram streaming API |
| Translation engine | Google Translate API |
| Display screen | Full-screen auto-scroll React app |
| Languages | Arabic + English + Urdu |
| UI | Clean, large-text, dark mode, masjid-safe |

## Phase 2 — Masjid Ready (weeks 4–6)

| Task | Detail |
|---|---|
| Admin dashboard | Set languages, font size, screen layout |
| Presenter control | Start/stop/pause from phone |
| Multi-screen | HDMI + browser-based display |
| Personal device | Congregation picks language on own phone |
| Branding | Masjid logo on screen |

## Phase 3 — Growth (weeks 7–12)

| Task | Detail |
|---|---|
| Stripe billing | Monthly subscription per masjid |
| Archive | Recordings stored, searchable by date/topic |
| More languages | Somali, Bengali, Turkish, French |
| Mobile app | Congregation follows on phone |
| Analytics | Language usage, attendance metrics |

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React + Vite + TailwindCSS |
| Backend | Node/Express |
| Speech-to-text | Deepgram |
| Translation | Google Translate API |
| Realtime | Socket.io (WebSockets) |
| DB | Supabase |
| Billing | Stripe |
| Hosting | Vercel (frontend) + Railway (backend) |

## Design Notes

- Borrow JobFilter UI patterns — dark, clean, card-based
- Large readable font (min 32px on display screens)
- RTL support for Arabic and Urdu
- Auto-scroll speed tied to speech pace

## Connections

- [[khutba.io Product Overview]]
- [[khutba.io APIs]]
