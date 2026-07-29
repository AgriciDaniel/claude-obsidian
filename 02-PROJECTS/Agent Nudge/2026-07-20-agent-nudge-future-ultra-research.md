# Agent Nudge — Future Ultra Research and Strategic Plan

Date: 2026-07-20  
Status: strategic research; directional, not a commitment to build every layer  
Related: [[2026-07-20-agent-nudge-super-x10-build-prompt]]

## Executive verdict

Agent Nudge should enter the market as a small local utility that prevents AI agents from missing consequential context. Its plausible long-term form is much larger:

> **The zero-trust context routing and provenance layer between AI agents.**

The near-term product answers: “Does this agent need this new fact right now?”

The future platform answers:

- Who or what asserted this context?
- Is the sender authenticated and authorized?
- May this information cross this project, tenant, geography, provider, or company boundary?
- Is it observation, inference, decision, constraint, warning, or revoked history?
- What evidence supports it?
- Who needs it, at what urgency, and with what interruption cost?
- When does it expire or become superseded?
- Was it delivered, acknowledged, used, ignored, contradicted, or harmful?
- What downstream action occurred because of it?

This is not another memory store. It is a control plane for context movement.

## Why this future is credible

The ecosystem is converging on distinct infrastructure layers:

1. **MCP** connects agents to tools, data, resources, and increasingly task/event primitives.
2. **A2A** connects independent agents through discovery, tasks, messages, streaming, and artifacts.
3. **CloudEvents/OpenTelemetry** provide portable event and observability shapes.
4. **AGNTCY** is assembling discovery, identity, encrypted transport, capability schemas, and multi-agent observability.
5. **Enterprise control planes** from Microsoft, GitHub, Google, and OpenAI are adding registries, identity, policy, audit, and shared context.
6. **NIST and OWASP** are focusing on agent identity, authorization, provenance, memory poisoning, excessive agency, and continuous risk controls.
7. **Agent payments and mandates** are emerging, making proof of authority and context lineage more important when agents can spend money or contract with services.

The likely outcome is that basic message transport and shared storage become commodities. Recipient relevance, interruption policy, trust, provenance, and outcome evidence remain unsolved coordination problems.

## Strategic category

Use different language by stage:

### Entry wedge

> The notification layer for AI agents.

### Team product

> The context routing layer for multi-agent work.

### Enterprise platform

> Zero-trust context routing for AI agents.

### Durable category

> The policy and provenance layer between agents.

Avoid positioning as “infinite memory”, “one shared brain”, or a new agent orchestration framework.

## The future architecture

```text
Agent hooks · Git · CI · issue trackers · A2A agents · MCP tools
                              │
                              ▼
                  Canonical event/fact ledger
              (versioned, immutable, CloudEvents-shaped)
                              │
                              ▼
          Identity · policy · redaction · trust · provenance
                              │
                              ▼
           Context delta + recipient relevance + timing
                              │
                              ▼
                 Durable nudge delivery ledger
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
         MCP/local         A2A/remote      Human/UI/SIEM
                              │
                              ▼
           acknowledgement · use · outcome · correction
                              │
                              └──── feedback to routing policy
```

AGNTCY identity, directories, and SLIM transport can sit beneath remote/federated operation later. Agent Nudge should integrate with those layers rather than recreate them.

## What the company must own

Protocols can carry messages. Agent Nudge must own the intelligence and evidence around whether the message should exist.

### 1. Context-delta extraction

Determine what materially changed since the recipient's last delivered and acknowledged state.

### 2. Recipient inference

Identify which active or future agent sessions are affected by the fact based on task, file, system, decision, dependency, risk, and authority.

### 3. Interruption policy

Choose among immediate warning, before-action advisory, next-turn context, session-start briefing, digest, quarantine, or suppression.

### 4. Nudge lifecycle

TTL, expiry, supersession, revocation, contradiction, acknowledgement, snooze, dismissal, and correction.

### 5. Provenance

