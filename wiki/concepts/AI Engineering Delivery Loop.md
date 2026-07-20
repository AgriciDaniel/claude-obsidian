---
type: concept
title: "AI Engineering Delivery Loop"
address: c-000005
created: 2026-07-20
updated: 2026-07-20
tags:
  - ai-engineering
  - multi-agent
  - delivery-loop
  - concept
status: mature
related:
  - "[[Full-Walkthrough-Workflow-for-AI-Coding]]"
  - "[[Matt Pocock]]"
  - "[[2026-07-20-live-agent-bridge]]"
sources:
  - "[[.raw/articles/full-walkthrough-workflow-for-ai-coding-matt-pocock-2026-04-24.en-orig.vtt]]"
complexity: intermediate
domain: "AI-assisted software engineering"
aliases:
  - "agentic engineering workflow"
  - "AI coding delivery workflow"
---

# AI Engineering Delivery Loop

The AI Engineering Delivery Loop is a human-guided workflow for turning ambiguous product intent into bounded, independently executable agent work with fast feedback and explicit review.

```text
idea
  → grill assumptions
  → research or prototype where uncertain
  → destination PRD
  → dependency-aware vertical slices
  → agent implementation with TDD
  → fresh-context automated review
  → human QA and taste
  → deployment evidence
  → new issues or completion receipt
```

## Core principles

### Shared understanding before autonomy

The human and agent first build a common design concept by resolving decisions one at a time. This is more important than polishing a long plan. Ambiguity that changes scope, architecture, user experience, data, or verification remains human-in-the-loop.

### Destination and journey are separate

The PRD describes the destination: problem, solution, user stories, implementation decisions, tests, and exclusions. The issue graph describes the journey: small tasks, dependencies, and which tasks can safely run in parallel.

### Vertical slices create early evidence

A thin slice crosses the relevant layers and yields something observable and testable. Horizontal batches delay integration feedback and let errors compound before the agent sees a working system.

### Execution state lives outside the conversation

Tasks, dependencies, claims, commits, tests, decisions, failures, and receipts are durable structured state. The conversation can be cleared. The next agent reconstructs the current situation from the compact state rather than inheriting an increasingly noisy transcript.

### Review uses a fresh context

Implementation and review should not share the same saturated context. A reviewer receives the diff, requirements, standards, and test evidence in a clean window. Humans retain the final architecture, QA, and taste boundary.

### Parallelism requires explicit coordination

Agents can work simultaneously only when tasks are independently grabbable and their dependencies, branch/worktree boundaries, and integration targets are visible. Parallelism without intent and conflict state merely creates more review and merge work.

## Agent Nudge mapping

Agent Nudge should not become the planner or orchestrator for this loop. It should guard the transitions between tools and sessions:

| Delivery-loop state | Agent Nudge object | Delivery moment |
|---|---|---|
| Current objective and paths | Session heartbeat / task intent | Session start and renewal |
| Work ownership | Expiring path or decision claim | Before overlapping work |
| Changed requirement | Versioned decision fact | Before affected action |
| Rejected approach | Failure fact + evidence | Before repetition |
| Completed slice | Verification/handoff receipt | Next session or review |
| Recipient position | Cursor + acknowledgement | Every sync boundary |

The narrow protocol is:

```text
declare → preflight → act → receipt
```

This yields the product test that matters: not whether a model may have stored some context, but whether the relevant agent received the current constraint before acting and whether the action changed.

## Failure modes

- **Transcript dumping:** raises context cost and mixes current state with obsolete exploration.
- **Stale documentation:** a completed plan is mistaken for current instruction.
- **Horizontal task slicing:** feedback arrives after multiple dependent layers have drifted.
- **Unleased locks:** abandoned agent state blocks future work forever.
- **Fixture-only dashboards:** the interface appears coordinated while no real provider event enters the loop.
- **Agent-count vanity metrics:** parallelism rises while useful output and review capacity do not.

## See also

- [[Full-Walkthrough-Workflow-for-AI-Coding]]
- [[2026-07-20-live-agent-bridge]]
- [[2026-07-19-video-ingest-codex-followthrough]]
