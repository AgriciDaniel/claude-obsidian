---
name: wiki-triage
description: "Runs the GTD capture/triage decision tree on an incoming item (task, idea, note, email, etc.) and files it through the methodology-mode router. Triggers on: capture this, triage this, what do I do with this, new task, process my inbox, gtd triage, clarify this item, qué hago con esto, nueva tarea."
allowed-tools: Read, Write, Bash
---

# wiki-triage: GTD Capture and Triage

Walk an incoming item through the GTD decision tree (David Allen's classic capture → actionability → 2-min rule → delegate → today/dated/waiting/someday/reference flowchart) and file the result through the methodology-mode router.

Don't interrogate the user with all five questions when the answer is already clear from context. Ask only what you don't know yet.

---

## The Decision Tree

```
1. Is there a concrete action?
   NO  → 2a (save or discard)
   YES → 2b (actionable path)

2a. Is it worth keeping?
   NO  → Discard. Tell the user; file nothing.
   YES → Is it a possible future action, or pure reference?
         → someday/maybe   (incubating idea, possible future action)
         → reference       (pure info, no action expected)

2b. Can it be done in 2 minutes?
   YES → Do it now. File nothing (tell the user).
   NO  → Can it be delegated?
         YES → waiting (delegated; ask who)
         NO  → Does it need to happen today?
               YES → today
               NO  → Can a date be attached?
                     → backlog (with or without due date)
```

Five terminal buckets: `today`, `backlog`, `waiting`, `someday`, `reference`.

---

## Triage Flow

### Step 1 — Understand the item

Read what the user gave you. Extract or confirm:
- What the item IS (task, idea, note, email thread, link, voice memo text, …)
- Any explicit hints the user gave (urgency, person involved, date)

If the item is ambiguous, ask ONE clarifying question before continuing.

### Step 2 — Walk the tree

Ask only what isn't already obvious. Suggested phrasings:

- **Actionability**: "Is there something concrete you need to do here, or is this more reference material?"
- **2-min**: "Could you knock this out in two minutes right now?"
- **Delegate**: "Is this something someone else should handle?"
- **Today vs. dated**: "Does this need to happen today, or can it sit in your backlog?"
- **Due date**: "Is there a specific date attached to this?"

### Step 3 — Determine bucket and title

From the answers, pick one of: `today`, `backlog`, `waiting`, `someday`, `reference`.

Choose a short, action-oriented title (for actionable buckets: verb + object, e.g. "Call dentist for appointment").

### Step 4 — Check the active mode

```bash
MODE=$(python3 scripts/wiki-mode.py get)
```

**If MODE=gtd**: use the router with the real bucket to get the filing path.

```bash
# Actionable items
PATH=$(python3 scripts/wiki-mode.py route action "<title>" --bucket today)
PATH=$(python3 scripts/wiki-mode.py route action "<title>" --bucket backlog [--due YYYY-MM-DD])
PATH=$(python3 scripts/wiki-mode.py route action "<title>" --bucket waiting)
PATH=$(python3 scripts/wiki-mode.py route action "<title>" --bucket someday)

# Reference items (source / pure info)
PATH=$(python3 scripts/wiki-mode.py route source "<title>")
# → lands in wiki/gtd/reference/ under gtd mode
```

**If MODE is anything else** (generic/lyt/para/zettelkasten): still run the triage — the decision tree is useful regardless of mode. Route with `type=action` or `type=source` as normal, but also write `gtd_bucket:` and (if applicable) `gtd_due:` into the page's frontmatter so the classification is preserved. Mention once, briefly, that `bash bin/setup-mode.sh --mode gtd` unlocks dedicated GTD folders.

### Step 5 — Acquire lock and write

```bash
bash scripts/wiki-lock.sh acquire "$PATH" || {
  echo "skipped: $PATH currently locked"; exit 0
}
# … write the page using the template from §Templates …
bash scripts/wiki-lock.sh release "$PATH"
```

Use the template matching the bucket (see §Templates below). Fill in frontmatter from the triage answers: title, bucket, due date, waiting_on, etc.

### Step 6 — Confirm

Tell the user where the item was filed and what bucket it landed in. One line is enough.

---

## Templates

Select from `skills/wiki-mode/templates/gtd/`:

| Bucket | Template |
|--------|----------|
| `today` | `action-template.md` |
| `backlog` | `action-template.md` |
| `waiting` | `waiting-template.md` |
| `someday` | `someday-template.md` |
| `reference` | `reference-template.md` |

---

## Edge Cases

**Item is actionable but user says "2 minutes"** — encourage them to do it now. Offer to file it as `today` if they want a record anyway.

**Waiting_on is unclear** — ask "Who are you waiting on for this?" before filing to `waiting`.

**No due date for backlog** — fine; the backlog filename won't have a date prefix. Ask once; if the user doesn't know, skip it.

**Mode is not gtd** — file normally via the existing router, but always add `gtd_bucket:` to frontmatter so the GTD classification isn't lost. Mention setup-mode once if it seems like the user would benefit from GTD folders.

**Discard** — tell the user plainly: "I'd toss this — it's neither actionable nor useful as reference. Want me to file it anyway?" Respect their answer.

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read the item carefully before asking anything. Most of the triage answers are already in what the user sent. |
| 2 | OBSERVE (int) | Am I rushing to "actionable" because it's the interesting path? Some things genuinely belong in reference or the trash. |
| 3 | LISTEN | The user's urgency, phrasing, and context clues carry most of the triage signal. Ask only what you still don't know. |
| 4 | THINK | Walk the tree in order; don't skip to a bucket you've already guessed before confirming with the user. |
| 5 | CONNECT (lat) | Does this item relate to an existing project or area? Note it in the filed page's `related:` frontmatter. |
| 6 | CONNECT (sys) | `wiki-mode.py route` determines the path; `wiki-lock.sh` protects concurrent writes; the template structures the page. |
| 7 | FEEL | A well-triaged item should feel like relief — clear next step, right bucket, nothing ambiguous left. |
| 8 | ACCEPT | "Discard" is a valid and valuable outcome. Not every capture deserves a file. |
| 9 | CREATE | File the page with full frontmatter; confirm to the user in one clean line. |
| 10 | GROW | If the same type of item keeps landing in the wrong bucket, that's feedback about the triage questions — note it. |
