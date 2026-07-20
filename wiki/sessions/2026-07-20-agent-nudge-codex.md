---
date: 2026-07-20
project: agent-nudge
agent: codex
status: completed
---
## What I did

Implemented and tested the v0.4 transactional project connector manager for Claude Code, Codex, and OpenCode.

## Files changed

- `src/connectors/index.ts`
- `src/connectors/manager.ts`
- `src/connectors/types.ts`
- `tests/unit/connectors.test.ts`
- `tests/integration/connectors.test.ts`

## Decisions made

- All three providers use the exact `ENFORCED` capability label with explicit covered-action and enabled/trusted-hook caveats.
- Provider JSON is merged using a manifest-recorded owned hook value; OpenCode plugins and optional bridges are hash-owned files.
- Connect/disconnect changes use backups, atomic writes, rollback, drift refusal, path containment, and junction/symlink checks.

## Next steps

- Wire the exported manager API into the v0.4 CLI and supply provider hook commands/OpenCode plugin content as connector artifacts.
