---
type: project-note
title: "Framtida faser — röst, always-on, ESP32, smarta funktioner"
project: jarvis
created: 2026-05-03
updated: 2026-05-03
tags:
  - project
  - roadmap
  - future-phases
related:
  - "[[_index]]"
  - "[[fas-1-text-jarvis]]"
---

# Framtida faser

Översikt av Fas 2–5. Detaljer skrivs när du faktiskt börjar varje fas — premature documentation är slöseri.

---

## Fas 2 — Röst (1 helg)

### Vad som läggs till

- **Speech-to-text (STT)**: säg en fråga, datorn transkriberar
- **Text-to-speech (TTS)**: Jarvis svarar med röst i högtalarna

### Tekniska val

| Komponent | Cloud-alternativ | Lokal-alternativ |
|---|---|---|
| **STT** | OpenAI Whisper API ($6/mån) | Lokala Whisper via `faster-whisper` (gratis, behöver GPU för snabbhet) |
| **TTS** | ElevenLabs ($5/mån, naturligast röst) | Piper TTS (gratis, robotigare) eller Coqui TTS |

### Min rekommendation

**Lokal Whisper + ElevenLabs**. STT är CPU-OK lokalt. TTS-kvaliteten är skillnaden mellan "kul leksak" och "verktyg du faktiskt använder" — där betalar du.

### Bibliotek

```python
pip install faster-whisper sounddevice elevenlabs
```

### Tidsåtgång

4–8 timmar. Mest tid på att få mikrofon + högtalare att fungera utan delay.

---

## Fas 3 — Always-on (1–2 veckor)

### Vad som läggs till

- **Wake-word**: säg "Hej Jarvis" → han börjar lyssna. Inga "tryck på knapp först".
- **Bakgrundsprocess**: Jarvis kör hela tiden, väntar tyst.
- **Tystnad mellan kommandon**: efter svar går han tillbaka till väntläge.

### Tekniska val

| Wake-word-engine | Pris | Kvalitet |
|---|---|---|
| **Picovoice Porcupine** | Gratis för hobby, $5–25/mån för custom wake-words | Bäst-i-test, snabb, kör lokalt |
| **OpenWakeWord** | Gratis, open source | Funkar OK men kräver finetuning |
| **Snowboy** (deprecated) | — | Skip, underhålls inte |

**Rekommendation**: Porcupine. Gratis-tier räcker för "Hey Jarvis"-wake-word.

### Tidsåtgång

1–2 veckor. Wake-word är det enkla. Det svåra är att få Jarvis att gå tillbaka till väntläge utan att haka upp sig på sin egen TTS-output.

### Komplikationer

- Acoustic echo cancellation: när Jarvis pratar via högtalaren får mikrofonen tillbaka det → "Jarvis hör sig själv". Lös med dedicated echo-cancelling library eller fysisk separation av mic/speaker.
- False activations: ord som låter som "Hej Jarvis" triggar ovillkorligt. Tröskelvärde måste tunas.

---

## Fas 4 — ESP32-embodiment (2–4 veckor)

### Vad som läggs till

- En liten **fysisk Jarvis-låda** i verkstaden
- ESP32 hanterar mikrofon, LED-ring, knapp
- WiFi-koppling till Python-hjärnan på din dator
- Du behöver inte ha laptopen öppen

### Hårdvara

| Komponent | Pris | Kommentar |
|---|---|---|
| ESP32-S3 (med inbyggd mic-stöd, INMP441 i2s) | ~150kr | S3 funkar bättre än standard ESP32 för audio |
| INMP441 mikrofon-modul | ~60kr | Digital I2S, hög kvalitet |
| MAX98357A I2S-amp + 3W högtalare | ~80kr | Liten, högläsande nog för verkstad |
| WS2812 LED-ring (12 eller 24 leds) | ~50kr | "Jarvis lyssnar"-feedback |
| Knapp | <10kr | För manuell wake (alternativ till röst) |
| 3D-printad kapsling | gratis (du har skrivare) | Designa själv |

Total: **~350kr** för en enhet.

### Arkitektur

```
[ESP32 i verkstaden]            [Python-hjärnan på din dator]
     |                                       |
     | mic audio (raw I2S)                   |
     |─────WiFi UDP/MQTT────────────────────>|
     |                                       | Whisper STT
     |                                       | Claude API
     |                                       | TTS
     |<────WiFi (TTS audio stream)──────────|
     | spelar upp via I2S-amp                |
     | LED-ring "tänker / pratar / klar"     |
```

### Tidsåtgång

2–4 veckor. Audio-streaming över WiFi är inte trivialt; first try kommer hacka. Räkna med iterationer.

### Bygg-ordning

1. ESP32 läser mic → spara som .wav
2. Spela upp .wav från ESP32 via högtalare
3. Skicka mic-data till PC över WiFi (testa med en enkel echo-server)
4. Integrera med Jarvis-Python-koden från Fas 1+2
5. Lägg till LED-ring för status
6. Lägg till knapp som alternativ wake
7. 3D-printa en snygg kapsling

---

## Fas 5 — Smarta funktioner (löpande)

Det här är inte en "fas" utan en **rad olika capabilities** du kan lägga till löpande, en i taget. Varje är en feature som Jarvis kan göra utöver att svara på frågor.

### Skriv-funktioner (vault writes)

- Lägg till anteckning i vault: "Jarvis, lägg till i material-noten att rPET kostar 200kr/kg från Add:North"
- Logga ett utfört jobb: "Jarvis, jobb #1234 lyckades på dopplackad metall, primer 30%"
- Skapa ny kund-not: "Jarvis, ny kund: Café X, beställning av 50 mugg-tryck"

Implementeras med **tool use / function calling** i Claude API. Jarvis bestämmer själv om svaret kräver att han skriver något, och kallar då en `write_note(path, content)`-funktion.

### Bambu-integration

- "Jarvis, vad gör skrivaren just nu?" → läser MQTT från Bambu
- "Jarvis, starta print X" → laddar 3MF-fil till Bambu, skickar print-kommando
- "Jarvis, varna mig när printen är klar" → schemalägger en notification

### Substrate-quick-reference

- "Jarvis, vad är inställningarna för bare aluminium?" → läser från substrate-databasen
- "Jarvis, vilket substrat liknar mest mörk akryl?" → semantic-search bland substrate-noterna

### Daily review

- Varje morgon kl 08:00: "Jarvis, daily review" → han läser gårdagens jarvis-log + senaste log.md-uppdateringar och sammanfattar
- "Jarvis, vad har hänt på fredag?" → tidsbaserad query

### Calendar / mail (om du vill)

- Google Calendar API integration
- Gmail API
- "Jarvis, vad händer imorgon?"
- "Jarvis, läs senaste mail från X"

Privatlivshänsyn: kräver fler API-keys och OAuth-flöden. Bara om du verkligen vill.

### Generativa printar

- "Jarvis, generera en unik mandala-design för en flaska, för seed 42, spara som SVG i `projects/printing/orders/`"
- Ringer en bild-generations-API (Replicate, fal.ai) eller kör en lokal SD/Flux-modell

---

## Min rekommendation

Bygg Fas 1, kör den i 2 veckor, lär dig vad du ANVÄNDER varje dag. Bygg sen den feature från Fas 5 du saknar mest.

Hoppa Fas 4 (ESP32-embodiment) tills du är säker på att text-Jarvis är värd att ha hela tiden — det är dyrt och komplext att bygga, slöseri om du inte använder honom dagligen.

Fas 2 (röst) är "kul" men inte nödvändig. Många AI-assistenter funkar lika bra som text. Test-kör utan röst först.
