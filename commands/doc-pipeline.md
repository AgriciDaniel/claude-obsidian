---
description: Convert source documents (.doc/.docx/.pdf/.pptx/.xlsx/...) into ingest-ready Markdown with a QC + approval gate. Reads the doc-pipeline skill.
---

Read the `doc-pipeline` skill. Then run the pipeline for the document(s) the user named (or, if none named, list the source files under `.raw/**/pre-convert/` and ask which to process).

Workflow:

1. **Stage 1 — Convert**: for each document, run
   `"$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/scripts/convert-doc.sh" "<source>"`.
   For 2+ documents, dispatch one subagent per document in parallel (Batch mode in the skill).
2. **Stage 2 — QC**: annotate each staging file in place with `<!-- REVIEW[...] -->`
   comments and the `<!-- PIPELINE-REVIEW -->` header. Annotate, never rewrite prose.
   Only flag checkworthy facts — do not web-search unless asked.
3. **Stage 3 — Gate**: present a compact per-document summary (fidelity, flag tally,
   checkworthy list, top high-severity items). Stop and let the author approve.
4. **Stage 4 — Finalize**: once the author sets `status: approved`, run
   `"$CLAUDE_PLUGIN_ROOT/skills/doc-pipeline/scripts/finalize-md.sh" <staging-file>`,
   then offer to hand the clean file to `wiki-ingest`.

If the user asks to fact-check a specific claim, follow the skill's Fact-check
protocol (web-research the flagged claim, append a verdict annotation, do not edit the claim).

Arguments (optional): a file path, a glob, or a topic filter like "GROW". Honor
`--out-dir` overrides for vaults that stage under a nested path (e.g. `.raw/training/`).
