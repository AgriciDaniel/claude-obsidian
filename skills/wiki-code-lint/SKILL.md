---
name: wiki-code-lint
description: >
  Code-fidelity health check for a Mode B code-architecture wiki — the wiki-code-* counterpart to
  the generic wiki-lint. Verifies the wiki still matches the codebase it was ingested from: code
  drift (anchored source SHAs vs HEAD), ingest staleness (how many commits behind the wiki is),
  coverage gaps (repo packages with no wiki page), and Obsidian link-resolution (every [[Title]]
  actually resolves — the alias/filename trap that silently breaks navigation). Read-only; produces
  a dated, tiered report and points each finding at its fix (/wiki-code-ingest --sync, or an alias
  backfill). Triggers on: "lint the code wiki", "is the architecture wiki still accurate", "check
  code drift", "code wiki health", "find undocumented modules", "is my code map stale", "wiki-code-lint".
allowed-tools: Read Write Edit Glob Grep Bash
---

# wiki-code-lint: Code-Fidelity Lint for Mode B Wikis

`wiki-lint` checks *vault hygiene* (orphans, dead links, frontmatter, tiling). This skill checks
something `wiki-lint` cannot: **is the code map still true to the code?** It runs four code-specific
checks against the repository the wiki was ingested from and writes a dated report whose findings map
1:1 to a remediation command.

It is the read-only **detector**; the **repair** is `/wiki-code-ingest` (`--sync` for drift/staleness,
a fresh single-path ingest for a coverage gap) or a one-line `aliases:` backfill for the link trap.

**This complements, does not replace, `wiki-lint`.** Run `wiki-lint` for generic health; run
`wiki-code-lint` for code fidelity. (`wiki-lint` keeps a shallow Code Drift pointer; this is the deep version.)

---

## Inputs

- **Vault** = the current working directory (must contain `wiki/`). If no vault: say *"No wiki vault
  found. Run /wiki first to set one up."* and stop.
- **Repo** = the code repository the wiki maps, passed as `--repo` (default `$CODE_REPO_ROOT`). The repo
  is **separate** from the vault. If the user doesn't name it, infer it from a code page's `source_paths`
  context or ask once.

Read-only throughout. Transport is irrelevant for detection (the helper scripts read `.md` directly); only
the optional alias auto-fix writes, and only after you show the report and the user approves.

---

## Locate the helper scripts (do not assume `./scripts/`)

The four checks are backed by Python helpers that ship **in this plugin**, not in the vault. A vault almost
never has a `./scripts/` dir — assuming it does is exactly why a drift check can silently no-op. Resolve the
plugin's script dir first:

```bash
# The plugin root is the dir that contains scripts/code-anchor-check.py.
PLUGIN="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN" ] || [ ! -f "$PLUGIN/scripts/code-anchor-check.py" ]; then
  # fallback: this skill is at <plugin>/skills/wiki-code-lint/SKILL.md
  PLUGIN="$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)"
fi
SCRIPTS="$PLUGIN/scripts"
VAULT="$(pwd)"
REPO="${CODE_REPO_ROOT:-<ask the user / infer from source_paths>}"
```

Every helper is invoked with **explicit** `--vault "$VAULT"` and (where relevant) `--repo "$REPO"` so it never
falls back to the plugin's own `wiki/`.

---

## The four checks (gate → peek → report)

Each check is feature-gated and emits structured exit codes; never collapse an unknown exit into "unknown".
Shared exit codes: `0` ready/finding · `2` usage · `3` wiki unreadable · `10` git missing · `11` --repo not a
git work tree. A *finding* (drift, gap, unresolved link) is **exit 0** — it is data, not an error.

Build the report incrementally: write the report header (below) first, then append each section by passing the
same `--report` path to each helper.

### 1. Code drift — `scripts/code-anchor-check.py` (reuse)
Recomputes every page's `code_anchors` SHA against HEAD; classifies **drifted / moved / untracked / malformed**.

```bash
python3 "$SCRIPTS/code-anchor-check.py" --repo "$REPO" --vault "$VAULT" --peek
case $? in
  0) python3 "$SCRIPTS/code-anchor-check.py" --repo "$REPO" --vault "$VAULT" --report "$REPORT" ;;
  10) echo "drift skipped: git not found" ;;
  11) echo "drift skipped: --repo not a git work tree" ;;
  3)  echo "drift skipped: wiki unreadable" ;;
  *)  echo "drift: unexpected exit; inspect output" ;;
esac
```
**Fix:** `/wiki-code-ingest --sync`.

### 2. Ingest staleness + 3. coverage gaps — `scripts/code-coverage-check.py` (new)
One helper, two sections. **Staleness:** per distinct `ingest_commit`, how many commits/days behind HEAD;
flags pages **missing** `ingest_commit` and commits **no longer in HEAD's history** (rebase/force-push orphans).
**Coverage gaps:** sibling packages at the *levels the wiki already documents* (parents of existing
`source_paths`) that no page maps — e.g. `app/domain/cluster_content/` when its peers all have pages. (An
ancestor-only page documenting the whole `app/domain/` does **not** count as covering a child — otherwise one
overview page hides every gap.)

