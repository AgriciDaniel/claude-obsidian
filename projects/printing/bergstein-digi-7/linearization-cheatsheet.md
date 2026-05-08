---
type: project-reference
title: "Linearization cheat sheet — Onyx 2015"
project: bergstein-digi-7
domain: uv-printing
created: 2026-05-03
updated: 2026-05-03
tags:
  - cheatsheet
  - linearization
  - onyx
  - calibration
related:
  - "[[onyx-setup-reference]]"
---

# Linearization cheat sheet

Snabb referens. Hänger vid skrivaren. Print ut den om du vill.

---

## När

- Var 3:e månad
- Efter ink-batch-byte
- Efter huvudservice
- När färger blir konstiga

---

## Steg för Onyx 2015

1. **Profile Manager → öppna media-profilen → Calibrate-fliken**
2. **Print Linearization Target** → välj produktions-mode (360 4-pass, alla lager)
3. Cura, vänta 15+ min
4. Mät med spektro **eller** ögonjämför mot referens
5. **Apply / Save** → Onyx bygger ny kurva
6. Print testbild → verifiera

---

## Vad du letar efter på linearization-printen

| Position | Ska se ut |
|---|---|
| 0% (omarkerad ruta) | Ren substrat-färg |
| 25% | Tydligt synlig men ljus |
| 50% | Halva mättnaden av 100% |
| 75% | Tydligt mörkare än 50%, lite ljusare än 100% |
| 100% | Maximalt mättad / mörk det här bläck-substrat-paret kan ge |

**Röd flagga:** om 75% och 100% ser nästan likadana ut → den kanalen mättas ut för tidigt → cap på Ink Restriction är för låg, eller bläcket puddlar.

---

## Per-kanal-checklista

För varje kanal (cirka 8 st i ditt setup):

- [ ] **C1 (Cyan)**: jämn progression från ljus till mättad
- [ ] **C2 (Magenta)**: jämn, ren rosa-magenta vid 100%
- [ ] **C3 (Yellow)**: jämn, ren gul (lätt orange-aning är OK för UV)
- [ ] **C4 (Black)**: djupt svart vid 100%, tydlig grå-skala
- [ ] **C5 (Primer)**: visuellt nästan osynlig (eftersom färglös), kolla ytstruktur istället
- [ ] **C6/C7/C8 (White)**: tydlig opacitet vid 100% mot mörkt substrat

---

## Verifierad bra-print

Spara alltid en bit av en lyckad linealisering med datum + ink-batch-info som referens:

```
Datum: ____________
Ink-batch: ________
Substrat: dopplackad metall
Profil: _______________
Anteckning: ____________
```

Lägg fysiskt i pärm vid skrivaren. Använd som visuell referens vid nästa linealisering.

---

## Vanliga problem och fix

| Problem | Trolig orsak | Fix |
|---|---|---|
| 100% ser ut som 75% | Ink limit för låg | Höj cap i Ink Restriction |
| Kurvan är extremt böjd | Stor ink-batch-skillnad | Re-linealisera och dokumentera nya batch |
| Linearization "tappar" efter en vecka | Head clogging eller drift | Daily nozzle check + clean |
| Visuell jämförelse är opålitlig | Saknar spektro | Investera i i1Pro begagnad |
| Vissa kanaler driftar mycket mer | Specifik ink-typ instabil | Re-linealisera oftare på den kanalen |

---

## Spektrofotometer-länkar (köp)

- [Tradera — i1Pro begagnade](https://www.tradera.com/search?q=i1Pro)
- [X-Rite Sweden — nya](https://www.xrite.com/sv/categories/calibration-profiling)
- [Lawicel — leverantör i Sverige](https://lawicel.se)

Spektrot löser 80% av "konstig färg"-problem permanent. Värt investeringen om du printar dagligen.
