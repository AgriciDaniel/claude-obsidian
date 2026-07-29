---
type: concept
title: "JobFilter Onboarding Stages"
complexity: intermediate
domain: "product"
aliases: ["jobfilter onboarding", "tradesman funnel"]
created: 2026-04-29
updated: 2026-04-29
tags:
  - concept
  - jobfilter
  - product
status: current
related:
  - "[[JobFilter Product Features]]"
sources: []
---

# JobFilter Onboarding Stages

## Definition

Six-stage funnel turning a tradesman visitor into a paying £49/month subscriber. Stage 5 (first real lead notification) is the make-or-break activation moment.

## Stages

### Stage 1 — Hook (Landing page)
- Tradesman sees headline, understands product in 5 seconds
- CTA: "Get My Filter Link"
- **Built:** ✅ "Quit Working For Ghosts" landing

### Stage 2 — Claim Link (MyLink page)
- Enter trade name → `jobfilter.uk/intake/[name]`
- Copy link instantly, share to WhatsApp
- **Built:** ✅ MyLinkPage exists (hardcoded username for now)

### Stage 3 — First Test (Intake page as customer)
- Tradesman fills own form as test customer
- Sees GOLD/SILVER/BIN result
- Moment of clarity: "Oh, that's what my customers will see"
- **Built:** ✅ 4-step intake form

### Stage 4 — Go Live
- Share link everywhere (WhatsApp status, Instagram bio, calls)
- QR sticker downloaded or ordered for van
- **Built:** ⚠️ Share buttons exist, QR sticker not built yet

### Stage 5 — First Real Lead ⭐ (Make-or-break)
- Customer submits through link
- WhatsApp ping arrives on tradesman's phone
- GOLD lead = dopamine hit = they're sold
- **Built:** ⚠️ WhatsApp alert wired (Twilio stub, needs env vars)

### Stage 6 — Paywall
- Free: 5 leads/month
- Paid £49/month: unlimited + WhatsApp alerts + QR sticker
- **Built:** ❌ No Stripe, no feature gate

## Build Priority

1. Add Twilio env vars → Stage 5 live (30 min)
2. Wire Supabase leads table → leads persist (2 hrs)
3. Auth + per-user routing → multiple tradesmen (1–2 days)
4. Stripe paywall → Stage 6 (1 day)

## Why It Matters

Stage 5 is retention. Everything before is setup friction. Optimise for fastest path to first WhatsApp ping.

## Connections

- [[JobFilter Product Features]]
