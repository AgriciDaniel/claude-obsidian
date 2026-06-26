---
type: reference
title: "Sesión 2026-06-26 noche: MCP diagnóstico y migración"
created: "2026-06-26"
updated: "2026-06-26"
tags:
  - session
  - mcp
  - obsidian
  - gtd-frontend
status: evergreen
related:
  - "[[hot]]"
  - "[[log]]"
---

# Sesión 2026-06-26 noche

## MCP Obsidian — Diagnóstico y migración

### Problema inicial
`mcp-obsidian` (uvx/stdio) retornaba error `40012: Unknown or invalid Content-Type` al llamar `obsidian_get_recent_changes`. El plugin Local REST API (v4.1.3) eliminó soporte para `application/vnd.olrapi.dataview.dql+txt` en alguna versión anterior.

### Investigación
- Instalado plugin **Dataview** en Obsidian: no resolvió el problema.
- Confirmado: `main.js` del plugin no contiene la string `dataview.dql` → el content-type no existe en esta versión.
- El plugin **ya incluye su propio servidor MCP** (HTTP built-in) — el nombre del plugin es "Local REST API **with MCP**".
- Puertos: HTTPS 27125, HTTP 27124 (insecure habilitado).

### Migración realizada
**Antes** (mcp-obsidian via uvx, stdio):
```json
{ "type": "stdio", "command": "uvx", "args": ["mcp-obsidian"],
  "env": { "OBSIDIAN_API_KEY": "Bearer 4c6a...", "OBSIDIAN_PORT": "27125" } }
```
Bug adicional: doble `Bearer` en el header (OBSIDIAN_API_KEY ya incluía "Bearer ").

**Después** (HTTP built-in, sin uvx):
```json
{ "type": "http", "url": "http://127.0.0.1:27124/mcp/",
  "headers": { "Authorization": "Bearer 4c6a74b2ebf8..." } }
```

Config completa con rollback en memoria: `reference_mcp_obsidian.md`.

### Estado final
- `obsidian_get_recent_changes`: sigue roto en el nuevo server también. El problema es del plugin, no del transporte.
- Los otros 15 tools del MCP funcionan correctamente.
- La migración igual vale: sin proceso uvx, sin doble-Bearer, server más actualizado.

---

## Token Progress Bar (pendiente)

El usuario quiere una progress bar en gtd-frontend que muestre el uso de tokens en la ventana de 5 horas de Claude. Se planificó una solución (backend lee transcripts JSONL → endpoint → frontend), pero el usuario la rechazó por "muy tirada de los pelos". Está buscando un repo de referencia para replantear el enfoque.

**Estado:** en pausa, esperando repo de referencia del usuario.

---

## Auto-save behavior

El usuario señaló que el trigger de guardar cada ~10 interacciones no se está cumpliendo consistentemente. Hay que revisar y corregir el comportamiento (pendiente al final de esta sesión).

---

## Slang guardado
- **messi** = "me sirve" — aprobación positiva.
