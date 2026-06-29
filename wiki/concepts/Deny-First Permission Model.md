---
address: c-000009
type: concept
title: "Deny-First Permission Model"
created: 2026-06-05
updated: 2026-06-05
tags:
  - concept
  - agent-architecture
  - security
  - claude-code
status: developing
related:
  - "[[Agent Harness Engineering]]"
  - "[[queryLoop Architecture]]"
  - "[[Dive into Claude Code]]"
---

# Deny-First Permission Model

Claude Code's safety architecture: deny-first policy, 7 permission modes, 7 independent safety layers, and the invariant that a broad deny always overrides a narrow allow.

## Core Invariant

> **A broad deny always overrides a narrow allow. The strictest rule wins.**

Permissions are never restored on resume — trust is re-established per session from scratch. Design favors auditability over query power.

## 7 Permission Modes (graduated trust spectrum)

From most restrictive to least:

1. `plan` — read-only planning
2. `default` — standard interactive
3. `acceptEdits` — auto-accept file edits
4. `auto` — ML classifier approval (`yoloClassifier`)
5. `dontAsk` — skip permission prompts
6. `bypassPermissions` — internal override
7. `bubble` — internal subagent mode

The spectrum is traversable: auto-approve rates grow from ~20% to 40%+ with developer experience.

## 7 Independent Safety Layers

Defense in depth from tool pre-filtering through shell sandboxing to hook interception.

> [!contradiction] Shared Failure Modes
> Defense-in-depth degrades when layers share constraints. Per-subcommand parsing causes event-loop starvation — commands exceeding 50 subcommands bypass security analysis entirely to prevent the REPL from freezing. This is a known architectural limitation documented in the paper.

## Authorization Pipeline (4 Stages)

1. **Pre-filtering** — strip denied tools from the model's view entirely (model never sees they exist)
2. **PreToolUse hooks** — can return `permissionDecision` to allow/block before rule evaluation
3. **Deny-first rule evaluation** — deny always overrides allow, even when allow is more specific
4. **Permission handler** — 4 branches: coordinator, swarm worker, speculative classifier, interactive

## Auto-Mode Classifier

`yoloClassifier.ts`: separate LLM sidecar with internal/external permission templates. Two-stage: fast-filter + chain-of-thought.

Source of the 93% approval-rate finding, which revealed approval fatigue. The response was to restructure boundaries (not add more warnings) — a concrete example of the "Human Decision Authority" value driving architectural change.

## Pre-Trust Execution Window (CVE Pattern)

2 patched CVEs share this root cause: hooks and MCP servers execute during initialization before the trust dialog appears. This creates a structurally privileged attack window outside the deny-first pipeline.

## Turn Pipeline Integration

Permission gate is step 7 of the 9-step [[queryLoop Architecture]] turn pipeline, after tool dispatch (step 6) and before tool execution (step 8).

## Sources

- [[Dive into Claude Code]] (arXiv 2604.14228)
- [[Dive-into-Claude-Code-README]]

## Related

- [[queryLoop Architecture]] — permission gate is step 7 in the turn pipeline
- [[Agent Harness Engineering]] — permissions are a core harness component (the safety posture decision)
