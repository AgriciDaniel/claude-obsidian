---
type: session
title: "claude-obsidian v1.4 Release Session"
created: 2026-04-08
updated: 2026-04-08
tags:
  - meta
  - session
  - release
  - audit-response
status: evergreen
related:
  - "[[claude-obsidian-ecosystem]]"
  - "[[cherry-picks]]"
  - "[[full-audit-and-system-setup-session]]"
  - "[[claude-obsidian-v1.2.0-release-session]]"
  - "[[LLM Wiki Pattern]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# claude-obsidian v1.4 Release Session

A complete release cycle covering v1.1, v1.4.0, and v1.4.1. Includes ecosystem research, external audit response, multi-agent compatibility rollout, full em-dash style cleanup, git history scrub for privacy, and a hotfix for the plugin install command syntax.

## Release Sequence

| Version | What shipped |
|---|---|
| v1.1 | URL ingestion, image/vision ingestion, delta tracking manifest, 3 new skills (defuddle, obsidian-bases, obsidian-markdown), multi-depth wiki-query modes, PostToolUse auto-commit hook, removal of invalid `allowed-tools` frontmatter field |
| v1.4.0 | Dataview to Bases migration, Canvas JSON 1.0 spec completeness, hooks hardening plus PostCompact, MCP setup hardened with Obsidian CLI option, custom callouts documented, 6 multi-agent bootstrap files, 249 em dashes scrubbed, security-rewrote git history to remove a placeholder email |
| v1.4.1 | Hotfix for the wrong plugin install command syntax in README and docs/install-guide.md |

## v1.1: First Feature Release of This Session

Shipped in response to an internal quality check against the wider ecosystem (16+ Claude plus Obsidian projects researched, filed in [[claude-obsidian-ecosystem]]). The highest-value features from competing implementations were cherry-picked and shipped as v1.1.

### New skills (Agent Skills spec compliant)

- `skills/defuddle/SKILL.md`: strips ads, nav, and clutter from web pages before URL ingestion. Saves 40 to 60 percent on tokens for typical articles.
- `skills/obsidian-markdown/SKILL.md`: full reference for Obsidian Flavored Markdown (wikilinks, embeds, all callout types, properties, math, Mermaid). Cross-references kepano/obsidian-skills as the authoritative source.
- `skills/obsidian-bases/SKILL.md`: native Obsidian Bases `.base` file syntax. Uses correct `filters/views/formulas` structure (NOT Dataview-style `from/where`). Rewritten mid-session after the first attempt used the wrong syntax.

### wiki-ingest upgrades

- **URL ingestion**: passes any `https://` URL directly. Uses WebFetch, optionally pipes through defuddle, saves to `.raw/articles/`, then runs the normal ingest pipeline.
- **Image/vision ingestion**: `.png`, `.jpg`, `.gif`, `.webp`, etc. Claude reads the image natively, extracts text via OCR and concepts via vision, saves the description to `.raw/images/`, then ingests.
- **Delta tracking**: `.raw/.manifest.json` tracks MD5 hash per source, timestamps, and the pages produced. Re-running ingest on unchanged files skips them automatically. Override with "force ingest".

### wiki-query multi-depth modes

Three query tiers:

- **Quick** (`query quick: ...`): hot.md plus index.md only. About 1,500 tokens. Best for fact lookups.
- **Standard** (default): hot plus index plus 3 to 5 relevant pages. About 3,000 tokens. Best for most questions.
- **Deep** (`query deep: ...`): full wiki cross-reference plus optional web search supplement. About 8,000+ tokens. Best for synthesis, comparisons, "tell me everything about X".

### Hook: PostToolUse auto-commit

Every `Write` or `Edit` tool call to `wiki/` or `.raw/` triggers `git add` and `git commit` automatically. Guarded by `[ -d .git ]` so it never errors in non-git directories, and by `git diff --cached --quiet` so it never creates empty commits. Matcher: `Write|Edit`.

### Critical fix: `allowed-tools` frontmatter removed

The Agent Skills spec only supports `name`, `description`, `argument-hint`, `compatibility`, `disable-model-invocation`, `license`, `metadata`, and `user-invokable` fields in SKILL.md frontmatter. The `allowed-tools` field was never valid and was being silently ignored. Removed from all 10 SKILL.md files to match the kepano/obsidian-skills authoritative convention.

## v1.4.0: External Audit Response

External auditor delivered a 21-source review (the "compass artifact") against Agent Skills spec, Claude Code hooks, Obsidian v1.9 through v1.12, and JSON Canvas 1.0. Initial audit score: 6.5/10. Many findings were already resolved in v1.1 (the audit was conducted against a snapshot from before that release). The remaining valid findings became v1.4.0. Full findings and prioritization are in [[cherry-picks]].

