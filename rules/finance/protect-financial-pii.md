---
id: finance/protect-financial-pii
domain: finance
title: Do not transmit identifiable financial data without explicit consent
severity: blocker
applies_when: >
  You are about to paste, upload, or send data containing account numbers, balances, holdings,
  transactions, names, tax IDs, or salary figures into a web search, an API, a third-party
  tool, or any host the user did not name.
globs:
  - "**/*"
agents: [claude, cursor, windsurf, copilot, codex, gemini]
source: "FINRA 2026 Regulatory Oversight Report (unintended disclosure of sensitive data by AI agents)"
---

Stop before any egress of identifiable financial data. Ask for explicit consent, naming the
exact destination and the exact fields that would leave. Absent a clear yes, redact or work
locally.

**Why.** Egress is irreversible. A position file pasted into a search query, a portfolio
uploaded to a charting service, a client name sent to an enrichment API: each of these leaks
data that cannot be recalled, and each is a disclosure event with consequences that land on
the user, not on you. The agent's failure mode here is not malice, it is helpfulness. Reaching
for a third-party tool to enrich a ticker list feels like good service right up to the moment
the ticker list is someone's actual holdings.

**How to apply.**
1. Before any outbound call, scan the payload for: account numbers, balances, holdings and
   position sizes, transaction histories, counterparty names, tax identifiers, compensation.
2. If any are present, do not send. Ask first, and be specific: name the destination host and
   list the fields that would leave.
3. Prefer local computation. Most analysis on a holdings file needs no network at all.
4. When you need external data about the securities, send the ticker, not the position. Query
   the instrument, never the exposure.
5. Redaction is the default fallback, not the exception. Strip identifiers, aggregate, or
   substitute placeholders, then proceed.
6. Silence is not consent, and neither is the user having handed you the file. Giving you data
   to analyze is not giving you permission to forward it.
