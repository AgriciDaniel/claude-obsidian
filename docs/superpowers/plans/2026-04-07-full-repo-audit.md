# claude-obsidian Full Repo Audit Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Comprehensive read-only audit of every layer of the claude-obsidian repo — plugin manifest, skills, commands, agents, hooks, Obsidian vault config, wiki content, README, install guide, and git hygiene. No changes. Report findings only.

**Architecture:** 12 parallel audit areas, each checked independently. Findings consolidated into a single AUDIT-REPORT.md at the end. Every check is either PASS, WARN (works but suboptimal), or FAIL (broken/incorrect).

**Tech Stack:** bash, python3 (json validation), grep, git, manual file reading

---

## Audit Areas Overview

```
Area 1  — Git health & .gitignore effectiveness
Area 2  — Plugin manifests (plugin.json + marketplace.json)
Area 3  — Skill files (7× SKILL.md + references/)
Area 4  — Command files (4× commands/*.md)
Area 5  — Agent files (2× agents/*.md)
Area 6  — Hooks (hooks/hooks.json)
Area 7  — Obsidian vault config (.obsidian/*.json)
Area 8  — Obsidian plugin files (4 plugins)
Area 9  — CSS snippets (3 files)
Area 10 — Wiki content (all .md pages + canvases)
Area 11 — Documentation accuracy (README, WIKI.md, CLAUDE.md, install-guide.md, setup-vault.sh)
Area 12 — Cross-file consistency + security
```

---

## Task 1: Git Health & .gitignore Effectiveness

**Files to read:** `.gitignore`, output of `git status`, `git ls-files`, `git remote -v`, `git fsck`

- [ ] **Step 1: Check working tree and remotes**

```bash
cd /home/agricidaniel/claude-obsidian
git status
git remote -v
git fsck --quiet 2>&1
```

Expected: clean working tree, origin=AgriciDaniel/claude-obsidian, community=avalonreset-pro/claude-obsidian, no fsck errors.

- [ ] **Step 2: Verify .gitignore is actually blocking personal files on disk**

```bash
cd /home/agricidaniel/claude-obsidian
git check-ignore -v \
  "2026-04-07 14-19-00.mkv" \
  "Claude SEO Posts cover 1.gif" \
  "Cosmic Brain Clean.gif" \
  "Cosmic Brain Cover.png" \
  "cosmic code.png" \
  "PROMPT.md" \
  "WIKI 1.md" \
  "Welcome.md" \
  "Untitled.canvas" \
  "Untitled 1.canvas" \
  "Demo Images.canvas" \
  "Banana Images.canvas" \
  "Untitled.base" \
  "Excalidraw/" \
  "_attachments/code-genesis.png" \
  "_attachments/neural-voyager.png" \
  "_attachments/the-frontier.png" 2>&1
```

Expected: every file returns a matching .gitignore rule. FAIL if any file is NOT ignored.

- [ ] **Step 3: Confirm no personal files are accidentally tracked**

```bash
cd /home/agricidaniel/claude-obsidian
git ls-files | grep -E "(skool-hub|Claude SEO|Cosmic Brain|cosmic code|Nate|PROMPT|Untitled|Banana|Demo Images|\.mkv|\.mp4|\.mov)"
```

Expected: zero output. FAIL if any match.

- [ ] **Step 4: Check Excalidraw main.js and data.json are NOT tracked**

```bash
cd /home/agricidaniel/claude-obsidian
git ls-files .obsidian/plugins/obsidian-excalidraw-plugin/
```

Expected: only `manifest.json` and `styles.css`. FAIL if `main.js` or `data.json` appear.

- [ ] **Step 5: Confirm total tracked file count is reasonable**

```bash
cd /home/agricidaniel/claude-obsidian
git ls-files | wc -l
git ls-files
```

Expected: ~94 files. Review list for anything unexpected.

---

## Task 2: Plugin Manifest Audit

**Files to read:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] **Step 1: Validate plugin.json**

```bash
python3 -c "import json; d=json.load(open('/home/agricidaniel/claude-obsidian/.claude-plugin/plugin.json')); print(json.dumps(d, indent=2))"
```

