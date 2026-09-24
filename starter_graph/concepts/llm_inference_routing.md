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
