---
name: feature-request
description: "Capture a feature idea as a structured GitHub issue on saixso/vault-os. Walks the user through describing the feature, why it matters, and its scope, then files a labeled issue. Triggers on: /feature-request, I have a feature idea, feature request, new feature, I want to add."
allowed-tools: Read Bash
---

# feature-request: File a vault-os feature request

Capture feature ideas as structured GitHub issues on `saixso/vault-os`. One idea per invocation — keep it focused.

---

## Workflow

### Step 1 — What

Ask the user:

> What's the feature? Describe it in a sentence or two.

Wait for their response. Extract a short title and the description.

### Step 2 — Why

Ask the user:

> What problem does this solve, or why does it matter?

Wait for their response.

### Step 3 — Scope

Ask the user to pick a scope:

- **Small** — hook, script, config change
- **Medium** — new skill, new workflow
- **Large** — architecture change, multi-skill integration

Map scope to phase:
- Small/Medium → `phase-2`
- Large → `phase-3`

### Step 4 — File the issue

Create the issue using `gh`:

```bash
gh issue create \
  --repo saixso/vault-os \
  --title "<title>" \
  --label "enhancement,<phase-label>" \
  --body "<body>"
```

Issue body format:

```markdown
## Problem

<why it matters — from step 2>

## Proposal

<feature description — from step 1>

## Acceptance Criteria

- [ ] <1-3 concrete criteria derived from the proposal>

## Scope

**<Small|Medium|Large>** — <phase-2|phase-3>
```

### Step 5 — Report

Show the user the issue URL and a one-line summary.

---

## Constraints

- One issue per invocation
- Always target `saixso/vault-os` repo
- Requires `gh` CLI authenticated with access to the repo
- Do not check for duplicates — keep it simple, user can close dupes on GitHub
