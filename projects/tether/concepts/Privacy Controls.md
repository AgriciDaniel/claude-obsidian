---
name: Privacy Controls
description: Extracted privacy controls and RLS-based enforcement recommendations
type: concept
---

# Privacy Controls

Highlights:
- Default circle-only visibility
- Per-trip visibility overrides
- Block users and instances
- Delete federated data (GDPR compliance)
- Use Supabase RLS to enforce row-level access: sample policies needed

Action items:
- Draft RLS policies for locations, trips, trip_photos
- Decide on end-to-end encryption (E2EE) for location payloads (open question)

> [!gap] E2EE decision pending. Adds significant complexity for federated search and notifications.

