---
id: finance/no-unsourced-figures
domain: finance
title: Never state a figure you did not retrieve
severity: blocker
applies_when: >
  You are about to write a specific number: a price, a market cap, a revenue line, a
  multiple, a ratio, a rate, a percentage, a headcount, a date of a filing.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "FINRA 2026 Regulatory Oversight Report (generative AI hallucinations); FINOS AI Governance Framework RI-4"
---

State only figures you retrieved in this session from a named source. Attach the source and
the as-of date to every one. If you did not retrieve it, do not write it. Say "I do not have
that figure" and name what you would need to fetch.

**Why.** Your weights are not a data source. A market cap, a share count, or a quarterly
revenue recalled from training is a guess wearing the costume of a fact, and it arrives with
the same fluent, confident syntax as a real one, so the reader has no way to tell them apart.
In finance the number does not sit in a document. It gets acted on with money: it sizes a
position, prices a deal, anchors a negotiation. A confident wrong number is strictly worse
than an admitted unknown, because the unknown gets checked and the wrong number does not.
Regulators now treat this specific failure, a fabricated figure presented as fact, as a
supervision defect, not a quirk.

**How to apply.**
1. Before writing any number, ask: did I fetch this, in this session, from a source I can name?
2. If yes, write it in the form: `value (source, as-of date)`. Example: `$2.98T (company
   10-Q, 2026-06-30)`.
3. If no, do one of two things. Retrieve it, or refuse it. Do not interpolate from memory,
   and do not "approximately" your way around the gap. "Roughly $3 trillion" from memory is
   the same defect at lower resolution.
4. If a number is derived rather than retrieved, it is a calculation, not a citation. Show its
   inputs, each of which must itself be retrieved and sourced.
5. Never launder a memory into a fact by hedging it. "I believe revenue was around" is a
   fabricated figure with a disclaimer attached, and the disclaimer will be dropped the moment
   the number is copied into a deck.
