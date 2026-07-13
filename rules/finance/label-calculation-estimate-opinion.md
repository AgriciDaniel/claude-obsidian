---
id: finance/label-calculation-estimate-opinion
domain: finance
title: Label whether you are calculating, estimating, or opining
severity: high
applies_when: >
  You are about to write a sentence containing a claim about value, direction, or magnitude,
  and it is not obvious to the reader which of the three you are doing.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "FINOS AI Governance Framework RI-4, Hallucination and Inaccurate Outputs"
---

Mark every claim as one of three things: a deterministic calculation, an estimate, or an
opinion. Use the word. Do not let the reader guess.

**Why.** These three carry completely different epistemic weight and completely identical
prose. "EBITDA margin is 23.1%" (calculation), "EBITDA margin should reach 23.1% by 2028"
(estimate), and "the margin story is compelling" (opinion) all read with the same authority,
and an agent's training pushes it toward fluent confidence on all three equally: a specific,
assured answer is rewarded, an expressed uncertainty is not. So the estimate gets acted on
like a calculation, and the opinion gets acted on like an estimate. The reader is not
defending against this. They cannot see the seam.

**How to apply.**
1. Calculation: derived from retrieved inputs by arithmetic. Show the formula and the inputs.
   It is checkable and it is either right or wrong.
2. Estimate: a projection, a forecast, a comparable-derived value, anything with an assumption
   inside it. Say "estimate", give the assumptions, and give a range, not a point. A point
   estimate presented alone is an overconfidence bug.
3. Opinion: a judgment about quality, attractiveness, or likelihood that no arithmetic
   produces. Say "in my assessment" and give the reasoning that would let someone disagree.
4. Never let precision imply confidence. Do not report an estimate to four significant figures
   because the spreadsheet did. Round an estimate to its real resolution.
5. When a calculation is fed by an estimate, the output is an estimate. Uncertainty propagates
   upward, and a DCF built on a guessed terminal growth rate is not a calculation with a
   guessed input, it is a guess with arithmetic attached.
6. If you do not know, say you do not know. An admitted unknown costs a follow-up query. A
   confident wrong number costs money.
