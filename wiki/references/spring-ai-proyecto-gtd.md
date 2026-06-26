---
type: reference
title: "Proyecto Spring AI — GTD API"
created: "2026-06-24"
updated: "2026-06-24"
tags:
  - gtd
  - reference
  - java
  - spring-ai
  - portfolio
related: []
---

# Proyecto Spring AI — GTD API

API REST en Java que replica el triage GTD de Claudio: input en lenguaje natural → árbol de decisión (Maxi_idea.md) → archivo `.md` con timestamp en el vault.

## Ubicación

```
D:\Maxi\git\claude-obsidian\workspace\test-java\Java
```

## Stack

- Java 21 (virtual threads activados)
- Spring Boot 3.3.5
- Spring AI 1.0.0-M6
- Maven

## Estructura del proyecto

```
Java/
  pom.xml
  src/main/java/ar/maxi/gtd/
    GtdApplication.java
    api/ChatController.java         ← POST /api/chat
    api/BucketController.java       ← GET /api/buckets, /api/today, POST done
    service/ClassifierService.java  ← llama al LLM, devuelve Map
    service/VaultService.java       ← lee/escribe .md en el vault
    util/MarkdownSerializer.java    ← frontmatter YAML ↔ Map
  src/main/resources/
    application.properties
    prompts/classifier.st           ← árbol de decisión GTD
```

## Endpoints

| Método | Path | Qué hace |
|--------|------|----------|
| POST | `/api/chat` | Clasifica y archiva. Body: `{"message":"..."}` |
| GET | `/api/today` | Items del bucket today |
| GET | `/api/buckets` | Todos los buckets activos |
| GET | `/api/buckets/{bucket}` | Items de un bucket específico |
| POST | `/api/items/{filename}/done` | Marca item como done |

## Switching de providers

El código Java no cambia entre providers. Solo cambia `application.properties`.

### Groq (activo)

```properties
spring.ai.openai.api-key=${GROQ_API_KEY}
spring.ai.openai.base-url=https://api.groq.com/openai
spring.ai.openai.chat.options.model=llama-3.3-70b-versatile
spring.ai.openai.chat.options.stream=false
spring.ai.retry.max-attempts=1
```

### Google AI Studio / Gemini

```properties
spring.ai.openai.api-key=${GOOGLE_API_KEY}
spring.ai.openai.base-url=https://generativelanguage.googleapis.com/v1beta/openai/
spring.ai.openai.chat.options.model=gemini-2.0-flash
```

### Anthropic (JavaClaude/)

```properties
spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY}
spring.ai.anthropic.chat.options.model=claude-sonnet-4-6
```

## Levantar el servidor

```powershell
$env:GROQ_API_KEY = [System.Environment]::GetEnvironmentVariable("GROQ_API_KEY", "User")
cd "D:\Maxi\git\claude-obsidian\Java"
mvn spring-boot:run
```

## Gotchas aprendidos

- **Vertex AI ≠ Google AI Studio**: `spring-ai-vertex-ai-gemini-spring-boot-starter` requiere GCP project-id. Para AI Studio usar el starter OpenAI con base-url de Google.
- **URL duplicada en Groq**: no agregar `/v1/` al base-url — Spring AI lo agrega solo. URL correcta: `https://api.groq.com/openai` (sin `/v1/`).
- **Streaming en Groq**: agregar `spring.ai.openai.chat.options.stream=false` para evitar `HttpRetryException`.
- **Spring AI 1.0.0 GA no está en Maven Central**: usar `1.0.0-M6`.
- **Variables de entorno en PowerShell**: leer del nivel User con `[System.Environment]::GetEnvironmentVariable("KEY", "User")` y asignar a `$env:KEY` antes de `mvn spring-boot:run`.
- **Encoding UTF-8 en PowerShell**: para caracteres con tilde usar `[System.Text.Encoding]::UTF8.GetBytes(...)` en el body del curl.

## Schema flexible

`ClassifierService` devuelve `Map<String, Object>`. `VaultService` escribe todo como frontmatter YAML. Para agregar un campo nuevo: editar `classifier.st`, reiniciar una vez. Los archivos viejos no se rompen.

## Vault path

Hardcodeado en `VaultService.java:13`: `D:/Maxi/git/claude-obsidian`
