# Volume 2: Mathematical Specifications, Security Guardrails, and Quality Gates

---

## 1. Information-Theoretic Secret Detection (Shannon Entropy)

Standard security scrapers rely solely on regular expressions targeting known vendor prefixes (e.g. `ghp_`, `hf_`, `AKIA`). This leaves a catastrophic blind spot:
* Custom database connection strings and passwords.
* Arbitrary high-entropy API secrets lacking vendor-specific prefixes.
* Hex-encoded private key segments or JWT payloads.

To guarantee zero secret leakage into persistent memory, OKF couples **Structural Regex** with **Shannon Information Entropy**.

### Mathematical Formulation
For any character sequence $S = (s_1, s_2, \dots, s_N)$ of length $N$ over an alphabet $\Sigma$, the Shannon Entropy $H(S)$ measures the average information density per character in bits:

$$H(S) = -\sum_{x \in \Sigma} P(x) \log_2 P(x)$$

Where the empirical probability $P(x)$ of character $x$ is defined as:

$$P(x) = \frac{\text{count}(x, S)}{N}$$

```
                SHANNON ENTROPY DISTRIBUTION SPECTRUM (Bits / Char)
  0.0                      2.5             3.8       4.1     4.3     4.8        6.0
  ├─── Repeating Strings ───┼── Natural Prose ─┼── Code ──┼───┼── API Keys ───────┤
  │    "aaaaaaaaaaaa"       │   "The quick brown fox"     │   │   "dK3#m9!xP7$qR..."  │
  │    (H = 0.0)            │   (H = 2.8 - 3.4)           │   │   (H = 4.4 - 5.2)     │
  └─────────────────────────┴─────────────────────────────┴───┴───────────────────┘
                                                       ▲   ▲
                               Assignment Key-Value Gate ─┘   │
                               Unstructured Token Gate ───────┘
```

### Derivation of Operational Thresholds

1. **Natural Language Prose:**
   * English text exhibits significant redundancy due to grammar and character frequency distributions (e.g. 'e', 't', 'a' occur far more frequently than 'z', 'q').
   * Empirical Shannon Entropy of standard English text: **$2.50 \le H(S) \le 3.65$**.

2. **Source Code & Scripting Syntax:**
   * Code contains punctuation, indentation, and variable naming conventions.
   * Empirical Shannon Entropy of code snippets: **$3.00 \le H(S) \le 4.15$**.

3. **Key-Value Pair Assignments ($H > 4.3$):**
   * Pattern: `([a-zA-Z0-9_]+_key|token|secret|password)\s*[:=]\s*["']?([a-zA-Z0-9/+=_\-]{20,})["']?`
   * When a string is explicitly assigned to a variable named `key`, `token`, `secret`, or `password`, the prior probability of it being a credential is high.
   * **Threshold:** Any assigned value of length $\ge 20$ with **$H(S) > 4.3$** is redacted to `<HIGH_ENTROPY_SECRET_REDACTED>`.

4. **Unstructured Tokenizer Fallback ($H \ge 4.5, \text{length} \ge 24$):**
   * Arbitrary high-entropy strings floating in unstructured text without explicit assignment.
   * Higher entropy threshold ($H \ge 4.5$) is required to avoid false positives on CamelCase variable names, UUIDs, or compiler hashes.
   * **Threshold:** Any isolated token of length $\ge 24$ with **$H(S) \ge 4.5$** is redacted to `<HIGH_ENTROPY_TOKEN_REDACTED>`.

### Whitelisting & False Positive Invariants
To prevent redacting non-secret development tokens, the tokenizer enforces strict exemptions:
1. **HTTP/HTTPS URLs:** Prefixes matching `http://` or `https://` are skipped.
2. **Git Commit SHAs:** 40-character lowercase hexadecimal strings (`^[0-9a-f]{40}$`) are preserved.
3. **Markdown Relative Paths:** Strings ending in `.md` are preserved.

---

## 2. Multi-Pass Sanitization Pipeline

