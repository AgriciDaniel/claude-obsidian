---
type: substrate
substrate: "Anodiserad aluminium"
category: metal-treated
primer_pct: 40
white_combined_pct: 210
white_per_channel_pct: 70
cmyk_pct: 80
tac_pct: 300
dwell_s: 6
difficulty: easy
adhesion_test_target: "5B"
status: tested
created: 2026-05-01
updated: 2026-05-01
last_successful_job: null
last_failed_job: null
related:
  - "[[onyx-setup-reference]]"
  - "[[dopplackad-metall]]"
tags:
  - substrate
  - metal
  - aluminum
  - anodized
---

# Anodiserad aluminium

Förlåtande substrat. Anodiseringsskiktet (porös oxid) griper bläcket mekaniskt — en av de bästa metallerna för UV-tryck.

## Settings

| Parameter | Värde |
|---|---|
| Primer | 40% |
| White combined | 210% |
| Per white-kanal | 70% |
| CMYK | 80% |
| TAC per strike | 300% |
| Inter-layer dwell | 6s |
| Adhesion test mål | 5B |

## Yt-prep

1. IPA wipe (samma protokoll som dopplackad metall)
2. **INTE scuffa** — anodiseringen ÄR vidhäftningskeyen, sliter du av den blir det sämre
3. Hantera med handskar

## Anteckningar

Oxidlagret är poröst → bläck förankrar mekaniskt → bra adhesion även med moderat primer. Färgen kan dock skifta något pga oxidlagrets transparens (anodiserade material är ofta lätt translucenta i ytskiktet).

Bygg separat ICC-profil för varje anodiseringsfärg (klar/svart/färgad anodisering ger olika optiska egenskaper).
