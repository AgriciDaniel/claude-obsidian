---
date: 2026-07-21
project: mazos-site
agent: codex
status: completed
---
## What I did

- Audited the live portfolio at `https://mazos-site.vercel.app/` and the `/mazos` case study from product, conversion, visual design, accessibility, performance, SEO, security, and responsive perspectives.
- Audited `github.com/manazoid4/mazos-site` at commit `cd2ba2458a1583db54c55a87a85e9456b23686e7` for architecture, dependencies, tests, CI, branch protection, repository metadata, and deployment resilience.
- Expanded the review into a multi-perspective opportunity audit covering career positioning, founder/product viability, portfolio allocation, GitHub reputation, external validation, distribution, and current UK market conditions.
- Found a critical JobFilter source mismatch: the production implementation uses Contracts Finder, while post-24-February-2025 procurement opportunities are published on Find a Tender. A live FTS API sample returned current electrical, construction, maintenance, and roofing opportunities.
- Compared JobFilter's concept and claims against current procurement-intelligence competitors and found that it conflates public tenders, planning/EPC prospecting, and consumer lead marketplaces.
- Audited the public GitHub profile: 1,410 contributions but no real name, bio, profile README, website, or pinned repositories; all highlighted original repositories currently have zero stars/forks and no visible external adoption.
- Verified `npm run lint` and `npm run build` pass; `npm audit --omit=dev` reports zero vulnerabilities.
- Measured Lighthouse: mobile 98 performance / 100 accessibility / 100 best practices / 100 SEO; desktop 100 across all four categories.
- Confirmed all tested live product, asset, and GitHub links return HTTP 200.
- Implemented the audit in two reviewable branches with independent product/career, founder, repository, accessibility, visual, security, and reliability perspectives.
- Rebuilt JobFilter's live procurement path around bounded Find a Tender OCDS packages, authoritative CPV matching, latest-release merging, expiry filtering, source readiness, safe pagination/retries, cancellation, and fail-closed radius evidence.
- Truth-aligned the portfolio around operational B2B/applied-AI engineering, promoted Agent Nudge as the current technical flagship, labelled JobFilter as source repair/validation, and added accessibility, metadata, local assets, security headers, deterministic tests, CI, and a working static start path.
- Opened draft PRs `JobFilterV1#383` and `mazos-site#4`; all required GitHub Actions and Vercel preview checks passed.
- Added `verify`-gated PR protection to `mazos-site/main`, enforced for admins with conversation resolution and force-push/deletion disabled. Enabled Dependabot security updates and improved repository metadata.
- Re-ran the portfolio work as an ultrawork overhaul against the Inference Group Junior AI Engineer archetype. Direct research found the advert is stale/syndicated and its Exeter location is not reliable, so the portfolio now targets the broader junior applied-AI engineering category rather than one expired vacancy.
- Rebuilt the homepage positioning, information architecture, project copy, responsive layout, metadata, social card, sitemap, tests, and smoke checks around agent infrastructure, public-data pipelines, integrations, verification, and production safeguards.
- Removed MAZos from recruiter navigation, homepage, metadata, and sitemap; the legacy route is now a no-index handoff into outcome-led project evidence.
- Replaced the old JobFilter image with responsive local evidence captured from the repaired branch: a B14 building scan that returns zero rather than inventing a locality match.
- Updated draft PR `mazos-site#4` at commit `2a622fd`; both required `verify` runs and the Vercel preview passed. Independent positioning and visual QA reported no remaining P0/P1 blockers.

## Files changed

- `C:\Users\manaz\JobFilterV1`: FTS fetch/mapping, postcode/radius logic, scan cancellation, source configuration, Find Jobs copy, CI, README, fixtures, and regression tests on `agents/jobfilter-find-a-tender`.
- `C:\Users\manaz\Projects\mazos-site`: portfolio/case-study HTML, styles, metadata, headers, local images, runtime scripts, CI, tests, and README on `agents/portfolio-truth-and-quality`.
- Latest portfolio overhaul adds `public/jobfilter-scan-result.webp` and `public/jobfilter-scan-result-mobile.webp`, rewrites `app/page.tsx`, reduces `app/mazos/page.tsx` to a no-index handoff, and refreshes social/SEO assets and verification contracts.
- `wiki/sessions/2026-07-21-mazos-site-codex.md`.

## Decisions made

- Treat the audit as a conversion and credibility improvement plan, not a redesign: the evidence-led brutalist visual system is coherent and should be preserved.
- Position Manazir as an AI-native product engineer for operational B2B software: turning messy, data-heavy workflows into auditable products with human control.
- JobFilter should be demoted from `Production`/flagship until it migrates to Find a Tender, proves relevance on a labelled evaluation set, and produces external user evidence.
- Agent Nudge is the best temporary technical flagship for AI developer-tool and agent-governance opportunities; MAZos remains supporting method evidence.
- Pause new product creation for 90 days. Recall and OpenFlowKit should be demoted until they have complete end-to-end proof or external usage.
- Use a default opportunity allocation of 70% employment pipeline, 20% external product proof/pilots, and 10% founder exploration.
- Highest-priority fixes are: repair JobFilter's source and product identity; fix GitHub/career identity; create external proof; clarify primary audience/CTA; add CI/branch protection; and then complete the site quality work.
- Keep MAZos secondary as method evidence; use Agent Nudge as the temporary technical flagship and restore JobFilter only after source and customer validation.
- Preserve honest zero-result states: buyer headquarters are not delivery-location evidence, and unproven distance must not be treated as zero miles.
- Do not merge or deploy automatically; both implementation PRs remain drafts for owner review.
- Treat the linked Inference advert as a role archetype, not a live Exeter vacancy. Lead with junior applied-AI engineering while keeping model-development claims separate from agent infrastructure and software verification.
- Do not keyword-stuff Python, model evaluation, cloud, teamwork, or client outcomes. Those remain genuine evidence gaps and should be closed with new work or confirmed personal information.

## Next steps

1. Review the green draft PRs: `https://github.com/manazoid4/JobFilterV1/pull/383` and `https://github.com/manazoid4/mazos-site/pull/4`.
2. Complete `JobFilterV1#382`: label 100-500 notices, resolve NUTS/locality evidence, interview 10 SMEs, run 3 pilots, and gate paid activation on actionable territory coverage.
3. Complete `mazos-site#3`: GitHub identity/profile README/pins, verified LinkedIn/CV destinations, and at least one external proof signal. GitHub profile API editing is blocked until the token has `user` scope.
4. Publish reproducible evidence: the source-assumption postmortem, an Agent Nudge benchmark, and a verification-receipt explainer.
5. Track qualified conversations, pilots, active users, introductions, interviews, and rejection reasons weekly; do not use project count or commit volume as success metrics.
6. Highest-leverage next proof: build a small Python retrieval/tool-use system over official tender documents with a labelled evaluation set, accuracy/quality metrics, latency/cost reporting, and a monitored cloud deployment.
7. Confirm and add recruiter filters only when true: permanent UK work rights, notice period/availability, on-site or relocation stance, education, a current CV, and verified LinkedIn.
