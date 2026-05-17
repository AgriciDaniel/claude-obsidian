---
type: reference
title: "Methodology Modes — Quick Decision Tree"
tags:
  - reference
  - methodology
  - wiki-mode
status: evergreen
related:
  - "[[methodology-modes-guide]]"
  - "[[wiki-mode]]"
---

# Methodology Modes — Quick Decision Tree

Pick a vault organizational style with `bash bin/setup-mode.sh`.

```
                  ┌──────────────────────────────────┐
                  │ Do you have a methodology         │
                  │ preference for organizing notes?  │
                  └──────────────┬───────────────────┘
                                 │
                ┌────────────────┴────────────────┐
              NO                                 YES
                │                                 │
                ▼                                 ▼
       ┌────────────────┐         ┌──────────────────────────────┐
       │   GENERIC      │         │ How do you think about content│
       │ (v1.7 default; │         └────────────────┬──────────────┘
       │  no opinion)   │                          │
       └────────────────┘     ┌────────────────────┼────────────────────┐
                              │                    │                    │
                              ▼                    ▼                    ▼
                    "topic clusters    "active projects     "atomic claims
                     + navigation       vs ongoing           with IDs +
                     by links"          responsibilities"    dense links"
                              │                    │                    │
                              ▼                    ▼                    ▼
                       ┌──────────┐         ┌──────────┐         ┌────────────────┐
                       │   LYT    │         │   PARA   │         │ ZETTELKASTEN   │
                       │  (MOCs)  │         │ (4-bucket│         │ (timestamped   │
                       │          │         │  actionable)       │  IDs, flat)    │
                       └──────────┘         └──────────┘         └────────────────┘
```

## Quick comparison

| | Generic | LYT | PARA | Zettelkasten |
|---|---|---|---|---|
| Folders | sources/entities/concepts/sessions/ | mocs/notes/ | projects/areas/resources/archives/ | (none — flat) |
| Navigation | folder browse | link follow via MOCs | folder browse | ID reference |
| Naming | descriptive | descriptive | descriptive | timestamp prefix |
| Best for | beginners, mixed use | knowledge clusters | knowledge workers, GTD | researchers, academics |
| Discipline | low | medium | medium | high |

## Per-mode follow-up

After setting mode:

- **Generic**: nothing further; v1.7 behavior preserved
- **LYT**: create your first MOC; new ingests update MOCs automatically via wiki-ingest
- **PARA**: process the `wiki/projects/inbox/` + `wiki/resources/incoming/` buckets periodically
- **Zettelkasten**: build the parent/child relationship graph as notes accumulate; rely on Obsidian Graph view

## Cross-reference

Full guide: [[methodology-modes-guide]]
Skill: [[wiki-mode]] (`skills/wiki-mode/SKILL.md`)
Router: `scripts/wiki-mode.py`
Setup: `bash bin/setup-mode.sh`