Source event, agent/session identity, project, file/commit/test evidence, transformation history, confidence, policy version, and delivery receipts.

### 6. Attention economics

Each agent and human has a context/noise budget. The system should optimize useful interventions, not delivery volume.

### 7. Outcome learning

Measure which nudges prevented repeated work, conflicts, invalid approaches, policy breaches, wasted spend, or unsafe actions.

The feedback dataset around “this context helped this agent at this moment” is the strongest potential moat.

## Identity model

Never define an agent as only a provider name.

Future identity separates:

- tenant/organization;
- human owner or delegating principal;
- agent/workload identity;
- role and declared capability;
- model/provider/version;
- runtime/device/container;
- adapter/plugin version;
- project and trust domain;
- session and task;
- delegation/authority chain;
- signing key and attestation state.

Near term: OS user + local install identity + provider session + project.

Team stage: OIDC/SSO identity, tenant, RBAC, signed service identity.

Enterprise stage: workload identity, short-lived credentials, SPIFFE/mTLS federation, signed Agent Cards, key rotation, and revocation.

There must never be implicit trust because two agents run on the same laptop, network, provider, or tenant.

## Future nudge envelope

The long-term envelope should support:

```text
id + schema version + immutable content hash
issuer + subject + audience
tenant + project + purpose
claim type: observation | inference | decision | constraint | attempt | warning
source references + source hashes
created at + valid from + valid until
supersedes + revokes + contradicts
sensitivity + residency + sharing policy
confidence + verification state
policy version + policy decision ID
delegation/authority reference
signature + key ID + timestamp
delivery + acknowledgement + use receipts
```

Do not implement the whole cryptographic envelope in the local MVP. Preserve schema versioning, immutable IDs, source hashes, extension fields, expiry, supersession, and transport-independent canonical objects so it can evolve without a rewrite.

## Zero-trust policy model

Before remote/team delivery, every context read or nudge delivery becomes a policy decision.

Inputs:

- authenticated sender and recipient;
- project/tenant/trust domain;
- declared purpose;
- sensitivity and residency;
- source trust and integrity;
- recipient provider/model/destination;
- action risk;
- user/organization policy;
- time, expiry, and revocation state.

Outputs:

- allow;
- deny;
- redact then allow;
- quarantine for review;
- require step-up authorization;
- require human approval;
- delay/digest;
- revoke previous delivery where supported.

Read access to context must remain separate from permission to execute an action. A nudge is evidence, never executable authority.

## Provenance and audit

Build toward an append-only, tamper-evident ledger capturing:

- capture;
- normalization;
- redaction;
- fact creation;
- policy input and decision;
- routing score and factors;
- delivery attempts;
- acknowledgement/evidence access;
- correction/supersession/revocation;
- downstream outcome where observable.

Exports should later support JSONL, OTLP/OpenTelemetry, SIEM pipelines, retention policies, and incident evidence packages.

Do not log raw prompts, secrets, hidden reasoning, or full content by default. “Audit everything” without minimization creates a larger security problem.

## Standards strategy

### Build on

- MCP for local agent tools/resources and acknowledgements.
- A2A for remote agent discovery, tasks, messages, and generic delivery.
- CloudEvents-style canonical events for dedupe and routing.
- OpenTelemetry GenAI/agent conventions for trace export.
- OAuth/OIDC and resource indicators for remote authorization.
- Signed A2A Agent Cards for capability/identity assertions.
- OPA-style policy decision/enforcement separation.
- SPIFFE-style workload identity/federation for enterprise deployments.
- AGNTCY directory/OASF/identity/SLIM only when scale requires them.

### Do not invent

- a proprietary agent transport;
- a new OAuth replacement;
- a new universal agent identity standard;
- a blockchain for local context;
- a new vector database;
- a closed replacement for MCP or A2A;
- a universal orchestration framework.

### Potential open standard contribution

Publish the Nudge Envelope and lifecycle as an open, versioned A2A extension:

