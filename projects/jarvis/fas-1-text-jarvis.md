---
type: project-note
title: "Fas 1 — Text-Jarvis i terminalen (lokal Ollama)"
project: jarvis
created: 2026-05-03
updated: 2026-05-03
difficulty: beginner
estimated_time: "1–2 timmar (varav ~30 min är download)"
tags:
  - project
  - phase-1
  - python
  - ollama
  - local-llm
related:
  - "[[_index]]"
---

# Fas 1 — Text-Jarvis (lokal Ollama)

Mål: efter den här fasen kör du `python jarvis.py` i en terminal, ställer en fråga, och får ett svar baserat på din Obsidian-vault. **Helt lokalt — ingen API-key, inget internet behövs efter setup, inga kostnader.**

Tid: 1–2 timmar varav största delen är model-download (~9GB).

---

## Hårdvara — du har bra setup för detta

| Komponent | Du har | Räcker det? |
|---|---|---|
| RAM | 64 GB | ✅ Massor över för en 14B-modell |
| GPU | RTX 5070 Ti (16GB VRAM) | ✅ Modellen får plats helt på GPU → snabba svar |
| CPU | i9-9900K | ✅ Räcker för fallback om GPU inte används |

Modellen vi kör (qwen2.5:14b) tar ~9GB diskplats och ~10GB VRAM när den laddas. Du kommer inte att märka av den i normal datoranvändning.

---

## Status efter förberedelse

✅ Python 3.14 + venv installerat
✅ ollama Python-SDK installerat
✅ Ollama-service installerat och igång (port 11434)
✅ qwen2.5:14b — model nedladdas i bakgrunden, kontrollera status med:

```bash
"C:\Users\jakob\AppData\Local\Programs\Ollama\ollama.exe" list
```

När du ser `qwen2.5:14b` i listan är download klar. Tar 5–15 min beroende på din uppkoppling.

---

## När modellen är klar — kör Jarvis

**Git Bash:**
```bash
cd /c/Users/jakob/claude-obsidian/projects/jarvis/code
./venv/Scripts/python.exe jarvis.py
```

**PowerShell:**
```powershell
cd C:\Users\jakob\claude-obsidian\projects\jarvis\code
.\venv\Scripts\python.exe jarvis.py
```

Du borde se:
```
🤖 Jarvis vaknar... Modell: qwen2.5:14b (lokal via Ollama)
   Läser vault: C:\Users\jakob\claude-obsidian
📚 Indexerade ~50 filer.
Hej. Vad vill du veta? (skriv 'exit' för att avsluta)

>>>
```

Första svaret efter en kall start tar ~10–30s (modellen laddas in i VRAM). Efterföljande svar är 2–5s.

---

## Tre testfrågor att börja med

1. **Vault-fakta**: `vad är primer-procenten på dopplackad metall?`
   — Han ska svara med 30% och citera `[[dopplackad-metall]]`.

2. **Konceptuell sök**: `förklara DragonScale Memory på 3 meningar`
   — Han läser från `wiki/concepts/DragonScale Memory.md`.

3. **Översikt**: `vilka projekt har vi öppna just nu?`
   — Han ska lista 3D-print-hållbarhet, electronics-esp32, jarvis, printing.

---

## Anpassningar i jarvis.py

Öppna filen och leta efter `CONFIG`-sektionen högst upp.

### Byt modell

`MODEL = "qwen2.5:14b"` → ändra till annan modell. Du måste först ha pullat den med `ollama pull <namn>`.

| Modell | Diskstorlek | RAM/VRAM | Bra för |
|---|---|---|---|
| **qwen2.5:14b** (default) | 9 GB | 10 GB | Bästa balans, svenska + engelska |
| **qwen2.5:7b** | 4.5 GB | 5 GB | Snabbare, något sämre kvalitet |
| **llama3.1:8b** | 4.7 GB | 5 GB | Bra general-purpose |
| **gemma2:27b** | 17 GB | 18 GB | Bättre svenska, fyller hela din VRAM |
| **llama3.3:70b** | 43 GB | 48 GB | Smartast — kör på CPU (långsamt) eller GPU+CPU split |

