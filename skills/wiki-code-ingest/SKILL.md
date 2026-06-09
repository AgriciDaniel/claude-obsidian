---
name: wiki-code-ingest
description: "Ingest a code repository (or sub-path) into the Obsidian wiki as a Mode B architecture map. Walks the repo honoring .gitignore, gathers deterministic signals (file tree, language/LOC, dependency manifests, git anchors, import edges), then synthesizes modules/components/flows/dependencies/decisions pages with drift anchors. Human-in-loop. Supports whole-repo bootstrap, single-path ingest, and --sync re-ingest. Triggers on: map my codebase, ingest this repo, architecture wiki for my repo, understand this project, ingest this module, document this service, code ingest, sync the wiki with the code."
allowed-tools: Read Write Edit Glob Grep Bash
---

# wiki-code-ingest: Codebase → Mode B Architecture Wiki

Turn a code repository into a navigable Obsidian wiki of **modules, components, flows, dependencies, and decisions**. The hard signals are gathered deterministically by three helper scripts; you (the LLM) do the synthesis — naming modules, writing purposes, drawing the architecture. A whole-repo bootstrap typically creates 1 page per major package plus the five key overview pages.

**This is the automation Mode B always implied** (`skills/wiki/references/modes.md` §Mode B) but never had: until now Mode B was a folder template filled in by hand.

**Syntax standard**: Obsidian Flavored Markdown — wikilinks `[[Note Name]]`, callouts `> [!type] Title`, YAML frontmatter properties.

---

## Gitignore guarantee (non-negotiable)

The wiki indexes **only files git would track or show as untracked-not-ignored**. All three signal scripts enumerate via `git ls-files --cached --others --exclude-standard`, so anything in `.gitignore` / `.git/info/exclude` / the global excludes (build output, `node_modules`, secrets, vendored deps) is **never** read or indexed. Do not work around this by reading ignored paths directly.

---

## Transport, concurrency, addresses — shared mechanics

These work exactly as in `skills/wiki-ingest/SKILL.md`; follow those sections, they are not duplicated here:

- **Transport** — consult `.vault-meta/transport.json`; write via cli → mcp → filesystem (`skills/wiki-cli/SKILL.md`).
- **Concurrency** — every `wiki/` page write MUST be preceded by `bash scripts/wiki-lock.sh acquire <path>` and followed by `release`. Per-file locks make multi-writer safe (`skills/wiki-ingest/SKILL.md` §Concurrency).
- **Address Assignment** — if `[ -x ./scripts/allocate-address.sh ] && [ -d ./.vault-meta ]`, every new non-meta page gets `address: c-NNNNNN` and the `.raw/.manifest.json` `address_map` is updated (`skills/wiki-ingest/SKILL.md` §Address Assignment). Module/component/dependency/flow/decision pages are non-meta → they get addresses. The overview pages `[[Architecture Overview]]`/`[[Dependency Graph]]` are non-meta too.

---

## Inputs and modes

The user points at a repo. The repo is **separate from the vault** — pass its path explicitly; the vault is the current working directory.

| Trigger | Mode |
|---|---|
| "map my codebase", "ingest this repo", "architecture wiki" | **Whole-repo bootstrap** |
| "ingest app/workers/crawler", "document this module" | **Single-path ingest** (`--subpath`) |
| "sync the wiki with the code", invoked by the auto-sync hook | **`--sync`** (re-ingest only changed paths) |

---

## Step 1 — Run the signal scripts (deterministic, cheap)

Pick a slug for the repo and run all three into `.raw/code/<slug>/`:

```bash
REPO="/abs/path/to/repo"          # the code repo (NOT the vault)
SLUG=$(basename "$REPO")
OUT=".raw/code/$SLUG"
python3 scripts/code-scan.py      "$REPO" --out "$OUT"     # tree.json, languages.json
python3 scripts/code-manifests.py "$REPO" --out "$OUT"     # deps.json
python3 scripts/code-signals.py   "$REPO" --out "$OUT"     # git.json (anchors!), edges.json
```

For a single-path ingest add `--subpath app/workers/crawler` to each. These five JSON files under `.raw/code/<slug>/` are your source of truth — read them, do not re-walk the repo yourself.

