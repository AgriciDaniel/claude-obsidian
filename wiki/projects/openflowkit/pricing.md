---
type: concept
title: "OpenFlowKit Pricing"
complexity: basic
domain: product
aliases: ["Open Flow pricing", "OpenFlowKit tiers"]
created: 2026-06-03
updated: 2026-06-03
tags:
  - concept
  - openflowkit
  - pricing
  - business-model
status: current
related:
  - "[[OpenFlowKit Product Overview]]"
  - "[[OpenFlowKit Market Fit]]"
  - "[[OpenFlowKit Next Steps]]"
sources: []
---

# OpenFlowKit — Pricing Model

## Tier Overview

| Tier | Price | Target |
|---|---|---|
| Free | £0 | Individual, casual users |
| Pro | £9/mo | Power users, professionals |
| Teams | £7/seat/mo | Small teams with shared vocab needs |
| Enterprise | Contact | Private deploy, compliance-heavy orgs |

## Free Tier

- Local capture (audio never leaves device)
- 3 writing modes (e.g. Casual, Email, Raw)
- Basic session history
- No sharing links
- No account required for core flow

Rationale: eliminate all friction for first use. Browser, speak, done. Convert users who hit the mode or history limit.

## Pro (£9/mo)

- All 6 writing modes (Email, Slack, Code, Formal, Casual, Raw)
- Unlimited history
- Speak-to-Share URL generation
- Snippet library (save and reuse phrases)

Rationale: £9/mo sits below Wispr Flow-tier pricing while offering features no competitor has (modes + sharing). Developer and power user segment. Annual option should be considered at launch.

## Teams (£7/seat/mo)

- Everything in Pro
- Shared vocabulary and custom dictionary across team
- Admin controls (seat management, access)
- Usage analytics per seat

Rationale: cheaper per seat than Pro to incentivise bulk adoption. Shared vocab is the unlock — it solves consistency problems in team writing (sales, support, legal). Min seat count TBD (suggest 3).

## Enterprise (Contact)

- Private deploy (self-hosted or dedicated Vercel env)
- SSO integration
- Audit logs
- Custom SLA

Rationale: some orgs (finance, legal, healthcare) will not use shared cloud even with local-first defaults. Private deploy + SSO + audit logs covers procurement requirements. Price on ACV basis.

## Conversion Strategy

- Free to Pro: user hits 3-mode limit or wants Speak-to-Share
- Pro to Teams: user starts sharing snippets with colleagues, or admin sees adoption
- Teams to Enterprise: compliance team flags shared infra, requests private deploy

## Pricing Rationale vs Competitors

- Wispr Flow: no public pricing, estimated $10-15/mo, desktop-only, no modes
- Superwhisper: $9.99/mo, Mac-only, no modes
- OpenFlowKit Pro at £9/mo matches on price but has modes, sharing, and browser-native delivery

## Connections

- [[OpenFlowKit Product Overview]]
- [[OpenFlowKit Market Fit]]
- [[OpenFlowKit Next Steps]]
