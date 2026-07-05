---
title: JobFilter — Project Index
created: 2026-07-05
updated: 2026-07-05
type: entity
tags: [project, saas, trades, leads, birmingham]
---

# JobFilter

> High-quality job leads for UK tradesmen. Filter real work from noise.

**GitHub:** https://github.com/manazoid4/JobFilterV1  
**Local:** `C:\Users\manaz\Desktop\JobFilter`  
**Stack:** React 19 + Vite 6 + Express + Firebase + Stripe + Tailwind v4  
**Status:** Pre-launch / active development (#1 priority)  
**Live URL:** TBD (hosted on Firebase Hosting)

---

## What it does

- Tradesman signs up → sets their trade + postcode
- App scans public procurement sources (FTS, Contracts Finder, Sell2Wales, PCS) + internal leads
- Leads are scored 0–100 with reason codes
- Free tier: 3 leads; paid: unlimited with priority
- WhatsApp intake state machine collects homeowner job requests
- Stripe handles subscriptions + priority pass one-off payments
- Email alerts via Resend on new lead matches

## Notes index

| Note | Description |
|---|---|
| [[wiki/projects/jobfilter/ARCHITECTURE]] | Modules, data flow, server routes |
| [[wiki/projects/jobfilter/DATA-MODEL]] | Firestore collections, lead schema |
| [[wiki/projects/jobfilter/API]] | API routes, webhook endpoints |
| [[wiki/projects/jobfilter/SETUP]] | Local dev setup |
| [[wiki/projects/jobfilter/DEPLOYMENT]] | Firebase hosting, CI/CD |
| [[wiki/projects/jobfilter/DECISIONS]] | Key technical tradeoffs |
| [[wiki/projects/jobfilter/TODO]] | Pending tasks and blockers |
