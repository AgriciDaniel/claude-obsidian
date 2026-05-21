---
name: doc-pipeline
description: "Convert source documents (.doc/.docx/.pdf/.pptx/.pptm/.xlsx/.html/...) into ingest-ready Markdown for the wiki vault. Stage 1 runs a deterministic raw conversion (markit + a pandoc reference). Stage 2 is a quality-control pass that annotates conversion fidelity, language, clarity, redundancy, verbosity, currency, links, source references, footnotes, tables, and Mermaid-diagram opportunities as inline <!-- REVIEW --> comments WITHOUT changing the content. Stage 3 is a human approval gate. Stage 4 strips annotations into a clean file the wiki-ingest skill can read. Checkworthy facts are only flagged; web fact-checking runs on explicit request. Triggers on: convert to markdown, doc pipeline, konvertiere für ingest, QC dieses Dokument, ingest-fertig machen, prepare documents for ingest, or when source documents are dropped into a pre-convert folder."
---

# doc-pipeline: Documents → Ingest-ready Markdown

Turns raw source documents into **ingest-ready Markdown** for the wiki, with a
human approval gate in the middle. The clean output feeds the `wiki-ingest` skill.

```
<vault>/.raw/**/pre-convert/<file>     Stage 0  source (immutable)
        │  convert-doc.sh
        ▼
<vault>/.raw/_staging/<slug>.md        Stage 1  raw markdown  + _ref/<slug>.ref.md
        │  QC pass (this skill) — annotate in place, do NOT edit content
        ▼
<vault>/.raw/_staging/<slug>.md        Stage 2  raw MD + <!-- REVIEW --> comments
        │  human reads annotations → sets status: approved        ← APPROVAL GATE
        ▼
        │  finalize-md.sh
        ▼
<vault>/.raw/<slug>.md                 Stage 4  clean, ingest-ready → wiki-ingest
```

**Core rule: QC annotates, it never rewrites.** Every concern becomes a comment;
the author decides what to act on. The Stage-4 file carries the original
information verbatim, minus conversion artifacts.

The two helper scripts live in `scripts/` next to this skill. Run the pipeline
via the `/doc-pipeline` command, which guarantees `$CLAUDE_PLUGIN_ROOT` is set:

```bash
"$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/scripts/convert-doc.sh"   # Stage 1
"$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/scripts/finalize-md.sh"   # Stage 4
```

If the skill is triggered without `$CLAUDE_PLUGIN_ROOT` set (e.g. autonomously,
not through the command), locate this skill's own directory and call the scripts
from its `scripts/` subfolder. The scripts operate on the **current vault**
(resolved via `git rev-parse`), regardless of where the plugin is installed.
Requires `markit` (`npm i -g markit-ai`); a `pandoc` reference and macOS
`textutil`/`libreoffice` pre-handling are used when available.

---

## When to use

- Source documents land in a `pre-convert/` folder under `.raw/` and need ingesting.
- The user names a document and says "convert", "QC", "prüfen", "ingest-fertig".
- A batch: "convert all of these", "process everything in pre-convert".

Single doc → run the stages inline. 2+ docs → dispatch one subagent per document
for Stage 1+2 in parallel (see Batch mode), then review and finalize.

---

## Stage 1 — Convert (deterministic, no judgement)

```bash
"$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/scripts/convert-doc.sh" "<path/to/source>"
# custom staging layout, e.g. a vault that nests under .raw/training/:
"$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/scripts/convert-doc.sh" "<src>" --out-dir .raw/training/_staging
```

- Writes `.raw/_staging/<slug>.md` (markit) and `.raw/_staging/_ref/<slug>.ref.md` (pandoc, for docx/doc/html/epub).
- Pre-handles `.doc` (textutil/libreoffice→docx), `.pptm` (→.pptx), strips dead temp image links.
- PDF/pptx/xlsx have **no pandoc reference** → QC compares the raw MD against the **original** (`Read` opens PDFs and images directly).

Do not hand-edit in this stage. If markit produced garbage, note it and stop.

---

## Stage 2 — Quality Control (annotate in place)

Read three things: the **raw MD**, the **reference** (`_ref/<slug>.ref.md` if present),
and the **original** (`Read` the source for PDFs/decks). Then write annotations
**into the raw MD file** using the schema below. **Never alter the prose itself** —
only insert HTML comments and the header block.

### 2a. Prepend the PIPELINE-REVIEW header

Insert at the very top of the staging file (HTML comment → invisible in Obsidian):

```html
<!-- PIPELINE-REVIEW
source: <relative path to original>
converter: markit <version>[ + <pre-handling, e.g. textutil .doc→.docx>]
reference: pandoc <version> | original-read (PDF/deck)
fidelity: <0.00–1.00> — <one-line justification>
counts: src≈<words> / md=<words>
status: pending-approval        # change to "approved" to unlock finalize
flags: <tally, e.g. 2×fidelity:high, 3×redundancy, 1×table, 2×fact?, 1×mermaid?>
checkworthy:                    # facts a web check could verify — see Fact-check
  - "<verbatim claim>" — <why it's checkworthy>
ingest-hints: <e.g. promote **bold** section titles to ##; PAGE footer removed>
-->
```

`fidelity` judges how completely the MD carries the original's information
(1.00 = nothing lost/distorted). Justify it from the diff/original.

### 2b. Inline annotation schema

