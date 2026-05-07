---
type: concept
title: "Fetch → Validate → Delete Pattern"
complexity: basic
domain: backend-security
aliases:
  - "fetch-validate-delete"
  - "atomic authorization pattern"
created: 2026-05-08
updated: 2026-05-08
tags:
  - concept
  - backend
  - security
  - nestjs
  - prisma
  - authorization
status: mature
related:
  - "[[concepts/_index]]"
  - "[[Heer Backend Standards]]"
sources:
  - "Heer code review session 2026-05-08"
---

# Fetch → Validate → Delete Pattern

Wzorzec autoryzacji dla operacji destruktywnych w NestJS/Prisma. Reguła: **najpierw pobierz zasób, sprawdź uprawnienia, dopiero wtedy usuń**.

## Problem

`prisma.model.delete({ where: { id }, include: { ... } })` zwraca dane dopiero po usunięciu rekordu. Authorization check na danych zwróconych przez `delete()` == sprawdzenie uprawnień PO wykonaniu operacji. Okno wyścigu: rekord znika zanim ktokolwiek sprawdzi, czy użytkownik miał prawo.

```typescript
// ❌ ZŁE — autoryzacja po usunięciu
const deleted = await prisma.poll.delete({
  where: { id: pollId },
  include: { group: { select: { adminId: true } } },
});
if (deleted.creatorId !== userId) throw new ForbiddenException(); // za późno
```

## Rozwiązanie

```typescript
// ✅ DOBRE — trzy etapy
const poll = await prisma.poll.findUnique({
  where: { id: pollId },
  include: { group: { select: { adminId: true } } },
});
if (!poll) throw new NotFoundException();
if (poll.creatorId !== userId && poll.group?.adminId !== userId) {
  throw new ForbiddenException('Not creator or group admin');
}
await prisma.poll.delete({ where: { id: pollId } });
```

## Etapy

| Etap | Operacja | Cel |
|------|----------|-----|
| 1. Fetch | `findUnique({ include: { group: true } })` | Pobranie zasobu + powiązanych danych w jednym query |
| 2. Validate | Sprawdzenie `creatorId` i `group.adminId` | Autoryzacja przed akcją |
| 3. Delete/Action | `delete({ where: { id } })` | Wykonanie dopiero po pozytywnej weryfikacji |

## Łączenie join-ów

Jeśli autoryzacja wymaga danych z powiązanej tabeli (np. `group.adminId`), użyj `include` w kroku Fetch. Eliminuje zbędny round-trip do bazy:

```typescript
// ❌ Dwa queries
const poll = await prisma.poll.findUnique({ where: { id } });
const group = await prisma.group.findUnique({ where: { id: poll.groupId } });

// ✅ Jedno query
const poll = await prisma.poll.findUnique({
  where: { id },
  include: { group: { select: { adminId: true } } },
});
```

## Gdzie stosować

- Wszystkie metody `close()`, `delete()`, `archive()` w serwisach NestJS
- Wszędzie gdzie uprawniony jest inny użytkownik niż creator (np. admin grupy)
- Dotyczy: `PollsService`, `TripsService`, `GroupsService` i wszystkich przyszłych serwisów

## Powiązane wzorce

- **Prisma Error Code Exposure** — kody `P2002`, `P2025` nie mogą trafiać do response body. Loguj server-side, klientowi zwracaj tylko `message`.
- **DTO ↔ Service consistency** — jeśli serwis używa `dto.field!` (non-null assertion), DTO musi mieć ten field jako wymagany (`@IsNotEmpty()` bez `@IsOptional()`).
