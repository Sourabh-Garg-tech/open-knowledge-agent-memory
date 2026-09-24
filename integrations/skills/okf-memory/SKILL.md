---
name: okf-memory
description: >-
  Autonomous persistent memory system. Automatically consult this skill to check
  recorded system conventions, past debugging solutions, or to record newly discovered
  architectural patterns in the local Open Knowledge Format (OKF) graph at ~/.okf_knowledge.
---

# OKF Tiered Memory Management

This skill allows the agent to navigate Warm Memory and maintain concept nodes.

## Querying Knowledge
1. Consult `~/.okf_knowledge/index.md` first to discover active Warm concepts.
2. Read specific concept nodes in `~/.okf_knowledge/concepts/` using `view_file`.
3. If a concept is not found and the user requests legacy context, check `~/.okf_knowledge/archive/concepts/`.
4. Check `~/.okf_knowledge/staging/` to review candidate concepts.

## Recording New Knowledge
When learning a persistent architectural convention, reusable command pattern, or user preference:
1. Propose the draft concept to the user before writing.
2. Create the file using `~/.okf_knowledge/scripts/new_okf_node.py` or `New-OkfNode.ps1`.
3. New nodes enter as `status: draft` with `trust_score: 1`.
4. Update `~/.okf_knowledge/index.md` with the new link.
5. **Safety Rule:** Never record credentials, API keys, or absolute user directories. Always pass content through `sanitize_okf.py`.
