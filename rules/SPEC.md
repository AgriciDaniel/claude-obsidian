# Rule Pack Spec (v2.0)

One rule, one file. `rules/<domain>/<slug>.md`. The file is the **single source of
truth**; `scripts/render-rules.py` compiles it into each coding agent's native
dialect. Never hand-edit a rendered file — it is overwritten on every render.

## Why single-source

Six agents (Claude Code, Cursor, Windsurf, Copilot, Codex/OpenCode, Gemini) each
want rules in a different file, in a different format, with different frontmatter.
Hand-maintaining six copies guarantees drift. Here, a rule is authored once and
`render-rules.py` emits the six dialects. Drift becomes structurally impossible.

## Format

```markdown
---
id: coding/verify-by-execution        # must equal <domain>/<slug>
domain: coding                        # coding | finance
title: Verify by execution, not inspection
severity: blocker                     # blocker | high | medium
applies_when: >                       # ONE line. Becomes the agent's trigger.
  You are about to call something done, fixed, or working.
globs:                                # optional; Cursor/Copilot path scoping
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]   # who receives it
source: "Anthropic engineering guidance, 2025"               # attribution or ""
---

Imperative statement of the rule. Second person. No hedging.

**Why.** The failure this prevents, concretely. Name the cost.

**How to apply.** What to actually do, as steps or a checklist.
```

## Rules for rules

- **Imperative, second person.** "Run the test." Not "tests should be run."
- **`applies_when` is a trigger, not a summary.** It must describe an observable
  moment ("you are about to write a `catch`"), so an agent can pattern-match it
  against its own next action. A rule an agent cannot notice it needs is dead weight.
- **Severity is a promise.** `blocker` = shipping without it is a defect. Do not
  inflate; a pack where everything is a blocker is a pack where nothing is.
- **Every rule earns its context budget.** These are injected into every prompt of
  every agent that subscribes. A rule that is merely true but never changes an
  action is a tax on every token that follows it. Cut it.
- **No rule may contradict another in the same domain.** The renderer enforces
  unique ids; it cannot enforce coherence. That is on the author.

## Severity → enforcement

| Severity  | Rendered as | Behavior |
|-----------|-------------|----------|
| `blocker` | `alwaysApply: true`, top of file | Injected into every request |
| `high`    | `alwaysApply: true`, after blockers | Injected into every request |
| `medium`  | glob-scoped / on-demand | Loaded when the globs match |

## Render targets

| Agent | Output | Format |
|---|---|---|
| `claude` | `.claude/rules/<domain>.md` | Markdown + trigger list |
| `cursor` | `.cursor/rules/<domain>.mdc` | MDC frontmatter (`description`, `globs`, `alwaysApply`) |
| `windsurf` | `.windsurf/rules/<domain>.md` | Markdown + YAML frontmatter |
| `copilot` | `.github/instructions/<domain>.instructions.md` | `applyTo` frontmatter |
| `codex` | `AGENTS.md` (managed block) | Plain markdown, delimited |
| `gemini` | `GEMINI.md` (managed block) | Plain markdown, delimited |

Managed blocks are delimited by `<!-- BEGIN render-rules:<domain> -->` and
`<!-- END render-rules:<domain> -->`. Text outside the markers is preserved
verbatim, so `AGENTS.md` and `GEMINI.md` keep their hand-written content.
