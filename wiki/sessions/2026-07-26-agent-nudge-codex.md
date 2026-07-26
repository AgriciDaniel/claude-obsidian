---
date: 2026-07-26
project: agent-nudge
agent: codex
status: completed
---

## What I did

- Pulled the shared vault from `fork/main` and reviewed the Agent Nudge project history and AI Engineering Delivery Loop.
- Indexed `C:\Users\manaz\Projects\agent-nudge` with codebase-memory-mcp and mapped the compiler, daemon, CLI, UI, storage, connector, and Electron seams.
- Audited the current Brief Compiler implementation, `/v1/compile` route, `CompilerView`, repository context reader, existing CSS, package scripts, and compiler tests.
- Researched current Stripe webhook, Billing Entitlements, and customer portal guidance from official Stripe documentation.
- Designed the commercial direction: keep assurance and security features free; charge for saved automation through managed workspaces, automatic drift watching, custom profiles, changelog writes, and direct agent handoffs.
- Produced the working architecture and four-batch implementation sequence in conversation, but did not yet replace `docs/dogfood/MAZ-MODE-BUILD-PLAN.md`.
- Implemented Agent Nudge v0.5.0: repository context health and receipts, safe repo bootstrap, deterministic changelogs, signed offline Pro licensing with a 14-day trial, daemon-enforced entitlements, allowlisted Claude/Codex/Aider handoffs, and Stripe Checkout/license delivery/portal/webhook API routes.
- Rebuilt the compiler screen as a navy/yellow industrial workbench with context drift, token budget, Git state, changelog controls, runner output, and local license activation.
- Hardened loopback CORS, process spawning, credential redaction, output bounds, file containment, and license-state permissions.
- Verified 42 unit tests, 20 integration tests, 2 end-to-end tests, lint, typecheck, build, CLI flows, zero production dependency vulnerabilities, Windows installer/portable packaging, and a loopback-only portable executable smoke test.
- Added the canonical project `CHANGELOG.md`, linked it from the README, and recorded the v0.5.0 productization and security work.
- Ran a multi-perspective commercial audit covering skeptical buyers, solo developers, team leads, security, conversion, retention, competition, pricing, email consent, and defensibility.
- Wrote `docs/dogfood/COMMERCIAL-SITE-AUDIT.md` with the paid-launch blockers, one-time pricing recommendation, 14-day trial rules, consented email-list plan, moat ladder, and four implementation batches.
- Rebuilt successfully after the documentation changes.
- Published the complete v0.5 branch through GitHub PR #24, waited for the full quality workflow, and squash-merged it into `main` at `ddcf9de`.
- Detected production 404s on every direct SPA route, fixed the clean-URL rewrite through PR #25, verified the preview, and squash-merged the fix at `e97b29e`.
- Deployed the exact merged tree to Vercel production (`dpl_7RzH9EPvxBzSALNCTkADmFZDBxPW`) and verified the canonical alias, all public routes, current pricing/changelog bundle content, static discovery files, and API method guards.
- Restored the user-owned local `AGENTS.md`, MAZ build plan, and YouMind synthesis byte-for-byte after publishing; none entered the route-fix PR.
- Normalized GitHub issue #7 into a ready execution gate, preserved the user-owned files in a dedicated stash, and branched `agents/v051-local-control-auth` from the latest `origin/main`.
- Implemented v0.5.1 local control authentication: a random per-install credential outside repositories, Windows owner-only ACLs, loopback Host/Origin validation, daemon-wide bearer checks, stable instance identity, HMAC health challenges, and atomic credential rotation.
- Replaced the unsafe Electron `Origin: null` path with a bounded preload/main-process request bridge; authenticated CLI, provider hooks, and connector outbox requests without exposing the credential to the renderer.
- Added `agent-nudge auth rotate`, the public v0.5.1 security changelog entry, `docs/THREAT_MODEL.md`, and five focused authentication/leakage regressions.
- Ran the pre-push production audit: no tracked junk, no real high-confidence secrets, zero production dependency vulnerabilities, changed-file formatting clean, lint/typecheck/build green, 62 unit + 27 integration + 2 end-to-end tests green, and built daemon/CLI rotation smoke green.
- Published PR #26, waited for GitHub CI, confirmed zero review comments, and squash-merged it into `main` at `df931f3`.
- Deployed the exact merged commit to Vercel production (`dpl_J4nscnCA3k6LCcEn17dTYa1qCwuE`) and verified all public routes, live v0.5.1 bundle strings, the canonical alias, and 405 method guards on commercial APIs.
- Reapplied the user-owned files and verified all three match the preservation stash byte-for-byte; they remain unstaged.
- Implemented the versioned nudge outcome receipt protocol for acknowledge, dismiss, snooze, wrong, stale, and used across the daemon, Electron UI, CLI, and MCP.
- Enforced active same-project recipient ownership, valid transitions, exact-replay idempotency, and one `BEGIN IMMEDIATE` transaction covering nudge state, feedback, and the change-log cursor.
- Added 11 focused receipt regressions for every action, changed-intent replay, snooze-duration replay, cross-project access, wrong recipients, inactive sessions, terminal states, rollback, privacy redaction, and legacy-route retirement.
- Ran an independent security/atomicity review, moved receipt validation under the write transaction, and documented that `clientId` is a self-reported attribution label rather than independent identity.
- Verified changed-file formatting, lint, typecheck, build, 62 unit tests, 38 integration tests, 2 end-to-end tests, and zero production dependency vulnerabilities.
- Published PR #27, waited for green GitHub CI, squash-merged it at `7356f14`, and closed issue #7.
- Deployed the exact merged tree to Vercel production (`dpl_67c3KrFM5EnL6LgRLMiHrvXJCxyf`) and verified the canonical alias, all public routes, live receipt copy, discovery files, and commercial API method guards.
- Restored `AGENTS.md`, the MAZ build plan, and the YouMind synthesis from the preservation stash and verified all three byte-for-byte.

