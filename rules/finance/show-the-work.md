---
id: finance/show-the-work
domain: finance
title: Show the formula and the inputs, not just the output
severity: high
applies_when: >
  You are about to report a computed result: a valuation, a return, a growth rate, a margin, a
  multiple, an NPV, an IRR, a weighted average.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "CFA Institute Standards of Professional Conduct V(A) Diligence and Reasonable Basis"
---

Report every computed figure with the formula that produced it and the inputs that fed it. A
number the reader cannot reconstruct is not a finding, it is a claim.

**Why.** An unauditable number is worthless in finance, because its whole value lies in being
checkable. The reader's job is to disagree with your inputs, and they cannot do that if the
inputs are inside your head. Worse, a bare output hides its own errors: a fat-fingered
discount rate and a correct one produce equally plausible-looking NPVs, and only the visible
arithmetic tells them apart. The cost of hiding the work is not aesthetic. It is that a wrong
number survives review.

**How to apply.**
1. State the formula before the result. `EV/EBITDA = EV / LTM EBITDA`, then the substitution,
   then the number.
2. List every input with its own source and as-of date. If an input is itself derived, chain
   down to the retrieved figures at the bottom.
3. Show the substitution, not just the symbols. `= 48,200 / 3,150 = 15.3x` lets a reader catch
   in one second what a paragraph of description hides.
4. Name every assumption baked into the arithmetic: the discount rate, the terminal growth,
   the tax rate, the share count basis (basic or diluted), the period (LTM, NTM, fiscal or
   calendar).
5. When you use code, make the code the artifact. A cell the reader can rerun beats a number
   they must trust.
6. If a result is too complex to show inline, show it anyway, in an appendix or a table. Length
   is a cheaper cost than unfalsifiability.
