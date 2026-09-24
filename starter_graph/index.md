---
type: index
title: Global Autonomous Knowledge Base
description: Master tiered knowledge graph maintained by AI coding agents across sessions.
status: stable
trust_score: 5
tags: [system, index, global]
updated_at: 2026-09-24
anonymized: true
---

# Global Knowledge Base (OKF)

This is the primary root index for machine-level knowledge, system conventions, and cross-project development patterns.

## 1. Warm Memory Graph (Active Concepts)
* [System Profile](./concepts/system_profile.md) — Host OS, shell, python runtime, container toolchains, and environment profile.
* [Developer Conventions](./concepts/dev_conventions.md) — Global coding guidelines, tool preferences, and safety rules.
* [API Design Standards](./concepts/api_design_standards.md) — REST & HTTP API contracts, idempotency keys, and error envelopes.
* [Database Migration Policy](./concepts/database_migration_policy.md) — Zero-downtime expand-and-contract migrations, lock timeout controls, and rollback safety.
* [Distributed Caching Patterns](./concepts/distributed_caching_patterns.md) — Cache-aside pattern, jittered TTLs, stampede prevention, and key namespacing.
* [LLM Inference Routing](./concepts/llm_inference_routing.md) — Multi-provider failover, exponential backoff with jitter, and token budget governance.

## 2. Cold Memory Archive
* Stagnant or superseded concepts older than 45 days are archived to `archive/concepts/`.

## 3. Staging Inbox
* Newly synthesized candidates await review in `staging/` before being promoted to Warm Memory.