The complete sanitization sequence executed by [`sanitize_okf.py`](./03_IMPLEMENTATION_AND_CODE_BLUEPRINTS.md#a-sanitize_okfpy) and [`Sanitize-OkfContent.ps1`](./03_IMPLEMENTATION_AND_CODE_BLUEPRINTS.md#a-sanitize-okfcontentps1) follows a 4-stage pipeline:

```
                    INPUT CONTENT (Raw Markdown / Log)
                                   │
                                   ▼
                 [Pass 1: Path & Identity Normalization]
                 • C:\Users\<user> ──► ~
                 • $USERPROFILE    ──► ~
                 • $COMPUTERNAME   ──► <HOST_ANONYMIZED>
                                   │
                                   ▼
                 [Pass 2: Network & Key Block Scrubbing]
                 • 192.168.x.x / 10.x.x.x
                 • -----BEGIN PRIVATE KEY----- ... -----END PRIVATE KEY-----
                                   │
                                   ▼
                 [Pass 3: Structural Regex (Known Prefixes)]
                 • ghp_* (GitHub PAT)      ──► <GITHUB_PAT_REDACTED>
                 • hf_* (Hugging Face)     ──► <HF_TOKEN_REDACTED>
                 • AIza* (Google Cloud)    ──► <GCP_KEY_REDACTED>
                 • sk-* (OpenAI Keys)      ──► <OPENAI_KEY_REDACTED>
                 • Bearer <token>          ──► Bearer <TOKEN_REDACTED>
                                   │
                                   ▼
                 [Pass 4: Shannon Entropy Statistical Scan]
                 • Key-Value Assignments: H > 4.3 (len >= 20)
                 • Unstructured Tokens:   H >= 4.5 (len >= 24)
                                   │
                                   ▼
                      SANITIZED OUTPUT (Clean OKF Node)
```

---

## 3. Automated Quality Gate: Git Pre-Commit Boundary

Memory integrity is not left to developer discipline. It is physically enforced at the Git version control boundary.

```
       USER OR AGENT CALLS
          [git commit]
               │
               ▼
┌───────────────────────────────────────────────┐
│ Git Hook: .git/hooks/pre-commit               │
│ Calls: python scripts/test_okf_graph.py       │
└───────┬───────────────────────────────┬───────┘
        │ Exit Code 0 (Success)         │ Exit Code != 0 (Failure)
        ▼                               ▼
┌───────────────────────────────┐       ┌───────────────────────────────┐
│ COMMIT ACCEPTED               │       │ COMMIT ABORTED                │
│ • Graph integrity verified    │       │ • Dead relative link detected │
│ • All frontmatter valid       │       │ • Unredacted path found       │
│ • No secrets or entropy leaks │       │ • Leaked API token identified │
│ • Warm cap <= 50 nodes        │       │ • Warm cap exceeded           │
└───────────────────────────────┘       └───────────────────────────────┘
```

### Pre-Commit Script (`~/.okf_knowledge/.git/hooks/pre-commit`)
Git for Windows executes hooks inside an embedded MSYS bash shell. To avoid path separator bugs (`\` vs `/`), the hook script resolves paths dynamically:

```bash
#!/usr/bin/env bash
# OKF Graph Integrity & Security Pre-Commit Guard

echo "=== [Pre-Commit Hook] Running OKF Graph Integrity & Security Verification ==="

python scripts/test_okf_graph.py
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: OKF Graph validation failed! Commit aborted."
    echo "Check for dead links, unsanitized paths, or frontmatter errors before committing."
    exit 1
fi

echo "SUCCESS: OKF Graph verified clean. Proceeding with commit."
exit 0
```

---

## 4. Verification Checkpoint Matrix

The Python validator [`test_okf_graph.py`](./03_IMPLEMENTATION_AND_CODE_BLUEPRINTS.md#b-test_okf_graphpy) runs an automated 5-point audit on every commit:

| Check # | Audit Target | Detection Rule | Remediation on Failure |
| :--- | :--- | :--- | :--- |
| **Check 1** | **Warm Memory Cap** | `warm_count <= 50` | Run `prune_okf_memory.py` to archive stale nodes |
| **Check 2** | **YAML Frontmatter** | Regex `^---\s*\r?\n(.*?)\r?\n---` | Add missing metadata headers |
| **Check 3** | **Absolute User Paths** | Matches `$HOME`, `$USERPROFILE`, or `C:\Users\...` | Run `sanitize_okf.py` to replace with `~` |
| **Check 4** | **Unredacted API Keys** | Matches known token prefixes (`ghp_`, `hf_`, `sk-`) | Scrub credentials immediately |
| **Check 5** | **Dead Relative Links** | Checks `[label](path.md)` against disk path | Fix broken links or restore missing concept files |