- urgency;
- timing;
- TTL;
- supersession/revocation;
- relevance explanation;
- acknowledgement/snooze/dismiss;
- evidence references;
- redaction class.

Keep basic interoperability open. Monetize relevance, policy, administration, governance, analytics, and managed reliability.

## Roadmap horizons

### Horizon 0 — Local proof, 0–6 months

Goal: prove that timely context deltas prevent real wasted work.

- Windows-first local daemon, MCP, hooks, desktop inbox.
- Claude Code and Codex.
- deterministic relevance and noise budgets;
- per-project isolation;
- decisions, failed approaches, file conflicts;
- source links, TTL, supersession, acknowledgement;
- local audit ledger and kill switch;
- seven-day dogfood loops;
- no required cloud, model API, team auth, or payments.

Success signal: users can name specific collisions or repeated investigations the product prevented.

### Horizon 1 — Developer/team relay, 6–18 months

Goal: move from one machine to coordinated teams.

- macOS/Linux and more agent adapters;
- encrypted team synchronization;
- tenant/project scopes;
- GitHub/GitLab/CI/issue tracker event ingestion;
- SSO, roles, approvals, policy templates;
- team context inbox and delivery receipts;
- A2A gateway and signed capability card;
- OpenTelemetry export;
- API/SDK and adapter marketplace;
- private cloud/on-prem option;
- relevance evaluation suite.

This is the first strong paid product: shared teams, policy, audit, and reliable synchronization.

### Horizon 2 — Enterprise context control plane, 18–36 months

Goal: govern context movement across large agent fleets.

- organization-wide agent inventory and capability registry;
- RBAC + ABAC/policy as code;
- delegated authority chains;
- signed nudge envelopes;
- KMS/BYOK, residency, retention, legal hold;
- DLP, SIEM, IAM, SOC integrations;
- SPIFFE/mTLS federation;
- approved providers/models/adapters;
- quarantine and incident response;
- policy simulator and “why allowed/denied/delivered”;
- replay/evidence packages;
- formal conformance tests for adapters.

### Horizon 3 — Federated agent network, 3–5 years

Goal: safely route context across companies and trust domains.

- federated directories and portable agent identities;
- verifiable capabilities and attestations;
- cross-company sharing contracts;
- purpose-bound encrypted context;
- reputation informed by verified outcomes;
- negotiation, dissent, escalation, and conflict workflows;
- cross-protocol routing over A2A/AGNTCY infrastructure;
- standards-compatible revocation and provenance.

### Horizon 4 — Agent attention infrastructure, 5–10 years

Goal: become part of the basic operating fabric for massive agent populations.

- each agent has a governed context inbox and attention budget;
- context routes by relevance, authority, cost, privacy, and urgency;
- agents negotiate subscriptions to facts/events rather than ingest everything;
- humans manage teams of human and machine workers through exceptions and policy;
- context provenance travels with decisions and transactions;
- agents can purchase services only within explicit mandates and budgets;
- organizational memory becomes a living graph of evidence, decisions, outcomes, and revocations;
- Agent Nudge becomes analogous to notification infrastructure + policy gateway + provenance ledger for agents.

This horizon is a direction, not a current build plan.

## JobFilter-inspired commercial principles, translated for agent teams

Use JobFilter as a pattern library, not as product copy. The audiences, stakes, buying motions, and interface are different.

| JobFilter principle | Agent Nudge translation |
|---|---|
| Lead quality over lead volume | Consequential nudge precision over notification volume |
| Explainable deterministic lead score | Explainable deterministic relevance and risk score |
| Speed-to-lead | Context-to-action latency: deliver before the affected action |
| GOLD/SILVER/BRONZE/BIN qualification | `BLOCK`, `ACT_NOW`, `NEXT_BOUNDARY`, `DIGEST`, `DROP` delivery classes |
| Territory/trade focus | Start with multi-agent software teams using two or more vendors |
| Outcome tracking from lead to win | Track source → delivery → acknowledgement → action → avoided rework |
| Flat, legible offer | One sentence, one core loop, and transparent self-serve tiers |
| Free scan proves value | Free local mode proves what would have been nudged without exporting data |
| Competitor weaknesses sharpen the offer | Position against memory dumps, stale context, closed vendor suites, and noisy observability |
| ROI dashboard | Show conflicts prevented, hours/tokens saved, stale decisions blocked, and incident evidence |