Check every field:
- `name` = `"claude-obsidian"` (exact, kebab-case, no spaces)
- `version` = `"1.2.0"`
- `description` — present, accurate, no "cosmic-brain" references
- `author.name` = `"AgriciDaniel"`
- `author.url` — valid GitHub URL
- `license` = `"MIT"`
- `homepage` — points to AgriciDaniel/claude-obsidian
- `repository` — points to AgriciDaniel/claude-obsidian
- `keywords` — array of relevant strings

- [ ] **Step 2: Validate marketplace.json**

```bash
python3 -c "import json; d=json.load(open('/home/agricidaniel/claude-obsidian/.claude-plugin/marketplace.json')); print(json.dumps(d, indent=2))"
```

Check:
- `owner.name` = `"AgriciDaniel"`
- `owner.url` = `"https://github.com/AgriciDaniel"` (no email field)
- `metadata.version` = `"1.2.0"`
- `plugins[0].name` = `"claude-obsidian"`
- `plugins[0].source.repo` = `"AgriciDaniel/claude-obsidian"`
- `plugins[0].version` = `"1.2.0"`
- `plugins[0].homepage` and `repository` both point to correct repo

- [ ] **Step 3: Version consistency across all files**

```bash
grep -r "\"version\"" /home/agricidaniel/claude-obsidian/.claude-plugin/ | grep -v ".git"
grep "version" /home/agricidaniel/claude-obsidian/README.md | head -5
grep "version" /home/agricidaniel/claude-obsidian/docs/install-guide.md | head -5
```

Expected: all version references say `1.2.0`.

---

## Task 3: Skill Files Audit

**Files:** `skills/wiki/SKILL.md`, `skills/wiki-ingest/SKILL.md`, `skills/wiki-query/SKILL.md`, `skills/wiki-lint/SKILL.md`, `skills/save/SKILL.md`, `skills/autoresearch/SKILL.md`, `skills/canvas/SKILL.md`

For **each** SKILL.md file, check:

### 3a. Frontmatter validity

- [ ] **Step 1: Read and validate all SKILL.md frontmatter**

```bash
for f in /home/agricidaniel/claude-obsidian/skills/*/SKILL.md; do
  echo "=== $f ==="
  python3 -c "
import sys
content = open('$f').read()
if not content.startswith('---'):
    print('FAIL: no frontmatter')
    sys.exit(1)
end = content.index('---', 3)
print(content[:end+3])
"
done
```

For each file, verify:
- `name:` field present and matches folder name
- `description:` field present, single line, triggers correctly describe when to use the skill
- `allowed-tools:` field present and is a valid YAML list
- No broken YAML (colons in values must be quoted)

### 3b. Tool list accuracy

- [ ] **Step 2: Check tool lists are reasonable for each skill**

Read each SKILL.md and verify `allowed-tools` lists only real Claude Code tools: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `Agent`, `TodoWrite`, `WebFetch`, `WebSearch`.

Flag any tool listed that doesn't exist in Claude Code.

### 3c. Instruction completeness

- [ ] **Step 3: Read the body of each SKILL.md**

```bash
cat /home/agricidaniel/claude-obsidian/skills/wiki/SKILL.md
cat /home/agricidaniel/claude-obsidian/skills/wiki-ingest/SKILL.md
cat /home/agricidaniel/claude-obsidian/skills/wiki-query/SKILL.md
cat /home/agricidaniel/claude-obsidian/skills/wiki-lint/SKILL.md
cat /home/agricidaniel/claude-obsidian/skills/save/SKILL.md
cat /home/agricidaniel/claude-obsidian/skills/autoresearch/SKILL.md
cat /home/agricidaniel/claude-obsidian/skills/canvas/SKILL.md
```

For each, check:
- Does the body give Claude enough instruction to actually perform the operation?
- Are file paths referenced correct? (e.g. `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`)
- Are any paths still referencing `cosmic-brain`?
- Are referenced `references/` files present on disk?
- Does `skills/wiki/SKILL.md` have a routing table covering all 7 operations?
- Does `skills/canvas/SKILL.md` reference `canvas-spec.md`?
- Does `skills/autoresearch/SKILL.md` reference `program.md`?