### Tier 1: Critical fixes

**Dataview to Bases migration** (the biggest correctness fix). Obsidian Bases shipped as a core plugin in v1.9.10 (August 2025), providing native database-like views that replace Dataview for most use cases. Created `wiki/meta/dashboard.base` with six views (Recent Activity, Seed Pages, Entities Missing Sources, Open Questions, Comparisons, Sources). Updated `wiki/meta/dashboard.md` to embed the new base file as primary and keep the legacy Dataview queries as optional fallback. Reorganized README plugins section to recommend Bases (core, no install needed) as primary and mark Dataview as optional/legacy.

**Canvas JSON 1.0 spec completeness**. Added previously missing fields to `skills/canvas/references/canvas-spec.md`:
- Group nodes: `background` (string path) and `backgroundStyle` (`cover`, `ratio`, `repeat`)
- Edges: `fromEnd` (defaults to `"none"`) and `toEnd` (defaults to `"arrow"`). Asymmetric defaults that produce a single arrow without explicit specification.
- Documented the official hex ID convention alongside the descriptive ID alternative.

### Tier 2: Important improvements

**Hooks hardening plus PostCompact**. `hooks/hooks.json` updated:

- SessionStart now uses both `command` and `prompt` types. The command runs `[ -f wiki/hot.md ] && cat wiki/hot.md || true` as the canonical safety check that works in non-vault sessions without erroring. Matcher: `startup|resume`.
- **NEW PostCompact hook** re-injects `wiki/hot.md` after context compaction. Critical insight: hook-injected context does NOT survive compaction, only `CLAUDE.md` does. Without this hook the hot cache disappears mid-session after any compact event.
- PostToolUse auto-commit now guarded by `[ -d .git ]` in addition to the existing safeguards.
- New `hooks/README.md` documents all four hooks plus the known plugin-hooks STDOUT bug (`anthropics/claude-code#10875`) and workarounds.

**MCP setup hardened**. `skills/wiki/references/mcp-setup.md` now has a `> [!warning]` callout above the `NODE_TLS_REJECT_UNAUTHORIZED: "0"` line explaining that it disables TLS verification process-wide (acceptable for `127.0.0.1` only). Added **Option D: Obsidian CLI** (Obsidian v1.12+) as the recommended alternative that avoids the TLS workaround entirely by using the native CLI via the Bash tool.

**Custom callouts documented**. The vault defines four custom callout types in `.obsidian/snippets/vault-colors.css`:

| Callout | Color | Icon | Use for |
|---|---|---|---|
| `contradiction` | reddish-brown | `lucide-alert-triangle` | New source conflicts with existing claim |
| `gap` | beige | `lucide-help-circle` | Topic has no source yet |
| `key-insight` | bright blue | `lucide-lightbulb` | Important takeaway worth highlighting |
| `stale` | gray | `lucide-clock` | Claim may be outdated |

Full documentation added to `skills/wiki/references/css-snippets.md` including built-in fallback equivalents for users who do not want the custom CSS. `skills/wiki-ingest/SKILL.md` got an explicit note that `[!contradiction]` depends on the CSS snippet.

### Tier 3: Multi-agent compatibility (low complexity, high reach)

Skills are already in the cross-platform Agent Skills format. The only thing missing was adapter files so other AI coding agents could discover them. Added:

| File | For |
|---|---|
| `AGENTS.md` | Codex CLI, OpenCode |
| `GEMINI.md` | Gemini CLI, Antigravity |
| `.cursor/rules/claude-obsidian.mdc` | Cursor (always-on rules) |
| `.windsurf/rules/claude-obsidian.md` | Windsurf Cascade |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `bin/setup-multi-agent.sh` | Idempotent symlink installer that wires up `skills/` into each agent's expected location |

This turns claude-obsidian into a multi-agent plugin at near-zero compatibility cost. Pattern borrowed from [[Ar9av-obsidian-wiki]] which was the reference implementation for multi-agent support.

## Style Cleanup: Em Dash Scrub

Per user preference saved to feedback memory: never use em dashes (U+2014) or `--` as punctuation. Use periods, commas, colons, or parentheses instead. Hyphens in compound words (auto-commit, multi-agent) are fine.

Wrote a context-aware Python scrubber at `/tmp/scrub_em_dashes.py` with rules:

- Heading lines (`^#`): em dash becomes `:`
- List items (`^-`, `^|`): em dash becomes `:` (for label-description patterns)
- Prose: em dash becomes `.` with next word capitalized

**Result**: 249 em dashes removed across 26 files. Scrubbed every SKILL.md, every doc, every hook file, every bootstrap file, and marketplace.json. Manual smoothing required for:

