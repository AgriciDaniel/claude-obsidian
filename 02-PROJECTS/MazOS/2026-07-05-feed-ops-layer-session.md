# MazOS Session — AI Feed Ops-Layer Upgrade (2026-07-05)

> PR #19 `feat: feed ops-layer` — merged to main (`9cb66dc`), live on production. Follows [[2026-07-05-ai-feed-v1-report]] and [[2026-07-05-full-audit]].

## What shipped

**Ranking (revenue + velocity)**
- Feed scores now revenue-weighted via Shipping Spine playbook `moneyLabel` (high +8, medium +4).
- Ship-log commits on the current spine priority boosted +5 ("direct progress"); off-priority demoted −5 ("no action needed").
- Spine computed once per feed build, shared across sources.

**Item quality (noise cuts)**
- Runs: all failures + only 2 most recent passes. Ship log capped 6. Resolved decisions capped 3. Intake capped 5.
- `whyItMatters`/`nextAction` rewritten product-specific and directive; stale items carry repo path + branch.

**Agent handoff**
- Copy prompts restructured: OBJECTIVE / CONTEXT / EVIDENCE / READ FIRST / VERIFY WITH / REPORT BACK.
- Spine feed item reuses the real spine handoff prompt (repo, branch, verify, done criteria).
- `→ Task Gate` button on every feed item drafts it into `/sessions` preflight scoring (localStorage handshake).

**System internals (new)**
- `GET /api/mazos/system` + `src/lib/mazos/systemInfo.ts`: CPU %, RAM, GPU VRAM/util/temp (read-only nvidia-smi), disk free, uptime.
- SystemStrip under cockpit header, local mode only, red at ≥90% CPU / ≥92% RAM / ≥92% VRAM. Hosted hides it (`local:false`).
- Feed emits memory-pressure attention item at ≥92% RAM/VRAM.

**UI**: dense 2-col feed grid (verdict + ~10 items in one viewport), `Spine (NOW)` jump from verdict.

## Validation

- lint ✓, build ✓, local system route 200 (GTX 1660 Ti, 1128/6144 MB VRAM read live), local feed 200.
- Production after merge: `/api/mazos/system` 200 `local=false`, `/api/mazos/feed` 200 hosted-fallback verdict "Ship next: JobFilter", root 200.

## Next steps (planned, not built)

1. **Read/mute state** — `data/mazos/feed-state.json`, local-only writes; only if v1.1 proves daily-useful.
2. **Thumbs up/down ranking feedback** — static per-type weight file, personal ranking without any model.
3. **Proof Receipts as feed items** — roadmap feature 3, natural fit for run/commit evidence.
4. **Prompt-only "summarize this feed"** — copyable LLM prompt before any automatic calls.
5. **External AI feed v2** — GitHub/Reddit curated builder feed; Gemini research prompt already written ([[2026-07-05-ai-feed-research-prompt]]), report pending. Feed tab + intake queue are its landing zone.
6. **Hygiene from audit**: delete ~10 stale merged branches; disk on local machine at 17 GB free — worth clearing before big builds.