### 3d. Reference files

- [ ] **Step 4: Verify all reference files exist and are accurate**

```bash
cat /home/agricidaniel/claude-obsidian/skills/wiki/references/plugins.md
cat /home/agricidaniel/claude-obsidian/skills/wiki/references/css-snippets.md
cat /home/agricidaniel/claude-obsidian/skills/wiki/references/mcp-setup.md
cat /home/agricidaniel/claude-obsidian/skills/wiki/references/frontmatter.md
cat /home/agricidaniel/claude-obsidian/skills/wiki/references/modes.md
cat /home/agricidaniel/claude-obsidian/skills/wiki/references/git-setup.md
cat /home/agricidaniel/claude-obsidian/skills/wiki/references/rest-api.md
cat /home/agricidaniel/claude-obsidian/skills/canvas/references/canvas-spec.md
cat /home/agricidaniel/claude-obsidian/skills/autoresearch/references/program.md
```

Check each for:
- No `cosmic-brain` or `Nate Herk` references
- Plugin names match actual installed plugins (calendar, thino, excalidraw, banners)
- CSS snippet names match actual files in `.obsidian/snippets/`
- Any hardcoded paths still valid

---

## Task 4: Command Files Audit

**Files:** `commands/wiki.md`, `commands/save.md`, `commands/autoresearch.md`, `commands/canvas.md`

- [ ] **Step 1: Read all command files**

```bash
cat /home/agricidaniel/claude-obsidian/commands/wiki.md
cat /home/agricidaniel/claude-obsidian/commands/save.md
cat /home/agricidaniel/claude-obsidian/commands/autoresearch.md
cat /home/agricidaniel/claude-obsidian/commands/canvas.md
```

For each command file, check:
- Has YAML frontmatter with `description:` field
- Description accurately describes what the command does
- If it references a skill, does that skill exist? (`/wiki` → `skills/wiki/SKILL.md` etc.)
- No `cosmic-brain` references
- Commands match what README says they do (cross-check against README commands table)

---

## Task 5: Agent Files Audit

**Files:** `agents/wiki-ingest.md`, `agents/wiki-lint.md`

- [ ] **Step 1: Read both agent files**

```bash
cat /home/agricidaniel/claude-obsidian/agents/wiki-ingest.md
cat /home/agricidaniel/claude-obsidian/agents/wiki-lint.md
```

Check:
- YAML frontmatter present with `description:`
- Description accurately describes when Claude Code should invoke this agent
- Instructions match what the corresponding skill (`wiki-ingest`, `wiki-lint`) does
- File paths referenced in instructions are valid

---

## Task 6: Hooks Audit

**File:** `hooks/hooks.json`

- [ ] **Step 1: Validate JSON and check structure**

```bash
python3 -c "
import json
h = json.load(open('/home/agricidaniel/claude-obsidian/hooks/hooks.json'))
print(json.dumps(h, indent=2))
"
```