The adapted product law is:

> **Better context, fewer interruptions, before the action—not more memory and more messages.**

Do not copy trade, lead, territory, auction, or exclusivity language into Agent Nudge. Do not reuse JobFilter's visual identity. The transferable asset is commercial discipline: qualify value, prove the outcome, explain the score, and make one prevented mistake worth more than the subscription.

## Ideal customer sequence

Trying to sell to “everyone using AI” will blur the pain and waste the early learning window.

1. **First wedge:** 3–30 person software/product teams actively switching work among Claude Code, Codex, Cursor, Gemini/OpenCode, CI agents, and humans in the same repositories.
2. **Expansion wedge:** AI-native agencies and product studios coordinating many client repos and ephemeral agents.
3. **High-value wedge:** regulated or security-sensitive teams that require local/private context, provenance, policy, and audit.
4. **Platform market:** enterprises coordinating agents across engineering, support, operations, finance, research, and customer systems.

The buyer changes over time: individual developer → engineering lead/founder → platform engineering or AI operations → CISO/CIO. Keep product language specific to the buyer at each stage.

## Revenue-maximizing pricing architecture

Pricing below is a hypothesis to test, not a promise. Use pounds for the UK launch and localize currency later. Preserve a generous local proof while charging for collaboration, governance, risk reduction, and operational convenience.

### Community — £0 forever

- one user, one device, up to three projects;
- local daemon, CLI, MCP, core Claude/Codex adapters;
- deterministic rules and seven-day local history;
- limited replay/export;
- no cloud account required.

Purpose: adoption, trust, adapter contributions, and measurable proof. Never cripple privacy or local usefulness merely to force an upgrade.

### Pro — £19/month or £190/year

- one user across multiple devices;
- unlimited local projects;
- encrypted personal sync;
- advanced rules, longer history, replay, and personal ROI report;
- all maintained developer-agent adapters;
- priority updates/support.

Annual pricing gives roughly two months free, improves cash flow, and reduces churn. Display annual as the default while keeping monthly transparent.

### Team — £299/workspace/month or £2,990/year

- five human collaborators and ten active agents included;
- shared projects, encrypted relay, policies, approvals, team dashboard, connector management, and audit export;
- 100,000 governed event evaluations per month included;
- £15/month per additional active agent and a simple published overage for high event volume;
- email support and a guided onboarding session.

This is deliberately a workspace minimum rather than cheap per-seat software. The value is coordination across the system, including machine workers, and one avoided collision can repay the month.

### Business — £999/workspace/month or £9,990/year

- 25 humans and 50 active agents included;
- SSO, advanced RBAC/ABAC, retention controls, DLP integrations, policy simulation, incident replay, SIEM/OpenTelemetry export, and priority support;
- private relay option and multiple workspaces;
- quarterly value review using verified prevented-work and risk evidence.

This tier creates a self-serve-to-sales bridge without forcing every serious customer into an opaque enterprise negotiation.

### Enterprise — £30,000–£150,000+ annual contract

- price by deployment scope, governed active-agent band, compliance requirements, connectors, support, and data residency—not by human seats alone;
- on-premises or air-gapped deployment, SCIM, enterprise IAM/KMS/DLP/SIEM, legal hold, regional storage, signed envelopes, workload federation, SLAs, and named support;
- charge £5,000–£25,000 one-time for deployment, policy design, connector certification, migration, and training when real services are required;
- use annual prepayment and multi-year agreements with price protection, not blanket discounts;
- reserve custom engineering and guaranteed connector timelines for paid statements of work.

