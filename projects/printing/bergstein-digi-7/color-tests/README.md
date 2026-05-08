---
type: project-reference
title: "Färgtest v1 — användarguide"
project: bergstein-digi-7
domain: uv-printing
created: 2026-05-01
updated: 2026-05-01
tags:
  - project
  - printing
  - color-test
  - onyx
status: working-doc
related:
  - "[[onyx-setup-reference]]"
---

# Färgtest v1 — användarguide

Diagnostikchart för Bergstein Digi 7 med CMYK + Primer + 3 White vid 360 DPI på dopplackad metall. Skriv ut på din riktiga produktionsmedia, inte på papper, så blir testet relevant.

## Två versioner

| Fil | Storlek | När att använda |
|---|---|---|
| **`fargtest-100x100-v1.svg`** | 100 × 100 mm | **Standard.** Matchar Bergstein Digi 7:s 100×100mm print area i Onyx-inställningarna. Använd den här i normal produktion. |
| `fargtest-v1.svg` | A4 (210 × 297 mm) | Endast för referens / utskrift på större skrivare för manualpärm. Kommer inte rippa direkt på Bergsteinens 100×100-area. |

Den här guiden gäller båda versionerna — sektionerna är desamma, bara mer kompakta i 100×100-versionen (5 steg i ramper istället för 11, ingen process-combinations-sektion, mindre text).

---

## Vad testet är till för

Det här är ett **produktions-realistiskt diagnostikchart**. Det går igenom samma färghanteringspipeline som riktiga jobb (RGB → ICC → device CMYK), så det visar vad slutkunden får.

För **ren ink-kalibrering** (där du vill veta exakt hur mycket en specifik kanal lägger på vid 60% utan ICC-konvertering) använd Onyx inbyggda Phase 3 (Print Ink Restriction Test) och Phase 4 (Print Linearization Target) istället. De skickar pure device CMYK utan att gå genom ICC-profilen.

---

## Skriv ut den i Onyx

1. **Onyx Job Editor → Open File** (eller dra och släpp `fargtest-v1.svg` på job-fönstret).
2. Välj din aktiva media-profil för Bergstein Digi 7 + dopplackad metall.
3. Set print mode: 360 × 360 DPI, 4-pass bidi, full layer stack (primer + 3W + CMYK).
4. **Storlek: 100% (210 × 297 mm)**. Skala inte, då går mätningarna fel.
5. Print → Cure fully.
6. Vänta minst 24h innan du gör cross-hatch-testet i sektion 7.

---

## De 8 sektionerna och vad de fångar

| # | Sektion | Vad du kollar | Vad det betyder om det ser fel ut |
|---|---|---|---|
| 1 | CMYK ramps (0–100%) | Smidig övergång, ingen banding, jämn täthet | Banding → bidi-alignment fel; hopp i kurvan → linjärisering behöver göras om |
| 2 | White opacity wedge | Var slutar svart att synas igenom? | Det är din opacity-floor. Sätt produktions-vit till nivån strax över denna |
| 3 | Pure solids | Renhet hos C/M/Y/K, fullständig täckning hos W och primer | Smutsig solid → ink limit för hög, ink puddlar; svag solid → ink limit för låg |
| 4 | Process combinations | Att overprint ger förväntad sekundärfärg (C+Y = grön etc.) | Trapping-problem eller fel ICC; inte rätt sekundär = svår CMYK-balans |
| 5 | Grayscale neutralitet | Gråa rutor är neutrala, inget färgstick | Färgstick (vanligen blå eller grön) → ICC-profilen måste byggas om mot detta substrat |
| 6 | Hudtoner | Realistiska hudtoner, inga gröna eller orangea drag | Hudtoner ute → ICC behöver byggas om; vanligaste indikator för dålig profil |
| 7 | Vidhäftningstest | Cross-hatch + tape (ASTM D3359) → 5B mål | < 4B = öka primer eller bättra ytförberedelse. Se onyx-setup-reference för fullt protokoll |
| 8 | Upplösning + register | 2pt-text läsbar, hairlines synliga, registermärken centrerade | Suddig text → bidi/print mode för snabbt; register förskjutet → calibrera huvudpositionen |

---

## När ska du köra testet?

Kör det:

- **Vid varje ny mediaprofil** (efter Phase 1–7 i setup-walkthrough)
- **Vid varje ny ink-batch** (kemin kan skifta)
- **Vid varje ny substrat-batch** (lacker varierar)
- **Var 6:e månad** även om inget bytts (ICC-profiler driver)
- **Vid felsökning** när produktionsutskrifter ser konstiga ut

---

## Vad du behöver för att utvärdera

| Verktyg                                | Vad du gör med det                                                                          |
| -------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Ögonen**                             | 80% av defekter syns visuellt. Se sektion 1, 2, 5, 6                                        |
| **Cross-hatch + tape (3M Scotch 600)** | Sektion 7, 24h efter print                                                                  |
| **Spektrofotometer (i1Pro / eXact)**   | Mät delta-E på sektion 3 och 5 mot referens. Mål: ΔE < 3 på solid CMYK; ΔE < 2 på grayscale |
| **Magnifier 10x**                      | Sektion 8 hairlines + cross-hatch detaljgranskning                                          |
| **Svart referenskort**                 | Backa sektion 2 och 6 så du verkligen ser opaciteten                                        |

---

## CMYK-precision: viktigt att förstå

SVG-formatet är RGB-bara. Färgvärdena i denna fil är **RGB-approximationer** av ren CMYK:

- 100% C visas som `#00aeef` (≈ Pantone Process Cyan)
- 100% M visas som `#ec008c` (≈ Pantone Process Magenta)
- 100% Y visas som `#fff200` (≈ Pantone Process Yellow)
- 100% K visas som `#000000`

När Onyx ripper SVG:n går RGB-värdena genom din aktiva ICC-profil för att producera device CMYK. Det betyder att en "100% C"-ruta i SVG blir nästan-men-inte-exakt 100% C på utskriften (kan bli t.ex. 96C/4M/0Y/0K beroende på profilen).

**Detta är OK för visuell utvärdering** — du testar exakt den pipeline som produktionsjobb går genom. Men om du vill mäta exakt **hur mycket bläck** ditt 100%-värde lägger på för kalibreringssyften, använd Onyx Print Ink Restriction Test istället. Den skickar pure device-CMYK och bypassar ICC.

---

## Spara utskrifterna

1. Märk varje utskrift med datum, profil-namn, ink-batch på baksidan.
2. Förvara minst 3 senaste i en fysisk pärm bredvid printern.
3. Vid felsökning, lägg den nya utskriften bredvid det senaste goda batchet och jämför sektionerna A/B. Skillnader pekar direkt mot vad som driftat.

---

## Versioner

- **v1 (2026-05-01)**: initial diagnostikchart, 8 sektioner, A4 portrait. RGB-approximationer för CMYK.
- **v2 (planerad)**: PDF-version med device-cmyk() för precisa CMYK-värden, separata Pantone-referensrutor om du behöver matcha specifika spotfärger.
