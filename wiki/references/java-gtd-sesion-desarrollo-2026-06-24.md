---
type: reference
title: "java-gtd — Sesión de desarrollo 2026-06-24"
created: 2026-06-24
updated: 2026-06-24
tags:
  - java-gtd
  - spring-boot
  - gtd
  - arquitectura
  - sesion
status: active
related:
  - "[[java-gtd]]"
  - "[[java-gtd-git-workflow]]"
---

# java-gtd — Sesión de desarrollo 2026-06-24

Sesión completa de desarrollo sobre el repo `java-gtd` (Spring Boot + Groq + Obsidian vault). Se implementaron cinco features y se establecieron reglas de workflow.

---

## 1. Unificación de referencias (`feature/unified-references`)

**Problema:** las notas de referencia GTD (escritas por la API) iban a `wiki/gtd/reference/` mientras que las notas que guarda Claude iban a `wiki/references/`. Dos carpetas para la misma categoría.

**Solución:** `wiki/references/` como ubicación canónica para todo.

Cambios:
- `VaultService.java` — `referenceDir` apunta a `wiki/references/`
- `scripts/wiki-mode.py` — `DEFAULT_CONFIG.gtd.reference_folder` → `wiki/references/`
- `.vault-meta/mode.json` — actualizado
- `wiki/gtd/referencia.base` — filtro cambiado a `type == "reference"` sin restricción de carpeta (la vista captura referencias de todo el vault)
- `.obsidian/snippets/vault-colors.css` — selector actualizado a `wiki/references`
- Migración física: 4 archivos de `wiki/gtd/reference/` movidos a `wiki/references/`

---

## 2. Multi-tarea en `/api/chat` (`feature/multi-task-chat`)

**Problema:** un solo mensaje puede contener N tareas distintas ("cancelá X, agendá Y, agregale Z a W").

**Diseño clave — por qué se pasan las tareas abiertas al LLM:**
Sin contexto, el LLM no puede saber a qué tarea concreta apunta "la cita de las 16". Al serializar `listAllFlat()` en el prompt, el LLM puede hacer matching semántico y devolver el `target_file` exacto.

**Schema de respuesta del LLM — array de operaciones:**
```json
[
  {"op": "done",   "target_file": "20260624-090000-cita-medico.md"},
  {"op": "create", "bucket": "today", "title": "...", "body": "...", "due": null, "tags": []},
  {"op": "update", "target_file": "20260624-100000-lista-compras.md", "append": "- vino"}
]
```

**Cambios en el código:**

`ClassifierService.classifyAll(message, openTasks)`:
- Serializa `openTasks` a JSON e interpola `{open_tasks}` en el prompt
- Parsea respuesta como `List<Map>` en vez de `Map`

`VaultService`:
- `listAllFlat()` — lista plana con `file`, `title`, `bucket` para contexto del LLM
- `appendToTask(filename, append)` — lee nota, agrega texto al body, reescribe
- `resolveFile(filename)` — helper compartido que busca en `actionsDir` y `referenceDir`

`ChatController`:
- Carga `openTasks`, llama `classifyAll`, itera con `dispatch(op)`
- Cada operación falla de forma independiente (error en una no aborta las otras)
- Devuelve `List<Map>` en vez de `Map`

**Resultado de prueba:**
```
POST /api/chat {"message": "cancelá la cita de las 16, agendá que voy a comer con mi vieja a las 20 y a las compras agregale un vino"}

→ [
    {"op":"done",   "filed":false, "error":"no match encontrado"},   // no había cita en el vault
    {"op":"create", "filed":true,  "file":"...-comer-con-mi-vieja.md", "bucket":"today"},
    {"op":"update", "filed":true,  "file":"comprar-comida-gato.md",    "appended":"un vino"}
  ]
```

---

## 3. Session auto-save counter

El Stop hook de Claude Code llama a `scripts/session-counter.sh` al terminar cada respuesta. Incrementa `.vault-meta/interaction-count.txt`. Cada múltiplo de 10 emite `SAVE_REMINDER` en el output del hook, que dispara el guardado proactivo al vault.

---

## 4. Git workflow — reglas establecidas

**Regla 1 — repos separados:**
- `D:\Maxi\git\claude-obsidian` — vault Obsidian + plugin. **Nunca hacer git aquí desde Claude.**
- `D:\Maxi\git\claude-obsidian\workspace\test-java\Java` — repo java-gtd. Único repo donde hacemos commits.

**Regla 2 — nunca push a master:**
```
git checkout -b feature/<nombre>
# ... cambios ...
git push -u origin feature/<nombre>
# usuario crea PR y mergea desde GitHub
git checkout master && git pull
```

---

## 5. Two-level prompt fallback + discard log (`feature/discard-log-prompt-fallback`)

**Commits:** `5c9f950` (feat) + `6183153` (fix NPE) — PR abierto, pendiente de merge

### 5.1 Two-level prompt

**Problema:** el prompt nivel 1 (`classifier.st`) es liviano. En mensajes ambiguos puede devolver `discard` cuando en realidad hay algo clasificable con más contexto.

**Solución:** retry automático en `ClassifierService`.

```
Nivel 1 → classifier.st (liviano, pocos tokens)
    ↓ si parse falla O todos los ops son now/discard
Nivel 2 → classifier-fallback.st (árbol detallado + 3 ejemplos + "discard es último recurso")
```

`ClassifierService` ahora devuelve `ClassifyResult(ops, usedFallback)`.

**Bug encontrado en tests:** `allNonFiling()` llamaba `Set.of("now","discard").contains(null)` — los ops `done`/`update` no tienen campo `bucket`, y `Set.of()` inmutable lanza NPE con null. Fix: `done`/`update` se cortocircuitan como "útiles" sin leer `bucket`.

### 5.2 Discard log

Items que siguen siendo `discard` después del fallback se loguean en `.vault-meta/discard-log.jsonl` (append, silencioso en error).

```json
{"ts":"2026-06-24T23:38:10Z","message":"hola","ops":[{"op":"create","bucket":"discard",...}]}
```

`VaultService.logDiscard(message, ops)` — nuevo método. `ChatController` lo llama después de `dispatch()`.

### 5.3 Tests ejecutados y resultados

| Test | Input | Resultado | Estado |
|------|-------|-----------|--------|
| Create simple | `"tengo que llamar al medico esta semana"` | `[{op:create, bucket:backlog, filed:true}]` | ✅ |
| Discard + log | `"hola"` | `[{op:create, bucket:discard, filed:false}]` + entrada en `discard-log.jsonl` | ✅ |
| Done + update mismo mensaje | `"ya hice la cama, y al medico agrega que tambien tengo que pedir turno para el dentista"` | `[{op:done, filed:true}, {op:update, filed:true, appended:"..."}]` | ✅ |

---

## Estado del repo al cierre de sesión

```
master
├── PRIMER MVP
├── feat: unified-references (merged)
├── feat: multi-task-chat (merged)
└── feature/discard-log-prompt-fallback (PR abierto — 2 commits)
    ├── ClassifierService — ClassifyResult, two-level retry, fix NPE allNonFiling
    ├── VaultService — logDiscard() → .vault-meta/discard-log.jsonl
    ├── ChatController — llama logDiscard() para ops discard
    └── prompts/classifier-fallback.st — prompt nivel 2
```