### Paid design-partner motion before mature SaaS

Do not wait for perfect self-serve product-market fit before testing willingness to pay.

- recruit 5–10 teams with obvious multi-agent coordination pain;
- sell a six-week instrumented pilot for £1,500–£5,000 depending on team size and privacy requirements;
- define baseline duplicate work, conflict, recovery time, and context failures before installation;
- credit part of the pilot fee toward an annual Team/Business contract if success gates are met;
- never offer an unbounded free enterprise pilot—free users provide opinions while paid pilots reveal procurement and value truth.

### Packaging rules that protect revenue

- Meter **governed active agents/workspaces and evaluated event volume**, not raw messages sent. Raw-message pricing rewards spam and creates fear of using the product.
- Keep core relevance, security, and privacy honest on every tier. Monetize collaboration, scale, retention, advanced policy, integrations, deployment, assurance, and support.
- Put SSO, SCIM, advanced audit, DLP, legal hold, private deployment, and SLA in Business/Enterprise because they have high buyer value and ongoing delivery cost.
- Use feature gates that match customer maturity; do not create artificial limits that make the proof unreliable.
- Offer a 30-day Team guarantee only against explicit onboarding and usage conditions, with a refund if the system produces no accepted useful nudge and no verified prevented-work event.
- Avoid lifetime deals. Avoid deep early discounts that permanently anchor value. Give founding customers a time-limited rate lock in exchange for reference calls, data-quality feedback, and case-study permission.
- Never sell customer context, train on private content, or make privacy a paid add-on.

### Expansion and revenue flywheel

```text
free local proof
    → personal ROI evidence
    → shared team workspace
    → more agents/connectors/projects
    → policy and audit dependence
    → Business/Enterprise control plane
    → certified integrations and services
    → stronger outcome benchmarks and higher-confidence routing
```

Expansion signals should trigger timely sales outreach: more than five collaborators, multiple repositories, repeated policy denies, sustained high event volume, requests for SSO/audit/private deployment, or verified savings above ten times the current subscription.

### Pricing validation plan

Run pricing as evidence collection, not founder guesswork:

1. Interview at least 20 ICP teams using Van Westendorp-style price questions plus concrete willingness-to-pay tests.
2. Quote paid pilots at three controlled price bands; record close rate, sales cycle, objections, and required security work.
3. Compare workspace-based, active-agent, and hybrid pricing using identical value stories.
4. Track gross margin after storage, relay, support, connectors, and compliance—not just top-line ARR.
5. Raise price when ROI evidence, activation, and retention support it; do not add features merely to justify a weak price.
6. Review packaging quarterly while grandfathering contracts intentionally, never accidentally.

Core commercial metrics:

- visitor → local install → first useful nudge → seven-day retained project;
- free → Pro and free/team trial → paid workspace conversion;
- pilot → annual contract conversion;
- gross and net revenue retention;
- expansion ARR from agents, workspaces, connectors, and governance;
- gross margin by tier;
- customer acquisition payback and sales cycle;
- verified customer value / annual contract value ratio;
- churn reason split: noise, weak ROI, missing integration, trust, budget, or incumbent bundle.

Target a value-to-price ratio of at least 10:1 in early case studies. The goal is not the highest sticker price; it is the highest sustainable lifetime gross profit without weakening trust or product signal.

## Business model progression

### Open-source core

- local daemon;
- schemas/protocol;
- MCP/A2A adapters;
- deterministic routing basics;
- personal desktop/CLI;
- local exports.

### Individual Pro

- cross-device encrypted sync;
- advanced rules;
- longer retention;
- more adapters;
- better analytics and replay.

Initial hypothesis: £19/month or £190/year.

### Team

- shared projects;
- SSO;
- approvals;
- policies;
- audit;
- integration management;
- hosted relay;
- team-level relevance tuning.

