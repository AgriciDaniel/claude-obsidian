---
name: wiki-workflow
description: "Fable-driven multi-agent workflow layer for the Compound Vault (v2.0 'Live Core'). Ships deterministic orchestration scripts under `workflows/`, run with Claude Code's Workflow tool, that fan out over many subagents: `deep-ingest.js` (parallel ingest of many sources, verify, lint), `research-sweep.js` (multi-modal web sweep, dedupe, adversarial verify, file), `rules-audit.js` (audit a diff or codebase against the rules/ packs). Fable is the default fan-out model; verify and judge stages escalate to a stronger model. Token-expensive and strictly opt-in: the user must ask. Triggers on: wiki-workflow, run a workflow, deep ingest, deep-ingest, research sweep, research-sweep, rules audit, rules-audit, fan out, fan-out, multi-agent, orchestrate agents, parallel ingest, adversarial verify, audit this diff against the rules, sweep the web on."
allowed-tools: Read, Write, Bash
---

# wiki-workflow: Deterministic Multi-Agent Orchestration

A skill tells one agent how to do one thing. A **workflow** tells the harness how to run many agents in a fixed shape: fan out over N sources, pipeline the results, have independent skeptics attack a finding, loop until the well runs dry.

The scripts live under `workflows/` and are executed with Claude Code's **Workflow tool**. The shape is code, so it is deterministic. The work inside each node is a subagent, so it is not. That split is the point: the orchestration cannot drift, and the reasoning can.

**These are token-expensive and strictly opt-in. The user must ask for one.** Never launch a workflow because it seemed like a good idea. A `deep-ingest` over 40 sources is 40 subagents plus verification; that is a real bill, and the user is the one who pays it.

---

## Model policy: Fable fans out, a stronger model judges

**`claude-fable-5` is the default fan-out model.** It is fast enough and cheap enough to run wide, which is the whole reason a fan-out is affordable at all. Twenty parallel ingests on Fable cost what a couple of them would cost on a frontier model.

**Escalate the verify and judge stages to a stronger model.** The rationale is asymmetric cost of error:

- A fan-out node that gets one source slightly wrong is one bad page, and the verify stage catches it.
- A verify node that gets it wrong **certifies** the bad page. There is nothing downstream to catch it.

So spend where a mistake is unrecoverable, and economize where it is not. Cheap and wide at the leaves; expensive and careful at the gate.

---

## Available workflows

### `workflows/deep-ingest.js`

Fan out over many sources, ingest each in parallel, verify, lint.

Fan out one subagent per source (Fable). Each reads its source, extracts entities and concepts, files pages per the vault's methodology mode, and reports what it created. A verify stage checks the new pages against their sources. A final lint pass catches orphans and dead wikilinks introduced by the batch.

Use when: a folder of sources has landed in `.raw/` and ingesting them one at a time would take all afternoon.

### `workflows/research-sweep.js`

Multi-modal web sweep, dedupe, adversarial verify, file into the wiki.

Fan out searches and fetches across sources (Fable), dedupe the findings at a barrier, run adversarial verification on each surviving claim, then file the survivors as wiki pages with citations.

Use when: a topic needs real coverage, not one search and a summary. Every network call in this workflow clears `net-policy.py` first.

### `workflows/rules-audit.js`

Audit a diff or a codebase against the `rules/` packs, report violations by severity.

Fan out one subagent per rule (or per rule pack) against the target, each looking for violations of exactly its own rule. Collect, dedupe, and report by severity with `file:line` citations. The packs live at `rules/coding/` and `rules/finance/`.

Use when: a workstream is staged and you want a broad, parallel sweep against the rule set. Complements the `verifier` agent, which is a single deep read of the staged diff; this is many shallow reads, one per rule.

---

## The patterns

### `pipeline()` by default

Stage B starts on each item as soon as stage A finishes **that item**. No barrier. A slow source does not hold up the twelve fast ones behind it.

This is the default because most stages genuinely do not need all prior results. Ingesting source 7 does not depend on source 3.

### `parallel()` only at a real barrier

