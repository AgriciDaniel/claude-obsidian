---
name: wiki-query
description: "Answer questions using the Obsidian wiki vault. Reads hot cache first, then index, then relevant pages. Synthesizes answers with citations. Files good answers back as wiki pages. Supports quick, standard, and deep modes. Triggers on: what do you know about, query:, what is, explain, summarize, find in wiki, search the wiki, based on the wiki, wiki query quick, wiki query deep."
allowed-tools: Read Glob Grep
---

# wiki-query: Query the Wiki

The wiki has already done the synthesis work. Read strategically, answer precisely, and file good answers back so the knowledge compounds.

---

## Scripts Location

`scripts/*` invocations below resolve vault-local first, falling back to the shared repo checkout via `CLAUDE_OBSIDIAN_REPO` (set once per machine, e.g. `P:\source\llm\projects\claude-obsidian`):

```bash
SCRIPTS="scripts"; [ -d "$SCRIPTS" ] || SCRIPTS="${CLAUDE_OBSIDIAN_REPO:?CLAUDE_OBSIDIAN_REPO not set — point it at your claude-obsidian checkout}/scripts"
```

Use `$SCRIPTS/<name>` wherever this doc shows `scripts/<name>`.

---

## Transport (v1.7+)

Reads should prefer the same transport the rest of the plugin uses. Consult `.vault-meta/transport.json` (auto-created by `bash $SCRIPTS/detect-transport.sh`) and use the `preferred` entry:

- **cli** — `obsidian-cli read "$VAULT" "$NOTE"` and `obsidian-cli search "$VAULT" "<query>"` (Obsidian-native ranking); see [`skills/wiki-cli/SKILL.md`](../wiki-cli/SKILL.md)
- **mcp-obsidian** / **mcpvault** — `mcp__obsidian-vault__read_note`, `search_notes`; see [`skills/wiki/references/mcp-setup.md`](../wiki/references/mcp-setup.md)
- **filesystem** — Claude's `Read` and `Glob`/`Grep` tools (final floor; always works)

Full decision tree: [`wiki/references/transport-fallback.md`](../../wiki/references/transport-fallback.md). Quick mode (hot.md only) is transport-agnostic — always uses `Read`.

---

## Retrieval (v1.7+)

If `wiki-retrieve` is feature-detected — `[ -x "$SCRIPTS/retrieve.py" ] && [ -d .vault-meta/chunks ] && [ -f .vault-meta/bm25/index.json ]` — Standard and Deep modes consult it BEFORE the legacy hot→index→drill chain:

```bash
uv run $SCRIPTS/retrieve.py "<the user's question verbatim>" --top 5
```

Output is JSON with a `candidates` array. Each candidate has `absolute_path` to the source page, a `snippet`, and `bm25_score` + `rerank_score`. Read the cited pages (using the transport selector from §Transport above) and synthesize with chunk-level citation.

If `retrieve.py` exits 10 (feature not provisioned), or any step in the pipeline errors, fall back to the v1.6 legacy read order described in the Standard/Deep workflows below — no user-visible breakage.

Quick mode always skips retrieval (hot.md only — keeps the ~1,500 token budget intact).

Full spec: [`skills/wiki-retrieve/SKILL.md`](../wiki-retrieve/SKILL.md). Setup: `bash bin/setup-retrieve.sh`. The legacy read-order workflows below remain authoritative when wiki-retrieve is not installed.

---

## Query Modes

Three depths. Choose based on the question complexity.

| Mode | Trigger | Reads | Token cost | Best for |
|------|---------|-------|------------|---------|
| **Quick** | `query quick: ...` or simple factual Q | hot.md + index.md only | ~1,500 | "What is X?", date lookups, quick facts |
| **Standard** | default (no flag) | hot.md + index + 3-5 pages | ~3,000 | Most questions |
| **Deep** | `query deep: ...` or "thorough", "comprehensive" | Full wiki + optional web | ~8,000+ | "Compare A vs B across everything", synthesis, gap analysis |

---

## Quick Mode

Use when the answer is likely in the hot cache or index summary.

1. Read `wiki/hot.md`. If it answers the question, respond immediately.
2. If not, read `wiki/index.md`. Scan descriptions for the answer.
3. If found in index summary, respond and do not open any pages.
4. If not found, say "Not in quick cache. Run as standard query?"

Do not open individual wiki pages in quick mode.

---

## Standard Query Workflow

