# DragonScale Memory Guide

DragonScale Memory is an optional extension for `claude-obsidian`. It adds conservative helpers for log rollups, stable page addresses, duplicate-page linting, and frontier topic suggestion. Start with [docs/install-guide.md](./install-guide.md). For the design spec and rationale, read [wiki/concepts/DragonScale Memory.md](../wiki/concepts/DragonScale%20Memory.md).

This page stays close to shipped behavior in `v1.6.0`. It explains what setup creates, what each mechanism actually does, what it needs, and how to turn it off safely without uninstalling the repo.

## What DragonScale Is

### Scope and opt-in status

DragonScale is a memory-layer extension for the wiki. It covers rollups, deterministic page IDs, duplicate detection, and one opt-in topic-selection path for `/autoresearch`. It is not required for the base vault.

If you never run `bash bin/setup-dragonscale.sh`, the base install and the original skill behavior remain in place. The repo uses feature detection so DragonScale can stay optional instead of becoming a hard dependency.

The concept page is broader than this guide. This guide is operational. When the spec and implementation differ in detail, prefer the shipped scripts and skills for day-to-day behavior.

### What ships in 1.6.0

Version `1.6.0` ships all four DragonScale mechanisms as opt-in features:

- Mechanism 1, Fold Operator: `skills/wiki-fold/`
- Mechanism 2, Deterministic Page Addresses: `scripts/allocate-address.py` plus `wiki-ingest` and `wiki-lint` integration
- Mechanism 3, Semantic Tiling Lint: `scripts/tiling-check.py` plus `wiki-lint` integration
- Mechanism 4, Boundary-First Autoresearch: `scripts/boundary-score.py` plus `skills/autoresearch/SKILL.md` Topic Selection logic

Use `CHANGELOG.md` for the release trail, [docs/install-guide.md](./install-guide.md) for the quick-start view, and [wiki/concepts/DragonScale Memory.md](../wiki/concepts/DragonScale%20Memory.md) for the full design context.

## Before You Enable It

### Base install requirements

DragonScale is an add-on, not a replacement for base setup. Do the normal vault install first by following [docs/install-guide.md](./install-guide.md).

At minimum:

- clone the repo or install the plugin
- run `bash bin/setup-vault.sh`
- open the folder as an Obsidian vault
- use `/wiki` to scaffold or continue setup

The DragonScale setup script accepts one optional argument, the vault path:

```bash
bash bin/setup-dragonscale.sh
```

```bash
bash bin/setup-dragonscale.sh /path/to/vault
```

If you omit the path, it uses the repo root inferred from `bin/`.

### Universal prerequisite: Python

Python (3.8+) is the universal prerequisite. Mechanism 2 uses it for `scripts/allocate-address.py`, and Mechanisms 3 and 4 use it for their respective helpers. File locking is handled by `scripts/_lock.py` (cross-platform, no external dependencies).

Quick check:

```bash
command -v python || command -v python3
```

If neither prints a path, install Python before relying on DragonScale.

### Mechanism 3 extra prerequisites: python3, ollama, nomic-embed-text

Mechanism 3 is the only mechanism with the full local embeddings stack. You need `python3`, `ollama`, and the `nomic-embed-text` model pulled into ollama.

Useful checks:

```bash
command -v python3
```

```bash
curl -sS http://127.0.0.1:11434/api/version
```

```bash
ollama pull nomic-embed-text
```

The setup script does not install any of those. It only checks and reports status. Mechanism 4 needs `python3`, but not ollama. Mechanisms 1 and 2 do not need either.

### What happens when optional deps are missing

DragonScale is meant to fail closed or no-op cleanly.

If `python3` is missing:

- Mechanism 3 cannot run
- Mechanism 4 cannot run
- Mechanisms 1 and 2 still work

If ollama is unreachable, `scripts/tiling-check.py` exits `10`. If ollama is reachable but `nomic-embed-text` is not installed, it exits `11`. `wiki-lint` is expected to treat those as skip conditions for semantic tiling, not as a reason to break the rest of the lint flow.

If the boundary helper fails, `/autoresearch` falls back to the normal ask-the-user topic path. It does not force a candidate list and it does not improvise a topic.

If DragonScale setup has never been run, `wiki-ingest` and `wiki-lint` keep their non-DragonScale behavior.

## Setup

### Run bin/setup-dragonscale.sh

Run:

```bash
bash bin/setup-dragonscale.sh
```

The script is idempotent. It is safe to re-run and it does not overwrite the runtime files it already created.

Before provisioning state, it verifies:

- `scripts/allocate-address.py`
- `scripts/tiling-check.py`
- `skills/wiki-fold/SKILL.md`

If any of those are missing, setup stops and tells you to reinstall the plugin.

What setup does:

