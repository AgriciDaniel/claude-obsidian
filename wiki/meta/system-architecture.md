---
type: meta
title: "System Architecture"
tags: [meta, architecture]
created: 2026-04-18
updated: 2026-04-18
---

# How This Second Brain Works

A complete description of every moving part in this vault and how they connect.
Read this when onboarding a new agent, debugging unexpected behavior, or
planning extensions.

---

## Layers

```
┌──────────────────────────────────────────────────────────────┐
│ 1. OBSIDIAN — human read/write surface                       │
│    wiki/ is visible, engine folders hidden via CSS snippet   │
├──────────────────────────────────────────────────────────────┤
│ 2. CLAUDE CODE — conversational agent + skill runtime        │
│    Reads CLAUDE.md; loads skills/ and commands/ on demand     │
├──────────────────────────────────────────────────────────────┤
│ 3. KNOWLEDGE CAPTURE                                          │
│    inbox/  → inbox-classifier skill  → wiki/                  │
│    chat   → learn skill             → wiki/ + learn-queue     │
├──────────────────────────────────────────────────────────────┤
│ 4. EVOLUTION LAYER (OpenSpace-inspired)                       │
│    FIX / DERIVED / CAPTURED taxonomy                          │
│    .claude/skill-metrics.json  — quality tracking             │
│    .claude/learn-queue.json    — pending preference reviews   │
│    .claude/learn-rejects.log   — safety scan rejections       │
├──────────────────────────────────────────────────────────────┤
│ 5. OPENSPACE MCP (optional external brain)                    │
│    openspace-mcp server exposes execute_task / search_skills  │
│    Globally registered in ~/.claude.json for all projects     │
├──────────────────────────────────────────────────────────────┤
│ 6. VERSIONING                                                 │
│    PostToolUse auto-commit hook — every Write/Edit to wiki/   │
│    becomes a git commit, giving us a full DAG for free        │
└──────────────────────────────────────────────────────────────┘
```

---

## Directory Map

| Path | Purpose | Who writes |
|------|---------|-----------|
| `wiki/` | Public second brain — the thing you read | `learn`, `inbox-classifier`, you |
| `wiki/hot.md` | Last-~500-words context cache | `learn`, ingest skills |
| `wiki/log.md` | Append-only session log | Every filing operation |
| `wiki/meta/` | System-level docs (this file) | Maintenance ops |
| `inbox/` | Dump zone for raw thoughts | You |
| `.raw/` | Immutable source docs | You (ingest reads, never modifies) |
| `.raw/processed/` | Archived inbox notes after filing | `inbox-classifier` |
| `skills/` | Skill definitions (SKILL.md + references/) | Maintenance |
| `commands/` | Slash-command entry points | Maintenance |
| `bin/` | Shell scripts invoked by hooks | Maintenance |
| `hooks/` | Hook configuration (auto-commit etc.) | Maintenance |
| `.claude/settings.json` | SessionStart + Stop hooks | Maintenance |
| `.claude/learn-queue.json` | Pending preference reviews | `learn` skill |
| `.claude/skill-metrics.json` | Page-level quality metrics | `learn` skill |
| `.claude/learn-rejects.log` | Safety-rejected captures | `learn` skill |
| `_templates/` | Obsidian Templater templates | You |
| `_attachments/` | Images/PDFs | You |

---

## Skills

| Skill | Entry | Purpose |
|-------|-------|---------|
| `wiki` | `/wiki` | Scaffold new vault or check setup |
| `wiki-ingest` | "ingest [file]" | Classify a source doc from `.raw/` into wiki pages |
| `wiki-query` | "query: [question]" | Answer from wiki content |
| `wiki-lint` | "lint the wiki" | Health check (orphans, gaps) |
| `inbox-classifier` | "process my inbox" | Classify `inbox/*.md` into wiki sections |
| `learn` | `/learn`, `/reflect`, Stop hook | Distill conversations into wiki + queue prefs |
| `delegate-task` (global) | user MCP | Offload tasks to OpenSpace worker |
| `skill-discovery` (global) | user MCP | Search OpenSpace local + cloud skill library |

---

## Hooks

**`SessionStart`** (runs when you open Claude Code in this vault):
1. `bash bin/check-inbox.sh` — alerts if `inbox/` has unprocessed notes
2. `bash bin/learn-queue-check.sh` — alerts if preferences await review

**`Stop`** (runs when a Claude session ends gracefully):
1. Emits a reminder to run the `learn` skill before exiting

**`PostToolUse`** (project-level, in `hooks/hooks.json`):
1. Auto-commits any Write/Edit to `wiki/` — gives us the version DAG

---

## The Learning Loop (end-to-end)

