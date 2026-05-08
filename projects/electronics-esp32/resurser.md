---
type: project-note
title: "Resurser — ESP32 + elektronik + programmering"
project: electronics-esp32
created: 2026-05-03
updated: 2026-05-03
tags:
  - resources
  - learning
  - links
related:
  - "[[_index]]"
---

# Resurser

Kortlista på det jag faktiskt skulle använda. Inte uttömmande — utvalda för signal-noise-ratio.

---

## Svenska elektronikbutiker

| Butik | Bra för | Webb |
|---|---|---|
| **Electrokit** | Svenskt komponent-flaggskepp. Hyfsade priser, snabb leverans, allt finns. | electrokit.com |
| **Lawicel** | Mer industriellt utbud, bra för avancerade sensorer | lawicel.se |
| **Conrad** | Stort sortiment men dyrt; bra som backup | conrad.se |
| **Kjell & Co** | Konsument-grejer (kablar, USB-laddare) men inte komponenter | kjell.com |
| **AliExpress** | Billigaste, längsta leveranstid (~3 veckor till Sverige). Bra för "köpa 10 st av samma sak" |  |

**Rekommendation**: Electrokit för 90% av dina inköp i lärandefasen. När du vet vad du behöver, AliExpress för bulk.

---

## YouTube-kanaler (engelska)

| Kanal | Bra för |
|---|---|
| **Andreas Spiess** | "The guy with the Swiss accent". ESP32-fokus, djup teknisk men begriplig. Bästa kanalen för seriös ESP32. |
| **DroneBot Workshop** | Långa, välproducerade tutorials. Bra för att fasa in nya koncept. |
| **GreatScott!** | Tysk maker. Lite kortare, mer projekt-fokus. |
| **ElectroBOOM** | Underhållande + lärorik om vad man INTE ska göra. |
| **Bitluni** | Avancerade ESP32-projekt — bra när du växt ur tutorials. |

---

## Böcker

| Bok | Vad |
|---|---|
| **"Practical Electronics for Inventors" (Scherz & Monk)** | Standardreferens. Tjock men värd det. ~600kr. |
| **"Programming the ESP32" av Andreas Spiess** | Direkt-anpassad till ESP32, hyfsad nybörjar-kurva. |
| **"MicroPython Cookbook"** | Recept-format, bra som uppslagsverk. |

För svenska: jag känner inte till någon bra svensk ESP32-bok. Engelska är standarden i hobby-elektronik.

---

## Online-tutorials & dokumentation

| Resurs | Vad |
|---|---|
| **micropython.org/docs** | Officiell dokumentation. Stötandet-svår första gången, men du kommer dit. |
| **randomnerdtutorials.com** | Mest utförliga gratis-tutorials online. Sök "RandomNerdTutorials ESP32 [vad du vill göra]" som default. |
| **lastminuteengineers.com** | Snabba tutorials, ofta bilder + kod-exempel. |
| **forums.adafruit.com** | Bra Q&A för svåra problem. |
| **r/esp32** (Reddit) | Aktivt community, snabba svar. |

---

## Programmeringslärande (utöver ESP32)

Eftersom du vill växa generellt:

| Resurs | Vad |
|---|---|
| **Python.org tutorial** | Officiell, kort, gratis. Klar på 4–6 timmar. |
| **Real Python** (realpython.com) | Bredare Python-fokus, många artiklar gratis. |
| **Automate the Boring Stuff** (gratis online: automatetheboringstuff.com) | Praktisk Python för icke-programmerare. Klassiker. |
| **Codecademy** | Strukturerade kurser, bra för disciplin. Betald. |

För svenska: **Codeacademy.se** finns men är begränsad. Kodboken.se har grundkurser.

---

## Communities

| Var | Vad |
|---|---|
| **r/esp32** | Reddit, ~150k medlemmar. Engelska. |
| **r/learnpython** | Bra för Python-frågor utan att skämmas |
| **Hackster.io** | Projekt-galleri, inspiration |
| **/r/esp8266** | Lite äldre chip men många fortfarande där, många tutorials överlappar |
| **MicroPython Forum** | mer fokuserat än r/esp32 men aktivt |

Svenska: **Sweclockers Forum → Bygg & Mod** har en elektronik-tråd. Mindre aktiv men finns.

---

## Verktyg du kommer behöva (utöver kod-IDE)

| Verktyg | Pris | När du behöver det |
|---|---|---|
| **Multimeter** | 100–300kr | Direkt. Mätning av spänning, motstånd, kontinuitet. |
| **Lödkolv** (om du går bortom breadboard) | 200–500kr | Vecka 4–8. Permanenta lödningar. |
| **Logikanalysator** | 200–400kr (LA1010 eller liknande) | När du har konstiga buggar i I2C/SPI. Inte direkt. |
| **Oscilloskop** | 1500kr+ | Nice-to-have men inte nödvändigt det första året. |
| **3D-printern** | ✅ Du har | För att printa kapslingar, hållare, fixturer till dina ESP32-projekt. |

---

## Mitt råd för första 30 dagarna

1. **Köp ett ESP32-starter-kit från Electrokit** — har du redan ESP32 men ofta saknas LED, motstånd, breadboard. Cirka 250kr.
2. **Klar [[projekt-1-blinka]] första kvällen.** Inte fundera, bara följa stegen.
3. **Följ en RandomNerdTutorial-guide** för "ESP32 Wi-Fi" andra kvällen. Få det att fungera. Förstå inte allt — det är ok.
4. **Skriv om en av deras tutorials med din egen kod, inte copy-paste.** Det är där lärandet sitter.
5. **Logga vad du gör i Obsidian** — den här mappen är just till för det. Skapa en `loggbok.md` om du vill.

Du behöver ingen kurs. ESP32-communityn är så stor och tutorials så bra att du kan lära dig själv om du bara håller momentum.