- verifies `scripts/allocate-address.py` exists
- makes `scripts/tiling-check.py` executable
- creates `.vault-meta/` if needed
- creates address, tiling, and legacy-baseline state files if missing
- creates `.raw/.manifest.json` if missing
- runs sanity checks at the end

What setup does not do:

- install ollama
- pull `nomic-embed-text`
- backfill addresses onto old pages
- run a fold
- run semantic tiling
- rewrite your existing wiki pages

### What files and state it creates

Setup provisions a small amount of runtime state.

In `.vault-meta/` it creates:

- `address-counter.txt`
- `tiling-thresholds.json`
- `legacy-pages.txt`

In `.raw/` it creates:

- `.manifest.json`

`address-counter.txt` starts at `1`, so the next reserved page address in a brand-new vault will be `c-000001`.

`tiling-thresholds.json` is seeded with `error: 0.90`, `review: 0.80`, and `calibrated: false`. These are conservative seed bands, not calibrated truth for your vault.

`legacy-pages.txt` gets a rollout marker comment:

```text
# rollout: YYYY-MM-DD
```

`wiki-lint` uses that baseline to separate legacy pages from post-rollout pages for address enforcement.

`.raw/.manifest.json` starts with empty `sources` and `address_map` objects. The ingest skill maintains that file. The source documents under `.raw/` remain immutable.

### How to verify setup

The setup script already performs sanity checks, but it is useful to verify a few things yourself.

Check the next address without reserving one:

```bash
python ./scripts/allocate-address.py --peek
```

Check that runtime state exists:

```bash
ls -1 .vault-meta
```

Check tiling readiness without computing embeddings:

```bash
python3 ./scripts/tiling-check.py --peek
```

Check the boundary helper:

```bash
python3 ./scripts/boundary-score.py --top 5
```

If your vault is small or tightly integrated, the boundary helper may report no positive-score frontier pages. That is still a valid run.

## Mechanism 1: Fold Operator

### What it does

The fold operator is a log rollup. It reads the most recent `2^k` entries from `wiki/log.md` and produces an extractive fold page under `wiki/folds/`.

The fold is additive. It does not delete, move, or rewrite the child entries. The fold is extractive. Every outcome and theme in the output must be traceable to a child log entry.

The current shipped skill is intentionally narrow. It supports a flat fold over raw log entries. Hierarchical fold-of-folds behavior remains outside the scope of the current skill even though the concept spec discusses stacked folds.

The fold ID is deterministic for a given range:

```text
fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}
```

That gives structural idempotency. If the exact fold already exists, the skill should stop instead of writing a duplicate.

### When to use it

Use a fold when the log has accumulated a coherent batch of work and you want a checkpoint page that is easier to scan than a raw run of entries.

Typical cases:

- after several ingests on one theme
- after a burst of research sessions
- before a long flat `wiki/log.md` gets harder to use

Do not treat folds as garbage collection. They summarize. They do not compact by deletion.

Example command:

```text
fold the log, dry-run k=3
```

That asks for a dry-run over `2^3 = 8` entries.

### Dry-run vs commit mode

Dry-run is the default and it is stdout-only. That matters because the repo has a PostToolUse hook for writes.

In dry-run mode:

- no file is written
- no auto-commit hook is triggered
- you get the proposed fold content in the terminal output

In commit mode:

- the fold page is written to `wiki/folds/`
- `wiki/index.md` is updated
- `wiki/log.md` gets a new fold entry

The skill docs expect three separate write operations in commit mode, so three auto-commits from the hook are normal.

Example commit command:

```text
fold the log, commit k=3
```

Run a dry-run first. Commit only if the fold content looks right.

To disable Mechanism 1 without uninstalling DragonScale, stop invoking `wiki-fold`. Existing fold pages can remain in the vault, or you can remove them manually if you no longer want them.

## Mechanism 2: Deterministic Page Addresses

### Address format and rollout policy

Mechanism 2 assigns stable frontmatter addresses. The shipped format is:

```yaml
address: c-000042
```

`c-` means creation-order counter. The numeric part is zero-padded to six digits. This is not a content hash. The spec is explicit that the shipped address is deterministic and stable, but not content-addressable.

The rollout baseline is `2026-04-23`. After DragonScale adoption, post-rollout non-meta pages are expected to have addresses. Legacy pages are exempt until you do a deliberate backfill.

The helper has three real modes:

```bash
python ./scripts/allocate-address.py
```

```bash
python ./scripts/allocate-address.py --peek
```

```bash
python ./scripts/allocate-address.py --rebuild
```

The default mode reserves and prints the next address. `--peek` is read-only. `--rebuild` recomputes the counter from the highest observed `c-NNNNNN`.

Example command:

```bash
python ./scripts/allocate-address.py --peek
```