```
┌─ Conversation happens ─────────────────────────────────────┐
│                                                             │
│   You say things. Claude helps.                             │
│                                                             │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼ session ends / you say /reflect
┌─ learn skill fires ────────────────────────────────────────┐
│                                                             │
│  1. Extract: walk transcript via 7 sweep categories         │
│     (facts, people, resources, learnings, journal,          │
│      preferences, decisions)                                │
│                                                             │
│  2. Classify by evolution type:                             │
│     FIX      — existing page needs correction               │
│     DERIVED  — extends an existing page                     │
│     CAPTURED — net-new                                      │
│                                                             │
│  3. Safety scan — reject content with keys/injection        │
│                                                             │
│  4. Anti-loop check — skip pages touched in last 60 min     │
│                                                             │
│  5. Route:                                                  │
│     Facts/projects/people/resources → direct write          │
│     Preferences → queue in .claude/learn-queue.json         │
│                                                             │
│  6. Update metrics — skill-metrics.json                     │
│                                                             │
│  7. Update wiki/log.md + wiki/hot.md                        │
│                                                             │
│  8. Report summary                                          │
│                                                             │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼ next session
┌─ SessionStart hook ────────────────────────────────────────┐
│                                                             │
│  "N preferences pending review — say 'review learnings'"    │
│                                                             │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼ you say "review learnings"
┌─ Queue walk-through ───────────────────────────────────────┐
│                                                             │
│  For each pending entry: approve / reject / edit            │
│  → approved prefs land in CLAUDE.md under                   │
│    "## Learned Preferences"                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## OpenSpace Integration

OpenSpace is a Python framework ([github.com/HKUDS/OpenSpace](https://github.com/HKUDS/OpenSpace))
providing **autonomous skill evolution** for agents. It's now globally
installed:

- **Binary:** `<python-scripts-dir>/openspace-mcp.exe` (or `openspace-mcp` on macOS/Linux)
- **Source:** clone of `github.com/HKUDS/OpenSpace` installed with `pip install -e .`
- **MCP registration:** `~/.claude.json` → `mcpServers.openspace`
- **Host skills:** `~/.claude/skills/delegate-task` + `~/.claude/skills/skill-discovery`

### What it adds

1. **`execute_task` tool** — delegate a complex multi-step task to OpenSpace's
   worker agent. It searches its local skill registry, executes, auto-evolves
   skills on failures.
2. **`search_skills` tool** — browse local + cloud skill library before
   handling a task yourself.
3. **`fix_skill` / `upload_skill` tools** — repair a broken skill; share a
   useful skill with the cloud community.

### When to use it

- Task needs tools beyond what Claude Code has directly (GUI automation, shell
  heavy work, bespoke MCP tools)
- You tried and failed — OpenSpace may have a tested skill for it
- Cross-project skill reuse — solve it once, reuse everywhere

### What we borrowed conceptually

Without running OpenSpace itself, our `learn` skill adopts its core ideas:

| OpenSpace concept | Our equivalent |
|-------------------|----------------|
| FIX / DERIVED / CAPTURED evolution taxonomy | Same names, applied to wiki pages |
| SkillQualityMetrics (applied/completion/fallback rate) | `.claude/skill-metrics.json` page-level metrics |
| Version DAG with parent_skill_ids | Git auto-commit history + `parent:` frontmatter for DERIVED |
| Safety gate (`check_skill_safety`) | Safety scan before write — rejects keys/injection |
| Anti-loop guard | 60-minute same-page cooldown |
| Post-execution analyzer trigger | `Stop` hook → `learn` skill |
| Metric monitor (periodic scan) | `/learn-health` command |
| Confirmation gates | Preference queue + user review |

---

## Failure Modes & Recovery

| Problem | Symptom | Fix |
|---------|---------|-----|
| `inbox/` stops showing notification | SessionStart runs but no output | Check `bin/check-inbox.sh` executable (`chmod +x`) |
| Preferences never reach CLAUDE.md | Queue fills but never drains | Say "review learnings" each session, or set a cron |
| Wiki pages get overwritten | FIX writes replaced instead of appended | Read `skill-metrics.json` — if `last_touched` is stale, evolution ran twice |
| OpenSpace MCP fails to start | Tools missing in `search_skills` | Check `openspace-mcp.exe` runs standalone; verify LLM creds in `.env` if using `execute_task` |
| Safety scan false-positive | Real content in `learn-rejects.log` | Lower scan strictness in `evolution-taxonomy.md` patterns |
| Auto-commit hook doesn't fire | Wiki changes not versioned | Verify `hooks/hooks.json` has PostToolUse entry, git repo initialized |

---

## Extending the System

To add a new **capture source** (e.g., email, voice memos):
1. Add a landing directory (like `inbox/`)
2. Write a classifier skill under `skills/` with a routing matrix
3. Add a SessionStart notifier script under `bin/`
4. Register the notifier in `.claude/settings.json`

To add a new **quality signal** (e.g., frequency of references):
1. Extend `skill-metrics.json` schema
2. Update `learn/SKILL.md` Step 7.5 to emit the signal
3. Update `commands/learn-health.md` to surface it

To **actually use OpenSpace** for a task:
1. Tell Claude "use OpenSpace to [task]"
2. Or invoke `execute_task` directly via the MCP
3. Evolved skills land under `OPENSPACE_HOST_SKILL_DIRS` (typically
   `~/.claude/skills`)

---

## References

- Inbox classifier: [skills/inbox-classifier/SKILL.md](../../skills/inbox-classifier/SKILL.md)
- Learn skill: [skills/learn/SKILL.md](../../skills/learn/SKILL.md)
- Evolution taxonomy: [skills/learn/references/evolution-taxonomy.md](../../skills/learn/references/evolution-taxonomy.md)
- Preference patterns: [skills/learn/references/preference-patterns.md](../../skills/learn/references/preference-patterns.md)
- OpenSpace paper/repo: [github.com/HKUDS/OpenSpace](https://github.com/HKUDS/OpenSpace)
