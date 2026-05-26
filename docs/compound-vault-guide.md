# Compound Vault — v1.7 Guide

**Status:** v1.7.0 (codename "Compound Vault refoundation"), released 2026-05-17  
**Audience:** users upgrading from v1.6, new adopters, and skill authors integrating with v1.7+ primitives  
**Companion docs:** [dragonscale-guide.md](dragonscale-guide.md) (optional Memory extension), [install-guide.md](install-guide.md), [CHANGELOG.md](../CHANGELOG.md)

---

## Why "Compound Vault"

The v1.7 line introduces a system name — **Compound Vault** — that names the architecture, distinct from the plugin name (`claude-obsidian`). The plugin name stays for SEO continuity and the existing 4.1k+ stars; the system name covers the 13 cohering skills that make the architecture work.

Three-clause positioning:

> *"Compounding vault, not chat. CLI-native, not chat-window. Methodology-aware, not generic."*

- **Compounding vault** — Karpathy's LLM Wiki pattern. Knowledge accumulates across sessions; the wiki gets richer with every ingest.
- **CLI-native** — Obsidian 1.12 made the `obsidian` binary a first-class surface. v1.7 makes it the default transport and demotes MCP to fallback.
- **Methodology-aware** — partial in v1.7 (modes ship in v1.8). The framing already shapes the v1.7 scope.

Drop-in tagline candidate (for blog/marketing):

> **"Karpathy's wiki, in your Obsidian."**

---

## What changed from v1.6 (executive summary)

v1.7 ships in four workstreams (§3.1 substrate / §3.2 transport / §3.3 retrieval / §3.4 concurrency), each one independent enough to roll back if it causes trouble. None are breaking — a v1.6 vault that does nothing on upgrade continues to behave exactly as v1.6.

| Workstream | What | Why | Adopter action |
|---|---|---|---|
| §3.1 Substrate | 3 skills upgrade soft-defer → hard-prefer for `kepano/obsidian-skills` | Stop competing with the platform owner | `claude plugin marketplace add kepano/obsidian-skills` (recommended) |
| §3.2 Transport | New `wiki-cli` skill + `detect-transport.sh` + decision tree | Obsidian 1.12 CLI is the fastest, safest write path | None — auto-detected on first session |
| §3.3 Retrieval | New `wiki-retrieve` skill + contextual prefix + BM25 + cosine rerank | Anthropic Sept 2024 research: 35-67% retrieval-failure reduction | `bash bin/setup-retrieve.sh` (opt-in) |
| §3.4 Concurrency | New `wiki-lock.sh` + 4 skill guards + hook debounce | Close the latent multi-writer corruption bug | None — universally beneficial, no setup |

---

## §3.1 Substrate dependency on kepano/obsidian-skills

