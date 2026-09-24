# Volume 4: Knowledge Graph Architecture & Domain Concept Synthesis

---

## 1. Graph Topology & Schema Specifications

The OKF Knowledge Graph uses standard GitHub Flavored Markdown files with strict YAML frontmatter headers. It acts as an indexed semantic graph where markdown files represent conceptual nodes and relative links represent directed associative edges.

```
                              ┌────────────────┐
                              │    index.md    │ (Root Directory Table of Contents)
                              └───────┬────────┘
                                      │
        ┌───────────────┬─────────────┼───────────────┬────────────────┐
        ▼               ▼             ▼               ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
│system_profile│ │dev_convention│ │   api_   │ │  database_   │ │ distributed_ │
│     .md      │ │     .md      │ │ design_  │ │  migration_  │ │   caching_   │
└───────┬──────┘ └──────┬───────┘ │standards │ │  policy.md   │ │ patterns.md  │
        │               │         └───.md────┘ └──────┬───────┘ └──────┬───────┘
        └───────────────┼──────────────┼──────────────┘                │
                        │              ▼                               │
                        └──────► [Cross-Links] ◄───────────────────────┘
```

### Concept Node YAML Frontmatter Schema

Every markdown node residing in `~/.okf_knowledge/concepts/` must adhere to this formal schema:

```yaml
---
type: concept                     # Node classification: concept | index | reference
title: String                     # Standardized, human-readable title
description: String               # 1-2 sentence semantic summary
status: draft                     # candidate | draft | verified | stable
trust_score: 1                    # Integer [0 - 5]
tags: [tag1, tag2]                # Categorization and retrieval tags
created_at: YYYY-MM-DD            # ISO 8601 creation date
updated_at: YYYY-MM-DD            # ISO 8601 last modified date
anonymized: true                  # Boolean confirming path & PII scrubbing
sources: [source-reference]       # Architecture Decision Record (ADR), commit, or doc link
---
```

---

## 2. Institutional Knowledge Ingestion Methodology

Rather than relying on unstructured text or raw transcript dumps, modern engineering teams synthesize institutional knowledge from three authoritative repositories:

1. **Architectural Decision Records (ADRs):** Formal organizational choices regarding protocols, data schemas, and infrastructure topologies.
2. **Post-Mortems & PR Code Reviews:** Documented resolutions of historical production incidents, edge-case race conditions, and team conventions.
3. **Agent Interaction Trajectories:** Successful coding patterns, performance optimizations, and user corrections recorded during developer-AI pair programming sessions.

```
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│     ADR Repository     │  │  Post-Mortem Reports   │  │  Agent Session Logs    │
└───────────┬────────────┘  └───────────┬────────────┘  └───────────┬────────────┘
            │                           │                           │
            └───────────────────────────┼───────────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │          3-STAGE DISTILLATION ENGINE      │
                  │                                           │
                  │  Stage 1: De-Noising & Churn Elimination  │
                  │  Stage 2: Invariant Rule Extraction       │
                  │  Stage 3: Shannon Entropy Sanitization    │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │    OKF WARM MEMORY GRAPH (concepts/*.md)  │
                  │    High-Density, Test-Verified Knowledge  │
                  └───────────────────────────────────────────┘
```

### The 3-Stage Distillation Pipeline
1. **Stage 1 (De-Noising & Churn Elimination):** Strip away exploratory discussions, trial-and-error debugging loops, and temporary build issues.
2. **Stage 2 (Invariant Rule Extraction):** Extract only the immutable technical invariants: API envelope specifications, database isolation levels, caching strategies, and concurrency thresholds.
3. **Stage 3 (Sanitization & Semantic Linking):** Scrub all machine paths, internal IPs, and credentials using Shannon Entropy verification before committing to Git.

---

## 3. Universal Production Concepts & Master Index

Below is the complete text of six foundational Warm Memory nodes representing universal industry best practices in modern software engineering:

### A. Master Index (`~/.okf_knowledge/index.md`)
```markdown
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
* Query Cold Memory only on explicit fallback or when reviewing historical decisions.

## 3. Staging Inbox
* Newly synthesized candidates await review in `staging/` before being promoted to Warm Memory.
```

---

