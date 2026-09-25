---

## Persistent Autonomous Memory & Reasoning Directives (OKF)
1. **Auto-Consult Memory**: Before executing tasks that involve environment configs, toolchains, or previously solved patterns, automatically consult `~/.okf_knowledge/index.md` via the `okf-memory` skill.
2. **Auto-Triad**: For high-complexity tasks (zero-downtime database migrations, financial reconciliation math, cryptographic protocols, major cross-system refactors), automatically invoke the `adversarial-triad` workflow ([ARCHITECT] -> [CRITIC] -> [JUDGE]) to audit the plan. Routine tasks run in single-pass mode.
3. **Staged Trust Model**: All newly recorded concepts start as `status: draft`. Promotion to `status: verified` requires practical testing, and `status: stable` requires explicit confirmation.
4. **Zero Secret & PII Leakage**: Always use `sanitize_okf.py` before saving nodes. Never store credentials, API tokens, passwords, or absolute machine paths.
5. **Memory Tiering**: Active Warm Memory is soft-capped at 50 nodes in `~/.okf_knowledge/concepts/`. Stale nodes (>45 days) are archived to `archive/concepts/`. Staging candidates older than 14 days are auto-purged.
6. **Epistemic Hierarchy**: Live User Instructions > Live Working Code & Tests > OKF Persistent Memory. If live code or tests contradict memory, memory yields and proposes an update.
7. **Reflexive Turn Auto-Capture (Silent Invariant Ingestion)**: At the conclusion of any task that establishes a verified toolchain fix, environment workaround, core architecture rule, or explicit user preference:
   - Discard ephemeral syntax errors, temporary scratch scripts, or conversational chit-chat.
   - Silently invoke `record_okf_learning.py` (or `Record-OkfLearning.ps1`) with `status: draft` in `~/.okf_knowledge/concepts/`.
   - Acknowledge captured knowledge with a single concise bullet link in your final response.
8. **Antigravity-OKF Full Symbiosis & Dual Sync**:
   - **Unified Architecture**: OKF is native to Antigravity and Antigravity is native to OKF across all workspaces and conversations.
   - **Live Turn Telemetry**: All Antigravity sessions trigger global lifecycle hooks (`~/.gemini/config/hooks.json`) on loop completion to stream sanitized turn telemetry into OKF staging (`staging/live_turn_harvest.jsonl`).
   - **Offline & Cross-Session Synthesis**: Non-live conversations and active workspace Git commits are automatically aggregated nightly into candidate proposals via `OKF-DreamSynthesis`.
   - **Cognitive Ground Truth**: Any durable decision, toolchain fix, or user directive made in ANY Antigravity session immediately updates OKF.
