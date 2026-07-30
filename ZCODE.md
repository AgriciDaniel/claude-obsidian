# claude-obsidian: ZCode instructions

Read `AGENTS.md` as the canonical host-neutral contract. Skills live in
`skills/<name>/SKILL.md` and the portable core lives in `claude_obsidian/`.

ZCode reads `AGENTS.md` at the workspace and user scope natively, so no
mirrored rules file is needed. Install skill discovery with:

```bash
bash bin/setup-multi-agent.sh --host zcode
bash bin/setup-multi-agent.sh --host zcode --apply
```

The first command previews the links; the second applies that reviewed scope.
Links land in `~/.zcode/skills/` (user-level), so every ZCode workspace can
invoke the skills without per-project setup.

This repository is product source, not the default user vault. Create a
separate vault with the dry-run-first `init` command or adopt an existing vault.
Resolve that vault before reading `wiki/hot.md` or running a skill.

All shared mutations use one inspected `claude-obsidian.transaction.v1` bundle.
Parallel workers draft only. Do not use direct shared writes, automatic commits,
or the deprecated per-file lock helper. Remote egress and destructive actions
need explicit user consent.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
