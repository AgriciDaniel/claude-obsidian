---
type: index
title: "Substrate-databas — Bergstein Digi 7"
created: 2026-05-03
updated: 2026-05-03
related:
  - "[[onyx-setup-reference]]"
  - "[[../substrates|substrates.base]]"
tags:
  - index
  - substrate
---

# Substrate-databas

Sökbar databas över alla substrat ni printar på, med Onyx-startvärden + adhesion-test-historik per substrat.

**Hur du använder den:**

1. Öppna `substrates.base` (i mappen ovanför) — den renderar automatiskt som tabell i Obsidian
2. Filtrera, sortera, sök tabellen som du vill
3. Klicka på ett substrat-namn för att se hela noten med detaljer
4. När du gör ett lyckat jobb: uppdatera `last_successful_job` i den substrat-noten med datum + jobb-ID
5. Vid failat jobb: uppdatera `last_failed_job` + lägg till en kort anteckning om vad som gick fel

## Substrat just nu

| Substrate | Svårighet | Status |
|---|---|---|
| [[dopplackad-metall]] | Easy | Production |
| [[anodiserad-aluminium]] | Easy | Tested |
| [[bar-aluminium]] | Medium | Tested |
| [[rostfritt-bart]] | Hard | Caution |
| [[malad-metall]] | Easy | Tested |
| [[glas]] | Medium | Tested |
| [[akryl-klar]] | Easy | Tested |
| [[akryl-mork]] | Medium | Tested |

## Lägg till nytt substrat

Kopiera en befintlig substrat-not (närmaste typ — t.ex. en metall-not för ett nytt metall-substrat), döp om filen, uppdatera frontmatter-fälten:

- `substrate:` — namn
- `category:` — kategori (`metal-bare` / `metal-coated` / `metal-treated` / `glass` / `plastic-clear` / `plastic-colored`)
- `primer_pct`, `white_combined_pct`, etc. — start-värden
- `difficulty:` — `easy` / `medium` / `hard`
- `status:` — `untested` / `tested` / `production` / `caution`

Spara → den dyker upp automatiskt i `substrates.base`-tabellen.

## Vyer i databasen

`substrates.base` har fyra inbyggda vyer:

1. **Alla substrat** — fullständig översikt
2. **Endast metall** — filtrerar bara metallbaserade substrat
3. **Snabbreferens (produktion)** — kompakt tabell med bara start-värden, för en blick under en jobb-uppstart
4. **Job-historik** — vilka substrat har lyckats/failat senast, sorterat på datum

Du kan lägga till egna vyer genom att redigera `substrates.base` direkt i Obsidian.
