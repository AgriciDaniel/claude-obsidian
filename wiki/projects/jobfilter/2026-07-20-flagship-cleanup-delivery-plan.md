---
date: 2026-07-20
project: jobfilter
type: implementation-plan
status: proposed
owner: manazoid4
---

# JobFilter Flagship + GitHub Cleanup Delivery Plan

## Executive decision

JobFilter becomes the flagship portfolio project. Stop expanding the product until its core promise is truthful and the complete revenue path is proven.

The programme has two linked workstreams:

1. **JobFilter completion:** real signal → qualified opportunity → paid access → WhatsApp delivery → outcome receipt.
2. **Public GitHub hygiene:** clean current repository surfaces without pretending the historical development record never existed.

## Evidence snapshot — 20 July 2026

### JobFilter product

- `npm run lint` passes.
- `npm run build` passes and generates 113 routes/pages.
- Production `/api/status` is publicly accessible and reports:
  - Stripe secret/webhook configured, but every Stripe price ID is false.
  - WhatsApp is not configured.
  - Companies House is not configured.
  - EPC is not configured.
- `/test` and `/dev-portal` return HTTP 200 in production.
- The live homepage claims planning, energy, tender and company signals, early timing, exclusive territories and WhatsApp delivery beyond what production configuration proves.
- `DirectorySignal` is a guaranteed internal/fabricated data source and still enters the live ranking pool.
- The 54-case quality regression passed schema/junk checks but produced zero sellable real leads across 42 valid scans (`oneLeadRulePasses=0/42`).
- CI runs only `npm ci` and `npm run build`; there is no required unit, integration, E2E, lint, security or migration test gate.
- `npm audit` reports 17 vulnerabilities, including 9 high severity, amplified by unused legacy Vite, React Router and Vercel dependencies.
- `main` is unprotected.
- `auto-merge.yml` attempts to auto-merge every non-draft PR after the single build check.
- The vault digest workflow commits directly to `main` daily.

### JobFilter repository hygiene

- 1,226 tracked files.
- 530 tracked files under `Obsidian_Memory/`.
- 49 files under `memoryraw_claude/`.
- 37 files under `.agents/`.
- 31 files under `codex-output/`.
- 377 tracked files contain Claude/Codex/agent-generation terms.
- 76 branches total; all 75 non-main branches are associated with merged PRs.
- 64 branch names use AI/agent prefixes.
- 367 PRs total; 298 bodies and 63 titles contain explicit AI/agent terms, and 296 PRs came from AI-named branches.

### Portfolio-wide GitHub hygiene

- 14 public repositories.
- GitHub profile has no bio, website, social links or pinned repositories.
- No public repository has automatic branch deletion enabled.
- 118 non-default branches across public repos are attached to merged PRs and are safe cleanup candidates after a final manifest review.
- 7 branches require manual review before deletion.
- Repository descriptions, homepages, topics and licences are inconsistent or missing.

## Non-negotiable truth

GitHub pull requests cannot be deleted through the normal product/API. Historical PR head branch names cannot be renamed after merge. Deleting remote branches cleans the branch list but does not erase the PR record.

Therefore:

- Clean current code, docs, settings, branches, README surfaces and future PR conventions.
- Edit boilerplate PR titles/bodies only through an approved, reversible manifest.
- Delete only comments that are pure generated logs and are owned by `manazoid4`; preserve decisions, review findings and test evidence.
- Do not rewrite Git history merely to hide AI assistance.
- If zero historical AI visibility is non-negotiable, create a new squashed public repository and archive/private the current one. That is a separate high-risk migration requiring explicit approval.

## Critical path

Governance freeze → truth/security fixes → production configuration → revenue E2E → lead-quality proof → product simplification → public flagship case study → pilot launch.

No portfolio redesign or new JobFilter feature outranks this path.

## Milestone M0 — Stop churn and protect main (S)

Delivers: one controlled delivery path with no unattended merge or direct-to-main content churn.

