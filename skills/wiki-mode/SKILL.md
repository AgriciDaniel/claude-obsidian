---
name: wiki-mode
description: "Methodology modes for the Compound Vault. Lets the vault declare an organizational style (LYT / PARA / Zettelkasten / Generic) that wiki-ingest, save, and autoresearch consult before filing new pages. Reads `.vault-meta/mode.json`; defaults to `generic` (v1.6/v1.7 behavior) when absent. Per the May 2026 compass artifact, methodology support was priority gap 5 — no other Claude+Obsidian competitor ships it as a first-class skill. Triggers on: set vault mode, switch to PARA, use LYT, what's my vault mode, zettelkasten setup, wiki mode, methodology mode, change mode, configure mode."
allowed-tools: Read, Write, Bash
---

# wiki-mode: Methodology Modes for the Compound Vault

The v1.6 + v1.7 vault structure was opinion-free — `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, and so on. That works for power-users with their own organizational instincts. It does NOT serve the large segment of Obsidian users who want a named methodology to follow.

**v1.8 ships `wiki-mode` to close that gap.** A vault declares a mode (LYT, PARA, Zettelkasten, or Generic) in `.vault-meta/mode.json`; the other skills consult it before deciding where to file new pages. Mode = `generic` is the default and preserves v1.6/v1.7 behavior exactly.

**Per May 2026 compass artifact**: This was priority gap 5 of the 5 identified. Ideaverse Pro 2.0 ($200 paid vault) ships LYT as an opinionated structure; no Claude+Obsidian competitor ships PARA / Zettelkasten / mode-aware routing as a first-class skill. v1.8 takes us from TIE → LEAD on the audit §9 methodology-support axis (5 of 7 axes #1).

---

## The four modes

### LYT (Linking Your Thinking — Nick Milo)

**Philosophy:** notes link, folders don't. The organizational primitive is the **MOC** (Map of Content) — a hub note that links into a cluster of atomic notes. You never browse folders; you navigate by following links.

**Filing convention:**
- `wiki/mocs/<topic>-moc.md` — the MOC for a topic cluster
- `wiki/notes/<atomic-note>.md` — flat list of atomic notes, named by their idea, all linked from at least one MOC

**When to use:** mid-to-large knowledge bases (>100 notes), users who think in terms of conceptual clusters, knowledge graphs.

### PARA (Tiago Forte)

**Philosophy:** organize by **actionability**, not topic. Active work in Projects, ongoing responsibilities in Areas, reference material in Resources, completed/inactive in Archives.

**Filing convention:**
- `wiki/projects/<project-name>/<note>.md` — active projects with a deadline/outcome
- `wiki/areas/<area-name>/<note>.md` — ongoing responsibilities (no deadline)
- `wiki/resources/<topic>/<note>.md` — reference material, organized by topic
- `wiki/archives/<year>/<note>.md` — completed projects, sunsetted areas

**When to use:** workflow-heavy users, knowledge workers managing many projects, GTD-adjacent practitioners.

### Zettelkasten (Niklas Luhmann's slip-box)

**Philosophy:** atomic notes, unique IDs, dense bidirectional linking. No folders. Every note answers exactly one idea. Notes find each other by ID references.

**Filing convention:**
- `wiki/<YYYYMMDDHHMMSSffffff>-<slug>.md` — flat, timestamped IDs (20 digits = date + microseconds, collision-resistant)
- Every note has `id:`, `parent_id:` (optional), `child_ids:` (optional) in frontmatter
- No subdirectories; the wiki/ root is the whole vault

**When to use:** academics, researchers, long-term thinkers building permanent knowledge artifacts. Highest discipline; smallest filing surface.

### Generic (default — v1.7 behavior)

**Filing convention:** preserves the v1.6/v1.7 default — `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, `wiki/<domain>/`. No opinion imposed.

**When to use:** when you don't want to commit to a methodology, or you're migrating from v1.7 and want zero behavior change.

---

## How to set the mode

```bash
bash bin/setup-mode.sh
```

Interactive prompt: pick one of the 4 modes. Writes `.vault-meta/mode.json`. Optionally seeds template folders (LYT `mocs/`, PARA `projects/areas/resources/archives/`).

To check the current mode programmatically:

```bash
cat .vault-meta/mode.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["mode"])'
```

