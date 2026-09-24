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
