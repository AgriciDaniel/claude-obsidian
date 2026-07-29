---
date: 2026-06-29
project: recall
agent: codex
status: completed
---
## What I did
- Reset Recall around the new personal intelligence layer direction: living profile, memory graph, taste graph, intent graph, project map, and agent brain.
- Added typed product models, editable demo data, and deterministic mock agent services.
- Added App Router pages for dashboard, capture, inbox, profile, personality, taste, patterns, intent, memory, graph, projects, prompts, ask, export, settings, and agents.
- Rewrote README and added PRODUCT_MAP.md and ROADMAP.md.
- Added tests for the mock agent pipeline and verified the production build.

## Files changed
- `README.md`
- `PRODUCT_MAP.md`
- `ROADMAP.md`
- `.gitignore`
- `package.json`
- `package-lock.json`
- `InstagramImporter.tsx`
- `app/layout.tsx`
- `app/page.tsx`
- `app/globals.css`
- `app/components/*`
- `app/{dashboard,capture,inbox,profile,personality,taste,patterns,intent,memory,graph,projects,prompts,ask,export,settings,agents}/page.tsx`
- `lib/types.ts`
- `lib/mockData.ts`
- `lib/agents.ts`
- `tests/agents.test.ts`

## Decisions made
- Kept the existing authorised import/API work intact instead of deleting it.
- Used mock deterministic services first so the architecture is understandable before real AI, OCR, transcript, embeddings, and MCP integrations.
- Kept social capture framed as user-provided links, official exports, browser extension capture, or future authorised APIs.
- Used evidence IDs throughout profile, insight, taste, intent, and prompt outputs.

## Next steps
- Add durable storage for `MemoryItem`, profile versions, and insight accept/reject state.
- Wire `/capture` to persist memory items instead of local preview only.
- Add real transcript/OCR/model adapter boundaries behind the current mock agents.
- Add Obsidian markdown and JSON export downloads.
- Open a PR from `agents/recall-personal-intelligence-reset` once the project remote is configured.
