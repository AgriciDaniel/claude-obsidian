# MazOS Full Audit — 2026-07-05

> Agent audit of local repo + GitHub (manazoid4/mazos-ui) + live Vercel deploy. Feeds the [[2026-07-05-ai-feed-research-prompt]].

## (a) Current State Summary

- **Repo**: `C:\Users\manaz\Projects\mazos-ui` → github.com/manazoid4/mazos-ui. Next.js 16 / React 19 / TypeScript 6 / Tailwind 4 / zustand. Typecheck (`tsc --noEmit`) **passes clean**.
- **Checked-out branch**: `agents/openwiki-cockpit` (NOT main), 1 commit ahead of main (`e3b00e6 feat: add OpenWiki cockpit`), pushed, with **open PR #15** awaiting merge.
- **Uncommitted**: untracked `data/` (runtime JSONL/state), `tsconfig.tsbuildinfo`, modified `research/mazos/latest-vault-scan.md`, dirty `external/agent-sources/penpot` submodule.
- **12 local branches**, all pushed; 0 open issues; only PR #15 open.
- **Vercel project**: `mazos-command-centre`, live at **https://mazos-command-centre.vercel.app**, deployed from **main** (`aca06d0`).
- **Identity**: local-first "Jarvis-lite" command cockpit. Deliberately **prompt-first, never-executing**: `config/control-panel.yaml` sets `safe_mode: true, allow_shell: false, allow_push: false`. Almost everything generates copyable prompts.

## (b) Recent Changes (repo only exists ~2 weeks)

