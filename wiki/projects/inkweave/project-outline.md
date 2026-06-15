---
type: concept
title: "InkWeave Project Outline"
complexity: intermediate
domain: product
aliases: ["inkweave outline"]
created: 2026-05-28
updated: 2026-06-15
tags:
  - inkweave
  - project
  - roadmap
status: current
related:
  - "[[InkWeave Product Overview]]"
  - "[[InkWeave Selling Points]]"
sources: []
---

# InkWeave — Project Outline

## Stage 1: MVP (Build Now)

Goal: prove the core loop works. User submits snippets → gets a full book back.

### Features
- [ ] Snippet intake form (web UI): title, genre, snippets upload (text paste or file)
- [ ] AI pipeline: snippet analysis → outline generation → chapter expansion → full manuscript compile
- [ ] Output: DOCX + PDF download
- [ ] Basic user auth (email/password)
- [ ] Stripe payment: one-time per book generation
- [ ] UK-first copy, pricing in GBP

### Tech Stack (Proposed)
| Layer | Choice |
|---|---|
| Frontend | Next.js (App Router) |
| Backend | Node.js / tRPC |
| AI | Claude API (claude-sonnet-4-6 or opus) |
| DB | Supabase (Postgres) |
| Payments | Stripe |
| File gen | Pandoc / docx templating |
| Hosting | Vercel (frontend) + Railway/Fly (backend) |

---

## Stage 2: Session Remote Control

Allow user to intervene and steer the AI mid-generation.

### Features
- [ ] Live generation stream (SSE/WebSocket)
- [ ] User sees chapters as they generate
- [ ] "Redirect" button: user types new direction, AI resumes from that point
- [ ] Chapter-level approve/reject/regenerate
- [ ] Session state saved so user can resume later

---

## Stage 3: Paid Upgrades

Bolt-on revenue after core product validated.

### Add-ons
- [ ] AI edit pass (style polish, grammar, pacing)
- [ ] Cover brief pack (Midjourney prompt pack tailored to book)
- [ ] UK Publishing Guide (PDF: ISBN, KDP, IngramSpark, distribution)
- [ ] Co-author mode (multiple users feeding snippets into one book)

---

## Stage 4: Scale

- [ ] Subscription tier (monthly: unlimited books)
- [ ] API for writing schools / publishers (white-label)
- [ ] Genre specialisation (romance, thriller, non-fiction)
- [ ] Community: author profiles, book showcase

---

## Monetisation Summary

| Source | Model | When |
|---|---|---|
| Book generation | Per-use GBP fee | Stage 1 |
| Add-on upgrades | One-time per book | Stage 3 |
| Remote control | Premium subscription | Stage 2 |
| Affiliates | Commission (Reedsy, IngramSpark) | Stage 3 |
| API/white-label | B2B contract | Stage 4 |

---

## Connections

- [[InkWeave Product Overview]]
- [[InkWeave Selling Points]]
- [[InkWeave APIs]]
