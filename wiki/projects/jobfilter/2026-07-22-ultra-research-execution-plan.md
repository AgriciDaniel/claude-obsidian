---
date: 2026-07-22
project: jobfilter
type: implementation-plan
status: proposed
owner: manazoid4
research: multi-agent
---

# JobFilter Ultra-Research Execution Plan

## Executive decision

**Paid/public launch is NO-GO.** JobFilter is suitable for a supervised demo and a founder-assisted discovery pilot only after the immediate security and data-integrity blockers are closed.

The product should become a narrow **public-works opportunity qualification tool for small employing contractors**, not a generic domestic “trades leads” product and not a paid wrapper around free tender alerts.

Recommended initial customer:

- UK construction or maintenance SME with roughly 5–25 staff
- some B2B or public-sector experience
- able to bid directly or pursue subcontract work
- target contract value around £30k–£500k
- first wedge: Birmingham/West Midlands electrical, M&E/maintenance and refurbishment firms

Recommended promise:

> Know which public works opportunities fit your firm—and which to skip—before you waste time bidding.

Core job-to-be-done:

> When a public works notice appears, tell me whether to BID, WATCH, pursue the SUBCONTRACT route, or SKIP—and show me the evidence and missing requirements before I waste an estimator's morning.

## Why this is the right product

Find a Tender is free, supports location and SME filters, saved searches and email notifications, and exposes reusable OCDS data. JobFilter therefore cannot sustainably charge for notice access, basic filtering, speed or alerts alone. The paid value must be **company-aware qualification, evidence, next action and accumulated outcome learning**.

The durable moat is the map between:

`firm capabilities -> notice requirements -> decision -> action -> outcome`

It is not access to public data.

## Current truth — 22 July 2026

### What is genuinely working

- Production home, scanner and pricing routes return HTTP 200.
- Production correctly returns 404 for `/test`, `/test/intake`, `/dev-portal` and `/api/status`.
- `main` is protected and requires the `check` status; administrators are included.
- Draft PR #383 makes Find a Tender the primary current-notice path, blocks fabricated production sources, applies authoritative CPV matching, rejects stale notices and fails closed on unproven locality.
- On the PR #383 branch, typecheck, FTS fixture regression, postcode, source-readiness, free-redaction, production-source-safety, lead-quality and a clean-install Next.js build pass.
- The build emits 114 routes and no committed secret was found.

### What is not working

- Production still serves the old source/copy model. A B14 electrical 25-mile scan returned Scotland semiconductor work, electric vans, Vietnam HVDC and La Paz works.
- The same production response reported schema drift: `leads.contact_path` and `source_benchmark_runs` were missing.
- Production outcome/statistics endpoints return 500 because `lead_outcomes.updated_at` is missing.
- Production source health reported no healthy source/run evidence.
- The prior 42-valid-scan audit produced zero sellable real leads. Its current test does not include the new FTS path and does not fail CI when the commercial threshold is missed.
- Draft PR #383 is three commits ahead of `main` and has not been deployed.
- Open nightly copy PRs #384–#386 overlap the same homepage, pricing, scanner and dependency files; some reintroduce domestic-marketplace language that conflicts with the FTS product.
- The nightly agent continues opening product-polish PRs despite the earlier freeze decision.
- After a fresh `npm ci`, the required dependency audit now fails with two high findings in the Next/sharp chain and one low body-parser finding. Yesterday's green CI predates the current advisory state.
- One offline regression still expects removed “Founding 30” copy.
- The production runtime regression is not portable on Windows because it mixes `127.0.0.1`, `localhost` and a fixed port; an isolated alternative port passes.
- The vault's `index`, `ARCHITECTURE`, `DATA-MODEL`, `API`, `SETUP`, `DEPLOYMENT`, `DECISIONS` and TODO notes still describe the retired Vite/Firebase application. The repository is Next.js 16 + Supabase.

## Critical path

```text
Freeze churn
  -> merge/deploy truthful FTS foundation
  -> close security and tenant-integrity holes
  -> reconcile production schema
  -> prove payment and cancellation lifecycle
  -> run 90-day supply/quality benchmark
  -> validate company-aware decisions with design partners
  -> run coverage-gated paid concierge pilot
  -> productise self-service only if the evidence gates pass
```

