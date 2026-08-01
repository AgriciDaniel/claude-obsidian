---
date: 2026-08-01
project: scrap-finance-partners
agent: codex
status: in-progress
---

## What I did

- Reviewed the current industrial evidence-room design and its desktop homepage capture.
- Located the client-preferred Bloomberg-terminal redesign at commit `0c3cc5e` and compared its visual language with the current site.
- Planned a Bloomberg-dominant blend that preserves the current evidence structure, approval gating, pricing, routes, mobile navigation, forms, and accessibility work.
- Refreshed the codebase knowledge graph for the current repository structure.

## Files changed

- No Scrap Finance Partners project files changed; this was a planning-only session.
- Added this vault session note.

## Decisions made

- Use the old Bloomberg version as an art-direction reference, not a commit to cherry-pick: the current route and data model are safer and more mature.
- Make the global canvas dark graphite with copper and restrained semantic colours; use the current light evidence-document treatment only as a deliberate contrast island.
- Restore data density, terminal labels, compact status strips, tabular layouts, and a split hero while retaining the current pain-led copy and real conversion path.
- Do not restore fake live claims, unverified savings figures, glass/glow, decorative grid/noise textures, or old inaccessible motion.
- Prototype the shared shell and homepage first, obtain visual approval, then roll the system across all secondary routes.

## Next steps

- Create `agents/scrap-finance-bloomberg-blend` when implementation is approved.
- Build the shared dark token layer, header/footer, and homepage prototype.
- Validate the prototype at desktop and mobile widths before extending it to Health Check, How We Help, Case Study, About, Ways to Work Together, Updates, Contact, and Privacy.
- Run the production build, interaction tests, accessibility checks, and route screenshots before opening a PR.
