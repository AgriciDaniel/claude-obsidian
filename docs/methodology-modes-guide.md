# Methodology modes

Methodology mode is a vault-local routing preference for new notes. It does not
change evidence rules, transaction safety, or existing files.

## Modes

| Mode | Principle | Typical routes |
|---|---|---|
| Generic | Familiar typed folders without a named methodology | `wiki/sources/`, `entities/`, `concepts/`, `sessions/` |
| LYT | Maps of Content connect atomic notes | `wiki/mocs/`, `wiki/notes/` |
| PARA | Organize by current actionability | `wiki/projects/`, `areas/`, `resources/`, `archives/` |
| Zettelkasten | Stable IDs, atomic notes, dense links | Flat `wiki/<id>-<slug>.md` |

Absent configuration means Generic. Choose based on retrieval and maintenance
habits, not prestige:

- Use Generic when types are enough and migration cost should stay low.
- Use LYT when curated maps are the primary navigation surface.
- Use PARA when project/action status should control filing.
- Use Zettelkasten when atomicity and dense linking are practiced consistently.

## Read the current mode

```bash
python3 scripts/claude-obsidian.py mode get --vault <vault>
```

The compatibility router can preview a destination without writing:

```bash
python3 scripts/wiki-mode.py --vault <vault> route concept "Example concept" --mode lyt
```

Treat router output as a proposal. Validate it as a vault-relative path and
include the chosen path in the operation preview.

## Configure safely

Mode changes use one configuration transaction and default to dry-run:

```bash
python3 scripts/claude-obsidian.py mode set para --vault <vault> \
  --generated-at <ISO-UTC> --operation-id mode-reviewed
python3 scripts/claude-obsidian.py mode set para --vault <vault> \
  --generated-at <ISO-UTC> --operation-id mode-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

The compatibility wrapper has the same behavior:

```bash
bash scripts/setup-mode.sh --vault <vault> --mode para
bash scripts/setup-mode.sh --vault <vault> --mode para \
  --generated-at <ISO-UTC> --approved-plan-sha256 <reviewed-sha256> --apply
```

Existing custom route settings are preserved. The command does not create
folders, move notes, rewrite links, or migrate old content.

The Zettelkasten allocator has one canonical format:
`YYYYMMDDHHMMSSffffff-UUID4HEX`. A legacy timestamp-only `id_format` is
normalized in read output and in the next reviewed `mode set` transaction;
existing filenames are not renamed. Routed filename components are bounded to
255 UTF-8 bytes with a deterministic hash suffix when a title must be shortened.

## Switching modes

Switching affects only later routing. Before changing:

1. identify which workflows consume routes;
2. preview representative source, entity, concept, session, and research names;
3. check for filename or basename collisions;
4. apply the configuration transaction;
5. run the deterministic linter after the first operation in the new mode.

Bulk reorganization is a separate migration project. It needs a complete move
map, link rewrite plan, expected hashes, collision handling, rollback, and
explicit user approval. Never make it a side effect of `mode set`.

## How skills consume mode

`wiki-ingest`, `save`, and `autoresearch` may call the router while drafting.
Workers include the proposed route in their draft packet; the parent
orchestrator decides and applies the final path. Query, lint, and retrieval do
not change behavior based on methodology mode.

Mode is organizational metadata, not evidence. A note's folder does not raise
its authority, freshness, or confidence.

## Troubleshooting

| Symptom | Response |
|---|---|
| Missing config | Generic is active; nothing is broken. |
| Invalid JSON | Repair or replace it through a reviewed transaction; the router fails safely. |
| Unexpected route | Preview with an explicit `--mode`, inspect custom settings, and sanitize the name. |
| Mixed old/new layout | Expected after switching; do not auto-move older notes. |
| Zettelkasten ID concern | New IDs combine a sortable UTC microsecond prefix with a UUIDv4 nonce. Existing timestamp-only IDs remain valid; still detect target collisions before apply. |
