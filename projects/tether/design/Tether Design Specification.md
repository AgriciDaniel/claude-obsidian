# Tether Design Specification

**Date:** 2026-04-13  
**Project:** Tether - Open-source Life360 Alternative  
**Version:** 1.0  

---

## Executive Summary

Tether is an open-source family location tracking application with social travel features. Built with Kotlin Multiplatform Mobile, it supports Android and iOS while sharing business logic. The app uses Supabase for backend services and implements a federated architecture for scalability and self-hosting.

**Core Features:**
- Real-time family location tracking via circles
- User-configurable location update frequencies
- Route tracking with 30-day history retention
- Travel Stories with achievements (Strava-inspired, exploration-focused)
- Lite social features with federated multi-instance architecture
- Privacy-first design with granular controls
- iOS Liquid Glass and Material Design themes
- Performance mode for battery optimization

---

## Architecture Overview

### Tech Stack

**Mobile:**
- Kotlin Multiplatform Mobile (KMM) for shared business logic
- Android UI: Jetpack Compose
- iOS UI: SwiftUI (called from Kotlin via expect/actual)
- Mapbox SDK for maps (both platforms)
- Platform-native location services (Android Location Services, iOS CoreLocation)

**Backend:**
- Supabase (PostgreSQL database, Auth, Realtime subscriptions, Storage)
- Edge Functions for notifications and background jobs
- Row-Level Security (RLS) for privacy enforcement

**Federation:**
- Hybrid federation model (users have home instance)
- ActivityPub-inspired protocol for cross-instance communication
- Lightweight discovery service for handle routing
- Official "Tether Cloud" instances + self-hosting support

### Architectural Layers

1. **Shared Kotlin Module**
   - Business logic (location processing, achievements, sync)
   - API clients (Supabase, GitHub, federation protocol)
   - Data models and validation
   - Offline queue management

2. **Platform-Specific UI**
   - Native Android (Jetpack Compose) and iOS (SwiftUI)
   - Platform-specific location service wrappers
   - Theme rendering (Liquid Glass and Material Design)
   - Push notification handling (FCM and APNs)

3. **Backend Services**
   - Supabase PostgreSQL for persistent data
   - Realtime subscriptions for live location updates
   - Storage buckets for user avatars
   - Edge Functions for notifications and federation

4. **Local Storage**
   - SQLite cache for offline support
   - 30-day rolling window of location history
   - Sync queue for pending writes

---

## User Experience

### Design System

**Theme Options:**

1. **iOS Liquid Glass (Default)**
   - Frosted glass blur effects
   - Translucent backgrounds with depth
   - Elevation via blur intensity
   - Spring-based animations

2. **Material Design**
   - Android Material 3 design language
   - Dynamic color support
   - Elevation shadows
   - Standard Material motion

**Animation Modes:**

- **Standard Mode:** Smooth spring animations, blur transitions, 60fps target
- **Performance Mode:** No animations, instant state changes, reduced visual effects
  - Auto-enabled at <20% battery
  - Suggested at <30% battery (user prompt)
  - Manual toggle in settings

**Visual Hierarchy:**
- Map as primary canvas (Mapbox)
- Blur-based cards floating over map (Liquid Glass)
- Solid surface cards (Material)
- Translucent bottom sheets
- Frosted navigation bars

### User Relationship Model

**Family Circles:**
- Users create or join family groups via invite codes
- Each user can be in one primary circle
- All circle members see each other's real-time locations
- Circle admin can remove members
- Leaving a circle revokes access immediately

**Location Update Frequencies (User-Configurable):**

| Mode | Interval | Use Case |
|------|----------|----------|
| Realtime | 5 seconds | "I want live tracking" |
| Frequent | 30 seconds | Active travel monitoring |
| Normal | 2 minutes | Balanced (default) |
| Relaxed | 5 minutes | Battery-friendly |

