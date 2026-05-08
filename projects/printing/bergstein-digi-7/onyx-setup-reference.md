---
type: project-reference
title: "Bergstein Digi 7 — Onyx RIP setup reference"
project: bergstein-digi-7
domain: uv-printing
created: 2026-05-01
updated: 2026-05-01
tags:
  - project
  - printing
  - uv-printing
  - onyx
  - bergstein
status: working-doc
related:
  - "[[adhesion-test-protocol]]"
---

# Bergstein Digi 7 — Onyx RIP setup reference

Everything from the working session on configuring the Bergstein Digi 7 (8-channel UV printer: CMYK + Primer + 3× White) for printing on dopplackad metall (dip-coated/lacquered metal) at 360 DPI in Onyx Media Manager.

> **Substrate caveat.** All numbers here are starting points. The cross-hatch adhesion test (see end of doc) is the only real arbiter — adjust until it passes 5B on your actual material with your actual ink batch.

---

## Hardware config

**Bergstein Digi 7 har 7 fysiska tryckhuvuden per färg.** Total kanaluppsättning:

| Färg | Antal heads | Channel-namn i Onyx |
|---|---|---|
| Cyan | 7 | C1, C2, C3, C4, C5, C6, C7 |
| Magenta | 7 | M1, M2, M3, M4, M5, M6, M7 |
| Yellow | 7 | Y1, Y2, Y3, Y4, Y5, Y6, Y7 |
| Black (K) | 7 | K1, K2, K3, K4, K5, K6, K7 |
| **Primer** (Spot 1) | 7 | Spot1.1–Spot1.7 |
| **White 1** (Spot 2) | 7 | Spot2.1–Spot2.7 |
| **White 2** (Spot 3) | 7 | Spot3.1–Spot3.7 |
| **White 3** (Spot 4) | 7 | Spot4.1–Spot4.7 |

**Total: 56 fysiska kanaler** (8 logiska bläck × 7 heads var).

"Digi 7" i printer-namnet refererar till dessa 7 heads per färg.

**Print order**: Primer → Triple-White → CMYK (3 separate strikes).

**Varför 7 heads per färg**: parallell ink-leverans. Alla 7 magenta-heads målar samma yta samtidigt → 7× snabbare än en singel-head-skrivare. Också redundans: om ETT head krånglar, kan de andra 6 kompensera (delvis).

**Konsekvens för felsökning**: när en färg är "svag" (t.ex. orange för gul), är det oftast 1–2 av de 7 heads för den färgen som är partiellt tilltäppta. Per-head nozzle check identifierar vilken/vilka.

**Konsekvens för Ink Restriction**: du har 7 separata caps per färg. För konsistent färg ska alla 7 ligga på samma värde. Om en kanal sänkts måste du höja de andra 6 för att kompensera, eller rengöra det krånglande headet och återställa.

---

## Substrate-specific settings (dopplackad metall)

**Surface prep is half the job.**

1. IPA (≥99%) wipe with lint-free cloth, let flash off 60s.
2. **Do NOT scuff** — sanding damages the lacquer and breaks the corrosion seal under it.
3. If the part is older than ~6 months from coating: double IPA wipe, then 5+ min wait before printing (lacquer vents absorbed solvents).
4. Avoid touching the surface after prep. Cotton gloves or vacuum handling.
5. Single most common failure: **silicone contamination → fish-eyes**. Cure with mild detergent + IPA double-clean.

**Onyx ink limits (starting values):**

| Channel | Setting | Notes |
|---|---|---|
| Primer | **30%** | Try 0% first if adhesion test passes — lacquer is already friendly |
| White ×3 combined | **180–200%** | Lower than bare metal; lacquer is opaque already |
| Each white channel | **65%** | Distributes load across all three heads |
| C M Y K | **80% each** | Standard UV CMYK over white |
| TAC per strike | 300% | |

If lacquer color is light (white, beige): drop combined whites to 150%. Lower whites = thinner ink film = better flex on curved drinkware.

**UV cure**: standard profile, no bump. Treat as plastic, not metal — lacquer doesn't conduct heat the way bare metal does. Inter-layer dwell: 5 seconds.

---

## Substrate comparison (for reference, in case the substrate changes)

