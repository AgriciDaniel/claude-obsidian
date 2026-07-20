# Agent Nudge — Super x10 One-Batch Build Prompt

> Copy-paste this entire document into one fresh Claude Code, Codex, or equivalent coding-agent session.
> Run it from `C:\Users\manaz\Projects`.
> Working product name: **Agent Nudge**. Treat the name as replaceable configuration; do not buy a domain, publish a package, create a cloud account, or deploy anything.
> Target local repo: `C:\Users\manaz\Projects\agent-nudge`.
> Objective: finish a genuinely runnable, Windows-first local MVP in one sustained batch, with verification and a final receipt.

---

## OPERATING MODE

You are the founding engineer, product architect, security reviewer, QA lead, UX designer, and technical writer for this build.

Work autonomously from inspection through implementation and verification. Do not pause for ordinary implementation choices. Make conservative assumptions, record them, and keep moving. Ask the user only when blocked by something that would materially change the product, require credentials, cause an external side effect, spend money, delete unrelated data, or publish/deploy the product.

This is a one-batch build, but not a reckless one-shot generation. Internally use this loop until the acceptance criteria pass:

1. Inspect.
2. Plan privately and write `BUILD_PLAN.md`.
3. Implement one coherent phase.
4. Run the narrowest relevant verification.
5. Fix failures before advancing.
6. Review against this prompt.
7. Run the full verification matrix.
8. Produce a machine-readable and human-readable build receipt.

Do not declare success because files exist. Success means the demo flow works, the test suite passes, the app builds, and the product visibly demonstrates a useful nudge moving from one simulated agent to another.

---

## MISSION

Build **Agent Nudge**, a local-first coordination layer for AI coding agents.

The product watches structured events from agents such as Claude Code and Codex, records compact evidence about what happened, identifies which other active agent or future session is likely to need that information, and delivers the smallest useful nudge at the safest useful moment.

The product is not a chatbot and not a generic shared-memory database.

The core promise is:

> When one AI agent learns something another agent should know, Agent Nudge delivers a small, relevant, source-backed message at the right moment.

Example:

```text
NUDGE FOR CODEX · HIGH RELEVANCE

Claude rejected the Redis caching approach after integration tests failed.
You are currently entering the same caching path.

Why now: overlapping project + directory + task topic
Source: Claude session cld_184 · commit a73d2e · 12 minutes ago
Fresh until: 18:30

[Acknowledge] [Show evidence] [Snooze] [Dismiss]
```

The product must make agents cooperate without dumping full transcripts into each other's context windows.

---

## PRODUCT THESIS

Shared memory answers: “Where can agents store information?”

Agent Nudge answers:

1. What changed?
2. Which agent needs to know?
3. Why is it relevant to that agent's current task?
4. How small can the message be while remaining actionable?
5. Should it interrupt now, appear before the next tool call, wait until the next prompt, or join a digest?
6. Did the receiving agent acknowledge, use, snooze, or reject it?
7. Was the nudge correct, useful, stale, noisy, or harmful?

The durable product advantage is the feedback loop around relevance and delivery—not storage volume.

---

## COMPETITIVE BOUNDARY

Build a product clearly different from:

- ContextStream: shared project memory and automatic session context.
- Pathmark: local memory and proactive recall.
- shared-agent-memory: shared graph plus file claims.
- Colony: claims, handoffs, plans, receipts, and coordination state.
- ContextRelay: cross-provider payload transport and pub/sub.
- Handoff/Wenlan: structured knowledge and explicit session handoffs.
- AgentFiles: addressed and versioned artifacts.
- AgentMem/Letta/Mem0: general agent memory infrastructure.
- GitHub Agent HQ: agents operating with shared GitHub context and memory.

Do not rebuild those products feature-for-feature.

Agent Nudge's v1 differentiator is:

> A deterministic, inspectable notification engine for agent context deltas, with recipient selection, delivery timing, acknowledgement, expiry, provenance, and noise controls.

---

## NON-NEGOTIABLE PRODUCT LAWS

1. **Local first.** Core operation requires no cloud account, API key, remote database, or LLM call.
2. **Evidence, not truth.** Every nudge cites the event, file, commit, test, session receipt, or user decision that produced it.
3. **Minimal delta.** Never inject an entire transcript when a five-line fact is sufficient.
4. **Recipient specific.** A broadcast feed is not a nudge. The system explains why this recipient received this item.
5. **Delivery has timing.** `urgent`, `before_tool`, `next_turn`, `session_start`, and `digest` are distinct.
6. **No hidden-model claims.** Never claim to know the model's internal knowledge. Track what a session was sent, what it acknowledged, and what it acted on.
7. **Staleness is a first-class failure.** Every durable fact has freshness, expiry, supersession, or a refresh condition.
8. **Silence is valuable.** Noise budgets and relevance thresholds matter more than total recall.
9. **Safe installation.** Never overwrite existing Claude/Codex settings. Preview, back up, merge only owned blocks, and support clean uninstall.
10. **No raw secrets.** Redact before persistence. Never store `.env` contents, tokens, passwords, private keys, auth headers, or credential-bearing commands.
11. **No transcript hoarding by default.** Store structured receipts and selected excerpts, not complete conversations.
12. **Deterministic core.** V1 relevance scoring must work without embeddings or an LLM.
13. **Human authority.** A user can inspect, correct, supersede, mute, delete, export, or purge every stored item.
14. **Portable protocol.** Claude and Codex are first adapters, not hardcoded product boundaries.
15. **Measurable usefulness.** Track avoided collisions, acknowledged warnings, dismissals, stale nudges, and estimated repeated work prevented.

