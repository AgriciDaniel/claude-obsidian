---
description: Periodic scan of wiki quality metrics — flags stale/over-corrected/hub pages for review.
---

Run the periodic health scan described in
[skills/learn/references/evolution-taxonomy.md](../skills/learn/references/evolution-taxonomy.md#quality-metrics-tracked-in-claudeskill-metricsjson).

Read `.claude/skill-metrics.json` and surface:

1. **Over-corrected pages** — `total_corrections / total_references > 0.3`.
   These pages are wrong more than right; recommend a deep review or rewrite.

2. **Hub pages to split** — `total_derivations > 5`. Consider converting the
   page into an `_index.md` with children.

3. **Stale-but-important pages** — `days_since_last_touched > 60` AND
   `total_references > 3`. Used a lot, but never refreshed — likely drifting.

4. **Orphans** — pages with `total_references == 0` and `last_touched > 30d`.
   Candidates for archival.

5. **Queue pressure** — if `.claude/learn-queue.json` has >5 pending items,
   prompt to run "review learnings" before more accumulate.

Output a short report per category. Do NOT auto-modify anything — this is a
read-only audit that hands findings back to the user.
