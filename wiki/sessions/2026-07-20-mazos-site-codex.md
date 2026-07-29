---
date: 2026-07-20
project: mazos-site
agent: codex
status: completed
---
## What I did
- Audited `https://mazos-site.vercel.app/` and `/mazos` as a digital CV portfolio from recruiter, product/IA, repository-truth, visual-design, accessibility, responsive, performance, and SEO perspectives.
- Compared the live portfolio claims with public GitHub repository metadata and README implementation/status evidence.
- Inspected the `manazoid4/mazos-site` source, tested desktop and 390px mobile rendering, verified public demo destinations, and ran TypeScript plus a production build.

## Files changed
- `wiki/sessions/2026-07-20-mazos-site-codex.md`
- No `mazos-site` project files changed; audit only.

## Decisions made
- `/` should be the canonical digital CV and make Manazir, target role, proof, experience, skills, CV, and contact the organising principle.
- `/mazos` should be a subordinate MAZos engineering case study, not a competing homepage or investor pitch.
- Replace the equal six-card catalogue with 2–3 evidence-rich featured projects and a compact additional/archived work section.
- Use precise lifecycle labels such as Public demo, Working MVP, Internal tool, Prototype, and Archived; do not call deployed prototypes "Live" or the portfolio "revenue products" without evidence.
- Populate copy from implemented repository evidence, while keeping business outcomes and personal contribution manually curated.

## Next steps
- Rewrite the information architecture and project manifest, including unique Case study / Live demo / GitHub actions.
- Add role positioning, CV download, experience, capabilities, project screenshots, dates, ownership, engineering decisions, and verifiable outcomes.
- Correct the current credibility conflicts, especially InkWeave's archived status, mock/prototype limitations in FlowLens and Recall, the five-versus-six project count, and receipt-backed/daily-use claims.
- Improve link target sizes/names, route metadata, sitemap/robots, focus styling, mobile spacing, dependency audit findings, and Next.js workspace-root warning.
- Re-run the design and technical audit after implementation.
