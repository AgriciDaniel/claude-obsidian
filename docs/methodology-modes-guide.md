# Methodology Modes Guide — v1.8.0

**Status:** v1.8.0 GA (2026-05-17)
**Scope:** picks an organizational style for your vault and routes new pages accordingly.
**Origin:** closes priority gap 5 from the May 2026 compass artifact.

---

## TL;DR

Pick a mode that matches how YOU think:

| You think in... | Pick |
|---|---|
| Topic clusters + navigation by following links | **LYT** |
| Active projects vs ongoing responsibilities vs reference material | **PARA** |
| Atomic claims with unique IDs and dense linking | **Zettelkasten** |
| No methodology / want v1.7 default | **Generic** |

```bash
bash bin/setup-mode.sh           # interactive
bash bin/setup-mode.sh --mode lyt   # non-interactive
```

After picking, `wiki-ingest`, `save`, and `autoresearch` consult the mode before deciding where to file new pages. Existing files are NOT moved; the mode only affects future filing.

---

## Why methodology modes exist

The May 2026 compass artifact identified 5 priority gaps. claude-obsidian v1.7 closed 4 of them (substrate alignment, default transport, hybrid retrieval, multi-writer safety) and deferred the 5th — methodology support — to v1.8.

The audit §9 axis evaluation called methodology support a **TIE** in May 2026: nobody else in the Claude+Obsidian space ships it as a first-class skill. Ideaverse Pro 2.0 ($200 paid vault) ships LYT as an opinionated structure but it's a vault, not a skill set. PARA, Zettelkasten, and mode-aware routing are entirely unserved.

v1.8.0 closes that gap. After this release, claude-obsidian is **#1 on 5 of 7 axes** per the compass framework (compounding wiki, multi-writer safety, retrieval architecture, license openness, methodology support). The remaining 2 (GUI ergonomics, derivative outputs) require larger releases (v2.5+ for GUI, v2.0 for derive).

---

## The four modes

### Generic (default)

**Philosophy:** no methodology imposed. Same as v1.6/v1.7.

**Filing convention:**
- `wiki/sources/<slug>.md` — ingested source documents
- `wiki/entities/<Name>.md` — people, orgs, products (capitalization preserved)
- `wiki/concepts/<Name>.md` — concepts and frameworks
- `wiki/sessions/<date>-<topic>.md` — session notes from `/save`

**When to use:**
- You're migrating from v1.7 and want zero behavior change
- You don't want to commit to a methodology yet
- You have your own organizational instincts and want minimal opinion

**Pros:** zero learning curve; matches v1.7 muscle memory; flexible.
**Cons:** no opinion to lean on; can sprawl in large vaults.

---

### LYT (Linking Your Thinking — Nick Milo)

**Philosophy:** the organizational primitive is the **MOC** (Map of Content). Atomic notes flat under one folder; MOCs link into clusters of notes. You navigate by following links, not by browsing folders.

**Filing convention:**
- `wiki/mocs/<topic>-moc.md` — Map of Content for a topic cluster
- `wiki/notes/<atomic-note>.md` — all atomic notes flat (no subfolders)
- Every atomic note has at least one MOC in its frontmatter `mocs:` field
- New ingests land in `wiki/notes/`; consumer skill also updates the relevant MOC

**Templates** (under `skills/wiki-mode/templates/lyt/`):
- `moc-template.md` — MOC scaffolding with core-notes / adjacent-MOCs / open-questions sections
- `atomic-template.md` — atomic note with MOC backlinks

**When to use:**
- Mid-to-large knowledge bases (>100 notes)
- You think in conceptual clusters and knowledge graphs
- You're an LYT practitioner or want to be one

**Pros:** scales beautifully; navigation gets richer with growth; explicit knowledge structure.
**Cons:** discipline of always-update-MOCs; flat notes folder can feel chaotic without good search.

---

### PARA (Tiago Forte)