**Smart Optimizations:**
- Geofencing: Pause updates when stationary at saved places (>10 min)
- Speed-based intervals: Increase frequency by 2x when traveling >50mph
- Battery awareness: Drop to lower frequency if <20% battery

### Notification System

**Notification Types (All User-Configurable):**

✅ **Arrival Alerts** - Member arrives at saved place  
✅ **Departure Alerts** - Member leaves saved place  
✅ **Speed Alerts** - Member exceeds threshold (70/80/90 mph configurable)  
✅ **Low Battery Alerts** - Member's battery <15%  
✅ **Social Notifications** - Reactions, comments, follows  
✅ **Achievement Notifications** - Own + circle member unlocks  

**Delivery Strategy:**
- Critical alerts (speed, emergency): Immediate push
- Social notifications: Batched every 15 minutes
- Achievement unlocks: Immediate but can be snoozed

**Quiet Hours:**
- Optional "Do Not Disturb" schedule (e.g., 10pm - 7am)
- Emergency alerts can override (configurable)

**Granular Control:**
- Toggle each notification type per circle
- Different settings for different circles
- Per-metric opt-out for leaderboards

---

## Data Models

### Supabase PostgreSQL Schema

#### Core Tables

**users**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  avatar_url TEXT,
  location_update_frequency TEXT DEFAULT 'normal_2m',
    -- Options: realtime_5s, frequent_30s, normal_2m, relaxed_5m
  performance_mode BOOLEAN DEFAULT false,
  theme TEXT DEFAULT 'liquid_glass',
    -- Options: liquid_glass, material
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**circles**
```sql
CREATE TABLE circles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
  invite_code TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**circle_members**
```sql
CREATE TABLE circle_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  circle_id UUID REFERENCES circles(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'member',
    -- Options: admin, member
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(circle_id, user_id)
);
```

**locations**
```sql
CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  accuracy FLOAT NOT NULL, -- meters
  speed FLOAT, -- m/s
  heading FLOAT, -- degrees
  battery_level INT, -- 0-100
  timestamp TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_locations_user_timestamp ON locations(user_id, timestamp DESC);

-- Auto-delete locations older than 30 days
CREATE OR REPLACE FUNCTION delete_old_locations()
RETURNS void AS $$
BEGIN
  DELETE FROM locations WHERE timestamp < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule via pg_cron