Check:
- Valid JSON (no parse errors)
- Event names are valid Claude Code hook events: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreCompact`, `Notification`
- `SessionStart` hook exists — should update hot cache at session start
- `SessionEnd` or `Stop` hook exists — should save/update hot cache at end
- Hook commands reference files that exist (check paths)
- `timeout` values are reasonable (not 0, not > 300)
- Hook type is `"command"` (valid type)

---

## Task 7: Obsidian Vault Config Audit

**Files:** `.obsidian/community-plugins.json`, `.obsidian/appearance.json`, `.obsidian/app.json`, `.obsidian/graph.json`, `.obsidian/workspace.json`, `.obsidian/workspace-visual.json`

- [ ] **Step 1: Validate all .obsidian JSON files**

```bash
for f in /home/agricidaniel/claude-obsidian/.obsidian/*.json; do
  echo "=== $(basename $f) ==="
  python3 -c "import json; json.load(open('$f')); print('VALID JSON')" 2>&1
done
```

- [ ] **Step 2: Check community-plugins.json**

```bash
cat /home/agricidaniel/claude-obsidian/.obsidian/community-plugins.json
```

Expected: exactly `["obsidian-excalidraw-plugin","obsidian-banners","calendar","thino"]` — 4 entries, no duplicates.

- [ ] **Step 3: Check appearance.json**

```bash
cat /home/agricidaniel/claude-obsidian/.obsidian/appearance.json
```

Expected: `enabledCssSnippets` contains exactly `["vault-colors","ITS-Dataview-Cards","ITS-Image-Adjustments"]`.

- [ ] **Step 4: Check app.json (userIgnoreFilters)**

```bash
cat /home/agricidaniel/claude-obsidian/.obsidian/app.json
```

Expected: `userIgnoreFilters` lists `agents/`, `commands/`, `hooks/`, `skills/`, `_templates/`, `README.md`, `CLAUDE.md`, `WIKI.md`, `Welcome.md`. These hide plugin infrastructure from Obsidian's file explorer.

- [ ] **Step 5: Check graph.json**

```bash
cat /home/agricidaniel/claude-obsidian/.obsidian/graph.json
```

Check: `"search": "path:wiki"` filter present, colorGroups defined for entities/concepts/sources/meta, `hideUnresolved: true`.

- [ ] **Step 6: Check workspace.json for stale references**

```bash
grep -n "cosmic-brain\|skool-hub\|Nate" /home/agricidaniel/claude-obsidian/.obsidian/workspace.json
grep -n "cover.gif" /home/agricidaniel/claude-obsidian/.obsidian/workspace.json
```

Expected: zero `cosmic-brain` or `skool-hub` hits. Any GIF reference should point to `claude-obsidian-gif-cover-16x9.gif`.

---

## Task 8: Obsidian Plugin Files Audit

**Files:** All files under `.obsidian/plugins/`

- [ ] **Step 1: Verify all 4 plugins have required files**

```bash
for plugin in calendar thino obsidian-excalidraw-plugin obsidian-banners; do
  echo "=== $plugin ==="
  ls /home/agricidaniel/claude-obsidian/.obsidian/plugins/$plugin/
done
```

Expected per plugin: `manifest.json`, `main.js`, `styles.css`. Calendar and Thino also have `data.json` (tracked intentionally).

- [ ] **Step 2: Validate all manifest.json files**

```bash
for plugin in calendar thino obsidian-excalidraw-plugin obsidian-banners; do
  echo "=== $plugin ==="
  python3 -c "
import json
m = json.load(open('/home/agricidaniel/claude-obsidian/.obsidian/plugins/$plugin/manifest.json'))
print(f'id={m.get(\"id\")} version={m.get(\"version\")} minAppVersion={m.get(\"minAppVersion\")}')
"
done
```

Check: each manifest has `id`, `name`, `version`, `minAppVersion`, `author` fields.

- [ ] **Step 3: Confirm excalidraw main.js is NOT tracked but IS on disk**

```bash
git -C /home/agricidaniel/claude-obsidian ls-files .obsidian/plugins/obsidian-excalidraw-plugin/main.js
ls -lh /home/agricidaniel/claude-obsidian/.obsidian/plugins/obsidian-excalidraw-plugin/main.js
```

Expected: `git ls-files` returns nothing (not tracked). `ls` shows the file exists on disk (~8MB).

---

## Task 9: CSS Snippets Audit

**Files:** `.obsidian/snippets/vault-colors.css`, `.obsidian/snippets/ITS-Dataview-Cards.css`, `.obsidian/snippets/ITS-Image-Adjustments.css`

- [ ] **Step 1: Read all 3 snippets**

```bash
cat /home/agricidaniel/claude-obsidian/.obsidian/snippets/vault-colors.css
cat /home/agricidaniel/claude-obsidian/.obsidian/snippets/ITS-Dataview-Cards.css
cat /home/agricidaniel/claude-obsidian/.obsidian/snippets/ITS-Image-Adjustments.css
```

Check:
- `vault-colors.css` — defines color variables for wiki folder types, dims plugin dirs. No broken selectors.
- `ITS-Dataview-Cards.css` — has GPL-2.0 attribution header (lines 1-4)
- `ITS-Image-Adjustments.css` — has GPL-2.0 attribution header (lines 1-4)
- No `cosmic-brain` or `skool-hub` references in any snippet

---

## Task 10: Wiki Content Audit

**Files:** All files in `wiki/`

### 10a. Core meta files

- [ ] **Step 1: Read and check wiki/index.md**

```bash
cat /home/agricidaniel/claude-obsidian/wiki/index.md
```

Check:
- Frontmatter valid YAML
- Concepts section: lists LLM Wiki Pattern, Hot Cache, Compounding Knowledge
- Entities section: lists Andrej Karpathy
- Questions section: lists "How does the LLM Wiki pattern work"
- Comparisons section: lists "Wiki vs RAG"
- Navigation links present

- [ ] **Step 2: Check wiki/hot.md**

```bash
cat /home/agricidaniel/claude-obsidian/wiki/hot.md
```

Check: updated to 2026-04-07, mentions claude-obsidian rename, no Nate Herk references, session link present.

- [ ] **Step 3: Check wiki/log.md**

```bash
cat /home/agricidaniel/claude-obsidian/wiki/log.md
```

Check: has v1.2.0 session entry at top, append-only format, no Nate Herk references.

- [ ] **Step 4: Check wiki/getting-started.md**

```bash
cat /home/agricidaniel/claude-obsidian/wiki/getting-started.md
```

Check: 3-step quick start accurate, commands table matches commands/ directory, links resolve.

- [ ] **Step 5: Check wiki/meta/dashboard.md Dataview queries**

```bash
cat /home/agricidaniel/claude-obsidian/wiki/meta/dashboard.md
```

Check: no references to `answer_quality` or `confidence` fields (these don't exist in seed pages). Queries use `status`, `updated`, `type` — fields that exist in seed page frontmatter.

### 10b. Wikilink resolution

- [ ] **Step 6: Extract all wikilinks and check they resolve**

```bash
python3 -c "
import os, re, glob

wiki_files = glob.glob('/home/agricidaniel/claude-obsidian/wiki/**/*.md', recursive=True)
all_titles = set()
for f in wiki_files:
    title = os.path.splitext(os.path.basename(f))[0]
    all_titles.add(title.lower())

