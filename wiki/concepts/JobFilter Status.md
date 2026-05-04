---
type: meta
title: "JobFilter Status"
domain: "product"
aliases: ["jobfilter hot cache", "jobfilter current state"]
created: 2026-04-29
updated: 2026-04-29
tags:
  - meta
  - jobfilter
  - hot-cache
status: evergreen
related:
  - "[[JobFilter Product overview]]"
  - "[[Intake Engine]]"
  - "[[JobFilter Onboarding Stages]]"
  - "[[JobFilter Product Features]]"
  - "[[JobFilter Design System]]"
sources: []
---

# JobFilter Status

**Read this FIRST when starting any JobFilter session.** Compact current state.

## What's Built (as of 2026-04-29)

- Landing page ("Quit Working For Ghosts") ✅
- 4-step intake form (job → urgency → budget → details) ✅
- Filter engine (GOLD/SILVER/BIN scoring) ✅
- WhatsApp alert stub (Twilio REST, needs env vars) ✅
- MyLink page (copy + WhatsApp share) ✅
- Free Tools page (calculators, scans) ✅

## What's Half-Built

- Single hardcoded user (no auth) ⚠️
- Lead persistence = localStorage only (no Supabase) ⚠️
- Postcode filter = prefix only (no radius math) ⚠️
- Vantage/Vicinity/Codex = concept stage, not built ⚠️

## What's Not Built

- Stripe paywall (£49/mo gate) ❌
- QR van sticker generator ❌
- Auth + multi-tenant ❌
- Email newsletter wiring ❌

## Active Branches

- `codex/decision-engine-flow` (PR #36) — main work branch
- `claude/festive-lichterman-21957e` (PR #37) — recent intake weapon system merge

## Last CI State

- 2026-04-29: Bad merge of `main` → `codex/decision-engine-flow` caused duplicate `phone` declarations. Fixed in commit `ba267a4`.

## Live Env Needed

Twilio for WhatsApp alerts:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_TO`
- `TWILIO_WHATSAPP_FROM`

## Top Priorities (build order)

1. Add Twilio env vars → WhatsApp goes live (30 min)
2. Wire Supabase leads table → leads persist (2 hrs)
3. QR sticker generator (2 hrs)
4. Auth + multi-user (1–2 days)
5. Stripe paywall (1 day)

## Tech Stack

- Frontend: React + Vite + Tailwind
- Backend: Express
- DB: Supabase (partial)
- Alerts: Twilio WhatsApp
- Hosting: Firebase Functions for backend

## Connections

- [[JobFilter Product overview]]
- [[Intake Engine]]
- [[JobFilter Onboarding Stages]]
- [[JobFilter Product Features]]
