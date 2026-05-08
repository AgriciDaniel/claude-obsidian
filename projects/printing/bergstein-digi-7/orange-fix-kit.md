---
type: project-reference
title: "Orange-fix kit — Bergstein Digi 7 + Onyx 2015"
project: bergstein-digi-7
domain: uv-printing
created: 2026-05-03
updated: 2026-05-03
tags:
  - first-aid
  - orange
  - color-fix
  - onyx-2015
related:
  - "[[onyx-setup-reference]]"
  - "[[linearization-cheatsheet]]"
  - "[[color-tests/orange-diagnos-100x100|test-pattern]]"
---

# Orange-fix kit

För dig att jobba igenom i morgon. Test-pattern + diagnos-flöde + exakta värden + spektro-targets. Allt på ett ställe.

> Symptom: orange (C0 M75 Y100 K0) blir blekare och mer gul än den ska på dopplackad metall.

> **VIKTIGT**: Bergstein Digi 7 har **7 fysiska M-heads parallellt**. När magenta är svag är det oftast 1–2 av de 7 som är partiellt tilltäppta — inte alla. Diagnosen är därför per-head, inte per-färg. Det förklarar exakt ditt symptom: en clogged M-head av 7 ger ~86% magenta-leverans → orange skiftar mot gul, blir blekare.

---

## Steg 0 — Per-head nozzle check (gör detta FÖRST)

Innan du printar test-pattern eller mäter med spektro: kolla om det är en eller flera M-heads som har problem. Det är **det troligaste fyndet**.

1. **Skrivarens meny → Maintenance → Nozzle Check** (eller motsvarande på Bergstein)
2. Det printar en testbild med alla 56 kanaler separata
3. Studera M-sektionen specifikt — alla 7 raderna ska se identiska ut
4. Leta efter:
   - **Saknade linjer** i en specifik M-rad → den heads nozzles är blockerade
   - **Bleknade linjer** i en eller flera M-rader → den heads ink-flöde är reducerat
   - **Skeva eller dubbelaktiga linjer** → head misalignment
5. **Notera vilken M (M1–M7) som har problem**

**Om en eller flera M-heads har luckor:**

→ Hoppa direkt till **FIX C — head clean** (uppdaterad nedan). Du behöver inte mäta spektro eller printa test-pattern först. Rengör först, mät sen.

**Om alla 7 M-heads ser fina ut:**

→ Fortsätt till Steg 1 (test-pattern). Då är problemet linearization eller render intent, inte ett fysiskt head-problem.

---

## Steg 1 — Print test-pattern

**Fil:** [`color-tests/orange-diagnos-100x100.svg`](color-tests/orange-diagnos-100x100.svg)

Kör i Onyx 2015 med:

- Profil: din nuvarande dopplackad-metall-profil (samma du har problem med)
- Print mode: 360 × 360, 4-pass bidi, full layer stack (primer + 3W + CMYK)
- Storlek: 100% (100 × 100 mm), inte skalad
- Substrat: dopplackad metall, samma batch som din problem-print

Cura helt. Vänta 24h innan du mäter med spektro.

---

## Steg 2 — Mät / observera

Patternen har 6 sektioner. Här är vad varje säger dig.

### Rad 1 — Magenta-ramp

Mät L\* på varje ruta (eller jämför visuellt mot M-ramp i en Pantone-bok om du har).

**Förväntat:**

| Ruta | L\* (ungefär) | a\* (ungefär) |
|---|---|---|
| 0% | 90+ (substrat-färg) | nära 0 |
| 25% | 70–75 | +25 till +35 |
| 50% | 60–65 | +45 till +60 |
| 75% | 55–60 | +60 till +75 |
| 100% | 46–50 | +70 till +80 |

**Röda flaggor:**

- Om 100%-rutan inte är märkbart mörkare än 75% → magenta-cap är för låg ELLER huvudet är clogged
- Om kurvan inte är jämn (t.ex. 50% är nästan lika mörk som 75%) → linearization-drift på M
- Om a\* ligger lågt över hela rampen → magenta-blecket är ovanligt blekt (batch-problem eller cure-problem)

### Rad 2 — Yellow-ramp (referens)

Samma test för gul. Eftersom gul oftast är den mest stabila kanalen är detta din "kontrollgrupp". Om Y-rampen ser fin ut men M-rampen är skev → problemet är specifikt magenta.

**Förväntat 100%Y:** L\* runt 88–90, b\* runt +90 till +95.

### Rad 3 — Orange-svep

