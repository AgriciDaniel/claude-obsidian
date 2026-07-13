---
id: finance/units-currency-scale
domain: finance
title: Units, currency, and scale are load-bearing
severity: high
applies_when: >
  You are about to write a magnitude, compare two figures, or combine numbers that came from
  different tables, filings, or sources.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: ""
---

State the unit, the currency, and the scale on every figure. Never combine or compare two
numbers until you have confirmed that all three match.

**Why.** The most expensive errors in financial work are not subtle analytical mistakes, they
are unit mistakes, and they are off by a factor of a thousand. Millions read as billions.
Basis points read as percent, a 100x error that looks entirely reasonable on the page. Local
currency summed with USD. Thousands-scaled filing tables added to units-scaled ones. Each of
these is trivially preventable and each has moved real money, precisely because the resulting
number is not absurd enough to trip anyone's alarm.

**How to apply.**
1. Write the full unit every time: `EUR 1,240mm`, not `1,240`. `+35bps`, not `+35`.
2. Check the scale header on every source table before you read a value out of it. Filings
   routinely label tables "in thousands" and the label is far from the number.
3. Before any arithmetic across sources, verify unit, currency, and scale agree. If they do
   not, convert explicitly and show the conversion and its rate, with the rate's as-of date.
4. Never mix percent and basis points in one sentence, one table, or one chart axis. Pick one
   and convert the rest.
5. Name the currency basis for anything cross-border: reporting currency, functional currency,
   or converted, and at which rate (spot, average, period-end).
6. Say the period basis out loud: LTM, NTM, fiscal year, calendar year, quarter annualized. A
   fiscal year that ends in June is not a calendar year, and comparing them is a category
   error dressed as a growth rate.