---

## MVP SUCCESS SCENARIOS

The completed product must demonstrate all three scenarios end to end.

### Scenario A — Conflicting edit

1. Claude session claims or edits `src/lib/cache.ts`.
2. Codex session attempts to edit the same file.
3. Agent Nudge produces an urgent/pre-tool warning for Codex.
4. The warning identifies Claude, the file, age, project, and source event.
5. Codex can acknowledge, inspect evidence, or proceed despite the advisory warning.
6. The event and response appear in the desktop timeline.

### Scenario B — Changed decision

1. Claude records: “Use signed cookies, not localStorage, for session state.”
2. The decision is scoped to the authentication area and linked to a source.
3. Codex begins a task touching authentication.
4. Agent Nudge delivers a compact next-turn nudge before implementation.
5. The UI explains the relevance factors and shows freshness.

### Scenario C — Failed approach

1. One agent records a failed Redis approach with test evidence.
2. Another agent begins work with overlapping repo/path/topic signals.
3. Agent Nudge warns that the approach was already attempted and rejected.
4. The receiving agent can open the failure receipt without receiving the whole prior transcript.

Also demonstrate one intentionally irrelevant event that is correctly suppressed.

---

## TARGET STACK

Use a TypeScript-first npm-workspaces monorepo so the entire MVP can be built on Windows with one runtime family.

- Node.js 20+
- TypeScript strict mode
- npm workspaces
- Electron + Vite + React for the Windows desktop/tray app
- Fastify for the localhost daemon API
- WebSocket or Server-Sent Events for live UI updates; pick one and document why
- SQLite through a mature local driver
- Zod for runtime validation and shared schemas
- Official MCP TypeScript SDK for the stdio MCP server
- Vitest for unit/integration tests
- Playwright for the critical desktop/web-renderer flows where practical
- electron-builder for an unsigned local Windows package
- ESLint + Prettier

Do not add Supabase, Firebase, Redis, Kafka, a vector database, Docker, Kubernetes, authentication SaaS, analytics SaaS, or an AI API to the MVP.

If an exact package is incompatible with the installed Node/Windows environment, choose the smallest maintained substitute, record the reason in `DECISIONS.md`, and keep the architecture intact.

---

## REPOSITORY SHAPE

Create this structure unless inspection reveals a compelling technical constraint:

```text
agent-nudge/
  apps/
    daemon/                 # localhost API, event ingestion, delivery scheduler
    desktop/                # Electron shell + React operator UI + tray
  packages/
    core/                   # schemas, scoring, policies, nudge compiler
    storage/                # SQLite migrations and repositories
    mcp-server/             # MCP tools/resources
    cli/                    # install, doctor, demo, export, purge, uninstall
    adapter-claude/         # Claude Code hook normalization and install plan
    adapter-codex/          # Codex hook normalization and install plan
    test-fixtures/          # provider hook payloads and scenario fixtures
  docs/
    PRODUCT.md
    ARCHITECTURE.md
    PROTOCOL.md
    SECURITY.md
    PRIVACY.md
    COMPETITOR-NOTES.md
    MANUAL-TEST.md
    LANDING-COPY.md
    WINDOWS-INSTALL.md
  scripts/
  BUILD_PLAN.md
  BUILD_RECEIPT.md
  DECISIONS.md
  AGENTS.md
  CLAUDE.md
  README.md
  SECURITY.md
  LICENSE
  package.json
  tsconfig.base.json
```

Use MIT unless a dependency or existing repository state makes that inappropriate. Record the decision.

---

## CORE DOMAIN MODEL

Implement versioned Zod schemas and exported TypeScript types. SQLite rows may be normalized, but the protocol objects must retain this meaning.

