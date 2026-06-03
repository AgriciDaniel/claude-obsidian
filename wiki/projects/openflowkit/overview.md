---
type: concept
title: "OpenFlowKit Product Overview"
complexity: basic
domain: product
aliases: ["Open Flow", "OpenFlowKit", "openflowkit overview"]
created: 2026-06-03
updated: 2026-06-03
tags:
  - concept
  - openflowkit
  - product
  - voice
  - privacy
status: current
related:
  - "[[OpenFlowKit Market Fit]]"
  - "[[OpenFlowKit Pricing]]"
  - "[[OpenFlowKit Next Steps]]"
sources: []
---

# OpenFlowKit (Open Flow) — Product Overview

## Definition

Privacy-first browser voice dictation app. Speak into the browser, get clean, context-shaped text out. No backend for core flow. Nothing leaves the device without explicit consent.

- Brand name: Open Flow
- Repo: github.com/manazoid4/openflowkit
- Deployed: openflowkit.vercel.app (Vercel)

## Core Flow

| Step | What happens |
|---|---|
| Speak | Web Speech API captures audio in-browser |
| Auto-clean | Deterministic refinement shapes text to chosen mode |
| Output | Copy to clipboard or generate shareable URL |

No server round-trip for the free tier core flow.

## Six Writing Modes

| Mode | Output style |
|---|---|
| Email | Structured, professional, sentence-complete |
| Slack | Casual, punchy, scannable |
| Code | camelCase / snake_case / commands formatted correctly |
| Formal | Document-grade, polished prose |
| Casual | Conversational, natural tone |
| Raw | Transcript only, no refinement |

Free tier: 3 modes. Pro: all 6.

## Tech Stack

- Vite + React + TypeScript
- Web Speech API (native browser, no AI dependency for free tier)
- Deterministic refinement (rule-based, not LLM-dependent)
- Deployed on Vercel

## Six Business Moats

1. **Offline-capable** — core flow works without internet
2. **Six writing modes** — output shaped per context automatically, not manually
3. **Privacy by default** — audio never leaves device without consent
4. **Team vocabulary** — shared snippets and custom dictionaries
5. **Developer-aware** — code-mode formats identifiers and commands correctly
6. **Speak-to-Share** — voice to URL-encoded shareable snippet, no install needed on recipient's end

## Key Differentiator: Speak-to-Share

Voice input compresses to a shareable URL. Recipient opens it in a browser, no account or install required. Fully client-side, no backend storage.

## Connections

- [[OpenFlowKit Market Fit]]
- [[OpenFlowKit Pricing]]
- [[OpenFlowKit Next Steps]]