- [ ] **0.1 Disable broad auto-merge** — DoD: no PR can merge without the required checks and an explicit human merge/approval. `[LOW] [SEC]`
- [ ] **0.2 Disable or relocate vault-direct commits** — DoD: product `main` receives no digest/session-note commits; vault output goes to the private vault repo. `[LOW]`
- [ ] **0.3 Pause NightlyBuildAgent/product-polish runs** — DoD: no scheduled agent opens or merges product changes while P0/P1 work is active. `[LOW]`
- [ ] **0.4 Protect `main`** — DoD: direct pushes are rejected, required checks are enforced and stale approvals are dismissed. `[MED] [SEC] [EXT]`
- [ ] **0.5 Enable automatic branch deletion after merge** — DoD: future merged PR branches are removed automatically. `[LOW] [EXT]`
- [ ] **0.6 Establish one PR template** — DoD: every new PR states problem, user impact, scope, verification and remaining risk without model/tool boilerplate. `[LOW]`

## Milestone M1 — Trust and security floor (M)

Delivers: production stops exposing internal surfaces or presenting fabricated signals as live work.

- [ ] **1.1 Create claims inventory** — DoD: every material live-site claim is marked `VERIFIED`, `QUALIFY`, `SAMPLE` or `REMOVE`, with code/data evidence. `[MED]`
- [ ] **1.2 Remove internal fallback leads from production results** — DoD: `DirectorySignal` can be used only in explicit demo/test fixtures and can never appear as a live/free/paid lead. `[HIGH] [SEC]`
- [ ] **1.3 Add honest scanner states** — DoD: no-results, partial-source failure and no-coverage states are explicit and never replaced with invented jobs. `[MED]`
- [ ] **1.4 Protect production diagnostics** — DoD: `/test`, `/test/intake`, `/dev-portal` and integration configuration details are unavailable to unauthenticated production users. `[MED] [SEC]`
- [ ] **1.5 Reconcile public copy with configured sources** — DoD: homepage, pricing, methodology and comparisons make no unsupported coverage, timing, exclusivity, customer, scarcity or budget claim. `[MED]`
- [ ] **1.6 Remove or verify testimonial** — DoD: the named Birmingham testimonial has permission/evidence or is removed. `[LOW] [SEC]`
- [ ] **1.7 Apply tenant-safety migrations** — DoD: `lead_outcomes` and all user-owned tables enforce per-user access, verified by two-user tests. `[HIGH] [SEC] [EXT]`
- [ ] **1.8 Add secret/dependency scanning** — DoD: secret scanning, push protection and dependency alerts are enabled; current tree and history have a reviewed redacted report. `[MED] [SEC] [EXT]`
- [ ] **1.9 Resolve dependency vulnerabilities** — DoD: zero high/critical `npm audit` findings in the production dependency graph. `[MED] [SEC]`

## Milestone M2 — One complete paid journey (L)

Delivers: one test customer can pay, activate a territory, receive a real qualified alert and lose access correctly on cancellation.

- [ ] **2.1 Choose one WhatsApp provider** — DoD: Meta Cloud API or Twilio is documented as canonical; the other implementation, env vars and legal copy are removed. `[MED] [EXT] [BLOCKED: USER]`
- [ ] **2.2 Configure the £39 monthly product/price** — DoD: Vercel exposes the correct price ID and the pricing CTA creates a Stripe test checkout. `[LOW] [EXT] [BLOCKED: USER]`
- [ ] **2.3 Verify webhook idempotency and ownership** — DoD: duplicate webhooks do not duplicate state, and one user's event cannot change another user's plan. `[HIGH] [SEC]`
- [ ] **2.4 Prove signup → checkout → activation** — DoD: a fresh test account confirms email, pays, receives the correct plan and records trade/postcode/phone. `[HIGH] [SEC] [EXT]`
- [ ] **2.5 Prove WhatsApp delivery** — DoD: one real GOLD opportunity produces one message to the test customer with no duplicates or fallback success. `[HIGH] [EXT]`
- [ ] **2.6 Prove cancellation/failure handling** — DoD: cancellation or payment failure revokes paid depth and alerts while preserving customer data and explaining recovery. `[HIGH] [SEC] [EXT]`
- [ ] **2.7 Add revenue E2E to release gate** — DoD: a repeatable staging test verifies checkout, webhook, subscription and delivery using test credentials. `[HIGH] [SEC]`

## Milestone M3 — Lead quality proof (L)

Delivers: evidence that the core product supplies genuinely useful opportunities in the chosen wedge.

