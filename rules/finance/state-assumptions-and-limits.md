---
id: finance/state-assumptions-and-limits
domain: finance
title: State model assumptions and material limitations up front
severity: medium
applies_when: >
  You are about to deliver a model, a projection, a valuation, or a report, and the assumptions
  that drive it are currently buried in the middle or absent.
globs:
  - "**/*.ipynb"
  - "**/*.py"
  - "**/*.xlsx"
  - "**/*.csv"
  - "**/*.md"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "CFA Institute Standards of Professional Conduct V(B) Communication with Clients"
---

Open every model or report with its assumptions and its material limitations, before the
result. Name what would break it.

**Why.** Every model is a set of assumptions with a number stapled to the end, and the number
is the only part that gets read. Put the assumptions at the bottom and they are decoration:
the reader has already anchored on the output and has no idea that the entire valuation turns
on a terminal growth rate somebody typed in. Assumptions disclosed after the fact are not
disclosure, they are an alibi. The limitation that matters is the one the reader learns about
before they act, not the one you can point to afterward.

**How to apply.**
1. Lead with an assumptions block: the drivers, their values, and where each came from.
2. Name the sensitivity. Which one or two inputs move the answer most, and by how much? If a
   50bps change in the discount rate moves the valuation 20%, that belongs above the result,
   not in a footnote.
3. State the limitations concretely, not as boilerplate. "Comps set excludes private peers, so
   the multiple may be overstated" is a limitation. "Past performance is not indicative of
   future results" is noise.
4. Name what data you could not get and how its absence biases the answer, in which direction.
5. Give ranges and scenarios, not a single point. A base, bear, and bull case communicates
   uncertainty that a single number actively conceals.
6. Say what would falsify the conclusion. A model that nothing could break is not a model, it
   is an advertisement.
