---
type: meta
title: "Lint Report 2026-04-13"
created: 2026-04-13
updated: 2026-04-13
tags: [meta, lint]
status: developing
---

# Lint Report: 2026-04-13

## Summary
- Pages scanned: 7
- Issues found: 29
- Auto-fixed: 0
- Needs review: 29

---

## Dead Links

These wikilinks reference pages that do not exist:

1. **[[Android Location Tracking]]** — referenced in [[Battery Optimization Strategies]], [[Phase 1 Progress]], [[README]]
   - **Suggest:** Create implementation doc or rename to existing page

2. **[[Database Schema]]** — referenced in [[Multi-Instance Configuration]], [[README]]
   - **Suggest:** Create schema doc or link to migration files

3. **[[Discovery Service]]** — referenced in [[README]]
   - **Suggest:** Create stub page (Phase 5 work)

4. **[[Federated Social Architecture]]** — referenced in [[Multi-Instance Configuration]], [[README]]
   - **Suggest:** Create architecture doc or remove from README

5. **[[iOS Location Tracking]]** — referenced in [[Battery Optimization Strategies]], [[Phase 1 Progress]], [[README]]
   - **Suggest:** Create implementation doc or rename to existing page

6. **[[KMM Project Setup]]** — referenced in [[2026-04-13 - Initial Brainstorming]], [[README]]
   - **Suggest:** Create setup guide or remove link

7. **[[Location Tracking Patterns]]** — referenced in [[README]]
   - **Suggest:** Create best practices doc or remove link

8. **[[Performance Mode]]** — referenced in [[Battery Optimization Strategies]], [[README]]
   - **Suggest:** Create feature doc (Phase 2 work)

9. **[[Privacy & Security]]** — referenced in [[Multi-Instance Configuration]], [[README]]
   - **Suggest:** Create privacy doc or link to RLS policies

10. **[[Supabase Backend]]** — referenced in [[2026-04-13 - Initial Brainstorming]], [[README]]
    - **Suggest:** Create backend guide or link to supabase/ directory

11. **[[Tether Cloud]]** — referenced in [[README]]
    - **Suggest:** Create stub page for official instances

12. **[[tether-banner.png]]** — referenced in [[README]]
    - **Suggest:** Add banner image to assets/ or remove banner field

---

## Orphan Pages

These pages exist but have no inbound wikilinks:

1. **[[Roadmap - All Phases]]** — 471 lines, comprehensive roadmap
   - **Suggest:** Link from [[README]] as "Complete Roadmap"

---

## Missing Pages

Concepts mentioned in multiple pages but lacking their own page:

1. **Supabase** — mentioned in 5+ pages, no dedicated page
   - **Suggest:** Create "Supabase Integration Guide" at `knowledge-base/Supabase Integration Guide.md`

2. **Edge Functions** — mentioned in 3 pages, no dedicated page
   - **Suggest:** Create "Edge Functions Overview" or link to supabase/functions/

3. **RLS Policies** — mentioned in 3 pages, no dedicated page
   - **Suggest:** Create "Row-Level Security Guide" at `knowledge-base/Row-Level Security Guide.md`

4. **Mapbox** — mentioned in 3 pages, no dedicated page
   - **Suggest:** Create "Mapbox Integration" stub (Phase 1 remaining work)

---

## Frontmatter Gaps

Pages missing required fields:

1. **[[README]]**
   - Missing: `created`, `updated`
   - Has: `banner`, `tags`, `status`, `phase`, `progress`
   - **Suggest:** Add `created: 2026-04-13`, `updated: 2026-04-13`

2. **[[Phase 1 Progress]]**
   - Missing: `type` (should be `meta` or `project`)
   - Has: `tags`, `date`, `status`, `progress`
   - **Suggest:** Add `type: meta`

3. **[[Roadmap - All Phases]]**
   - Missing: `created`, `updated`, `type`
   - Has: `tags`, `status`
   - **Suggest:** Add `type: meta`, `created: 2026-04-13`, `updated: 2026-04-13`

4. **[[Multi-Instance Configuration]]**
   - Missing: `type` (should be `design` or `architecture`)
   - Has: `tags`, `date`, `status`
   - **Suggest:** Add `type: design`

5. **[[2026-04-13 - Initial Brainstorming]]**
   - Missing: `type` (should be `meeting`)
   - Has: `tags`, `date`, `attendees`, `status`
   - **Suggest:** Add `type: meeting`

