---
type: meta
title: "Hot cache — Jakobs aktiva trådar"
updated: 2026-05-08
tags:
  - meta
  - hot-cache
---

# Hot cache

Senaste status och aktiva trådar. Uppdateras löpande. Läs först om du vill veta vad som är på gång.

---

## Senast uppdaterat

**2026-05-08:** Vault rensad. Tagit bort upstream-projektets innehåll (DragonScale Memory, ekosystem-research, etc.) och behåller bara personliga projekt + infrastruktur som behövs för Claude Code och Jarvis. Allt på `_archive/` är borttaget permanent — det fanns ingen användning.

---

## Aktiva trådar

### Bergstein Digi 7 (UV-printverkstad) — produktion + felsökning

- **Onyx 2015** används som RIP. Inga ICC-profiler aktiva, kör direkt med linearization.
- **Aktivt problem (2026-05-03 → i morgon)**: Orange (C0 M75 Y100 K0) blir blekare och mer gul på dopplackad metall. Diagnos och fixar klara i [[../projects/printing/bergstein-digi-7/orange-fix-kit|orange-fix-kit]]. Plan för i morgon: per-head nozzle check först, sen test-pattern + spektro-mätning.
- **Hårdvara**: 7 fysiska heads per färg = 56 kanaler totalt. CMYK + Primer + 3 White.
- **Substrat-fokus**: dopplackad metall. Fullständig substrat-databas i `projects/printing/bergstein-digi-7/substrates/`.

### Jarvis (lokal AI-assistent)

- **Fas 1 klar (2026-05-03).** Kör lokalt via Ollama (qwen2.5:14b). Skrivbordsgenväg `Jarvis.lnk` startar honom.
- Konversationer loggas i `wiki/jarvis-log/`.
- **Pausat just nu** för att lösa orange-problemet. Resume-pointer: när Jakob säger "Jarvis igen" eller "Fas 2" → gå till `projects/jarvis/_index.md`.

### 3D-print + hållbarhet (brainstorm-fas)

- 5 startnoter klara. Inget aktivt arbete just nu.
- Resume-pointer: när Jakob är redo att välja en idé → gå till `projects/3d-print-hallbarhet/affarsideer.md`. Top-3-rekommendation finns där.

### ESP32 + elektronik-lärande

- Setup-anteckningar klara. ESP32-D inköpt men ännu inte använd.
- Resume-pointer: starta med `projects/electronics-esp32/projekt-1-blinka.md` när tid finns för 60 min ostörd hands-on.

---

## Style-preferenser för instruktioner

Se [[../CLAUDE|CLAUDE.md]] för full spec. Kort version:

- Sektioner med `---` separatorer
- Tabeller för strukturerad info
- Numrerade steg-för-steg
- Förklara både "vad det betyder" och "vad du gör"
- Konkreta exempel och vardagliga analogier (Jakob är ny på programmering, elektronik, viss färgteknik)
- Inga em-dashes
- Konkreta filer/scripts/launchers när relevant
- Avsluta med "Tre saker att göra direkt"

---

## Vault-struktur (efter rensning 2026-05-08)

```
claude-obsidian/
├── projects/                  ← din riktiga arbete (4 projekt)
│   ├── printing/
│   ├── 3d-print-hallbarhet/
│   ├── electronics-esp32/
│   └── jarvis/
├── wiki/                      ← cross-projekt-kunskap
│   ├── index.md
│   ├── hot.md (denna fil)
│   └── jarvis-log/            ← Jarvis-konversationer hamnar här
├── CLAUDE.md                  ← personliga instruktions-prefs
├── Excalidraw/                ← ritningar (om du börjar rita)
├── LICENSE                    ← krävs av git
└── (gömda)                    ← infrastruktur Claude Code behöver
    ├── skills/
    ├── scripts/
    ├── hooks/
    ├── agents/
    ├── commands/
    ├── bin/
    ├── tests/
    ├── .claude-plugin/
    └── .vault-meta/
```
