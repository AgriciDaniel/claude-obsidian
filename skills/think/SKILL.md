---
name: think
description: "Apply the 10-principle thinking loop (OBSERVE-OBSERVE-LISTEN-THINK-CONNECT-CONNECT-FEEL-ACCEPT-CREATE-GROW) to any non-trivial problem. Walks Claude through external observation, metacognition, active listening, first-principles analysis, lateral connection, system orchestration, intuition, intellectual humility, generative output, and iterative growth. Triggers on: think this through, 10-principle review, /think, OBSERVE LISTEN THINK, deep think, systematic thinking, structured reasoning, walk this through, audit my thinking, am I thinking about this right."
allowed-tools: Read, Grep, Glob, Bash
---

# think: The 10-principle thinking loop

A meditation, a discipline, and a checklist. Use this skill when a problem is non-trivial enough that disciplined thinking pays for itself: architectural decisions, post-mortems, ambiguous user requests, audits, multi-stakeholder tradeoffs, "should we ship?" moments, "what are we missing?" moments.

The 10 principles are not a recipe. They are stages of attention. You move through them in order on the first pass, then loop back to the earlier ones as new information emerges. The discipline is in NOT skipping the awkward ones (OBSERVE-internal, ACCEPT, GROW) just because they are uncomfortable.

This skill ships v1.9.0 of claude-obsidian. It is the meta-skill that informs how the other 14 skills think. Each of those skills also has a per-skill "How to think" appendix mapping these 10 stages to that skill's specific work.

---

## The 10 principles

### 1. OBSERVE (the external input)

Thinking begins with data collection. Look at the environment, the current landscape, the patterns and inefficiencies and opportunities — without immediately trying to solve them. Read the raw inputs.

In practice: read the code before changing it. Read every commit before claiming the branch is clean. Read every page in the vault before answering a question that should be sourced. Resist the urge to jump to a fix on the first symptom.

### 2. OBSERVE (the internal metacognition)

Now observe yourself. This is metacognition — thinking about how you are thinking. Are you operating on assumptions? Do you have a bias in this architecture? Are you anchored on a previous decision? Is there a finding count you are unconsciously targeting?

In practice: write a one-paragraph "bias log" before scoring something. Note ownership bias, ship-it bias, familiarity bias, anchoring. The bias does not go away by being noted — it gets contained.

### 3. LISTEN (active receptivity)

Observing is often visual or analytical. Listening requires shutting down the ego to absorb external feedback. Pay attention to user intent, community discussions, error messages, the subtle signals in the noise that tell you what people actually need rather than what you think they need.

In practice: read the SKILL.md description before assuming what a skill does. Read the user's exact phrasing before paraphrasing it back. Read the failure message before guessing the failure mode. The user's confusion is data.

### 4. THINK (critical processing)

The analytical engine. Once you have the inputs, break the problem down to first principles. Structure the logic, map the workflows, evaluate the constraints, synthesize the raw data into a coherent strategy.

In practice: this is the cut where the six-cut engineering kernel lives. Read-before-write. Name like the next reader is hostile. Smallest unit that works. Delete more than you add. Evidence over intuition. Failure is the spec. THINK is where rigor pays off, but it cannot start without 1-3.

### 5. CONNECT (associative / lateral thinking)

Great ideas rarely happen in a vacuum; they happen at intersections. Take two seemingly unrelated concepts and link them. SEO algorithms × agentic AI behavior. Retrieval architecture × LLM compaction. The "Aha!" moment is finding the hidden relationship between distinct variables.

In practice: when auditing a skill, ask "does this bug pattern exist in adjacent skills?" When designing an API, ask "what other interface is this isomorphic to?" Lateral thinking finds cross-cutting bugs the per-component view misses.

### 6. CONNECT (system orchestration)

The second CONNECT is about execution. Moving from an isolated idea to an integrated system. How do these individual thoughts, tools, or agents plug into one another to create a seamless, functioning whole? This is the principle of building the wiring.

In practice: when shipping a new skill, audit how it integrates with hooks, transport, locks, the router, the verifier agent. The skill that works in isolation but breaks the auto-commit hook is not a working skill.

