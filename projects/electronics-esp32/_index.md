---
type: project-hub
title: "Elektronik + programmering med ESP32"
project: electronics-esp32
created: 2026-05-03
updated: 2026-05-03
status: active
tags:
  - project
  - electronics
  - programming
  - esp32
  - bambu-lab
related:
  - "[[../3d-print-hallbarhet/_index|3D-print hållbarhet]]"
---

# Elektronik + programmering med ESP32

Lärande-projekt: bygg upp elektronik- och programmeringskunskap med ESP32 som verktyg. Varje delmål kombineras med Bambu-skrivaren för att ge konkret användbar funktion direkt — du lär dig genom att bygga saker som faktiskt förbättrar din verkstad.

> **Status: aktiv**. Du har hårdvaran, du har skrivaren, första projektet kan börja idag.

---

## Vad du har

| Hårdvara | Status |
|---|---|
| Bambu S1 Combo | ✅ 1000h erfarenhet |
| ESP32-D dev board | ✅ Inköpt |
| Breadboard + jumper wires + LED + motstånd | ❓ Behövs (ingår sällan i grund-ESP32-paket) |
| USB-C / micro-USB-kabel för ESP32 | ❓ Kontrollera vilken kontakt boarden har |
| Multimeter | ❓ Köp om du inte har — 100–200kr på Clas Ohlson räcker att börja |

Saknar du basic elkomponenter: gå till **Electrokit.com** (Malmö, snabb leverans inom Sverige) och beställ ett "starter kit" för ESP32. Innehåller breadboard, motstånd, LEDs, knappar, jumper-kablar, ofta även en sensor eller två. ~250–400kr för grund.

---

## 3-månaders roadmap

### Månad 1 — Grunderna (4–6 veckor)

- ✅ Vecka 1: Hello World — blinka en LED. [[projekt-1-blinka|Steg-för-steg-guide]]
- Vecka 2: Knapp + LED (digital input). Tryck knapp → LED blinkar.
- Vecka 3: Analog läsning (potentiometer styr LED-ljusstyrka via PWM)
- Vecka 4–6: Sensor-läsning (DHT22 temperatur/luftfuktighet)

**Vad du lär dig**: GPIO, digital/analog I/O, PWM, basic Python-syntax, breadboard-tänkande.

### Månad 2 — WiFi + nätverk

- WiFi-anslutning på ESP32
- HTTP-requests (skicka data till en webserver)
- MQTT (publicera/lyssna på meddelanden)
- Liten webserver på ESP32 (kontrollera LED från telefonen)

**Vad du lär dig**: nätverk, klient/server-modell, JSON, hur IoT egentligen fungerar.

### Månad 3 — Kombinera med Bambu

Plocka 1–2 idéer från [[projekt-ideer]]. Förslag i ordning:

1. **LED-notifikation när print är klar** — enkelt, motiverande, första riktiga produktivitetsvinst
2. **Temperatur/luftfuktighets-monitor i kapsling** — användbart för materialval (PLA vs ABS), enkelt att bygga
3. **Filament-vågen** (load cell) — börjar bli mer avancerat, lär dig SPI/I2C

**Vad du lär dig**: integrering, debugging i flera lager, hur "smart hem"-grejer i verkligheten är hopplockade.

---

## Sub-noter

| Not | Vad |
|---|---|
| [[projekt-1-blinka]] | Komplett steg-för-steg från "ESP32 i förpackning" till "LED blinkar". 60 min. |
| [[projekt-ideer]] | 10 ESP32-idéer, alla kopplade till din skrivare, sorterade efter svårighet |
| [[resurser]] | Böcker, YouTube-kanaler, svenska butiker, communities |

---

## Programmeringsspråk-val

Du behöver välja: **MicroPython eller Arduino C++?**

| | MicroPython | Arduino C++ |
|---|---|---|
| Lätthet | ⭐⭐⭐⭐⭐ enklast att börja | ⭐⭐⭐ brantare kurva |
| Prestanda | OK för det mesta | Snabbare, mindre minnesförbrukning |
| Community | Stor, växer | Enorm, mest tutorials |
| Syntax | Vanlig Python — du hittar svar via Python-frågor | C-syntax — kräver lite mer disciplin |
| Debugging | Live REPL — kör kod direkt på chippet | Compile + flash varje gång |

**Min rekommendation för dig**: **MicroPython först** (månad 1), sen **Arduino C++ som tillägg** när du vill ha bättre prestanda eller jobba med projekt där andra Arduino-tutorials passar. MicroPython låter dig komma igång på 30 minuter mot 2+ timmar för Arduino.

---

## Decision log

| Datum | Beslut | Varför |
|---|---|---|
| 2026-05-03 | Projekt öppnat. Start med MicroPython. | Snabbast väg till "fungerande LED" + Python är användbart bortom ESP32 |

(Lägg till nya beslut här över tid.)
