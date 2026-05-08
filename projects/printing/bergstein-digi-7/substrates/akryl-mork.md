---
type: substrate
substrate: "Mörk/färgad akryl"
category: plastic-colored
primer_pct: 70
white_combined_pct: 250
white_per_channel_pct: 83
cmyk_pct: 80
tac_pct: 300
dwell_s: 6
difficulty: medium
adhesion_test_target: "5B"
status: tested
created: 2026-05-01
updated: 2026-05-01
last_successful_job: null
last_failed_job: null
related:
  - "[[onyx-setup-reference]]"
  - "[[akryl-klar]]"
tags:
  - substrate
  - plastic
  - acrylic
  - colored
---

# Mörk eller färgad akryl

Färgad akryl kräver maximal vit-täckning för att färgerna ovanpå ska se rätt ut. Substratfärgen lyser annars genom även 200%-vit på de mörkaste plattorna.

## Settings

| Parameter | Värde |
|---|---|
| Primer | 70% (högre än klar akryl — mörk yta = mer slät, mer behov av key) |
| White combined | **250%** (max) |
| Per white-kanal | 83% |
| CMYK | 80% |
| TAC per strike | 300% |
| Inter-layer dwell | 6s |
| Adhesion test mål | 5B |

## Yt-prep

Som klar akryl: IPA only, ingen aceton. Hantera med handskar.

## Anteckningar

Bygg separat ICC per akryl-färg. Svart akryl + 200% vit ger fortfarande svaga gråa toner i highlights eftersom den mörka substraten lyser igenom.

Om du planerar mycket mörk akryl: överväg en "dubbel-vit-strike"-mode i Onyx (en 250%-strike, härda fullt, sedan en till 200%-strike) för 100% blockerande täckning. Långsammare men ger trovärdiga vita highlights.

Kromade/metallfärgade akryl-typer kan reflektera UV tillbaka i tryckhuvudet — kör testbit innan stor batch så du inte får cure-problem.
