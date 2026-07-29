---
type: concept
title: "khutba.io APIs"
complexity: basic
domain: technical
aliases: ["khutba apis", "khutba integrations"]
created: 2026-05-01
updated: 2026-05-01
tags:
  - concept
  - khutba
  - technical
status: current
related:
  - "[[khutba.io Project Outline]]"
sources: []
---

# khutba.io — APIs & Integrations

## Speech-to-Text

| Option | Notes | Cost |
|---|---|---|
| **Deepgram** ✅ | Lowest latency (<300ms), streaming, Arabic support | ~$0.0043/min |
| OpenAI Whisper | Best accuracy for Arabic, REST only (not streaming) | ~$0.006/min |
| AssemblyAI | Good multilingual, streaming supported | ~$0.0062/min |
| Google Speech-to-Text | Broad language support, higher cost | ~$0.016/min |

**Recommended: Deepgram** — best latency for live display.

## Translation

| Option | Notes | Cost |
|---|---|---|
| **Google Translate API** ✅ | Best Arabic + Urdu + Somali + Bengali coverage | ~$20/1M chars |
| DeepL API | Best quality EN/DE/FR, weak on Arabic/Urdu | ~$25/1M chars |
| LibreTranslate | Free, self-hosted, lower quality | Free |

**Recommended: Google Translate API** — widest language coverage for Muslim community.

## Realtime Transport

| Option | Notes |
|---|---|
| **Socket.io** ✅ | WebSocket + fallback, self-hosted, no vendor lock |
| Ably | Managed WebSocket, generous free tier |
| Pusher | Simple API, managed |

## Database

| Option | Notes |
|---|---|
| **Supabase** ✅ | Postgres + realtime + auth, free tier |

## Billing

| Option | Notes |
|---|---|
| **Stripe** ✅ | Standard, supports UK billing |

## Hosting

| Layer | Platform |
|---|---|
| Frontend | Vercel |
| Backend + WebSocket | Railway or Render |

## Required Env Keys

```
DEEPGRAM_API_KEY=
GOOGLE_TRANSLATE_API_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

## Estimated Cost Per Masjid/Month

*(2 khutbas/week, ~1hr each)*

| Service | Usage | Cost |
|---|---|---|
| Deepgram | ~8hr/mo | ~$2.06 |
| Google Translate | ~60k chars/mo | ~$1.20 |
| Supabase | Free tier | $0 |
| Vercel | Free tier | $0 |
| **Total** | | **~$3.26/mo** |

Margin at £29/mo starter plan = strong.

## Connections

- [[khutba.io Project Outline]]
