---
type: concept
title: "SEO Drift Monitoring"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - seo
  - monitoring
  - change-detection
status: evergreen
related:
  - "[[Claude SEO]]"
  - "[[Pro Hub Challenge]]"
---

# SEO Drift Monitoring

"Git for SEO" — captures baselines of SEO-critical page elements, then diffs against current state to detect regressions. Contributed to [[Claude SEO]] v1.9.0 by Dan Colta.

## What It Tracks

17 comparison rules across 3 severity levels:

| Severity | Examples |
|----------|----------|
| CRITICAL | Schema removed, canonical changed, noindex added, H1 removed |
| WARNING | Title changed, CWV regression >20%, meta description changed |
| INFO | H2 structure changed, content hash changed, image count changed |

## Architecture

- **SQLite persistence** at `~/.cache/claude-seo/drift/baselines.db`
- **4 Python scripts**: `drift_baseline.py` (capture), `drift_compare.py` (diff), `drift_report.py` (HTML report), `drift_history.py` (timeline)
- **Security-hardened**: uses only `fetch_page.py` for URL fetching (SSRF-protected). Original submission had a curl fallback that bypassed SSRF protection — completely removed during integration.

## Commands

```
/seo drift baseline <url>    # Capture current state
/seo drift compare <url>     # Compare against baseline
/seo drift history <url>     # Show all checks over time
```
