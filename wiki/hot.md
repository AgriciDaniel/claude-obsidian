---
type: meta
title: "Hot Cache"
updated: 2026-06-26T00:00:00
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[Wiki Map]]"
  - "[[getting-started]]"
  - "[[DragonScale Memory]]"
---

# Recent Context

Navigation: [[index]] | [[log]] | [[overview]]

## Last Updated

2026-06-26: Sesión noche. MCP migrado: mcp-obsidian (uvx/stdio) → built-in HTTP server (http://127.0.0.1:27124/mcp/). `get_recent_changes` sigue roto (DQL deprecated en plugin v4.1.3), resto de tools OK. Plan token progress bar para gtd-frontend rechazado, esperando repo de referencia del usuario. Auto-save behavior a corregir.

2026-06-26: Sesión buenas noches. Indexado proyecto GTD (2 repos). Fix MCP Obsidian: cambio en `obsidian.py` puerto 27124→27125. Requiere reinicio de Claude Code para aplicar. MCP no testeado todavía.

2026-06-25: Sesión buenas noches. Tarea GTD `ir-a-dormir` marcada done. Nota guardada en `wiki/gtd/reference/20260625-buenas-noches.md`.

2026-06-25: Limpieza de hot cache. Eliminado historial de dev heredado del repo original (v1.6-v1.9), Key Lessons, Install ID de agricidaniel, Repo Locations incorrectas. Removido bloque Release Blog Post de CLAUDE.md. Agregada sección Emotional Awareness a CLAUDE.md (tagging interno ai-x, nunca preguntar directo).

2026-06-24: v1.10.0 implementado localmente. GTD como 5to modo de metodología (Generic/LYT/PARA/Zettelkasten/GTD). Nueva skill `wiki-triage` con árbol de decisión David Allen. `scripts/wiki-mode.py` con flags `--bucket` y `--due`. 4 templates en `skills/wiki-mode/templates/gtd/`. Tests: 10 templates, 5 modos.

## Plugin State

- **Version**: 1.10.0
- **Skills**: 16 (wiki, wiki-ingest, wiki-query, wiki-lint, wiki-fold, save, autoresearch, canvas, defuddle, obsidian-bases, obsidian-markdown, wiki-cli, wiki-retrieve, wiki-mode, think, wiki-triage)
- **Scripts (v1.6)**: `scripts/allocate-address.sh`, `scripts/tiling-check.py`, `scripts/boundary-score.py`
- **Scripts (v1.7)**: `scripts/detect-transport.sh`, `scripts/contextual-prefix.py`, `scripts/bm25-index.py`, `scripts/rerank.py`, `scripts/retrieve.py`, `scripts/wiki-lock.sh`
- **Scripts (v1.8)**: `scripts/wiki-mode.py`, `bin/setup-mode.sh`
- **Setup**: `bin/setup-vault.sh`, `bin/setup-dragonscale.sh`, `bin/setup-multi-agent.sh`, `bin/setup-retrieve.sh`, `bin/setup-mode.sh`
- **Hooks**: 4 (SessionStart, PostCompact, PostToolUse, Stop)
- **Repo**: `D:\Maxi\git\claude-obsidian`

## DragonScale Mechanisms

1. **Fold operator** (M1): `skills/wiki-fold/` — log rollups, primer fold real en `wiki/folds/`.
2. **Deterministic addresses** (M2): `scripts/allocate-address.sh` — frontmatter `address: c-NNNNNN`, vault counter en 3.
3. **Semantic tiling lint** (M3): `scripts/tiling-check.py` — primer tiling report en `wiki/meta/tiling-report-2026-04-24.md`.
4. **Boundary-first autoresearch** (M4): `scripts/boundary-score.py` — `/autoresearch` sin tema propone frontier pages (opt-in).

## Style Preferences

- Sin em dashes (U+2014) ni `--` como puntuación. Puntos, comas, dos puntos o paréntesis.
- Respuestas cortas y directas.
- Tool calls paralelos cuando son independientes.

## Active Threads

### Proyecto GTD (2 repos independientes)

**Backend — java-gtd**
- Path local: `workspace\test-java\Java`
- GitHub: https://github.com/mmilei/java-gtd
- Stack: Spring Boot 3.3.5 + Spring AI + Groq (Llama 3.3-70b)
- Estado: master limpio, 27 tests, 12 endpoints.

**Frontend — gtd-frontend**
- Path local: `workspace\test-node\gtd-frontend`
- GitHub: https://github.com/mmilei/gtd-frontend
- Stack: Vite + Three.js + TailwindCSS
- Estado: repo inicializado, `src/scene.js` presente.

**Vault GTD:** `wiki/gtd/` — acciones, reference, bases.
**Pendiente:** definir próximo paso concreto (feature, integración, deploy, etc).
