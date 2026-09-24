# Volume 1: Architecture, Cognitive Theory, and Token Economics

---

## 1. Dual-Process Cognitive Architecture (System 1 vs. System 2)

Human cognition operates via two distinct processing modes (Kahneman, *Thinking, Fast and Slow*):
* **System 1 (Fast, Autonomous, Low-Energy):** Rapid pattern matching, heuristic-driven execution, minimal cognitive overhead.
* **System 2 (Slow, Deliberative, High-Energy):** Rigorous algorithmic reasoning, adversarial critique, formal risk evaluation.

Standard AI agent implementations suffer from a failure to separate these modes:
1. **Unconstrained System 1 Execution:** Agents generate code immediately without pre-flight critique, leading to subtle logic errors, state corruption, race conditions, security vulnerabilities, and architectural debt.
2. **Universal System 2 Execution:** Agents attempt exhaustive multi-agent debates on simple tasks (e.g. updating a CSS margin or renaming a variable), resulting in 200–300% token inflation, high latency, and developer frustration.

```
                                  USER REQUEST
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │   Task Complexity Classifier      │
                     │   (Domain & Stakes Evaluation)    │
                     └─────────────────┬─────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
        [Low-Complexity / Routine]            [High-Complexity / High-Stakes]
                    │                                     │
                    ▼                                     ▼
          SYSTEM 1: SINGLE-PASS                 SYSTEM 2: ADVERSARIAL TRIAD
          • Read Memory (Index/Node)            • Multi-Agent Debate Loop:
          • Direct Code Generation                1. [ARCHITECT] (Proposal & Diffs)
          • Execute & Verify Tests                2. [CRITIC] (Adversarial Audit)
          • Return Result                         3. [JUDGE] (Synthesis & Ruling)
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                             EXECUTION & ARTIFACT
```

### The Adversarial Triad Implementation
When triggered for high-stakes domains (zero-downtime database schema migrations, financial ledger transactions, distributed consensus, authentication protocols, major cross-system refactors), the primary agent orchestrates a three-role dialectic debate:

1. **The Architect (Subagent: `self`)**:
   * Analyzes technical specifications and generates a comprehensive design proposal.
   * Produces explicit file diffs, sequence diagrams, and mathematical invariants.
2. **The Critic (Subagent: `research` / strictly read-only)**:
   * Operates with an adversarial mindset, seeking failure modes.
   * Audits for: lookahead bias, race conditions, off-by-one errors, token bloat, credential leaks, and backward compatibility breakage.
   * Cannot edit files or execute state-modifying shell commands.
3. **The Judge (Primary Agent)**:
   * Reviews the Architect's proposal against the Critic's objections.
   * Rejects unmitigated risks, adjusts trade-offs, and issues a final, production-hardened execution plan.

---

## 2. Four-Tier Memory Topology

Memory is partitioned into four distinct operational tiers based on temporal relevance, volatility, and verification status:

