---
description: Regenerate Claude's observations notebook about the user's patterns (runs at most once per 24h).
---

Invoke the `analyze-patterns` skill at
[skills/analyze-patterns/SKILL.md](../skills/analyze-patterns/SKILL.md).

Reads recent log/journal/project/area entries, rewrites
`wiki/_claude/observations.md` with fresh behavioral / workflow / emotional /
thematic / contradiction / hypothesis signals, and updates
`.claude/last-observation.json`. Exits silently if <24h since last run unless
user explicitly invokes.