```bash
python3 "$SCRIPTS/code-coverage-check.py" --repo "$REPO" --vault "$VAULT" --peek
# exit 0 → run with --report "$REPORT"; 10/11/3 → skip with the matching message
```
**Fix:** staleness → `/wiki-code-ingest --sync`; gap → `/wiki-code-ingest <repo> <missing-path>`.

### 4. Link resolution / alias convention — `scripts/wiki-link-resolve-check.py` (new)
Models Obsidian's **real** resolver (a `[[X]]` resolves to a file named `X.md` or a page aliasing `X` — **not**
to a page whose `title:` is `X`). Flags **unresolved** links, Mode B pages **unreachable by their own title**
(no filename match, no self-alias — the dominant failure when `/wiki-code-ingest` writes slug filenames without
`aliases:`), and **shadowed** titles (the title resolves to the wrong file, e.g. an empty root stub). No git needed.

```bash
python3 "$SCRIPTS/wiki-link-resolve-check.py" --vault "$VAULT" --peek   # exit 0 ready, 3 wiki unreadable
python3 "$SCRIPTS/wiki-link-resolve-check.py" --vault "$VAULT" --report "$REPORT"
```
**Fix:** add `aliases: ["<title>"]` to each flagged page (safe auto-fix — see below), and ensure
`/wiki-code-ingest` emits the alias going forward. Watch for `/` in a title — it is a path separator in a
wikilink, so a `/`-containing title can't be linked at all; rename it or use a `[[file|display]]` alias.

---

## Report

Write to `wiki/meta/code-lint-report-YYYY-MM-DD.md` (distinct prefix from `wiki-lint`'s `lint-report-` so both
coexist). Header first, then let the helpers append their four sections:

```markdown
---
type: meta
title: "Code Lint Report YYYY-MM-DD"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [meta, lint, code]
status: developing
---

# Code Lint Report: YYYY-MM-DD

Vault: `<vault>` · Repo: `<repo>` @ `<head7>` · wiki ingested at `<ingest7>`.

## Summary
- Drift: N drifted / M moved / K untracked
- Staleness: <N commits / D days> behind HEAD
- Coverage gaps: N undocumented package(s)
- Link resolution: N unresolved · M pages unreachable by title

<!-- helper sections (## Code Drift, ## Coverage & Staleness, ## Link Resolution) appended below -->
```

Tier findings **BLOCKER / HIGH / MEDIUM / LOW** in your spoken summary (not by ease of fix):
- **BLOCKER** — links unresolved en masse / pages unreachable by title (navigation broken); ingest commit orphaned.
- **HIGH** — drifted anchors on load-bearing modules; pages missing `ingest_commit`.
- **MEDIUM** — coverage gaps; wiki several commits behind.
- **LOW** — a single drifted file; one stale dependency page.

Each finding names its remediation command. The report is machine-parseable and intended to hand to
`/wiki-code-ingest --sync` (or a human) as the next step.

---

## Before auto-fixing

Always show the report first, then ask: *"Apply the safe fixes, or review each?"* (mirrors `wiki-lint`).

**Safe to auto-fix (after approval):**
- Add `aliases: ["<title>"]` to pages flagged unreachable/unresolved (the alias backfill).
- Delete empty decoy stub files that shadow a real page.

**Never auto-fix — re-ingest instead:**
- Drift / staleness → `/wiki-code-ingest --sync` (the code is the source of truth; regenerate the page, don't hand-edit drift away).
- Coverage gaps → `/wiki-code-ingest <repo> <path>` (synthesise the missing page from real signals).

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md).

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Run every check against the *actual* repo + every anchored page. The git SHA is ground truth, not the page's prose. |
| 2 | OBSERVE (int) | Am I trusting `title:` to mean a link resolves? Obsidian resolves by filename/alias — model the real resolver, not the intent. |
| 3 | LISTEN | Which repo did the user mean? Confirm `--repo` before reporting drift against the wrong tree. |
| 4 | THINK | Tier by blast radius: broken navigation > drifted load-bearing module > one stale dep. Not by ease of fix. |
| 5 | CONNECT (lat) | Drift + staleness + a coverage gap on the same package usually share a root cause: a partial or missing `--sync`. |
| 6 | CONNECT (sys) | `code-anchor-check` (drift) + `code-coverage-check` (gaps/staleness) + `wiki-link-resolve-check` (links) compose one report; the fix is always `/wiki-code-ingest`. |
| 7 | FEEL | A report that says "run `--sync`" beats a catalogue of SHAs. Make every finding actionable. |
| 8 | ACCEPT | Some uncovered packages are deliberate (trivial, vendored, planned). Flag, don't force — the human decides. |
| 9 | CREATE | `wiki/meta/code-lint-report-YYYY-MM-DD.md`, tiered, each finding → its remediation command. |
| 10 | GROW | A recurring link-resolution finding means the *ingest* is wrong: fix `/wiki-code-ingest` to emit `aliases:`, not just the pages. |