**What it is:** Three claude-obsidian skills (`obsidian-markdown`, `obsidian-bases`, `canvas`) overlap with skills in `kepano/obsidian-skills` (by Steph Ango, Obsidian's CEO). In v1.6 we soft-deferred ("if kepano is installed, prefer it"). In v1.7 we hard-prefer: kepano is canonical; our copies are the floor.

**Why:** Continuing to ship parallel implementations of platform-owner primitives is a structural losing fight. The kepano marketplace has 30.5k+ stars; we have 4.1k+. Adopting kepano as substrate signals alignment and frees us to invest in the *workflow* layer (ingest, query, lint, autoresearch, save, retrieve) that no one else owns.

**What changed in the codebase:**
- `skills/obsidian-markdown/SKILL.md:11` — preface rewrites to "This skill is a self-contained fallback. Prefer `kepano/obsidian-skills`."
- `skills/obsidian-bases/SKILL.md:11` — same pattern.
- `skills/canvas/SKILL.md:14` — same pattern (json-canvas spec defers to kepano; wiki-scoped workflows stay claude-obsidian's).
- `skills/defuddle/SKILL.md:11` — documented as canonical (kepano does not ship a defuddle skill).
- `.claude-plugin/marketplace.json` — `recommendedCompanions` array names `kepano/obsidian-skills` with install hint, rationale, and repo link.

**Adopter action:** Run `claude plugin marketplace add kepano/obsidian-skills`. Existing skills keep working without it (the local fallbacks remain functional).

---

## §3.2 Default transport — Obsidian CLI with fallback chain

**What it is:** A four-tier transport stack with auto-detection. New skill `wiki-cli` documents the CLI recipes. New script `scripts/detect-transport.sh` writes `.vault-meta/transport.json` so other skills can consult it.

Fallback chain (highest to lowest precedence):
1. **cli** — `obsidian-cli` binary (Obsidian 1.12+). No MCP server, no TLS, no plugin.
2. **mcp-obsidian** — REST-API-backed MCP server (Local REST API plugin required). Auto-detection deferred to v1.7.x.
3. **mcpvault** — Filesystem-backed MCP server (BM25 search; no Obsidian plugin). Auto-detection deferred.
4. **filesystem** — Direct `Read`/`Write`/`Edit` tools. Always available; the floor.

**Why:** v1.6 documented four equal transports. Skills used direct `Read`/`Write` by default. v1.7 sharpens the recommendation and makes selection a one-line lookup against `.vault-meta/transport.json`.

**Architecture:**

```
detect-transport.sh (run at session start or vault setup)
    │
    └─ writes → .vault-meta/transport.json
                {
                  "preferred": "cli" | "filesystem",
                  "fallback_chain": [...],
                  "available": { cli: {...}, filesystem: {...}, mcp_obsidian: null, mcpvault: null }
                }

skills (wiki-ingest, wiki-query, save, autoresearch, wiki-lint):
    ├─ each has a "## Transport (v1.7+)" section near the top
    ├─ reads transport.json at runtime
    └─ uses obsidian-cli if "preferred": "cli", else Read/Write
```

**Adopter action:** None — the detection runs automatically and refreshes after 7 days. To force a refresh: `bash scripts/detect-transport.sh --force`. To manually pin to an MCP transport, edit `.vault-meta/transport.json` and set `"manual_override": true` so the detection script leaves your edit alone.

**See:** [`wiki/references/transport-fallback.md`](../wiki/references/transport-fallback.md) for the full decision tree and [`skills/wiki-cli/SKILL.md`](../skills/wiki-cli/SKILL.md) for the per-operation recipes.

---

## §3.3 Hybrid retrieval pipeline — wiki-retrieve (opt-in)

**What it is:** A new opt-in skill that replaces the v1.6 static `Read(hot.md) → Read(index.md) → Read(N pages)` query path with chunk-level retrieval using BM25 + cosine rerank over contextually-prefixed chunks. Implements Anthropic's [Sept 2024 Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) pattern as agent-skill plumbing.

**Why:** Page-level granularity loses to chunk-level granularity any time the answer lives in a specific passage. Anthropic measured a 35% retrieval-failure reduction from contextual prefixes, 49% from hybrid BM25+vector, and 67% from adding a reranker. v1.7 implements the contextual + sparse + rerank stack. (A separate dense vector stage is on the v1.7.x roadmap.)

**Architecture:**

```
INGEST (one-time + incremental):

  wiki/<page>.md
       │
       ▼
  scripts/contextual-prefix.py
       │  ├─ chunks on paragraph boundaries (~500 tokens target, 200 char overlap)
       │  └─ generates 1-2 sentence prefix per chunk
       │       tier 1: ANTHROPIC_API_KEY  → Anthropic API (Haiku, prompt-cached
       │                                    when body ≥ ~16 KB / Haiku 4.5 floor)
       │       tier 2: claude on PATH    → `claude -p` subprocess
       │       tier 3: synthetic          → frontmatter title + first paragraph
       │
       ▼  .vault-meta/chunks/<address>/chunk-NNN.json

  scripts/bm25-index.py build
       └─ inverted index over chunks' contextualized_text → .vault-meta/bm25/index.json

QUERY:

  query string
       │
       ▼
  scripts/retrieve.py "<query>" --top 5
       ├─ scripts/bm25-index.py query → top-20 candidates by BM25
       ├─ scripts/rerank.py            → cosine on nomic-embed-text via ollama
       │     (no-op if ollama unreachable; BM25 order preserved)
       └─ page-address dedupe          → final top-5 with absolute_path
       │
       ▼
  caller (wiki-query / autoresearch) reads cited pages and synthesizes
```

**Feature gating:** Other skills detect wiki-retrieve via:

```bash
[ -x scripts/retrieve.py ] && [ -d .vault-meta/chunks ] && [ -f .vault-meta/bm25/index.json ]
```

If detection fails, skills fall back to the v1.6 legacy read order. The skill never breaks the base plugin.

**Cost ceiling:** ~$12 per 1,000 documents per Anthropic's published figure (Haiku + prompt caching, tier 1). Tier 2 (claude CLI) is free in dollars but slower. Tier 3 (synthetic) is free and hermetic; loses most of the contextual benefit but BM25 + rerank still work.

**Adopter action:**

```bash
bash bin/setup-retrieve.sh         # full provisioning (auto-picks prefix tier)
bash bin/setup-retrieve.sh --no-llm  # force tier 3 (zero LLM dependency)
bash bin/setup-retrieve.sh --check   # diagnostics only; no provisioning
```

After setup, `wiki-query` standard/deep modes automatically use the new pipeline. Quick mode (hot.md only) is unchanged.

**See:** [`skills/wiki-retrieve/SKILL.md`](../skills/wiki-retrieve/SKILL.md) for the full skill spec, recipe reference, and v1.7.x roadmap (BGE cross-encoder, Cohere Rerank, separate dense vector stage).

---

## §3.4 Multi-writer safety — wiki-lock (core)

**What it is:** Per-file advisory locking via `scripts/wiki-lock.sh`. Every wiki page write MUST be preceded by `wiki-lock acquire <path>` and followed by `wiki-lock release <path>`.

**Why:** v1.6 had a latent corruption bug. `skills/wiki-ingest/SKILL.md:259-264` documented "single-writer only" as a convention, but the actual page-write paths had no enforcement. Two parallel sub-agents writing to the same wiki page could silently trample each other. The Karpathy-LLM-Wiki-Stack README explicitly warned about this. v1.7 closes the hole.

**Design (age-based, not flock-style):**

`flock(2)` advisory locks release when the holding process exits. That doesn't fit our model where `acquire` and `release` are SEPARATE bash invocations from the same skill (each Bash tool call is its own short-lived process — neither's PID survives long enough to mean anything). So `wiki-lock.sh` uses:

- **Atomic noclobber-write of a lockfile** (race-safe on POSIX filesystems).
- **Epoch-based AGE staleness**: a lock older than `STALE_AFTER_SEC` (default 60) is auto-reaped. Crashed holders unblock in ≤60s without manual intervention.
- **Cross-process release allowed**: `release` is `rm -f` (no PID match required). Skill authors are trusted to release locks they acquire. The `wiki-lock clear-stale --max-age 0` command is the canonical recovery path.
- **PID in the lockfile is informational only** (helpful for `list` and debugging).

**Skill integration:**

Four skills gained "## Concurrency (v1.7+)" sections with the recipe:

```bash
if bash scripts/wiki-lock.sh acquire wiki/concepts/Foo.md; then
  # … do the write via the §Transport-selected method …
  bash scripts/wiki-lock.sh release wiki/concepts/Foo.md
else
  # rc=75 = EX_TEMPFAIL = another writer in flight. Retry once after 2s;
  # if still held, log to wiki/log.md and skip this page.
  sleep 2
  bash scripts/wiki-lock.sh acquire wiki/concepts/Foo.md && {
    # write …
    bash scripts/wiki-lock.sh release wiki/concepts/Foo.md
  } || echo "skipped wiki/concepts/Foo.md (locked)"
fi
```

**Hook integration:** `hooks/hooks.json` PostToolUse now defers `git add` if any locks are currently held. Prevents torn commits during multi-agent ingest. Falls through gracefully when `wiki-lock.sh` is absent.

**Adopter action:** None — `wiki-lock.sh` is core in v1.7 (no opt-in). Sub-agents that don't follow the acquire/release pattern are racing against any other writer (as before — but now there's a tool to fix it).

