---
type: concept
title: Zero-Downtime Database Migration Policy
description: Expand-and-contract schema migrations, lock timeout controls, and rollback safety.
status: verified
trust_score: 4
tags: [database, sql, migrations, devops, safety]
created_at: 2026-09-24
updated_at: 2026-09-24
anonymized: true
sources: [adr-012-zero-downtime-migrations]
---

# Zero-Downtime Database Migration Policy

## Summary
Operational safety rules for applying relational database schema migrations without locking tables or degrading production latency.

## Key Technical Specifications
* **Expand-and-Contract Pattern (Three-Phase Deployment):**
  1. *Phase 1 (Expand):* Add new columns or tables as nullable or with safe defaults. Application writes to both old and new schemas.
  2. *Phase 2 (Migrate):* Backfill historical data in small, indexed batches during low-traffic windows.
  3. *Phase 3 (Contract):* Deprecate old columns and remove them in a subsequent deployment after confirming zero active readers.
* **Lock Timeout Controls:**
  * Every DDL migration must explicitly configure a short lock timeout (e.g. `SET lock_timeout = '2s';`).
  * If exclusive lock acquisition exceeds the threshold, the migration aborts rather than queuing blocking transactions behind it.
* **Concurrent Index Creation:**
  * In PostgreSQL, always use `CREATE INDEX CONCURRENTLY` to avoid taking shared write locks on active production tables.

## References & Cross-Links
* [Master Index](../index.md)
* [API Design Standards](./api_design_standards.md)
* [Distributed Caching Patterns](./distributed_caching_patterns.md)