```ts
type AgentProvider = 'claude-code' | 'codex' | 'opencode' | 'cursor' | 'unknown';
type DeliveryMode = 'urgent' | 'before_tool' | 'next_turn' | 'session_start' | 'digest';
type NudgeState = 'queued' | 'delivered' | 'acknowledged' | 'snoozed' | 'dismissed' | 'expired' | 'superseded';
type FactKind = 'decision' | 'change' | 'failure' | 'warning' | 'claim' | 'release' | 'verification' | 'handoff';

type ProjectIdentity = {
  id: string;
  displayName: string;
  rootPath: string;
  gitRemoteHash?: string;
  gitRootHash: string;
};

type AgentSession = {
  id: string;
  provider: AgentProvider;
  providerSessionId?: string;
  projectId: string;
  cwd: string;
  startedAt: string;
  lastSeenAt: string;
  endedAt?: string;
  activeTask?: {
    summary: string;
    paths: string[];
    tags: string[];
  };
  status: 'active' | 'idle' | 'ended' | 'unknown';
};

type AgentEvent = {
  id: string;
  schemaVersion: 1;
  occurredAt: string;
  receivedAt: string;
  provider: AgentProvider;
  sessionId: string;
  projectId: string;
  eventType:
    | 'session.started'
    | 'session.ended'
    | 'prompt.submitted'
    | 'tool.before'
    | 'tool.after'
    | 'tool.failed'
    | 'file.changed'
    | 'task.updated'
    | 'receipt.created';
  paths: string[];
  commandClass?: string;
  payload: Record<string, unknown>;
  sourceRef?: SourceRef;
  redaction: { applied: boolean; rules: string[] };
  idempotencyKey: string;
};

type SourceRef = {
  type: 'hook-event' | 'git-commit' | 'git-diff' | 'test-run' | 'file' | 'user-decision' | 'manual';
  label: string;
  uri?: string;
  commitSha?: string;
  filePath?: string;
  sessionId?: string;
};

type ContextFact = {
  id: string;
  schemaVersion: 1;
  projectId: string;
  authorSessionId: string;
  kind: FactKind;
  title: string;
  summary: string;
  paths: string[];
  tags: string[];
  sourceRefs: SourceRef[];
  confidence: number;       // 0..1, evidence confidence—not model certainty
  createdAt: string;
  expiresAt?: string;
  refreshWhen?: string;
  supersedesFactId?: string;
  sensitivity: 'normal' | 'restricted' | 'secret-blocked';
};

type AgentContextManifest = {
  sessionId: string;
  deliveredFactIds: string[];
  acknowledgedFactIds: string[];
  dismissedFactIds: string[];
  lastUpdatedAt: string;
};

type RelevanceFactor = {
  code: string;
  label: string;
  score: number;
  evidence: string;
};

type Nudge = {
  id: string;
  schemaVersion: 1;
  factId: string;
  recipientSessionId: string;
  projectId: string;
  title: string;
  body: string;
  deliveryMode: DeliveryMode;
  state: NudgeState;
  relevanceScore: number;
  relevanceFactors: RelevanceFactor[];
  whyNow: string;
  sourceRefs: SourceRef[];
  createdAt: string;
  deliverAfter?: string;
  expiresAt: string;
  deliveredAt?: string;
  acknowledgedAt?: string;
  snoozedUntil?: string;
  dismissedReason?: string;
  dedupeKey: string;
};

type FeedbackEvent = {
  id: string;
  nudgeId: string;
  sessionId: string;
  action: 'opened' | 'acknowledged' | 'used' | 'snoozed' | 'dismissed' | 'reported_stale' | 'reported_wrong';
  at: string;
  note?: string;
};
```

Never equate `deliveredFactIds` with facts that are definitely present in a model's hidden working memory. Label the UI honestly: “delivered”, “acknowledged”, and “used”, never “the model knows”.

---

## EVENT INGESTION AND FACT CREATION

Build a provider-neutral event envelope plus provider-specific normalizers.

### Default collection policy

Collect:

- session lifecycle metadata;
- repo/project identity;
- tool name and safe command classification;
- touched file paths;
- Git commit/diff metadata;
- test/build outcomes and short sanitized tails;
- explicitly authored decisions, failures, warnings, and handoffs;
- task summary and declared paths/tags;
- acknowledgements and delivery receipts.

Do not collect by default:

- full prompts;
- full assistant responses;
- full terminal transcripts;
- file contents;
- `.env` values;
- clipboard contents;
- browser history;
- credentials;
- unrelated repositories;
- private home-directory documents.

Provide an opt-in “store sanitized excerpt” field for manually created facts. Make the default off.

### Fact creation rules

V1 automatically creates facts only for high-signal deterministic events:

- file claim/release;
- overlapping edit warning;
- failed verification with named path/task;
- successful verification receipt;
- changed Git commit touching a path another active session declared;
- explicit `record_decision`, `record_failure`, `record_warning`, or `handoff` MCP calls.

Do not attempt to summarize arbitrary conversations automatically in V1.

---

## DETERMINISTIC RELEVANCE ENGINE

Implement a transparent scoring engine. Store every factor used so the UI can answer “Why did I receive this?”

Start with these configurable weights:

```ts
const DEFAULT_WEIGHTS = {
  sameProject: 25,
  exactPathOverlap: 45,
  directoryOverlap: 20,
  activeTaskTagOverlap: 15,
  failureRisk: 20,
  changedDecision: 20,
  activeFileClaimConflict: 60,
  sourceVerified: 10,
  recipientAlreadyAcknowledged: -100,
  recipientDismissedRelated: -30,
  stale: -60,
  authorIsRecipient: -100,
};
```

Required policy:

