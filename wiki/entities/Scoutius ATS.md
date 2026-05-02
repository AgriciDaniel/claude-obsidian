---
type: entity
title: "Scoutius ATS"
address: c-000003
entity_type: product
role: "Internal hire-CRM replacing Workable for hiring lecturers"
first_mentioned: "[[Scoutius Sprint 1 Day 1-2]]"
created: 2026-04-30
updated: 2026-04-30
tags:
  - entity
  - product
  - ats
  - scoutius
status: active
related:
  - "[[Scoutius Sprint 1 Day 1-2]]"
  - "[[entities/_index]]"
sources:
  - "[[Scoutius Sprint 1 Day 1-2]]"
---

# Scoutius ATS

Internal hire-CRM (applicant tracking system) under active solo-development to replace Workable for the team's lecturer-hiring workflow. Owner: Vladosik (product owner, non-coder). Sole developer: Claude. Build window: 10–12 weeks. Budget: ~$130/month MVP.

## Why It Exists

Workable failed the team in seven concrete ways: locked first two pipeline stages, no on-hold vacancy state, broken role management (hiring managers see salary expectations), silent email delivery failures, no Ukrainian localization, rigid scorecards, no UTM attribution. Each has a corresponding architectural response in Scoutius. The ATS is not generic — it is shaped specifically by these gaps.

## Stack (frozen)

Next.js 16 (App Router) · TypeScript · Tailwind v4 · shadcn/ui · Supabase (Postgres + Auth + Realtime + Storage) · Drizzle ORM · Inngest · Resend · Apify (LinkedIn sourcing) · Claude Sonnet 4.5 via Vercel AI SDK · next-intl (UA + EN) · Vercel Pro · Sentry · PostHog · Vitest · Playwright.

Architecture document records 21 grilled questions and 130+ locked decisions. Versions in the doc are a snapshot; Next 16 + Tailwind 4 (vs. doc's Next 15) accepted as drift-OK because App Router and public API are unchanged.

## Architecture Invariants

- `tenant_id UUID NOT NULL` on every domain table from day 1, even though MVP is single-tenant. Phase 3 unlocks multi-tenancy without a schema migration.
- RLS enabled on all critical tables. Application-level RBAC is primary, RLS is the safety net. Mandatory because Supabase Realtime requires RLS for client-side subscription security.
- Six fixed roles: `super_admin`, `admin`, `recruiter_lead`, `recruiter`, `hiring_manager`, `external`. Custom-roles editor is Phase 2.
- Threads are first-class with `(candidate_id, channel, vacancy_id NULLABLE)` so Phase 3 WhatsApp/Telegram channels slot in without rework.
- Email delivery state machine (`queued → sent → delivered → bounced → complained → failed`) without opens/clicks tracking — fixes Workable's silent-fail without engagement-tracking baggage.
- Sourcing as Inngest step function with `step.waitForEvent` for Apify webhook + 2h timeout fallback poll.
- Optimistic concurrency on stage moves via `applications.stage_version`.

## MVP Scope (frozen)

**IN.** Pipeline-Kanban with Realtime; Vacancies + Applications + Evaluations with custom fields; six roles + RLS; confidential vacancies; on-hold orthogonal to pipeline; email outbound + inbound + threading + delivery tracking; Markdown templates; linear sequences with auto-pause on reply; LinkedIn-only sourcing; Postgres FTS + ⌘K; Auth (email + magic link + Google OAuth + TOTP); invite-only onboarding; audit log; UA + EN; funnel + velocity dashboards; UTM intake; Sentry + PostHog.

**OUT (deferred).** Career page, multi-tenancy unlock, IG/X/Threads sourcing, custom-roles editor, ClamAV virus scanning, WhatsApp/Telegram channels, Stripe billing, saved searches, cross-entity global search, Meilisearch.

## Sprint Cadence

12 weekly sprints. Each ends in a demo-able state. Pre-agreed tear-out clauses: if sourcing pipeline does not run end-to-end by end of week 6 → push to Phase 1.5 without renegotiation; same for sequences end of week 7. Rollout is parallel 2–4 weeks (Workable + Scoutius live simultaneously) before cutover.

## Repo & Environment

- GitHub: `Growth-Uni/scoutius-ats` (private)
- Local path: `~/Desktop/scoutius-ats/`
- Domains: `scoutius.vercel.app` (production placeholder for Sprint 1 DoD; custom domain `scoutius.io` later), `staging.scoutius.io` planned but not bound yet
- Supabase: separate `scoutius-staging` (Free) and "Production Super App" (Pro) projects
- Region: `eu-central-1` (Frankfurt)

## Status

Active. Sprint 1 in progress — see [[Scoutius Sprint 1 Day 1-2]] for the latest progress log.
