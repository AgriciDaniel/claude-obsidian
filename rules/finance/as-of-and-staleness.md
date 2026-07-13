---
id: finance/as-of-and-staleness
domain: finance
title: Timestamp market data; stale presented as live is a defect
severity: high
applies_when: >
  You are about to present a price, a yield, a rate, an FX cross, an index level, or any
  quantity that moves during a trading day.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "FINRA 2026 Regulatory Oversight Report (inaccurate market data impacting decision making)"
---

Carry the as-of timestamp on every market data point, and say what it is: live, delayed,
prior close, or historical. Never let a stale figure read as a current one.

**Why.** Market data decays in seconds. A quote from Friday's close presented in a Tuesday
memo as "the price" is not slightly wrong, it is a different number, and any spread, ratio, or
valuation built on top of it inherits the error silently. The defect is rarely the retrieval.
It is the presentation: the timestamp gets dropped somewhere between the fetch and the
sentence, and a stale number, once undated, is indistinguishable from a live one forever
after.

**How to apply.**
1. Write the as-of with the value, always: `$412.30 (prior close, 2026-07-10)`. Not `$412.30`.
2. Say which regime the data is in. Real-time, 15-minute delayed, prior close, or end-of-day
   are four different claims and are not interchangeable.
3. If the data is older than the decision horizon it feeds, flag the gap explicitly rather
   than quietly using it. A weekly close is fine for a five-year DCF and useless for an
   execution decision.
4. Timestamp the derived figures too. A P/E built from Monday's price and last quarter's EPS
   is as-of both, and both belong in the note.
5. If you cannot establish an as-of date for a figure, you do not have the figure. Treat it as
   unretrieved.
6. Never source a price from your training data. Your cutoff is not a timestamp, it is a
   horizon, and prices past it are unknowable to you.