No new feature, copy-polish run, national trade page, planning/EPC adapter, AI bid-writing feature or paid acquisition outranks this path.

## Phase 0 — containment and one reviewed release (days 0–3)

### 0.1 Freeze automated product churn

- Pause NightlyBuildAgent and any autonomous copy/polish automation for JobFilter.
- Do not open new implementation PRs until the current queue is classified.
- Treat PR #383 as the foundation branch.
- Review PRs #381 and #384–#386 against the new product contract; retain only changes that support public-works qualification.
- Close superseded or contradictory PRs instead of merging overlapping versions of homepage/pricing/scanner copy.

Definition of done:

- One active release PR, one source of truth, no automated product PR creation.

### 0.2 Make PR #383 releasable

- Rebase on the chosen current `main` after PR triage.
- Resolve the current two high dependency advisories without a blind downgrade or `npm audit fix --force`; verify Next image/build behaviour after any sharp override/update.
- Update or remove the stale “Founding 30” copy regression.
- Make the runtime test choose an available port and use one host consistently.
- Rerun every required CI gate from a clean install.

Definition of done:

- Fresh `npm ci`, zero high/critical production audit findings, all regressions green, build green, preview reviewed, draft removed.

### 0.3 Close immediately exploitable application paths

The following must be authenticated, ownership-checked, signed, rate-limited or removed before the next paid/public release:

- outcome and flag mutations in `server/routes/outcomeReport.ts`
- arbitrary branded email sending in `server/routes/leadEmailChase.ts`
- public n8n handlers in `app/api/n8n/*`
- paid object bypass in `server/routes/startSignals.ts`
- query-string owner/subscription bypass in `server/routes/subscriptionStatus.ts`
- unmatched catch-all API requests that do not terminate with an explicit 404

Escape all user-controlled content placed into outbound HTML.

Definition of done:

- Anonymous callers cannot mutate another tenant, send outbound messages, obtain paid lead depth or infer entitlement.

### 0.4 Deploy one truthful public narrative

Every primary surface must describe one product: public-works opportunity qualification.

Remove or qualify:

- domestic extensions/homeowner jobs
- “before Checkatrade” and Bark/MyBuilder auction comparisons
- exclusive postcode patches or territory scarcity
- guaranteed volumes
- planning/EPC/energy/company signals not proven live
- “before the job goes public”
- budget-confirmed WhatsApp leads
- “one job pays for a year” gross-value arithmetic

Primary journey:

`/ -> /find-jobs -> /methodology or /trust -> /pricing -> /signup -> /activation-pending -> /dashboard -> /leads/[id] -> /account`

Keep auth/reset/legal as supporting routes. Remove Vantage, Vicinity, Codex, Tradie Zone/Stack, compliance packs, calculators and consumer intake from primary navigation until the qualification product works.

Definition of done:

- Production content and API behaviour match the reviewed SHA; a live claims inventory has evidence for every material promise.

### 0.5 Repair the vault source of truth

Update the core project notes to Next.js 16 + Supabase, the active repository path, the FTS-first source model and the current blockers. Archive obsolete Firebase/Vite statements rather than leaving contradictory operating instructions.

## Phase 1 — security, schema and revenue integrity (days 3–14)

### 1.1 Reconcile Supabase from a clean staging database

- Create one reconciliation migration rather than continuing to layer `CREATE TABLE IF NOT EXISTS` over conflicting types.
- Resolve `subscriptions.user_id`, plan fields, profiles, leads, `contact_path`, `source_benchmark_runs` and `lead_outcomes.updated_at` conflicts.
- Add foreign keys and RLS to every user-owned or PII table, including outcomes, delivery events, alerts, benchmarks and audits.
- Define data retention/deletion for IP addresses, phone numbers, full message bodies and raw Stripe/n8n payloads.
- Reset a staging project and apply the complete ordered migration chain.
- Compare staging and production schema with an automated contract check.
- Test with two real auth users: each can access only their own profile, leads, outcomes, alerts, subscriptions and delivery events.

Definition of done:

