---
id: finance/guard-against-lookahead-bias
domain: finance
title: Guard against look-ahead and survivorship bias
severity: high
applies_when: >
  You are about to backtest a strategy, evaluate a historical period, screen a universe of
  past constituents, or explain why something did or would have happened.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "arXiv 2605.24564, Mitigating Look-Ahead Bias in Financial Backtesting with LLMs"
---

Before reporting any historical or backtested result, prove that no information from after the
decision date reached the decision, and that the universe includes the names that failed.
State both checks in the output.

**Why.** Look-ahead bias does not produce a wrong answer, it produces a beautiful one, and
that is what makes it lethal: a backtest that quietly saw the future returns a Sharpe ratio
nobody questions until it is traded. Survivorship bias does the same by deleting the losers
from the sample, so the strategy looks robust because the bankruptcies are simply not there.

There is a third form specific to you. Your weights have already read what happened. A model
trained through 2025 knows how NVIDIA and Netflix moved, so on any period inside your training
window you are retrieving the outcome, not predicting it, and no data-pipeline audit can see
this because the leak is not in the pipeline, it is in you. Under bias-corrected evaluation,
most LLM-derived alpha vanishes. Assume yours will too.

**How to apply.**
1. For every input, ask: was this knowable, in this form, at the decision timestamp? Restated
   financials, revised macro prints, and index membership assigned in hindsight all fail this.
2. Use point-in-time data with the correct publication lag. A quarter that reported six weeks
   after period end was not tradable on period end.
3. Build the universe from constituents as of the decision date, delisted and bankrupt names
   included. If your data provider dropped them, say so, and treat the result as an upper
   bound.
4. Declare the parametric leak. If the test period predates your training cutoff, say it
   plainly: results on this window are contaminated by model knowledge and are not evidence of
   predictive skill.
5. Prefer out-of-sample windows after your cutoff. When that is impossible, blind the inputs:
   strip names, tickers, and dates so you cannot recognize the episode.
6. Never write the causal story before the data. "The stock fell because of X" reconstructed
   after the fact is narrative, not analysis, and it is where hindsight enters the model.