- Different project: suppress unless explicitly cross-project scoped.
- Same author and recipient session: suppress.
- Already acknowledged exact fact: suppress.
- Exact active file-claim conflict: `urgent` or `before_tool`.
- Score 70+: `before_tool` or `next_turn`, depending on event risk.
- Score 50–69: `next_turn`.
- Score 30–49: `session_start` or `digest`.
- Below 30: suppress.
- Expired or superseded facts: suppress by default.
- No more than 3 non-urgent nudges per session per 10 minutes.
- Collapse related facts into one nudge when dedupe keys overlap.
- An urgent nudge must still be advisory in V1. Do not silently block edits.

Make thresholds and weights editable in the desktop Settings screen and persisted locally. Include “Reset defaults”.

Write table-driven unit tests for boundary values, negative factors, expiry, deduplication, and noise budgets.

---

## NUDGE COMPILER

Compile facts into compact messages using deterministic templates. No LLM call.

Every message must contain:

- recipient agent;
- severity/delivery mode;
- one-sentence event;
- why it matters now;
- source label and age;
- freshness/expiry;
- available actions.

Hard limits:

- title: 90 characters;
- body: 600 characters by default;
- at most 3 source references in the compact view;
- no raw stack trace in the nudge body;
- no secret-shaped text;
- expandable evidence lives outside the injected message.

Provide templates for claim conflict, changed decision, failed approach, verification result, handoff, and generic warning.

---

## DELIVERY ENGINE

Implement a queue that is crash-safe, idempotent, and inspectable.

Delivery modes:

- `urgent`: desktop toast + tray badge + agent hook output at the next safe boundary.
- `before_tool`: returned to the relevant pre-tool hook as additional context/advisory warning.
- `next_turn`: injected on `UserPromptSubmit` or retrieved through MCP before the next substantial action.
- `session_start`: compact briefing returned when a relevant agent session starts or resumes.
- `digest`: desktop inbox only until explicitly opened or requested.

An adapter may have weaker capabilities. Degrade honestly:

- If live injection is unsupported, queue for MCP retrieval and show `delivery_degraded` in the UI.
- Never pretend a nudge reached an agent unless a hook/MCP delivery receipt exists.
- Desktop toast delivery is not the same as agent-context delivery; track them separately.

Persist attempts, outcomes, errors, retry count, and the exact adapter capability used.

---

## MCP SERVER

Create one local stdio MCP server named `agent-nudge`.

Required tools:

```text
register_session
heartbeat_session
update_active_task
record_decision
record_failure
record_warning
record_handoff
claim_paths
release_paths
get_nudges
acknowledge_nudge
snooze_nudge
dismiss_nudge
explain_nudge
report_nudge_used
report_nudge_wrong
get_project_context_manifest
agent_nudge_health
```

Requirements:

- Validate all input with shared Zod schemas.
- Return compact text plus structured content where supported.
- Paginate lists.
- Default `get_nudges` to no more than 5 items.
- Never return secret-blocked facts.
- Require project/session identity for all session-scoped operations.
- Include idempotency keys for writes.
- Make destructive purge unavailable through MCP in V1.

Expose read-only resources if supported cleanly:

```text
nudge://projects/{projectId}/inbox/{sessionId}
nudge://projects/{projectId}/timeline
nudge://facts/{factId}
nudge://nudges/{nudgeId}/explanation
```

---

## CLAUDE CODE ADAPTER

Use current documented Claude Code lifecycle hooks and MCP support.

Support these hook points where available:

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `PostToolUseFailure`
- `Stop`
- `SessionEnd`
- optionally `FileChanged` if it can be used without creating excessive noise

The adapter must:

1. Read hook JSON from stdin.
2. Normalize only documented/safely detected fields.
3. Redact before sending to the daemon.
4. Fail open for ordinary telemetry failures.
5. Return advisory context only when a queued nudge matches the current session/tool/path.
6. Never approve permissions or bypass Claude's normal permission flow.
7. Use short timeouts and never hang an agent session because the daemon is offline.

Installer behavior:

- Generate a preview first.
- Back up existing `.claude/settings.json` or user settings before mutation.
- Merge a marker-owned hook block without replacing unrelated settings.
- Offer project and user scope separately.
- Register MCP using supported configuration.
- On native Windows, account for local `npx`/Node invocation requirements.
- Provide clean uninstall that removes only Agent Nudge-owned entries.

Ship hook payload fixtures based on documented event shapes and test every normalizer.

---

## CODEX ADAPTER

Use current documented Codex hooks, `AGENTS.md`, `.codex/config.toml`, and MCP support.

Support these hook points where available:

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `PostToolUseFailure`
- `Stop`
- `SessionEnd` if supported by the installed surface

The adapter must follow the same safety and timeout rules as Claude.

Installer behavior:

- Prefer `hooks.json` or inline hooks, but never add both in the same layer.
- Preview and back up before changes.
- Distinguish user-level and trusted project-level configuration.
- Never mark a repository trusted on the user's behalf.
- Register the MCP server through supported Codex configuration/CLI.
- Add only a concise marker-owned instruction block to `AGENTS.md` when the user explicitly chooses project instructions.
- Remove only owned configuration on uninstall.