**Test coverage:** `tests/test_wiki_lock.sh` (14 hermetic assertions) and `tests/test_concurrent_write.sh` (the critical correctness gate — 10 parallel workers, no losses, no garbled lines). `make test-concurrent` and `make test-lock`.

**See:** [`scripts/wiki-lock.sh`](../scripts/wiki-lock.sh) header comments for the full semantics, and `skills/wiki-ingest/SKILL.md` §Concurrency for the canonical integration pattern.

---

## Skill inventory (v1.7)

13 skills total. New in v1.7: `wiki-cli`, `wiki-retrieve`.

| Skill | Status | Role |
|---|---|---|
| `wiki` | core | Setup / scaffold / sub-skill router |
| `wiki-ingest` | core | Source → wiki pages with cross-refs |
| `wiki-query` | core | Question answering (now uses wiki-retrieve if installed) |
| `wiki-lint` | core | Health check (orphans, dead links, addresses, tiling) |
| `wiki-fold` | DragonScale Mech 1 | Extractive log rollups |
| `wiki-cli` | **new in v1.7 (§3.2)** | Obsidian CLI transport wrapper |
| `wiki-retrieve` | **new in v1.7 (§3.3, opt-in)** | Contextual + BM25 + rerank |
| `save` | core | File conversations as wiki notes |
| `autoresearch` | core | Iterative web research → wiki |
| `canvas` | core (defers to kepano json-canvas) | Visual wiki layer |
| `defuddle` | core (canonical) | Web page cleaner |
| `obsidian-markdown` | core (defers to kepano) | Obsidian Flavored Markdown reference |
| `obsidian-bases` | core (defers to kepano) | Bases YAML reference |