broken = []
for f in wiki_files:
    content = open(f).read()
    links = re.findall(r'\[\[([^\]|#]+)', content)
    for link in links:
        link = link.strip()
        if '/' in link:
            # path-style link
            full = '/home/agricidaniel/claude-obsidian/wiki/' + link + '.md'
            if not os.path.exists(full) and not os.path.exists('/home/agricidaniel/claude-obsidian/wiki/' + link):
                broken.append((f, link))
        elif link.lower() not in all_titles:
            broken.append((f, link))

if broken:
    for f, l in broken:
        print(f'BROKEN: {os.path.basename(f)} -> [[{l}]]')
else:
    print('All wikilinks resolve')
"
```

### 10c. Canvas files

- [ ] **Step 7: Validate all canvas JSON files**

```bash
for f in /home/agricidaniel/claude-obsidian/wiki/canvases/*.canvas \
         /home/agricidaniel/claude-obsidian/wiki/"Wiki Map.canvas"; do
  echo "=== $(basename "$f") ==="
  python3 -c "
import json
c = json.load(open('$f'))
nodes = c.get('nodes', [])
edges = c.get('edges', [])
print(f'{len(nodes)} nodes, {len(edges)} edges')
file_nodes = [n for n in nodes if n.get('type') == 'file']
for n in file_nodes:
    print(f'  file: {n[\"file\"]}')
"
done
```

For each file-type node, check the referenced file exists on disk.

### 10d. Seed page frontmatter

- [ ] **Step 8: Check frontmatter on all seed wiki pages**

```bash
for f in \
  "/home/agricidaniel/claude-obsidian/wiki/concepts/LLM Wiki Pattern.md" \
  "/home/agricidaniel/claude-obsidian/wiki/concepts/Hot Cache.md" \
  "/home/agricidaniel/claude-obsidian/wiki/concepts/Compounding Knowledge.md" \
  "/home/agricidaniel/claude-obsidian/wiki/entities/Andrej Karpathy.md" \
  "/home/agricidaniel/claude-obsidian/wiki/questions/How does the LLM Wiki pattern work.md" \
  "/home/agricidaniel/claude-obsidian/wiki/comparisons/Wiki vs RAG.md"; do
  echo "=== $(basename "$f") ==="
  python3 -c "
content = open('$f').read()
end = content.index('---', 3)
print(content[:end+3])
"
done
```

Verify each has: `type`, `title`, `updated`, `status`, `related` fields. Check `status` is one of: `seed`, `developing`, `mature`, `evergreen`.

---

## Task 11: Documentation Accuracy Audit

### 11a. README

- [ ] **Step 1: Check README image references all resolve**

```bash
python3 -c "
import re, os
readme = open('/home/agricidaniel/claude-obsidian/README.md').read()
imgs = re.findall(r'src=\"([^\"]+)\"', readme)
for img in imgs:
    path = '/home/agricidaniel/claude-obsidian/' + img
    exists = os.path.exists(path)
    print(f'{'PASS' if exists else 'FAIL'}: {img}')
"
```

- [ ] **Step 2: Check all install commands in README are accurate**

```bash
grep -n "claude plugin install\|git clone\|bash bin/" /home/agricidaniel/claude-obsidian/README.md
```

Verify:
- `claude plugin install github:AgriciDaniel/claude-obsidian` — correct
- `git clone https://github.com/AgriciDaniel/claude-obsidian` — correct
- `bash bin/setup-vault.sh` — script exists and is executable

- [ ] **Step 3: Check commands table in README matches actual commands/ directory**

```bash
grep -A2 "| \`/wiki\`\|ingest\|/save\|/autoresearch\|/canvas\|lint\|hot cache" /home/agricidaniel/claude-obsidian/README.md
ls /home/agricidaniel/claude-obsidian/commands/
```

Every command listed in README should have a corresponding file in `commands/`.

- [ ] **Step 4: Check plugins section in README matches actual installed plugins**

```bash
grep -A4 "Pre-installed\|pre-installed" /home/agricidaniel/claude-obsidian/README.md | head -30
cat /home/agricidaniel/claude-obsidian/.obsidian/community-plugins.json
```

Verify plugin names in README match community-plugins.json.

### 11b. setup-vault.sh

- [ ] **Step 5: Validate setup-vault.sh syntax and content**

```bash
bash -n /home/agricidaniel/claude-obsidian/bin/setup-vault.sh && echo "SYNTAX OK"
cat /home/agricidaniel/claude-obsidian/bin/setup-vault.sh
```

Check:
- `bash -n` reports no syntax errors
- `set -euo pipefail` present (safe scripting)
- Writes `graph.json`, `app.json`, `appearance.json` — are the values written still accurate?
- Downloads Excalidraw from correct URL (zsviczian's repo, `releases/latest`)
- Success message lists all 4 plugins and 3 CSS snippets

### 11c. docs/install-guide.md

- [ ] **Step 6: Check install guide accuracy**

```bash
cat /home/agricidaniel/claude-obsidian/docs/install-guide.md
```

Check:
- Version in header says `1.2.0`
- Install commands match README
- Plugin table matches installed plugins
- No `cosmic-brain` references
- `docs/install-guide.pdf` exists

```bash
ls -lh /home/agricidaniel/claude-obsidian/docs/install-guide.pdf
```

### 11d. WIKI.md

- [ ] **Step 7: Check WIKI.md for stale references**

```bash
grep -n "cosmic-brain\|Nate Herk\|nateherk" /home/agricidaniel/claude-obsidian/WIKI.md | head -10
```

Note: WIKI.md is gitignored so stale content there doesn't affect the repo, but flag it.

### 11e. CLAUDE.md

- [ ] **Step 8: Check CLAUDE.md accuracy**

```bash
cat /home/agricidaniel/claude-obsidian/CLAUDE.md
```

Check:
- Plugin name is `claude-obsidian`
- No placeholder text remaining
- Skill trigger phrases match actual skill descriptions
- No `cosmic-brain` references

---

## Task 12: Cross-File Consistency + Security

### 12a. Name and URL consistency

- [ ] **Step 1: Scan all tracked files for any remaining cosmic-brain references**

```bash
cd /home/agricidaniel/claude-obsidian
git ls-files | xargs grep -l "cosmic-brain\|Cosmic Brain" 2>/dev/null
```

Expected: zero results (or only historical/contextual in wiki session notes).

- [ ] **Step 2: Check all repo URLs point to AgriciDaniel/claude-obsidian**

```bash
cd /home/agricidaniel/claude-obsidian
git ls-files | xargs grep -h "github.com/AgriciDaniel\|github.com/avalonreset" 2>/dev/null | sort -u
```

Expected: all URLs use `AgriciDaniel/claude-obsidian` or `avalonreset-pro/claude-obsidian`. No `cosmic-brain` in any URL.

### 12b. Security scan

- [ ] **Step 3: Scan for potential secrets or sensitive data**

```bash
cd /home/agricidaniel/claude-obsidian
git ls-files | xargs grep -il "api.key\|apikey\|api_key\|secret\|password\|token\|bearer\|sk-\|ghp_\|OBSIDIAN_API" 2>/dev/null
```

For any matches: read the file and confirm values are placeholders, not real credentials.

- [ ] **Step 4: Check Obsidian plugin data.json files for personal data**

```bash
cat /home/agricidaniel/claude-obsidian/.obsidian/plugins/calendar/data.json
cat /home/agricidaniel/claude-obsidian/.obsidian/plugins/thino/data.json
```

Verify: no personal notes, tokens, or private data — only plugin settings (weekStart, locale, etc.).

### 12c. Plugin install simulation

- [ ] **Step 5: Verify plugin install path would work**

The command `claude plugin install github:AgriciDaniel/claude-obsidian` works by:
1. Fetching the repo
2. Reading `.claude-plugin/plugin.json`
3. Loading `skills/*/SKILL.md`, `commands/*.md`, `agents/*.md`, `hooks/hooks.json`

Simulate this by confirming:

```bash
# All skills discoverable
ls /home/agricidaniel/claude-obsidian/skills/*/SKILL.md

