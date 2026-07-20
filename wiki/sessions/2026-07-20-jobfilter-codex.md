---
date: 2026-07-20
project: jobfilter
agent: codex
status: completed
type: session
title: "JobFilter flagship and portfolio cleanup"
created: 2026-07-20
updated: 2026-07-20
tags:
  - jobfilter
  - portfolio
  - github-hygiene
  - release
related:
  - "[[wiki/projects/jobfilter/INDEX]]"
  - "[[2026-07-20-jobfilter-whats-new-codex]]"
---

## What I did

- Merged JobFilter PR [#369](https://github.com/manazoid4/JobFilterV1/pull/369): production source safety, internal-route 404s, free-tier redaction protection, dependency upgrades, stronger CI, honest public copy, and dead frontend removal.
- Merged JobFilter PR [#375](https://github.com/manazoid4/JobFilterV1/pull/375): reduced the public tree from 1,226 to 360 files, removed raw transcripts/prompts/session material/retired Firebase and automation code, preserved 19 useful regressions under `tests/regression`, and made the README flagship-ready.
- Removed Vantage, Vicinity, and Codex promotions from JobFilter's main customer journey while preserving their routes.
- Cleaned 289 historical JobFilter PR bodies, removed 434 generated footer/session lines, and normalised 41 generated title prefixes without deleting technical review evidence.
- Deleted 109 verified merged branches across active public repositories; JobFilter now has only `main` and no open PRs.
- Enabled JobFilter branch protection, automatic merged-branch deletion, Dependabot security updates, vulnerability alerts, secret scanning, and push protection.
- Closed four obsolete Dependabot PRs and dismissed 21 alerts that referenced only the deleted legacy Firebase manifest. The active root dependency audit is clean.
- Merged portfolio PR [#1](https://github.com/manazoid4/mazos-site/pull/1): JobFilter is now the primary case study, supporting-project descriptions reflect repository reality, and `/mazos` is a factual secondary case study instead of a competing pitch.
- Updated JobFilter repository description, homepage, and topics for public discovery.
- Verified production deployments at `jobfilter.uk`, `mazos-site.vercel.app`, and `/mazos`.

## Files changed

- JobFilter: `leadEngine/sourceConfig.ts`, production middleware/routes, CI and PR templates, primary homepage/pricing/footer copy, dependency manifests, README, and `tests/regression/`.
- JobFilter public cleanup: removed operational vaults, model transcripts, prompts, session logs, stale audits, n8n workflows, retired Firebase, old migration helpers, and unused tool folders from the current tree.
- Portfolio: `app/page.tsx`, `app/mazos/page.tsx`, `app/globals.css`, `app/layout.tsx`, README, Next config, and dependency manifests.

## Decisions made

- JobFilter is the flagship because it has the strongest production and verification evidence.
- Public copy states current limitations directly. A live product is not presented as commercially proven while 42 valid audit scans yield no sellable result.
- MAZos is supporting operator tooling, not the first concept a recruiter must understand.
- Historical Git objects were not rewritten. Removed public-tree material remains recoverable from Git history, avoiding force-push and audit-evidence destruction.
- Archived repositories and unmerged branches were preserved unless a branch was proven merged.

## Next steps

- Prove lead supply with configured EPC, Companies House, planning/source coverage, then rerun the 42-scan sellable-lead audit.
- Configure live Stripe price IDs, WhatsApp credentials, and required Supabase migrations/tables.
- Simplify JobFilter's oversized 114-route surface around the scanner, results, pricing, account, and delivery journey.
- Add employer/recruiter-specific profile details when the founder chooses a target role, biography, location precision, and CV history.
