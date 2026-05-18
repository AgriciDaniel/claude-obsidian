---
name: save
description: >
  Save the current conversation, answer, or insight into the Obsidian wiki vault as a
  structured note. Analyzes the chat, determines the right note type, creates frontmatter,
  files it in the correct wiki folder, and updates index, log, and hot cache.
  Triggers on: "save this", "save that answer", "/save", "file this",
  "save to wiki", "save this session", "file this conversation", "keep this",
  "save this analysis", "add this to the wiki".
allowed-tools: Read Write Edit Glob Grep
---

# save: File Conversations Into the Wiki

Good answers and insights shouldn't disappear into chat history. This skill takes what was just discussed and files it as a permanent wiki page.

The wiki compounds. Save often.

---

## Transport (v1.7+)

The session-note write itself follows the standard transport policy. Read `.vault-meta/transport.json` (auto-created by `bash scripts/detect-transport.sh`):

- **cli** — `obsidian-cli write "$VAULT" "$NOTE" < session.md`; see [`skills/wiki-cli/SKILL.md`](../wiki-cli/SKILL.md)
- **mcp-obsidian** / **mcpvault** — `mcp__obsidian-vault__write_note`
- **filesystem** — Claude's `Write` tool with absolute path

Full decision tree: [`wiki/references/transport-fallback.md`](../../wiki/references/transport-fallback.md). Index/log/hot updates use the same transport.

---

## Mode awareness (v1.8+)

Before creating the session note, consult the vault's methodology mode via `python3 scripts/wiki-mode.py route session "<topic-summary>"`. The router returns the vault-relative path:

- **generic**: `wiki/sessions/<date>-<topic>.md` (v1.7 default)
- **LYT**: `wiki/notes/<date>-<topic>.md` + update the relevant session/journal MOC
- **PARA**: `wiki/projects/inbox/<date>-<topic>.md` (user reroutes to specific projects)
- **Zettelkasten**: `wiki/<ID>-session-<topic>.md` (timestamped ID becomes the filename prefix)

If `.vault-meta/mode.json` is absent, the router returns mode=generic paths. **Important global rule**: per global CLAUDE.md `/save` convention, sessions for cross-project work should still file to `~/Documents/Obsidian Vault/sessions/` rather than the project's wiki. The mode router applies when filing to the project's own wiki/, not when filing to the global personal vault.

## Concurrency (v1.7+)

Session-note writes MUST be preceded by `wiki-lock acquire`:

```bash
NOTE_PATH="wiki/questions/<slug>.md"   # or wiki/concepts/, wiki/meta/, etc.
bash scripts/wiki-lock.sh acquire "$NOTE_PATH" || {
  echo "skipped: $NOTE_PATH currently locked by another writer"; exit 0
}
# … write the note via §Transport-selected method …
bash scripts/wiki-lock.sh release "$NOTE_PATH"
```

For multi-file saves (e.g., session note + index update + log append), acquire each lock in sorted-path order to avoid deadlocks. Index/log/hot updates lock just like content pages.

See `skills/wiki-ingest/SKILL.md` §Concurrency for the full lock semantics.

---

## Note Type Decision

Determine the best type from the conversation content:

| Type | Folder | Use when |
|------|--------|---------|
| synthesis | wiki/questions/ | Multi-step analysis, comparison, or answer to a specific question |
| concept | wiki/concepts/ | Explaining or defining an idea, pattern, or framework |
| source | wiki/sources/ | Summary of external material discussed in the session |
| decision | wiki/meta/ | Architectural, project, or strategic decision that was made |
| session | wiki/meta/ | Full session summary: captures everything discussed |

If the user specifies a type, use that. If not, pick the best fit based on the content. When in doubt, use `synthesis`.

---

## Save Workflow

**Step 0: Decide the destination root.** Check in order:

1. **User explicit override.** If the user said "save to this project's wiki" / "save to the personal vault" / a specific path, respect it.
2. **Project CLAUDE.md or global `~/.claude/CLAUDE.md` `/save` rule.** If either declares a personal-vault destination (e.g., `~/Documents/Obsidian Vault/`), that is the destination ROOT. The Note Type table below describes paths relative to whichever root is active. Append the new note to `<root>/log/ingest-log.md` at the top, in the format that file already uses.
3. **Default.** The project's own `wiki/` folder.

