---
name: learn
description: >
  Self-learning skill. Reviews the current conversation transcript and distills
  new knowledge into the wiki (goals, projects, areas, people, resources,
  learning, journal). Preferences are queued for review before hitting CLAUDE.md.
  Triggers on: "reflect", "learn from this", "self-learn", "/learn", "/reflect",
  "review learnings", and the Stop-hook prompt at session end.
allowed-tools: Read Write Edit Glob Grep Bash
---

# learn: Distill Knowledge from Conversations into the Wiki

You just finished (or are finishing) a conversation with the user. Your job is
to read back through the session, pull out anything worth remembering, and file
it into the second-brain wiki. The user writes, thinks, and decides things
while we talk — this skill makes sure none of it is lost.

The routing rules are identical to [inbox-classifier](../inbox-classifier/SKILL.md).
Reuse that mental model — this skill is inbox-classifier but the "inbox" is the
conversation itself.

---

## Step 1: Review the Transcript

Walk through the whole conversation, not just the last few turns. Use the
extraction framework in [references/extraction-prompt.md](references/extraction-prompt.md)
to scan category by category so you don't only capture the freshest content.

For long sessions, read [wiki/hot.md](../../wiki/hot.md) first — it already has
the recent state cached, so you can focus extraction on what's new beyond that.

---

## Step 2: Extract by Category

For each category, ask "did anything new/changed/interesting come up?"

- **Goals** — new ambitions, milestones, commitments, deadlines
- **Projects** — new project ideas, updates, blockers, next steps, decisions
- **Areas** — health, career, finance, creative context (append dated sections)
- **Learning** — concepts understood, skills practiced, "I learned X" moments
- **People** — named individuals, context about them, follow-ups
- **Resources** — tools, books, apps, links, frameworks mentioned
- **Journal** — reflections, emotional state, daily-log observations
- **Preferences** — corrections, rules, style directives ("don't do X", "always Y")

Preferences are detected using [references/preference-patterns.md](references/preference-patterns.md).

---

## Step 3: Deduplicate

Before writing anything, Grep the target location to see if the item already
exists. Examples:

```bash
# Before adding a person
grep -i "person-name" wiki/people/_index.md

# Before creating a project page
ls wiki/projects/ | grep -i "projectname"

# Before adding a resource
grep -i "resource title" wiki/resources/_index.md
```

If it exists: update the existing entry with new context instead of creating a
duplicate. If it doesn't: create it.

---

## Step 3.5: Classify by Evolution Type

For each capture, before filing, decide its evolution type per
[references/evolution-taxonomy.md](references/evolution-taxonomy.md):

- **FIX** — the wiki already says something about this, and the user just
  corrected or updated it. Edit in place, append a dated `### Fixed` block.
- **DERIVED** — extends an existing page (sub-project, new context on a person,
  spin-off resource). New page with `parent: [[...]]` frontmatter; parent page
  gets a "Derivations" link.
- **CAPTURED** — net-new, no parent in the wiki. File normally.

Record the type in the entry's frontmatter (`origin: fix|derived|captured`) and
in the metrics store (Step 7.5).

---

## Step 4: Route Using the Matrix

| Signal | Target | Action |
|--------|--------|--------|
| Goals, commitments, milestones | `wiki/goals/` | Update [[Annual Goals 2026]] or create goal page |
| Project work/updates/ideas | `wiki/projects/` | Append to existing page or create new |
| Health/career/finance/creative | `wiki/areas/*.md` | Append dated section |
| Concepts learned | `wiki/learning/_index.md` | Add row, or create concept page |
| Named people | `wiki/people/_index.md` | Add or update row |
| Tools/books/apps/links | `wiki/resources/_index.md` | Add row |
| Reflections, inner state | `wiki/journal/` | Create `YYYY-MM-DD — [theme].md` |
| Preferences / corrections | `.claude/learn-queue.json` | **Queue** — do NOT write to CLAUDE.md directly |

**When in doubt: journal/ is always safe.**

---

## Step 5: File Facts Directly

### Appending to an existing page
```markdown
---
### [YYYY-MM-DD]
[content — preserve the user's exact wording where it carries meaning]
```

