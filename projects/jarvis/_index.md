---
type: project-hub
title: "Jarvis — AI-assistent för Obsidian-vault"
project: jarvis
created: 2026-05-03
updated: 2026-05-03
status: active
tags:
  - project
  - ai
  - llm
  - obsidian
  - voice
related:
  - "[[../electronics-esp32/_index|ESP32-projektet]]"
---

# Jarvis — AI-assistent för Obsidian-vault

Bygg din egen AI-assistent som kan prata med dig (text först, sen röst), läsa din Obsidian-vault, och svara på frågor om dina projekt, anteckningar, och liv.

> **Verklighetscheck**: Iron Man-Jarvis är fortfarande sci-fi (åratal av minne, holografer, robotkroppar). Men en **dagligt användbar AI-assistent kopplad till din vault** är ett verkligt 1–2-helgers-projekt. Det här dokumentet är roadmappen från "tomt projekt" till "jag pratar med min dator om mina anteckningar".

---

## Vad du faktiskt får

Efter Fas 1 (en helg):
- Kör `python jarvis.py` i terminalen
- Ställer en fråga: "vilken primer-procent kör jag på dopplackad metall?"
- Får svar baserat på din vault-data
- Konversationen sparas tillbaka som not i vaulten

Efter Fas 2 (en till helg):
- Du pratar in mikrofon → han svarar med röst i högtalare

Efter Fas 3 (vecka 5–6):
- Always-on. Säger "Hej Jarvis" och han väcks. Tystnar mellan kommandon.

Efter Fas 4 (månad 2):
- En liten ESP32-låda i verkstaden med mikrofon + LED-ring + knapp. Du behöver inte ha laptopen öppen.

Efter Fas 5 (månad 3+):
- Han kan SKRIVA till vaulten också. Lägga till anteckningar. Köra commands. Starta en print-fil. Logga ett jobb i substrate-databasen. Allt med röst.

---

## 5-fas-roadmap

| Fas | Vad du bygger | Tid | Komplexitet |
|---|---|---|---|
| **1** | Text-Jarvis i terminalen, läser din vault, svarar via Claude API | 1 helg | ⭐ |
| **2** | Lägg till röst (Whisper för STT, ElevenLabs eller lokal TTS för output) | 1 helg | ⭐⭐ |
| **3** | Always-on med wake-word ("Hej Jarvis"), bakgrundsprocess | 1–2 veckor | ⭐⭐⭐ |
| **4** | ESP32-embodiment — fysisk låda med mikrofon, LED, knapp | 2–4 veckor | ⭐⭐⭐⭐ |
| **5** | Skriv-funktioner: lägg till anteckningar, kör commands, kontrollera Bambu | löpande | ⭐⭐⭐⭐ |

Du behöver inte göra alla. Fas 1 + 5 räcker för 90% av nyttan.

---

## Kostnads- och beroende-realitet

| Komponent | Kostnad | Notering |
|---|---|---|
| **Claude API key** | ~$5 free credit, sen ~$25/mån vid 50 frågor/dag | Anthropic.com → API → skapa key |
| **Whisper** (STT) | Gratis lokalt, $6/mån via OpenAI API | Lokalt funkar bra på din dator |
| **ElevenLabs** (TTS) | $5/mån för 30k tecken | Eller använd gratis lokal TTS (Piper) |
| **Lokal LLM-alternativ** | Gratis, kräver kraftig dator | Ollama + Llama 3 8B kör på de flesta moderna laptops |
| **ESP32 + mic + speaker** | ~400kr | För Fas 4 |

**Helt gratis-alternativ**: Ollama + Llama 3 + lokal Whisper + Piper TTS. Lite sämre kvalitet men $0/mån. Bra för att lära sig, sen byt till cloud API om du vill ha bättre.

**Min rekommendation för dig**: Claude API + lokal Whisper. Bästa balansen. Cirka $25–30/mån. Värt det för att slippa kämpa med lokal LLM-prestanda i lärandefasen.

---

## Sub-noter

| Not | Vad |
|---|---|
| [[fas-1-text-jarvis]] | Steg-för-steg från tomt projekt till fungerande text-Jarvis. Kod ingår. |
| [[framtida-faser]] | Översikt av Fas 2–5: vad som krävs, vilka val du har |

---

## Anslutning till dina andra projekt

- **Obsidian-vaulten**: Jarvis läser direkt från `wiki/`, `projects/`, etc. Du behöver inget extra plugin för Fas 1.
- **ESP32-projektet**: Fas 4 använder din ESP32. Du borde göra [[../electronics-esp32/projekt-1-blinka|blink-projektet]] först så du har grunderna.
- **Substrat-databasen**: bra demo för Fas 1. Fråga "vilka inställningar för dopplackad metall?" och se honom svara från [[../printing/bergstein-digi-7/substrates/_index|substrates]].

---

## Decision log

| Datum | Beslut | Varför |
|---|---|---|
| 2026-05-03 | Projekt öppnat | Vill bygga AI-assistent kopplad till vault |
| 2026-05-03 | Start med Claude API, inte lokal LLM | Snabbare till första "wow"-ögonblick. Byt senare om du vill. |

---

## Öppna frågor (svara innan du börjar Fas 1)

1. Har du en Anthropic API-key, eller behöver vi gå igenom hur man skaffar?
2. Vilken dator ska Jarvis köra på? (Bör vara på medan du jobbar — verkstadsdatorn? Laptopen?)
3. Föredrar du svenska eller engelska för Jarvis röst/svar?
4. Vill du att Jarvis ska kunna svara om personliga grejer (kalender, mail) eller bara om vault-innehåll?

Säg "Fas 1, kör" så går vi igenom [[fas-1-text-jarvis]] tillsammans.
