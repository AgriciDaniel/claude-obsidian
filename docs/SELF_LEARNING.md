# Self-Learning System

A continuously-improving layer for `claude-obsidian` that distills every
conversation into durable wiki knowledge, with classified evolution
(**FIX / DERIVED / CAPTURED**), a preference-review queue, and a private
behavioral-pattern notebook regenerated every 24 hours.

## What It Does

1. **Distills conversations into wiki entries.** At the end of a session
   (or on demand via `/learn`, `/reflect`), Claude scans the transcript for
   durable facts, preferences, decisions, corrections, and domain knowledge —
   then writes them to the right wiki page using the evolution taxonomy.

2. **Classifies each learning by evolution type:**
   - **FIX** — in-place repair of a wrong/stale statement on an existing page.
     Adds a dated `### Fixed` block alongside the correction.
   - **DERIVED** — a specialization/refinement of an existing rule. Creates a
     new page with `parent: [[Parent Page]]` frontmatter and appends the
     derivation to the parent's "Derivations" section.
   - **CAPTURED** — net-new knowledge with no parent. Creates a fresh page.

3. **Queues preference/rule candidates** with confidence scores (0.60–0.95).
   User reviews the queue at any time ("review learnings") and accepted items
   land in `CLAUDE.md` or the appropriate wiki page.

4. **Maintains a 24h behavioral-observation notebook** at
   `wiki/_claude/observations.md` (not shipped here — per-user). Six lenses:
   behavioral, workflow, emotional, recurring themes, blind spots, hypotheses.
   Regenerates via `/analyze-patterns`, gated to run at most once per 24h.

5. **Auto-files dropped notes** from `inbox/` into the right wiki destination
   via the `inbox-classifier` skill.

## Install

### 1. Drop the files in place

This PR ships everything into canonical locations. After merging, make sure
your project has:

```
skills/learn/SKILL.md
skills/learn/references/{evolution-taxonomy,preference-patterns,extraction-prompt}.md
skills/analyze-patterns/SKILL.md
skills/inbox-classifier/SKILL.md
commands/{learn,reflect,learn-health,analyze-patterns}.md
bin/{check-inbox,learn-queue-check,observation-check}.sh
inbox/README.md
wiki/meta/system-architecture.md
.obsidian/snippets/hide-engine.css          # optional cosmetic
```

### 2. Wire the hooks

Add to `.claude/settings.json` at the **vault** level:

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "bash bin/check-inbox.sh" },
        { "type": "command", "command": "bash bin/learn-queue-check.sh" },
        { "type": "command", "command": "bash bin/observation-check.sh" }
      ]}
    ],
    "Stop": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "echo 'LEARN: Session ending — invoke the learn skill (skills/learn/SKILL.md) to distill new knowledge from this conversation into the wiki before exiting.'" }
      ]}
    ]
  }
}
```

The three SessionStart hooks are non-fatal (exit 0 when silent). The Stop
hook prints a reminder; Claude uses it to trigger the `learn` skill.

### 3. Enable the Obsidian CSS snippet (optional)

Open Obsidian → Settings → Appearance → CSS snippets → toggle
`hide-engine` on. Hides the engine directories (`skills/`, `commands/`,
`bin/`, `.claude/`) from the file tree so the vault looks like a wiki, not
a codebase.

## Usage

| Command | What it does |
|--------|--------------|
| `/learn` | Manual distillation of the current conversation |
| `/reflect` | Same as `/learn`, alternate trigger phrase |
| `"review learnings"` | Walks the queue of candidate rules/preferences; accepted items are applied |
| `/learn-health` | Diagnostics: queue depth, reject rate, last-run timestamps |
| `/analyze-patterns` | Regenerates `wiki/_claude/observations.md` (≤1×/24h) |

The system also runs implicitly: at Stop, the hook reminder nudges Claude to
invoke `learn`; dropped inbox notes trigger `inbox-classifier`.

## Evolution Taxonomy

See `skills/learn/references/evolution-taxonomy.md` for the complete rubric.
Three classes:

| Class | Trigger | Write pattern |
|------|---------|---------------|
| **FIX** | New info contradicts existing page | Edit in place; append dated `### Fixed` note |
| **DERIVED** | New info refines an existing rule | New page with `parent:` frontmatter; link both ways |
| **CAPTURED** | New info has no parent | New page in the domain folder |

Every write includes:
- A **confidence score** (0.60–0.95) per
  `skills/learn/references/preference-patterns.md`.
- An **anti-loop guard**: no page is rewritten more than once per 60 minutes.
- A **safety scan** for API-key-shaped strings (`sk-[A-Za-z0-9]{20,}`,
  `ghp_…`, `xox[bpoa]-…`) — matches abort the write.

## Credits

- **Evolution taxonomy (FIX/DERIVED/CAPTURED)** and skill-quality-metrics
  concepts adapted from [OpenSpace](https://github.com/HKUDS/OpenSpace).
- **Preference-queue flow** inspired by
  [claude-reflect](https://github.com/BayramAnnakov/claude-reflect).

## Manual Test Plan

1. **Inbox classify:** drop a note into `inbox/` and ask Claude to
   "process my inbox". Confirm it moves to the right wiki folder.
2. **Reflect:** after a short conversation adding a new fact, say
   `/reflect`. Confirm a wiki page is created/updated with a confidence
   score.
3. **Pattern analysis:** run `/analyze-patterns`. Confirm
   `wiki/_claude/observations.md` is (re)generated and
   `.claude/last-observation.json` is updated. Re-run within 24h and
   confirm it's skipped.
4. **Queue review:** say "review learnings". Confirm queued candidates are
   walked and accepted items land in their targets.
5. **Health check:** run `/learn-health` and confirm it reports queue depth
   and last-run timestamps without error.