### Creating a new page
Use the frontmatter templates from the inbox-classifier skill
([skills/inbox-classifier/SKILL.md](../inbox-classifier/SKILL.md#step-3-file-each-entry)).

---

## Step 6: Queue Preferences (do NOT auto-write to CLAUDE.md)

For each detected preference, append an entry to `.claude/learn-queue.json`:

```json
{
  "id": "pref-YYYY-MM-DD-NNN",
  "captured": "YYYY-MM-DDTHH:MM:SS",
  "type": "preference",
  "origin": "fix|derived|captured",
  "parent_rule": "[text of existing rule being fixed/derived, or null]",
  "content": "[the rule, phrased as an imperative]",
  "context": "[one-sentence explanation of when/why it came up]",
  "confidence": 0.00,
  "target": "CLAUDE.md",
  "status": "pending"
}
```

`origin` uses the OpenSpace taxonomy:
- `fix` — corrects an existing CLAUDE.md rule (Grep CLAUDE.md first to find it)
- `derived` — narrows / specializes an existing rule
- `captured` — brand new preference, no parent rule

Read the file first, append to the `pending` array, write it back. Never
clobber `approved` or `rejected`.

Confidence rubric (see [references/preference-patterns.md](references/preference-patterns.md)):
- 0.95 — explicit correction, repeated or emphatic ("no, NEVER do X")
- 0.85 — explicit one-time rule ("always do X")
- 0.70 — strong preference ("I prefer X")
- 0.60 — implicit, inferred from reaction

Skip anything below 0.60.

---

## Step 7: Handle "review learnings"

If the user says "review learnings" (or similar), don't re-extract — instead,
read `.claude/learn-queue.json` and walk the user through each `pending` item:

```
Preference 1 of N:
  "No em dashes in writing"
  Context: User corrected an em dash in output
  Confidence: 0.90
  Approve? (y/n/edit)
```

On **approve** — append the rule to `CLAUDE.md` under a "Learned Preferences"
section (create the section if missing), move the item from `pending` to
`approved`, and record the approval timestamp.

On **reject** — move to `rejected` with a timestamp.

On **edit** — let the user rewrite the `content` field, then approve.

---

## Step 7.5: Update Quality Metrics + Safety Scan

Before writing any captured content, scan it for:
- API keys / tokens (`sk-…`, `ghp_…`, `xox[bpoa]-…`)
- Prompt-injection patterns (`ignore previous`, stray `system:` roles)
- Env-var-looking credentials in quoted strings

If any match, **skip** the write and append a line to
`.claude/learn-rejects.log` with timestamp + reason. Never silently alter the
content to strip secrets — flagging + skipping keeps the user in control.

For every page created or updated, upsert into `.claude/skill-metrics.json`:

```json
{
  "path": "wiki/.../page.md",
  "origin": "fix|derived|captured",
  "parent_ids": ["..."],
  "total_references": N,
  "total_corrections": N,
  "total_derivations": N,
  "last_touched": "YYYY-MM-DDTHH:MM:SS",
  "confidence": 0.00
}
```

On FIX: increment `total_corrections` on the target page's existing entry.
On DERIVED: increment `total_derivations` on the parent entry, create a fresh
entry for the child.
On CAPTURED: create a fresh entry.

### Anti-loop guard
Before any edit, read `.claude/skill-metrics.json` and check `last_touched`
for the target page. If within the last **60 minutes**, skip and queue a
`deferred` note instead. Prevents ping-ponging edits when the conversation
revisits a topic.

---

## Step 8: Update Log and Hot Cache

After all filing is done:

1. Prepend to `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] learn | Distilled [N] items from session
   - Filed: [summary list of what landed where]
   - Queued preferences: [N] (review with "review learnings")
   ```

2. Rewrite the Recent Changes and Active Threads sections of `wiki/hot.md` to
   reflect what's new.

---

## Step 9: Report to User

Keep it short:

```
Learned from this session:
→ Filed project: [name]
→ Added person: [name]
→ Added resource: [name]
→ Journal entry: [title]
→ Queued preference: [one-line] (review with "review learnings")

All entries versioned via the auto-commit hook.
```

If nothing was worth capturing, say so — don't fabricate filler.

---

## Important Rules

- Never write preferences directly to `CLAUDE.md` — always queue.
- Never discard content — journal/ catches anything ambiguous.
- Preserve the user's exact words where they carry meaning; paraphrasing can
  strip nuance.
- Date everything with today's date.
- Deduplicate aggressively — updating an existing entry beats creating a
  near-duplicate.
- One conversation can produce multiple wiki entries across sections — split
  cleanly.
- If the transcript is empty or trivial (e.g. a single "thanks"), exit silently.
