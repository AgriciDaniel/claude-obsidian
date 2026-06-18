---
type: concept
title: "Spec-Build-Review Loop"
complexity: intermediate
domain: "automation"
aliases: ["loops build guide", "self-fixing loop", "/spec /build /review"]
created: 2026-06-18
updated: 2026-06-18
tags:
  - concept
  - automation
  - claude-code
  - skills
status: current
related: []
sources: ["SF157 Loops Build Guide (Actionable AI)"]
---

# Spec-Build-Review Loop

A loop built from three Claude Code skills that fixes its own work: `/spec` → (`/build` ⇆ `/review` until clean) → done.

## Why a loop beats a single prompt

A prompt is one shot — you ask, take whatever comes back. A loop scores its own output against a standard, fixes the weak parts, and repeats until actually right. Scoring and rewriting are different acts — forcing self-critique before rewrite turns blind editing into directed search.

## The three skills

Installed globally at `~/.claude/skills/{spec,build,review}/SKILL.md` — available to every agent/session, not just this project.

### `/spec`
Interviews user one focused question at a time (goal, requirements, constraints, definition of done). Does NOT build. Writes spec to `specs/<name>.md` with: objective, exact requirements, edge cases, concrete definition of done.

### `/build`
Reads `specs/<name>.md`, builds exactly what it says. No scope creep, no unrelated refactors, no invented requirements. Lists which spec requirements it covered when done.

### `/review`
Compares build against spec requirement-by-requirement. Lists every gap/bug naming the exact spec item failed. Hands fixes back to `/build`. Only passes when every requirement is fully met.

## How to run it

1. `/spec` once, answer its questions → produces `specs/<name>.md`.
2. Paste: "Loop /build and /review: build from the spec, review the build against the spec, fix whatever fails, then repeat until the review passes clean. Keep going on your own until it passes."
3. High effort mode + walk away — it loops `/build` ⇆ `/review` autonomously until clean.

## Lighter-weight variants (not installed, noted for reference)

- **Plan-optimizer skill** (one-command installer, by @goodalexander/@seangeng) — scores/critiques/rewrites any plan until it can't improve.
- **One-paragraph loop** — no install, paste after any task: self-score 0-100 against a rubric you write first, list weakest parts, rewrite, repeat until score stops improving by a real margin.

## Status

Installed 2026-06-18 — `/spec`, `/build`, `/review` live globally in `~/.claude/skills/`.
