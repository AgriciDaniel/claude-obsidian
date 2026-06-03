# Privacy Boundary

`claude-obsidian` is published as a mechanism, not as a copy of a private vault.

The public project should help maintainers and users reproduce the workflow without receiving anyone's personal records, source imports, or generated outputs.

## Public Package

These materials are safe for the public repository when they are polished, documented, and useful to Codex maintainers:

- Core Codex skills and command entrypoints.
- Setup scripts and test scripts.
- Templates and seed example pages.
- Public documentation and release notes.
- Architecture diagrams that describe the mechanism.
- Minimal sample vault structure with placeholder content.

Experimental integrations and rough workflow experiments should stay out of the public surface until they have docs, tests, and a clear maintenance story.

## Private Local Vault

These materials are not part of the public package:

- `00_inbox/`
- `10_sources/`
- `20_logs/`
- `30_life/`
- `40_work/`
- `50_knowledge/`
- `60_outputs/`
- `_system/`
- `_plugin/`
- `.workflow/`

The same rule applies to equivalent folders in other vault layouts, including raw imports, personal dashboards, finance notes, health notes, conversation logs, browser history, client work, and generated media.

## Design Rule

When a workflow needs to be documented publicly:

1. Describe the mechanism.
2. Use placeholder paths and fictional examples.
3. Keep private examples out of screenshots, source snippets, and test fixtures.
4. Publish only reusable templates, scripts, and docs.
5. Treat private records as local runtime data.

## Maintainer Checklist

Before publishing:

- Check `git status --short`.
- Avoid broad `git add .` from a working vault.
- Stage only intended mechanism files.
- Search staged files for private path names and personal project labels.
- Confirm no logs, source imports, client material, finance data, or generated outputs are staged.

Suggested check:

```bash
git diff --cached --name-only
```

Then inspect any suspicious file before committing.