### How ingest and lint use it

`wiki-ingest` enables address assignment only when `./scripts/allocate-address.py` is present and `./.vault-meta` exists. If both conditions are true, new non-meta pages get `address:` in frontmatter. If not, ingest proceeds without addresses.

`wiki-lint` enables address validation only when `./scripts/allocate-address.py` is present and `./.vault-meta/address-counter.txt` exists. If those conditions are true, lint checks address format, uniqueness, counter consistency against `--peek`, missing addresses on post-rollout pages, and `address_map` consistency in `.raw/.manifest.json`.

The single-writer rule matters here. The allocator uses cross-platform file locking, but the ingest skill still says Phase 2 is single-writer only. Do not run parallel ingests from multiple sessions or sub-agents that assign addresses.

One hard rule from the skill docs is worth repeating. Never edit `.vault-meta/address-counter.txt` directly. Only mutate it through `scripts/allocate-address.py`.

To disable Mechanism 2 without uninstalling:

1. stop running ingests that depend on address assignment
2. remove `.vault-meta/` if you want feature detection to turn off
3. stop using `./scripts/allocate-address.py`

Existing `address:` fields can stay on pages. They become inert metadata if the feature is disabled.

## Mechanism 3: Semantic Tiling Lint

### What it checks

Mechanism 3 is an embedding-based duplicate-page detector. It scans markdown files under `wiki/` and excludes:

- `wiki/folds/`
- `wiki/meta/`
- common meta filenames such as `index.md`, `log.md`, `hot.md`, `overview.md`, `dashboard.md`, `Wiki Map.md`, and `getting-started.md`
- files with `type: meta`
- files with `type: fold`
- symlinks or paths that escape the vault root

It computes one embedding per included page, compares pairs by cosine similarity, and emits candidate overlap in bands.

Default bands:

- `>= 0.90` as error
- `0.80 - 0.90` as review
- `< 0.80` as pass

The helper never auto-merges pages. It only reports candidates for review.

Example command:

```bash
python3 ./scripts/tiling-check.py --peek
```

That gives structured diagnostics without computing embeddings.

### Local embeddings requirement

By default, the helper only trusts a local ollama endpoint at `http://127.0.0.1:11434`. Remote ollama endpoints require an explicit override flag because page bodies are sent as embedding input.

Remote override example:

```bash
python3 ./scripts/tiling-check.py --allow-remote-ollama --peek
```

The normal ready path is local:

1. `python3` is installed
2. ollama is reachable on localhost
3. `nomic-embed-text` is installed in ollama

Important exit codes:

- `0` success
- `10` ollama unreachable
- `11` model missing

`wiki-lint` is written to treat those as skip conditions.

### Calibration and no-op behavior

The shipped thresholds are conservative seeds, not calibrated truth. The skill docs call for a manual one-time calibration pass per vault. Until you do that, expect both false negatives and false positives.

The helper also has intentional no-op behavior. If ollama or the model is missing, it exits with the skip code. It does not fake results.

Useful commands:

```bash
python3 ./scripts/tiling-check.py --peek
```

```bash
python3 ./scripts/tiling-check.py --rebuild-cache
```

```bash
python3 ./scripts/tiling-check.py --report wiki/meta/tiling-report-YYYY-MM-DD.md
```

`--report` is real and path-confined to the vault. Use it when you want a saved report. Use `--peek` when you only want readiness and diagnostics.

To disable Mechanism 3 without uninstalling:

1. stop running `python3 ./scripts/tiling-check.py`
2. stop using the semantic-tiling path in `wiki-lint`
3. do not provision ollama or the model if you do not need them

Note that `.vault-meta/` is a shared gate for Mechanisms 2, 3, and 4. Do not remove it to disable Mechanism 3 alone, or you will also turn off address allocation and boundary-first autoresearch. The tiling cache lives under `.vault-meta/` but is inert when the helper is not invoked.

## Mechanism 4: Boundary-First Autoresearch

### What it does

Mechanism 4 scores frontier pages in the wiki graph. The shipped formula is:

```text
boundary_score(p) = (out_degree(p) - in_degree(p)) * recency_weight(p)
```

In practice, high-score pages point outward to many scoreable pages, receive relatively fewer inbound links, and were updated recently enough to still be frontier-like.

The helper reads `wiki/**/*.md`, builds a wikilink graph, and emits ranked results to stdout or JSON. It is intentionally stdout-only. Unlike the tiling helper, it has no `--report PATH` mode.

Example command:

```bash
python3 ./scripts/boundary-score.py --json --top 5
```

That is the exact command the autoresearch skill uses for candidate generation.

### Agenda-control caveat

This caveat is explicit in both the spec and the skill docs.

This is agenda control, not pure memory.

