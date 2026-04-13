---
tags: [tether, meeting-notes, brainstorming]
date: 2026-04-13
attendees: [User, Claude]
status: completed
---

# Initial Brainstorming Session - Tether Project

**Date:** 2026-04-13  
**Duration:** ~2 hours  
**Outcome:** Complete design specification + 60% Phase 1 implementation

---

## Project Vision

Build an **open-source Life360 alternative** called **Tether** with:
- Family location tracking (privacy-first)
- Travel Stories (Strava-like, but for exploration not speed)
- Federated social features (multi-instance scalable)
- Beautiful UI (Liquid Glass + Material Design themes)

---

## Key Decisions Made

### Tech Stack
- ✅ **Kotlin Multiplatform Mobile** - Share logic between Android/iOS
- ✅ **Supabase** - Auth + Database + Realtime + Storage
- ✅ **Mapbox** - Maps on both platforms
- ✅ **SQLite** - Local offline cache

### Architecture
- ✅ **Federated multi-instance** - Users have "home instance" like email
- ✅ **Runtime discovery** - Auto-discover instance configs via discovery service
- ✅ **Privacy-first** - Circle-only sharing by default, granular controls
- ✅ **30-day location retention** - Auto-delete old data

### Features Prioritized
1. **Core location tracking** (user-configurable frequencies: 5s, 30s, 2m, 5m)
2. **Family circles** (not multi-group yet)
3. **Travel Stories** with achievements (exploration-focused, NOT speed competitions)
4. **Lite social** (follows, reactions, comments - no DMs/stories/hashtags)
5. **Performance mode** (auto-enable at <20% battery)

### UX Decisions
- ✅ **Liquid Glass theme** as default (iOS design language)
- ✅ **Material Design** toggle for Android users
- ✅ **User-friendly errors** (no technical jargon, clear actions)
- ✅ **GitHub bug reporting** (in-app form creates GitHub issues)

---

## Questions Asked & Answered

**Q: What platforms?**  
A: Android + iOS (Kotlin Multiplatform Mobile)

**Q: User relationship model?**  
A: Family circles (simple, can add multi-group later)

**Q: Location update strategy?**  
A: User-configurable (5s, 30s, 2m, 5m) - privacy over automated decisions

**Q: Notification types?**  
A: All configurable (arrival, departure, speed, battery, social, achievements)

**Q: Route history retention?**  
A: 30 days time-limited with auto-deletion

**Q: Strava-like feature?**  
A: Travel Stories with achievements - exploration/reliability focus, NO speed competitions

**Q: Social architecture?**  
A: Federated multi-instance (like Mastodon) for scalability + self-hosting

---

## Design Highlights

### Travel Stories (Not Speed Competitions!)
**Key Insight:** Gamifying speed is dangerous for driving. Instead:
- 🏆 **Achievements** for distance, exploration, reliability, family togetherness
- 📖 **Trip Stories** with photos, shareable with circles
- 📊 **Leaderboards** for safe metrics (distance, punctuality) - NO speed

### Federated Architecture
**Key Insight:** Single Supabase instance won't scale, need federation.
- Users have handle: `alice@tether-cloud-1.app`
- Discovery service auto-configures instances
- Self-hosting supported
- Cross-instance follows/reactions

### Performance Mode
**Key Insight:** Battery drain kills adoption.
- Auto-enable at <20% battery
- Prompt at <30%
- Disables animations, reduces location frequency, lowers map quality

### Error Handling
**Key Insight:** Technical errors confuse users.
- User sees: "Location services are turned off. Tap to open settings."
- NOT: `GPS_PERMISSION_DENIED error code 403`

---

## Implementation Progress (Phase 1: 60%)

### ✅ Completed (4 parallel agents)

1. **KMM Project Setup** (kotlin-specialist agent)
   - 50+ files, Gradle config, version catalogs
   - Shared module with expect/actual pattern
   - Android + iOS targets configured

2. **Supabase Backend** (backend-developer agent)
   - 17 tables (users, circles, locations, trips, achievements, social)
   - 50+ RLS policies for privacy
   - Realtime subscriptions on 5 tables
   - Storage buckets with policies
   - Edge function for 30-day auto-deletion

3. **Android Location Tracking** (mobile-developer agent)
   - FusedLocationProvider integration
   - Foreground service + WorkManager
   - Jetpack Compose permission UI
   - 23 files, ~3,800 lines

4. **iOS Location Tracking** (swift-expert agent)
   - CoreLocation Swift wrapper
   - Kotlin expect/actual bridge
   - SwiftUI permission flow
   - 6 battery optimization strategies
   - 18 files, ~4,135 lines

### ⏸️ Remaining (40%)
5. Family circles UI (Compose + SwiftUI)
6. Real-time map with Mapbox
7. SQLite offline cache

---

## Open Questions for Next Session

1. **Environment variables:** How to handle API keys securely with multi-instance?
   - **Decision:** Runtime discovery + local instance registry (not hardcoded)

2. **Discovery service:** Where to host?
   - Options: Supabase Edge Function, Cloudflare Workers, dedicated API

3. **Self-hoster registration:** Manual approval or automatic?
   - Recommendation: Automatic with email verification

4. **Instance allowlist/blocklist:** Centralized or per-user?
   - Recommendation: Both (global blocklist + user-level allowlist)

---

## Next Steps

### Immediate (This Week)
1. ✅ Save all docs to Obsidian (DONE)
2. Implement Discovery Service (Supabase Edge Function)
3. Implement Multi-Instance Manager (Kotlin shared)
4. Build instance management UI (Compose + SwiftUI)

### Short-term (Next 2 Weeks)
5. Complete Phase 1 remaining 40%
6. Start Phase 2 (UI/UX polish)
7. Set up CI/CD pipeline
8. Beta testing program

---

## Documentation Created

### Design Specs
- ✅ Tether Design Specification (993 lines)
- ✅ Multi-Instance Configuration Architecture

### Implementation Docs
- ✅ KMM Project Setup (README, QUICKSTART, etc.)
- ✅ Supabase Backend (migrations, Edge Functions)
- ✅ Android Location Tracking (complete guide)
- ✅ iOS Location Tracking (START_HERE, usage guides)

### Total Lines: ~15,000+ (code + docs)

---

## Key Takeaways

1. **Parallel agent dispatch saved ~75% time** - 4 agents working simultaneously
2. **Design-first approach prevented scope creep** - Clear spec before coding
3. **Federated architecture is the right call** - Scalability + self-hosting
4. **Privacy-first sells** - Users want control, not forced public
5. **Safety over gamification** - No speed competitions = responsible design

---

## Action Items

- [x] Complete design specification
- [x] Implement 60% of Phase 1
- [x] Save all docs to Obsidian
- [ ] Implement Discovery Service
- [ ] Implement Multi-Instance Manager
- [ ] Complete Phase 1 (family circles, map, offline cache)

---

**Meeting Rating:** ⭐⭐⭐⭐⭐ (Highly productive!)  
**Next Meeting:** TBD (after Discovery Service implementation)
