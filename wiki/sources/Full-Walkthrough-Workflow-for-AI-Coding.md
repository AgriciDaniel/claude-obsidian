---
type: source
title: "Full Walkthrough: Workflow for AI Coding"
address: c-000003
created: 2026-07-20
updated: 2026-07-20
tags:
  - ai-engineering
  - agent-workflows
  - software-delivery
  - source
status: mature
related:
  - "[[Matt Pocock]]"
  - "[[AI Engineering Delivery Loop]]"
  - "[[2026-07-20-live-agent-bridge]]"
sources:
  - "[[.raw/articles/full-walkthrough-workflow-for-ai-coding-matt-pocock-2026-04-24.en-orig.vtt]]"
source_type: video
author: "Matt Pocock"
date_published: 2026-04-24
url: "https://www.youtube.com/watch?v=-QFHIoCo-Ko"
confidence: high
key_claims:
  - "AI coding tasks should stay inside a fresh-context smart zone and be split into small independently grabbable vertical slices."
  - "Human alignment and QA remain essential; autonomous implementation should run against explicit tasks and fast feedback loops."
  - "Shared execution state, dependencies, tests, and fresh-context review are more reliable than continuously compacting a long conversation."
---

# Full Walkthrough: Workflow for AI Coding

## Source snapshot

- Presenter: [[Matt Pocock]]
- Publisher: AI Engineer
- Runtime: 1:36:30
- Published: 2026-04-24
- Ingested: 2026-07-20
- Transcript: YouTube English original automatic captions
- Raw transcript SHA-256: `a464b86a1d5ece7e07553497bc1fff0ed0b6c463e4fe3d3cbe013e58a5bedace`

## Executive summary

Pocock presents an end-to-end AI-assisted software delivery workflow built around shared understanding, compact execution state, independently grabbable work, test-driven feedback, and deliberate human review. The core argument is conservative in a useful way: AI changes the speed and shape of implementation, but established software-engineering practices still determine whether the result is coherent and reviewable.

The workflow is not “write a specification and trust generated code.” Humans establish the design concept and destination, agents execute bounded slices, and humans re-enter for QA, architecture, and taste. Parallel agents are coordinated through explicit task dependencies, branches/worktrees, tests, and review—not by sharing an ever-growing transcript.

## Workflow

1. **Protect the smart zone.** Fresh contexts perform better than heavily accumulated ones; keep the permanent prompt small and size work so exploration, implementation, and testing fit inside a bounded session (`00:03:00–00:11:05`).
2. **Grill the idea before planning.** The agent interviews the human one question at a time until both share a design concept, surfacing decisions the original brief omitted (`00:12:17–00:21:17`).
3. **Create a destination document.** Summarize the aligned concept into a PRD with user stories, implementation decisions, testing decisions, and explicit out-of-scope items (`00:29:18–00:35:56`).
4. **Turn the PRD into a dependency graph.** Slice it into independently grabbable issues with blocking relationships, separating human-in-the-loop work from AFK implementation (`00:39:32–00:53:12`).
5. **Prefer vertical tracer bullets.** Each early slice should cross the relevant storage, service, API, UI, and test boundaries so the system produces feedback immediately (`00:42:50–00:46:58`).
6. **Implement with feedback loops.** Agents choose an unblocked task, use TDD, run types/tests, commit, and report a bounded result (`00:54:02–01:10:58`).
7. **Review from a fresh context.** A separate review context avoids asking an already saturated implementation session to judge its own work (`01:05:11–01:06:24`).
8. **Keep humans at the quality boundary.** Manual QA imposes product taste and catches failures that automated tests miss (`01:11:17–01:13:35`).
9. **Design deep, testable modules.** Small interfaces around substantial behavior make codebases easier for humans and agents to understand and test (`01:14:19–01:23:07`).
10. **Parallelize only independent work.** A planner selects unblocked issues, implementers work in isolated branches/worktrees, reviewers inspect the commits, and a merger integrates the branches (`01:29:50–01:32:19`).

## Implications for Agent Nudge

This source strengthens Agent Nudge’s narrow product thesis:

- The product should share **current execution state and constraints**, not raw conversation history.
- A recipient needs the **smallest relevant delta** at session start and immediately before consequential action.
- Task intent, dependencies, path claims, changed decisions, failed approaches, and verification receipts are the highest-value shared objects.
- Each agent needs a delivery cursor and acknowledgement state so context arrives once and can be proved current.
- Claims need leases and expiry to avoid turning transient work into permanent stale locks.
- The useful loop is `declare → preflight → act → receipt`, with the context pack acting as a preflight instrument.
- The live product proof must use the production ingestion and sync path, not seeded dashboard fixtures.

## Tensions and cautions

- The presentation is a practitioner workshop, not a controlled study; its numerical context-window heuristics should be treated as experience-based guidance.
- The source recommends removing completed PRDs to avoid documentation rot. Agent Nudge should instead preserve immutable facts while making expiry, supersession, invalidation, and current-state folding first-class so stale history cannot masquerade as current instruction.
- Parallel output increases review load. The product should measure avoided collisions and changed actions, not celebrate agent count or message volume.
- Provider capabilities differ. Hard blocking should be capability-labelled and opt-in; advisory preflight remains the portable baseline.

## Chapters

- `00:00:14` — Thesis of AI engineering
- `00:04:20` — Research and prototyping
- `00:12:45` — Grill session
- `00:22:10` — Writing the PRD
- `00:35:50` — Slicing work into issues
- `00:48:15` — Implementation with AI agents
- `01:05:30` — Human-in-the-loop review
- `01:18:45` — Deployment and monitoring
- `01:28:10` — Codebases for AI effectiveness
- `01:34:06` — Final takeaways

## See also

- [[AI Engineering Delivery Loop]]
- [[2026-07-20-live-agent-bridge]]
- [[2026-07-19-video-ingest-codex-followthrough]]