> The `.raw/code/<slug>/` artifacts are the code-ingest equivalent of `wiki-ingest`'s `.raw/articles/*.md` fetch artifacts — generated, not user-dropped, so writing them does not violate the "`.raw/` is immutable" rule (which governs user source files).

---

## Step 2 — Whole-repo bootstrap flow

1. **CHECKPOINT 1 (scope).** Read `languages.json` + the top of `tree.json`. Confirm with the user: *"This is a {primary}-primary repo, {N} files. Map the whole repo, or a sub-path? One page per top-level package, or finer?"* Skip only if the user said "just do it."
2. **Read context, avoid dupes.** Read `wiki/hot.md` (recent context) and `wiki/index.md` (existing pages — do not recreate).
3. **Derive the module set** from `tree.json.dirs` — major packages/services (top-level dirs under the scope, plus any dir with many files). 
4. **CHECKPOINT 2 (module list).** Present the proposed modules: *"I'll create pages for: [[Module A]], [[Module B]], … Merge any? Skip any? Rename?"* Let the user adjust.
5. **Per approved module**, route the path and synthesize the page:
   ```bash
   P=$(python3 scripts/wiki-mode.py route module "Crawler Worker")   # → wiki/modules/Crawler-Worker.md (generic)
   bash scripts/wiki-lock.sh acquire "$P" && { : write page ; bash scripts/wiki-lock.sh release "$P"; }
   ```
   Read **3-5 of the module's real top files** (via `tree.json`) for the body — do not read the whole module. Body covers: purpose, key files, public surface, and dependencies as `[[wikilinks]]` derived from `edges.json` (intra-repo edges where `external:false`). Add a `> [!gap]` callout where `edges.json` was ambiguous (regex edges are best-effort).
   Write the frontmatter using the **Mode B code-page schema** (`skills/wiki/references/frontmatter.md` → "module / component / …"), including the **drift anchors** (Step 3) and an **`aliases:` entry equal to the page title** — the router writes a dashed/slug filename (`wiki/modules/Crawler-Worker.md`), so without the alias `[[Crawler Worker]]` does not resolve and every inbound link to the page breaks. `/wiki-code-lint` flags this; emit the alias here so it never fires.
