---
name: hot-sync
description: >
  Regenerate wiki/hot.md from ground truth (git, plugin version, skill count,
  domains, log headers). Preserves the Active Threads block. Use when the hot
  cache is stale or after a session that changed vault state.
  Triggers on: /hot-sync, /hot, "refresh hot cache", "regenerate hot.md",
  "hot sync", "sync hot".
---

# hot-sync: Deterministic Hot Cache Refresh

`wiki/hot.md` is injected at every session start. Soft LLM prompts to update it
fail. This skill runs a script that rewrites Ground Truth from the repo and
leaves Active Threads alone.

## Workflow

1. Confirm you are in a vault root (directory containing `wiki/`), or resolve
   `vault:` from `.claude/CLAUDE.md` / `CLAUDE.md` if present.
2. Run:
   ```bash
   bash scripts/hot-sync.sh
   ```
   From another vault root:
   ```bash
   bash /path/to/vault-os/scripts/hot-sync.sh /path/to/vault
   ```
3. Optionally edit the Active Threads block between
   `<!-- ACTIVE-THREADS:START -->` and `<!-- ACTIVE-THREADS:END -->` with a few
   short bullets (current work, do-not-push notes). Do not edit Ground Truth.
4. Report the script's one-line summary to the user.

## Output

- Overwrites `wiki/hot.md`
- Preserves Active Threads markers and content
- Does not touch `wiki/log.md`, `wiki/index.md`, or `.raw/`

## Constraints

- Prefer the script. Do not freehand-rewrite the whole hot cache.
- Do not append session diaries. Ground Truth is regenerated; Active Threads
  stay short (a handful of bullets).
- No network. No LLM calls inside the script path.
- After meaningful wiki work, run hot-sync (or rely on SessionStart wiring)
  instead of the old Stop-hook "please update hot.md" prompt.
