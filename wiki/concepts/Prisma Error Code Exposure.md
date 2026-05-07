---
type: concept
title: "Prisma Error Code Exposure"
complexity: basic
domain: backend-security
aliases:
  - "prisma-error-leak"
  - "database error exposure"
created: 2026-05-08
updated: 2026-05-08
tags:
  - concept
  - security
  - prisma
  - nestjs
  - api
status: mature
related:
  - "[[Fetch-Validate-Delete Pattern]]"
  - "[[concepts/_index]]"
sources:
  - "Heer code review session 2026-05-08"
---

# Prisma Error Code Exposure

Antywzorzec: zwracanie kodów błędów Prismy (`P2002`, `P2025`, `P2003`) w response body API. Ujawnia strukturę bazy danych klientowi.

## Problem

```typescript
// ❌ ZŁE — kod P2002 w response
return {
  statusCode: 409,
  message: 'Conflict',
  extra: { code: exception.code }, // P2002 = unique constraint
};
```

Klient widzi `P2002` → wie, że używasz Prismy, zna constraint który złamał, może mapować pola.

## Rozwiązanie

```typescript
// ✅ DOBRE — tylko message dla klienta
// Log: pełny błąd (code, meta) server-side
this.logger.error({ code: exception.code, meta: exception.meta });

// Response: tylko komunikat
return {
  statusCode: 409,
  message: 'Resource already exists',
};
```

## Kody Prisma → przyjazne komunikaty

| Kod | Znaczenie | Bezpieczna wiadomość |
|-----|-----------|---------------------|
| `P2002` | Unique constraint violation | "Resource already exists" |
| `P2025` | Record not found | "Resource not found" |
| `P2003` | Foreign key constraint | "Related resource not found" |

## Gdzie w Heer

`backend/src/common/filters/app-exception.filter.ts` — filtr wyjątków aplikacji. Usunięto `extra: { code: exception.code }` z odpowiedzi.
