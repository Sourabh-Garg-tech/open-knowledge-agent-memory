---
type: concept
title: API Design Standards & HTTP Contracts
description: Architectural conventions for RESTful APIs, idempotency keys, error envelopes, and cursor pagination.
status: verified
trust_score: 4
tags: [api, rest, http, architecture, standards]
created_at: 2026-09-24
updated_at: 2026-09-24
anonymized: true
sources: [adr-004-api-design]
---

# API Design Standards & HTTP Contracts

## Summary
Core conventions for building robust, backwards-compatible, and high-performance HTTP REST APIs.

## Protocol Invariants
1. **Idempotency for Mutating Operations:**
   * All `POST` endpoints creating resources must require an `Idempotency-Key` header (UUIDv4).
   * Backend caches the operation result for 24 hours to prevent duplicate processing during network retries.
2. **Standard Error Envelope:**
   * All error responses (4xx, 5xx) must return a standardized JSON structure:
   ```json
   {
     "error": {
       "code": "RESOURCE_NOT_FOUND",
       "message": "Human-readable description.",
       "details": [],
       "trace_id": "req_01HXYZ..."
     }
   }
   ```
3. **Deterministic Pagination:**
   * Prefer cursor-based pagination (`cursor` and `limit`) over offset-based pagination to avoid missing records during high-write workloads.
4. **ISO 8601 Timestamps:**
   * All timestamps in requests and responses must use UTC ISO 8601 formatting (`YYYY-MM-DDTHH:MM:SSZ`).

## References & Cross-Links
* [Master Index](../index.md)
* [Developer Conventions](./dev_conventions.md)
* [Database Migration Policy](./database_migration_policy.md)