- Clean reset succeeds, schema contract passes, two-user isolation passes, production drift is zero.

### 1.2 Repair the Stripe lifecycle

- Derive checkout user ID and email from the authenticated Supabase session; never trust client metadata.
- Make webhook claiming and business-state mutation atomic and retry-safe.
- Do not record an event processed or return success when activation/cancellation handling failed.
- Move the customer portal to a registered authenticated App route.
- Add `/account` to desktop/mobile member navigation.
- Implement explicit past-due, cancelled, reactivated and checkout-cancelled UI states.
- Prove test checkout -> webhook -> entitlement -> payment failure -> cancellation -> portal -> reactivation.

Definition of done:

- Duplicate webhooks are harmless; failed handlers retry; one user cannot affect another; cancellation is discoverable and works.

### 1.3 Make alert delivery truthful

- Store and pass a customer's locality/region/radius into scheduled scans.
- Distinguish genuine empty demand from partial or total source failure.
- Return explicit provider success/failure from email and WhatsApp functions.
- Do not advance `last_sent_at` on failed delivery.
- Add a durable outbox, retry policy, idempotency key and delivery receipt.
- Make cadence copy match actual infrastructure. Do not call once-daily cron “instant” or “hourly.”
- Let users pause, edit and delete alerts.
- Use approved Meta proactive templates with consent and opt-out controls before enabling WhatsApp.

Definition of done:

- A local alert cannot contain unproven distant work; a provider failure is visible and retried; the advertised cadence is measured.

### 1.4 Establish one scoring/decision contract

- Remove the conflicting 90/75/60 versus 80/50 thresholds.
- Apply all fusion/outcome adjustments before calculating the final tier/readiness.
- Never normalize an unknown publication date to “now.”
- Version the scoring policy and store factor/provenance breakdown.
- Make BID/WATCH/SUBCONTRACT/SKIP the primary user decision; keep the numeric score as supporting evidence.

Definition of done:

- UI, API, methodology and stored records agree for every score and decision.

### 1.5 Add operational visibility

- Replace the shallow health check with separate readiness for database, source ingestion, Stripe, email and WhatsApp.
- Add structured event/request IDs and error aggregation.
- Monitor source freshness, scan latency, webhook failures, schema errors, delivery retries and zero-result spikes.
- Reconcile privacy/legal copy with Vercel Analytics, Meta/Resend/Stripe/Supabase and actual retention.

## Phase 2 — prove lead supply before building more product (days 7–30)

### 2.1 Run a real 90-day FTS supply audit

Build a reproducible corpus of 100–500 current notices across the proposed West Midlands wedge. Segment by:

- CPV/service line
- notice type: pipeline, preliminary engagement, planned procurement, tender, award
- SME suitability
- buyer and region/NUTS/locality evidence
- contract value and lot value
- deadline and response route
- eligibility/accreditation requirements
- direct-bid versus subcontract potential
- freshness, duplicate and amendment state

Do not treat a national match as a local opportunity. The benchmark must exercise the same production pipeline and must fail CI/release gating when thresholds are missed.

### 2.2 Replace postcode-only onboarding with a firm profile

Minimum profile:

- services and CPVs
- counties/regions plus genuine travel radius where postcode evidence exists
- direct-bid/subcontract preference
- contract/lot value range
- turnover and employee band
- insurance, accreditations and framework memberships
- public-bid experience
- current bid capacity
- hard exclusions

### 2.3 Build the free coverage report

Before signup or payment, show:

- last 30/90-day opportunity counts for the firm profile
- completeness and source coverage
- one fully explained sample decision
- whether the profile meets the minimum coverage gate
- honest “insufficient coverage” when it does not

Do not charge when the profile fails the gate.

### 2.4 Build decision cards, not feed cards

Each opportunity must show:

- BID / WATCH / SUBCONTRACT / SKIP
- why it fits
- why it may fail
- missing eligibility evidence
- verified delivery geography and provenance
- value/lot confidence
- deadline and response route
- buyer/incumbent/history context when available
- next action and outcome capture

## Phase 3 — founder-assisted validation (days 14–45)

### 3.1 Conduct 15–20 problem interviews

