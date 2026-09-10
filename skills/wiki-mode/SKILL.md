---
name: wiki-mode
description: "Read or configure the vault filing methodology and suggest destinations for planned knowledge creation under Generic, LYT, PARA, or Zettelkasten. Use for wiki mode, methodology mode, what is my vault mode, set vault mode, switch to PARA, use LYT, Zettelkasten setup, change mode, configure mode, or methodology routing. This skill does not save content or migrate notes."
---

# Route by vault methodology

This skill returns filing suggestions. It does not write knowledge pages or
move existing notes. If `.vault-meta/mode.json` is absent, use `generic`. If
the file exists but is invalid, fail closed and repair it through a reviewed
configuration operation before suggesting routes; never silently substitute
Generic for corrupt user configuration.

Resolve the installed product root from this skill's own location, not from the
vault or current working directory:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
MODE_HELPER="$PRODUCT_ROOT/scripts/wiki-mode.py"
test -f "$CORE" && test -f "$MODE_HELPER"
```

Every `../wiki/references/` link in this file resolves the same way, relative
to this skill's own directory under `$PRODUCT_ROOT`, never relative to the
selected vault's `wiki/` directory.

## Read and route safely

Always select the vault explicitly:

```bash
python3 "$MODE_HELPER" --vault "$VAULT" get
python3 "$MODE_HELPER" --vault "$VAULT" config
python3 "$MODE_HELPER" --vault "$VAULT" route concept "Concept name"
python3 "$MODE_HELPER" --vault "$VAULT" route source "Source title"
```

The helper validates the selected vault, confines paths, sanitizes names, and
prints a suggestion only. A calling skill may override the suggestion when the
user supplies a more specific project, area, MOC, or parent note, but it must
still apply its eventual writes through one operation transaction.

| Mode | Routing intent |
|---|---|
| `generic` | Type-based folders such as sources, entities, concepts, and sessions. |
| `lyt` | Atomic notes under `wiki/notes/`, connected through MOCs. |
| `para` | Projects, Areas, Resources, or Archives chosen by actionability. |
| `zettelkasten` | Flat atomic notes with time-sortable, collision-resistant identifiers and explicit links. |

Use the templates under `templates/` as structural guidance, not authority to
overwrite user conventions.

## Change mode

A mode change is one configuration operation, dry-run first:

1. Read the current `.vault-meta/mode.json`, or start from the helper's default
   config when it is absent.
2. Validate the requested mode as exactly `generic`, `lyt`, `para`, or
   `zettelkasten`. Preserve the other mode-specific settings.
3. Choose and retain a pinned UTC timestamp and operation ID for both commands.
4. Preview the canonical configuration transaction; the command records the
   current target hash and limits the write to `.vault-meta/mode.json`:

   ```bash
   python3 "$CORE" mode set "$MODE" --vault "$VAULT" \
     --generated-at "$GENERATED_AT" --operation-id "$OPERATION_ID"
   ```

5. Show the old mode, new mode, exact changed path, and complete preview. Copy
   its `approved_plan_sha256` only after review.
6. Apply by regenerating that exact vault-bound plan:

   ```bash
   python3 "$CORE" mode set "$MODE" --vault "$VAULT" \
     --generated-at "$GENERATED_AT" --operation-id "$OPERATION_ID" \
     --approved-plan-sha256 "$APPROVAL_SHA256" --apply
   ```

Follow the [operation transaction contract](../wiki/references/operation-transactions.md).
Do not use `scripts/wiki-mode.py`'s legacy direct-write `set` action or a setup
script to bypass this workflow.

Changing mode affects routing for future operations only. Never bulk-create
folders, move notes, rewrite wikilinks, or migrate existing pages as a side
effect. If migration is later requested, plan and review it as a distinct
operation with its own hashes and transaction.

## Checkpoint

Observe the user's current structure, think about how they retrieve and act on
notes, verify a few proposed routes before changing configuration, and grow by
revisiting the mode only when real filing friction appears.
