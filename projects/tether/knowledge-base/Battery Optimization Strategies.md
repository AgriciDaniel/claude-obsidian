---
tags: [knowledge, mobile, location, battery, optimization]
type: knowledge
category: best-practices
difficulty: intermediate
status: complete
created: 2026-04-13
updated: 2026-04-13
---

# Battery Optimization Strategies for Location Tracking

## Overview

Location tracking is one of the most battery-intensive operations on mobile devices. This guide covers proven strategies to minimize battery drain while maintaining tracking accuracy.

---

## Key Principles

1. **Use the minimum accuracy required** - GPS is expensive, WiFi/cell tower is cheap
2. **Increase update intervals when possible** - 5s vs 5min = massive battery difference
3. **Pause when stationary** - No need to track when user hasn't moved
4. **Leverage OS optimizations** - Deferred updates, significant changes
5. **Monitor battery level** - Reduce tracking when low

---

## Strategy 1: Adaptive Accuracy

**Concept:** Reduce GPS accuracy when high precision isn't needed.

### Android Implementation
```kotlin
val locationRequest = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, intervalMs)
    .setMinUpdateIntervalMillis(intervalMs)
    .build()

// Switch to balanced mode when battery < 20%
if (batteryLevel < 20) {
    locationRequest.priority = Priority.PRIORITY_BALANCED_POWER_ACCURACY
}
```

**Battery Impact:**
- High accuracy: ~5-8% battery/hour
- Balanced: ~2-4% battery/hour
- Low power: ~1-2% battery/hour

---

## Strategy 2: Distance Filters

**Concept:** Only update when user moves X meters, ignore small movements.

### iOS Implementation
```swift
locationManager.distanceFilter = 10 // meters
// Only get updates when user moves 10m
```

### Android Implementation
```kotlin
locationRequest.setSmallestDisplacement(10f) // meters
```

**Battery Impact:** 30-50% reduction for stationary users

---

## Strategy 3: Geofencing for Known Locations

**Concept:** Pause updates when user is at home/work for extended time.

### Algorithm
```kotlin
fun shouldPauseTracking(
    currentLocation: Location,
    knownPlaces: List<Place>,
    stationaryThreshold: Duration = 10.minutes
): Boolean {
    val nearbyPlace = knownPlaces.find { place ->
        currentLocation.distanceTo(place.location) < place.radius
    }
    
    return nearbyPlace != null && 
           timeSinceLastMovement() > stationaryThreshold
}
```

**Battery Impact:** 70-90% reduction when stationary at saved places

---

## Strategy 4: Speed-Based Intervals

**Concept:** Update more frequently when traveling fast (driving), less when walking/stationary.

### Tether Implementation
```kotlin
enum class UpdateFrequency(val baseInterval: Long) {
    REALTIME_5S(5_000),
    FREQUENT_30S(30_000),
    NORMAL_2M(120_000),
    RELAXED_5M(300_000);
    
    fun adjustedInterval(currentSpeed: Float): Long {
        return when {
            currentSpeed > 50f -> baseInterval / 2 // Driving: 2x frequency
            currentSpeed < 1f -> baseInterval * 2  // Stationary: 0.5x frequency
            else -> baseInterval
        }
    }
}
```

**Battery Impact:** 20-40% reduction for mixed travel

---

## Strategy 5: Deferred Updates (iOS)

**Concept:** Batch location updates when precision isn't time-critical.

### iOS Implementation
```swift
// Allow updates to be deferred up to 500m or 2 minutes
locationManager.allowDeferredLocationUpdates(
    untilTraveled: 500, // meters
    timeout: 120        // seconds
)
```

**How it works:**
- iOS batches location fixes in hardware
- Delivers them in one burst
- Reduces CPU wake-ups by 60-80%

**Battery Impact:** 40-60% reduction for highway driving

---

## Strategy 6: Significant Location Changes (iOS)

**Concept:** Use cell tower changes instead of GPS for coarse tracking.

