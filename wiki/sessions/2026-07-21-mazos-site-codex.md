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

## Files changed

- `wiki/sessions/2026-07-21-mazos-site-codex.md` only.
- No project repository files were changed.

## Decisions made

- Treat the audit as a conversion and credibility improvement plan, not a redesign: the evidence-led brutalist visual system is coherent and should be preserved.
- Position Manazir as an AI-native product engineer for operational B2B software: turning messy, data-heavy workflows into auditable products with human control.
- JobFilter should be demoted from `Production`/flagship until it migrates to Find a Tender, proves relevance on a labelled evaluation set, and produces external user evidence.
- Agent Nudge is the best temporary technical flagship for AI developer-tool and agent-governance opportunities; MAZos remains supporting method evidence.
- Pause new product creation for 90 days. Recall and OpenFlowKit should be demoted until they have complete end-to-end proof or external usage.
- Use a default opportunity allocation of 70% employment pipeline, 20% external product proof/pilots, and 10% founder exploration.
- Highest-priority fixes are: repair JobFilter's source and product identity; fix GitHub/career identity; create external proof; clarify primary audience/CTA; add CI/branch protection; and then complete the site quality work.
- Keep MAZos secondary as method evidence; use Agent Nudge as the temporary technical flagship and restore JobFilter only after source and customer validation.

## Next steps

1. Immediately remove/demote JobFilter's `Production` claim and migrate/dual-source ingestion to the Find a Tender OCDS API with pagination and a labelled relevance benchmark.
2. Choose one JobFilter market: public-procurement qualification for construction SMEs or planning/EPC prospecting for local trades; stop mixing the two propositions.
3. Complete the GitHub profile, pin intentional repositories, add licenses where open source is claimed, publish a one-page CV, and link the correct LinkedIn/profile.
4. Recruit 10 procurement/trades interviews and 5 multi-agent developers; pursue one paid JobFilter pilot and five Agent Nudge testers.
5. Publish reproducible evidence: the source-assumption postmortem, an Agent Nudge benchmark, and a verification-receipt explainer.
6. Add GitHub Actions, tests/link checks, branch protection, Dependabot, and Node/npm pinning across promoted repositories; repair OpenFlowKit's failing main-branch CI.
7. Fix the portfolio's ARIA, metadata, image, security-header, and conversion findings after the truth/positioning changes.
8. Track qualified conversations, pilots, active users, introductions, interviews, and rejection reasons weekly; do not use project count or commit volume as success metrics.
