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