6. **[[Battery Optimization Strategies]]**
   - Missing: `type`, `created`, `updated`, `status`
   - Has: `tags`, `category`, `difficulty`
   - **Suggest:** Add `type: knowledge`, `status: complete`, `created: 2026-04-13`, `updated: 2026-04-13`

7. **[[Tether Design Specification]]**
   - Missing: frontmatter entirely (only has title and metadata as text)
   - **Suggest:** Add frontmatter with `type: design`, `tags: [tether, design, spec]`, `status: complete`, `created: 2026-04-13`, `updated: 2026-04-13`

---

## Missing Cross-References

Entities mentioned but not linked:

1. **Kotlin Multiplatform Mobile** — mentioned in [[README]], [[Tether Design Specification]], but not linked
   - **Suggest:** Link first mention to [[KMM Project Setup]] (once created)

2. **Supabase** — mentioned in all pages, rarely linked
   - **Suggest:** Link to [[Supabase Backend]] or [[Supabase Integration Guide]] (once created)

3. **Edge Functions** — mentioned in [[Multi-Instance Configuration]], [[Phase 1 Progress]], not linked
   - **Suggest:** Create wikilink on first mention

4. **Location tracking** — mentioned everywhere, not consistently linked
   - **Suggest:** Link to [[Android Location Tracking]] and [[iOS Location Tracking]] (once created)

---

## Empty Sections

Headings with no content underneath:

None found. All sections have content.

---

## Stale Index Entries

No `index.md` file exists. Index should be created.

---

## Naming Convention Issues

All filenames follow Title Case with spaces ✅  
All folders are lowercase with dashes ✅  
No naming violations found.

---

## Writing Style Check

### Non-Declarative Language

1. **[[Battery Optimization Strategies]]** line 1:
   - "Location tracking is one of the most battery-intensive operations" ✅ (declarative)
   - Overall style is good

2. **[[Multi-Instance Configuration]]** line 1:
   - Uses declarative present tense ✅
   - Overall style is good

3. **[[Tether Design Specification]]** line 1:
   - Uses mostly declarative language ✅
   - Some future-tense statements ("will be implemented") could be rephrased

### Missing Citations

All technical claims have inline context or references to implementation files ✅

### Uncertainties Not Flagged

No `> [!gap]` or `> [!contradiction]` callouts found. Pages are well-defined.

---

## Recommended Actions

### High Priority (Do First)

1. **Create missing implementation docs** (11 dead links):
   - `implementation/Android Location Tracking.md`
   - `implementation/iOS Location Tracking.md`
   - `implementation/KMM Project Setup.md`
   - `implementation/Supabase Backend.md`

2. **Create `wiki/index.md`** (no index currently exists):
   - List all pages with one-line summaries
   - Group by category (design, implementation, knowledge-base, meta)

3. **Add frontmatter to [[Tether Design Specification]]**:
   - Missing frontmatter entirely (most critical spec doc)

4. **Fix frontmatter gaps** on 6 other pages:
   - Add `type`, `created`, `updated` fields

### Medium Priority

5. **Create knowledge base pages** (3 missing pages):
   - `knowledge-base/Supabase Integration Guide.md`
   - `knowledge-base/Row-Level Security Guide.md`
   - `knowledge-base/Mapbox Integration.md`

6. **Create stub pages for future work** (3 dead links):
   - `design/Discovery Service.md` (Phase 5)
   - `design/Federated Social Architecture.md`
   - `design/Performance Mode.md` (Phase 2)

7. **Link orphan pages**:
   - Add [[Roadmap - All Phases]] to [[README]]

### Low Priority

8. **Add cross-references** where entities are mentioned:
   - Link "Supabase" → [[Supabase Backend]]
   - Link "Edge Functions" → Edge Functions page (once created)
   - Link "KMM" → [[KMM Project Setup]] (once created)

9. **Create banner image** or remove banner field from [[README]]

10. **Create meta dashboard** (optional):
    - `meta/dashboard.md` with Dataview queries

---

## Safe to Auto-Fix?

The following can be auto-fixed without human review:

- ✅ Add missing frontmatter fields (`type`, `created`, `updated`) with placeholder values
- ✅ Create `wiki/index.md` with current page list

The following NEED REVIEW before fixing:

- ⚠️ Creating 11 missing pages (may want to rename existing files in GitHub repo instead)
- ⚠️ Removing dead links (pages may exist in `/home/maku/Documents/GitHub/HomeTether/` but not synced to wiki yet)
- ⚠️ Adding wikilinks to existing text (may change meaning)

---

**Should I auto-fix the safe items (frontmatter + index), or do you want to review each one first?**
