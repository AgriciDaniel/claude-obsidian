---
type: project-note
title: "10 ESP32-projekt för Bambu-skrivaren"
project: electronics-esp32
created: 2026-05-03
updated: 2026-05-03
tags:
  - project-ideas
  - bambu
  - esp32
  - integration
related:
  - "[[_index]]"
  - "[[projekt-1-blinka]]"
---

# 10 ESP32-projekt för Bambu-skrivaren

Sorterade i ordning från "kan göras vecka 2" till "kan göras månad 6". Varje projekt bygger på de föregående, så du växer kontinuerligt.

---

## ★ Beginner (vecka 2–4)

### 1. LED-notifikation: print klar
**Vad det är**: En extern LED-stripe (eller en enkel LED) som lyser grönt när printen är klar, rött om den failat.

**Hur det funkar**: ESP32 ansluter via WiFi till Bambus MQTT-API (Bambu skickar status-events). När den ser "print finished" tänds grönt.

**Du lär dig**: WiFi-anslutning, MQTT-grunderna, parsa JSON, GPIO-styrning från events.

**Komponenter**: ESP32, 1 RGB-LED (eller WS2812 strip), 3 motstånd. ~50kr.

**Värde**: ingen mer "är printen klar?"-pendling till verkstaden. Du ser från andra rummet.

---

### 2. Temp + luftfuktighet i kapsling
**Vad det är**: DHT22-sensor monterad i printkapslingen, ESP32 läser värdena, OLED-skärm visar dem live.

**Hur det funkar**: Sensorn skickar digital data till ESP32 var 2:a sekund. ESP32 visar på 0.96-tums OLED-skärm.

**Du lär dig**: I2C-kommunikation, sensor-bibliotek, OLED-rendering, datalogging.

**Komponenter**: DHT22 (~70kr), 0.96" OLED I2C (~80kr), några wires.

**Värde**: kritiskt för PLA i fuktig miljö → du ser direkt om filamentet är torrt nog att printa. Logga över tid och du ser tröskelvärden.

---

### 3. Power consumption monitor
**Vad det är**: CT clamp (kontaktlös strömsensor) runt strömkabeln till skrivaren, ESP32 mäter och loggar.

**Hur det funkar**: SCT-013-30 ger ut en spänning proportionell mot strömmen. ESP32 läser via ADC, räknar till watt × tid.

**Du lär dig**: Analog läsning, sampling, kalibrering, datalogging till SD-kort eller cloud.

**Komponenter**: SCT-013-30 (~150kr), spänningsdelare-resistorer (~20kr).

**Värde**: konkret hållbarhetsdata — vad kostar en X-timmars-print i el? Bygger underlag för kund-prissättning.

---

## ★★ Intermediate (vecka 5–10)

### 4. Filament-vågen (load cell)
**Vad det är**: Spool-hållare med inbyggd våg. Ser hur mycket filament som finns kvar på rullen i realtid.

**Hur det funkar**: HX711 ADC läser av en load cell (typ 5kg eller 10kg), ESP32 räknar gram, jämför mot startvikt.

**Du lär dig**: SPI-kommunikation, kalibrering med kända vikter, mer avancerad sensor-fusion.

**Komponenter**: HX711 modul (~50kr), 5kg load cell (~100kr), 3D-printad spool-hållare med integrerad våg.

**Värde**: "har jag tillräckligt filament för det här jobbet?" → automatisk varning om dåligt utfall. Plus exakt material-kostnad-tracking.

---

### 5. Smart belysning i kapsling
**Vad det är**: WS2812 LED-strip i kapslingen som ändrar färg baserat på print-status. Vit vid normal print, röd vid fel, grön vid klar, dimmad blå när idle.

**Hur det funkar**: ESP32 lyssnar på Bambu MQTT, styr LED-strip via en datapinn.

**Du lär dig**: Avancerad LED-kontroll (NeoPixel-bibliotek), state machines, lite UI-design.

**Komponenter**: 1m WS2812 strip (~150kr), 5V power supply.

**Värde**: ergonomi (bra ljus i kapsling vid övervakning), feedback (du ser status från långt håll).

---

### 6. RFID-filament-identifiering
**Vad det är**: NFC-tags på dina filament-rullar. Skanna mot ESP32 → loggas vilken rulle är installerad just nu.