```
┌────────────────────────────────────────────────────────────────────────┐
│                              HOT MEMORY                                │
│  • Location: Active Context Window (Terminal Buffer & In-Memory State) │
│  • Latency: Instantaneous | Cost: High (per-token context burn)        │
│  • Lifespan: Ephemeral (Single CLI invocation or chat session)         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Distillation
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                              WARM MEMORY                               │
│  • Location: ~/.okf_knowledge/concepts/                                │
│  • Capacity: Soft-Capped at 50 Concept Nodes                           │
│  • Structure: Markdown with YAML Frontmatter & Cross-Links             │
│  • Lifespan: Active domain knowledge (Touch threshold <= 45 days)     │
└──────────────────┬───────────────────────────────────┬─────────────────┘
                   │                                   │
                   │ Cold Pruning (>45 Days)           │ Promotion
                   ▼                                   ▲
┌──────────────────────────────────────┐  ┌────────────┴─────────────────┐
│             COLD MEMORY              │  │        STAGING INBOX         │
│ • Location: archive/concepts/        │  │ • Location: staging/         │
│ • Lifespan: Indefinite historical    │  │ • Source: Background synthesis│
│ • Ingestion: Manual retrieval only   │  │ • Lifespan: 14-Day Auto-TTL  │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

### 1. Hot Memory (Ephemeral Context)
* Active tokens held in the LLM's immediate working context.
* Kept lean by avoiding massive historical transcript dumping.

### 2. Warm Memory (`~/.okf_knowledge/concepts/`)
* Curated, verified institutional knowledge.
* **50-Node Soft Cap:** Prevents memory creep. Concept files average 200–400 tokens each.
* **Permanent Anchor Nodes:** `system_profile.md` and `dev_conventions.md` are exempt from expiration.

### 3. Cold Memory (`~/.okf_knowledge/archive/concepts/`)
* Repositories for deprecated, seasonal, or stale concepts untouched for $>45$ days.
* Preserves git history and intellectual property without polluting active search indexes.

### 4. Staging Inbox (`~/.okf_knowledge/staging/`)
* Ingestion sandbox for candidate concepts generated by background analysis, commit log mining, or automated ingestion.
* Governed by a **14-day auto-purge TTL** to eliminate review fatigue.

---

## 3. Staged Trust Hierarchy

A fatal flaw in autonomous agent design is **hallucination feedback loops**: an agent hallucinates a convention, stores it in persistent memory, and in future sessions treats its own hallucination as ground truth.

OKF resolves this with a **formal zero-trust promotion lifecycle**:

```
                       ┌───────────────────────────────┐
                       │       status: candidate       │
                       │   • Trust Score: 0 - 1        │
                       │   • Source: Background scrapers│
                       │   • Location: staging/        │
                       │   • Action: Untrusted         │
                       └───────────────┬───────────────┘
                                       │ Interactive Capture
                                       ▼
                       ┌───────────────────────────────┐
                       │         status: draft         │
                       │   • Trust Score: 1 - 2        │
                       │   • Source: Agent conversation│
                       │   • Location: concepts/       │
                       │   • Action: Experimental      │
                       └───────────────┬───────────────┘
                                       │ Empirical Test Pass
                                       ▼
                       ┌───────────────────────────────┐
                       │       status: verified        │
                       │   • Trust Score: 3 - 4        │
                       │   • Source: Passed test/compiler│
                       │   • Location: concepts/       │
                       │   • Action: Reliable Default  │
                       └───────────────┬───────────────┘
                                       │ Human User Sign-Off
                                       ▼
                       ┌───────────────────────────────┐
                       │        status: stable         │
                       │   • Trust Score: 5            │
                       │   • Source: Explicit approval │
                       │   • Location: concepts/       │
                       │   • Action: Invariant Rule    │
                       └───────────────────────────────┘