Mechanism 4 does not just describe the vault. It influences what the agent is likely to research next. That crosses the memory and planning boundary.

The project keeps it opt-in and labels it honestly. If you want the strict memory-layer subset only, omit this path. Do not use `/autoresearch` without a topic, or do not set up and invoke the boundary scorer.

### How /autoresearch behaves with and without it

With Mechanism 4 available, and only when `/autoresearch` is invoked without a topic, the skill:

1. checks for `scripts/boundary-score.py`
2. checks for `./.vault-meta`
3. checks for `python3`
4. runs `./scripts/boundary-score.py --json --top 5`
5. presents the top frontier pages as candidate topics
6. lets the user pick, override with free text, or decline

If the helper exits non-zero, returns invalid JSON, or returns an empty `results` array, the skill falls back.

Without Mechanism 4, or after fallback, `/autoresearch` simply asks:

```text
What topic should I research?
```

The helper suggests. The user still decides.

To disable Mechanism 4 without uninstalling:

1. stop running `python3 ./scripts/boundary-score.py`
2. use `/autoresearch [topic]` with an explicit topic
3. avoid the no-topic `/autoresearch` path if you do not want frontier suggestions

Note that `.vault-meta/` is a shared gate for Mechanisms 2, 3, and 4. Do not remove it to disable Mechanism 4 alone. The scorer itself is read-only and uses no shared state; disabling it just means not invoking it.

## Operational Policies

### Single-writer rule

DragonScale assumes a single writer for the address-assignment path. The allocator is lock-guarded, which protects the counter from simple races. It does not turn the whole wiki into a safe multi-writer system.

The ingest skill is explicit here. Do not run parallel ingests from multiple Claude sessions or sub-agents that assign addresses.

The safe operating policy is:

- one active ingest writer at a time
- one address allocator path at a time
- no direct manual edits to counter state

Mechanism 1 is human-invoked and easy to serialize. Mechanism 3 uses a lock for cache I/O. Mechanism 4 is read-only.

### Feature detection and graceful fallback

DragonScale is meant to be feature-detected, not assumed.

`wiki-ingest` only assigns addresses when the allocator is executable and `.vault-meta/` exists.
`wiki-lint` only validates addresses when the allocator exists and `.vault-meta/address-counter.txt` exists.
`wiki-lint` only runs semantic tiling when the helper exists and `python3` is available, then interprets readiness from `--peek`.
`autoresearch` only uses boundary-first selection when the helper exists, `.vault-meta/` exists, and `python3` is present.

When those conditions are not met, the repo falls back to earlier behavior. That is the intended operational posture.

## Troubleshooting

### Missing Python

Python (3.8+) is required for all DragonScale mechanisms. Check:

```bash
command -v python || command -v python3
```

If neither is available, install Python for your platform, then rerun:

```bash
bash bin/setup-dragonscale.sh
```

Do not work around this by editing `.vault-meta/address-counter.txt` directly.

### Missing ollama or model

This only blocks Mechanism 3. It does not block the rest of DragonScale.

Check ollama reachability:

```bash
curl -sS http://127.0.0.1:11434/api/version
```

Check tiling readiness:

```bash
python3 ./scripts/tiling-check.py --peek
```

If the helper exits `10`, ollama is not reachable. If it exits `11`, pull the model:

```bash
ollama pull nomic-embed-text
```

Then rerun:

```bash
python3 ./scripts/tiling-check.py --peek
```

Remember that Mechanism 4 does not need ollama. If you only want boundary-first autoresearch, `python3` is enough.

### Safe rollback / disable path

You do not need to uninstall the repo to turn DragonScale off. Use the smallest rollback that fits what you want:

- Mechanism 1: stop invoking `wiki-fold`. It uses no shared state.
- Mechanism 2: stop using `./scripts/allocate-address.py`. Existing `address:` frontmatter fields remain as plain content.
- Mechanism 3: stop running `python3 ./scripts/tiling-check.py` and stop invoking the semantic-tiling path in `wiki-lint`. Cache under `.vault-meta/` is inert when not used.
- Mechanism 4: stop running `python3 ./scripts/boundary-score.py` and avoid the no-topic `/autoresearch` path. The scorer is read-only; disabling is not invoking it.

`.vault-meta/` is a shared gate for Mechanisms 2, 3, and 4. Removing it disables all three together, not just one.

If you want to disable DragonScale feature detection across the setup-based mechanisms at once, remove `.vault-meta/`:

```bash
rm -rf .vault-meta
```

Then stop invoking the DragonScale-specific helpers and skills. This leaves your normal wiki content intact. It does not remove fold pages, and it does not strip existing `address:` fields from frontmatter. Those remain as plain content unless you choose to clean them up manually.

If you later want DragonScale back, rerun:

```bash
bash bin/setup-dragonscale.sh
```