# All commands discoverable
ls /home/agricidaniel/claude-obsidian/commands/*.md

# All agents discoverable
ls /home/agricidaniel/claude-obsidian/agents/*.md

# Hooks valid
python3 -c "import json; json.load(open('/home/agricidaniel/claude-obsidian/hooks/hooks.json')); print('hooks.json VALID')"

# Plugin manifest readable
python3 -c "import json; d=json.load(open('/home/agricidaniel/claude-obsidian/.claude-plugin/plugin.json')); print(f'Plugin: {d[\"name\"]} v{d[\"version\"]}')"
```

---

## Task 13: Compile Audit Report

- [ ] **Step 1: Write AUDIT-REPORT.md**

Create `/home/agricidaniel/claude-obsidian/docs/AUDIT-REPORT.md` with:
- Date: 2026-04-07
- Summary table: area → PASS/WARN/FAIL + one-line note
- Details section per area with all findings
- Recommended fixes section (issues only, no changes made)

Format:

```markdown
# claude-obsidian Audit Report
Date: 2026-04-07

## Summary

| Area | Status | Note |
|------|--------|------|
| 1. Git health | PASS/WARN/FAIL | ... |
...

## Findings

### Area 1: Git Health
...

## Recommended Fixes
1. ...
```

---

## Self-Review

**Spec coverage:**
- Plugin manifest ✓ (Task 2)
- All 7 skills ✓ (Task 3)
- All 4 commands ✓ (Task 4)
- Both agents ✓ (Task 5)
- Hooks ✓ (Task 6)
- Obsidian config ✓ (Task 7)
- Obsidian plugins ✓ (Task 8)
- CSS snippets ✓ (Task 9)
- Wiki content + wikilinks + canvases ✓ (Task 10)
- README + install guide + setup script + CLAUDE.md ✓ (Task 11)
- Cross-file consistency + security + install simulation ✓ (Task 12)
- Report generation ✓ (Task 13)

**No placeholders:** All steps have exact commands with expected output.

**Read-only confirmed:** Zero write operations in any task except Task 13 (report file).