```

* **Candidate:** Auto-generated proposals. Never consulted for code generation without explicit human inspection.
* **Draft:** Active experiments recorded during pair programming. Marked with caveats.
* **Verified:** Code patterns that have been executed, run against test suites, and validated without errors.
* **Stable:** Permanent architecture rules confirmed by the developer.

---

## 4. Token Economics: Efficiency vs. Effectiveness

### A. Mathematical Context Compression Ratio
In traditional workflows, developers either paste long past conversations or rely on naive vector databases that inject thousands of tokens of messy chat logs into context.

In an active software engineering repository, accumulated developer-agent session transcripts, pull request discussions, and chat logs easily exceed **3,000,000+ raw tokens**.
OKF Warm Memory distills the complete set of verified architecture invariants, deployment conventions, and interface constraints into **modular concept nodes totaling ~2,500 tokens**.

$$\text{Compression Factor} = \frac{3,000,000}{2,500} = \mathbf{1,200\times \text{ Reduction}}$$

$$\text{Context Compression Ratio} = 1 - \left(\frac{2,500}{3,000,000}\right) = \mathbf{99.917\%}$$

### B. Progressive Disclosure vs. Context Dumping
Agents never inject the entire Warm Memory graph into context. They operate via **Progressive Disclosure**:
1. Agent queries `index.md` (~300 tokens) to discover relevant node paths.
2. Agent reads only the target node (e.g. `api_design_standards.md`, ~350 tokens).
3. Total input footprint: **~650 tokens**, compared to 10,000–30,000 tokens for generic RAG chunks.

### C. The Churn Elimination Multiplier (Effectiveness)
Token efficiency counts raw tokens spent. **Token effectiveness** measures output correctness per token consumed.

When an agent lacks verified domain knowledge (e.g., that payment endpoints require an `Idempotency-Key` header, or that database pagination must use deterministic cursor ordering instead of `OFFSET`), the session degrades into **multi-turn debugging churn**:

```
WITHOUT OKF (Correction Churn Cycle)
Turn 1: Generate flawed code (Missing idempotency key) ──► 3,500 Tokens
Turn 2: Reviewer / User provides rejection feedback    ──► 1,800 Tokens
Turn 3: Agent attempts fix (Breaks pagination logic)   ──► 3,800 Tokens
Turn 4: User corrects architecture again               ──► 1,200 Tokens
Turn 5: Final working rewrite                         ──► 4,000 Tokens
──────────────────────────────────────────────────────────────
TOTAL CONSUMPTION: ~14,300 Tokens across 5 turns

WITH OKF (Pre-Flight Verified Memory)
Turn 1: Read api_design_standards.md                  ──►   350 Tokens
Turn 1: Generate 100% compliant code on Turn 1         ──► 3,500 Tokens
──────────────────────────────────────────────────────────────
TOTAL CONSUMPTION: ~3,850 Tokens across 1 turn
NET SAVINGS: 10,450 Tokens (73.1% Reduction) + 0 Human Fatigue
```

---

## 5. Cache Invalidation & Stale Knowledge Resolution Architecture

A critical vulnerability in persistent memory systems is **stale knowledge drift**: when the underlying codebase or dependencies evolve, but the stored memory remains anchored to obsolete patterns, leading to hallucinated regressions.

OKF resolves the classic Cache Invalidation Problem through an **Epistemic Hierarchy** and a 4-layer invalidation engine:

```
                         EPISTEMIC GROUND TRUTH HIERARCHY
                         
  Level 1 (Highest):     LIVE USER INSTRUCTIONS
                         Direct user statements and corrections always override memory.
                                    ▲
                                    │ Overrides
  Level 2 (Empirical):   LIVE CODEBASE & PASSING TESTS
                         Actual files on disk, compiler errors, and automated test suites.
                                    ▲
                                    │ Overrides
  Level 3 (Heuristic):   OKF PERSISTENT MEMORY (~/.okf_knowledge)
                         Cached heuristics and historical patterns (Priors, not dogmas).
```

### The 4 Layers of Invalidation & Refresh

1. **Source Lineage Tracking (`sources:` metadata):**
   * Every concept node records the source files or ADRs it was derived from.
   * If a source file's last modified time (`mtime`) or Git commit is newer than the node's `updated_at` timestamp, the agent treats the concept as an **unverified cache** and re-inspects the source file.

2. **Conflict Detection & Trust Demotion:**
   * When live code or test suites contradict a concept node, the agent immediately flags the divergence.
   * The node's trust status is demoted from `status: stable` to `status: draft` or `stale`, preventing bad historical advice from being treated as invariant truth.

3. **Atomic Memory Refresh Lifecycle:**
   * Once a divergence is confirmed, the agent proposes a refreshed node:
     * Updates the technical specification to match current code.
     * Appends an entry to the `Verification & Test Record` status history.
     * Bumps `updated_at` to the current date.
     * Commits the updated node through the Git pre-commit gate.

4. **Temporal Decay (Biological Forgetting Curve):**
   * Concepts that are never consulted, updated, or re-verified within **45 days** are automatically relocated from `concepts/` to `archive/concepts/` by `prune_okf_memory.py`.
   * Stale, dead architectural rules automatically fade out of active Warm Memory without manual human pruning.

