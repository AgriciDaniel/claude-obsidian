# MAZos Investor Site — Build Prompt (loop spec, 3 iterations)

> Repo: `manazoid4/mazos-site` (new, public). Local: `C:\Users\manaz\mazos-site`.
> Audience: AI-literate investors and operators. Goal of the loop: **finished scaffold** — deployable one-pager, build green, three verified iterations.

## PRODUCT PITCH (the content truth — do not embellish)

MAZos is a **loop cockpit**: an operating console where a solo founder turns "what should ship next" into supervised AI agent loops with machine-verified receipts. Agents generate; MAZos gates, verifies, and keeps score. It is the missing control plane for the loop-engineering era (Osmani/Cherny, June 2026: "stop prompting agents, design the loops that prompt them").

Honest evidence (no invented numbers):
- Running daily as the operator's own control plane across a 5-product portfolio
- Every loop iteration produces a machine receipt: verify exit code, commit range, diff size, criteria tamper-hash
- Loops cannot self-complete: completion requires a passing receipt + all criteria + (for autonomous loops) an independent evaluator
- Autonomous morning triage discovers work and proposes loops; a human approves every one
- Built on the published playbooks: Anthropic harness engineering, generator/evaluator split, Ralph-style plan/build loops

## DESIGN LAW (anti-AI-slop, JobFilter-quality)

- One page. No gradients, no glassmorphism, no emoji, no "Unlock the power of AI", no stock illustration.
- Industrial-clean: white/near-white background, ink text, ONE accent color, hard 2px borders, mono for data/labels only, generous whitespace, line-height 1.6.
- Every claim concrete and evidence-shaped (like JobFilter's proof points). If a number isn't real, don't show a number.
- Sections: (1) masthead one-liner + what it is in 2 sentences; (2) THE LOOP — 5-step strip (discover → gate → prompt → verify → receipt); (3) RECEIPTS — a real receipt rendered as the hero artifact (JSON, real fields); (4) WHY NOW — 3 short grafs (loop engineering wave, verification bottleneck, solo-operator leverage); (5) OPERATOR — who built it, portfolio line; (6) CONTACT — one email CTA, no forms.
- Stack: Next.js App Router + TypeScript + plain CSS. Zero other deps. Static export-friendly.

## LOOP CONTRACT (3 iterations, each ends verify-green + commit)

- Iteration 1 — SCAFFOLD (vertical slice): repo init, package.json/tsconfig/next config, globals.css design system, complete page.tsx with all 6 sections in final structure (placeholder-free copy, first pass). Verify: `npm run build` exit 0. Commit.
- Iteration 2 — EVIDENCE + POLISH: render the real receipt artifact, tighten all copy (cut 30%), responsive pass, metadata/OG/title. Verify build. Commit.
- Iteration 3 — SHIP QUALITY: a11y (landmarks, contrast, focus), README, favicon, final copy read-aloud pass; RATCHET: add `npm run lint` (tsc) so regressions can't ship silently. Verify build + lint. Commit.
- Stop conditions: 3 iterations max; any iteration failing verify twice → stop and report.
- FORBIDDEN: extra pages, analytics, forms, dependencies, fake metrics, testimonials.