- `skills/obsidian-markdown/SKILL.md`: 4 code-block annotation tables where the scrubber produced broken fragments. Converted to proper markdown tables.
- `skills/wiki-query/SKILL.md`: 4 "If X. Respond." fragments rewritten as "If X, respond."
- `bin/setup-multi-agent.sh`: 1 leftover em dash at end-of-line that the scrubber missed (only matched space-em-space). Plus one awkward echo string fixed.

The user-facing feedback was clear: "make it proper and natural". The scrubbed prose reads cleaner with the fragmented sentences smoothed out.

## Security: Email Removal and Git History Rewrite

A placeholder email `[scrubbed-email]` (which the user confirmed does not exist as a real address) was in `marketplace.json` plus two docs. Removed from working tree first, then rewrote git history to scrub it from all commits.

**Tool**: `git filter-repo` (available at `~/.pyenv/versions/3.12.4/bin/git-filter-repo`).

**Two passes required**:

1. `git filter-repo --replace-text /tmp/email-replacements.txt --force` scrubs blob contents across all commits.
2. `git filter-repo --replace-message /tmp/email-msg-replacements.txt --force` scrubs commit messages. The first pass caught 3 occurrences in file contents but missed 1 occurrence in a commit subject line. The second pass caught that.

**Replacement string**: `[scrubbed-email]==>***REMOVED***`

**Post-rewrite actions**:
- Re-added the `origin` remote that filter-repo removes for safety
- Moved `v1.4.0` tag forward to include the security commit (since v1.4.0 had not been consumed yet by any user)
- Force-pushed main plus both tags (`v1.1` and `v1.4.0`)
- Updated the v1.4.0 GitHub release notes to include a "Security Note" section

**Verification**: grep across all refs, all blobs, all commit messages returned zero matches for the scrubbed email string. GitHub release bodies checked for same: both v1.1 and v1.4.0 release pages clean.

**Caveat for other clones**: history rewrite means every commit hash changed. Any other machine or private `community` remote at `avalonreset-pro/claude-obsidian` that has the repo still contains the old history. Those need `git fetch && git reset --hard origin/main` or a force push to clean up.

## v1.4.1: Plugin Install Command Hotfix

The v1.4.0 README and install guide showed this install command:

```bash
claude plugin install github:AgriciDaniel/claude-obsidian
```

This form does not exist in Claude Code. Users trying it see:

```
Failed to install plugin "github:AgriciDaniel/claude-obsidian": Plugin "github:AgriciDaniel/claude-obsidian" not found in any configured marketplace
```

### The correct install flow (per `code.claude.com/docs/en/plugin-marketplaces`)

Plugin installation is a **two-step** process:

```bash
# Step 1: add the marketplace catalog
claude plugin marketplace add AgriciDaniel/claude-obsidian

# Step 2: install the plugin from the catalog by name
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

Where `claude-obsidian` is the plugin name (from `plugin.json`) and `claude-obsidian-marketplace` is the marketplace name (from `marketplace.json`). The `@` delimiter separates them.

### Why the confusion existed

There is no `claude plugin install github:owner/repo` shortcut. The marketplace abstraction is mandatory: Claude Code always fetches via a registered marketplace. A single-repo plugin like claude-obsidian is both the marketplace host and the plugin host, and the user must register the marketplace first before installing any plugin from it.

### Related CLI commands (useful to know)

| Command | What it does |
|---|---|
| `claude plugin marketplace list` | Show all registered marketplaces |
| `claude plugin marketplace add owner/repo` | Register a new marketplace from a GitHub repo |
| `claude plugin marketplace update <name>` | Refresh the marketplace catalog and re-clone |
| `claude plugin marketplace remove <name>` | Unregister a marketplace (also uninstalls its plugins) |
| `claude plugin install <plugin>@<marketplace>` | Install a specific plugin |
| `claude plugin list` | Show all installed plugins and their status |
| `claude plugin validate .` | Validate a marketplace.json, plugin.json, and frontmatter |

### Files changed in v1.4.1

- `README.md`: Option 2 install section rewritten with two-step flow
- `docs/install-guide.md`: same correction
- `.claude-plugin/plugin.json`: 1.4.0 to 1.4.1
- `.claude-plugin/marketplace.json`: both `metadata.version` and `plugins[0].version` bumped to 1.4.1

### Confirmed working

After v1.4.1 was published, the user ran the corrected commands and saw:

```
claude-obsidian@claude-obsidian-marketplace
  Version: 1.4.1
  Scope: user
  Status: ✔ enabled
