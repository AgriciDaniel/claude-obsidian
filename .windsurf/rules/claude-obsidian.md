# claude-obsidian: Windsurf rules

Read `AGENTS.md` as the canonical host-neutral contract. Preview and then
install Cascade skill links with
`bash scripts/setup-multi-agent.sh --host windsurf --workspace "$PWD"` followed by
the same command with `--apply`, and load the matching
`skills/<name>/SKILL.md` when a request triggers it.

The product clone and user vault are separate. Resolve the user vault before
reading hot context or mutating knowledge. Raw payloads are create-only;
parallel workers return drafts; one orchestrator inspects and applies one
recoverable transaction. Queries and lint remain read-only. Network egress,
destructive repair, and Git checkpoints require explicit user consent.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