**Hur det funkar**: PN532 RFID-läsare läser NFC-tagg. ESP32 skickar info till en logging-server (kan vara Obsidian via skript, eller en simpel JSON-fil).

**Du lär dig**: SPI/I2C, RFID-protokoll, integrering med externa system.

**Komponenter**: PN532-modul (~150kr), 10 NFC-taggar (~50kr).

**Värde**: automatisk material-databas. Kombinera med [[../printing/bergstein-digi-7/substrates/_index|substrate-databasen]] för full produktionsspårbarhet.

---

### 7. Web-dashboard på ESP32
**Vad det är**: ESP32 hostar en mini-webserver som visar all data (temp, fukt, energi, vikt) på en webbsida du når från telefonen.

**Hur det funkar**: ESP32 kör en async webserver på port 80, serverar HTML + WebSocket-uppdateringar.

**Du lär dig**: HTML/CSS/JS-grunder, WebSockets, async programming.

**Komponenter**: bara ESP32 (om du redan har sensorerna från projekt 2/3/4).

**Värde**: en samlad vy. Bonus: du lär dig webutveckling som är användbart i andra sammanhang.

---

## ★★★ Advanced (månad 3–6)

### 8. Spaghetti-detektion med kamera
**Vad det är**: ESP32-CAM (en variant med kamera) tittar på print-bädden, kör en lokal ML-modell som upptäcker "print failure" och stoppar skrivaren.

**Hur det funkar**: TensorFlow Lite Micro-modell tränad på spaghetti vs. normala prints. Kör inferens var 30:e sekund. Vid detektering → MQTT-meddelande till Bambu API som pausar.

**Du lär dig**: Maskininlärning på edge-devices, vision, modelloptimering, kritisk integration.

**Komponenter**: ESP32-CAM modul (~100kr) — note: detta är en separat board från din ESP32-D, så köp till.

**Värde**: räddar prints som annars hade förstört en hel rulle filament. Konkret ROI.

---

### 9. Multi-printer-orchestrator
**Vad det är**: Om du någonsin köper printer #2 — ESP32 koordinerar mellan flera skrivare. Print queue, lastbalansering, gemensam status-skärm.

**Hur det funkar**: Avancerad MQTT-arkitektur, state-management, möjligen en webdashboard.

**Du lär dig**: distribuerade system, message brokers, system design.

**Komponenter**: en ESP32 per skrivare + en central server.

**Värde**: skalningssprång. Ej relevant förrän du har 2+ skrivare.

---

### 10. Smart enclosure (allt-i-ett)
**Vad det är**: Komplett kapsling med automatisk temperaturreglering, fläktstyrning, dörrlås, belysning, säkerhet (rök/UV-detektorer).

**Hur det funkar**: Kombinerar projekt 2, 3, 5 + relä-styrning + säkerhetslogik.

**Du lär dig**: större system-design, säkerhetskritisk programmering, hårdvara-säkerhet (relä-isolation).

**Komponenter**: relämoduler (~100kr för 4 reläer), fläktar (~80kr), DC power supply, 3D-printad kapslingstomgång.

**Värde**: optimal printmiljö för varje materialtyp. ABS i 50°C, PLA i rumstemperatur, automatiskt.

---

## Hur du väljer

**Om du vill ha snabb belöning**: börja med #1 (LED-notifikation). Ger dopaminkick på 2 dagar.

**Om du vill ha mest praktisk nytta för verkstaden**: #2 (temp/fukt) eller #4 (filament-vågen).

**Om du vill växa snabbast som programmerare**: #7 (web-dashboard) lär dig flest överförbara skills.

**Om du vill imponera på framtida kunder/arbetsgivare**: #8 (ML failure-detection) är ett portfolio-projekt.

---

## Tips

Tre principer för att inte fastna:

1. **En sak i taget**. Bygg, testa, dokumentera, gå vidare. Inte 3 projekt parallellt.
2. **Klart innan perfekt**. Får du LED:n att blinka i ett projekt — gå vidare även om koden är ful. Refaktorera senare.
3. **Logga vad som inte funkade**. När du fastnar 2h på något: skriv ner orsaken. Du kommer fastna på samma grej igen om 6 månader.
