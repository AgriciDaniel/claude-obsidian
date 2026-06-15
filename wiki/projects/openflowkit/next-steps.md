---
type: concept
title: "OpenFlowKit Next Steps"
complexity: basic
domain: product
aliases: ["Open Flow roadmap", "OpenFlowKit implementation"]
created: 2026-06-03
updated: 2026-06-15
tags:
  - concept
  - openflowkit
  - roadmap
  - deployment
status: current
related:
  - "[[OpenFlowKit Product Overview]]"
  - "[[OpenFlowKit Market Fit]]"
  - "[[OpenFlowKit Pricing]]"
sources: []
---

# OpenFlowKit — Next Steps and Deployment Status

## Current Deployment State

- GitHub: https://github.com/manazoid4/openflowkit
- Local PC location: `C:\Users\manaz\Desktop\openflowkit`
- Live URL: openflowkit.vercel.app
- Platform: Vercel (auto-deploy on push to main)
- Stack: Vite + React + TypeScript, Web Speech API
- Status: deployed, core flow functional
- Terminal bridge: shipped (HTTP server on port 7373 + WebSocket component, clipboard + keystroke injection)

## Implementation Priorities

### P0 — Core Functionality (must work before any marketing)

- [x] All 6 writing modes implemented and tested across browsers
- [x] Web Speech API fallback handling (browsers without support)
- [x] Speak-to-Share URL encoding and decoding working end-to-end
- [x] Clipboard copy working across browser/OS combinations
- [x] Terminal bridge (HTTP + WebSocket, clipboard/keystroke injection)
- [ ] Free tier mode gate (3 modes, prompt to upgrade for others)

### P1 — Auth and Payments (required before Pro launch)

- [ ] Auth layer (email/password or OAuth — keep simple, consider Clerk or Supabase Auth)
- [ ] Stripe integration for Pro (£9/mo) and Teams (£7/seat/mo) billing
- [ ] Seat management UI for Teams tier
- [ ] Usage history persistence (local for Free, cloud-synced for Pro+)

### P2 — Team Features

- [ ] Shared vocabulary store (snippet library synced across team seats)
- [ ] Admin dashboard (seat management, usage analytics)
- [ ] Custom dictionary (add domain-specific words for better Code mode output)

### P3 — Enterprise Readiness

- [ ] SSO support (SAML/OIDC via Clerk or Auth0)
- [ ] Audit log generation and export
- [ ] Private deploy documentation (self-hosted Vercel or Docker)
- [ ] Enterprise contact form and onboarding flow

## Technical Decisions to Make

| Decision | Options | Notes |
|---|---|---|
| Auth provider | Clerk, Supabase Auth, NextAuth | Clerk has good Teams/org support |
| Payments | Stripe | Standard, well-documented |
| History persistence | localStorage (Free), Supabase (Pro+) | Keep Free fully local |
| Snippet library storage | IndexedDB (local), Supabase (Pro+) | Match history model |
| Code mode refinement | Rule-based regex vs LLM post-pass | Rule-based first for offline promise |

## Go-to-Market Sequence

1. Validate core flow with 10-20 real users (ungate, invite only)
2. Ship Pro tier (Stripe + auth) — target developer segment first (Code mode is the hook)
3. Share on Hacker News, Product Hunt, Reddit r/productivity
4. Speak-to-Share is the viral loop — every shared link is a distribution event
5. Teams tier as inbound from Pro users who share internally
6. Enterprise as pull from Teams orgs with compliance requirements

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Web Speech API browser support gaps | Safari requires permission grant; document clearly. Fallback: paste text mode |
| Speak-to-Share URL length limits | Keep encoded payloads short; truncate gracefully |
| Free tier abuse | Rate-limit by IP for anonymous users |
| Offline promise broken by future features | Keep core audio pipeline strictly local; only sync layer goes to cloud |

## Connections

- [[OpenFlowKit Product Overview]]
- [[OpenFlowKit Market Fit]]
- [[OpenFlowKit Pricing]]