- **Jul 1**: Command-centre rebuild — tabbed cockpit (NOW/LOOPS/PROJECTS/INTAKE/SYSTEM), command palette (Ctrl+K), Loop Engineering deck, Decision Inbox, project status, Hermes external agent-source submodules + Tool Router.
- **Jul 2–3**: Vercel deployment prep; **local bridge** (`scripts/mazos-local-bridge.mjs`, port 3047 → local app 3046, proxies only `/api/mazos/*`); auto-start scheduled task "MAZos Local Stack".
- **Jul 4**: **Shipping Spine v1** (PR #11) — playbooks + spine API + first-viewport panel; fix for 500 on Vercel read-only fs (PR #13); **Agent Task Gate + Mission Planner** (`/sessions`, task scoring 0–100, risk levels); Market-Breaker roadmap doc.
- **Jul 5**: **OpenWiki cockpit** (`/openwiki` page + API, OpenWiki desktop app/SQLite integration) — **PR #15, open, not yet on main/production**.

## (c) Feature Inventory

**Done & deployed (on main + live):**

| Feature | Where | Notes |
|---|---|---|
| Shipping Spine | NOW tab + `GET /api/mazos/shipping-spine` | Flagship. Per-product row: objective, next action, blocker, owner, safety, handoff prompt. Live, 200. |
| Product Playbooks | `src/lib/mazos/playbooks.ts` | 4 hardcoded playbooks: JobFilter, Recall, OpenFlowKit, MAZos. |
| Loop Engineering Deck | LOOPS tab, `/api/mazos/loops` | Ralph-style loop templates with budgets/gates. Never executes — copies runner prompts. |
| Decision Inbox | LOOPS tab, `/api/mazos/decisions` | Stop-and-ask queue; approve/deny/answer → resolution prompt. JSONL log. |
| Project Command Cards + Status | PROJECTS tab, `/api/mazos/project-status` | Git-evidence status for JobFilter/Recall/MAZos/Vault. |
| Ship Log | PROJECTS tab, `/api/mazos/shiplog` | Commits today/7d across repos + publishable update markdown. |
| Stale Work Radar | NOW + PROJECTS, `staleRadar.ts` | Dirty/unpushed findings → "babysit prompt". |
| Handoff Generator | PROJECTS tab, `handoff.ts` | Scoped Hermes/Codex briefs, safety L1–L3 + verify commands. |
| Context Packs | `/api/mazos/context-pack` | Per-project markdown pack saved to `data/mazos/context-packs`. |
| Repo Command Centre | PROJECTS tab, `/api/mazos/repos` | Branch/dirty/unpushed/scripts per configured repo. |
| Source Intake | INTAKE tab, `/api/mazos/ingest` | URLs/PDFs → queue JSONL routed to Recall/Obsidian. |
| Vault Intelligence | INTAKE tab, `/api/mazos/vault` | Light Obsidian vault scan. |
| Tool Router | INTAKE tab, `/api/mazos/tool-router` | Keyword-routes tasks to external agent-source submodules. |
| Ops Radar | SYSTEM tab, `/api/mazos/health` | Pings localhost services; all offline from cloud without bridge (expected). |
| Action Matrix + Run History | SYSTEM tab, `/api/mazos/action`, `/api/mazos/runs` | ~30 actions in `commandRegistry.ts`; mostly prompt handlers. |
| Command Palette | Ctrl+K overlay | Fuzzy actions/loops/projects/tabs. |
| Agent Task Gate | `/sessions`, `/api/mazos/task-gate` + `/api/mazos/mission-plan` | Preflight scoring of agent tasks; mission planner. Live, 200. |
| Local Bridge | `scripts/mazos-local-bridge.mjs` | Hosted UI tries `127.0.0.1:3047` first, falls back to hosted API. |
| Focus Sprint | `/focus`, `/api/mazos/focus`, zustand `focusStore.ts` | 45-min accountable sprint mode. |

**Done but NOT deployed (PR #15, current branch):** OpenWiki cockpit — `/openwiki` page + `GET/POST /api/mazos/openwiki`.

**Stubbed / half-done:**
- Email digest (`/api/mazos/email*`, Resend): `email.enabled: false`, env vars unconfirmed. Dormant.
- Loops: STATE.md says "Last run: never" — infra built, never calibrated/used.
- Roadmap features 3–5 not built: Proof Receipts, Safe Action Capsules, Founder Revenue Radar (`docs/MAZOS_MARKET_BREAKER_ROADMAP.md`).
- `.ralph/` state inconsistency (STATE says complete, prd.json pending).
- `install.ps1` / README "port 9999" / Python prerequisite legacy — actual app is `next dev -p 3046`.
- No tests; "lint" is just `tsc --noEmit`.

## (d) Architecture — relevant to adding an AI Feed panel

- **Framework**: Next.js 16 App Router; all client UI essentially one big client component per page (`src/app/page.tsx` = 334 dense lines, tab-switched inline panels). Pages: `/`, `/sessions`, `/focus`, `/openwiki`.
- **Data pattern**: no React Query/SWR — plain fetch via `mazosFetch()` wrapper: tries local bridge (127.0.0.1:3047) first when hosted, falls back to hosted API. New feed **must use `mazosFetch`**. Data via `useEffect` + `useState`; zustand only for focus store.
- **API pattern**: one route per concern at `src/app/api/mazos/<name>/route.ts` (Node runtime); pure logic in `src/lib/mazos/<name>.ts`.
- **Persistence**: no DB. Files under `data/mazos/` — JSONL event logs + markdown snapshots. Hosted Vercel fs read-only; writes try/catch-skipped (`shippingSpine.ts:200-205`). Feed ingestion must run local-only via bridge or get a real store.
- **Ingestion precedent**: INTAKE tab + `/api/mazos/ingest` queues URLs/files as JSONL — natural feed entry point.
- **Component conventions**: `Panel` wrapper, `CopyBlock`, `SafetyBadge` (L1–L3), `setModal({title, body})`, hand-rolled dark theme in `globals.css` (`.panel`, `.repo`, `.spineRow`); Tailwind 4 + shadcn installed but barely used.
- **Where feed lives**: new tab in `TABS` array + `{tab==='FEED'&&...}` block, or on NOW below Shipping Spine; data layer = `src/lib/mazos/feed.ts` + `src/app/api/mazos/feed/route.ts` reading/writing `data/mazos/feed.jsonl` via `mazosFetch`.
- **Env vars (names only)**: `MAZOS_BRIDGE_PORT`, `MAZOS_LOCAL_TARGET`, `RESEND_API_KEY`, `NOTIFY_EMAIL`, `EMAIL_FROM`.

## (e) Live Deploy Health (https://mazos-command-centre.vercel.app)

| Route | Status |
|---|---|
| `/` | 200, cockpit renders |
| `/api/mazos` | 200 |
| `/api/mazos/shipping-spine` | 200, full spine JSON — read-only-fs fix works |
| `/api/mazos/health` | 200 (local services offline from cloud — expected) |
| `/api/mazos/task-gate` | 200 |
| `/sessions` | 200 |
| `/openwiki` + API | **404 — only on PR #15** |

Deployed build = main (`aca06d0`). Only gap between local and production is PR #15.

## (f) Risks / Tech Debt

1. **PR #15 unmerged** — OpenWiki cockpit only unshipped work; branch README already documents it as live.
2. **10 stale agent branches** fully merged/superseded — branch hygiene needed.
3. **No persistence on hosted** — biggest architectural constraint for AI feed (consider Supabase/KV or accept local-only).
4. **Monolithic page.tsx** — feed as separate page/extracted component cleaner (precedent: `/sessions`, `/openwiki`).
5. **Zero tests**; lint is typecheck only.
6. **Hardcoded absolute Windows paths** throughout; exposed publicly via hosted API (low risk, known).
7. No secrets in code (swept clean). No TODO/FIXME in `src/`.
8. **Heavy submodules** (`external/agent-sources/*`) bloat repo; penpot dirty; `.vercelignore` mitigates deploys.
9. Dead/legacy artifacts: `install.ps1`, port-9999/Python README refs, `temp.json`, `.ralph/` mismatch, dormant email code.
10. **Loops never run** — deck untested; STATE.md flags calibration as top task.

Key files for feed work: `src/app/page.tsx`, `src/lib/mazos/shippingSpine.ts`, `src/lib/mazos/playbooks.ts`, `src/app/api/mazos/ingest/route.ts`, `src/lib/mazos/paths.ts`, `scripts/mazos-local-bridge.mjs`, `config/control-panel.yaml`, `docs/MAZOS_MARKET_BREAKER_ROADMAP.md`.
