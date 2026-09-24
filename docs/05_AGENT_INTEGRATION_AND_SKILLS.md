# Volume 5: Universal Agent Integration, Global Directives, and Skills

---

## 1. Universal Agent Integration Architecture

Different AI coding platforms use different customization primitives. The OKF system is platform-agnostic and maps cleanly across tools:

| Platform | Rules File | Procedural Workflows / Skills | Storage Location |
| :--- | :--- | :--- | :--- |
| **Google Antigravity** | `~/.gemini/AGENTS.md` or `AGENTS.md` | `~/.gemini/config/skills/<name>/SKILL.md` | `~/.okf_knowledge/` |
| **OpenCode** | `%USERPROFILE%\.config\opencode\opencode.json` | Project scripts / custom instructions | `~/.okf_knowledge/` |
| **Claude Code** | `CLAUDE.md` / `~/.claude/config` | Custom sub-prompts / tools | `~/.okf_knowledge/` |
| **Cursor IDE** | `.cursorrules` / User Rules | Custom slash commands / MCP | `~/.okf_knowledge/` |
| **Windsurf / Cascade** | `.windsurfrules` | Custom workflows | `~/.okf_knowledge/` |

---

## 2. Global Directives Block (`AGENTS.md` / `GEMINI.md`)

To enforce autonomous memory consultation, security sanitization, and the System 2 dialectic debate, append this exact block to your global agent instructions file (e.g. `%USERPROFILE%\AGENTS.md` or `~/.gemini/AGENTS.md`):

```markdown
---

## Persistent Autonomous Memory & Reasoning Directives (OKF)
1. **Auto-Consult Memory**: Before executing tasks that involve environment configs, toolchains, or previously solved patterns, automatically consult `~/.okf_knowledge/index.md` via the `okf-memory` skill.
2. **Auto-Triad**: For high-complexity tasks (zero-downtime database migrations, financial reconciliation math, cryptographic protocols, major cross-system refactors), automatically invoke the `adversarial-triad` workflow ([ARCHITECT] -> [CRITIC] -> [JUDGE]) to audit the plan. Routine tasks run in single-pass mode.
3. **Staged Trust Model**: All newly recorded concepts start as `status: draft`. Promotion to `status: verified` requires practical testing, and `status: stable` requires user confirmation.
4. **Zero Secret & PII Leakage**: Always use `Sanitize-OkfContent.ps1` before saving nodes. Never store credentials, API tokens, passwords, or absolute machine paths.
5. **Memory Tiering**: Active Warm Memory is soft-capped at 50 nodes in `~/.okf_knowledge/concepts/`. Stale nodes (>45 days) are archived to `archive/concepts/`. Staging candidates older than 14 days are auto-purged.
```

---

## 3. Production Skill Definitions

In Antigravity and compatible agent runtimes, procedural behaviors are structured as **Skills** (directories containing YAML frontmatter and operational runbooks).

### A. Skill 1: `okf-memory`
Deploy to: `~/.gemini/config/skills/okf-memory/SKILL.md`

```markdown
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
1. Consult `~/.okf_knowledge/index.md` first to identify active Warm concepts.
2. Read specific concept nodes in `~/.okf_knowledge/concepts/` using `view_file`.
3. If a concept is not found and the user requests legacy context, check `~/.okf_knowledge/archive/concepts/`.
4. Check `~/.okf_knowledge/staging/` to alert the user if candidate concepts await review.

## Recording New Knowledge
When learning a persistent architectural convention, reusable command pattern, or user preference:
1. Always propose the draft to the user before writing.
2. Create the file using `~/.okf_knowledge/scripts/New-OkfNode.ps1` or `python scripts/new_okf_node.py`.
3. New nodes enter as `status: draft` with `trust_score: 1`.
4. Update `~/.okf_knowledge/index.md` with the new link.
5. **Safety Rule:** Never record credentials, API keys, or absolute user directories.
```

---

### B. Skill 2: `adversarial-triad`
Deploy to: `~/.gemini/config/skills/adversarial-triad/SKILL.md`

```markdown
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
```

---

## 4. Progressive Disclosure Workflow in Practice

```
                     AGENT TURN COMMENCES
                              │
               Is Task Related to Config/Domain?
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
            [YES]                            [NO]
              │                               │
    Read index.md (~300 tok)                  │
              │                               │
    Match Keyword to Node                     │
              │                               │
    Read concepts/*.md (~350 tok)             │
              │                               │
              └───────────────┬───────────────┘
                              │
                Is Task High-Complexity/Stakes?
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
            [YES]                            [NO]
              │                               │
     [ADVERSARIAL TRIAD]               [SINGLE-PASS]
   Architect ─► Critic ─► Judge        Execute Code Fast
              │                               │
              └───────────────┬───────────────┘
                              │
                  Execution & Verification
                              │
                 Did We Discover New Pattern?
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
            [YES]                            [NO]
              │                               │
    Run sanitize_okf.py                       │
              │                               │
    Write to concepts/*.md (draft)            │
              │                               │
    Update index.md                           │
              │                               │
    Git Commit (Pre-Commit Gate)              │
              │                               │
              └───────────────┬───────────────┘
                              │
                         FINISH TURN
```

---

## 4. Human-in-the-Loop Developer CLI (okf-*)

To inspect, query, and manage the knowledge graph without breaking developer focus or leaving the terminal, OKF provides high-speed native shell functions ($PROFILE or ~/.bashrc):

| Command | Action | Use Case |
| :--- | :--- | :--- |
| okf-status | Displays terminal dashboard (Warm/Staging/Archive counts, capacity, Git status). | Daily check of knowledge graph health. |
| okf-search "<query>" | Rapid grep across all concept notes with line numbers. | Finding previously solved architecture patterns. |
| okf-new "<Title>" "[Desc]" | Scaffolds a schema-compliant node in concepts/. | Manually recording a new convention. |
| okf-verify | Runs test_okf_graph.py graph validator & Shannon entropy scan. | Quality gate check before git pushes. |
| okf-prune | Runs memory TTL pruning and archiving. | Maintaining warm memory soft cap (<= 50). |
| okf-dream [repoPath] | Triggers background "Dream Synthesis" on recent git commits. | Distilling learnings from recent commits into staging. |
| okf-open [concept] | Opens specific concept note or memory folder in editor. | Direct reading and manual edits. |


