# FlowLens — 24-Month Financial Model

**Date:** 2026-07-11. Solo founder, UK market, Vercel + Supabase + Stripe + AI API stack.
**Honesty note up front:** repo docs contain no evidence of current revenue (pricing rationale + personas only). This model therefore starts from £0 MRR at month 0. If real MRR exists, shift the curve right by wherever you actually are.

Tier data from `docs/product/pricing.md`: Founder £19/mo, Starter £120/mo, Team £450/mo, Business £1,200/mo, Agency £650/mo, Enterprise custom.

---

## Assumptions — walked through, with reasoning

**A1. Acquisition channel = founder-led outbound + content, no paid ads.**
Solo founder, no budget line for CAC. Realistic demo volume: 8–15 qualified demos/month once a repeatable pitch exists (months 4+), near zero in months 1–3 while the desktop capture app (currently "not yet implemented") gets finished. *This is the assumption most people skip: FlowLens cannot sell until capture actually works — the wow moment depends on it.*

**A2. Sales cycle by tier.**
Founder tier: self-serve, days. Starter: 2–4 weeks. Team/Business: 6–12 weeks (COO buyer, security questions, at least one stakeholder demo). Model consequence: no Business-tier revenue before month 6 no matter how good the product is.

**A3. Demo → paid conversion: 10–25% blended.**
Range not point. Comparable PLG-ish B2B tools convert 15–20% of qualified demos; solo founder without case studies sits at the low end initially, improves with proof. Use 10% months 4–9, 20% months 10+.

**A4. Churn: 3–6%/month early, 2–3% later.**
Monthly contracts, unproven category, no integrations shipped yet (integrations package is "typed stubs"). Early adopters churn hard when routing into Jira/Slack isn't real. Falls once integrations land and captures accumulate (switching cost = your evidence library lives here).

**A5. Mix shifts upmarket over time.**
Months 4–9: mostly Founder (£19) + Starter (£120) — the tiers a solo founder can close. Months 10–24: Team/Agency enter; maybe 1–2 Business by month 18–24. Blended ARPU: **£60–90/mo early → £150–250/mo by month 24.** Wide range because one Business account (£1,200) moves blended ARPU more than ten Founder accounts.

**A6. Infra cost per active workspace: £2–8/mo.**
Vercel Pro £16/mo flat-ish; Supabase £20–25/mo base until storage-heavy; AI spend dominates: workflow analysis on capture ≈ £0.10–0.50/capture (long-context calls), power workspace does 20–60 captures/mo → £2–30/mo AI cost at the extreme. Mitigation already in repo (mock provider abstraction → can route cheap models for extraction, expensive only for synthesis). Gross margin stays **85–92%** — normal SaaS.

**A7. Fixed costs: £60–120/mo.**
Vercel + Supabase + Sentry/PostHog free tiers + domain + Stripe fixed. Labour = you, unpaid. That's the entire burn. Runway is not the constraint; **your attention is.**

---

## The model — three scenarios, 24 months

MRR at key months (customers × blended ARPU, churn-adjusted):

| Month | Pessimistic | Base | Optimistic |
|---|---|---|---|
| 3 | £0 (still building capture) | £60 (3 Founder) | £300 (2 Starter + 3 Founder) |
| 6 | £150 | £700 (2 Starter + ~5 Founder + 1 Team trial converting) | £2,200 |
| 9 | £400 | £1,800 | £4,500 |
| 12 | £800 | £3,500 (≈ 6 Starter + 4 Team-ish + tail) | £8,000 |
| 18 | £1,500 | £7,500 (first Business acct assumed here) | £18,000 |
| 24 | £2,500 | £13,000 | £32,000 |

Costs at month 12 (base): infra ~£150/mo, AI ~£200/mo, tools ~£50/mo → **~£400/mo total → ~89% gross margin, ~£3,100/mo gross profit.**

What separates the scenarios is **not price or churn — it's demos/month**. Pessimistic = 3/mo (side-project attention). Base = 10/mo. Optimistic = 20/mo with a repeatable channel (e.g. MSP/IT communities, r/msp, UK ops communities). Everything else is second-order.

## MRR needed to go full-time

UK solo founder, modest: £3,000/mo net → need ~£3,800–4,200/mo gross (income tax/NI on ~£46–50k/yr equivalent) → with 89% margin: **≈ £4,300–4,700 MRR**.
- Base case crosses this around **month 13–14**.
- Optimistic: month 8–9. Pessimistic: never inside 24 months.
- Composition matters: that's ~4 Business, or ~10 Team, or ~36 Starter accounts. The Business-tier path needs 4 logos; the Starter path needs 36. Four logos is the achievable solo number — which means the model quietly says: **the real business is 5–10 mid-market accounts, not a thousand founders at £19.**

## The 3 assumptions the whole model is most sensitive to

1. **Demos/month (A1).** ±2x on this input = ±2x on every MRR row. It's a pure function of your available attention — which is currently split across 6+ projects (see portfolio synthesis). This assumption is really "does FlowLens get your focus."
2. **Capture app actually shipping (A1 dependency).** Desktop app + extension are typed stubs today. Until capture works end-to-end there is no wow moment, no demo, no revenue — every month of build delay shifts the entire table right by a month. Binary risk, not a range.
3. **Team/Business conversion by a solo founder (A2+A3 upper tiers).** If mid-market buyers won't buy from a one-person company (procurement, SOC2 questions), ceiling is the Starter/Founder tier mix → month-24 base drops from £13k to ~£4–5k. The Enterprise/Business tiers on the pricing page are currently untested hypotheses.

## What would change this model fastest

Run 5 unpaid pilot captures with real UK ops/MSP teams in the next 30 days. Each pilot resolves A3 (do they convert), A4 (do they stay), and the tier-mix question simultaneously — no spreadsheet iteration can.