| Substrate             | Primer | White combined | TAC  | Notes                                      |
| --------------------- | ------ | -------------- | ---- | ------------------------------------------ |
| **Dopplackad metall** | 30%    | 180–200%       | 300% | This config; closest to "plastic" behavior |
| Anodized aluminum     | 40%    | 210%           | 300% | Forgiving; oxide layer grips ink           |
| Bare aluminum         | 70%    | 220%           | 300% | Needs scuff + max primer                   |
| Stainless (bare)      | 80%    | 220%           | 280% | Hardest; primer is non-negotiable          |
| Coated/painted metal  | 30%    | 220%           | 300% | Behaves like the coating                   |
| Glass                 | 30%    | 250%           | 280% | Maximum opacity needed                     |
| Clear acrylic         | 30%    | 230%           | 300% |                                            |
| Dark/colored acrylic  | 70%    | 250%           | 300% |                                            |

---

## Onyx Media Manager — 8-phase setup walkthrough

Order matters. Don't skip. Menu names in parentheses are alternates seen across Onyx versions ~12 through 22.

### Phase 1 — Confirm printer is configured

1. Open **Onyx Configure Printer** ("Printer Manager").
2. Verify Bergstein Digi 7 in the list. If missing, **Add Printer** → load Bergstein's `.PrinterFile` for the Onyx version. Without the right PrinterFile, channel mapping is wrong and nothing else works.
3. Double-click the printer entry. Confirm:
   - 8 channels total
   - Channel order matches Bergstein's docs (CMYK + Primer + W + W + W in their physical head order)
   - Ink type: UV
   - Connection set up

### Phase 2 — Create a new media profile