Recruit employing firms with recent B2B/public procurement experience. Ask them to show the last three notices they pursued or rejected. Measure the real review process, bid effort, disqualifiers and missing evidence. Do not recruit generic domestic sole traders for this test.

### 3.2 Recruit ten West Midlands design partners

Recommended cohort:

- electrical contractors
- M&E/building maintenance firms
- refurbishment/small works contractors

Give each firm five real, manually reviewed decisions. Record whether they agree, what action they take and how long review took.

### 3.3 Test paid concierge delivery

Packaging:

- **Free coverage report:** profile, recent counts, one explained sample
- **Founding pilot — £39/month per firm:** qualified decisions, saved exclusions, deadline reminders and outcomes
- **Assisted test — about £99/month:** human-checked shortlist plus monthly profile/qualification review

Avoid “£39 forever” and do not use a fake £79 anchor. Guarantee the agreed usefulness/coverage threshold, not a won contract.

Recommended promise:

> If your first 30 days do not produce the pre-agreed minimum number of qualified opportunities, we refund the month.

Use email first. WhatsApp is a delivery channel, not the product, and should not delay learning unless the cohort demands it.

## Phase 4 — productise only after evidence (days 31–90)

### 4.1 Instrument the full funnel

North-star metric:

> Paid accounts with at least one user-confirmed action-worthy opportunity in the trailing 30 days.

Track without leaking PII:

- visit -> coverage check -> profile completion
- coverage pass/fail
- time to first qualified opportunity
- opportunity opened/saved/actioned
- alert opt-in and alert-to-detail click
- checkout -> activation -> cancellation/refund
- BID/WATCH/SUBCONTRACT/SKIP and dismissal reason
- expression of interest, bid, shortlist, win/loss
- self-reported bid time and time saved
- outcome by source, CPV, buyer, value band and score version

### 4.2 Complete the self-service journey

- Preserve the middleware `next` destination through login.
- Add honest loading, empty, degraded and error states.
- Put account/billing in navigation.
- Let users edit firm profile, alert preferences and WhatsApp consent.
- Implement account deletion/export.
- Either rebuild consumer intake as tenant-owned end-to-end functionality or remove it from launch. Today it uses a random local username, loses the owner, stores the lead in the homeowner browser and redirects the homeowner to a protected tradesperson route.

### 4.3 Pass accessibility and mobile release gates

- Associated labels and visible keyboard focus
- live regions for errors/status
- WCAG AA colour contrast
- step/progress announcements and focus transfer
- 200% zoom and reduced motion
- 320/375/430px populated dashboard/account/lead states
- no clipped action groups or horizontal data loss

### 4.4 Rationalise the runtime

- Choose native App routes as the default API boundary.
- Remove or migrate duplicate App/Pages/Express implementations.
- Retain SEO trade/city pages only when truthful and useful; keep them out of the core navigation until conversion evidence exists.
- Reduce the 114-route product surface after reachability and search-value review.

## Proposed evidence gates

These thresholds are proposed starting points and should be accepted or revised before the benchmark begins.

### Gate A — deploy the FTS foundation

- Zero high/critical production dependency findings
- All required tests and clean build pass
- All high-risk unauthenticated endpoints closed
- Production SHA equals reviewed SHA
- No fabricated, stale, unproven-trade or unproven-locality result appears
- Source outage is shown as degraded service, not “no demand”

### Gate B — invite paid pilot customers

- 100–500 human-labelled notices
- precision@10 at least 80%
- duplicate rate below 2%
- stale opportunity rate below 1%
- every displayed decision has source, value/location confidence, deadline and response route provenance
- at least 80% of ten target profiles receive two qualified opportunities per month
- at least 50% receive one user-confirmed action-worthy opportunity per month
- full Stripe lifecycle and two-user tenant isolation pass

### Gate C — expand to 30–50 account regional beta

- at least 10 paid design partners complete the first month
- at least 70% month-2 logo retention in the founding cohort
- at least 50% of active accounts confirm one action-worthy opportunity in 30 days
- measured reduction in review time or avoided unsuitable bids
- refund/cancellation causes are understood and no systematic coverage failure remains
- browser E2E, accessibility, payment, cancellation, alerts and degraded-source states pass