Use it only when a stage genuinely needs **all** prior results:

- **Dedupe.** You cannot know an item is a duplicate until you have seen everything it might duplicate.
- **Early-exit.** You cannot decide to stop until you have counted what came back.
- **Ranking or selection across the whole set.**

A barrier you did not need is pure latency: every item waits for the slowest one for no reason. If you cannot name what the stage needs from the other items, it does not need a barrier.

### Adversarial verify

Do not ask "is this claim true?" A model asked to check its own kind of work agrees with it.

Instead: dispatch N independent skeptics, each prompted to **REFUTE** the finding. Give each the claim and the evidence and ask it to break them. If a **majority** land a refutation, the finding dies. Independence matters: the skeptics must not see each other's verdicts, or the first one anchors the rest.

This is where you escalate the model. A skeptic that cannot find a real flaw is worse than useless, because its silence reads as confirmation.

### Loop-until-dry

For discovery of unknown size: run a round, and if it produced new material, run another. Stop when a round yields nothing new.

Always bound it. A max-round cap and a per-round novelty threshold, or the loop will chase asymptotically diminishing returns on the user's budget.

---

## The network gate applies inside workflows too

**Every workflow node that touches the network goes through `net-policy.py` first**, exactly as it would in a single-agent run.

```bash
python3 scripts/net-policy.py check-fetch "$URL" || exit $?
```

Fan-out does not dilute consent. Twenty subagents each doing an unchecked fetch is not twenty small violations; it is one large one, and it is harder to see. On an `ask` verdict (exit 3), the node stops and the workflow surfaces the prompt to the human. A subagent cannot grant consent on the user's behalf, and it cannot grant it to itself.

Egress from inside a workflow is the same rule, harder: `check-egress` with the payload paths, secrets blocked unconditionally, consent explicit.

---

## Running one

```bash
ls workflows/
```

Then invoke it with the Workflow tool. Before you do, tell the user what it will cost in rough terms: how many subagents, roughly how wide the fan-out, which stages escalate. Let them say no.

---

## Cross-reference

- Network policy gate: [`skills/web-live/SKILL.md`](../web-live/SKILL.md)
- Browser transport (used by `research-sweep`): [`skills/browser/SKILL.md`](../browser/SKILL.md)
- Ingest semantics (used by `deep-ingest`): [`skills/wiki-ingest/SKILL.md`](../wiki-ingest/SKILL.md)
- Rule packs (used by `rules-audit`): `rules/coding/`, `rules/finance/`, `rules/SPEC.md`
- Single-pass pre-commit review: `agents/verifier.md`
- Filing destination for new pages: [`skills/wiki-mode/SKILL.md`](../wiki-mode/SKILL.md)

---

## How to think (10-principle mapping)

When working on this skill, apply the 10-principle loop. See [`skills/think/SKILL.md`](../think/SKILL.md) for the canonical framework.

| # | Principle | Application here |
|---|-----------|-------------------|
| 1 | OBSERVE (ext) | Read `workflows/` and see which scripts actually exist before promising one. |
| 2 | OBSERVE (int) | Am I reaching for a workflow because the task needs one, or because fan-out feels impressive? |
| 3 | LISTEN | Workflows are opt-in. The user asks, or you do not run one. |
| 4 | THINK | Pipeline unless a stage needs every prior result. Name the barrier before you add it. |
| 5 | CONNECT (lat) | Verification is adversarial or it is theater. Prompt the skeptics to refute, not to agree. |
| 6 | CONNECT (sys) | Fable at the leaves, a stronger model at the gate. Spend where an error is unrecoverable. |
| 7 | FEEL | A fan-out that returns twenty near-identical pages is telling you the dedupe barrier is in the wrong place. |
| 8 | ACCEPT | Some tasks are just one agent doing one thing. Orchestration has a floor below which it is only cost. |
| 9 | CREATE | Verified pages filed into the wiki, cited, linked, and linted. Not a pile of subagent transcripts. |
| 10 | GROW | Every workflow that ran too wide or too deep is a tuning signal. Adjust the caps; do not adjust the user's bill. |
