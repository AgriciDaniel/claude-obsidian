---
id: finance/reconcile-material-figures
domain: finance
title: Cross-check every material figure against a second source
severity: high
applies_when: >
  You are about to report a figure that a decision will rest on, or you have pulled a headline
  number from exactly one source and are about to build on it.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "arXiv 2502.15865, Standard Benchmarks Fail: Auditing LLM Agents in Finance Must Prioritize Risk"
---

Reconcile every material figure against a second, independent source before you report it.
When the two disagree, report the disagreement. Do not silently pick one.

**Why.** A single source is a single point of failure, and the characteristic agent failure is
shallow sourcing: grab the first plausible number, build a whole model on it, present the
model with total confidence. Aggregators propagate each other's errors, a scraped table drops
a column, a figure is restated and the stale version outranks the new one. The second source
is what converts "the number I found" into "the number", and the cost of skipping it is that
every downstream figure inherits an error nobody looked for.

**How to apply.**
1. Decide what is material: any figure a decision hinges on, any input that drives more than a
   trivial share of an output, any headline number you will be quoted on.
2. For each, pull an independent second source. Independent means a different origin, not a
   different site republishing the same wire. Two aggregators quoting one filing is one source.
3. Prefer primary sources to reconcile against: the filing, the exchange, the central bank,
   the registry. Reconcile derived figures back to the primary line item.
4. If the two agree within a trivial tolerance, report the figure and name both sources.
5. If they disagree materially, do not average them and do not pick the convenient one. Report
   both, name the discrepancy, and say which you are using and why.
6. If you cannot get a second source, say so explicitly at the point of use. "Single-sourced,
   unreconciled" is a legitimate label. A silent single source is not.