**Philosophy:** organize by **actionability**, not topic. Active work in Projects (with deadline + outcome), ongoing responsibilities in Areas (no deadline), reference material in Resources (by topic), completed/inactive work in Archives.

**Filing convention:**
- `wiki/projects/<project-name>/<note>.md` — active projects
- `wiki/projects/inbox/<note>.md` — new ingests + session notes land here for triage
- `wiki/areas/<area-name>/<note>.md` — ongoing responsibilities
- `wiki/resources/<topic>/<note>.md` — reference material
- `wiki/resources/incoming/<note>.md` — new sources land here for topical sorting
- `wiki/resources/people/<Name>.md` — entity pages
- `wiki/resources/concepts/<Name>.md` — concept pages
- `wiki/archives/<year>/<note>.md` — completed projects, sunsetted areas

**Templates** (under `skills/wiki-mode/templates/para/`):
- `project-template.md` — project with status / deadline / outcome / next-action
- `area-template.md` — area with scope / standards / review cadence
- `resource-template.md` — reference material with topic + sources

**When to use:**
- Workflow-heavy users
- Knowledge workers managing many projects
- GTD-adjacent practitioners
- Anyone who has read Tiago Forte's "Building a Second Brain"

**Pros:** explicit project lifecycle; clear separation of active vs reference; matches how knowledge workers actually operate.
**Cons:** requires periodic review to move completed projects → archives; "incoming" buckets need to be processed.

---

### Zettelkasten (Niklas Luhmann's slip-box)

**Philosophy:** atomic notes, unique IDs, dense bidirectional linking. No folders. Every note answers exactly one idea. Notes find each other by ID references.

**Filing convention:**
- `wiki/<YYYYMMDDHHMMSSffffff>-<slug>.md` — flat under wiki/, timestamped IDs (20 digits = date + microseconds, collision-resistant)
- Every note has `id:`, `parent_id:` (optional), `child_ids:` (optional) in frontmatter
- No subdirectories; the wiki/ root is the whole vault
- All organization is via `parent_id` / `child_ids` / `[[ID]]` references in note bodies

**Templates** (under `skills/wiki-mode/templates/zettel/`):
- `atomic-template.md` — atomic claim with parent/child IDs + reasoning + sources

**When to use:**
- Academics and researchers
- Long-term thinkers building permanent knowledge artifacts
- Anyone who's read "How to Take Smart Notes" by Sönke Ahrens
- High-discipline, small-filing-surface preference

**Pros:** maximum link density; encourages atomic thinking; ages well over decades.
**Cons:** steepest discipline curve; flat file list is intimidating without good search; ID-based reference is less mnemonic than name-based.

---

## How modes interact with other skills

The integration is **automatic** — once you set a mode, `wiki-ingest`, `save`, and `autoresearch` consult it on every new page. You never have to think about it.

| Skill | What it does | How mode affects it |
|---|---|---|
| `wiki-ingest` | files new source/entity/concept pages | router determines destination folder per mode |
| `save` | files session notes from the current conversation | router determines `wiki/sessions/` (generic), `wiki/notes/` + MOC update (LYT), `wiki/projects/inbox/` (PARA), or `wiki/<ID>-session-...` (Zettel) |
| `autoresearch` | files synthesis page after a research loop | router determines `wiki/concepts/` (generic), `wiki/notes/` + topic MOC (LYT), `wiki/resources/<topic>/` (PARA), or `wiki/<ID>-...` (Zettel) |

The router (`scripts/wiki-mode.py route <type> "<name>"`) is the single source of truth. Skills don't compute paths themselves; they call the router and use what it returns.

---

## Switching modes later

Switching modes is **safe but does NOT auto-migrate**:

1. Run `bash bin/setup-mode.sh` (or `--mode <new-mode>` non-interactively)
2. The new mode is written to `.vault-meta/mode.json`
3. Existing files remain in their original locations and continue to work
4. New files file per the new mode
5. (Optional manual step) Use your file manager or `git mv` to migrate existing files to the new structure