- [ ] **3.1 Narrow the launch wedge** — DoD: one or two trades and one geography are selected for the pilot with a documented minimum weekly opportunity target. `[LOW] [BLOCKED: USER]`
- [ ] **3.2 Make Contracts Finder the proven baseline** — DoD: freshness, source ID, deadline, buyer, value confidence and fetch health are measured and visible internally. `[MED]`
- [ ] **3.3 Implement real distance semantics** — DoD: radius results use geospatial distance or the UI stops calling the selector miles/radius. `[HIGH]`
- [ ] **3.4 Version explainable scoring** — DoD: each opportunity stores score version and factor breakdown for source confidence, trade fit, geography, freshness, value confidence, contactability and competition risk. `[HIGH]`
- [ ] **3.5 Create a 50-case truth set** — DoD: 50 source records have human labels for relevant, irrelevant, duplicate, stale, contactable and worth-pricing. `[MED]`
- [ ] **3.6 Set quality release thresholds** — DoD: a version cannot ship unless it meets agreed precision, duplicate, staleness and empty-output thresholds on the truth set. `[MED] [BLOCKED: USER]`
- [ ] **3.7 Close the outcome loop** — DoD: users can record viewed/contacted/quoted/won/rejected/false-positive and the system reports results per score version. `[HIGH]`
- [ ] **3.8 Run a seven-day pilot sample** — DoD: the selected wedge has a seven-day report showing real opportunity volume and how many were worth contacting. `[MED] [EXT]`

## Milestone M4 — Product simplification (M)

Delivers: the flagship feels like one focused product instead of 113 loosely related surfaces.

- [ ] **4.1 Define the core route set** — DoD: the primary journey contains only home, scanner, methodology/trust, pricing, auth, dashboard/account and legal routes. `[LOW]`
- [ ] **4.2 Demote adjacent services** — DoD: Vantage, Vicinity, Codex and 14 add-on pages are removed from primary navigation until the lead subscription proves demand. `[MED]`
- [ ] **4.3 Shorten the homepage** — DoD: a tradesperson can state what is live, what £39 buys and the next action after one mobile viewport plus one supporting section. `[MED]`
- [ ] **4.4 Make samples unmistakable** — DoD: every illustrative card is permanently labelled and visually distinct from live results. `[LOW]`
- [ ] **4.5 Accessibility/responsive release pass** — DoD: keyboard, screen reader, 320/375/430px, 200% zoom and reduced-motion checks pass. `[MED]`
- [ ] **4.6 Add product analytics** — DoD: scan, no-result, qualified-result, signup, checkout, activation, WhatsApp and outcome events can be followed as one funnel without personal-data leakage. `[MED] [SEC]`

## Milestone M5 — JobFilter public repository cleanup (L)

Delivers: a public engineering repository that a hiring manager can understand in five minutes.

- [ ] **5.1 Move private operational material** — DoD: Obsidian memory, raw model memory, prompts, session handoffs and agent reports live only in the private vault and are absent from the public tree. `[HIGH] [SEC]`
- [ ] **5.2 Preserve valuable regressions neutrally** — DoD: useful scripts under `codex-output/` move to `tests/regression/` with product-focused names and documented assertions. `[MED]`
- [ ] **5.3 Remove stale root reports/migration scripts** — DoD: the root contains only active configuration, README, licence, contribution/security docs and necessary source directories. `[MED]`
- [ ] **5.4 Standardise the runtime** — DoD: package name is `jobfilter`; unused Vite, Express, React Router, Alpine and legacy build tooling are removed only after reachability tests. `[HIGH]`
- [ ] **5.5 Establish real quality scripts** — DoD: `typecheck`, `lint`, `format:check`, `test`, `test:integration`, `test:e2e`, `audit` and `build` exist and run in CI. `[HIGH]`
- [ ] **5.6 Rewrite README for public proof** — DoD: README covers problem, current status, implemented architecture, limitations, setup, tests, screenshots/demo and avoids roadmap-as-fact. `[MED]`
- [ ] **5.7 Add repository governance docs** — DoD: licence decision, `CONTRIBUTING.md`, `SECURITY.md`, issue templates and PR template are present. `[LOW] [BLOCKED: USER]`
- [ ] **5.8 Produce branch cleanup manifest** — DoD: every stale branch is listed with repo, merged PR and deletion eligibility; no branch is deleted by inference alone. `[LOW]`
- [ ] **5.9 Delete approved merged branches** — DoD: approved branches are gone and default branches remain untouched. `[LOW] [EXT] [DESTRUCTIVE: APPROVAL REQUIRED]`
- [ ] **5.10 Produce PR-metadata cleanup manifest** — DoD: proposed title/body/comment edits show before/after text and preserve technical decisions and verification. `[MED]`
- [ ] **5.11 Apply approved PR metadata edits** — DoD: only approved boilerplate/log text is removed; no review evidence or human decision disappears. `[HIGH] [EXT] [DESTRUCTIVE: APPROVAL REQUIRED]`