If a current Codex event field differs from Claude's, create a provider normalizer rather than forcing one provider's payload into the other.

---

## LOCAL DAEMON API

Bind only to `127.0.0.1`, never `0.0.0.0`.

Use an unprivileged fixed default port with automatic fallback and a local discovery file. Suggested default: `43119`.

Required routes:

```text
GET    /health
GET    /v1/status
POST   /v1/events
POST   /v1/sessions/register
POST   /v1/sessions/:id/heartbeat
POST   /v1/sessions/:id/end
GET    /v1/sessions
POST   /v1/facts
GET    /v1/facts
GET    /v1/facts/:id
POST   /v1/claims
DELETE /v1/claims/:id
GET    /v1/nudges
GET    /v1/nudges/:id
POST   /v1/nudges/:id/acknowledge
POST   /v1/nudges/:id/snooze
POST   /v1/nudges/:id/dismiss
POST   /v1/nudges/:id/feedback
GET    /v1/timeline
GET    /v1/metrics
POST   /v1/demo/reset
POST   /v1/demo/run/:scenario
```

Requirements:

- consistent error envelope;
- request IDs;
- Zod validation;
- bounded request body sizes;
- structured local logs with secret redaction;
- SQLite WAL mode where appropriate;
- migrations with schema versioning;
- graceful shutdown;
- crash-safe queue processing;
- idempotent event ingestion;
- health output showing database, queue, adapter, and migration status;
- development CORS limited to the desktop renderer origin;
- no remote network calls in normal operation.

---

## SQLITE MODEL

Create migrations and repository tests for at least:

```text
projects
agent_sessions
agent_events
context_facts
fact_sources
file_claims
nudges
nudge_deliveries
feedback_events
context_manifests
settings
schema_migrations
```

Add indexes for project/session/time lookups, active claims, queued nudges, dedupe keys, fact paths/tags, and expiry scans.

Store timestamps as UTC ISO strings. Normalize Windows paths for comparison while retaining the original display path. Treat path matching as case-insensitive on Windows.

Include export to sanitized JSONL and a preview-first purge command. Back up the database before an applied purge.

---

## CLI

Create a polished command called `agent-nudge`.

Required commands:

```text
agent-nudge start
agent-nudge stop
agent-nudge status
agent-nudge doctor
agent-nudge demo
agent-nudge demo conflict
agent-nudge demo decision
agent-nudge demo failure
agent-nudge install claude --scope user --dry-run
agent-nudge install codex --scope user --dry-run
agent-nudge install all --scope project --dry-run
agent-nudge uninstall claude --dry-run
agent-nudge uninstall codex --dry-run
agent-nudge export --project <id>
agent-nudge purge --project <id> --dry-run
agent-nudge config show
agent-nudge config reset
```

Rules:

- Mutating install/uninstall/purge commands default to dry-run unless `--apply` is supplied.
- Show exact files that would change.
- Create timestamped backups.
- Refuse to print secret values.
- `doctor` checks Node version, daemon, database, config ownership markers, Claude/Codex availability, MCP registration, hook validity, and port conflicts.
- `demo` must work without Claude or Codex installed.

---

## WINDOWS DESKTOP APP

Build a real Electron desktop/tray app, not just a browser page in a repository.

### Design direction

Use a calm operational-console aesthetic:

- near-black, warm white, and signal yellow;
- compact typography;
- crisp borders;
- no AI gradients, glowing orbs, fake neural networks, mascots, or decorative charts;
- excellent empty, offline, loading, and error states;
- keyboard accessible;
- useful at 1280×720 and above;
- system tray badge/state: healthy, nudges waiting, daemon offline.

### Primary screen

Use one main workspace with five tightly connected zones:

```text
TOPBAR       Agent Nudge · daemon status · active agents · pause nudges · demo
INBOX        queued/delivered nudges with severity, recipient, freshness, actions
LIVE AGENTS  provider, project, task, claimed paths, last seen, delivery capability
TIMELINE     events → facts → nudge decision → delivery → feedback
INSPECTOR    evidence, relevance score breakdown, source refs, delivery attempts
```

Secondary navigation may contain:

- Rules
- Metrics
- Settings
- Install/Doctor

### Required interactions

- Acknowledge, snooze, dismiss, mark used, report wrong/stale.
- Expand “Why this nudge?” to show every scoring factor.
- Open source path/commit safely when available.
- Pause all non-urgent nudges.
- Mute a project, path pattern, fact kind, or source session.
- Edit thresholds and noise budgets.
- Run each demo scenario.
- Preview adapter installation changes.
- Export project data.
- Preview purge.
- See delivery degraded/offline states.

### Metrics

Show only honest, derived local metrics:

- nudges created/delivered/acknowledged/dismissed;
- acknowledgement rate;
- median time to acknowledgement;
- duplicate nudges suppressed;
- expired/stale reports;
- active edit conflicts surfaced;
- failed approaches warned about;
- estimated repeated-work events avoided, clearly labelled as an estimate;
- noise rate = dismissed or reported-wrong / delivered.

