---
type: reference
title: "InkWeave APIs"
complexity: intermediate
domain: engineering
aliases: ["inkweave apis", "inkweave integrations"]
created: 2026-05-28
updated: 2026-05-28
tags:
  - inkweave
  - apis
  - engineering
status: current
related:
  - "[[InkWeave Product Overview]]"
  - "[[InkWeave Project Outline]]"
sources: []
---

# InkWeave — APIs & Integrations

## Core AI

| Service | Use | Notes |
|---|---|---|
| Anthropic Claude API | Book generation pipeline | claude-sonnet-4-6 default, claude-opus-4-7 for premium |
| Streaming (SSE) | Session remote control | Streamed token output to frontend |

## Payments

| Service | Use |
|---|---|
| Stripe | One-time payments + subscription tiers |
| Stripe Checkout | Hosted payment page |
| Stripe Webhooks | Post-payment generation trigger |

## File Output

| Service | Use |
|---|---|
| Pandoc | Markdown → DOCX / PDF conversion |
| AWS S3 / Supabase Storage | Generated file storage, presigned download URLs |

## Auth

| Service | Use |
|---|---|
| Supabase Auth | Email/password + magic link |

## Future / Stage 3+

| Service | Use |
|---|---|
| Reedsy Affiliate | UK publishing affiliate referrals |
| IngramSpark Affiliate | UK distribution affiliate |
| Midjourney API (when available) | Cover generation |
| SendGrid / Resend | Transactional email (generation complete, receipts) |

## Connections

- [[InkWeave Product Overview]]
- [[InkWeave Project Outline]]
