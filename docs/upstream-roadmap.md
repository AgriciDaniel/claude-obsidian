# Upstream Roadmap: Deterministic Wiki-Quality Tooling

**Status:** approved — implementation in progress (PR0 next)
**Created:** 2026-05-21
**Last review:** 2026-05-26 (decisions logged below)
**Scope:** Promote vault-proven quality tooling (lint aggregator, enforcement hook, issue-tracking workflow, maintenance utilities) into the `agentic-knowledge-management` plugin so every consuming vault — not just one — gets deterministic, automated quality and consistency.
**Source vault:** `ai-secondbrain` (the reference vault these tools were battle-tested in).
**Target repo:** `philippsied/agent-based-knowledge-management` (fork). No upstream PRs to `AgriciDaniel/claude-obsidian` planned — fork is the production line.

## 0. Decision log (2026-05-26 review)

Closed before implementation. Each maps to a section below.

| # | Decision | Rationale | Affects |
|---|---|---|---|
| D1 | **Split PR3** into **PR3a** (pre-commit) and **PR3b** (CI). | Two tooling decisions in one review = high blast radius. Split lets pre-commit be validated locally before CI rolls out. | §5 table, §5 detail |
| D2 | **Tier-1 mechanism = `.pre-commit-config.yaml`** (pre-commit framework, pre-commit.com). | Industry standard, versioned hook defs, zero-install bootstrap for contributors. Accepts the Python dep cost. | §3.1, §5 PR3a |
| D3 | **CI severity: ERROR + WARN break the build, INFO reports.** | Stricter than "ERROR only" but realistic given the plugin's current clean state. Requires severity classification in `run-lint.sh`. | §3.1, §5 PR3b |
| D4 | **JSON-Schema for frontmatter** ships as **PR1.5** (after PR1, before PR2). | §3.2: schema is the one sub-problem where a standard tool genuinely fits. Separate PR keeps PR1 atomic. | §3.2, §5 PR1.5 (new) |
| D5 | **Env-var name = `KM_VAULT_PATH`** (not `VAULT_PATH`). | Namespaced; consistent with the vault hook's existing `KM_PLUGIN_REPO`; no collision with HashiCorp Vault. | §4, §5 PR0 |
| D6 | **Target = fork only.** No PR back to `AgriciDaniel/claude-obsidian`. | Upstream is push-disabled; fork is the production line. Reduces coordination overhead. | §1 (header) |
| D7 | **Roadmap committed to `main` in the fork** before PR0 (no PR for the doc itself). | Doc is reference material, not code; anchorable from subsequent PR descriptions. | meta — not in doc body |

---

## 1. Why this document exists

The reference vault has accreted a working quality toolchain — a lint aggregator,
a deterministic path/naming-safety hook, a LIFO issue-tracking workflow, and bulk
maintenance scripts. None of it lives in the plugin yet. The naive move is "copy
the scripts and the hook into the plugin." This document argues that the naive
move is **necessary but not sufficient**, defines the architecture that *is*
sufficient, and sequences the work into independently-mergeable PRs.

The driving requirement, stated by the maintainer:

> *Deterministically and automatically preserve the quality and consistency of
> the wiki **from the ground up**.*

"From the ground up" and "deterministically" are the load-bearing words. They
rule out an enforcement layer that only fires inside one specific agent runtime.

---

## 2. Critical assessment — why "just add scripts + a hook" is insufficient

### 2.1 The enforcement-tier gap

The vault's `wiki-path-safety.sh` is wired as a **Claude Code `PreToolUse` hook**.
That hook fires *only* inside interactive Claude Code sessions. It is bypassed by:

- Obsidian UI edits (the vault is an Obsidian vault),
- plain `git commit` from any tool or human,
- **other agents** — and the plugin *actively distributes its skills to other
  agents* via `bin/setup-multi-agent.sh` (symlinks into `.codex/`, `.opencode/`,
  `.gemini/`, `.cursor/`, `.windsurf/`).

The vault's own issue tracker already records this limitation
(*"Hook greift nur in interaktiven Claude-Sessions"*). An author-time hook alone
**cannot** provide a determinism guarantee, by construction.

### 2.2 Drift / no single source of truth

