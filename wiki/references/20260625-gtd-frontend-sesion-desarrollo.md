---
type: session
title: "GTD Frontend — Sesión de desarrollo 2026-06-25"
created: 2026-06-25
updated: 2026-06-25
tags:
  - gtd
  - frontend
  - java-gtd
  - vite
  - dev-session
status: developing
related:
  - "[[java-gtd]]"
  - "[[spring-ai-proyecto-gtd]]"
  - "[[java-gtd-sesion-desarrollo-2026-06-24]]"
---

# GTD Frontend — Sesión de desarrollo 2026-06-25

Sesión completa de construcción del frontend GTD sobre el backend Java ya estabilizado.

## Repos involucrados

- **Backend**: `D:\Maxi\git\claude-obsidian\workspace\test-java\Java` → GitHub `mmilei/java-gtd`
- **Frontend**: `D:\Maxi\git\claude-obsidian\workspace\test-node\gtd-frontend` → GitHub `mmilei/gtd-frontend`
- Backend no fue tocado en esta sesión. Todo el trabajo fue frontend.

## Setup de git del frontend

El directorio `workspace/test-node/gtd-frontend` estaba vacío y heredando el `.git` de `claude-obsidian`. La solución: `workspace/` ya está en el `.gitignore` de claude-obsidian, así que se clonó el repo `mmilei/gtd-frontend` directamente ahí como repo anidado.

```bash
git clone https://github.com/mmilei/gtd-frontend "D:\Maxi\git\claude-obsidian\workspace\test-node\gtd-frontend"
```

Git identity local seteada en el repo clonado:
```bash
git config user.email "mileimaximiliano@gmail.com"
git config user.name "mmilei"
```

## Cómo levantar los servidores

**Backend (8080):**
```powershell
$key = [System.Environment]::GetEnvironmentVariable("GROQ_API_KEY", "User")
cd D:\Maxi\git\claude-obsidian\workspace\test-java\Java
mvn spring-boot:run "-DGROQ_API_KEY=$key"
```

**Frontend (5173):**
```powershell
cd D:\Maxi\git\claude-obsidian\workspace\test-node\gtd-frontend
npm run dev
```

Si es clone fresco, correr `npm install` antes.

## Bugs corregidos

### Bug 1 — chat() sin destructuring
`main.js` pasaba el objeto `{fallback, ops}` completo a `appendApiResponse()` como si fuera el array de ops. Esto causaba TypeError y `refreshBuckets()` nunca corría.

**Fix:** `const { fallback, ops } = await chat(text)`

### Bug 2 — tags no renderizados
`itemCard()` en `buckets.js` no tenía código para mostrar `item.tags`.

**Fix:** Agregado rendering de tags con filtro de tags de sistema (`gtd`, `action`, `reference`, `project`).

## Features implementadas

### Animación "boink" al marcar done
- CSS `@keyframes boink`: card escala a 1.05x con flash verde, luego se contrae y desaparece (280ms)
- Web Audio API `playBoink()`: oscilador sine 880Hz → 440Hz, decay 180ms. Sin archivos externos.
- Three.js `pulse()` dispara simultáneamente para efecto en el background.

### Preview del body en cards
Primera línea no-markdown del `item.body` (máx 80 chars) aparece en las cards del sidebar, en gris tenue.

```js
function bodySnippet(body) {
  const line = body.split('\n').find(l => l.trim() && !/^#+\s/.test(l) && !/^[-*]\s/.test(l))
  return line ? line.trim().slice(0, 80) + (line.length > 80 ? '…' : '') : ''
}
```

### Modal de edición
Click en cualquier card (excepto el botón done) abre un modal con:
- Título de la tarea (display only)
- Textarea editable con el body completo
- Guardar con `PUT /api/items/{file}/body`, Ctrl+Enter como shortcut
- Escape cierra sin guardar

Implementado en `src/modal.js` (nuevo archivo).

**API agregada en `api.js`:**
- `fetchItem(filename)` → `GET /api/items/{file}`
- `replaceBody(filename, body)` → `PUT /api/items/{file}/body`

### Tag Bar interactiva
Fila horizontal de pills sobre la lista de items, debajo de los tabs de bucket.

- Muestra todos los tags no-sistema del bucket actual con su conteo
- Click en pill → filtra items; click de nuevo → deselecciona
- Se resetea al cambiar de bucket
- Se oculta automáticamente si no hay tags en el bucket (`.tag-bar:empty { display: none }`)
- Tags de sistema filtrados: `gtd`, `action`, `reference`, `project`

### Panel de Referencias (slide-in)
Panel que se abre desde la derecha (380px) con botón "Ref" en el header o tecla `R`.

- Search client-side por título + body en tiempo real
- Cards ricas: título + 3 líneas de body + fecha + todos los tags
- Agrupadas por primer tag no-sistema; grupo `—` al final
- Click en card → abre modal de edición
- Se refresca automáticamente si está abierto después de un mensaje al chat
- Escape cierra el panel
- Implementado en `src/refs.js` (nuevo archivo)

## Idea registrada en TODO.md

**Markdownify**: endpoint que toma el body vago de una tarea y lo pasa por el LLM (Groq ya integrado) para enriquecerlo — extraer tags, formatear markdown, identificar subtareas. Se activaría desde el modal con un botón "✨ Mejorar".

## Estado de ramas al cierre

Ambos repos en `master`, limpios:
- Frontend: `master` @ `8b0c038` (incluye `fix/chat-response-tags` y `feat/boink-preview-edit-modal` mergeados)
- Backend: `master` @ `773e1d7`

Rama activa en frontend al cierre: `feat/tag-bar` (pusheada, pendiente de PR + merge).

## Próxima sesión

- Mergear `feat/tag-bar` (tag bar + panel referencias)
- Implementar `feat/refs-panel` como rama separada si se quiere separar
- Implementar tag cross-bucket (`GET /api/tags` en backend)
- Evaluar vista Galaxy (grafo de referencias por tag)
- Markdownify (LLM enrichment del body)