Med din hårdvara kan du faktiskt köra **gemma2:27b** eller till och med **llama3.3:70b** (sistnämnda blir långsam, men funkar).

### Ändra personligheten

Letar upp `SYSTEM_PROMPT`. Standard:

```
Du är Jarvis, en personlig AI-assistent för Jakob. ...
```

Ändra till vad du vill. Vill du att han är kortfattad? "Svara i max 3 meningar." Personlighet? "Du är torr och sarkastisk."

### Ändra hur mycket vault som skickas

`MAX_VAULT_TOKENS = 8000` — höj för smartare svar (skickar mer kontext, längre svarstid). Sänk för snabbare. Med din 16GB VRAM kan du gå upp till 16000 utan problem.

### Temperature

I `client.chat()` -anropet: `temperature: 0.6`. Lägre = mer deterministisk. Högre = mer kreativ. För Q&A på vault-data är 0.3–0.6 bra. För brainstorming, 0.8.

---

## Loggning

Varje konversation sparas som markdown i `wiki/jarvis-log/jarvis-YYYY-MM-DD.md`. En ny fil per dag, alla turer i samma dagens fil.

Bonus: dessa filer dyker upp i din Obsidian-vault som vanliga noter. Du kan tagga, länka, söka i dem — din egna chat-historik blir en del av vaulten.

---

## Vanliga problem

| Symptom | Lösning |
|---|---|
| `Kan inte ansluta till Ollama` | Service inte igång. Sök "Ollama" i Start-menyn och starta, eller kör `ollama serve` i en terminal. |
| `Modell qwen2.5:14b inte hittad` | Download inte klar än, eller misslyckad. Kör `ollama pull qwen2.5:14b` igen. |
| Svaren är långsamma (>20s per svar) | Modellen ligger på CPU istället för GPU. Kontrollera `nvidia-smi` att GPU används. |
| Datorn blir het / fläktarna går högt | Normalt. Modellen jobbar. Ingen skada sker. |
| Svaren är klyschiga / generic | Frågan för bred. Använd specifika ord från dina noter. |
| Svenska blir lite konstig | qwen2.5 har bra men inte perfekt svenska. Prova `gemma2:27b` för bättre svenska (kostnaden är längre svarstid). |

---

## Ollama-grundkommandon

| Kommando | Vad det gör |
|---|---|
| `ollama list` | Visa nedladdade modeller |
| `ollama pull <namn>` | Ladda ner en modell |
| `ollama rm <namn>` | Ta bort en modell (frigör disk) |
| `ollama run <namn>` | Chatta direkt i terminalen utan jarvis.py |
| `ollama ps` | Visa modeller som är inladdade i RAM/VRAM just nu |

Om du har Ollama installerat men inte på PATH, prefix med:
`"C:\Users\jakob\AppData\Local\Programs\Ollama\ollama.exe"` istället.

---

## När du är klar med Fas 1

Du har en fungerande lokal Jarvis. Han läser din vault, svarar på svenska, kostar inget att köra, all data stannar på din maskin.

Vad nu?

- **Använd honom dagligen i 2 veckor.** Du upptäcker vad du saknar — det driver vad Fas 2–5 ska prioritera.
- **Hoppa till [[framtida-faser|Fas 5 (smarta funktioner)]]** om du vill att han ska kunna SKRIVA till vaulten istället för bara läsa. Det är där den verkliga nyttan kommer.
- **Fas 2 (röst)** kan vänta tills text-flödet är riktigt smidigt.

---

## Loggbok

| Datum | Vad jag gjorde | Vad jag lärde mig |
|---|---|---|
| | | |
