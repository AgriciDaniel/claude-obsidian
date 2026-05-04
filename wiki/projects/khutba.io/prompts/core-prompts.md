---
type: reference
title: "khutba.io Core Prompts"
domain: prompts
created: 2026-05-01
updated: 2026-05-01
tags:
  - prompts
  - khutba
status: current
---

# khutba.io — Core Prompts

## Product & Strategy

### Define a new feature
```
We're building khutba.io — live auto-translation display for masjids.
Feature request: [FEATURE].
Stack: React + Node + Deepgram + Google Translate + Socket.io + Supabase.
Keep it simple. No overengineering. How should we build this?
```

### Pitch copy
```
Write a short pitch for khutba.io targeted at [TARGET: masjid committee / Islamic centre / imam].
Core value: live multilingual auto-scrolling translation of khutba on screens.
Tone: respectful, community-focused, practical. Under 100 words.
```

### Pricing decision
```
khutba.io pricing context: ~$3.26/mo API cost per masjid.
Current tiers: Starter £29, Masjid £59, Centre £99.
Question: [PRICING QUESTION].
Consider: community budgets, Muslim charity culture, value vs cost.
```

## Technical

### Build a new component
```
khutba.io stack: React + Vite + TailwindCSS frontend, Node/Express backend,
Socket.io realtime, Deepgram speech-to-text, Google Translate API.
Build: [COMPONENT/FEATURE].
Requirements: clean, minimal, no unnecessary abstractions.
```

### Debug live translation pipeline
```
khutba.io pipeline: mic → Deepgram stream → translate → Socket.io → display.
Problem: [DESCRIBE ISSUE].
Check: latency, language codes, WebSocket connection, API key validity.
```

### RTL display fix
```
khutba.io displays Arabic and Urdu (RTL) on screen.
Problem: [DESCRIBE DISPLAY ISSUE].
Stack: React + TailwindCSS. Fix RTL rendering only. Don't touch LTR languages.
```

## Session Notes

### Save session output
```
Session date: [DATE]. khutba.io work done: [SUMMARY].
Save to: wiki/projects/khutba.io/sessions/[DATE]-session.md
Include: what was built, decisions made, next steps.
```

### Append running log entry
```
Append to: wiki/projects/khutba.io/sessions/running-log.md
Format:
## [DATE] — [SESSION TITLE]
- Built: [what]
- Decided: [what]
- Next: [what]
```
