---
name: wiki-retrieve
description: "Hybrid retrieval primitive for the Compound Vault. Replaces the v1.6 static hot→index→drill read order with contextual-prefix + BM25 + cosine-rerank, modeled on Anthropic's Sept 2024 Contextual Retrieval research (35-49-67% retrieval-failure reduction). Opt-in via `bash bin/setup-retrieve.sh`; feature-detected by wiki-query and autoresearch. Triggers on: retrieve, hybrid retrieval, BM25, rerank, contextual retrieval, search the chunks, chunk search, vault search, semantic search, what chunks match, find relevant passages."
allowed-tools: Read Bash
---

# wiki-retrieve: Hybrid Retrieval over the Vault

The v1.6 query path was `Read(hot.md) → Read(index.md) → Read(3-5 pages) → synthesize`. It worked, but page-level granularity loses to chunk-level granularity any time the answer lives in a specific passage rather than a whole page. The v1.7 `wiki-retrieve` skill is the chunk-level upgrade — opt-in, feature-gated, and replaces nothing if you don't run the setup.

**Origin**: This skill is original to claude-obsidian. There is no upstream kepano equivalent. The technique is from [Anthropic's Sept 2024 Contextual Retrieval research](https://www.anthropic.com/news/contextual-retrieval) — we implement it as agent-skill plumbing.

---

## Data privacy (v1.7.1+)

Tier 1 (Anthropic API) and tier 2 (claude CLI subprocess) of the contextual-prefix generator send **wiki page bodies off-machine**. As of v1.7.1, both tiers are GATED behind explicit user consent at two layers:

- `scripts/contextual-prefix.py --allow-egress` (default off). Without the flag, `pick_prefix_tier()` returns `"synthetic"` regardless of `ANTHROPIC_API_KEY` or `claude` binary presence.
- `bin/setup-retrieve.sh` prompts before any non-synthetic Stage 1 run; default is abort.

To run fully on-machine (tier 3 synthetic prefix + local ollama rerank), use `bash bin/setup-retrieve.sh --no-llm`. This is also the effective behavior if you decline the consent prompt or omit `--allow-egress`.

The guard mirrors `scripts/tiling-check.py:351` `--allow-remote-ollama`. v1.6 vaults that never provisioned this skill see zero behavior change.

---

## Architecture

```
INGEST (one-time, then incremental):

  wiki/<page>.md
       │
       ▼
  scripts/contextual-prefix.py
       │   ├─ chunk on paragraph boundaries (~500 token target, 200 char overlap)
       │   ├─ generate 1-2 sentence prefix per chunk
       │   │     tier 1: ANTHROPIC_API_KEY → Anthropic API (Haiku, prompt-cached)
       │   │     tier 2: `claude` on PATH  → claude -p subprocess
       │   │     tier 3: synthetic         → frontmatter title + first paragraph
       │   └─ write .vault-meta/chunks/<address>/chunk-NNN.json
       │
       ▼
  scripts/bm25-index.py build
       └─ inverted index over chunks' contextualized_text → .vault-meta/bm25/index.json

QUERY:

  query string
       │
       ▼
  scripts/retrieve.py "<query>" --top 5
       ├─ bm25-index.py query "<query>" --top 20    (sparse candidate set)
       ├─ rerank.py "<query>" --candidates -        (dense rerank via ollama cosine)
       │     cosine(query_embedding, chunk_embedding)
       │     embeddings cached in .vault-meta/embed-cache.json keyed by body_hash
       └─ dedupe by page-address, return top-N candidates with absolute_path
       │
       ▼
  caller (wiki-query / autoresearch) reads the cited pages and synthesizes
```

---

## Feature gating

Other skills must detect this skill before using it. The canonical detection:

```bash
[ -x scripts/retrieve.py ] && [ -d .vault-meta/chunks ] && \
  [ -f .vault-meta/bm25/index.json ] && \
  echo "wiki-retrieve installed" || echo "fallback: legacy hot→index→drill"
```

If detection fails, callers MUST fall back to the v1.6 read order. This skill never breaks the base plugin.

---

## Setup

```bash
bash bin/setup-retrieve.sh
```

What it does, in order:
1. Sanity-checks the 4 scripts are present and executable.
2. Creates `.vault-meta/chunks/` and `.vault-meta/bm25/`.
3. Probes ollama at `http://127.0.0.1:11434` for `nomic-embed-text` (rerank prerequisite). Reports status; does not install.
4. Reports which contextual-prefix tier will be used (Anthropic API / claude CLI / synthetic).
5. Runs `contextual-prefix.py --all` to chunk + contextualize every wiki page.
6. Runs `bm25-index.py build`.
7. Smoke-tests `retrieve.py` against the query "wiki".

Flags:
- `--check` — diagnostics only, no provisioning.
- `--no-llm` — force tier-3 synthetic prefix (cheapest, zero LLM dependency).
- `--rebuild` — re-chunk every page even if body_hash matches.

---

## Cost ceiling

Per Anthropic's published research, contextual-prefix generation costs approximately **$12 per 1,000 documents** with Haiku + prompt caching. For a 100-page vault with ~3 chunks per page, that's ~$3.60 one-time, with incremental updates much cheaper (only changed pages re-process).

If you want to validate cost before running on a large vault:

```bash
bash bin/setup-retrieve.sh --no-llm   # provision with tier-3 synthetic prefix
# inspect retrieval quality manually; if insufficient, re-run without --no-llm
```

The `claude-cli` subprocess tier (no API key) is free in $ terms but slower (~3-10s per chunk depending on Haiku availability).

---

## Skill commands (recipe)

These are the commands wiki-query and autoresearch will execute when wiki-retrieve is feature-detected. Other skills should mirror this pattern.

### Standard retrieve
```bash
python3 scripts/retrieve.py "your question here" --top 5
```
Output: JSON with `candidates` array. Each candidate has `absolute_path` to the source page; caller reads that page (using the v1.7 transport selector) and synthesizes.

### BM25-only (skip rerank)
```bash
python3 scripts/retrieve.py "query" --top 5 --no-rerank
```
Faster (no ollama call); lower quality.

### Explain mode (debugging)
```bash
python3 scripts/retrieve.py "query" --top 5 --explain
```
Adds an `explain` block with per-stage diagnostics (BM25 candidate count, dedupe size, etc.).

### Direct BM25 inspection
```bash
python3 scripts/bm25-index.py query "query" --top 10
python3 scripts/bm25-index.py stats
```

### Rerank strategy probe
```bash
python3 scripts/rerank.py "query" --peek
```
Reports which strategy will run (cosine via ollama / no-op).

---

## Integration with wiki-query

After this skill is installed, `skills/wiki-query/SKILL.md` standard and deep modes will:

1. Read `wiki/hot.md` (always — quick context).
2. Call `python3 scripts/retrieve.py "<query>" --top 5`.
3. Read the candidate pages from the result's `absolute_path` field (using the v1.7 transport selector — `obsidian-cli read` or `Read` tool).
4. Synthesize with chunk-level citation.

Quick mode is unchanged (hot.md only — never invokes retrieval).

If `retrieve.py` exits 10 (feature not provisioned), `wiki-query` falls back to the legacy v1.6 `Read(index.md) → Read(N pages)` order. No user-visible breakage.

---

## Index maintenance

The index is NOT auto-refreshed when wiki pages change. Re-run after substantive ingest sessions:

```bash
python3 scripts/contextual-prefix.py --all      # incremental: only re-processes changed pages
python3 scripts/bm25-index.py build             # always full rebuild (cheap; pure Python)
```

A future v1.7.x patch will add an opt-in PostToolUse hook that triggers contextual-prefix + BM25 rebuild after every N writes. For v1.7.0, refresh is manual.

To wipe and start over:

```bash
rm -rf .vault-meta/chunks/ .vault-meta/bm25/ .vault-meta/embed-cache.json
bash bin/setup-retrieve.sh
```

---

## Future tiers (v1.7.x roadmap)

Documented for transparency; not implemented in v1.7.0:

| Stage | v1.7.0 | v1.7.x target |
|---|---|---|
| Contextual prefix | API / claude-cli / synthetic | + Voyage embed-based pseudo-prefix |
| Sparse retrieval | BM25 | + SPLADE learned-sparse |
| Dense retrieval | (none — rerank-only) | Separate vector candidate set fused with BM25 (true hybrid) |
| Rerank | nomic cosine / no-op | + sentence-transformers BGE-base, Cohere Rerank, Voyage Rerank |
| Multi-vault | (single-vault) | Federation via wiki-federate (backlog #15) |

---

## Cross-reference

- Decision tree for transports: [`wiki/references/transport-fallback.md`](../../wiki/references/transport-fallback.md)
- Concurrency policy: [`skills/wiki-ingest/SKILL.md`](../wiki-ingest/SKILL.md) §Concurrency
- DragonScale Memory: [`wiki/concepts/DragonScale Memory.md`](../../wiki/concepts/DragonScale%20Memory.md)
- Anthropic Contextual Retrieval research: https://www.anthropic.com/news/contextual-retrieval

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read the BM25 index state + embed cache state before issuing a query. Stale caches produce wrong answers. |
| 2 | OBSERVE (int) | Am I trusting the cache when it should have been invalidated by recent ingests? Check mtime against last ingest. |
| 3 | LISTEN | The user's query — what does it actually ask? Decompose into intent and terms before matching. |
| 4 | THINK | Which retrieval strategy fits this query? BM25-only / BM25 + rerank / contextual-prefix + BM25 + rerank. |
| 5 | CONNECT (lat) | How does this hybrid compare to v1.6 baseline? +32pp top-1 / +41% error reduction is the published delta. |
| 6 | CONNECT (sys) | `--allow-egress` consent gate for Anthropic API; ollama runs local-only; rerank caches under `.vault-meta/`. |
| 7 | FEEL | When not provisioned, exit 10 with a friendly "run `bash bin/setup-retrieve.sh` first" message — not a stack trace. |
| 8 | ACCEPT | When retrieval returns empty, say so honestly. Don't fabricate. Don't pad with low-confidence guesses. |
| 9 | CREATE | A ranked candidate list with `--explain` traceability for every score component. |
| 10 | GROW | Queries that consistently fail → content gaps in the wiki. Track those as autoresearch inputs. |