If Gate B fails, widen from postcode-radius micro-trades to region-wide small contractors and subcontract/retender intelligence. Do not revive unproven domestic lead claims.

## 30/60/90-day delivery map

### Days 0–30

- freeze automated PR churn
- triage/close overlapping PRs and release #383 safely
- close security/outbound/entitlement holes
- reconcile Supabase and prove tenant isolation
- fix Stripe identity, webhook and cancellation
- align all public/legal/trust copy
- run 90-day supply audit
- define firm profile and coverage gate
- instrument core funnel/quality events
- interview 15–20 firms and recruit ten design partners

### Days 31–60

- start £39 founder-assisted cohort
- test roughly £99 assisted qualification
- deliver company-aware decision cards and a daily/weekly exception digest
- capture dismissals, actions, bid time and outcomes
- add pipeline and preliminary-engagement notices if the supply audit supports them
- add award/incumbent/retender context where it changes decisions
- publish only verified coverage and customer proof

### Days 61–90

- proceed to 30–50 account regional beta only if Gate C inputs are green
- productise profile, billing, alerts and account control
- pass browser/accessibility/mobile release suite
- add one adjacent trade or one adjacent region, not both
- begin founder-led outbound to firms visible in award data
- test partnerships with bid consultants, procurement advisers and Meet the Buyer programmes
- publish evidence-led regional tender pages backed by current data

## Explicit defer list

Do not build or market these before Gate B:

- domestic homeowner lead marketplace
- planning/EPC prospecting
- exclusive territories or scarcity counters
- national coverage across 18 trades
- WhatsApp as a headline feature
- AI bid writing
- broad paid acquisition
- annual pricing
- merchant/referral partnerships unrelated to the pilot
- generic social/content automation
- visual polish unrelated to accessibility or the core journey

## Founder-only actions

1. Approve the product decision: public-works qualification for employing SMEs.
2. Approve the first wedge: West Midlands electrical, M&E/maintenance and refurbishment.
3. Pause the nightly JobFilter automation and authorise closure of superseded PRs.
4. Provide/confirm a staging Supabase project and run the approved reconciliation migration.
5. Confirm test/live Stripe price IDs and webhook endpoint after the code lifecycle is repaired.
6. Confirm Resend sender/domain and `CRON_SECRET` before alert testing.
7. Decide whether Meta WhatsApp is required for the pilot; if yes, approve templates and consent/opt-out flow.
8. Accept or revise Gates B/C before data collection begins.
9. Recruit the first ten design partners; agents can prepare the list and scripts, but founder credibility is the highest-leverage outreach channel.

## Current external evidence

- The Cabinet Office states that Find a Tender is free, supports saved-search alerts, SME filters and reusable OCDS data: https://www.gov.uk/government/publications/procurement-act-2023-short-guides/buyers-and-suppliers-how-to-use-the-central-digital-platform-the-enhanced-find-a-tender-service-html
- FTS pipeline notices provide up to 18 months of earlier procurement visibility and are explicitly intended to help SMEs plan: https://www.gov.uk/government/publications/procurement-act-2023-short-guides/uk1-the-new-pipeline-notice-html
- FTS exposes notice lifecycle data through the OCDS release-package API: https://www.gov.uk/government/publications/open-contracting
- The Small and Medium Business Hub confirms the current government direction toward SME procurement participation: https://www.gov.uk/guidance/small-and-medium-business-hub
- Current low-cost competitors include free alerts from Scrymint and paid tender intelligence such as TenderTracker; this confirms that JobFilter must sell decision quality rather than feed access: https://scrymint.com/ and https://tendertracker.co.uk/pricing

## Immediate next execution batch

One bounded batch should now be opened from this plan:

1. pause nightly automation and triage PRs #381/#383–#386;
2. make #383 green against today's audit/test state;
3. close the unauthenticated service-role/outbound/paid-bypass endpoints;
4. deploy the truthful FTS release;
5. create the Supabase reconciliation migration and staging reset proof.

Do not mix the 90-day benchmark or new product UI into that security/release batch.
