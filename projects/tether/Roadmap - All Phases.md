---
tags: [tether, tasks, roadmap, phases]
status: active
---

# Tether Development Roadmap - All Phases

Complete task breakdown for all 6 phases of Tether development.

---

## Phase 1: Core Location Tracking (60% Complete)

**Timeline:** Months 1-2  
**Status:** In Progress

### Completed Tasks ✅

- [x] Kotlin Multiplatform project setup
- [x] Supabase backend integration (17 tables, RLS policies)
- [x] Android location tracking (FusedLocationProvider)
- [x] iOS location tracking (CoreLocation)

### Remaining Tasks ⏸️

- [ ] **Family Circles UI** (1 week)
  - [ ] Create circle screen (Compose + SwiftUI)
  - [ ] Join circle via invite code
  - [ ] Circle member list view
  - [ ] Leave circle functionality
  - [ ] Circle settings (name, admin controls)
  - [ ] Integration with Supabase `circles` table

- [ ] **Real-time Map with Mapbox** (1.5 weeks)
  - [ ] Mapbox SDK integration (Android + iOS)
  - [ ] Map view component (Compose + SwiftUI)
  - [ ] Display user's current location
  - [ ] Display circle members' locations
  - [ ] Real-time marker updates (Supabase Realtime)
  - [ ] Map controls (zoom, center, follow mode)
  - [ ] Custom markers with user avatars
  - [ ] Location accuracy indicators

- [ ] **SQLite Offline Cache** (1 week)
  - [ ] SQLite schema for local cache
  - [ ] Location history cache (30-day window)
  - [ ] Circle member cache
  - [ ] Sync queue for offline writes
  - [ ] Background sync worker
  - [ ] Conflict resolution (last-write-wins)
  - [ ] Cache invalidation strategy

- [ ] **Basic Error Handling** (3 days)
  - [ ] Network error handling
  - [ ] Permission denied flows
  - [ ] GPS disabled handling
  - [ ] User-friendly error messages

---

## Phase 2: UI/UX Polish (0% Complete)

**Timeline:** Month 3  
**Status:** Not Started

### Design System

- [ ] **Liquid Glass Theme Implementation** (1 week)
  - [ ] Frosted glass blur effects (Android + iOS)
  - [ ] Translucent backgrounds with depth
  - [ ] Elevation via blur intensity
  - [ ] Spring-based animations
  - [ ] Map overlay cards (blur-based)
  - [ ] Frosted navigation bars

- [ ] **Material Design Theme** (1 week)
  - [ ] Material 3 design language (Android)
  - [ ] Dynamic color support
  - [ ] Elevation shadows
  - [ ] Standard Material motion
  - [ ] Theme toggle in settings
  - [ ] Persist theme preference

### Performance & Animations

- [ ] **Animation System** (3 days)
  - [ ] Standard mode (60fps spring animations)
  - [ ] Performance mode (no animations)
  - [ ] Blur transitions
  - [ ] Map marker animations
  - [ ] Bottom sheet transitions

- [ ] **Performance Mode** (1 week)
  - [ ] Auto-enable at <20% battery
  - [ ] Prompt at <30% battery
  - [ ] Disable all animations
  - [ ] Reduce map rendering quality
  - [ ] Lower location update frequency
  - [ ] Battery monitoring service
  - [ ] User manual toggle

### Notifications

- [ ] **Notification System** (1 week)
  - [ ] FCM (Android) + APNs (iOS) setup
  - [ ] Supabase Edge Function for triggers
  - [ ] Arrival alerts (geofence enter)
  - [ ] Departure alerts (geofence exit)
  - [ ] Speed alerts (threshold exceeded)
  - [ ] Low battery alerts (<15%)
  - [ ] Push notification UI

- [ ] **Notification Preferences** (3 days)
  - [ ] Granular toggle per type
  - [ ] Per-circle notification settings
  - [ ] Quiet hours configuration
  - [ ] Emergency override settings
  - [ ] Notification history view

