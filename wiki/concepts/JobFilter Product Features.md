---
type: concept
title: "JobFilter Product Features"
complexity: basic
domain: "product"
aliases: ["jobfilter features", "intake engine", "filter engine"]
created: 2026-04-29
updated: 2026-04-29
tags:
  - concept
  - jobfilter
  - product
status: current
related:
  - "[[JobFilter Onboarding Stages]]"
sources: []
---

# JobFilter Product Features

## Definition

JobFilter is a digital gatekeeper for tradesmen. One unique link filters all enquiries — bad leads blocked, GOLD leads delivered to WhatsApp instantly. Price: £49/month.

## Core Mechanic

Tradesman shares `jobfilter.uk/intake/[username]` everywhere. Every enquiry goes through a 4-step qualification flow before the tradesman sees it.

## Built Features (2026-04-29)

### Intake Form — 4 steps
1. Job type: Electrical / Plumbing / Roofing / Building
2. Urgency: Emergency / This week / Later
3. Budget: Under £500 / £500–£2k / £2k–£5k / £5k+
4. Details: phone + postcode + photos + description

### Filter Engine — GOLD / SILVER / BIN
| Signal | Score change |
|---|---|
| Base | +40 |
| Emergency | +30 |
| This week | +20 |
| Postcode provided | +20 |
| Photos uploaded | +10 |
| Under £500 | → BIN (force 0) |
| £500–£2k | +5 |
| £2k–£5k | +15 |
| £5k+ | +25 |
| Vague details (<20 chars) | -20 |
| "cheap/low budget" keywords | -50 |

- **GOLD** ≥ 80
- **SILVER** ≥ 50
- **BIN** < 50

### WhatsApp Gold Alerts
- Fires on GOLD tier only
- Message:
  ```
  🏆 NEW GOLD LEAD
  Job: [type]
  Area: [postcode outward]
  Budget: [range]
  Score: [X]/100
  Tap to call: [phone]
  ```
- Twilio WhatsApp REST
- Requires: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_TO`, `TWILIO_WHATSAPP_FROM`

### Filter Link Page
- Shows `jobfilter.uk/intake/[username]`
- Copy + WhatsApp share buttons

## Planned Features

### QR Van Sticker
- QR code → `jobfilter.uk/intake/[username]`
- Downloadable PNG (free), printed sticker (upsell)
- Effort: ~2 hrs

### Lead Persistence
- Save to Supabase (currently localStorage only)
- Effort: 2–3 hrs

### Auth + Multi-user
- Each tradesman gets own account + link
- Currently hardcoded to single user
- Effort: 1–2 days

### Stripe Paywall
- Free: 5 leads/month
- Paid: £49/month unlimited
- Effort: 1 day

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React + Vite |
| Backend | Express |
| DB | Supabase |
| Alerts | Twilio WhatsApp |
| Scoring | Server-side (no ML) |

## Connections

- [[JobFilter Onboarding Stages]]
