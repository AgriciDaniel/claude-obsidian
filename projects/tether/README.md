---
banner: "![[tether-banner.png]]"
tags: [project, mobile, kotlin, location-tracking, open-source]
status: in-progress
phase: phase-1
progress: 60%
---

# Tether Project Hub

> Open-source family location tracking app with federated social features

## 📊 Project Status

**Current Phase:** Phase 1 - Core Location Tracking (60% complete)  
**Started:** 2026-04-13  
**Tech Stack:** Kotlin Multiplatform Mobile, Supabase, Mapbox

---

## 🗂️ Documentation Structure

### 📐 Design Documents
- [[Tether Design Specification]] - Complete design spec (main reference)
- [[Multi-Instance Configuration]] - Federated architecture & runtime discovery
- [[Database Schema]] - Supabase tables and relationships

### 🏗️ Implementation Guides
- [[KMM Project Setup]] - Kotlin Multiplatform setup
- [[Android Location Tracking]] - FusedLocationProvider implementation
- [[iOS Location Tracking]] - CoreLocation implementation
- [[Supabase Backend]] - Database migrations and Edge Functions

### 🧠 Knowledge Base
- [[Location Tracking Patterns]] - Best practices for mobile location
- [[Battery Optimization Strategies]] - Power management techniques
- [[Federated Social Architecture]] - Multi-instance communication
- [[Privacy & Security]] - RLS policies and data protection

### 📝 Meeting Notes
- [[2026-04-13 - Initial Brainstorming]] - Project kickoff and requirements

---

## 🎯 Quick Links

| Category | Link |
|----------|------|
| **Design Spec** | [[Tether Design Specification]] |
| **Current Work** | [[Phase 1 Progress]] |
| **Next Steps** | [[Phase 1 Remaining Tasks]] |
| **GitHub Repo** | `/home/maku/Documents/GitHub/HomeTether` |

---

## 📈 Progress Tracking

### Phase 1: Core Location Tracking (60% ✅)

- [x] Kotlin Multiplatform project setup
- [x] Supabase backend (17 tables, RLS policies)
- [x] Android location tracking (FusedLocationProvider)
- [x] iOS location tracking (CoreLocation)
- [ ] Family circles UI
- [ ] Real-time map (Mapbox)
- [ ] SQLite offline cache

### Phase 2: UI/UX Polish (0%)
- [ ] Liquid Glass theme
- [ ] Material Design theme
- [ ] Performance mode
- [ ] Notification system

### Phase 3: Travel Stories (0%)
- [ ] Trip recording
- [ ] Achievement system
- [ ] Trip sharing

---

## 🔗 Related Projects

- [[Discovery Service]] - Instance discovery for federation
- [[Tether Cloud]] - Official managed instances

---

## 📌 Key Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-13 | Kotlin Multiplatform Mobile | Share logic between Android/iOS |
| 2026-04-13 | Supabase for backend | Auth + DB + Realtime + Storage in one |
| 2026-04-13 | Federated architecture | Scalability + self-hosting |
| 2026-04-13 | Runtime discovery for instances | Best UX for multi-instance |
| 2026-04-13 | No speed competitions | Safety-first (exploration over speed) |

---

**Last Updated:** 2026-04-13  
**Maintained By:** Project Team