To switch modes later: re-run `setup-mode.sh`. Existing files are NOT auto-migrated; the new mode only affects newly-filed pages from that point. Migration is a manual operation (see [migration section](#migration-between-modes) below).

---

## Mode config schema (`.vault-meta/mode.json`)

```json
{
  "schema_version": 1,
  "mode": "lyt|para|zettelkasten|generic",
  "configured_at": "ISO-8601 timestamp",
  "config": {
    "lyt": {
      "moc_folder": "wiki/mocs/",
      "notes_folder": "wiki/notes/"
    },
    "para": {
      "projects_folder": "wiki/projects/",
      "areas_folder": "wiki/areas/",
      "resources_folder": "wiki/resources/",
      "archives_folder": "wiki/archives/"
    },
    "zettelkasten": {
      "id_format": "YYYYMMDDHHMMSSffffff",
      "no_folders": true,
      "root_folder": "wiki/"
    },
    "generic": {
      "sources_folder": "wiki/sources/",
      "entities_folder": "wiki/entities/",
      "concepts_folder": "wiki/concepts/",
      "sessions_folder": "wiki/sessions/"
    }
  }
}
```

The `config` block always includes ALL four modes; the active one is named by `mode`. This lets you switch modes without losing custom folder overrides.

---

## How other skills consume the mode

The integration layer is in three skills:

- `skills/wiki-ingest/SKILL.md` — "## Mode awareness (v1.8+)" section
- `skills/save/SKILL.md` — "## Mode awareness (v1.8+)" section
- `skills/autoresearch/SKILL.md` — "## Mode awareness (v1.8+)" section

Each consults `.vault-meta/mode.json` (via `cat` or direct Read). If absent → mode = generic, behavior unchanged. If present and mode != generic, route per the mode's config.

The routing table:

| Content type | Generic | LYT | PARA | Zettelkasten |
|---|---|---|---|---|
| New source ingest | `wiki/sources/foo.md` | `wiki/notes/foo.md` + add to topic MOC | `wiki/resources/<topic>/foo.md` | `wiki/<ID>-foo.md` |
| New entity | `wiki/entities/<Name>.md` | `wiki/notes/<Name>.md` + entity MOC | `wiki/resources/people/<Name>.md` | `wiki/<ID>-<name>.md` |
| New concept | `wiki/concepts/<Name>.md` | `wiki/notes/<Name>.md` + concept MOC | `wiki/resources/concepts/<Name>.md` | `wiki/<ID>-<name>.md` |
| Session note (`/save`) | `wiki/sessions/<date>-<topic>.md` | `wiki/notes/<date>-<topic>.md` + session MOC | `wiki/projects/<project>/<date>-<topic>.md` | `wiki/<ID>-session-<topic>.md` |
| Research output (`/autoresearch`) | `wiki/concepts/<topic>.md` | `wiki/notes/<topic>.md` + topic MOC | `wiki/resources/<topic>/<topic>.md` | `wiki/<ID>-<topic>.md` |

---

## Templates

Per-mode templates live at `skills/wiki-mode/templates/`:

- [`lyt/moc-template.md`](templates/lyt/moc-template.md) — MOC scaffolding
- [`lyt/atomic-template.md`](templates/lyt/atomic-template.md) — atomic note linking into MOCs
- [`para/project-template.md`](templates/para/project-template.md) — project with status + deadline + next-action
- [`para/area-template.md`](templates/para/area-template.md) — ongoing responsibility
- [`para/resource-template.md`](templates/para/resource-template.md) — reference material
- [`zettel/atomic-template.md`](templates/zettel/atomic-template.md) — atomic claim + parent/child IDs

Skills that file new pages consult the template matching the (mode, content-type) pair as a structural starting point. Templates are SUGGESTIONS; the skill's own content logic always wins.

---

## Migration between modes

Switching modes does NOT auto-migrate existing files. Manual migration:

1. Set new mode: `bash bin/setup-mode.sh`
2. Existing files remain in their original locations and continue to work
3. New files file per the new mode
4. (Optional) Manually move existing files to the new structure using your file manager or `git mv`

Why no auto-migration: the wiki contains your thinking. Auto-rewriting paths could break wikilinks, lose data, or surprise you. Manual migration forces explicit decisions about what fits the new methodology vs what stays in its current home.

For LYT specifically: after switching to LYT, run `lint the wiki` (skill: wiki-lint) to identify orphan pages that would benefit from MOC inclusion.

---

## Feature gating

This skill is universally available in v1.8+. No `bin/setup-*.sh` required for the skill itself — only for explicitly setting a non-default mode. Skills that consume the mode check for `.vault-meta/mode.json`; absence = generic.

```bash
# Detection idiom for consumers:
if [ -f .vault-meta/mode.json ]; then
  MODE=$(python3 -c 'import json; print(json.load(open(".vault-meta/mode.json"))["mode"])')
else
  MODE="generic"
fi
```

---

## Why v1.8 ships this, not v2.0+

Per audit §9: methodology support is the cheapest axis to lead. Nobody else ships it. The implementation is mostly conventions + routing + templates; no new infrastructure, no new dependencies. It's the highest-ROI release in the roadmap before the bigger v2.0 (derive) + v2.5 (GUI) work.

After v1.8: claude-obsidian leads on 5 of 7 axes per compass artifact. The remaining 2 (GUI ergonomics, derivative outputs) are major releases by themselves.

---

## Cross-reference

- [`docs/methodology-modes-guide.md`](../../docs/methodology-modes-guide.md) — narrative guide, when-to-use-which decision tree
- [`wiki/references/methodology-modes.md`](../../wiki/references/methodology-modes.md) — short decision tree
- [`docs/compound-vault-guide.md`](../../docs/compound-vault-guide.md) — v1.7 omnibus (v1.8 builds on this)
- v1.7.0 audit §9 axis 6 (methodology TIE → LEAD): [`docs/audits/v1.7.0-audit-2026-05-17.md`](../../docs/audits/v1.7.0-audit-2026-05-17.md)

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read `.vault-meta/mode.json` to know which mode is active before routing anything. |
| 2 | OBSERVE (int) | Audit the assumption that mode=generic is the default — the user may be on LYT/PARA/Zettelkasten. |
| 3 | LISTEN | The mode is the user's organizational instinct, not yours. Respect what they configured. |
| 4 | THINK | Apply the mode-specific routing rule to the content type at hand (source / entity / concept / session / research). |
| 5 | CONNECT (lat) | This skill's `safe_name` is the canonical sanitizer — wiki-ingest, save, autoresearch all funnel through here. |
| 6 | CONNECT (sys) | Three consumer skills depend on `route` output; consistency across consumers is the v1.8 contract. |
| 7 | FEEL | Does the routed path feel right to the user? `wiki/notes/Foo.md` (LYT) means something different from `wiki/concepts/Foo.md` (generic). |
| 8 | ACCEPT | Mode choice is the user's call. Accept that PARA users will sometimes want to override the auto-route. |
| 9 | CREATE | Return the routed path string — a single safe filesystem location. |
| 10 | GROW | When modes change mid-vault, surface the migration cost honestly; existing pages do NOT auto-migrate. |