### 7. FEEL (emotional intelligence + intuition)

Pure logic is brittle without empathy. Factor in the human element. Design with user experience in mind. Understand the emotional resonance of your messaging. Trust hard-earned intuition when the data is ambiguous.

In practice: an error message that says "ERR: exit code 4" fails FEEL even if it passes THINK. A skill description that lists 12 triggers but doesn't explain WHEN to use it fails FEEL. The user installing the plugin for the first time experiences your decisions in a way `make test` cannot measure.

### 8. ACCEPT (intellectual humility)

No plan survives first contact with reality. Embrace constraints. Acknowledge when a hypothesis fails. Recognize when the market wants something different than what you built. Let go of sunk cost.

In practice: tier findings honestly. If your skill is 78/100, do not write 95/100. If the verdict is YELLOW, do not call it GREEN to please anyone. ACCEPT is the firewall against sycophancy.

### 9. CREATE (generative output)

Analysis paralysis is the enemy of progress. At some point, stop strategizing and start producing. Write the code. Draft the content. Launch the system. Ship the audit report.

In practice: an audit that never gets written is worse than a B+ audit that ships. A v1.8.2 fix that sits in working tree forever is worse than the same fix committed and pushed. CREATE is the answer when the prior stages have given you enough.

### 10. GROW (the iterative loop)

Thinking is not a straight line; it is a feedback loop. Take what you built (CREATE), see how it performs in reality, and use those lessons to upgrade your skills and expand your capacity for the next cycle.

In practice: every audit must end with a GROW section. What worked? What to improve next cycle? What inputs feed v_next? GROW is what turns one good decision into a compounding habit.

---

## When to invoke

Invoke `/think` when:

- You are about to make a non-trivial architectural decision (designing a new skill, restructuring a module, choosing between approaches)
- You are auditing a system and need a methodology spine (per the v1.8.0 pre-push audit pattern)
- The user's request is ambiguous and you need to listen harder before responding
- You hit a surprising result and need OBSERVE-internal before adjusting
- You are about to call something done and need to verify ACCEPT (anti-sycophancy) before claiming the verdict
- A post-mortem after something went sideways
- Closing out a session and need a GROW step before /save

Do NOT invoke `/think` for:

- Single-line typo fixes (the discipline is overkill; just fix it)
- Trivial lookups (no decision is being made; just answer)
- Cases where you have already moved through the 10 stages implicitly (don't ceremonially re-do it)

The framework's value scales with problem novelty + irreversibility. For a one-line fix that's easily reverted, the loop is dead weight. For a release-blocking audit decision, skipping any stage loses calibration.

---

## How to use

```
/think <problem statement>
```

Walks through the 10 stages in order. For each, answer the prompt questions below. Stage outputs feed into stage 9 (CREATE), which produces a recommendation or artifact.

Stages 1, 4, 9 are usually short. Stages 2, 7, 8, 10 are where most people skip. Watch yourself there.

---

## Stage-by-stage prompts

For each stage, answer these questions before moving to the next:

### 1. OBSERVE (external)
- What are the raw inputs? (Code? Docs? User intent? Logs?)
- What have I read in full vs. skimmed vs. assumed?
- What is the environment / state right now? (Working tree, recent commits, test status, deployment state)
- What surprises me, before I start interpreting?

### 2. OBSERVE (internal)
- What am I biased toward here? (Ownership, ship-it, novelty, anchoring, familiarity)
- What outcome am I unconsciously hoping for? Why?
- If a fresh-context reviewer joined right now, what would they question that I am taking for granted?
- Is my confidence calibrated to the evidence I actually have?

### 3. LISTEN
- What did the user actually ask for? (Quote verbatim.)
- What signals are in the noise? (Word choice, what they did NOT say, prior corrections in this thread or in memory)
- Are there community / domain signals I should consult? (Github issues, error messages, neighbor patterns)
- Whose voice is missing from this decision?

### 4. THINK
- What are the first principles in play? (Constraints, invariants, blast radius)
- Apply the six-cut engineering kernel: read-before-write, hostile naming, smallest unit, delete-more-than-you-add, evidence-over-intuition, failure-is-the-spec
- What are the alternatives I have NOT considered?
- What is the cheapest experiment that would prove me wrong?

### 5. CONNECT (lateral)
- Where else does this pattern show up?
- What seemingly unrelated domain solved a structurally similar problem?
- If the same bug exists in this code, does it exist in three neighbors?
- What metaphor unlocks the user's intuition for this?

### 6. CONNECT (system)
- How does this plug into the existing wiring? (Hooks, transport, locks, router, agents)
- Does anything need to be updated downstream / upstream / across?
- What new failure modes does integration create that the isolated component doesn't have?
- Is the documentation about integration up to date?

### 7. FEEL
- How does this LAND for the user? (UX, error messages, naming, onboarding friction)
- What emotional state is the user in when they hit this code path? (Frustrated? Exploring? Time-pressured?)
- Does my intuition say "something is off" even when the data says "we're good"?
- Does my intuition say "we're good" even when I cannot articulate why?

### 8. ACCEPT
- What is the honest tier of this finding / verdict? (No inflation.)
- What constraint am I being asked to soften that I should not?
- What sunk cost am I protecting that I should release?
- If this were someone else's work, would I be more critical?

### 9. CREATE
- What is the smallest artifact that ships the decision?
- What is the cleanest path from here to "done"?
- Are the inputs sufficient, or do I need to loop back to an earlier stage?
- Ship it.

### 10. GROW
- What worked well in this cycle?
- What would I do differently next time?
- What inputs feed v_next?
- Where should this lesson be stored so future-me does not have to re-derive it? (Wiki page? Memory? CLAUDE.md? Audit doc?)

---

## Anti-patterns

The loop fails when:

- **Skipping OBSERVE-internal.** Going straight from external observation to THINK without auditing your own biases produces confident wrong answers. The bias does not announce itself.
- **Skipping ACCEPT.** Padding a score, hedging a verdict, calling YELLOW "GREEN with disclosure". The framework's anti-sycophancy contract dies the moment ACCEPT becomes optional.
- **Skipping GROW.** Producing the artifact, shipping it, and moving on without feedback. Next cycle starts at the same first-principles baseline; nothing compounds.
- **Analysis paralysis at THINK.** Looping inside stage 4 forever, never reaching CREATE. The framework is a sequence, not a stopping rule. ACCEPT what you have, CREATE the artifact, GROW from the response.
- **Ceremony.** Writing all 10 stages for a one-line fix. The framework's cost should scale with problem stakes. Trivial problems are answered, not audited.

---

## Composition with other skills

The 10-principle framework composes with the rest of the plugin:

- **`/best-practices`** (six-cut engineering kernel): The THINK stage's analytical engine. The 10-principle loop wraps the six-cut; the six-cut is the inside of stage 4.
- **`/save`**: After GROW, save the insights worth not re-deriving. The session note IS the GROW artifact.
- **`/wiki-lint`**: Periodic audits of the wiki are themselves a GROW step at the system level.
- **`agents/verifier.md`**: An OBSERVE-internal substitute for solo work — fresh-context reviewer that catches biases the chair missed.
- **`/autoresearch`**: A LISTEN amplifier — surfaces external signals the chair would not have found alone.

Every other skill in this plugin has a "How to think" appendix mapping its specific work to these 10 stages. Read those appendices for skill-specific applications.

---

## Reference

- This skill is the canonical source for the 10-principle framework in this plugin.
- Pre-push audit example using the framework as audit methodology: [`docs/audits/v1.8.0-pre-push-audit-2026-05-18.md`](../../docs/audits/v1.8.0-pre-push-audit-2026-05-18.md)
- The framework's enforcement layer is `/best-practices` (loaded separately).
- The skill does not modify files or execute mutations. It loads structure and discipline; what you do with that is the next decision.

The 10 principles are a meditation. Without the stance, the framework becomes ceremony. With the stance, every cycle compounds.
