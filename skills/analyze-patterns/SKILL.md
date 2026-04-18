---
name: analyze-patterns
description: >
  Regenerate Claude's private observations about the user's patterns and
  tendencies. Reads the wiki (log, journal, projects, areas) and rewrites
  wiki/_claude/observations.md. Runs on demand ("/analyze-patterns", "analyze my
  patterns") or when SessionStart reports >24h since last regeneration.
allowed-tools: Read Write Edit Glob Grep Bash
---

# analyze-patterns: Generate Claude's Observations

You are updating Claude's private analytical notebook about the user. This is
pattern-recognition work, not summarization. Look across sessions for signals
the user themselves wouldn't spot.

---

## Step 1: Check Staleness

Read `.claude/last-observation.json`:
```json
{ "last_run": "YYYY-MM-DDTHH:MM:SS", "last_source_hash": "..." }
```

If `last_run` is <24h old AND the user didn't explicitly invoke this skill,
exit silently. No work needed.

---

## Step 2: Gather Source Material

Read (in this order):

1. `wiki/_claude/observations.md` — the current state, to compare against
2. `wiki/log.md` — last 14 days of filings (grep by date)
3. `wiki/hot.md` — current active context
4. `wiki/journal/*.md` — all entries from last 30 days
5. `wiki/projects/*.md` — active projects and their recent updates
6. `wiki/areas/*.md` — health / career / finances / creative sections, last 30 days
7. `.claude/learn-queue.json` — what preferences got queued (and rejected → interesting signal)
8. `.claude/learn-rejects.log` — safety rejections (also interesting)

Skip `wiki/_claude/` itself during reading — you're writing there, don't feed
yourself.

---

## Step 3: Analyze — Six Lenses

For each lens, ask the specific question. Write 2–5 observations per lens, or
leave blank if no signal.

### Behavioral Patterns
> What does the user repeatedly do (or avoid) across multiple sessions?

Look for: repeated question types, re-asked topics, habitual approaches, tools
they reach for first, things they never touch.

### Workflow Tendencies
> In what order does work happen? Where does it stall?

Look for: time-of-day patterns in journal entries, project pages that stall at
similar stages, recurring blockers.

### Emotional / Energy Signals
> What's heavy? What's energizing? Where's the ambivalence?

Read journal tone carefully. Note words that repeat — anxiety, excitement,
fatigue, defensiveness. Note what's written about vs what's written around.

### Recurring Themes
> What's come up ≥3 times in ≥2 different contexts in the last 30 days?

These are probably load-bearing concerns. Surface them even if the user hasn't
named them.

### Blind Spots & Contradictions
> Stated goals vs observed behavior. Things he says vs does.

Gentle, not gotcha. Example: "stated goal is a specific habit 4x/week, but
journal shows it mentioned once in last 14 days."

### Hypotheses to Test
> What do I *suspect* but can't confirm yet?

Frame as questions. Example: "Hypothesis: project stress peaks correlate with
financial anxiety, not creative blocks — needs more data to confirm."

---

## Step 4: Write

Rewrite `wiki/_claude/observations.md` preserving the section structure but
refreshing content. Keep the frontmatter, update `updated:` to today's date.

Include at the top:
```
**Last regenerated:** YYYY-MM-DD
**Sources inspected:** [list of file globs]
**Session count in window:** [N sessions inspected]
```

---

## Step 5: Update Timestamp

Write `.claude/last-observation.json`:
```json
{
  "last_run": "YYYY-MM-DDTHH:MM:SS",
  "last_source_hash": "[optional: sha of source files concatenated]"
}
```

---

## Step 6: Report

Short summary to user:
```
Refreshed observations. [N] new patterns, [N] carried over, [N] retired.
Notable: [one-line headline].
Full notebook: wiki/_claude/observations.md
```

---

## Rules

- **Don't fabricate.** Empty sections are better than invented patterns. The
  whole point is that these are grounded in what's actually in the vault.
- **Preserve carry-overs.** If a pattern from last run still holds, keep it —
  don't rewrite for novelty.
- **Retire stale hypotheses.** If a hypothesis was unconfirmed after 30 days
  and no new signal supports it, delete it.
- **Be kind but honest.** This isn't a roast. It's what a thoughtful friend
  would notice. Contradictions get surfaced gently.
- **Don't paste observations into the active chat unless asked.** This notebook
  is reference material, not conversation fodder.
