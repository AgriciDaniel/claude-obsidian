# MazOS AI Feed — Gemini Research Prompt

> Created 2026-07-05. Copy everything below the line into Gemini (research agent). Self-contained — includes MazOS audit context inline.
> Repo: https://github.com/manazoid4/mazos-ui · Live: https://mazos-command-centre.vercel.app

---

# RESEARCH BRIEF: "AI Feed" for MazOS — deep research task

You are a research agent. Produce a thorough, citation-backed research report. Do NOT write code. Every claim about a tool, repo, or API must include a link.

## 1. Context — what MazOS is (read carefully, your recommendations must fit this)

MazOS is a **personal, local-first AI command cockpit** ("Jarvis-lite") for a solo founder running multiple projects with AI coding agents. Key facts:

- **Stack**: Next.js 16 (App Router), React 19, TypeScript, Tailwind 4, zustand. Deployed on Vercel at https://mazos-command-centre.vercel.app.
- **Philosophy**: prompt-first, never-executing. Safe mode on. The app mostly *generates copyable prompts* for AI agents rather than executing actions itself.
- **Persistence constraint (critical)**: **no database**. All state is flat files (JSONL event logs + markdown) under `data/mazos/` on a local Windows machine. Vercel's filesystem is read-only, so the hosted version degrades gracefully; full functionality requires a **local bridge** (Node proxy on `127.0.0.1:3047` forwarding to the local dev app on port 3046). The hosted UI tries the bridge first, falls back to hosted API.
- **Existing UI**: single cockpit page with tabs — NOW (Shipping Spine: per-product next actions), LOOPS (agent loop templates + decision inbox), PROJECTS (git-evidence project status, ship log, handoff generator), INTAKE (URL/PDF ingest queue → JSONL, Obsidian vault scan, tool router), SYSTEM (service health, action matrix). Plus `/sessions` (agent task gate scoring), `/focus` (45-min sprints), `/openwiki` (knowledge base cockpit).
- **Existing ingestion precedent**: INTAKE tab already queues URLs/files as JSONL for later agent processing — the natural entry point pattern for a feed.
- **User**: technically capable, uses Claude Code / other coding agents daily, wants high signal density, zero tolerance for hype.

## 2. The feature to research — the AI Feed

A new panel/tab in MazOS: a **curated, high-signal feed of what people are actually building in AI right now** — the genuinely good stuff being shown on GitHub, Reddit, Hacker News, X, and blogs. Think "personal HN front page, but only AI builder content, aggressively filtered."

Hard requirement: **remove the gimmicky stuff**. No hype threads, no "I built a startup in 10 minutes" demo-ware, no landing-page-only launches, no engagement bait. Keep: real tools, agent patterns, MCP servers, workflows, repos, and techniques a builder would actually adopt.

## 3. Research questions — answer ALL of these

### A. Sources & APIs
Survey the best programmatic sources for AI builder content and how to pull from each in 2026:
- GitHub: trending (no official trending API — what are the current viable options: scraping, third-party APIs, GitHub search API sorted by stars/created date?), releases of key repos, topic feeds.
- Reddit: current API access rules/pricing for personal low-volume use; which subreddits have highest signal for AI builders (r/LocalLLaMA, r/ClaudeAI, r/MachineLearning, others?); JSON endpoints vs official API.
- Hacker News: Algolia HN Search API (free, no auth) — query patterns for AI content.
- Others worth including or explicitly rejecting: lobste.rs, Product Hunt, HuggingFace trending models/spaces, arXiv (cs.AI/cs.CL), X/Twitter (API cost — likely reject, confirm), newsletters/RSS (which ones are worth parsing), Bluesky.
For each source: API/endpoint, auth requirements, rate limits, cost, ToS considerations for a personal single-user tool, and honest signal-to-noise assessment.

### B. Prior art — teardown existing projects
Find open-source projects that already do this or something close: AI news aggregators, personal feed curators with LLM ranking, HN-style AI digests, "trending repos" dashboards, self-hosted RSS readers with AI filtering (e.g., anything in the Miniflux/FreshRSS + LLM space), GitHub digest bots. For each: repo link, what it does, what's genuinely good about its approach, what's weak, and what MazOS should steal from it. Minimum 8 projects, ranked.

### C. Curation & ranking — the gimmick filter
This is the heart of the research. How to algorithmically + LLM-assistedly separate signal from noise:
- Mechanical heuristics: star *velocity* vs absolute stars, commit recency/cadence, real code vs README-only repos, author track record, comment depth vs upvote count, cross-source corroboration (same project appearing on HN + Reddit + GitHub trending).
- LLM-as-curator patterns: scoring rubrics people actually use in production, prompt patterns for relevance/quality scoring, dedupe and clustering of the same story across sources, cost-efficient batching (score 100 items in one call).
- Propose a concrete **gimmick-filter rubric**: a scored checklist (e.g., working code exists / solves recurring workflow vs one-shot demo / maintained >30 days / adopted by others / substantive discussion) with suggested weights and a cut threshold.

### D. Content seed — what's cool right now
Survey the current (mid-2026) landscape and deliver a **starter feed of ~30 items**: impressive, non-gimmicky AI projects recently shown on GitHub/Reddit/HN. Prioritize categories relevant to MazOS's user: agent harnesses and orchestration, Claude Code / coding-agent tooling and workflows, MCP servers, local-first AI tools, personal automation cockpits/dashboards (MazOS-adjacent), knowledge/memory systems for agents. For each item: name, link, one line on why it matters, which category.

### E. Architecture recommendation (respect the constraints)
Given: Vercel read-only fs, no database, local bridge pattern, file-based JSONL persistence, solo user, prompt-first philosophy. Recommend:
- Ingestion cadence and where it runs (local scheduled task vs Vercel cron vs GitHub Action committing JSONL to the repo).
- Storage: stay file-based/local-only via bridge, or minimal cloud store (Vercel KV, Supabase free tier, or JSONL-in-git)? Weigh honestly for a single user.
- Scoring pipeline shape: fetch → mechanical pre-filter → LLM batch score → JSONL feed file → UI. Estimate monthly LLM cost at realistic volumes (e.g., 500 candidate items/day pre-filtered to 100 scored).
- Read/triage UX patterns worth copying from the best readers (keyboard triage, save-to-intake, "why this surfaced" explanations, thumbs up/down feeding back into scoring).

## 4. Deliverable format

Single structured markdown report:
1. **Executive summary** (10 lines max).
2. **Sources table** (source, API, auth, limits, cost, signal rating, verdict include/reject).
3. **Prior-art teardown** (ranked, with steal-this notes).
4. **Gimmick-filter rubric** (scored checklist, ready to implement).
5. **Starter feed** (~30 items, categorized).
6. **Recommended architecture** (one primary recommendation + one fallback, with reasoning tied to the constraints in §1).
7. **Risks & open questions**.

Cite links throughout. Prefer primary sources (repos, API docs) over blog posts about them. Flag anything you're uncertain about instead of guessing.