Do not invent ROI money figures or claim work was avoided without feedback evidence.

---

## ONBOARDING

First launch must provide:

1. One-sentence product explanation.
2. Privacy promise: local by default, structured metadata, no full transcript capture.
3. Read-only detection of Claude Code and Codex.
4. A choice to run demo mode before installing anything.
5. Project selection.
6. Adapter install preview.
7. Explicit apply action.
8. Doctor check.
9. A final “send test nudge” verification.

The user must be able to skip integration and still explore the complete product through demo mode.

---

## DEMO MODE

Demo mode is a first-class acceptance surface, not fake screenshots.

Seed two projects and three sessions:

- Claude Code working on authentication.
- Codex working on authentication.
- OpenCode working on an unrelated marketing page.

Provide deterministic fixture runners for:

- conflict;
- changed decision;
- failed approach;
- irrelevant suppression;
- expiry;
- acknowledgement;
- daemon restart with queued delivery retained.

Each demo must write through the same API, storage, scoring, delivery, and UI paths used by real adapters.

Add a reset button that removes only demo-tagged records.

---

## SECURITY AND PRIVACY

Threat-model the product before declaring it done.

At minimum address:

- prompt injection inside captured text;
- malicious project paths;
- path traversal;
- shell-command injection in hook installation;
- poisoned MCP inputs;
- secret leakage;
- symlink/junction surprises on Windows;
- local port exposure;
- settings-file corruption;
- unsafe auto-start behavior;
- one project leaking context into another;
- stale or superseded decisions being presented as current;
- a compromised agent flooding other agents with nudges;
- denial of service through huge payloads or event loops;
- recursive hooks caused by Agent Nudge's own writes;
- desktop renderer privilege escalation.

Required safeguards:

- bind localhost only;
- Electron context isolation on;
- Node integration off in renderer;
- narrow preload bridge;
- content security policy;
- payload size limits;
- allowlisted IPC;
- canonicalized path comparisons;
- project scoping on every query;
- rate limits/noise budgets;
- idempotency and recursion guards;
- secret-pattern redaction before database writes and logs;
- blocked path patterns including `.env*`, credential stores, `.ssh`, auth caches, and private keys;
- no shell construction from untrusted strings;
- backups and atomic settings writes;
- explicit install/uninstall ownership markers;
- no telemetry;
- no auto-update in MVP;
- no external URLs opened without visible user action.

Write `docs/SECURITY.md`, `docs/PRIVACY.md`, root `SECURITY.md`, and tests for the most important boundaries.

---

## INSTALLER SAFETY CONTRACT

The installer is a high-risk subsystem. Treat it as production code.

For every configuration change:

1. Resolve the exact target path.
2. Verify it is one of the supported Claude/Codex configuration locations.
3. Read and parse existing configuration.
4. Produce a preview/diff.
5. Back up the original with timestamp and checksum.
6. Apply an atomic write.
7. Re-parse and validate.
8. Run a doctor check.
9. On failure, restore the backup.
10. Record an install receipt without credentials.

Never overwrite an entire settings file with a template. Never remove hooks or MCP servers owned by other tools.

Tests must cover empty config, existing unrelated hooks, existing MCP servers, duplicate installation, malformed config, permission failure, uninstall, rollback, paths with spaces, and native Windows command invocation.

---

## DOCUMENTATION

### README.md

Include:

- sharp product pitch;
- animated-GIF placeholder instructions or static screenshots generated from demo mode;
- how the product differs from shared memory;
- architecture overview;
- privacy defaults;
- Windows prerequisites;
- install/build/run/package commands;
- demo in under 2 minutes;
- Claude and Codex integration overview;
- CLI reference;
- troubleshooting;
- known limitations;
- development workflow;
- license.

### docs/PRODUCT.md

Include:

- target user;
- job to be done;
- three MVP scenarios;
- non-goals;
- product laws;
- activation event;
- retention hypothesis;
- success metrics;
- biggest risks;
- path from local MVP to paid team product.

### docs/ARCHITECTURE.md

Include:

- component diagram;
- event lifecycle;
- sequence diagrams for all three scenarios;
- trust boundaries;
- adapter capability matrix;
- storage model;
- failure/degradation behavior;
- extension path for new agents.

### docs/PROTOCOL.md

Document:

- schema versions;
- events;
- facts;
- nudges;
- delivery receipts;
- acknowledgement/feedback;
- idempotency;
- expiry/supersession;
- redaction;
- provider adapter contract.

### docs/COMPETITOR-NOTES.md

Record the researched adjacent products and explain the narrow differentiation. Do not make unverifiable claims about their current pricing, adoption, or internals.

### docs/LANDING-COPY.md

Write concise launch copy around:

> The notification layer for AI agents.

Include headline alternatives, problem, three use cases, privacy section, how it works, differentiation, FAQ, and waitlist CTA copy. Do not create or submit a real waitlist.

---

## TEST STRATEGY

Tests are required, not optional polish.

### Unit

