---
name: Supabase Schema
description: Extracted Supabase PostgreSQL schema for Tether (core tables, trips, federation tables)
type: reference
---

# Supabase Schema

Contains CREATE TABLE statements and indexes extracted from the design spec. Key tables: users, circles, circle_members, locations, places, notification_preferences, trips, achievements, user_achievements, trip_photos, follows, reactions, comments, federated_instances, federated_users, outbox, inbox.

## Notes & action items
- Verify DECIMAL precision for latitude/longitude on both platforms.
- Confirm pg_cron availability in hosted Supabase; consider Edge Function alternative if not available.

