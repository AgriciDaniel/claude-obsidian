---
type: project-note
title: "Hållbara material — 3D-print"
project: 3d-print-hallbarhet
created: 2026-05-03
updated: 2026-05-03
tags:
  - materials
  - filament
  - sustainability
related:
  - "[[_index]]"
  - "[[affarsideer]]"
---

# Hållbara material

Snabbreferens på material som är realistiska för en småföretagare i Sverige 2026. Inte uttömmande — bara de praktiska.

---

## FFF / FDM (filament)

### Standardmaterial — bra utgångsläge

| Material | Egenskaper | Hållbarhetsstory |
|---|---|---|
| **PLA** | Lätt att printa, bra detaljer, biobaserat (majsstärkelse) | "Komposterbart" (i industriell anläggning, INTE hemma — viktigt att vara ärlig om) |
| **PETG** | Hållbar, kemikaliebeständig, transparent möjligt | Återvinningsbar (samma kod som PET-flaskor) |
| **TPU** | Flexibel, gummi-aktig | Mindre hållbarhetsfördel, men slitstark → mindre kasseringar |

### Hållbarhets-fokuserade material

| Material | Vad det är | Realistik | Pris |
|---|---|---|---|
| **rPET / Recycled PETG** | Filament från återvunna PET-flaskor | Funkar bra. Refilament Sweden, ColorFabb sells "PETG-Economy" som är delvis återvunnet. | ~150% av standard-PETG |
| **PLA Eco / Bio** | PLA med extra bio-tillsatser eller från avfallsströmmar (kaffegrums, sågspån) | Skön estetik (fläckigt, organiskt), kan vara svår att färgmatcha | ~200% av standard-PLA |
| **Alger-baserad** | Algae-PLA (Eumakers, ColorFabb HT8000) | Coolt på papper, dyrt och ojämn kvalitet i praktiken | ~300% |
| **Svamp-baserad** | Mycelium-baserade kompositer (mer för formgjutning än 3D-print) | Inte mogen för konsument-3D-print än | n/a |
| **Recycled från egna prints** | Köp en filament-extruder, smält dina misslyckade prints till nytt filament | Fungerar, men kapitalintensivt + kvalitet sjunker över återvinningar | Eget arbete + ~20k+ för utrustning |

### Realistisk hållbarhetsstrategi för småföretag

1. **Default: PETG** för slutprodukter (återvinningsbar, hållbar, vanlig)
2. **PLA** för prototyper och kortlivade prints (PLA fungerar bäst kompostering-wise)
3. **rPET / Recycled-batches** för premium-erbjudande (där kunden betalar för storyn)
4. **Återförsälj misslyckade prints** till en lokal recycler istället för soptipp

Var ärlig om vad ditt material faktiskt är. "Komposterbar" på en PLA-produkt är vilseledande om kunden inte har tillgång till industriell kompostering. Skriv "biologiskt baserad" istället.

---

## Resin (SLA / DLP / MSLA)

Resin är generellt mer problematiskt hållbarhetsmässigt — petroleum-baserade härdmonomerer, toxiska före härdning.

### Eco-resiner (utvecklas snabbt 2024–2026)

| Resin | Vad det är | Realistik |
|---|---|---|
| **Anycubic Plant-based Eco UV Resin** | Sojabönolja-baserad härdresin | Funkar, lite svagare än standard, lukt mildare |
| **Phrozen Aqua-Gray** | Vatten-tvättbar | Inte direkt eco men minskar IPA-användning |
| **Formlabs BioMed Resins** | För medicinsk användning | Inte konsument-relevant, listas för fullständighet |

### Hållbarhetsutmaning för resin

- Härdat resin är inte återvinningsbart i normalt avfallssystem
- Avfallsresin är farligt avfall — måste lämnas på återvinningscentral
- Tvättvätska (IPA eller vatten) kontaminerad

**Slutsats**: starta med FFF (filament). Resin är intressantare för smyckesdetaljer eller smådetaljer men kostar mer att hantera ansvarsfullt.

---

## Svenska / nordiska leverantörer

| Leverantör | Vad de erbjuder | Var |
|---|---|---|
| **Add:North** | Svenskt filament, bra kvalitet, säljer rPET | Karlstad |
| **3DOM Sweden** | Specialiserade filament inkl. återvunna typer | Webbutik |
| **Filaments.directly** | Brett sortiment, snabb leverans | EU |
| **ColorFabb (NL)** | Premium, har Eco/recycled-linjer | EU |
| **Refilament** | 100% recycled-fokus | EU |

---

## Kvalitetsfälla att undvika

Många "eco-filament" har sämre printbarhet — drag i nozzle, ojämn diameter, varierande färg mellan rullar. För en startup är inkonsekvens ett problem (du måste re-kalibrera per rulle, kunden får olika kvalitet mellan beställningar).

**Strategi**: när du valt en hållbarhetsleverantör, **lås in dig på 1–2 rullar i månaden i 3 månader** och bygg en process. Byt inte rulle eller leverantör mitt i en kund-leverans.