The vault currently *forks* `run-lint.sh`, `lint-orphans.py`, etc., while only
`lint-terminology.py` and `lint-title-overlap.py` are thin wrappers delegating to
the plugin. Naively "adding" the forked scripts to the plugin produces **two
copies that diverge** — exactly the `lint-autofix.py` vs. `rewrite-wikilinks.py`
duplication the vault already suffers from. Any upstream PR must therefore be
paired with **vault-side deletion + delegation**, so the plugin becomes the sole
definition of each tool.

### 2.3 The plugin-is-vault path conflation (the blocking flaw)

Today the plugin repo *is also* a vault, and several scripts assume it:

- `scripts/tiling-check.py:49` → `VAULT_ROOT = Path(__file__).resolve().parent.parent`
- `scripts/lint-terminology.py:222`, `scripts/lint-title-overlap.py:74` →
  `parser.add_argument("root", nargs="?", default="wiki")` (cwd-relative)

When the plugin is installed via the marketplace it lives under
`~/.claude/plugins/…` and is **not** the vault. The `__file__`-relative resolver
then computes the wrong root, and there is **no `VAULT_PATH`/env override** to
redirect it. The vault's own `run-lint.sh` inherits the same latent bug
(`cd "$(dirname "$0")/../.."`). This must be fixed *first* — otherwise every
upstreamed script silently computes the wrong vault root once installed.

---

## 3. Target architecture

### 3.1 Three-tier enforcement pyramid, one runner

```
Tier 0  author-time   Claude PreToolUse hook       fast, in-loop; blocks the bad write mid-session
Tier 1  commit-time   git pre-commit → run-lint     runtime-independent; catches UI / other-agent / plain git
Tier 2  merge-time    CI on PR/push → make lint+test the backstop; nothing merges dirty
        ───────────────────────────────────────────────────────────────────────────
        all three invoke the SAME run-lint.sh → a single, shared definition of "quality"
```

- **Tier 0** is what the vault has today. Keep it — it is the best *developer
  experience* (feedback before the write lands) — but treat it as advisory speed,
  not as the guarantee.
- **Tier 1** is the runtime-independent floor. A git pre-commit hook that runs the
  aggregator on staged wiki files catches everything that reaches local history,
  regardless of which tool or agent produced the edit. **Mechanism: the
  `pre-commit` framework (`.pre-commit-config.yaml`)** — versioned hook
  definitions, contributor zero-install bootstrap (D2).
- **Tier 2** is the deterministic ceiling. The plugin has **no CI today**
  (`.github/` contains only `copilot-instructions.md`). A workflow running
  `make lint` + `make test` on PR/push is the actual "from the ground up"
  guarantee. **Severity gate: ERROR + WARN break the build; INFO reports
  only** (D3) — requires `run-lint.sh` to emit a severity per finding.

All three tiers must call **one** entry point so "quality" is defined once.

### 3.2 Custom checks are unavoidable — consolidate, don't reinvent

Off-the-shelf linters (`markdownlint`, `vale`, JSON-Schema) do not understand
wiki semantics: wikilink hyphenation, DNT termbase synchronization, the
orphan/dead-link graph, address allocation. A thin custom check layer is
required. The right move is to **consolidate the custom checks behind one
runner**, **plus** add JSON-Schema for the frontmatter sub-problem (where a
standard tool genuinely fits — D4). Schema validation ships in **PR1.5**
(post-PR1, pre-PR2) so PR1 stays atomic.

### 3.3 Reuse the existing `wiki-lint` skill

The plugin already ships a `wiki-lint` skill and a `wiki-lint` agent. The
deterministic `run-lint.sh` should be the **engine** the skill calls, with the
skill adding LLM-judgment checks (stale claims, semantic duplication) on top —
not a parallel, duplicated implementation.

---

## 4. Portability analysis & the vault-root convention (the gate)

**What is already portable:** everything Claude Code auto-discovers
(`commands/`, `skills/`, `agents/`, `hooks/hooks.json`) loads without manual
`settings.json` edits; there are zero hardcoded user paths in code/config; setup
scripts derive paths from script location.

**What is not portable:** the tooling scripts (§2.3). Resolution is inconsistent
(`__file__`-relative vs. cwd-`"wiki"`) and has no override.

**Convention to adopt (PR0):** a single vault-root resolver, used by every script:

```
KM_VAULT_PATH (env)  →  positional argv  →  current working directory
```

