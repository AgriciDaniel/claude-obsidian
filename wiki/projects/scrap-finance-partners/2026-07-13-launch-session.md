---
type: session
project: scrap-finance-partners
date: 2026-07-13
tags: [launch, redesign, yardledger]
---

# Scrap Finance Partners — Launch-Ready Redesign (2026-07-13)

## Shipped (PR #3, merged to master, Vercel prod live)
- Quiet-industrial redesign: killed marquee ticker, gradient text, pulse dots, brutalist shadows, 7.5rem all-caps
- Mobile nav added (was none); dead contact + health-check forms wired to /api/lead (Resend, key in Vercel env)
- New /software page: **YardLedger** — Fred/Xero CSV → stock reconciliation, margin/tonne, month-end pack. £149/mo + £39/seat + £99/site, 3-month money-back, 13% to charity
- Launch blockers: privacy policy, robots.txt, sitemap, metadataBase, noindex demo, internal pages (/agents, /growth-hub, /knowledge) removed from public build
- Doctrine words fixed (retainer, Deliverable, KPI Dashboards); broken ink-tertiary token defined
- Deleted duplicate Vercel projects: scrap-finance-partners1, scrap-finance-partners-fzb7

## Key research findings (3 agent audits)
- Niche open: nobody combines FD-level + scrap knowledge + Fred fluency; "I speak Fred" = unclaimed position
- Market FD pricing £1.5k–£5k/mo → current £500/£1k/£2k tiers are under-priced
- AML supervision (HMRC or professional body) REQUIRED before trading — criminal offence otherwise; ICO reg + PI insurance too
- Trust: phone number, founder name/face, BMRA service membership badge

## Open items
- Founder name/photo not on site (needs uncle's sign-off)
- Real phone number
- Company legal identity in footer (TODO comment in site-footer.tsx)
- Stale `main` branch on repo (default is `master`) — consider deleting
- OG image still missing