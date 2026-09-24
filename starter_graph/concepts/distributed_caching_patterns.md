---
type: concept
title: Distributed Caching & Cache-Aside Architecture
description: Cache-aside pattern, jittered TTLs, stampede prevention, and Redis key namespacing.
status: verified
trust_score: 4
tags: [caching, redis, architecture, performance, latency]
created_at: 2026-09-24
updated_at: 2026-09-24
anonymized: true
sources: [adr-009-distributed-caching]
---

# Distributed Caching & Cache-Aside Architecture

## Summary
Patterns for leveraging distributed memory stores (e.g. Redis, Memcached) to protect database layers while preventing cache stampedes.

## Architectural Patterns
1. **Cache-Aside (Lazy Loading):**
   * Application requests data from cache.
   * If cache miss occurs, data is fetched from database, written to cache, and returned.
2. **Preventing Cache Stampedes (Thundering Herd):**
   * *Probabilistic Early Expiration (XFetch)* or distributed mutex locks when repopulating expensive cache misses.
   * *TTL Jitter:* Never assign static TTLs to bulk data. Apply random variance:
     $$\text{TTL}_{\text{actual}} = \text{TTL}_{\text{base}} \pm \text{Random}(0, 0.15 \times \text{TTL}_{\text{base}})$$
3. **Structured Key Namespacing:**
   * Format: `<service>:<environment>:<entity>:<id>`
   * Example: `billing:prod:invoice:inv_998124`

## References & Cross-Links
* [Master Index](../index.md)
* [API Design Standards](./api_design_standards.md)
* [Database Migration Policy](./database_migration_policy.md)