Detta är diagnos-grejen. Fem oranger med varierande magenta från 50% till 100%, alla med Y=100%.

Den ruta som **visuellt matchar din kund/referens-orange** säger vad magenta FAKTISKT lägger på just nu.

**Tolkning:**

| Visuell match | Vad det betyder |
|---|---|
| Din "M75"-ruta i mitten matchar referens | Allt är OK, problemet ligger i din original-fil eller designern |
| Din **M85**-ruta matchar referens | Magenta levererar ~10% mindre än angett → re-linealisera M, eller höj M-cap |
| Din **M100**-ruta matchar referens | Magenta levererar ~25% mindre → allvarlig drift, troligen clogged head + linearization |
| Din **M65**-ruta matchar referens | Magenta levererar ~10% MER än angett → mindre vanligt, men sänk M-cap eller re-linealisera |

### Rad 4 — Reference solids

Snabbcheck att alla rena kanaler beter sig OK.

**Spektro-mål 100% solids:**

| Kanal | L\* | a\* | b\* |
|---|---|---|---|
| 100% C | 55 ± 5 | -35 till -25 | -45 till -35 |
| 100% M | 47 ± 5 | +75 till +85 | -10 till 0 |
| 100% Y | 88 ± 5 | -10 till -5 | +90 till +98 |
| 100% K | 16 ± 5 | nära 0 | nära 0 |

Avvikelse på någon = den kanalen är problematisk.

### Rad 5 — Vit-underbas-test

Tre oranger med olika underliggande vit-täckning. Om ditt problem är att vit-underbasen är för låg, så ser du:

- "vit 150%" — märkbart mörkare och mer dämpad
- "vit 200% (din)" — mellanläge
- "vit 250%" — ljusast och mest mättat

Om "vit 250%"-rutan ser **drastiskt** mer rätt ut än din nuvarande 200% → höj vit-underbasen, antingen permanent i media-profilen eller per jobb.

### Rad 6 — Kvantitativa mål

Mät M75 Y100-rutan i rad 3 med spektrot. Jämför mot:

```
Förväntat: L* ≈ 60–65   a* ≈ +45 till +55   b* ≈ +60 till +75
```

**Om a\* < +40:** magenta för svag (förklarar "för gul")
**Om L\* > 70:** för ljus (förklarar "blekare")
**Om både:** kombinerat magenta-svaghet → fix på M-kanalen

---

## Steg 3 — Diagnos-flowchart

```
Print test pattern
       │
       ▼
M-ramp jämn och 100%M är mörk?
       │
   NEJ ─┴─ JA
   │       │
   │       ▼
   │   Y-ramp jämn?
   │       │
   │   NEJ ┴─ JA
   │       │   │
   │       │   ▼
   │       │  M75 Y100-ruta visuellt rätt orange?
   │       │       │
   │       │   NEJ ┴─ JA
   │       │       │   │
   │       │       │   ▼
   │       │       │  Problem ligger i source-fil eller render intent.
   │       │       │  → Kolla original-PDF eller render intent (relativ kolorimetrisk)
   │       │       │
   │       │       ▼
   │       │  Vit-underbas-rad ger märkbar skillnad?
   │       │       │
   │       │   NEJ ┴─ JA
   │       │       │   │
   │       │       │   ▼
   │       │       │  Höj vit-underbas → FIX A
   │       │       │
   │       │       ▼
   │       │  Tillämpa Color Adjustment Curve (M-justering) → FIX B
   │       │
   │       ▼
   │   Y-kanal har också drift → Re-linealisera HELA profilen → FIX D
   │
   ▼
M-kanalen är trasig.
   │
   ▼
Nozzle check med luckor i M-raden?
   │
   JA ┴─ NEJ
   │     │
   │     ▼
   │   Linearization-drift på M.
   │   → Höj M-cap i Ink Restriction → FIX A2
   │   → Eller re-linealisera M → FIX D
   │
   ▼
Head clog. → Kör head clean-cykler 1-2 ggr → kör nozzle check igen → FIX C
```

---

## Steg 4 — Fixar med exakta värden

### FIX A — Höj vit-underbas (om vit är boven)

**Permanent (rekommenderat):**

1. Onyx → **Profile Manager** → öppna dopplackad-metall-profilen
2. **Ink Restriction-fliken**
3. Hitta dina vit-kanaler (troligen C6, C7, C8)
4. Höj varje från **65%** till **77%**
5. Total kombinerad vit blir då 231% (77 × 3)
6. **Save**

