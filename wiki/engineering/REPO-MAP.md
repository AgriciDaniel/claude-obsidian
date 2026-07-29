---
title: Engineering Repo Map
created: 2026-07-05
updated: 2026-07-05
type: summary
tags: [engineering, repo-map]
---

# Engineering Repo Map

Links: [[wiki/projects/INDEX]] · [[wiki/engineering/AGENT-HANDOFF]]

## Stack map

| Project | Frontend | Backend/API | Data | Auth | Payments | AI | Deploy |
|---|---|---|---|---|---|---|---|
| JobFilter | React 19 + Vite | Express `server.ts` | Firestore | Firebase Auth | Stripe | Google GenAI dep; deterministic scoring | Firebase Hosting likely |
| InkWeave | Next.js 16 App Router | none observed | none observed | none observed | planned | generation pipeline types only | Vercel likely |
| OpenFlowKit | React 19 + Vite | local bridge only | local/in-memory likely | none observed | planned Pro/Teams | provider-neutral STT/LLM design | Vercel static + local bridge |
| Zawiya | Markdown/Obsidian/Notion | Node scripts | Markdown + Notion | Notion/GitHub access | n/a | AI workflow docs/prompts | GitHub repo + Notion sync |

## Shared patterns

- Agent-readable Markdown docs (`AGENTS.md`, `CLAUDE.md`) appear in all active repos.
- Vault path convention: project notes under `wiki/projects/{project}/`.
- Preferred workflow: pull latest, inspect state, make surgical changes, build/test, update vault.
- Most products are early-stage; avoid adding architecture before first paid/user flow works.

## Deployment style

| Style | Projects |
|---|---|
| Static web app | OpenFlowKit, maybe InkWeave |
| Fullstack Node/Vite | JobFilter |
| Knowledge repo + sync scripts | Zawiya |

## Auth/payments maturity

- JobFilter: most mature; Firebase + Stripe present.
- InkWeave: payment/auth needed before monetisation.
- OpenFlowKit: pricing/plan model exists; billing not implemented.
- Zawiya: operational; external auth through Notion/GitHub, not app users.

## AI usage maturity

- JobFilter: AI dependency exists but core value currently deterministic lead filtering/scoring.
- InkWeave: AI is core promise; implementation still mostly types/copy.
- OpenFlowKit: LLM-agnostic refinement design; browser capture + local bridge implemented.
- Zawiya: AI used for approved-safe ops/reporting workflows; privacy boundaries are strict.

## Fragile/risky areas

- JobFilter local divergence is severe. Backup before reset/merge.
- Zawiya private spiritual boundaries must be respected.
- OpenFlowKit bridge/native injection can become security-sensitive; keep local-only until reviewed.
- InkWeave must not overbuild; prove one paid generation path first.