1. **Read** `wiki/hot.md` first. It may already have the answer or directly relevant context.
2. **Read** `wiki/index.md` to find the most relevant pages (scan for titles and descriptions).
3. **Read** those pages. Follow wikilinks to depth-2 for key entities. No deeper.
4. **Synthesize** the answer in chat. Cite sources with wikilinks: `(Source: [[Page Name]])`.
5. **Offer to file** the answer: "This analysis seems worth keeping. Should I save it as `wiki/questions/answer-name.md`?"
6. If the question reveals a **gap**: say "I don't have enough on X. Want to find a source?"

---

## Deep Mode

Use for synthesis questions, comparisons, or "tell me everything about X."

1. Read `wiki/hot.md` and `wiki/index.md`.
2. Identify all relevant sections (concepts, entities, sources, comparisons).
3. Read every relevant page. No skipping.
4. If wiki coverage is thin, ask: "Quick web search to fill the gap (filed into the wiki), or `/autoresearch` to dig deep (also filed)?" Don't pick for the user.
5. Synthesize a comprehensive answer with full citations.
6. Always file the result back as a wiki page. Deep answers are too valuable to lose.

---

## Token Discipline

Read the minimum needed:

| Start with | Cost (approx) | When to stop |
|------------|---------------|--------------|
| hot.md | ~500 tokens | If it has the answer |
| index.md | ~1000 tokens | If you can identify 3-5 relevant pages |
| 3-5 wiki pages | ~300 tokens each | Usually sufficient |
| 10+ wiki pages | expensive | Only for synthesis across the entire wiki |

If hot.md has the answer, respond without reading further.

---

## Index Format Reference

The master index (`wiki/index.md`) looks like:

```markdown
## Entities
- [[Entity Name]]: role (first: [[Source]])

## Concepts
- [[Concept Name]]: definition (status: developing)

## Sources
- [[Source Title]]: author, date, type

## Questions
- [[Question Title]]: answer summary
```

Scan the section headers first to determine which sections to read.

---

## Type Sub-Index Format

Each type folder has a `_index.md` for focused lookups:

```markdown
---
type: meta
title: "Entities Index"
updated: YYYY-MM-DD
---
# Entities

## People
- [[Person Name]]: role, org

## Organizations
- [[Org Name]]: what they do

## Products
- [[Product Name]]: category
```

Use sub-indexes when the question is scoped to one type folder. Avoid reading the full master index for narrow queries.

---

## Filing Answers Back

Good answers compound into the wiki. Don't let insights disappear into chat history.

When filing an answer:

```yaml
---
type: question
title: "Short descriptive title"
question: "The exact query as asked."
answer_quality: solid
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [question, <domain>]
related:
  - "[[Page referenced in answer]]"
sources:
  - "[[wiki/sources/relevant-source.md]]"
status: developing
---
```

Then write the answer as the page body. Include citations. Link every mentioned concept or entity.

After filing, add an entry to `wiki/index.md` under Questions and append to `wiki/log.md`.

---

## Gap Handling

If the question cannot be answered from the wiki, always fall back to web research — but always ask which mode first:

1. Say clearly: "I don't have enough in the wiki to answer this well."
2. Identify the specific gap: "I have nothing on [subtopic]."
3. Ask: "Want me to look this up? Quick web search now (I'll file the answer into the wiki as a `question` page), or `/autoresearch` for a deep multi-source dive that gets filed too?"
4. Both paths file into the wiki — quick search files a single `question` page via the standard Filing Answers Back format; `/autoresearch` files its own structured pages via its own loop. Neither path is "unfiled." Only the depth differs.
5. Do not fabricate. Do not answer from training data if the question is about the specific domain in this wiki. Do not silently pick a research mode — wait for the user's choice.

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read `wiki/hot.md` first, then `wiki/index.md`, then specific pages. Don't skip the cache. |
| 2 | OBSERVE (int) | Am I synthesizing from training-data memory when I should be citing wiki pages? Check the source of each claim. |
| 3 | LISTEN | What is the user's REAL question? The surface query is often a proxy for a deeper need. |
| 4 | THINK | Quick / standard / deep mode? Match depth to question complexity, not eagerness. |
| 5 | CONNECT (lat) | Are there pages I missed that would CHANGE the answer? Cross-check related pages before answering. |
| 6 | CONNECT (sys) | Hot cache + index + wiki-retrieve (when provisioned) layer into a single retrieval pipeline. |
| 7 | FEEL | Cite specific pages, not vague references. Future-me wants traceability back to the source page. |
| 8 | ACCEPT | When the wiki doesn't have the answer, say so explicitly. Don't fabricate from training data. |
| 9 | CREATE | The answer with citations + an offer to file the answer if it's worth keeping. |
| 10 | GROW | Questions the wiki can't answer are content gaps — log them as autoresearch inputs. |
