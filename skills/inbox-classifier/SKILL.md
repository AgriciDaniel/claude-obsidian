---
name: inbox-classifier
description: >
  Classifies and files raw inbox notes into the correct wiki sections.
  Triggers on: "process my inbox", "process inbox", "file my notes", "classify inbox".
allowed-tools: Read Write Edit Glob Grep Bash
---

# inbox-classifier: Auto-classify Inbox Notes

You are processing raw, unstructured notes from the `inbox/` folder and filing them into the correct wiki sections. The user writes freely — your job is to read intent, classify, and file without losing anything.

---

## Step 1: Find Inbox Files

```bash
ls inbox/
```

Skip `README.md`. Process every other `.md` file found.

---

## Step 2: Read Each File

Read the full content. Then classify it using the rules below.

---

## Classification Rules

A single note can produce multiple wiki entries if it covers multiple topics. Split it if needed.

| If the note contains... | File to... |
|------------------------|------------|
| Goals, ambitions, targets, milestones, progress on goals | `wiki/goals/` — update [[Annual Goals 2026]] or create a new goal page |
| Project updates, project ideas, next steps, blockers | `wiki/projects/` — update existing project page or create new one |
| Health updates, fitness, sleep, habits, body, substances | `wiki/areas/Health.md` — append under relevant section |
| Career, work, income, skills, business decisions | `wiki/areas/Career.md` — append under relevant section |
| Money, spending, income, financial decisions | `wiki/areas/Finances.md` — append under relevant section |
| Creative work, design, aesthetic, art, music | `wiki/areas/Creative.md` — append under relevant section |
| Things learned, concepts understood, skills practiced | `wiki/learning/_index.md` — add row, or create a concept page |
| Notes about a specific person, follow-ups, context | `wiki/people/_index.md` — add or update row |
| Books, tools, apps, links, courses, frameworks | `wiki/resources/_index.md` — add row |
| Reflections, feelings, daily log, observations, inner state | `wiki/journal/` — create a new entry named `YYYY-MM-DD — [theme].md` |
| Random thoughts, observations with no clear category | `wiki/journal/` — file as a raw thought entry |

**When in doubt: journal/ is always safe.**

---

## Step 3: File Each Entry

### For APPENDING to an existing page:
Add a dated section at the bottom:
```markdown
---
### [YYYY-MM-DD]
[content]
```

### For CREATING a new page:
Use the appropriate frontmatter:

**Journal entry:**
```yaml
---
type: reflection
title: "[descriptive title]"
date: YYYY-MM-DD
tags: [journal]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Project page:**
```yaml
---
type: project
title: "[name]"
status: active
area: [health|career|finance|creative|personal]
priority: 2
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [project]
---
```

**Learning concept:**
```yaml
---
type: concept
title: "[concept name]"
status: developing
tags: [learning]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

---

## Step 4: Archive the Processed File

After filing, move the inbox note to `.raw/processed/`:
```bash
mv "inbox/[filename].md" ".raw/processed/[filename].md"
```

Do NOT delete it — keep it as the source of truth.

---

## Step 5: Update Index and Hot Cache

After processing all files:

1. Update `wiki/index.md` — add any new pages to the correct section
2. Update `wiki/log.md` — prepend a new entry:
```markdown
## [YYYY-MM-DD] inbox | Processed [N] inbox notes
- Filed: [list what was created/updated]
```
3. Update `wiki/hot.md` — rewrite the Recent Changes and Active Threads sections

---

## Step 6: Report to User

Show a clean summary:
```
Processed [N] notes:

→ Filed to journal/: [title]
→ Appended to Health: [what was added]
→ Created project: [name]
→ Added to learning: [topic]

All originals archived to .raw/processed/
```

---

## Important Rules

- Never discard content — if unsure, journal/ catches everything
- Preserve the user's exact words in the filed note, don't paraphrase away meaning
- Date everything — use today's date if the note has no date
- If a note is ambiguous, classify by the strongest signal in it
- One inbox note can produce multiple wiki entries if it genuinely covers multiple topics — split cleanly
