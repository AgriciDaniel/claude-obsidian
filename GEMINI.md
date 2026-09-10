# claude-obsidian: Gemini instructions

Read `AGENTS.md` as the canonical host-neutral contract. Skills live in
`skills/<name>/SKILL.md` and the portable core lives in `claude_obsidian/`.

Install skill discovery with:

```bash
bash scripts/setup-multi-agent.sh --host gemini
bash scripts/setup-multi-agent.sh --host gemini --apply
```

The first command previews the links; the second applies that reviewed scope.

This repository is product source, not the default user vault. Create a
separate vault with the dry-run-first `init` command or adopt an existing vault.
Resolve that vault before reading `wiki/hot.md` or running a skill.

All shared mutations use one inspected `claude-obsidian.transaction.v1` bundle.
Parallel workers draft only. Do not use direct shared writes, automatic commits,
or the deprecated per-file lock helper. Remote egress and destructive actions
need explicit user consent.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
