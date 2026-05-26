---
type: decision
title: "SuperApp Access Control Model"
created: 2026-05-22
updated: 2026-05-22
decision_date: 2026-05-22
status: active
tags:
  - decision
  - laba-mvp
  - production-super-app
  - access-control
  - rbac
related:
  - "[[Brand Book — Laba MVP]]"
  - "[[Applying Laba Brand Book to a New Product]]"
  - "[[App-Level vs RLS Tenant Scoping]]"
  - "[[Multi-Tenant ATS Data Model]]"
---

# SuperApp Access Control Model

The Laba Production Super App is an internal Next.js shell that wraps several Laba products (Researchius, Name Testius, Scoutius, Coursius, Textius, plus placeholders) as iframes behind a single login. Until this redesign it used a global role enum — `admin / editor / reader` — which gave or denied access to the entire app at once.

This page captures the **15 access-control decisions** that replaced that model with per-product, per-project grants plus an email-whitelist onboarding flow. The decisions came out of one structured grill-me session and are the binding contract for the implementation.

---

## TL;DR

- Access is granted on `(email, product, project)` triples. `product_id = NULL` is never used; `project_id = NULL` means "all projects".
- Onboarding is **email-whitelist**: an admin adds the email + grants up-front, the person goes to `/signup` and is admitted iff their email is in `allowed_emails`. No invitation emails. A DB trigger blocks `auth.users` inserts for non-whitelisted emails.
- **Owner** is a hardcoded boolean (`allowed_emails.is_owner`). Owners have implicit full access to every product in every project. Seeded via SQL — there is no UI to create the first owners — but the invite form CAN promote new users to owner.
- Active project is held in the `laba_project` cookie + supported as `?project=` deep-link query.
- Materials text data is stored per-project; materials_content PK = `(item_id, project_id)`.
- Tool URLs live in `product_urls(product_id, project_id NULLABLE, url, embed_mode)`. `project_id = NULL` row is the default; per-project rows override.

---

## The 15 locked decisions

| # | Question | Answer |
|---|---|---|
| 1 | Unit of access | **Logical product** (Scoutius is one product across all stages; Materials is one product across its 6 sub-items). |
| 2 | Grant level | **Binary** has-access / no-access. No per-product read/write modes. |
| 3 | Granularity | **Product × project** matrix. |
| 4 | "All projects" representation | `project_id = NULL` wildcard inside the grant row. |
| 5 | UI visibility | **Hide** non-accessible projects/stages/items. Users with zero grants see "Contact admin". |
| 6 | Onboarding | **Email-whitelist**, not invitation emails. |
| 7 | Materials write | Anyone with the Materials grant can edit text. No read-only sub-mode. |
| 8 | Admin UI shape | List of rows: **product → multi-select of projects** with "All projects" as the first option. |
| 9 | Existing-user migration | Trivial — only Vlad + Artem exist, seeded as owners. |
| 10 | Privileged tier | **Owner** is hardcoded. No UI-controlled "Admin" tier. |
| 11 | Active project source | **Cookie** as primary, `?project=` query as deep-link override. |
| 12 | Materials data scope | **Per-project**. Existing rows migrated to `ua-laba`. |
| 13 | Tool URLs scope | Default URL per product + optional per-project overrides. |
| 14 | Revoke / delete | Cascade grants on whitelist removal + soft-disable toggle + confirmed Delete Forever (owner-only). |
| 15 | Products / projects source | **Code** (`lib/products.ts`, `lib/projects.ts`). No DB table, no admin UI to manage them. |

---

## Schema

```sql
create table allowed_emails (
  email        text primary key,
  is_owner     boolean not null default false,
  is_disabled  boolean not null default false,
  created_at   timestamptz not null default now(),
  created_by   uuid references auth.users(id) on delete set null
);

create table grants (
  email        text not null references allowed_emails(email) on delete cascade,
  product_id   text not null,
  project_id   text,                                          -- NULL = all projects
  created_at   timestamptz not null default now()
);
create unique index grants_email_product_project_uniq
  on grants (email, product_id, coalesce(project_id, '__all__'));

create table product_urls (
  product_id   text not null,
  project_id   text,                                          -- NULL = default
  url          text not null default '',
  embed_mode   text not null default 'proxy',
  updated_at   timestamptz not null default now()
);
```

A SECURITY DEFINER helper `is_owner()` powers every RLS policy so a non-owner session can ask "am I an owner?" without exposing the table.

---

## Defense-in-depth gates

| Layer | What it checks |
|---|---|
| `/signup` page server action | Email is in `allowed_emails` and not disabled. Friendly "Contact admin" screen otherwise. |
| Postgres `BEFORE INSERT ON auth.users` trigger | Same check, fires even if the UI is bypassed. |
| `middleware.ts` | Redirects non-authed users to `/login`. |
| `/app/page.tsx` server render | Calls `getUserAccess()`, filters `STAGES` and projects, refuses if no visible products. |
| `/embed/[stage]/[item]/[[...path]]` proxy | Re-runs the grant check using `(product_id, cookie-project)`. 403 on miss. Also injects `?project=` to the upstream URL. |
| RLS on `allowed_emails`, `grants`, `product_urls`, `materials_content` | Owner-or-self read; owner-only write. |

The proxy gate is the most important one: without it any logged-in user could open `/embed/research/scoutius/...` directly and bypass the UI.

---

## Owner-vs-Regular toggle on invite (added 2026-05-22)

The original Q10 decision said owners are hardcoded SQL-only. After the system was live the invite form gained an explicit **Regular | Owner** segmented control:

- Regular (default) — shows the GrantsEditor below; per-product grants are required.
- Owner — hides GrantsEditor; the `createUser` action sets `is_owner=true` and inserts zero grant rows because owners have implicit full access.

This relaxes Q10 only in one direction: new owners can be promoted from another owner's session. There is still no UI to **demote** an owner — the seeded ones (Vlad, Artem) stay locked, and the edit page treats every owner row as `Locked`.

---

## What is NOT in the model

- **No teams or groups.** Each grant is per-email. If Marketing needs Name Testius, all five marketers get five separate grant rows.
- **No "all products" wildcard.** `is_owner = true` is the only way to access everything. There is no `product_id = NULL` row.
- **No expiry, no time-bounded grants.** Access is either granted or not.
- **No audit log.** Inserts/updates are not surfaced anywhere. Add later if compliance demands.
- **No per-product read/write distinction.** Iframe products manage their own permissions; the shell only gates visibility.

---

## Implementation status

All five rollout phases shipped on `main` of `temson94/production-super-app`:

1. Schema migration + lib helpers — PR #1 (squashed `0e6793a`)
2. Server-side enforcement — same PR
3. Shell UI filtering — same PR
4. New admin UI — same PR
5. Cleanup of `profiles` / `user_role` / `tool_settings` — same PR

Followed by hotfixes for migration ordering (`#2`, `#3`, `#4`), the materials/picker simplifications (`#6`), the broken Tailwind v4 redesign + revert (`#7-#11`), and the eventually-working Brand Book pass (`#12-#21`).

Full plan checked into the repo as `PLAN.md`. Migration files: `supabase/migrations/005_access_control.sql`, `006_materials_per_project.sql`, `007_cleanup_legacy_roles.sql`, `008_drop_materials.sql`.