The `KM_` prefix namespaces the variable (D5), is consistent with the existing
`KM_PLUGIN_REPO` in the vault hook, and avoids collision with HashiCorp Vault's
`VAULT_PATH`.

- Python: a tiny `lib/vault_root.py` helper returning a `Path`.
- Shell: a `lib/vault_root.sh` sourcing helper exporting `$VAULT_ROOT`.
- Default must be **cwd**, not `__file__`, so a marketplace-installed plugin
  operates on the user's vault, not on its own install directory.

The vault's hook already models a good pattern (`REPO_ROOT` derived from
`BASH_SOURCE`, `KM_PLUGIN_REPO` as an override). The shipped plugin version must
**drop the vault-specific `KM_PLUGIN_REPO` default and the `PLUGIN_REPO`
whitelist clause**, keeping only the generic, configurable whitelist.

---

## 5. The multi-PR roadmap

Sequenced by dependency and blast radius. Each PR is independently mergeable,
testable, and revertable. Critical chain: **PR0 → PR1 → PR3a → PR3b**.
PR1.5 / PR2 / PR4 / PR5 can interleave.

| PR | Contents | Purpose / Tier | Depends on | Risk |
|---|---|---|---|---|
| **PR0** | `lib/vault_root.{py,sh}` resolver (`KM_VAULT_PATH`→argv→cwd); route `tiling-check.py` + `lint-*` through it; wire the existing `test_lint_terminology.py` + `test_lint_title_overlap.py` into `make test` | Portability gate | — | low |
| **PR1** | `scripts/run-lint.sh` aggregator (de-vault-ified) + `scripts/lint-orphans.py`; runs terminology + title-overlap + orphans + frontmatter-gaps + spaced-filenames + **spaced-wikilinks-body**; emits JSON + Markdown report with severity (`error\|warn\|info`) per finding; `make lint`; connect to the `wiki-lint` skill | One definition of "quality" | PR0 | low–med |
| **PR1.5** | `schemas/frontmatter.schema.json` + `check-jsonschema` (or `ajv`) wired into `run-lint.sh` as a `frontmatter_schema` check; per-type schemas (`entity`, `concept`, `source`, `synthesis`, …) referenced by `$ref`; severity = `error` for unknown `type`, `warn` for missing recommended fields | Frontmatter validation (D4) | PR1 | low |
| **PR2** | `hooks/wiki-path-safety.sh` (generalized: configurable whitelist, no `KM_PLUGIN_REPO` default / no `PLUGIN_REPO` clause); register as `PreToolUse` (`Write\|Edit\|NotebookEdit`) in `hooks.json` | Tier 0 author-time | — (parallel) | low |
| **PR3a** | `.pre-commit-config.yaml` (pre-commit framework — D2) running `run-lint` on staged wiki files; bootstrap section in `CONTRIBUTING.md` (`pre-commit install`) | Tier 1 — commit-time | PR1 | low–med |
| **PR3b** | `.github/workflows/quality.yml` (the plugin's first CI) running `make lint` + `make test` on PR + push to main; **build fails on ERROR or WARN, INFO reports only** (D3); status badge in README | Tier 2 — merge-time | PR1, PR3a | med |
| **PR4** | `commands/wiki-handoff.md` + `commands/wiki-fix-issues.md` (LIFO push/pop) + `_templates/open-issues.md` + a `wiki-issues` skill + docs. **Mechanism only, not the vault's issue content** | Issue-tracking workflow | — (self-contained) | med |
| **PR5** | `scripts/rewrite-wikilinks.py` + `scripts/lint-rename.py` (+ `scripts/wiki-prepass.py` *after* fixing the German-compound heuristic at `wiki-prepass.py:28`). **`lint-autofix.py` excluded** (dedupe; `rewrite-wikilinks.py` is the keeper) | Bulk maintenance | PR0 | low |

### Per-PR detail & acceptance criteria

**PR0 — Vault-root resolution + portability foundation**
- New: `lib/vault_root.py`, `lib/vault_root.sh`.
- Change: `tiling-check.py` uses the resolver instead of `__file__/../..`;
  `lint-terminology.py` / `lint-title-overlap.py` keep argv but default to cwd
  via the resolver.
- Change: `Makefile` `test` target also runs `test-terminology` + `test-title-overlap`.
- Accept: `KM_VAULT_PATH=/tmp/somevault python3 scripts/lint-terminology.py`
  lints that vault; `make test` runs all five test files green; no script
  references `__file__` for vault root.

**PR1 — Canonical lint aggregator**
- New: `scripts/run-lint.sh` (ported, de-vault-ified, resolver-based),
  `scripts/lint-orphans.py`, `tests/test_run_lint.sh`.
- The runner aggregates the existing plugin checks + orphans + frontmatter gaps +
  spaced filenames + spaced-wikilinks-in-bodies; `--json` and report modes.
- Each finding carries a `severity: error | warn | info` field — required so the
  Tier-2 gate (D3) can distinguish blockers from advisories.
- Change: `wiki-lint` skill calls `run-lint.sh` for the deterministic pass.
- Accept: `make lint` produces a JSON summary with all metric keys + per-finding
  severity; a seeded spaced wikilink and a seeded orphan are both reported;
  report writes to `wiki/meta/lint-report-<date>.md` under the resolved vault root.

**PR1.5 — Frontmatter JSON-Schema validation** (D4)
- New: `schemas/frontmatter.schema.json` (base) + per-type schemas under
  `schemas/types/*.schema.json` (`entity`, `concept`, `source`, `synthesis`,
  `meta`, …) using `$ref` composition.
- New check in `run-lint.sh`: `frontmatter_schema` invoking `check-jsonschema`
  (preferred — pure Python, fits the existing stack) on every `wiki/**/*.md`
  frontmatter block.
- Severity: `error` for unknown `type` / malformed YAML; `warn` for missing
  recommended fields (`updated`, `tags`); `info` for unknown fields.
- Accept: a wiki page with `type: nonexistent` fails lint with severity `error`;
  a page missing `updated` fails with severity `warn`; running the check on the
  current reference vault produces a non-empty but actionable baseline report.

**PR2 — Author-time enforcement hook**
- New: `hooks/wiki-path-safety.sh`; `hooks.json` gains a `PreToolUse` entry.
- Whitelist is data-driven (no hardcoded plugin path); naming rule = hyphenated
  filenames for `wiki/*.md`.
- Accept: a write to a spaced filename is blocked with a helpful message; a write
  outside the whitelist is blocked; templates are exempt; non-vault sessions are
  unaffected (exit 0).

**PR3a — Commit-time enforcement (Tier 1)** (D2)
- New: `.pre-commit-config.yaml` using the pre-commit framework
  (`pre-commit.com`). Hooks run `run-lint.sh` against staged `wiki/**` paths
  only (fast path), plus targeted formatters/markers if useful (trailing
  whitespace, end-of-file-fixer).
- New / changed: `CONTRIBUTING.md` adds a "Local setup" section: `pip install
  pre-commit` (or `brew install pre-commit`) → `pre-commit install`.
- Accept: a staged spaced wikilink is blocked by `git commit`; a clean staged
  set commits cleanly; the hook only re-runs on staged paths (not the whole
  vault).

**PR3b — Merge-time enforcement (Tier 2)** (D3)
- New: `.github/workflows/quality.yml` — runs on `pull_request` + `push` to
  `main`. Steps: checkout → Python setup → `make test` → `make lint --json` →
  fail-on-severity script (`error` or `warn` → exit 1, `info` → exit 0).
- New: README status badge linking to the workflow.
- Pre-flight: the plugin repo must be clean against the new severity gate
  *before* PR3b merges — any pre-existing ERROR/WARN findings need cleanup PRs
  or explicit allowlisting first, so CI starts green.
- Accept: a PR introducing a spaced wikilink fails CI (`error`); a PR
  introducing only an orphan logged as `warn` also fails CI; a PR with only
  `info` findings passes; a clean PR passes.

**PR4 — Issue-tracking workflow**
- New: two command files, `_templates/open-issues.md`, `wiki-issues` skill, a
  short doc. LIFO discipline preserved from the vault commands.
- Ship the **mechanism and the empty template**, never the reference vault's
  issue *content*.
- Accept: `/wiki:handoff` appends a well-formed stack-top issue against a clean
  baseline; `/wiki:fix-issues` pops/verifies exactly one; both refuse a dirty
  `OPEN-ISSUES.md` baseline.

**PR5 — Bulk maintenance utilities**
- New: `scripts/rewrite-wikilinks.py`, `scripts/lint-rename.py`, tests.
- `wiki-prepass.py` only after the `:28` heuristic is fixed or its limitation is
  documented in the script header.
- Accept: a TSV rewrite map renames `[[Old]]`→`[[New]]` preserving `|alias` and
  `#anchor`; a dry-run mode prints without writing.

---

## 6. Cross-cutting conventions

- **Provenance per PR.** Each PR adds a `CHANGELOG.md` entry (Keep-a-Changelog,
  the plugin's existing discipline) and a `docs/influence-log.md` line.
- **Missing CONTRIBUTING.** The plugin has no contributor guide and no documented
  commit convention. Add a minimal `CONTRIBUTING.md` (adopt Conventional Commits,
  describe `make lint`/`make test`) — folded into **PR3a** (which already needs
  a "Local setup" section for the `pre-commit install` bootstrap).
- **Versioning.** `plugin.json` + `marketplace.json` versions are hand-synced;
  bump on the PR that lands user-visible capability (PR1, PR1.5, PR2, PR3b, PR4).

---

## 7. Vault-side counterpart (must accompany each upstream)

To avoid the drift described in §2.2, each plugin PR has a vault-side follow-up:

- After **PR1**: delete the vault's forked `scripts/lint/run-lint.sh` +
  `lint-orphans.py`; replace with thin wrappers delegating to the plugin (mirror
  the existing `lint-terminology.py` wrapper pattern).
- After **PR2**: point the vault's `.claude/settings.json` `PreToolUse` at the
  plugin-shipped hook, or keep a vault wrapper that execs it.
- After **PR4**: the vault keeps only its `OPEN-ISSUES.md` *content*; the command
  definitions come from the plugin.
- After **PR5**: drop the vault's `lint-autofix.py` (superseded).

End state: **plugin = single source of truth; vault = content + thin config.**

---

## 8. Non-goals / out of scope

- Do **not** upstream `lint-autofix.py` (redundant with `rewrite-wikilinks.py`).
- Do **not** upstream the reference vault's `OPEN-ISSUES.md` content or any
  vault-specific page.
- Do **not** add a heavyweight lint framework; keep the lightweight
  shell+Python ethos the plugin already uses.
- Reverse-direction items (e.g. the vault is missing DragonScale Mechanisms 2/3
  that the plugin already ships via `bin/setup-dragonscale.sh`) are a separate
  concern, tracked vault-side, not part of this roadmap.

---

## Appendix — current-state inventory (2026-05-21)

**Plugin has (`agentic-knowledge-management` v1.6.0):**
- Hooks: `SessionStart`, `PostCompact`, `PostToolUse` (auto-commit), `Stop`.
  **No `PreToolUse`.**
- Scripts: `allocate-address.sh`, `boundary-score.py`, `lint-terminology.py`,
  `lint-title-overlap.py`, `tiling-check.py`. **No aggregating runner.**
- Tests: 5 files; `make test` runs only address/tiling/boundary (terminology +
  title-overlap tests exist but are **not wired in**).
- CI: **none** (`.github/` = `copilot-instructions.md` only).
- Commands (thin wrappers): `autoresearch`, `canvas`, `doc-pipeline`, `save`, `wiki`.
- Skills (12): incl. `wiki-lint`, `wiki-ingest`, `wiki-query`, `wiki-fold`.
- Agents (2): `wiki-ingest`, `wiki-lint`.
- Manifest: no explicit component declaration (convention-based auto-discovery).

**Vault has that the plugin lacks (upstream candidates):**
- `.claude/hooks/wiki-path-safety.sh` (PreToolUse: path whitelist + hyphen naming).
- `scripts/lint/run-lint.sh` (aggregator; now includes `spaced_wikilinks_body`).
- `scripts/lint/lint-orphans.py`, `lint-rename.py`.
- `scripts/rewrite-wikilinks.py`, `scripts/wiki-prepass.py`.
- `.claude/commands/wiki/fix-issues.md` + `handoff.md` (LIFO issue tracking).
- `wiki/meta/OPEN-ISSUES.md` format (template only).

**Already delegating (no action):**
- Vault `lint-terminology.py` + `lint-title-overlap.py` are thin wrappers over the
  plugin implementations.