SELECT cron.schedule('delete-old-locations', '0 2 * * *', 'SELECT delete_old_locations()');
```

**places** (Saved locations like "Home", "Work")
```sql
CREATE TABLE places (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  radius FLOAT NOT NULL, -- geofence radius in meters
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**notification_preferences**
```sql
CREATE TABLE notification_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  circle_id UUID REFERENCES circles(id) ON DELETE CASCADE,
  arrival_alerts BOOLEAN DEFAULT true,
  departure_alerts BOOLEAN DEFAULT true,
  speed_alerts BOOLEAN DEFAULT true,
  speed_threshold INT DEFAULT 80, -- mph
  low_battery_alerts BOOLEAN DEFAULT true,
  social_notifications BOOLEAN DEFAULT true,
  achievement_notifications BOOLEAN DEFAULT true,
  UNIQUE(user_id, circle_id)
);
```

#### Travel Stories & Achievements

**trips**
```sql
CREATE TABLE trips (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ,
  distance_km FLOAT,
  max_speed_kmh FLOAT,
  avg_speed_kmh FLOAT,
  route_polyline TEXT, -- Encoded polyline for map rendering
  visibility TEXT DEFAULT 'circle',
    -- Options: circle, followers, public, unlisted
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trips_user_time ON trips(user_id, start_time DESC);
```

**achievements**
```sql
CREATE TABLE achievements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code TEXT UNIQUE NOT NULL, -- e.g., 'road_warrior_1000km'
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  icon_url TEXT,
  category TEXT NOT NULL,
    -- Options: distance, exploration, reliability, social
  threshold_value FLOAT, -- e.g., 1000 for 1000km
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed achievements
INSERT INTO achievements (code, name, description, category, threshold_value) VALUES
  ('road_warrior_1000', 'Road Warrior', 'Travel 1000 km', 'distance', 1000),
  ('explorer_25', 'Explorer', 'Visit 25 unique locations', 'exploration', 25),
  ('commute_master_50', 'Commute Master', 'Same route 50 times', 'reliability', 50),
  ('reliable_10', 'Reliable', 'On-time arrivals for 10 days', 'reliability', 10),
  ('adventure_squad', 'Adventure Squad', 'Family travels together', 'social', 1);
```

**user_achievements**
```sql
CREATE TABLE user_achievements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  achievement_id UUID REFERENCES achievements(id) ON DELETE CASCADE,
  unlocked_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, achievement_id)
);
```

**trip_photos**
```sql
CREATE TABLE trip_photos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
  photo_url TEXT NOT NULL, -- Supabase Storage URL
  caption TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Social Features

**follows**
```sql
CREATE TABLE follows (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
  followee_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'pending',
    -- Options: pending, accepted, rejected
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(follower_id, followee_id)
);
```

**reactions**
```sql
CREATE TABLE reactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  emoji TEXT NOT NULL,
    -- Options: 🔥 ❤️ 👍 😮 🎉 💯
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(trip_id, user_id, emoji)
);
```

**comments**
```sql
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  parent_comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comments_trip ON comments(trip_id, created_at DESC);
```

#### Federation Tables

**federated_instances**
```sql
CREATE TABLE federated_instances (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain TEXT UNIQUE NOT NULL, -- e.g., 'instance-a.tether.app'
  public_key TEXT NOT NULL, -- For HTTP signature verification
  status TEXT DEFAULT 'active',
    -- Options: active, blocked, suspended
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**federated_users**
```sql
CREATE TABLE federated_users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  local_id UUID UNIQUE, -- NULL if remote user
  handle TEXT UNIQUE NOT NULL, -- e.g., 'alice@instance-a.tether.app'
  instance_id UUID REFERENCES federated_instances(id),
  display_name TEXT,
  avatar_url TEXT,
  last_synced_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**outbox** (Outgoing federated activities)
```sql
CREATE TABLE outbox (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  activity_type TEXT NOT NULL,
    -- Options: follow, like, comment, share
  payload JSONB NOT NULL,
  target_instance_id UUID REFERENCES federated_instances(id),
  status TEXT DEFAULT 'pending',
    -- Options: pending, sent, failed
  retry_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**inbox** (Incoming federated activities)
```sql
CREATE TABLE inbox (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  activity_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  source_instance_id UUID REFERENCES federated_instances(id),
  processed BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Supabase Storage

**Buckets:**

1. **avatars** (public)
   - Path: `{user_id}/avatar.{jpg|png|webp}`
   - Max size: 5MB
   - Allowed formats: JPEG, PNG, WebP
   - Auto-resize: 256x256, 512x512

2. **trip-photos** (public with RLS)
   - Path: `{user_id}/{trip_id}/{photo_id}.{jpg|png|webp}`
   - Max size: 10MB per photo
   - Allowed formats: JPEG, PNG, WebP
   - Respect trip visibility settings

**Storage Policies:**
- Users can only upload to their own folders
- Read access based on circle membership and trip visibility
- Auto-delete photos when trip is deleted

### Local SQLite Cache

**Tables (Mirror Supabase):**
- `locations_cache` - 30-day rolling window
- `trips_cache` - User's own trips
- `sync_queue` - Pending writes (locations, reactions, comments)
- `offline_metadata` - Last sync timestamp per table

**Sync Strategy:**
- Write to SQLite first (offline-first)
- Background worker syncs to Supabase when online
- UI reads from SQLite, not Supabase directly
- Optimistic UI updates

---

## Location Tracking Implementation

### Platform-Specific Layer

**Android (FusedLocationProvider):**
- Request fine + background location permissions
- Foreground service for continuous tracking
- WorkManager for periodic updates when backgrounded
- Battery optimization exemption prompt

**iOS (CoreLocation):**
- Request "Always Allow" location permission
- Significant location change monitoring
- Background location updates capability
- Deferred updates when precision not critical

### Shared Kotlin Logic

**Update Frequency Enum:**
```kotlin
enum class UpdateFrequency(val intervalMs: Long) {
    REALTIME_5S(5_000),
    FREQUENT_30S(30_000),
    NORMAL_2M(120_000),
    RELAXED_5M(300_000)
}
```

**Location Processing Pipeline:**

1. Native platform captures location update
2. Shared Kotlin validates (accuracy >100m = skip)
3. Calculate derived metrics:
   - Speed (from displacement / time delta)
   - Distance from last point (Haversine formula)
   - Heading (bearing between points)
4. Batch if offline, send immediately if online
5. Update Supabase `locations` table
6. Broadcast via Supabase Realtime to circle members
7. Cache locally in SQLite

**Smart Optimizations:**

- **Geofencing:** Pause updates when stationary at saved place for >10 minutes
- **Speed-based intervals:** If speed >50mph, increase frequency by 2x temporarily
- **Battery awareness:** Drop to lower frequency if <20% battery
- **Accuracy filtering:** Discard locations with accuracy >100m

### Realtime Subscriptions

**Client Side:**
```kotlin
// Subscribe to circle members' locations
supabase.realtime
    .channel("locations")
    .on<LocationUpdate>(
        event = PostgresAction.INSERT,
        filter = "user_id=in.(${circleMemberIds.joinToString()})"
    ) { update ->
        // Update map markers in real-time
        updateMapMarker(update.userId, update.latitude, update.longitude)
    }
    .subscribe()
```

---

## Travel Stories & Achievements

### Trip Recording

**Automatic Trip Detection:**
- Start trip when speed >5mph for >30 seconds
- End trip when stationary (<5mph) for >5 minutes
- Calculate metrics:
  - Total distance (sum of Haversine distances)
  - Max speed (highest recorded speed)
  - Avg speed (total distance / duration)
  - Route polyline (Google Polyline Algorithm)

**Manual Trip Controls:**
- "Start Trip" button (force-start recording)
- "End Trip" button (force-stop)
- "Discard Trip" (delete without saving)

### Achievements System

**Achievement Categories:**

1. **Distance** - Total kilometers traveled
   - Road Warrior (1000 km)
   - Globe Trotter (5000 km)
   - Wanderer (10000 km)

2. **Exploration** - Unique locations visited
   - Explorer (25 unique places)
   - Adventurer (100 unique places)
   - Nomad (500 unique places)

3. **Reliability** - On-time arrivals
   - Reliable (10 consecutive on-time arrivals)
   - Punctual (50 consecutive on-time arrivals)
   - Timekeeper (100 consecutive on-time arrivals)

4. **Social** - Family interactions
   - Adventure Squad (family travels together 5 times)
   - Travel Buddy (give 100 reactions to family trips)
   - Storyteller (share 50 trips with circle)

**Unlock Logic:**
- Background job runs hourly to check thresholds
- Push notification on unlock
- Badge displayed on user profile
- Circle members notified (if user allows)

### Trip Sharing

**Visibility Levels:**
- **Circle Only** (default) - Only family circle members
- **Followers** - Circle + approved followers
- **Public** - Discoverable in public feed
- **Unlisted** - Only accessible via direct link

**Trip Story Components:**
- Route visualization on map
- Start/end time and duration
- Distance and speeds (max/avg)
- Achievements unlocked during trip
- Photos with captions (optional)
- Comments and reactions from viewers

---

## Social Features (Federated)

### Federation Architecture

**Home Instance Model:**
- Each user has a "home instance" (e.g., `alice@instance-a.tether.app`)
- Official "Tether Cloud" instances for easy signup
- Self-hosting option (Docker Compose + Supabase)
- Lightweight discovery service routes messages between instances

**Cross-Instance Communication:**
- HTTP-based federation protocol (ActivityPub-inspired)
- HTTP signatures for security (public/private key pairs)
- Inbox/outbox pattern (like email)
- Retry logic with exponential backoff
- Eventual consistency model

### Social Interactions

**Following:**
- Send follow request to user on different instance
- Home instance receives request, notifies user
- User approves/rejects
- Bi-directional following not required

**Reactions:**
- Six emoji types: 🔥 ❤️ 👍 😮 🎉 💯
- Federated reactions sent to trip owner's home instance
- Aggregated count displayed on trip
- Real-time updates via Realtime subscriptions

**Comments:**
- Threaded comments on trips
- Markdown support (bold, italic, links)
- Federated comments synced to home instance
- Moderation by trip owner (delete, block user)

**Public Discovery Feed:**
- Opt-in chronological feed (no algorithm)
- Shows public trips from followed users
- Respects visibility settings
- Cached locally for offline viewing

### Privacy Controls

**Default Settings:**
- New trips: Circle-only visibility
- New achievements: Share with circle
- Profile: Visible to circle + followers only

**Granular Controls:**
- Per-trip visibility override
- Block users (local + federated)
- Allowlist/blocklist instances (self-hosters)
- Opt-out of public discovery feed
- Delete all federated data (GDPR compliance)

---

## Error Handling & Offline Support

### Offline-First Architecture

**Local-First Data Flow:**
1. All writes go to local SQLite first
2. Background sync worker pushes to Supabase when online
3. UI reads from local cache, not directly from Supabase
4. Optimistic UI updates (show changes immediately)

**Conflict Resolution:**
- Location updates: Last-write-wins (timestamp-based)
- Profile changes: Server-side validation, retry on conflict
- Social interactions: Idempotent IDs prevent duplicates

### Error Scenarios & User-Friendly Messages

| Technical Error | User Sees |
|----------------|-----------|
| `401 Unauthorized` | "Session expired. Please sign in again" |
| `403 Forbidden` | "You're no longer part of this circle. Contact the circle admin." |
| `429 Rate Limited` | "Too many requests. Waiting 30 seconds..." |
| `500 Server Error` | "Our servers are having trouble. Retrying..." |
| `Network timeout` | "Can't reach the server. Check your internet connection." |
| `GPS_PERMISSION_DENIED` | "Location access required. Tap to open settings." |
| `LOCATION_DISABLED` | "Turn on location services to see family members." |
| `BATTERY_OPTIMIZATION_ON` | "For reliable tracking, disable battery optimization for Tether." |

**Error Dialog Structure:**
```
[Icon: 🔄/⚠️/❌]
[Clear Title: "Can't Update Location"]
[Simple Explanation: "Your device's location services are turned off"]
[Action Button: "Open Settings"] [Dismiss: "Not Now"]
```

### Automatic Performance Optimizations

**Battery-Based Triggers:**
- **<30% battery:** Prompt user to enable performance mode
- **<20% battery:** Auto-enable performance mode + toast notification
- **<15% battery:** Performance mode + reduce location frequency by one tier

**Performance Mode Effects:**
- Disable all animations
- Reduce map rendering quality
- Pause non-critical background syncs
- Lower location update frequency
- User can override in settings

### Network Error Handling

**Retry Strategy:**
- Exponential backoff: 1s → 2s → 4s → 8s → 30s max
- Queue writes locally with retry counter
- UI shows "syncing" indicator when queue >0 items
- Manual "retry sync" button if auto-retry exhausted

**API Error Handling:**
- 401: Force re-login flow
- 403: Show context-specific message (removed from circle, etc.)
- 429: Exponential backoff, reduce update frequency temporarily
- 500: Retry 3x, then show user-friendly error

### Location Issues

**GPS Accuracy:**
- Filter out locations with accuracy >100m
- Show accuracy circle around map marker
- Alert user if GPS hasn't fixed in 5 minutes

**Permission Denied:**
- Graceful degradation: Show last known location with staleness indicator
- Persistent banner: "Location access required for real-time tracking"
- Deep link to system settings

---

## Bug Reporting (GitHub Integration)

### In-App Bug Reporter

**Report Flow:**
1. User taps "Report a Problem" in settings
2. Form collects:
   - What were you trying to do? (text field)
   - What happened instead? (text field)
   - Optional: Attach screenshot
3. Auto-attached (user can review/remove):
   - App version
   - OS version
   - Device model
   - Last 50 non-PII log lines (requires consent)
4. "Submit Report" creates GitHub issue via GitHub API

**GitHub Issue Template:**
```markdown
## Bug Description
[User's description of what they were trying to do]

## Expected Behavior
[What the user expected to happen]

## Actual Behavior
[What actually happened]

## Device Info
- App Version: 1.2.3
- OS: Android 14 / iOS 17.2
- Device: Pixel 8 / iPhone 15 Pro

## Logs
[Last 50 log lines, sanitized]

## Screenshot
[If provided]

---
*Reported via in-app bug reporter*
```

**Auto-Applied Labels:**
- `bug` (all reports)
- `android` / `ios` (based on platform)
- `needs-triage` (maintainers remove after review)

**Privacy Safeguards:**
- User sees preview before submission
- No location data in logs
- No circle names or personal info
- User must consent to attach logs/screenshots
- GitHub issue link shown after creation: "Track your report: #123"

---

## Testing Strategy

### Test Pyramid

**1. Unit Tests (60% coverage target)**
- Location processing logic (distance, speed calculation)
- API client request/response parsing
- Achievement unlock conditions
- Notification preference logic
- Offline sync queue management
- Run via Kotlin Test on CI/CD

**2. Integration Tests (20% coverage)**
- Supabase API interactions (Wiremock mocks)
- SQLite cache sync flows
- Realtime subscription handling
- Authentication flows
- GitHub issue creation API
- Federation protocol (cross-instance follow)

**3. UI Tests (10% coverage)**
- Android: Espresso for critical flows
  - Login flow
  - Create/join circle
  - View map with live locations
- iOS: XCUITest for critical flows
- Focus on happy paths only

**4. Manual Testing (10%)**
- Cross-device testing (Android 10+, iOS 15+)
- Battery drain testing (24-hour tracking session)
- Offline → online transition edge cases
- Push notification delivery reliability

### Critical Test Scenarios

✅ **Location Tracking:**
- Verify location updates respect user's frequency setting
- Test geofence enter/exit detection accuracy
- Validate 30-day auto-deletion (run scheduled job manually)
- Offline queue batches and syncs when online

✅ **Privacy & Permissions:**
- User A cannot see User B's location unless in same circle
- Removed circle member loses access immediately
- Supabase RLS policies block unauthorized queries

✅ **Performance:**
- App uses <5% battery per hour in "Normal" mode
- Map renders 60fps with 10 circle members updating simultaneously
- Performance mode disables animations correctly
- Auto-enable performance mode at 20% battery

✅ **Social Features:**
- Federated follow request across instances
- Reactions sync within 5 seconds
- Comments thread correctly
- Visibility levels respected (circle vs followers vs public)

✅ **Error Handling:**
- Offline mode shows cached data correctly
- User-friendly error messages display (not technical codes)
- Bug report creates GitHub issue with correct metadata

### CI/CD Pipeline

**GitHub Actions:**
- Run on every PR
- Execute unit + integration tests
- Build Android APK + iOS IPA
- Generate automated screenshots for stores
- Deploy Supabase migrations to staging environment
- Run security scans (dependency vulnerabilities)

**Beta Testing:**
- TestFlight (iOS) + Google Play Internal Testing (Android)
- 50-100 beta testers before public launch
- Collect Crashlytics data + user feedback
- Iterate on battery/performance issues
- Monitor real-world location accuracy

---

## Implementation Phases

### Phase 1: Core Location Tracking (Months 1-2)
- Kotlin Multiplatform project setup
- Supabase auth integration
- Basic location tracking (Android + iOS)
- Family circles (create, join, leave)
- Real-time map with live locations
- SQLite offline cache
- Basic error handling

### Phase 2: UI/UX Polish (Month 3)
- Liquid Glass theme implementation
- Material Design theme implementation
- Theme toggle + persistence
- Performance mode (auto-enable on low battery)
- Notification system (arrival/departure/speed/battery)
- User-configurable location frequencies
- Saved places (Home, Work, etc.)

### Phase 3: Travel Stories (Months 4-5)
- Automatic trip detection
- Route visualization on map
- Trip metrics (distance, speed, duration)
- Achievement system with unlocks
- Trip sharing (circle-only visibility)
- Photo uploads to trips
- Leaderboards (circle-only, opt-in)

### Phase 4: Social Features (Months 6-7)
- User profiles with avatars
- Follow system (local instance only)
- Reactions on trips (6 emoji types)
- Threaded comments
- Public discovery feed (opt-in)
- Visibility controls (circle/followers/public/unlisted)

### Phase 5: Federation (Months 8-9)
- Federation protocol implementation
- Discovery service for handle routing
- Cross-instance follow requests
- Federated reactions and comments
- HTTP signature verification
- Instance allowlist/blocklist

### Phase 6: Self-Hosting & Polish (Month 10)
- Docker Compose setup
- Self-hosting documentation
- GitHub bug reporting integration
- Crashlytics/Sentry integration
- Beta testing program
- App Store/Play Store submission

---

## Success Metrics

### Engagement
- 70%+ weekly active users (open app 3+ times/week)
- 40%+ record at least one trip per week
- 60%+ unlock at least one achievement in first 30 days
- 20%+ share trips with circle members

### Performance
- <5% battery drain per hour (Normal mode)
- <3% battery drain per hour (Performance mode)
- 99%+ location update success rate
- <2 second map load time
- 60fps UI rendering (Standard mode)

### Retention
- Day-7 retention: 50%+
- Day-30 retention: 35%+
- Day-90 retention: 25%+

### Privacy & Safety
- Zero unauthorized location access incidents
- <1% user complaints about privacy
- 100% GDPR compliance audit
- User sentiment: "Privacy-first" messaging resonates

### Federation (Post-Launch)
- 5+ self-hosted instances in first 6 months
- 15%+ users on non-official instances
- <5 second cross-instance interaction latency

---

## Open Questions & Future Enhancements

### Open Questions
1. Should we support multiple circles per user in v2?
2. What's the optimal discovery service architecture (centralized vs decentralized)?
3. Should we implement end-to-end encryption for location data?
4. How do we handle abuse/spam in federated instances?

### Future Enhancements
- Android Auto / CarPlay integration
- Apple Watch / Wear OS companion apps
- Web dashboard (view-only map)
- Geofence automation (IFTTT-style: "When I arrive home, turn off notifications")
- Travel statistics/analytics (monthly summaries)
- Export data (CSV, GPX, KML)
- Voice commands ("Where is mom?")
- Offline maps (pre-download for offline viewing)

---

## Conclusion

Tether is designed as a privacy-first, open-source alternative to Life360 with unique social features inspired by Strava. The federated architecture ensures scalability beyond a single Supabase instance while supporting self-hosting for maximum user control.

Key differentiators:
- **Privacy by default** - Circle-only sharing, granular controls
- **No speed competitions** - Exploration and reliability over dangerous driving
- **Federated & self-hostable** - User data ownership
- **Battery-aware** - Automatic performance optimizations
- **User-friendly errors** - Non-technical messages with clear actions
- **Open-source** - Community-driven development

Next steps: Invoke `writing-plans` skill to create detailed implementation plan.