The mode router (`python3 scripts/wiki-mode.py route session "<topic>"`) applies when filing into the project's own `wiki/`. When filing into a personal-vault root, use the canonical folders documented in that vault's CLAUDE.md (commonly `sessions/`, `concepts/`, `sources/`) — the mode router is NOT consulted for personal-vault writes by default. Filename sanitization (slug + safe_name) still applies regardless of root: strip path separators, NUL bytes, control chars, leading dots/hyphens.

**Then continue the workflow:**

1. **Scan** the current conversation. Identify the most valuable content to preserve.
2. **Ask** (if not already named): "What should I call this note?" Keep the name short and descriptive.
3. **Determine** note type using the table above.
4. **Extract** all relevant content from the conversation. Rewrite it in declarative present tense (not "the user asked" but the actual content itself).
5. **Create** the note in `<destination-root>/<chosen-folder>/<title>.md` (per Step 0). Full frontmatter. If a note with the same path already exists, ASK before overwriting.
6. **Collect links**: identify any wiki pages mentioned in the conversation. Add them to `related` in frontmatter.
7. **Update** `wiki/index.md`. Add the new entry at the top of the relevant section.
8. **Append** to `wiki/log.md`. New entry at the TOP:
   ```
   ## [YYYY-MM-DD] save | Note Title
   - Type: [note type]
   - Location: wiki/[folder]/Note Title.md
   - From: conversation on [brief topic description]
   ```
9. **Update** `wiki/hot.md` to reflect the new addition.
10. **Confirm**: "Saved as [[Note Title]] in wiki/[folder]/."

---

## Frontmatter Template

```yaml
---
type: <synthesis|concept|source|decision|session>
title: "Note Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - <relevant-tag>
status: developing
related:
  - "[[Any Wiki Page Mentioned]]"
sources:
  - "[[.raw/source-if-applicable.md]]"
---
```

For `question` type, add:
```yaml
question: "The original query as asked."
answer_quality: solid
```

For `decision` type, add:
```yaml
decision_date: YYYY-MM-DD
status: active
```

---

## Writing Style

- Declarative, present tense. Write the knowledge, not the conversation.
- Not: "The user asked about X and Claude explained..."
- Yes: "X works by doing Y. The key insight is Z."
- Include all relevant context. Future sessions should be able to read this page cold.
- Link every mentioned concept, entity, or wiki page with wikilinks.
- Cite sources where applicable: `(Source: [[Page]])`.

---

## What to Save vs. Skip

Save:
- Non-obvious insights or synthesis
- Decisions with rationale
- Analyses that took significant effort
- Comparisons that are likely to be referenced again
- Research findings

Skip:
- Mechanical Q&A (lookup questions with obvious answers)
- Setup steps already documented elsewhere
- Temporary debugging sessions with no lasting insight
- Anything already in the wiki

If it's already in the wiki, update the existing page instead of creating a duplicate.

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read the full conversation. Identify the actual decisions and synthesis, not the verbatim transcript. |
| 2 | OBSERVE (int) | Am I in a save-everything mood? Some sessions don't have lasting insight; the Skip criteria exists for a reason. |
| 3 | LISTEN | Did the user specify destination or type? Their explicit override comes first; defaults come second. |
| 4 | THINK | Pick destination root (Step 0), then note type, then folder. Match path sanitization to destination convention. |
| 5 | CONNECT (lat) | Does this content already have a wiki page? Update vs create matters — duplicates pollute the index. |
| 6 | CONNECT (sys) | Index + log + hot cache + frontmatter relations all update together — atomicity matters. |
| 7 | FEEL | Filename future-me can read cold; frontmatter that supports search. Avoid noise that drowns the signal. |
| 8 | ACCEPT | Some sessions don't deserve saving. Honor the Skip criteria; don't archive everything. |
| 9 | CREATE | Write the note, append to log at top, update index, refresh hot cache. |
| 10 | GROW | Skipped saves are also signal — what threshold filtered them? Refine the type table over time. |