---

## Scripts inventory (v1.7)

| Script | Status | Role |
|---|---|---|
| `allocate-address.sh` | DragonScale Mech 2 | Atomic c-NNNNNN allocator (flock) |
| `tiling-check.py` | DragonScale Mech 3 | Embedding-based duplicate lint (fcntl) |
| `boundary-score.py` | DragonScale Mech 4 | Frontier scoring for autoresearch |
| `detect-transport.sh` | **new in v1.7 (§3.2)** | Transport detection → transport.json |
| `contextual-prefix.py` | **new in v1.7 (§3.3)** | Chunk + 3-tier prefix generation |
| `bm25-index.py` | **new in v1.7 (§3.3)** | Sparse inverted index (flock) |
| `rerank.py` | **new in v1.7 (§3.3)** | Cosine rerank via ollama (fcntl on cache) |
| `retrieve.py` | **new in v1.7 (§3.3)** | Hybrid retrieval orchestrator |
| `wiki-lock.sh` | **new in v1.7 (§3.4)** | Per-file advisory locks (noclobber) |

---

## Tests (v1.7)

`make test` runs 7 suites. All hermetic — zero network, zero ollama, zero LLM calls.

| Target | File | Assertions | Coverage |
|---|---|---|---|
| `make test-address` | `tests/test_allocate_address.sh` | ~10 | DragonScale Mech 2 |
| `make test-tiling` | `tests/test_tiling_check.py` | ~15 | DragonScale Mech 3 |
| `make test-boundary` | `tests/test_boundary_score.py` | ~35 | DragonScale Mech 4 |
| `make test-bm25` | `tests/test_bm25_index.py` | ~30 | tokenize, BM25 monotonicity, IDF |
| `make test-retrieve` | `tests/test_retrieve.py` | 22 | cosine, rerank, end-to-end subprocess |
| `make test-lock` | `tests/test_wiki_lock.sh` | 14 | acquire, release, age-based reap |
| `make test-concurrent` | `tests/test_concurrent_write.sh` | 6 | **the critical multi-writer correctness gate** |

The "hermetic test invariant" is preserved: nothing in `make test` requires the network, ollama, or any API key. Optional pipelines (contextual prefix with Anthropic API, rerank with ollama cosine) are tested via mocks and graceful fallbacks.

---

## What v1.7 is NOT

- Not a rewrite. DragonScale Mechanisms 1-4 are preserved and unchanged.
- Not a breaking change. v1.6 vaults that don't run setup-retrieve.sh see no behavior difference (modulo the wiki-lock integration, which is universally beneficial and adds no setup).
- Not a paid plugin. License stays MIT.
- Not a GUI Obsidian-plugin shell. Deferred to v2.5+ (the Claudian/deivid11 wrapper pattern is item #7 in the May 2026 gap-analysis backlog).
- Not multi-vault federation. Deferred to v2.x.

---

## Roadmap pointers

The May 2026 gap analysis identified 20 backlog items. v1.7 ships items 1, 2, 3, 4 (the top-quartile by value/effort) plus the latent-bug fix. Next milestones (subject to user prioritization):

- **v1.8** — Methodology modes (LYT / PARA / Zettelkasten / Generic via `wiki-mode`) + periodic reviews (`wiki-review`). Closes gaps #6 + #11.
- **v1.9** — Multimodal ingest adapters (YouTube, PDF, EPUB, image OCR via `wiki-ingest-multimodal`). Closes gaps #8 + #12.
- **v2.0** — NotebookLM-class derivative outputs (audio, quiz, flashcards, study guide via `wiki-derive`). Closes gaps #5 + #9 + #14.

Full plan: `~/.claude/plans/read-in-full-the-hidden-sun.md`.

---

## See also

- [CHANGELOG.md](../CHANGELOG.md) — v1.7.0 entry
- [docs/dragonscale-guide.md](dragonscale-guide.md) — DragonScale Memory extension (Mechanisms 1-4)
- [docs/install-guide.md](install-guide.md) — installation
- [wiki/references/transport-fallback.md](../wiki/references/transport-fallback.md) — transport decision tree
- [wiki/concepts/DragonScale Memory.md](../wiki/concepts/DragonScale%20Memory.md) — spec
- Anthropic Contextual Retrieval: https://www.anthropic.com/news/contextual-retrieval
- kepano/obsidian-skills: https://github.com/kepano/obsidian-skills
- Karpathy LLM Wiki gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