## Milestone M6 — Portfolio-wide GitHub publishing (M)

Delivers: one coherent public GitHub identity centred on JobFilter.

- [ ] **6.1 Classify all repositories** — DoD: every public repo is `flagship`, `supporting`, `prototype`, `archived`, `fork/contribution` or `private/internal`. `[LOW]`
- [ ] **6.2 Clean merged branches portfolio-wide** — DoD: approved 118 merged-PR branches are removed; the 7 review branches receive explicit keep/delete decisions. `[MED] [EXT] [DESTRUCTIVE: APPROVAL REQUIRED]`
- [ ] **6.3 Enable branch auto-delete everywhere** — DoD: all active repos delete merged head branches automatically. `[LOW] [EXT]`
- [ ] **6.4 Standardise repository metadata** — DoD: descriptions, homepages, topics, licences, archived state and default branches are accurate for all 14 public repos. `[MED] [EXT]`
- [ ] **6.5 Create GitHub profile README** — DoD: profile states role, flagship, selected systems, portfolio link and contact without inflated claims. `[LOW]`
- [ ] **6.6 Set profile and pins** — DoD: bio, location/availability, website and six intentional pins are configured; JobFilter is first. `[LOW] [EXT] [BLOCKED: USER]`
- [ ] **6.7 Clean active READMEs** — DoD: each featured/supporting repo has truthful status, demo, screenshots, architecture, limitations and verification commands. `[MED]`
- [ ] **6.8 Archive or privatise abandoned/internal work** — DoD: repositories not useful to users or the portfolio are intentionally archived/private with no broken deployment dependency. `[MED] [EXT] [BLOCKED: USER]`

## Milestone M7 — Flagship case study and pilot launch (L)

Delivers: JobFilter is both a credible product and a strong portfolio case study.

- [ ] **7.1 Publish JobFilter case study** — DoD: portfolio shows problem, role, architecture, constraints, source truth, test evidence, screenshots, current status and links. `[MED]`
- [ ] **7.2 Feature JobFilter first** — DoD: JobFilter is the dominant project on the portfolio homepage and GitHub profile. `[LOW]`
- [ ] **7.3 Recruit pilot trades** — DoD: at least five tradespeople in the selected wedge consent to a structured pilot. `[MED] [EXT] [BLOCKED: USER]`
- [ ] **7.4 Capture outcome evidence** — DoD: the pilot records opportunity volume, contacted, quoted, won, false positives and qualitative objections without fabricated attribution. `[MED] [EXT]`
- [ ] **7.5 Production go/no-go review** — DoD: security, truth, payment, delivery, quality, support, refund and rollback checklists are all green or explicitly accepted. `[HIGH] [SEC]`

## Required release gates

Every JobFilter release must pass:

1. Typecheck, lint, formatting and production build.
2. Unit and integration tests.
3. Scanner regression and truth-set thresholds.
4. Two-user tenant isolation tests.
5. Stripe test checkout/webhook/cancellation test.
6. WhatsApp test delivery and duplicate-suppression test.
7. Claims inventory check.
8. Secret/dependency scan.
9. Mobile, keyboard and core-journey E2E.
10. Human approval before merge/deploy.

## Founder decisions/blockers

1. Choose Meta WhatsApp Cloud API or Twilio as the single provider.
2. Create/confirm the £39 Stripe product and test/live price IDs.
3. Run/verify Supabase migrations and provide a staging project.
4. Choose the first pilot wedge: recommended Birmingham + builders/electricians.
5. Define a sellable-lead quality threshold and minimum weekly target.
6. Decide whether JobFilter production code stays public or whether the public surface becomes a clean case-study/release repository.
7. Choose licence policy for public original repos.
8. Approve branch and PR-metadata deletion manifests before mutation.

## Immediate execution order

1. M0 governance freeze.
2. M1 fabricated-data, exposed-diagnostics and claim fixes.
3. Founder configuration session for Stripe, Supabase and WhatsApp.
4. M2 one complete paid journey.
5. M3 seven-day lead-quality proof.
6. M4 simplification.
7. M5/M6 public cleanup and portfolio publishing.
8. M7 pilot and case study.