## Files changed

- `wiki/sessions/2026-07-26-agent-nudge-codex.md`
- Project implementation spans `api/`, `src/{changelog,commerce,context-health,licensing,onboarding,runners}`, daemon/CLI/storage/UI/Electron integration, tests, README, environment template, and package metadata.
- `CHANGELOG.md`
- `README.md`
- `docs/dogfood/COMMERCIAL-SITE-AUDIT.md`
- v0.5.1 project changes: `src/security/local-control.ts`, daemon/CLI/hook/outbox/Electron/UI integration, `docs/THREAT_MODEL.md`, focused tests, README, changelog, and package metadata.
- Receipt protocol changes: `src/{core/schemas.ts,storage/database.ts,daemon/server.ts,mcp/tools.ts,cli/index.ts,ui/App.tsx}`, focused/integration/e2e tests, protocol/security documentation, README, and changelog.

## Decisions made

- Recommended Community at $0 and Pro at $29/year, annual-only for launch; defer Team pricing until individual retention is demonstrated.
- Keep `POST /v1/compile`, redaction, conflict detection, context-health inspection, onboarding, and changelog preview free.
- Gate managed multi-repo workspaces, automatic drift watching, custom profiles, changelog writes, and one-click agent launches behind daemon-enforced entitlements.
- Use Stripe only in a hosted commerce service; issue signed offline-verifiable license envelopes to the local daemon and never ship Stripe secrets locally.
- Treat the present wildcard loopback CORS policy as a release blocker before adding activation or process-launch endpoints.
- Make direct handoffs use fixed provider adapters, argument arrays, `shell: false`, explicit previews, streamed receipts, and no arbitrary renderer-provided commands.
- Make the first implementation step a failing fixture-based `tests/unit/context-health.test.ts`, then add the context-health inspector.
- The shipped price is Community $0 and Pro $29/year. Stripe stays hosted; the desktop accepts only signed Ed25519 license tokens.
- The local daemon is the entitlement boundary. Renderer controls never execute arbitrary commands; provider adapters use fixed argument arrays with `shell: false`.
- Production dependencies audit clean. Remaining npm advisories are confined to development/build tooling and were not force-upgraded across breaking majors.
- Superseded the proposed $29/year local-only plan: recommend $49 one-time Personal, a $29 founder offer, 12 months of included updates, and an optional $29/year Updates Pass.
- Keep the 14-day trial cardless and preserve customer data when it falls back to Community.
- Do not sell Team yet; recurring value begins only with shared policy, identity, approvals, encrypted sync, and audit history.
- Treat the unauthenticated localhost control plane as the first paid-launch blocker. CORS is not authentication, and `null`-origin access must be removed before file mutation and process-launch routes can ship.
- The durable moat is a cross-provider source → delivery → acknowledgement → outcome evidence graph, not context-file parsing or local feature gates.
- Treat GitHub PR + green CI + exact merged-tree Vercel production deployment + route verification as the standing release path for live Agent Nudge changes.
- Keep the local control credential out of renderer memory, URLs, logs, exports, manifests, fixtures, and normal errors; only trusted local clients read it from the owner-only file.
- Split issue #7 deliberately: PR #26 shipped authentication first, PR #27 completed ownership-checked receipts, and sole-writer enforcement remains the next trust batch.
- Do not enable paid checkout merely because authentication shipped; purchase recovery, refund/revocation, installer trust, and ten clean external activations remain commercial gates.
- Serialize receipt validation and persistence under `BEGIN IMMEDIATE`; stale reads must never decide ownership, replay, or terminal transitions.
- Treat the shared installation credential as request authentication and `clientId` as an honest-client attribution/idempotency label, not separate cryptographic identity.
- Retire both legacy mutation routes with explicit `410 Gone` responses because every internal caller now uses the versioned protocol.

## Next steps

- Configure the production Stripe Price, secrets, webhook, and matching Ed25519 keypair from `.env.example`.
- Perform final human visual QA when the in-app browser surface is available; automated UI language checks and production builds pass.
- Enforce the daemon as the sole SQLite writer and add crash-recovery/concurrent-process coverage from issue #6.
- Resolve the `PUBLIC_APP_URL` / `PUBLIC_SITE_URL` mismatch and test purchase, redemption, recovery, refund, revocation, and device binding.
- Add a signed installer funnel and a consented double-opt-in email list before charging strangers.
