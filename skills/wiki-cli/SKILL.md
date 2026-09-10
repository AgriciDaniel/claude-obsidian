---
name: wiki-cli
description: "Detect and use the official Obsidian command-line interface for read-only vault access; use for wiki-cli, Obsidian CLI, Obsidian read, Obsidian search, vault transport, which transport, transport detection, backlinks, tags, or Obsidian command line. Mutations always go through the claude-obsidian transaction core."
---

# Obsidian CLI read transport

Use this skill only to detect transport and read or search a selected vault.
The official executable is `obsidian`; binary presence alone does not prove it
is usable.

Resolve the installed product root from this skill's own location, not from the
vault or current working directory:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
DETECT_TRANSPORT="$PRODUCT_ROOT/scripts/detect-transport.sh"
test -f "$DETECT_TRANSPORT"
```

Every `../wiki/references/` link in this file resolves the same way, relative
to this skill's own directory under `$PRODUCT_ROOT`, never relative to the
selected vault's `wiki/` directory.

## Detect safely

Probe without persisting host state:

```bash
bash "$DETECT_TRANSPORT" --peek --vault "$VAULT"
```

Trust `available.cli.usable`, not merely `present` or exit status. A supported
CLI can still be unavailable because the Obsidian app is not running, command
line access is disabled, or its response is an error. Use filesystem reads as
the portable fallback.

Persist a refreshed `.vault-meta/transport.json` only when the user or setup
workflow asks for a transport snapshot:

```bash
bash "$DETECT_TRANSPORT" --force --vault "$VAULT"
```

That file is derived runtime configuration, not knowledge content. Preserve a
valid `manual_override` recorded by the detector.

## Read and search

Run official CLI commands from the selected vault so Obsidian resolves the
correct workspace. Confirm supported syntax with the installed CLI before
relying on optional commands. Typical read-only forms are:

```bash
(cd "$VAULT" && obsidian read path="$NOTE")
(cd "$VAULT" && obsidian search query="$QUERY")
```

Use read-only commands for backlinks, tags, or Bases results only when the
detector reports the CLI ready. Otherwise read files under `$VAULT` directly
and use `rg` for search. Reject absolute note arguments, traversal, symlinks, or
resolved paths outside the selected vault.

## Mutation boundary

Do not use CLI create, write, append, property-set, daily-append, move, rename,
or delete commands. Do not replace those commands with direct filesystem
writes. Any knowledge or configuration change must be expressed as one
reviewed transaction through the portable core; see
[operation transactions](../wiki/references/operation-transactions.md).

Transport choice never changes mutation semantics. The CLI is an optional read
surface, not a lock manager, transaction engine, or Git checkpoint mechanism.

## Checkpoint

Observe actual capability, think about the least complex read transport, verify
that every resolved path stays in the vault, and accept filesystem fallback
when the CLI is not ready.