- schema parsing and version rejection;
- Windows path normalization;
- project identity isolation;
- redaction;
- relevance score factors and boundaries;
- delivery-mode selection;
- TTL/expiry;
- supersession;
- deduplication;
- noise budgets;
- nudge compiler length limits;
- context-manifest semantics;
- metric calculations.

### Storage

- migrations on empty DB;
- restart persistence;
- WAL/concurrency behavior appropriate to the driver;
- idempotent events;
- queue leasing/retry;
- expiry scans;
- export/purge preview and backup.

### Adapters

- Claude fixtures for supported lifecycle hooks;
- Codex fixtures for supported lifecycle hooks;
- missing fields;
- unknown future fields;
- malformed payloads;
- daemon offline;
- timeout;
- redaction before transport;
- no duplicate injection.

### Installer

- dry-run by default;
- backup/restore;
- owned-marker merge;
- idempotent reinstall;
- clean uninstall;
- malformed settings;
- Windows paths with spaces;
- unrelated config preservation.

### API/MCP

- validation errors;
- project/session isolation;
- payload limits;
- pagination;
- idempotency;
- delivery lifecycle;
- forbidden secret fact retrieval;
- health output.

### End to end

- Scenario A conflict.
- Scenario B changed decision.
- Scenario C failed approach.
- Irrelevant suppression.
- Acknowledge and manifest update.
- Restart retains queued nudge.
- Desktop displays correct explanation and evidence.

No test may require a paid API, real Claude/Codex account, network access, or modification of the user's actual agent configuration.

---

## DEVELOPMENT AND GIT RULES

Before editing:

1. Check whether `C:\Users\manaz\Projects\agent-nudge` exists.
2. If it exists, inspect `git status --short`, branch, remotes, recent log, README, AGENTS.md, and package files.
3. Preserve unrelated user changes.
4. Pull the intended base only if a configured remote exists and the working state makes that safe.
5. Never reset, force checkout, clean, or delete unrelated files.

If creating a new repository:

- create it locally;
- initialize Git;
- use branch `agents/agent-nudge-mvp`;
- do not create a GitHub repository or push without explicit user authorization.

If an existing repository is present:

- work on `agents/agent-nudge-mvp` or a fresh `agents/` branch;
- never push directly to `main`;
- commit coherent milestones;
- open a PR only if the remote exists, authentication works, and the user has already authorized publication in the current task context.

Do not deploy, publish npm packages, register startup tasks globally, edit real Claude/Codex settings, or install real hooks unless the user explicitly authorizes those external mutations. Build and test installation against temporary fixture directories.

---

## PHASED BUILD ORDER

Follow this dependency order. Do not start with the desktop visuals.

### Phase 0 — Preflight and plan

- inspect environment and target path;
- capture Node/npm/Git versions;
- check for existing repo and dirty state;
- create `BUILD_PLAN.md` with checkboxes and verification commands;
- scaffold workspaces and shared config;
- establish Git branch.

Acceptance:

- workspace installs;
- placeholder lint/typecheck/test commands execute;
- no real user config changed.

### Phase 1 — Core protocol

- schemas;
- path/project identity;
- redaction;
- relevance scoring;
- delivery policy;
- nudge compiler;
- table-driven tests.

Acceptance:

- all core tests pass;
- three scenarios produce expected scores and delivery modes;
- irrelevant scenario is suppressed.

### Phase 2 — Storage

- migrations;
- repositories;
- queue;
- manifests;
- metrics;
- export/purge preview;
- restart tests.

Acceptance:

- temporary SQLite database passes integration suite;
- duplicate events do not duplicate nudges;
- queued nudge survives process restart.

### Phase 3 — Daemon

- API;
- queue worker;
- live update transport;
- structured logs;
- health/degradation;
- demo runners.

Acceptance:

- daemon binds only to localhost;
- API integration tests pass;
- all scenarios run through real API/storage paths.

### Phase 4 — MCP and adapters

- MCP tools/resources;
- Claude normalizer/hook runner;
- Codex normalizer/hook runner;
- delivery receipts;
- fixture tests;
- offline/timeout behavior.

Acceptance:

- MCP inspector or an automated client smoke test can register two sessions, record a fact, retrieve a nudge, and acknowledge it;
- adapter fixture tests pass;
- daemon offline never blocks the simulated agent workflow.

### Phase 5 — Safe CLI and installer

- CLI commands;
- process lifecycle;
- doctor;
- dry-run install plans;
- backup/atomic merge/rollback;
- uninstall;
- fixture-directory tests.

Acceptance:

- `install all --scope project --dry-run` shows exact proposed changes;
- tests prove unrelated config is preserved;
- no real home-directory agent config changed.

### Phase 6 — Desktop/tray

- Electron security baseline;
- onboarding;
- dashboard;
- inbox/actions;
- live agents;
- timeline/inspector;
- rules/settings;
- metrics;
- tray state;
- demo controls.

Acceptance:

- renderer works with daemon live and offline;
- demo conflict appears in UI;
- explanation shows score factors and source;
- accessibility smoke checks pass.

### Phase 7 — Packaging and docs