Place each comment **immediately above or beside** the spot it refers to:

```html
<!-- REVIEW[<category>|<severity>]: <concise note, in the vault's content language> -->
```

- **severity**: `high` (blocks faithful ingest) · `med` · `low` · `info`
- **categories** (scan for every one):

| Category     | What to look for                                                            |
|--------------|-----------------------------------------------------------------------------|
| `fidelity`   | Missing/garbled/duplicated content vs. original or reference; cut-off text. |
| `structure`  | Heading hierarchy lost — e.g. `**Bold**`-only lines that should be `##`.     |
| `table`      | Tables rendered as prose/tabs; columns merged; should be a Markdown table.  |
| `language`   | Spelling, grammar, OCR typos, broken umlauts/diacritics.                     |
| `clarity`    | Convoluted sentences, undefined jargon, ambiguous phrasing.                  |
| `redundancy` | Content repeats an earlier passage. **Flag only — do not delete.**          |
| `verbosity`  | Unnecessarily long-winded explanation. **Flag only — do not tighten.**      |
| `currency`   | Possibly outdated study/year/figure/term; "new/current" claims to re-date.  |
| `link`       | Mentioned resource/URL not linked; internal reference → `[[wikilink]]`; dead link. |
| `source`     | Citation incomplete (author/year/title) or unattributed quote.              |
| `footnote`   | Footnote markers without targets — convert to MD footnotes `[^1]` … `[^1]:`.|
| `image`      | Image dropped or relevant figure missing (auto-marked by Stage 1).          |
| `mermaid?`   | A process/sequence/hierarchy in prose that a Mermaid diagram would clarify. Name the diagram type; do not insert unless asked. |
| `fact?`      | A checkworthy factual claim (statistic, attribution, date, study). Mirror into `checkworthy:`. **Do not web-search now.** |

### 2c. Annotation example

```html
<!-- REVIEW[structure|med]: '**Zielklärung**' ist Abschnittsüberschrift → beim Ingest zu '## Zielklärung' promoten -->
<!-- REVIEW[fidelity|high]: Tabelle S.2 des Originals (Phasen × Fragen) fehlt hier komplett -->
<!-- REVIEW[redundancy|low]: wiederholt die Definition aus Abschnitt 1 — nur anmerken, nicht löschen -->
<!-- REVIEW[mermaid?|info]: 4 Phasen als Ablauf — als Mermaid 'flowchart LR' darstellbar -->
<!-- REVIEW[fact?|med]: "80 % erfolgreich" — Quelle unklar, web-prüfbar -->
```

### 2d. Mermaid suggestions

When `mermaid?` applies, name the diagram type (`flowchart`, `sequenceDiagram`,
`mindmap`, `timeline`) and the nodes. **Do not insert the diagram during QC.**
Insert it only if the author says so — then add a fenced ```mermaid block and
drop the `mermaid?` comment.

---

## Stage 3 — Approval gate (human)

Present a compact summary per document: **fidelity score, flag tally, the
`checkworthy` list, and the top 3 high-severity items.** Then stop. The author:

1. reads the annotated staging file,
2. optionally requests a Mermaid insertion or a **fact-check** (see below),
3. sets `status: approved` in the PIPELINE-REVIEW header.

Never finalize a document the author has not approved.

---

## Stage 4 — Finalize (deterministic)

```bash
"$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/scripts/finalize-md.sh" .raw/_staging/<slug>.md
```

- Refuses unless `status: approved` (override `--force`).
- Strips the PIPELINE-REVIEW header and all `<!-- REVIEW -->` comments.
- Writes clean `.raw/<slug>.md`, ready for `wiki-ingest`. Leaves staging as audit trail.

Then hand off: "Run wiki-ingest on `.raw/<slug>.md`".

---

## Fact-check protocol (on request only)

Facts are **flagged, never auto-verified**. When the author points at a claim
("check the 80% figure", "verify the attribution", "fact-check doc X"):

1. Take the verbatim claim from the `checkworthy:` list.
2. Web-research it (WebSearch/WebFetch). Prefer primary/reputable sources.
3. Append the result as an annotation next to the claim — **still don't edit the claim**:

```html
<!-- REVIEW[fact?|<verdict>]: GEPRÜFT <date> — <confirmed|refuted|unclear>: <finding>. Quelle: <url> -->
```

verdict → `med` if confirmed, `high` if contradicted, `info` if inconclusive.
Correcting the text is a separate, explicit author decision.

---

## Batch mode (parallel)

For multiple documents, dispatch **one subagent per document** in a single
message. Each runs Stage 1 + Stage 2 and reports a short summary. Brief each with:
the source path, the `convert-doc.sh` call, this skill's QC checklist + schema,
"annotate in place, do not rewrite prose; do NOT web-search — only flag", and
"report under 250 words: fidelity, flags, checkworthy". Then present the combined
gate summary and finalize only what the author approves.

---

## Notes

- Annotation language follows the **vault's content language** (e.g. German).
- Do **not** add YAML frontmatter to staging/ingest-ready files — `wiki-ingest`
  owns frontmatter. The PIPELINE-REVIEW header is an HTML comment, not frontmatter.
- `.raw/_staging/` is regenerable; recommend gitignoring it.
- Privacy: if a source contains personal/sensitive data, pseudonymize per the
  vault's CLAUDE.md rules BEFORE conversion — the pipeline does not redact.