```

v1.4.1 installed at user scope and enabled.

## Key Lessons (Worth Remembering)

1. **Plugin install is always two-step**. There is no github shorthand form. `marketplace add` then `install plugin@marketplace`.
2. **`allowed-tools` is not a valid skill frontmatter field**. The Agent Skills spec only accepts `name`, `description`, `argument-hint`, `compatibility`, `disable-model-invocation`, `license`, `metadata`, `user-invokable`. kepano/obsidian-skills uses only `name` and `description` which is the gold standard convention.
3. **Obsidian Bases uses `filters/views/formulas`, not Dataview-style `from/where`**. Easy to confuse. Always check `help.obsidian.md/bases/syntax` for the current syntax.
4. **Canvas JSON 1.0 has asymmetric edge defaults**. `fromEnd` defaults to `"none"`, `toEnd` defaults to `"arrow"`. Omitting both produces a single arrow pointing from source to target.
5. **Hook-injected context does not survive context compaction**. Only `CLAUDE.md` does. Any plugin that injects context via SessionStart hooks should also add a PostCompact hook to restore it mid-session.
6. **`git filter-repo` needs two passes for full scrub**. `--replace-text` handles blob contents, `--replace-message` handles commit messages. Running only one leaves traces.
7. **`git filter-repo` removes the `origin` remote for safety**. Must re-add it manually before force-pushing.
8. **Marketplace name and plugin name can differ**. Our marketplace is `claude-obsidian-marketplace`, our plugin is `claude-obsidian`. The `@` delimiter disambiguates them.
9. **Style preference: no em dashes anywhere**. Periods, commas, colons, or parentheses instead. Applies to all prose, commit messages, release notes, file content. Hyphens in compound words are fine.

## Files Created in This Session

Summary of everything new or newly created:

| Path | Type | Purpose |
|---|---|---|
| `skills/defuddle/SKILL.md` | skill | Web page cleaner |
| `skills/obsidian-bases/SKILL.md` | skill | Obsidian Bases syntax |
| `skills/obsidian-markdown/SKILL.md` | skill | Full Obsidian syntax reference |
| `wiki/meta/dashboard.base` | bases dashboard | 6-view Bases dashboard |
| `wiki/comparisons/claude-obsidian-ecosystem.md` | comparison | 16+ project feature matrix |
| `wiki/concepts/cherry-picks.md` | concept | Prioritized feature backlog |
| `wiki/sources/claude-obsidian-ecosystem-research.md` | source | Research summary |
| `wiki/entities/Ar9av-obsidian-wiki.md` | entity | Multi-agent reference implementation |
| `wiki/entities/Nexus-claudesidian-mcp.md` | entity | Native Obsidian plugin |
| `wiki/entities/ballred-obsidian-claude-pkm.md` | entity | Goal cascade PKM |
| `wiki/entities/rvk7895-llm-knowledge-bases.md` | entity | Multi-depth query reference |
| `wiki/entities/kepano-obsidian-skills.md` | entity | Authoritative skill reference |
| `wiki/entities/Claudian-YishenTu.md` | entity | Native Obsidian plugin |
| `.raw/claude-obsidian-ecosystem-research.md` | raw source | Ecosystem research dump |
| `hooks/README.md` | doc | Hook documentation |
| `AGENTS.md` | bootstrap | Codex CLI / OpenCode |
| `GEMINI.md` | bootstrap | Gemini CLI / Antigravity |
| `.cursor/rules/claude-obsidian.mdc` | bootstrap | Cursor rules |
| `.windsurf/rules/claude-obsidian.md` | bootstrap | Windsurf Cascade |
| `.github/copilot-instructions.md` | bootstrap | GitHub Copilot |
| `bin/setup-multi-agent.sh` | script | Multi-agent symlink installer |

## Current Plugin State

- **Plugin installed**: `claude-obsidian@claude-obsidian-marketplace` version `1.4.1`, user scope, enabled
- **Releases on GitHub**: `v1.1`, `v1.4.0`, `v1.4.1`
- **10 skills** in `skills/`: wiki, wiki-ingest, wiki-query, wiki-lint, save, autoresearch, canvas, defuddle, obsidian-bases, obsidian-markdown
- **4 lifecycle hooks** in `hooks/hooks.json`: SessionStart, PostCompact, PostToolUse, Stop
- **6 multi-agent bootstrap files** covering Codex, OpenCode, Gemini, Cursor, Windsurf, GitHub Copilot
- **2 agents** in `agents/`: wiki-ingest, wiki-lint

## Deferred to v1.5.0

From the audit cherry-picks list, these items were identified but intentionally not included in v1.4.0:

- `/adopt` command for importing existing vaults (medium complexity, adds new surface)
- Vault graph analysis enhancement to wiki-lint (hub pages, cross-domain bridges, dead-ends)
- Semantic search via qmd MCP server (optional external dependency)
- Marp slide output from wiki queries (niche)
- Thinking mode vs Writing mode UX experiment