6. **Dependencies** — from `deps.json`, synthesize `wiki/dependencies/` pages (one per ecosystem, or per significant external dep): `type: dependency`, version, a one-line risk/role note.
7. **Flows** — from `edges.json` adjacency, trace notable request/data paths (entrypoint → service → worker). `edges.json` is the scaffold; you draw the real flow. `type: flow`.
8. **Key overview pages** (the Mode B set): `[[Architecture Overview]]`, `[[Data Flow]]`, `[[Tech Stack]]`, `[[Dependency Graph]]`, `[[Key Decisions]]`.
9. **Decisions** — create `wiki/decisions/` ADRs only if the repo has an `adr/` or `docs/decisions/` dir, or the user points at decisions; otherwise leave `[[Key Decisions]]` as a stub.
10. **Update meta** — `wiki/index.md` (add new pages), `wiki/hot.md` (overwrite with this ingest's context), and **prepend** to `wiki/log.md`:
    ```markdown
    ## [YYYY-MM-DD] code-ingest | <repo or repo/subpath>
    - Signals: `.raw/code/<slug>/` (HEAD <sha7>)
    - Modules created: [[Module A]], [[Module B]]
    - Pages updated: [[Architecture Overview]], [[Dependency Graph]]
    - Key insight: <one sentence>
    ```

**Single-path ingest** is the same flow with `--subpath`, but the module set is just that path's children and you do **not** regenerate the whole-repo overview pages — only PATCH them.

---

## Step 3 — Drift anchors (what makes re-sync possible)

Every code page records where in the repo it came from and the git content hash at ingest time, so `wiki-lint` can later detect when the code has drifted from the page. Pull anchors straight from `git.json.anchors` (a map of every tracked path → its blob/tree SHA):

```yaml
type: module
title: "Crawler Worker"
aliases:                       # MUST equal the page title — Obsidian resolves [[Crawler Worker]] by
  - "Crawler Worker"           #   filename/alias, not by `title:`. The router writes a dashed/slug
                               #   filename, so omitting this breaks every inbound link to this page.
source_type: code
status: active
language: python
purpose: "Crawls a registered domain and emits domain.crawled."
source_paths:
  - "app/workers/crawler/"
code_anchors:                 # flat "path@sha" list — split on the LAST @
  - "app/workers/crawler/@<git.json anchors['app/workers/crawler/']>"
ingest_commit: "<git.json head>"
ingested_at: <today>
depends_on:
  - "[[Domain Layer]]"
used_by:
  - "[[API Layer]]"
```

For a directory `source_path`, the anchor is the **tree** SHA; for a single file, the **blob** SHA. `git.json.anchors` already holds whichever is correct — just look it up. If a chosen `source_path` is not in `anchors` (untracked/uncommitted), omit it from `code_anchors` rather than inventing a hash.

---

## Step 4 — `--sync` mode (re-ingest changed paths)

Invoked manually ("sync the wiki with the code") or surfaced by the auto-sync hook (`scripts/code-sync-check.py` reads `.vault-meta/code-sync-queue.jsonl`). 

1. Read the pending entries in `.vault-meta/code-sync-queue.jsonl` (each has `repo`, `commit`, `changed_paths`).
2. Re-run the three signal scripts (whole repo, or `--subpath` per changed area).
3. For each wiki code page whose `source_paths` intersect the changed paths: PATCH the page body where the code changed and **refresh** its `code_anchors` + `ingest_commit` from the fresh `git.json`. Do **not** regenerate untouched pages or the overview pages (PATCH only).
4. Mark the drained queue entries `synced` and bump `last_synced_commit` in `.vault-meta/code-sync-state.json` (see `bin/setup-code-watch.sh`).
5. Prepend a `code-ingest | sync` entry to `wiki/log.md`.

---

## Parallelism (many modules)

For a repo with many modules, dispatch the `wiki-code-ingest` sub-agent (`agents/wiki-code-ingest.md`) **one per module**. The orchestrator (this skill) runs the three signal scripts **once**, then hands each sub-agent its module path plus the relevant slices of `tree.json`/`edges.json`/`git.json`. Sub-agent invariants (same as `agents/wiki-ingest.md`): acquire the page lock before writing; do **not** touch `index.md`/`log.md`/`hot.md`; do **not** call `allocate-address.sh` (the orchestrator backfills addresses single-writer). Cross-module work — `flows/`, `[[Dependency Graph]]`, reverse `used_by` edges — runs in the orchestrator after the fan-out, because it needs the whole `edges.json`.

---

## What not to do

- Do not index gitignored files (the scripts already exclude them — never bypass).
- Do not read whole modules; read 3-5 representative files per page (`tree.json` tells you which).
- Do not invent `depends_on` edges — derive them from `edges.json`; flag ambiguity with `> [!gap]`.
- Do not regenerate overview/untouched pages in single-path or `--sync` mode — PATCH.
- Do not skip the drift anchors — without them `wiki-lint` cannot detect drift and `--sync` cannot target pages.
- Do not omit the `aliases:` title-entry — without it (or a Title-matching filename) `[[Title]]` links do not resolve in Obsidian, and `/wiki-code-lint`'s link check flags every such page.

---

## How to think (10-principle mapping)

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | The signal JSONs first; real files second (3-5 per page). Never guess structure the scripts already measured. |
| 2 | OBSERVE (int) | Am I imposing an architecture the code doesn't have? Let `tree.json`/`edges.json` correct me. |
| 3 | LISTEN | What does the user want mapped — the whole system, or one service? Checkpoint before mass page creation. |
| 4 | THINK | Which dirs are real modules vs incidental? Which edges are load-bearing vs noise? |
| 5 | CONNECT (lat) | Modules ↔ modules via `edges.json`; pages ↔ deps via `deps.json`. |
| 6 | CONNECT (sys) | `code-*.py` for signals + `wiki-mode.py route` for paths + `wiki-lock.sh` for safety + anchors for drift. |
| 7 | FEEL | A page that stays true as the code moves — anchored, re-syncable, not a one-time snapshot. |
| 8 | ACCEPT | Regex import edges are best-effort. Mark uncertainty with `> [!gap]`; don't fake precision. |
| 9 | CREATE | Module/flow/dependency/decision pages with drift anchors + cross-links. |
| 10 | GROW | Each `--sync` keeps the map honest. Drift surfaced by `wiki-lint` is the signal to re-ingest. |
