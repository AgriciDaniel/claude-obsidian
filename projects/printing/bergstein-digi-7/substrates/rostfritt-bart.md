---
type: substrate
substrate: "Rostfritt stål (bart)"
category: metal-bare
primer_pct: 80
white_combined_pct: 220
white_per_channel_pct: 73
cmyk_pct: 75
tac_pct: 280
dwell_s: 10
difficulty: hard
adhesion_test_target: "4B"
status: caution
created: 2026-05-01
updated: 2026-05-01
last_successful_job: null
last_failed_job: null
related:
  - "[[onyx-setup-reference]]"
tags:
  - substrate
  - metal
  - stainless
  - difficult
---

# Rostfritt stål (bart, otreated)

Svåraste UV-substratet. Slätt, kemiskt inert, hög ytenergi-kontrast. Primer-vidhäftning är aldrig given här.

## Settings

| Parameter | Värde |
|---|---|
| Primer | 80% (max) |
| White combined | 220% |
| Per white-kanal | 73% |
| CMYK | 75% (lite lägre — tunnare ink-film, bättre flex) |
| TAC per strike | 280% (lägre än andra metaller) |
| Inter-layer dwell | 10s |
| Adhesion test mål | 4B (5B är ovanligt) |

## Yt-prep (kritisk, mest demanding)

1. Avfettning: IPA + grundlig lufttorkning
2. Scuffa med 600-grit eller fin Scotch-Brite — mekanisk key är obligatoriskt
3. Andra IPA-runda för att ta bort slipdamm
4. **Aldrig** beröra ytan efter prep — handskar eller vakuumhantering

## Anteckningar

Om adhesion-test failar 4B även med full primer + perfekt prep: byt primer-formulering. Standard UV-primer fungerar inte alltid på rostfritt — be Bergstein eller bläckleverantören om en stainless-specifik primer (oftast en chromate- eller silane-baserad).

Konsumera aldrig produktionstid med rostfritt utan att ha kört adhesions-test 24h efter härdning. Misslyckad adhesion på rostfritt visar sig ofta först efter användning.