### iOS Implementation
```swift
// Only updates when user changes cell towers (~500m-2km)
locationManager.startMonitoringSignificantLocationChanges()
```

**Battery Impact:** 90-95% reduction vs continuous GPS

**Use Case:** Background tracking when app is killed

---

## Strategy 7: Activity Type Optimization

**Concept:** Tell OS what user is doing (driving, walking, fitness).

### iOS Implementation
```swift
locationManager.activityType = .automotiveNavigation
// Optimizes for car travel (prioritizes roads)
```

### Android Implementation
```kotlin
DetectedActivity.IN_VEHICLE // Use for automotive tracking
DetectedActivity.ON_FOOT     // Use for walking tracking
```

**Battery Impact:** 10-20% reduction via OS optimizations

---

## Strategy 8: Background vs Foreground Modes

**Concept:** Different tracking strategies based on app state.

### Tether Implementation
```kotlin
sealed class TrackingMode {
    object Foreground : TrackingMode() {
        override val interval = 30_000L // 30s
        override val priority = Priority.PRIORITY_HIGH_ACCURACY
    }
    
    object Background : TrackingMode() {
        override val interval = 300_000L // 5min
        override val priority = Priority.PRIORITY_BALANCED_POWER_ACCURACY
    }
    
    object Killed : TrackingMode() {
        // Use significant location changes only
    }
}
```

**Battery Impact:** 50-70% reduction in background

---

## Strategy 9: Performance Mode (User-Triggered)

**Concept:** Let users manually reduce tracking when battery is low.

### Tether Implementation
```kotlin
when (performanceMode) {
    true -> {
        // Disable animations
        // Use low-power location priority
        // Increase update interval by 2x
        // Reduce map rendering quality
    }
    false -> {
        // Normal tracking
    }
}

// Auto-enable at 20% battery
if (batteryLevel <= 20 && !performanceMode) {
    enablePerformanceMode()
    notifyUser("Performance mode enabled to save battery")
}
```

**Battery Impact:** 40-60% reduction in performance mode

---

## Combined Strategy: Tether's Approach

**Adaptive Multi-Strategy System:**

1. **User sets base frequency** (5s, 30s, 2m, 5m)
2. **Speed adjustment** (2x faster when driving)
3. **Geofence pausing** (stop at home/work)
4. **Distance filtering** (ignore <10m movements)
5. **Battery-aware** (reduce at <30%, auto-performance at <20%)
6. **Background optimization** (5min intervals when backgrounded)

### Result
- **Normal usage:** ~2-3% battery/hour
- **Performance mode:** ~1-2% battery/hour
- **Stationary at home:** ~0.5% battery/hour
- **Active highway driving:** ~4-5% battery/hour

---

## Testing Battery Impact

### Android
```kotlin
// Use Battery Historian
adb bugreport > bugreport.zip
// Upload to: https://bathist.ef.lc/
```

### iOS
```swift
// Use Xcode Energy Log
// Instruments → Energy Log → Run for 30 min
```

### Real-World Testing
1. Full charge device
2. Run app for 24 hours
3. Measure battery drain
4. Target: <5% per hour in normal mode

---

## Common Mistakes

❌ **Arbitrary sleep() calls** - Use event-based waiting  
❌ **Always using high accuracy** - Use balanced when possible  
❌ **No distance filter** - Wastes battery on small movements  
❌ **Ignoring battery level** - Should reduce tracking when low  
❌ **Not pausing at known places** - Unnecessary tracking  
❌ **Foreground = background settings** - Background should be less frequent  

---

## Related Documentation

- [[Android Location Tracking]] - Tether's Android implementation
- [[iOS Location Tracking]] - Tether's iOS implementation
- [[Performance Mode]] - User-triggered battery optimization

---

## References

- [Android Location Best Practices](https://developer.android.com/training/location)
- [iOS CoreLocation Optimization](https://developer.apple.com/documentation/corelocation)
- [Battery Historian Tool](https://github.com/google/battery-historian)

---

**Category:** Best Practices  
**Difficulty:** Intermediate  
**Last Updated:** 2026-04-13
