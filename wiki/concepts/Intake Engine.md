---
type: concept
title: "Intake Engine"
complexity: intermediate
domain: "product"
aliases: ["intake link", "filter link", "filtering link"]
created: 2026-04-29
updated: 2026-04-29
tags:
  - concept
  - jobfilter
  - product
  - core
status: current
related:
  - "[[JobFilter Product overview]]"
  - "[[JobFilter Product Features]]"
  - "[[JobFilter Onboarding Stages]]"
  - "[[Vantage]]"
  - "[[Vicinity]]"
  - "[[Codex]]"
sources: []
---

# Intake Engine

## Definition

Core paid product. £49/month. Tradesman gets unique URL `jobfilter.uk/intake/[username]`. Every customer enquiry flows through 4-step qualification before reaching them. Bad leads blocked. GOLD leads delivered to WhatsApp.

## How It Works

1. Tradesman shares link (WhatsApp, Instagram bio, calls, QR sticker)
2. Customer fills 4 steps: job type → urgency → budget → details + phone + postcode + photos
3. [[Codex]] scores lead 0–100, assigns tier GOLD/SILVER/BIN
4. GOLD tier triggers WhatsApp alert to tradesman's phone

## 4-Step Form

| Step | Fields |
|---|---|
| 1 | Job type (Electrical / Plumbing / Roofing / Building) |
| 2 | Urgency (Emergency / This week / Later) |
| 3 | Budget (Under £500 / £500–£2k / £2k–£5k / £5k+) |
| 4 | Phone, postcode, photos, optional details |

## Tier Outcomes

- **GOLD** ≥ 80 → WhatsApp ping
- **SILVER** ≥ 50 → saved to dashboard, no alert
- **BIN** < 50 → blocked, tradesman never sees

## Why It Matters

The link IS the product. Single object tradesman shares, single moment of value (WhatsApp ping = sale closed in their head). All other features ([[Vantage]], [[Vicinity]], [[Codex]], [[Free Tools]]) exist to make this link more valuable or drive signups to it.

## Build Status

- Form built (4 steps) ✅
- Scoring engine ([[Codex]] live) ✅
- WhatsApp Twilio stub (needs env vars to go live) ✅
- Single hardcoded user (auth + multi-tenancy pending) ⚠️
- Stripe paywall (not built) ❌

## Connections

- [[JobFilter Product overview]]
- [[Codex]] — scoring engine inside intake
- [[Vicinity]] — geographic filter layer
- [[Vantage]] — source intelligence layer
- [[JobFilter Onboarding Stages]]
- [[JobFilter Product Features]]