Initial hypothesis: £299/workspace/month with included collaborators, agents, and governed event volume.

### Enterprise

- on-prem/air-gapped deployment;
- SCIM/IAM/KMS/DLP/SIEM;
- residency and retention;
- signed envelopes and workload federation;
- incident evidence;
- policy as code;
- compliance mappings;
- SLA and support.

Initial hypothesis: £30,000–£150,000+ annually plus scoped onboarding/services where justified.

Do not monetize by selling captured content or training on private customer context.

## Platform and market threats

### Vendor consolidation

GitHub, Microsoft, Google, OpenAI, Anthropic, and IDE vendors can provide shared context inside their own ecosystems.

Response: remain cross-provider, cross-runtime, and cross-company. Serve the boundary between platforms rather than compete inside one platform's strongest native path.

### Transport commoditization

MCP triggers, A2A notifications, AGNTCY messaging, or community extensions may make delivery trivial.

Response: never make transport the moat. Own relevance, policy, provenance, timing, attention budgets, and outcome measurement.

### Memory commoditization

Shared memory and semantic retrieval are already crowded.

Response: avoid “one shared brain”. Treat memory stores as inputs and route only changed, relevant, authorized context.

### Hook restrictions

Vendors may alter or restrict session visibility and lifecycle hooks.

Response: maintain adapter isolation and ingest indirect evidence from Git, CI, tasks, tests, artifacts, A2A, MCP, and user decisions.

### Protocol churn

A2A and MCP are evolving; some task/notification primitives remain experimental or optional.

Response: keep canonical internal objects transport-neutral, version schemas, maintain a durable inbox/outbox, and treat all delivery as idempotent/at-least-once.

### Trust failure

One leaked secret, poisoned memory, or wrongly routed sensitive context can destroy the product.

Response: privacy/security is product functionality from day one, not enterprise polish.

### Noise failure

If agents receive too many low-value nudges they will ignore the layer entirely.

Response: optimize precision and avoided rework, not message volume. Provide pause, mute, digest, expiry, feedback, and per-agent attention budgets.

## Future-proof now without overbuilding

The local MVP should include these seams now:

- versioned canonical event/fact/nudge schemas;
- immutable IDs and idempotency keys;
- source hashes and multiple source references;
- expiry, supersession, contradiction, and revocation-ready state;
- provider-neutral adapter interface;
- transport interface separate from relevance/policy;
- durable inbox/outbox and replay cursor;
- project namespace on every record/query;
- identity object separate from provider/model/session;
- policy decision interface, even if V1 policy is simple local rules;
- trace IDs spanning source event through feedback;
- extension metadata map for future protocol fields;
- content-minimizing telemetry;
- exportable ledger.

Do not add now:

- cloud synchronization;
- enterprise SSO;
- SPIFFE;
- full OPA deployment;
- remote A2A hosting;
- payments;
- agent marketplace;
- blockchain;
- reputation tokens;
- automatic execution based on nudges;
- cross-company sharing.

Architecture seams are required. Future products are not.

## Strategic metrics

### Product usefulness

- precision of delivered nudges;
- acknowledgement/use rate;
- dismiss/wrong/stale rate;
- interruption cost;
- conflicts prevented;
- repeated failed approaches prevented;
- decision violations caught;
- estimated context tokens avoided, clearly labelled.

### Trust

- evidence-open rate;
- unsigned/unverified source rate;
- policy denies/reviews;
- cross-project leakage incidents;
- redaction incidents;
- stale/poisoned context reports;
- time to revoke or supersede;
- delivery and acknowledgement integrity.

### Platform

- supported agent runtimes;
- adapter conformance pass rate;
- delivery latency/reliability;
- percentage of events normalized through open standards;
- time to support a new provider;
- active organizations/projects/agent sessions.

## Kill criteria

Do not continue merely because the future market is large.

Reconsider or kill the product if:

- real teams prefer repository/issue context and do not value proactive delivery;
- useful nudge precision cannot beat noise after tuning;
- providers make cross-vendor lifecycle access consistently impossible;
- users will not trust the product with project metadata;
- the only valued feature is generic search/memory;
- platform vendors solve cross-provider context with portable standards and no governance gap;
- avoided-work outcomes cannot be demonstrated.

## Research-backed final recommendation

Build the local MVP exactly as a focused wedge. Architect it as the first node of a much larger system:

> **Hooks/Git/CI → fact ledger → identity and policy → relevance and timing → durable delivery → feedback and provenance.**

Use MCP and A2A. Later integrate CloudEvents, OpenTelemetry, OPA, SPIFFE, and AGNTCY. Do not compete with them.

If the wedge proves useful, the company is not “shared memory for agents.” It is infrastructure that ensures the right machine receives the right evidence under the right authority at the right time—and leaves a trustworthy record of what happened next.

## Primary research anchors

- MCP 2026 roadmap: https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/
- MCP Tasks: https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks
- A2A specification: https://a2a-protocol.org/latest/specification/
- A2A roadmap: https://a2a-protocol.org/latest/roadmap/
- A2A Linux Foundation adoption: https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
- CloudEvents specification: https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md
- AGNTCY: https://docs.agntcy.org/
- AGNTCY identity: https://docs.agntcy.org/identity/identity/
- AGNTCY SLIM: https://docs.agntcy.org/slim/overview/
- NIST AI Agent Standards Initiative: https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative
- NIST agent identity/authorization concept: https://www.nist.gov/news-events/news/2026/02/new-concept-paper-identity-and-authority-software-agents
- NIST Zero Trust: https://csrc.nist.gov/pubs/sp/800/207/final
- NIST AI RMF: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- OWASP Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- OWASP Agentic Threats Navigator: https://genai.owasp.org/resource/owasp-gen-ai-security-project-agentic-threats-navigator/
- OpenTelemetry GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- SPIFFE concepts: https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
- Open Policy Agent: https://www.openpolicyagent.org/docs/http-api-authorization
- GitHub agent control plane: https://github.blog/changelog/2026-02-26-enterprise-ai-controls-agent-control-plane-now-generally-available/
- Microsoft Agent 365 registry: https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry?view=o365-worldwide
- Google Cloud Agent Registry: https://docs.cloud.google.com/agent-registry/register-agents
- OpenAI Frontier: https://openai.com/business/frontier/
- OpenAI Codex app and multi-agent supervision direction: https://openai.com/index/introducing-the-codex-app/
- Anthropic Claude Code usage research: https://www.anthropic.com/research/claude-code-expertise
- Microsoft Agent Framework: https://learn.microsoft.com/en-us/agent-framework/overview/
- Google Agent Development Kit: https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk
- AgentFiles cross-agent handoffs: https://www.agentfiles.io/
- Pathmark local shared context: https://github.com/hacksurvivor/pathmark
- Shared Agent Memory: https://github.com/dan-calin/shared-agent-memory
- Colony coordination layer: https://github.com/recodeee/colony
- Agent Bus MCP: https://www.agentbusmcp.com/
- LangSmith pricing benchmark: https://www.langchain.com/pricing
- Langfuse pricing benchmark: https://langfuse.com/pricing
- Langfuse monetization principles: https://langfuse.com/handbook/chapters/monetization
- Mem0 pricing benchmark: https://mem0.ai/pricing
- AgentOps pricing benchmark: https://www.agentops.ai/
- Reddit — switching between Claude and Codex loses context: https://www.reddit.com/r/codex/comments/1uzv7pt/how_do_you_share_codding_session_between_claude/
- Reddit — oversized handoffs exhaust context: https://www.reddit.com/r/ClaudeCode/comments/1uefjj1/context_drastically_exhausts_with_handoffs/
- Agent Payments Protocol: https://ap2-protocol.org/ap2/specification/
- x402: https://docs.x402.org/faq
- EU AI Act official overview: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