**Why no auto-migration:** the wiki contains your thinking. Auto-rewriting paths could break wikilinks, lose data, or surprise you. Manual migration forces explicit decisions about what fits the new methodology vs what stays in its current home.

**Specifically for LYT migration:** after switching to LYT, run `lint the wiki` (skill: wiki-lint) to identify orphan pages that would benefit from MOC inclusion.

---

## Mode config file

`.vault-meta/mode.json` is the active mode declaration. It's **gitignored by default** — the file is treated as host-specific runtime config. To commit your mode choice across machines / collaborators:

```bash
git add -f .vault-meta/mode.json
git commit -m "chore: declare vault mode as <mode>"
```

The file schema:

```json
{
  "schema_version": 1,
  "mode": "lyt|para|zettelkasten|generic",
  "configured_at": "2026-05-17T00:00:00Z",
  "config": {
    "lyt": {"moc_folder": "wiki/mocs/", "notes_folder": "wiki/notes/"},
    "para": {"projects_folder": "...", "areas_folder": "...", "resources_folder": "...", "archives_folder": "..."},
    "zettelkasten": {"id_format": "YYYYMMDDHHMMSSffffff", "no_folders": true, "root_folder": "wiki/"},
    "generic": {"sources_folder": "wiki/sources/", "entities_folder": "wiki/entities/", "concepts_folder": "wiki/concepts/", "sessions_folder": "wiki/sessions/"}
  }
}
```

The `config` block always includes all 4 modes. The active mode is named by `mode`. Per-mode folder paths can be overridden in your `mode.json` if you want non-default conventions.

---

## When NOT to use mode-awareness

- **Tiny vaults** (<20 notes): the overhead of organization isn't justified yet. Stick with generic.
- **Vaults you didn't choose to organize**: if you don't care about methodology, don't pick one. Generic is honest.
- **Cross-project shared vaults** (per global CLAUDE.md `/save` convention): the personal vault at `~/Documents/Obsidian Vault/` has its own organizational choices; the project's mode-router only applies to the project's own `wiki/`.

---

## Roadmap from here

v1.8.0 closes priority gap 5. The compass artifact's full picture:

| Axis (per audit §9) | v1.7.2 status | v1.8.0 status | Path to LEAD |
|---|---|---|---|
| Compounding wiki primitive | #1 | #1 | ✓ |
| Multi-writer safety | #1 | #1 | ✓ |
| Retrieval architecture (free tier) | #1 | #1 | ✓ |
| License / openness | #1 | #1 | ✓ |
| **Methodology support** | TIE | **#1** ← v1.8.0 closes | ✓ |
| Derivative outputs (audio/video/quiz) | NO | NO | v2.0 (wiki-derive) |
| GUI / install ergonomics | NO | NO | v2.5+ (Community Plugin fork) |

After v1.8.0: **#1 on 5 of 7 axes per compass framework**. The remaining 2 axes require multi-release effort:
- **v1.9** — multimodal ingest (YouTube / PDF / EPUB / image OCR)
- **v2.0** — `wiki-derive` skill: audio overviews, quiz generation, study guides, mindmap synthesis (NotebookLM parity)
- **v2.5+** — Community Plugin GUI shell (mainstream Obsidian user reach)

---

## Cross-reference

- [`skills/wiki-mode/SKILL.md`](../skills/wiki-mode/SKILL.md) — the skill itself
- [`scripts/wiki-mode.py`](../scripts/wiki-mode.py) — router + config helper
- [`bin/setup-mode.sh`](../bin/setup-mode.sh) — interactive setup
- [`tests/test_wiki_mode.py`](../tests/test_wiki_mode.py) — hermetic test suite (15 assertions)
- [`docs/compound-vault-guide.md`](compound-vault-guide.md) — v1.7 omnibus that v1.8 builds on
- v1.7.0 audit §9 axis 6: [`docs/audits/v1.7.0-audit-2026-05-17.md`](audits/v1.7.0-audit-2026-05-17.md)