### Saved Places

- [ ] **Places Management** (1 week)
  - [ ] Add saved place (Home, Work, etc.)
  - [ ] Geofence radius configuration
  - [ ] Edit/delete places
  - [ ] Place icons/colors
  - [ ] Auto-suggest from frequent locations
  - [ ] Integration with notifications

---

## Phase 3: Travel Stories (0% Complete)

**Timeline:** Months 4-5  
**Status:** Not Started

### Trip Recording

- [ ] **Automatic Trip Detection** (1 week)
  - [ ] Start trip (speed >5mph for 30s)
  - [ ] End trip (stationary <5mph for 5min)
  - [ ] Calculate distance (Haversine)
  - [ ] Calculate max/avg speed
  - [ ] Generate route polyline
  - [ ] Manual start/stop controls
  - [ ] Discard trip option

- [ ] **Trip Storage & Retrieval** (3 days)
  - [ ] Save trip to Supabase `trips` table
  - [ ] Query user's trip history
  - [ ] 30-day auto-deletion (part of location cleanup)
  - [ ] Trip details view
  - [ ] Route visualization on map

### Achievements

- [ ] **Achievement System** (1 week)
  - [ ] Seed 12 achievements in database
  - [ ] Background job to check unlock conditions
  - [ ] Unlock logic (distance, exploration, reliability, social)
  - [ ] Push notification on unlock
  - [ ] Achievement badge UI
  - [ ] User achievement collection view
  - [ ] Circle member achievement feed

- [ ] **Achievement Categories** (included above)
  - [ ] Distance (Road Warrior, Globe Trotter, Wanderer)
  - [ ] Exploration (Explorer, Adventurer, Nomad)
  - [ ] Reliability (Reliable, Punctual, Timekeeper)
  - [ ] Social (Adventure Squad, Travel Buddy, Storyteller)

### Trip Sharing

- [ ] **Trip Stories UI** (1 week)
  - [ ] Trip detail screen
  - [ ] Route map visualization
  - [ ] Trip stats display (distance, speed, duration)
  - [ ] Achievement badges earned during trip
  - [ ] Photo upload integration
  - [ ] Visibility selector (circle/followers/public/unlisted)

- [ ] **Photo Integration** (3 days)
  - [ ] Photo upload to Supabase Storage
  - [ ] Trip photo gallery
  - [ ] Photo captions
  - [ ] Image compression before upload
  - [ ] Photo deletion

### Leaderboards

- [ ] **Circle Leaderboards** (1 week)
  - [ ] Total distance leaderboard
  - [ ] Unique locations leaderboard
  - [ ] Punctuality score leaderboard
  - [ ] Opt-in/opt-out per metric
  - [ ] Circle-only (not global)
  - [ ] Refresh weekly/monthly

---

## Phase 4: Social Features (0% Complete)

**Timeline:** Months 6-7  
**Status:** Not Started

### User Profiles

- [ ] **Profile Management** (1 week)
  - [ ] Profile screen (view own + others)
  - [ ] Avatar upload to Supabase Storage
  - [ ] Display name edit
  - [ ] Bio/description field
  - [ ] Achievement collection display
  - [ ] Trip history preview
  - [ ] Privacy settings

- [ ] **Avatar System** (3 days)
  - [ ] Image picker (camera + gallery)
  - [ ] Resize to 1024x1024 before upload
  - [ ] Upload to `avatars/{user_id}/avatar.jpg`
  - [ ] Supabase auto-resize (256x256, 512x512)
  - [ ] Cache locally
  - [ ] Default avatar generation (initials)

### Following System

- [ ] **Follow Mechanics** (1 week)
  - [ ] Send follow request (local instance only in Phase 4)
  - [ ] Approve/reject request UI
  - [ ] Unfollow action
  - [ ] Follower/following lists
  - [ ] Follow notifications
  - [ ] Block user

