---
type: reference
title: java-gtd
status: active
created: 2026-06-24
updated: 2026-06-24
tags:
  - gtd
  - java
  - spring-boot
  - proyecto
related:
  - "[[index]]"
  - "[[gtd/_index]]"
---

# java-gtd

REST API en **Spring Boot 3 + Spring AI + Groq (Llama 3.3-70b)** que corre el árbol de decisión GTD sobre input en lenguaje natural y archiva el resultado como nota Markdown en este vault.

## Repo y paths

- **GitHub:** https://github.com/mmilei/java-gtd
- **Local:** `D:\Maxi\git\claude-obsidian\workspace\test-java\Java`
- **Vault destino:** `D:/Maxi/git/claude-obsidian` (este vault)
- **Escribe en:** `wiki/gtd/actions/` y `wiki/gtd/reference/`

## Arquitectura

| Clase | Rol |
|-------|-----|
| `ClassifierService` | Llama a Groq, parsea JSON del árbol GTD |
| `VaultService` | Escribe / lista / marca-done notas Markdown con frontmatter YAML |
| `MarkdownSerializer` | Serializa / parsea frontmatter vía SnakeYAML |
| `ChatController` | `POST /api/chat` — clasifica y archiva |
| `BucketController` | `GET /api/today`, `/api/buckets`, `/api/buckets/{bucket}`, `POST /api/items/{filename}/done` |

Prompt: `src/main/resources/prompts/classifier.st`

## Buckets

| Bucket | Comportamiento |
|--------|----------------|
| `today` | Se archiva en `actions/` |
| `backlog` | Se archiva en `actions/` |
| `waiting` | Se archiva en `actions/`, campo `delegado_a` |
| `someday` | Se archiva en `actions/` |
| `reference` | Se archiva en `reference/` |
| `now` | No se archiva — regla de los 2 minutos |
| `discard` | No se archiva |

## Configuración

Variable de entorno `GROQ_API_KEY` + vault path en `application-local.properties` (gitignored):

```properties
gtd.vault.path=D:/Maxi/git/claude-obsidian
```

## Uso rápido

```bash
# Correr
mvn spring-boot:run

# Clasificar un item
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "llamar al médico la semana que viene"}'

# Ver pendientes de hoy
curl http://localhost:8080/api/today
```
