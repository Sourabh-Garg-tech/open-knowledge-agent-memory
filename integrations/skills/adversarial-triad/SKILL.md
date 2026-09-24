---
name: adversarial-triad
description: >-
  Adversarial planning loop. Automatically activate this skill for high-complexity,
  high-stakes, or multi-step architecture planning tasks to conduct an internal
  Architect-Critic-Judge debate before writing code.
---

# Adversarial Triad Workflow

For high-complexity tasks (e.g. distributed consensus, zero-downtime database migrations, cryptographic key exchange):

1. **The Architect (Subagent: `self`)**:
   - Generates an optimal implementation proposal, explicit file diffs, and execution steps.
2. **The Critic (Subagent: `research` / read-only)**:
   - Evaluates the Architect's proposal with ruthless skepticism.
   - Hunts for: race conditions, edge-case failures, secret leakage, token consumption spikes, and regressions.
   - Operates with strictly read-only file and tool access.
3. **The Judge (Primary Agent)**:
   - Synthesizes the debate into a final, hardened plan that addresses all verified Critic objections.