Total uppdatering i [substrate-noten](substrates/dopplackad-metall.md):

```yaml
white_combined_pct: 230  # uppdaterat från 200
white_per_channel_pct: 77  # uppdaterat från 65
```

### FIX A2 — Höj M-cap (om M är capad lägre än Y)

1. Profile Manager → din profil → **Ink Restriction-fliken**
2. Hitta M-kanalen (troligen C2)
3. Notera nuvarande värde (säg 70%)
4. Höj till samma som Y-kanalens cap (säg Y är 80% → höj M till 80%)
5. **Save**
6. Om bläcket börjar puddla på testbiten → sänk med 5% och försök igen

### FIX B — Color Adjustment Curve (per jobb, snabb)

Onyx → Job Editor → öppna ditt orange-jobb → **Color Adjustments → Tone Curves**

Välj **M-kanalen**. Lägg till tre kurv-punkter:

| Input | Output |
|---|---|
| 0% | 0% |
| 25% | 27% |
| 50% | 55% |
| 75% | **85%** ← den viktiga |
| 100% | 100% |

Det här "boostar" M ungefär 10% i mid-range där din orange ligger. Förmodligen tillräckligt för att fixa just det här jobbet.

**Använd bara per jobb** — inte permanent. Permanent fix är linearization eller cap-justering.

### FIX C — Head clean (uppdaterad för 7-head-setup)

På Bergstein:

1. **Identifiera vilket M-head (M1–M7) som har problem** från nozzle check (Steg 0)
2. Skrivarens egen meny → Maintenance → Head Clean
3. **Om Bergstein har "per-head clean"-funktion**: välj specifikt det krånglande huvudet (t.ex. "Clean M3"). Mer effektivt och sparar bläck.
4. **Om bara global clean finns**: kör en cykel som rengör alla M-heads samtidigt
5. Välj nivå: **light → medium → strong** (börja light, eskalera bara om light inte räcker)
6. Print nozzle check igen — kolla att den specifika rad som hade luckor nu är ren
7. Upprepa upp till 3 gånger om luckor kvarstår

**Om fortfarande luckor efter 3 strong cleans på samma head:**

- Det är troligen mer än bara mjuk pappersfiber/torkad ink — kan vara skadade nozzles eller ink-tilltäppning djupare
- Tillfällig workaround: sätt det specifika headets cap till **0%** i Onyx Ink Restriction och höj de andra 6 M-heads med 16–17% var ((100-0)/6 ≈ 17%) för att kompensera
- Långsiktig: kontakta Bergstein support för manuell rengöring eller head-byte

**Per-head bypass-konfiguration (tillfällig)**

Om M3 är trasigt och du behöver fortsätta produktion:

| Kanal | Normal cap | Bypass-cap (M3 ute) |
|---|---|---|
| M1 | 80% | 93% |
| M2 | 80% | 93% |
| **M3** | **80%** | **0%** ← bypass |
| M4 | 80% | 93% |
| M5 | 80% | 93% |
| M6 | 80% | 93% |
| M7 | 80% | 93% |

Detta är en **tillfällig produktion-fix**, inte en permanent lösning. De 6 friska headsen jobbar 17% hårdare än normalt → kan ge förkortad livslängd om kvar för länge. Få M3 reparerat så snart som möjligt.

### FIX D — Re-linealisera

Se [`linearization-cheatsheet.md`](linearization-cheatsheet.md). Steg-för-steg där.

För just M-kanalen utan att göra hela profilen om: i Calibrate-fliken, klicka bara "Linearize C2" om Onyx 2015 stödjer per-kanal-linealisering. Om inte → linealisera hela profilen.

---

## Steg 5 — Verifiera fixen

Efter du har applicerat en fix:

1. Print om test-patternen
2. Mät M75 Y100-rutan med spektrot
3. Jämför mot mål-värdena (L\* 60–65, a\* +45 till +55, b\* +60 till +75)
4. Om inom mål → fix funkar, applicera permanent
5. Om utanför mål → backa fixet, testa nästa i diagnos-flowcharten

---

## Tre saker du gör i morgon

1. **Print test-pattern på dopplackad metall.** Cura, vänta minimum 1h (idealt 24h innan spektro-mätning).
2. **Mät M75 Y100-rutan.** Säg L\*, a\*, b\*-värdena så pekar jag på exakt rätt fix.
3. **Print nozzle check parallellt.** Säg om M-raden har luckor.

Med L\*a\*b\*-värdet och nozzle check-resultatet är vi 5 minuter från permanent fix.