- Windows package;
- screenshots from demo mode;
- README/docs;
- manual test script;
- security review;
- dependency/license review.

Acceptance:

- unsigned Windows artifact is produced if local prerequisites permit;
- otherwise exact packaging blocker is documented while all application builds remain green;
- clean clone instructions are reproducible.

### Phase 8 — Adversarial final review

Review the implementation against every product law and acceptance criterion.

Search specifically for:

- false “agent knows” wording;
- hidden external calls;
- full transcript capture;
- secret leakage;
- cross-project queries missing project scope;
- noisy injection loops;
- settings overwrites;
- unsafe shell interpolation;
- Electron renderer privilege;
- fake metrics;
- demo-only code bypassing production paths;
- TODOs inside critical flows;
- untested Windows path behavior.

Fix findings, rerun the full matrix, and only then write the build receipt.

---

## REQUIRED COMMANDS

Provide working root commands with these names:

```text
npm install
npm run dev
npm run dev:daemon
npm run dev:desktop
npm run lint
npm run format:check
npm run typecheck
npm run test
npm run test:integration
npm run test:e2e
npm run build
npm run package:win
npm run demo
npm run doctor
```

If a command cannot be supported on the current machine, it must fail with a precise actionable explanation, not silently pass.

---

## DEFINITION OF DONE

All mandatory items below must be true:

- The repository exists locally on an `agents/` branch.
- Strict TypeScript monorepo builds.
- Core operation requires no API key or cloud service.
- SQLite persists events, facts, sessions, nudges, deliveries, feedback, and manifests.
- Relevance scoring is deterministic and explainable.
- Delivery timing is implemented, not just represented in types.
- Claude and Codex adapter fixtures pass.
- MCP round-trip smoke test passes.
- CLI dry-run installer previews safe changes and preserves unrelated settings.
- Real user Claude/Codex configuration was not changed during tests.
- Desktop app runs and shows live daemon state.
- Tray state works or an exact platform blocker is documented.
- Conflict, changed decision, and failed approach demos work end to end.
- Irrelevant event is suppressed.
- Nudge can be acknowledged, snoozed, dismissed, and marked used/wrong/stale.
- “Why this nudge?” shows factor-level evidence.
- Expired and superseded facts are not injected.
- Secret redaction tests pass.
- Cross-project isolation tests pass.
- Queue survives restart.
- No raw transcripts are captured by default.
- No telemetry or hidden external requests exist.
- README and required docs are complete.
- Lint, formatting check, typecheck, unit tests, integration tests, and build pass.
- E2E and Windows packaging pass, or exact environment-specific blockers are recorded with all feasible checks green.
- Git status is understood; unrelated files remain untouched.
- Coherent local commits exist.
- No deploy, remote repo creation, push, package publication, or paid action occurred without explicit authorization.

---

## BUILD RECEIPT

Create `BUILD_RECEIPT.md` containing:

```markdown
# Agent Nudge MVP Build Receipt

## Outcome
pass | partial | blocked

## Product proof
- Scenario A:
- Scenario B:
- Scenario C:
- Irrelevant suppression:

## What shipped

## Architecture

## Files and workspaces created

## Verification
| Command | Result | Evidence |

## Security/privacy checks

## Installer safety checks

## Windows package

## Git
- Branch:
- Commits:
- Remote actions taken: none / exact list

## Known limitations

## Decisions made

## Exact next three product-validation steps
```

Also create `build-receipt.json` with equivalent machine-readable fields, command exit codes, timestamps, Git SHA, and artifact paths.

---

## FINAL RESPONSE FORMAT

Return exactly these sections:

1. **Outcome** — one direct sentence.
2. **Product proof** — result of all three scenarios plus irrelevant suppression.
3. **What exists now** — desktop, daemon, CLI, MCP, adapters, storage, docs.
4. **Verification** — every command and pass/fail result.
5. **Windows artifact** — exact path or exact blocker.
6. **Safety** — confirm whether any real agent config, remote, deployment, credential, or external account was touched.
7. **Git receipt** — branch, commits, status, PR URL only if one was authorized and created.
8. **Known limitations** — honest and concise.
9. **Next three validation steps** — user tests, not more speculative features.

Do not end with vague suggestions. Do not call the MVP complete if the demo path or verification is broken. Continue repairing within the batch until it passes or a genuine external blocker remains.

---

## PRODUCT VALIDATION AFTER THE BUILD

Do not implement these as extra MVP scope, but include them in `docs/PRODUCT.md` as the recommended next experiment:

1. Dogfood Agent Nudge across one real repository with Claude Code and Codex for seven days.
2. Measure delivered, acknowledged, dismissed, stale, and actually-used nudges.
3. Interview five multi-agent developers using the demo and the real hook flow.
4. Keep the product only if at least one of these repeatedly occurs:
   - conflicting edits prevented;
   - rejected approach not repeated;
   - changed decision reaches the right agent before implementation;
   - handoff time materially reduced.
5. If the product works, the paid path is team synchronization, policies, audit, shared projects, hosted relay, and enterprise deployment—not a larger generic memory store.

Build the local proof now.