1. Open **Onyx Media Manager** ("Profile Manager" / "Profile Tools").
2. **File → New Profile** ("New Media Profile" / "Create New").
3. **Printer**: Bergstein Digi 7
4. **Print mode**: 360 × 360 DPI, 4-pass bidi (the mode label depends on Bergstein's PrinterFile — look for "Production 360" or just "360").
5. **Base profile**: closest existing UV profile, or "blank/new".
6. **Name**: `BergsteinDigi7_dopplackad_360_CMYKWWW_v1` (date-stamp on save).
7. Save and continue. Profile is now in edit mode.

### Phase 3 — Ink limits per channel

1. **Print → Print Ink Restriction Test** ("Print Density Range" / "Print Ink Limits Wedge").
2. Onyx prints a step wedge: 0% → 100% per channel in 5% steps.
3. Cure fully before evaluating.
4. Inspect each channel:
   - **CMYK**: find where patches stop getting darker / start to puddle. Set limit at ~5% below that. Target **80%**.
   - **Each white channel**: find where opacity stops improving (test on dark backing card). Target **65%** each.
   - **Primer**: target **30%**. More than this and it pools and re-emulsifies under white.
5. Enter values back into Onyx under **Ink Restriction** / **Ink Limit** tab.
6. Save profile.

### Phase 4 — Linearization

1. **Print → Print Linearization Target** ("Print Calibration Target" / "Print Linearization Wedge").
2. Onyx prints a patch set for response curves.
3. **With spectro** (i1Pro 2/3, eXact, etc.): connect, use Onyx **Measure** dialog, scan all rows.
4. **Without spectro**: visual linearization is possible but only gets you ~80% of the way. Get a spectro before production.
5. Onyx auto-builds curves. Click **Apply**.
6. Save profile.

### Phase 5 — TAC limit

1. Profile editor → **Ink Restrictions** tab → **Total Ink Limit**.
2. Dopplackad metall: **300%** per strike.
3. Save.

### Phase 6 — White ink stack configuration

This wires up the primer + 3-white + CMYK layout.

1. **Color → White Ink Setup** ("Spot Color Setup" / "Multilayer Setup" depending on version).
2. Configure:
   - Mode: **Color Over White**
   - **Linked white channels**: link spots 2/3/4 as a single logical white. One "100% white" call splits across all three heads.
   - White density: 200% combined (each head ~65% × 3).
3. Layer order ("Print Stack" / "Strike Order"):
   - Strike 1: Primer (Spot 1)
   - Strike 2: White (Spots 2/3/4 linked)
   - Strike 3: CMYK
4. Inter-layer dwell: 5 seconds (under "Cure" or "Layer Settings").
5. Save.

### Phase 7 — ICC profile build

1. **Print → Print Profile Target** ("Print ICC Target" / "Print IT8 Chart"). Use TC918 or IT8.7/4.
2. Cure fully.
3. Measure with spectro (same one as linearization).
4. **Profile → Build ICC Profile** ("Profile Maker" / "Generate ICC").
5. ICC settings:
   - TAC: 300%
   - Black generation: GCR, medium
   - Black start: 25–30%
   - Max black: 95%
6. Save the ICC. Onyx auto-attaches to the media profile.
7. Save profile (final save).

### Phase 8 — Verify before production

Print this test set:

- 2 × 2 cm solid black square (full primer + full white + CMYK black)
- Skin-tone wedge
- Grayscale ramp
- Small color reference image

Cure fully. Wait **24 hrs** before testing — UV ink keeps hardening for the first day.

Then:

1. **Adhesion test** on the solid block (see protocol below).
2. **Visual check**:
   - Skin tones natural, not orange or green
   - Grayscale neutral, no color cast
   - Reference image looks like the original
3. If anything fails: re-do Phase 4 first (linearization), then Phase 7 (ICC) if colors still off.

---

## Adhesion test protocol (ASTM D3359)

This is the test that decides whether the print survives real use. Run it on every new substrate or ink batch.

1. Print a 2 × 2 cm solid block: full primer + full white + full black.
2. Cure fully. Let cool to room temp. **Wait 24 hrs** (UV ink continues to harden post-cure).
3. Score a **6 × 6 grid** (1 mm spacing) using a cross-hatch cutter or scalpel.
4. Apply 3M Scotch 600 tape, press firmly.
5. Pull at 60° angle in one motion.
6. Inspect under magnification.

| Grade | Result | Action |
|---|---|---|
| **5B** | No detachment | Pass — production-ready |
| **4B** | Small flakes at intersections only | Pass — acceptable |
| **3B** | Flakes along edges | Fail — increase primer or improve prep |
| **0B–2B** | Substantial detachment | Fail — fundamental problem (wrong primer, contamination, or curing) |

If failing repeatedly even with full primer + perfect prep: the ink/primer chemistry is wrong for the substrate. Bergstein or the ink supplier should provide a substrate-matched primer formulation.

---

## Common failure modes

| Symptom                                   | Most likely cause                 | Fix                                                 |
| ----------------------------------------- | --------------------------------- | --------------------------------------------------- |
| Fish-eyes / ink balls up                  | Silicone contamination on lacquer | Re-clean with IPA + mild detergent, rinse, dry      |
| Print peels in cross-hatch                | Insufficient primer or bad prep   | Bump primer +20%; verify IPA prep step              |
| Print cracks on flex                      | Ink film too thick                | Reduce TAC by 20–40%                                |
| Color shift vs preview                    | Wrong ICC for substrate           | Rebuild ICC on the actual material                  |
| Banding on solids                         | Bidi misalignment                 | Run Bergstein's bidi calibration first              |
| Color sinks into white (muddy)            | White not fully cured before CMYK | Extend inter-layer dwell to 8s; bump cure intensity |
| Primer pools / re-emulsifies              | Primer limit too high             | Drop primer to 30% or lower                         |
| Ghosting on rotational prints (drinkware) | Rotation sync drift               | Re-run rotation calibration; check encoder coupling |

---

## Production checklist (every batch)

Before starting a production run on a new substrate batch or after any ink change:

- [ ] IPA wipe, lint-free, 60s flash
- [ ] Cross-hatch test piece printed and tested (24 hrs cure)
- [ ] Result is 5B (or 4B with sign-off)
- [ ] Color reference verified against last good batch
- [ ] White opacity wedge looks consistent
- [ ] No fish-eyes, no banding, no ghosting
- [ ] ICC profile date checked (rebuild every 6 months or per ink-batch change)

---

## What to ask Bergstein support / supplier when stuck

- "What's the .PrinterFile version for Onyx [your version]? I need 8-channel CMYK + primer + 3W."
- "Recommended ink limit ceiling per channel for [substrate]?"
- "Do you have a substrate-matched primer formulation for dopplackad metall?"
- "What's the recommended cure intensity / dwell for [substrate type]?"
- "Bidi alignment routine for the Digi 7 — is there a built-in macro or do I run it manually?"

---

## Open items / things to refine

- **Spectro situation**: confirm whether one is on hand. Without it, linearization and ICC are eyeballed and color reproduction degrades visibly. Single biggest investment to make if absent.
- **Specific drinkware vs flat metal**: flat sheets and curved drinkware need different bidi/rotation calibrations. If running both, expect to maintain two profiles.
- **Lacquer aging**: dipped parts older than ~6 months handle differently. Worth a separate test wedge if you're getting old stock.

---

## Session notes

- Reference compiled from a working session 2026-04-30 to 2026-05-01.
- Onyx version not yet confirmed; menu names are generic across ~v12–v22.
- Bergstein Digi 7 head model not yet confirmed (Konica KM1024i / Ricoh Gen5 / Xaar 1003 are the common candidates for 8-channel UV at this resolution).
- Source of all numbers: general UV printing best practice, not Bergstein-specific factory data. Verify against Bergstein support before production.