### Reactions & Comments

- [ ] **Reactions System** (3 days)
  - [ ] 6 emoji reactions (🔥 ❤️ 👍 😮 🎉 💯)
  - [ ] Add/remove reaction
  - [ ] Reaction count aggregation
  - [ ] Reaction list (who reacted)
  - [ ] Real-time reaction updates

- [ ] **Comments System** (1 week)
  - [ ] Add comment to trip
  - [ ] Threaded replies
  - [ ] Markdown support (bold, italic, links)
  - [ ] Edit/delete own comments
  - [ ] Comment notifications
  - [ ] Moderation (trip owner can delete)

### Discovery Feed

- [ ] **Public Discovery Feed** (1 week)
  - [ ] Opt-in chronological feed (no algorithm)
  - [ ] Show public trips from followed users
  - [ ] Respect visibility settings
  - [ ] Pull-to-refresh
  - [ ] Pagination (20 trips per page)
  - [ ] Cache for offline viewing

---

## Phase 5: Federation (0% Complete)

**Timeline:** Months 8-9  
**Status:** Not Started

### Discovery Service

- [ ] **Central Discovery Service** (2 weeks)
  - [ ] Supabase Edge Function: `/api/instance?domain=X`
  - [ ] Instance config response (URL, anon key, features)
  - [ ] Rate limiting (100 req/hour per IP)
  - [ ] Instance registration endpoint
  - [ ] Email verification for self-hosters
  - [ ] Instance blocklist/allowlist
  - [ ] Deploy to production

- [ ] **Instance Registry** (1 week)
  - [ ] SQLite `instances` table
  - [ ] Local instance cache
  - [ ] Discovery service integration
  - [ ] Fallback to hardcoded configs
  - [ ] Manual instance addition UI

### Multi-Instance Manager

- [ ] **Dynamic Supabase Client** (1 week)
  - [ ] `SupabaseClientManager` in shared Kotlin
  - [ ] Client creation per instance
  - [ ] Client caching (reuse connections)
  - [ ] Switch between instances
  - [ ] Handle instance offline state

- [ ] **Instance Management UI** (1 week)
  - [ ] Add instance screen (handle entry)
  - [ ] Instance list (home + federated)
  - [ ] Switch active instance
  - [ ] Remove instance
  - [ ] Instance status indicators (online/offline)

### Federation Protocol

- [ ] **Cross-Instance Communication** (2 weeks)
  - [ ] HTTP signatures for security
  - [ ] Inbox/outbox pattern implementation
  - [ ] ActivityPub-inspired protocol
  - [ ] Public/private key generation
  - [ ] Message signing/verification
  - [ ] Retry logic with exponential backoff

- [ ] **Federated Follow** (1 week)
  - [ ] Send follow request to remote instance
  - [ ] Receive remote follow requests
  - [ ] Cross-instance follow approval
  - [ ] Federated user cache
  - [ ] Handle instance domain changes

- [ ] **Federated Reactions & Comments** (1 week)
  - [ ] Send reactions to remote instances
  - [ ] Receive remote reactions
  - [ ] Sync comments across instances
  - [ ] Handle deleted federated content
  - [ ] Cache for offline viewing

---

## Phase 6: Self-Hosting & Polish (0% Complete)

**Timeline:** Month 10  
**Status:** Not Started

### Self-Hosting

