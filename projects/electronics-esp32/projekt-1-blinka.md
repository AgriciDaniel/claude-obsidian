---
type: project-note
title: "Projekt 1 — Blinka en LED med ESP32"
project: electronics-esp32
created: 2026-05-03
updated: 2026-05-03
difficulty: beginner
estimated_time: "60 min"
tags:
  - project
  - tutorial
  - micropython
  - first-project
related:
  - "[[_index]]"
---

# Projekt 1 — Blinka en LED

Mål: från "ESP32 i förpackning" till "LED blinkar i takt med din kod" på ungefär 60 minuter. När du klarat det här har du verifierat att:

- Hårdvaran fungerar
- IDE:n är installerad och pratar med ESP32
- Du kan skriva, köra, och ändra kod

Allt annat byggs ovanpå det.

---

## Vad du behöver

| Sak | Var |
|---|---|
| ESP32-D dev board | ✅ Du har |
| USB-kabel till datorn (USB-C eller micro-USB beroende på board) | Kolla vilken kontakt din ESP32 har |
| Dator (Windows/Mac/Linux) | ✅ Du har |
| 1× LED (vilken färg som helst) | Electrokit / Clas Ohlson / restlådan från någon gammal grej |
| 1× motstånd 220–330Ω | Same |
| Breadboard | Same |
| 2× jumper-kablar (han-han) | Same |

Om du saknar elkomponenter: skip steg 4 och använd den **inbyggda blå LED:n på ESP32-boarden** (på GPIO 2 på de flesta dev boards). Då räcker det med ESP32 + USB-kabel.

---

## Steg 1 — Installera Thonny (15 min)

Thonny är en enkel Python-IDE som har ESP32-stöd inbyggt. Mycket lättare för nybörjare än VS Code eller Arduino IDE.

1. Gå till [thonny.org](https://thonny.org)
2. Ladda ner och installera för ditt OS
3. Starta Thonny

---

## Steg 2 — Anslut ESP32 och flasha MicroPython (20 min)

ESP32 levereras med en blank firmware. Du behöver flasha MicroPython på den.

1. Anslut ESP32 till datorn med USB-kabeln
2. I Thonny: **Verktyg → Inställningar (Tools → Options)** → fliken **"Tolk" (Interpreter)**
3. Välj **"MicroPython (ESP32)"** i dropdown:en
4. Klicka **"Installera eller uppdatera MicroPython"**
5. I dialogen som öppnas:
   - **Port**: välj porten där ESP32 dyker upp (Windows: COM3 eller liknande; Mac/Linux: /dev/cu.* eller /dev/ttyUSB0)
   - **Variant**: ESP32 / WROOM
   - **Version**: senaste stabila
6. Klicka **Installera** och vänta. Tar 30–90 sekunder.

**Felsökning om porten inte syns**:
- Windows: kan saknas en USB-driver. Sök "CP210x driver" på Silicon Labs hemsida och installera. Vissa boards har CH340-chip istället → sök "CH340 driver".
- Mac: macOS har inbyggda drivers, brukar bara funka.
- Linux: lägg till din användare i `dialout`-gruppen: `sudo usermod -a -G dialout $USER`, logga ut, logga in.

När installationen är klar, klicka **OK**. Du ska nu se en Python REPL-prompt (`>>>`) i Thonnys nedre fönster. Skriv:

```python
print("hej")
```

Och tryck Enter. Om "hej" printas — gratulerar, ESP32 kör Python.

---

## Steg 3 — Blinka inbyggda LED:n (10 min)

I Thonnys övre fönster, skriv:

```python
from machine import Pin
from time import sleep

led = Pin(2, Pin.OUT)  # GPIO 2 är inbyggda LED:n på de flesta ESP32-boards

while True:
    led.value(1)  # på
    sleep(0.5)
    led.value(0)  # av
    sleep(0.5)
```

Spara filen (**Arkiv → Spara som**) — välj **"MicroPython device"** som plats, och döp den till `main.py`. Filer som heter `main.py` körs automatiskt när ESP32 startar.

Klicka **Kör (F5)**. LED:n på boarden ska börja blinka 1 gång per sekund.

**Stoppa skriptet**: Ctrl+C i Thonny REPL-fönstret.

---

## Steg 4 — Anslut extern LED (15 min, optional)

Om du har breadboard och komponenter:

```
ESP32 GPIO 23 ──── motstånd 220Ω ──── LED+ ──── LED- ──── ESP32 GND
```

Ändra koden till:

```python
from machine import Pin
from time import sleep

led = Pin(23, Pin.OUT)

while True:
    led.value(1)
    sleep(0.3)
    led.value(0)
    sleep(0.3)
```

Kör. Den externa LED:n ska blinka snabbare än den inbyggda.

**Säkerhet**: motståndet är obligatoriskt. Utan det får LED:n för mycket ström och brinner upp inom sekunder. Glöm aldrig motståndet på en LED.

---

## Vad du lärt dig

- Hur ESP32 ansluts till datorn och flashas
- Hur Thonny pratar med MicroPython
- `Pin`-klassen för digital I/O
- Skillnad mellan inbyggd LED (GPIO 2) och extern LED (du valde själv vilken pin)
- Att en LED behöver motstånd

---

## Nästa steg

När den blinkar:

1. **Ändra blinkmönstret** — gör 2 snabba blinkningar, sen en paus, sen 2 till
2. **Lägg till en knapp** — Pin för digital input. Tryck knapp → LED på.
3. **Lägg till en till LED** — två LED:s, en blinkar fort, en långsamt
4. När du är trygg med GPIO: gå vidare till sensorer (DHT22) eller WiFi-anslutning

Eller hoppa direkt till [[projekt-ideer]] och välj något du faktiskt vill bygga.

---

## Loggbok (fyll i när du gör det)

| Datum | Vad jag gjorde | Vad jag lärde mig / fastnade på |
|---|---|---|
| | | |
