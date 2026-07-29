# Fable Power Prompts — Tailored to Manaz Portfolio

Source: braith.mp4 thread (5 Fable use-cases). Fable tokens expire 12 July 2026.
All `[X]` filled with real repos/projects. Copy-paste ready.

---

## 1. Multi-Day Migration Architect

**Target: flipsignal (only JS repo in portfolio — migrate to TypeScript, match rest of stack)**

```
Plan and execute this migration end to end: migrate manazoid4/flipsignal from JavaScript to strict TypeScript, matching the conventions used in manazoid4/flowlens and manazoid4/JobFilterV1 (Next.js + TypeScript). Break it into stages — tsconfig setup, dependency types, file-by-file conversion starting with lib/ then components/ then pages/api, then strict-mode cleanup — and only check in if something needs my input. Otherwise keep going until the build is green, lint passes, and every file is .ts/.tsx. Work on a branch and open a PR, never push to main.
```

**Alternate target: SecureShift scrapers → shared scraper core with JobFilterV1**

```
Plan and execute this migration end to end: extract the scraping/scoring pipeline shared between manazoid4/SecureShift and manazoid4/JobFilterV1 into one reusable package, and migrate both repos to consume it. Break it into stages, and only check in if something needs my input. Otherwise keep going until it's done, with both apps building and tests passing. Branch + PR per repo.
```

---

## 2. Financial Model Builder

**Target: FlowLens (actual revenue product)**

```
Build a financial model for FlowLens (workflow-evidence SaaS, UK market, solo founder, Vercel + Supabase + Stripe stack). Model 24 months: pricing tiers, conversion from free trial, churn, infra costs (Vercel/Supabase/AI API spend per active user), and my time as the only cost of labour. Walk through your assumptions as you go, not just final numbers. Where there's uncertainty, show the range instead of one number presented as certain. End with: MRR needed to go full-time, and the 3 assumptions the whole model is most sensitive to.
```

**Alternate: portfolio-level — which product to bet on**

```
Build a comparative financial model for my three most viable products: FlowLens (workflow evidence, has revenue), JobFilterV1 (AI lead qualification for UK trades), and inkweave (AI snippet-to-book, paid tiers). Same 24-month horizon and assumptions framework for each. Walk through assumptions as you go. Where there's uncertainty, show ranges. Conclude with expected-value ranking and what evidence would change the ranking.
```

---

## 3. Deep Research Analyst

**Target: portfolio focus decision — repos + vault as sources**

```
Here's everything I have on which product deserves my focus: the READMEs, specs/ and docs/ folders across manazoid4/flowlens, manazoid4/JobFilterV1, manazoid4/inkweave, manazoid4/mazos-ui, and manazoid4/saved-brain, plus the project notes in manazoid4/claude-obsidian (wiki/projects/). Don't just summarise, synthesise. Tell me where my own past notes agree, where they contradict each other (e.g. what I said each product was "for" at different dates), and what's genuinely uncertain versus what I've already decided and keep re-litigating. End with the single decision the evidence supports.
```

---

## 4. One-Shot App Builder

**Target: portfolio command dashboard (feeds MAZos)**

```
Build me a working app for a single-page portfolio dashboard: pulls my GitHub repos (manazoid4) via the GitHub API, shows last-commit recency, open PRs, and deploy status per project, with FlowLens, JobFilterV1, and inkweave pinned top. Tell me the design direction and why first. Then build the full thing in one pass, something I could actually use — Next.js 14, TypeScript, deployable to Vercel with just a GITHUB_TOKEN env var.
```

---

## 5. Enhanced Skills Builder

**Target: my every-session ship ritual (vault save + PR workflow)**

```
Build a reusable Claude Skill for this task I repeat: at the end of every work session, save outputs/decisions to the manazoid4/claude-obsidian vault (correct wiki folder, frontmatter, index update), commit on a branch, and open a PR — never push to main. Write the full SKILL.md, with a trigger description precise enough to fire on the right requests ("ship it", "save session", end-of-task wrap-up) and quiet on the wrong ones (mid-task saves, unrelated git work), plus any scripts it needs. Tell me where to save it and how to test the trigger works.
```

**Alternate: sharpen existing ultrawork skill**

```
Build a reusable Claude Skill upgrade for this task I repeat: the /ultrawork autonomous chain. Read my existing ultrawork skill, rewrite the full SKILL.md so it's sharper — precise trigger description that fires on "ultrawork" and max-autonomy requests but stays quiet otherwise, explicit stage ordering, failure handling per stage, and vault-save + PR steps baked in. Tell me where to save it and how to test the trigger works.
```
