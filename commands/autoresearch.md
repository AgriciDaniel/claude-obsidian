---
description: Run an autonomous research loop on a topic. Searches the web, synthesizes findings, and files everything into the wiki as structured pages. Use `--merge` to also integrate findings into existing entity/case/concept pages with full audit log.
---

Read the `autoresearch` skill. Then run the research loop.

Usage:
- `/autoresearch [topic]` — research a specific topic.
- `/autoresearch --merge [topic]` — research AND auto-merge findings into existing entity/case/concept pages. Writes a full audit log to `wiki/audit/`. Use this for vaults where knowledge must compound (legal, compliance, research, journalism, due-diligence).
- `/autoresearch` — if DragonScale Mechanism 4 (boundary-first, agenda-control, opt-in) is set up, offer the top 5 vault-frontier pages as topic candidates; you can **pick one**, **type a topic to override**, or **decline and be asked normally**. No automatic selection happens without user confirmation. If DragonScale is not set up OR the helper fails, the command falls back to "What topic should I research?"

DragonScale Mechanism 4 is labeled **agenda control** in the spec because it shapes what the agent researches next; it is not pure memory. The boundary score is a heuristic surfacing candidates, not an authoritative recommendation.

Before starting, read `skills/autoresearch/references/program.md` to load the research constraints and objectives.

If no vault is set up yet, say: "No wiki vault found. Run /wiki first to set one up."

After research is complete, update wiki/index.md, wiki/log.md, and wiki/hot.md.

If `--merge` flag was passed:

1. **Identify affected existing pages** — every entity page (people, organizations, properties, events), case page, and concept/claim page that the findings materially affect.

2. **Edit each affected page in-place** to integrate the new facts. Do not just add a "see also" link — write the new facts into the relevant section of the page in its existing voice and structure. Preserve a wikilink back to the canonical research page.

3. **Append `## Recent Updates` section** to each edited page (create if missing) with a single line: `- YYYY-MM-DD — [[<research-page-name>]] — <one-sentence summary of what was added>`.

4. **Write an audit log** at `wiki/audit/YYYY-MM-DD-autoresearch-<slug>.md` containing:
   - Topic researched (verbatim from user)
   - Sources fetched (URLs + brief description)
   - New page created (path)
   - All existing pages updated (path + what was merged into each)
   - Open questions surfaced
   - Confidence notes (any facts that conflict with existing vault content, any sources that were low-credibility)

Use the audit log as the canonical provenance trail — every fact merged into existing pages should be traceable back to a source listed in the log.

Report how many pages were created and what the key findings are.

If `--merge` was used, also report: how many EXISTING pages were updated (list them), and the path to the audit log.