- [ ] **Docker Compose Setup** (1 week)
  - [ ] Dockerfile for Supabase
  - [ ] Docker Compose configuration
  - [ ] Environment variable template
  - [ ] Database initialization script
  - [ ] Nginx reverse proxy config
  - [ ] SSL/TLS setup (Let's Encrypt)

- [ ] **Self-Hosting Documentation** (1 week)
  - [ ] Installation guide
  - [ ] System requirements
  - [ ] Domain setup instructions
  - [ ] Backup/restore guide
  - [ ] Troubleshooting section
  - [ ] Federation setup guide
  - [ ] Instance registration process

### Bug Reporting

- [ ] **GitHub Integration** (3 days)
  - [ ] In-app bug report form
  - [ ] Screenshot attachment
  - [ ] Auto-collect device info (with consent)
  - [ ] Last 50 log lines (sanitized)
  - [ ] GitHub API integration
  - [ ] Create issue with template
  - [ ] Auto-apply labels (bug, android/ios, needs-triage)

### Crash Reporting

- [ ] **Crashlytics Integration** (3 days)
  - [ ] Firebase Crashlytics (Android)
  - [ ] Sentry (iOS)
  - [ ] Capture non-PII metadata only
  - [ ] User opt-out setting
  - [ ] Crash dashboard setup
  - [ ] Alert on critical crashes

### Testing & QA

- [ ] **Beta Testing Program** (2 weeks)
  - [ ] TestFlight setup (iOS)
  - [ ] Google Play Internal Testing (Android)
  - [ ] Recruit 50-100 beta testers
  - [ ] Feedback collection form
  - [ ] Bug triage process
  - [ ] Weekly beta updates

- [ ] **Performance Testing** (1 week)
  - [ ] Battery drain testing (24-hour sessions)
  - [ ] Location accuracy testing
  - [ ] Network failure recovery
  - [ ] Offline mode testing
  - [ ] Real-time latency measurement
  - [ ] Map rendering performance

### App Store Preparation

- [ ] **App Store Submission** (1 week)
  - [ ] App Store screenshots (iOS)
  - [ ] Google Play screenshots (Android)
  - [ ] App description copy
  - [ ] Privacy policy
  - [ ] Terms of service
  - [ ] Location usage justification
  - [ ] Submit for review

- [ ] **Marketing Materials** (3 days)
  - [ ] Landing page
  - [ ] Demo video
  - [ ] GitHub README
  - [ ] Social media assets
  - [ ] Press kit

---

## Additional Tasks (Cross-Cutting)

### Security

- [ ] **Security Hardening** (ongoing)
  - [ ] RLS policy audit
  - [ ] API rate limiting
  - [ ] SQL injection prevention
  - [ ] XSS protection
  - [ ] HTTPS enforcement
  - [ ] Secrets management (no hardcoded keys)
  - [ ] Third-party security audit

### Performance

- [ ] **Optimization** (ongoing)
  - [ ] Database query optimization
  - [ ] Index analysis
  - [ ] Image compression
  - [ ] API response caching
  - [ ] Bundle size reduction
  - [ ] Lazy loading implementation

### Documentation

- [ ] **User Documentation** (Month 10)
  - [ ] Getting started guide
  - [ ] Feature tutorials
  - [ ] FAQ
  - [ ] Privacy guide
  - [ ] Self-hosting guide

- [ ] **Developer Documentation** (ongoing)
  - [ ] Architecture guide
  - [ ] Contributing guide
  - [ ] Code style guide
  - [ ] API documentation
  - [ ] Testing guide

---

## Summary Statistics

| Phase | Tasks | Status | Timeline |
|-------|-------|--------|----------|
| Phase 1 | 4 done, 3 remaining | 60% | Months 1-2 |
| Phase 2 | 0 done, ~20 tasks | 0% | Month 3 |
| Phase 3 | 0 done, ~15 tasks | 0% | Months 4-5 |
| Phase 4 | 0 done, ~12 tasks | 0% | Months 6-7 |
| Phase 5 | 0 done, ~10 tasks | 0% | Months 8-9 |
| Phase 6 | 0 done, ~15 tasks | 0% | Month 10 |

**Total Estimated Tasks:** ~90 major tasks  
**Current Progress:** 4/90 tasks (4.4% overall)  
**Phase 1 Progress:** 4/7 tasks (57% of Phase 1)

---

**Last Updated:** 2026-04-13  
**Next Review:** After Phase 1 completion
