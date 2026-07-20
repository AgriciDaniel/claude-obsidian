---
date: 2026-07-20
project: jobfilter
agent: codex
status: completed
type: session
title: "JobFilter What's New and Agent Nudge v0.4 Release"
tags:
  - jobfilter
  - agent-nudge
  - release
related:
  - "[[2026-07-20-live-agent-bridge]]"
  - "[[Full-Walkthrough-Workflow-for-AI-Coding]]"
---

# JobFilter What's New and Agent Nudge v0.4 Release

## What I did

- Shipped JobFilter's first customer-facing `/whats-new` system on GitHub PR #370.
- Added a single release-data source, build-blocking data validation, permanent anchors, metadata, JSON-LD, sitemap freshness, public/member/mobile navigation, and footer discovery.
- Seeded five customer-notable updates from commits already merged into the JobFilter production history. Internal commit and PR evidence stays server-only and is not rendered.
- Ran independent route, copy-evidence, accessibility, and QA reviews. Corrected overclaims, current-page semantics, reduced-motion behavior, sticky anchor offsets, and status contrast.
- Verified JobFilter at 320 px and 1440 px with no horizontal page overflow or console errors. Direct fragment links, canonical metadata, static HTML, and sitemap output passed.
- Published Agent Nudge v0.4.0 as a GitHub Release with the tested Windows installer and portable EXE.
- Confirmed the requested AI-coding workflow video was already ingested into both the unified desktop vault and the GitHub-backed vault with transcript and provenance.

## Files changed

- JobFilter: `app/whats-new/page.tsx`, `src/data/releases.json`, `src/lib/releases.ts`, `scripts/validate-releases.mjs`, navigation, footer, sitemap, package scripts, reduced-motion CSS, and `.gitignore` exception.
- Vault: this session note plus wiki index/log/hot-cache updates.
- Agent Nudge source remained unchanged; GitHub Release assets were published from the verified local v0.4.0 build.

## Decisions made

- Keep JobFilter News for industry intelligence and use What's New only for product releases.
- Use date-led customer updates instead of semantic versions because trades care about outcomes, not package numbers.
- Publish only user-notable changes; typo, font, and CTA sweeps do not become releases.
- Keep commit/PR evidence in a server-only module. The validator proves schema integrity; shipped truth remains evidence-backed review policy.
- Use Agent Nudge's local-first coordination wedge: structured claims, facts, preflight and receipts—not transcript sharing or claims that a model “knows” context.

## Next steps

1. Merge JobFilter PR #370 after CI and Vercel preview are green, then verify `https://jobfilter.uk/whats-new` in production.
2. Make JobFilter's next customer release the actual public shipment of What's New; do not list it before deployment.
3. Agent Nudge next: automate crash/stale-lock recovery and tighten the daemon into the single SQLite writer before adding cloud sync.
4. Portfolio rollout order: Agent Nudge changelog/release feed, OpenFlowKit releases, InkWeave generation-quality updates. Reuse the schema and validation pattern, but adapt copy and visual language per audience.

## Verification

- JobFilter: `npm run releases:check`, `npm run lint`, `npm run build`, static HTTP checks, sitemap checks, desktop/mobile browser smoke.
- Agent Nudge: v0.4 portable EXE health smoke passed on loopback; local SHA-256 hashes matched the build receipt.

## Links

- JobFilter issue: https://github.com/manazoid4/JobFilterV1/issues/368
- JobFilter PR: https://github.com/manazoid4/JobFilterV1/pull/370
- Agent Nudge v0.4.0: https://github.com/manazoid4/agent-nudge/releases/tag/v0.4.0
- Production Agent Nudge demo: https://agent-nudge-bay.vercel.app