### B. `system_profile.md` (Permanent Anchor Node)
```markdown
---
type: concept
title: System Environment Profile
description: Standardized host environment specs, shell configurations, and developer runtimes.
status: stable
trust_score: 5
tags: [system, environment, runtimes, toolchains]
created_at: 2026-09-24
updated_at: 2026-09-24
anonymized: true
sources: [environment-audit-standard]
---

# System Environment Profile

## Summary
Baseline runtime specifications and standard developer environments for local and containerized workflows.

## Host Specs & Toolchains
* **Operating System:** Cross-Platform Baseline (Windows 11 / Linux POSIX / macOS)
* **Shell Standards:** PowerShell Core (`pwsh`) on Windows; POSIX Bash on Linux/macOS
* **Developer Runtimes:** Python 3.10+, Node.js 20+ LTS, Git 2.40+, Docker Engine
* **Virtual Environments:** Always isolate Python dependencies in `.venv/` and Node dependencies in `node_modules/`.

## Directory Standards
* **User Root:** `~` (`%USERPROFILE%` on Windows, `$HOME` on Unix)
* **Knowledge Base:** `~/.okf_knowledge/`
* **Agent Global Config:** `~/.gemini/config/` or `~/.config/opencode/`
* **Active Workspaces:** Dedicated workspace trees outside system root directories

## References & Cross-Links
* [Master Index](../index.md)
* [Developer Conventions](./dev_conventions.md)
```

---

### C. `dev_conventions.md` (Permanent Anchor Node)
```markdown
---
type: concept
title: Developer Conventions & Engineering Standards
description: Global coding practices, memory governance, and tool usage rules.
status: stable
trust_score: 5
tags: [conventions, guidelines, architecture, security]
created_at: 2026-09-24
updated_at: 2026-09-24
anonymized: true
sources: [engineering-standards-charter]
---

# Developer Conventions & Engineering Standards

## Summary
Global engineering patterns and agent operating standards enforced across projects.

## Core Directives
1. **Never Hardcode Secrets:** API tokens, private keys, and passwords must never be written into code, markdown docs, or shell history. Use environment variables and secrets managers.
2. **Path Portability:** Always use relative paths (`~` or environment variables) in documentation and scripts; never expose raw machine paths.
3. **Deterministic Environments:** Always run within dedicated project virtual environments (`.venv` or Docker containers).
4. **Git Discipline:** Make focused, atomic commits. Run automated test suites prior to pushing or opening PRs.
5. **Memory Staging Gate:** Propose new learnings as `status: draft`. Never overwrite stable conventions without explicit developer confirmation.

## References & Cross-Links
* [Master Index](../index.md)
* [System Environment Profile](./system_profile.md)
* [API Design Standards](./api_design_standards.md)
```

---

### D. `api_design_standards.md`
```markdown
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
```

---

### E. `database_migration_policy.md`
```markdown
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
```

---

### F. `distributed_caching_patterns.md`
```markdown
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
```

---

### G. `llm_inference_routing.md`
```markdown
---
type: concept
title: LLM Inference Routing & Token Optimization
description: Multi-provider failover, exponential retry with jitter, and token budget governance.
status: verified
trust_score: 4
tags: [llm, routing, inference, tokens, ai-architecture]
created_at: 2026-09-24
updated_at: 2026-09-24
anonymized: true
sources: [adr-015-llm-router]
---

# LLM Inference Routing & Token Optimization

## Summary
Architecture for routing autonomous coding agents across multi-tiered LLM endpoints, optimizing for latency, cost, and reliability.

## Key Technical Specifications
* **Dynamic Provider Routing:**
  * Primary: High-speed serverless endpoints for System 1 fast execution.
  * Fallback: Dedicated higher-parameter reasoning models for System 2 Adversarial Triad debates.
* **Failover & Retry Architecture:**
  * Intercept HTTP 429 (Rate Limit) and 503 (Overloaded) status codes.
  * Apply exponential backoff with full jitter:
    $$t_{\text{backoff}} = \text{Random}(0, \min(t_{\text{max}}, t_{\text{base}} \times 2^{\text{attempt}}))$$
* **Token Budget Caps:**
  * Enforce maximum output token bounds (e.g., 4,000–8,000 tokens) in client configuration to eliminate runaway generation costs.
  * Use progressive context disclosure to keep prompt tokens bounded under 15,000 tokens per turn.

## References & Cross-Links
* [Master Index](../index.md)
* [Developer Conventions](./dev_conventions.md)
* [Distributed Caching Patterns](./distributed_caching_patterns.md)
```
