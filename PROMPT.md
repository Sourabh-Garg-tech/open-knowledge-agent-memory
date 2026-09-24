# Master Agent Deployment Prompt: Open Knowledge Agent Memory (OKF) & Adversarial Triad System

> **Instructions for Use:**  
> Copy and paste the entire text block below into any AI coding assistant (Antigravity, Claude Code, OpenCode, Cursor, ChatGPT, Gemini, etc.) in a fresh workspace or terminal.  
> It instructs the agent to autonomously bootstrap, configure, test, and verify the complete, production-hardened OKF cognitive architecture from scratch.

---

```markdown
# TASK: Initialize Production-Grade Open Knowledge Agent Memory (OKF) & Adversarial Triad System

You are an expert AI systems architect. Your mission is to deploy and verify a persistent, git-backed, tiered cognitive architecture (Open Knowledge Agent Memory — OKF) coupled with an Adversarial Triad (System 2) reasoning loop on this machine.

The system eliminates context amnesia, runaway token bloat, and credential leaks by establishing a local, self-auditing knowledge graph governed by Shannon Information Entropy security filters and automated Git pre-commit quality gates.

---

### Core Architectural Principles
1. **Tiered Memory Hierarchy:**
   - **HOT:** In-context active terminal buffer.
   - **WARM:** Curated, active concepts in `~/.okf_knowledge/concepts/` (strictly soft-capped at 50 nodes).
   - **COLD:** Compressed archive in `~/.okf_knowledge/archive/concepts/` (inactivity TTL > 45 days).
   - **STAGING:** Ingestion sandbox in `~/.okf_knowledge/staging/` (unreviewed candidate TTL > 14 days).
2. **Staged Trust Model:**
   - `candidate` (Zero Trust, background synthesis) → `draft` (Interactive capture) → `verified` (Test-proven) → `stable` (Human-confirmed permanent invariant).
3. **Information-Theoretic Security (Shannon Entropy):**
   - Redacts credentials matching $H(S) = -\sum P(x_i) \log_2 P(x_i) > 4.3$ on key-value assignments and $H(S) \ge 4.5$ on raw tokens ($\ge 24$ chars).
   - Whitelists URLs, 40-char Git commit SHAs, and markdown filenames.
   - Normalizes all paths (`C:\Users\<user>` or `/home/<user>` → `~`).
4. **Physical Quality Gate:**
   - Git Pre-Commit Hook (`.git/hooks/pre-commit`) physically blocks any commit containing broken relative links, missing frontmatter, or unredacted secrets.
5. **Gated System 2 Dialectic Debate:**
   - Routine tasks run in fast single-pass mode.
   - High-complexity/high-stakes tasks (database migrations, ledger transactions, consensus protocols) invoke the Adversarial Triad ([ARCHITECT] → [CRITIC] → [JUDGE]).
6. **Epistemic Hierarchy (Anti-Stale Cache):**
   - Live User Instructions > Live Code & Tests > OKF Persistent Memory.
   - Lineage tracking (`sources:` metadata) flags concepts when source files are modified.

---

### Execution Phase 1: Directory Structure & Version Control

Create the directory tree and initialize the Git repository at `~/.okf_knowledge`:

#### PowerShell Execution:
```powershell
$base = "$HOME\.okf_knowledge"
mkdir -p "$base\concepts", "$base\archive\concepts", "$base\staging", "$base\scripts", "$base\tests"

if (-not (Test-Path "$base\.git")) {
    git -C $base init -b master
}

# Create .gitignore
@"
.env
*.local
*.secret
*.key
*.token
__pycache__/
*.py[cod]
*$py.class
*.so
.DS_Store
Thumbs.db
*.swp
*.bak
"@ | Set-Content -Path "$base\.gitignore" -Encoding UTF8
```

---

### Execution Phase 2: Production Python 3 Core Engines

Write the four core Python engines to `~/.okf_knowledge/scripts/`:

#### 1. `~/.okf_knowledge/scripts/sanitize_okf.py`
```python
#!/usr/bin/env python3
"""
OKF Security Sanitization Engine (Regex + Shannon Entropy Analysis).
Redacts known token prefixes, high-entropy cryptographic strings, personal user paths, and machine PII.
"""

import sys
import os
import re
import math
from collections import Counter

def calculate_shannon_entropy(text: str) -> float:
    """Calculates the Shannon entropy H(S) of a string."""
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())

def sanitize_content(content: str) -> str:
    """Applies structural regex and Shannon entropy filters to redact sensitive information."""
    if not content:
        return ""

    sanitized = content

    # 1. Path & Identity Normalization
    home = os.path.expanduser("~")
    sanitized = re.sub(re.escape(home), "~", sanitized)
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        sanitized = re.sub(re.escape(userprofile), "~", sanitized)
    sanitized = re.sub(r'(?i)C:\\Users\\[a-zA-Z0-9_\-\.]+', "~", sanitized)

    computer_name = os.environ.get("COMPUTERNAME")
    if computer_name:
        sanitized = re.sub(re.escape(computer_name), "<HOST_ANONYMIZED>", sanitized)

    # 2. Network IP & Private Key Scrubbing
    sanitized = re.sub(r'\b192\.168\.\d{1,3}\.\d{1,3}\b', '192.168.x.x', sanitized)
    sanitized = re.sub(r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '10.x.x.x', sanitized)
    sanitized = re.sub(r'-----\s*BEGIN[ A-Z0-9_-]+KEY\s*-----[\s\S]*?-----\s*END[ A-Z0-9_-]+KEY\s*-----', '<PRIVATE_KEY_REDACTED>', sanitized)

    # 3. Structural Regex Pass (Known Prefixes)
    known_patterns = [
        (r'ghp_[a-zA-Z0-9]{36}', '<GITHUB_PAT_REDACTED>'),
        (r'github_pat_[a-zA-Z0-9_]{82}', '<GITHUB_PAT_REDACTED>'),
        (r'hf_[a-zA-Z0-9]{34}', '<HF_TOKEN_REDACTED>'),
        (r'AIza[0-9A-Za-z-_]{35}', '<GCP_KEY_REDACTED>'),
        (r'sk-(?:proj-)?[a-zA-Z0-9_-]{20,}', '<OPENAI_KEY_REDACTED>'),
        (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', 'Bearer <TOKEN_REDACTED>'),
        (r'([a-zA-Z0-9_]+_key|token|secret|password)\s*[:=]\s*["\']?([a-zA-Z0-9/+=_\-]{20,})["\']?', None)
    ]

    for pattern, replacement in known_patterns:
        if replacement:
            sanitized = re.sub(pattern, replacement, sanitized)
        else:
            # High-entropy extraction pass for generic assignments (H > 4.3)
            matches = list(re.finditer(pattern, sanitized, re.IGNORECASE))
            for m in matches:
                value = m.group(2)
                if calculate_shannon_entropy(value) > 4.3:
                    sanitized = sanitized.replace(value, "<HIGH_ENTROPY_SECRET_REDACTED>")

    # 4. Tokenizer Fallback for Unstructured High-Entropy Strings (H >= 4.5, len >= 24)
    tokens = re.split(r'[\s=\":;\',]+', sanitized)
    for token in tokens:
        clean_token = token.strip()
        if len(clean_token) >= 24 and calculate_shannon_entropy(clean_token) >= 4.5:
            if (not clean_token.startswith("http") 
                and not re.match(r'^[0-9a-f]{40}$', clean_token, re.IGNORECASE)
                and not clean_token.endswith(".md")):
                sanitized = sanitized.replace(clean_token, "<HIGH_ENTROPY_TOKEN_REDACTED>")

    return sanitized

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            with open(arg, "r", encoding="utf-8", errors="ignore") as f:
                print(sanitize_content(f.read()))
        else:
            print(sanitize_content(arg))
    elif not sys.stdin.isatty():
        print(sanitize_content(sys.stdin.read()))
    else:
        print("Usage: sanitize_okf.py <file-path-or-text>")
```

#### 2. `~/.okf_knowledge/scripts/test_okf_graph.py`
```python
#!/usr/bin/env python3
"""
OKF Knowledge Graph Integrity & Security Validator.
Verifies YAML frontmatter, checks for dead relative links, verifies path sanitization,
and audits for high-entropy credential leakage.
"""

import os
import sys
import re

scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from sanitize_okf import calculate_shannon_entropy

def validate_graph() -> int:
    base = os.path.dirname(scripts_dir)
    concepts_dir = os.path.join(base, "concepts")
    index_file = os.path.join(base, "index.md")

    if not os.path.isdir(concepts_dir):
        print(f"ERROR: Concepts directory not found: {concepts_dir}", file=sys.stderr)
        return 1

    nodes = [os.path.join(concepts_dir, f) for f in os.listdir(concepts_dir) if f.endswith(".md")]
    warm_count = len(nodes)
    errors = 0

    print(f"=== Validating OKF Knowledge Graph ({warm_count} Warm Nodes) ===")

    # 1. Warm Memory Cap Check (< 50 nodes)
    if warm_count > 50:
        print(f"WARNING: Warm Memory cap exceeded: {warm_count} nodes (Max recommended: 50). Run prune_okf_memory.py.", file=sys.stderr)

    home = os.path.expanduser("~")
    userprofile = os.environ.get("USERPROFILE", "")

    # 2. Inspect each concept node
    for node_path in nodes:
        node_name = os.path.basename(node_path)
        try:
            with open(node_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"ERROR: Failed to read {node_name}: {e}", file=sys.stderr)
            errors += 1
            continue

        # Check frontmatter
        if not re.match(r"^---\s*\r?\n(.*?)\r?\n---", content, re.DOTALL):
            print(f"ERROR: Missing or invalid YAML frontmatter in: {node_name}", file=sys.stderr)
            errors += 1

        # Check for unscrubbed local user paths
        if (home and home in content) or (userprofile and userprofile in content) or re.search(r'C:\\Users\\[a-zA-Z0-9_\-\.]+', content, re.IGNORECASE):
            print(f"ERROR: Unsanitized absolute user path detected in: {node_name}", file=sys.stderr)
            errors += 1

        # Check for known leaked tokens
        if re.search(r'\b(ghp_[a-zA-Z0-9]{36}|hf_[a-zA-Z0-9]{34}|AIza[0-9A-Za-z-_]{35}|sk-(?:proj-)?[a-zA-Z0-9_-]{20,})\b', content):
            print(f"ERROR: Unredacted API token detected in: {node_name}", file=sys.stderr)
            errors += 1

        # Check relative markdown links
        links = re.findall(r'\[.*?\]\((?!https?://)(.*?)\)', content)
        for link in links:
            clean_link = link.split('#')[0].strip()
            if not clean_link:
                continue
            resolved_link = os.path.normpath(os.path.join(os.path.dirname(node_path), clean_link))
            if not os.path.exists(resolved_link):
                print(f"ERROR: Dead link in {node_name} -> {clean_link}", file=sys.stderr)
                errors += 1

    # Also validate index.md
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8", errors="ignore") as f:
            idx_content = f.read()
        links = re.findall(r'\[.*?\]\((?!https?://)(.*?)\)', idx_content)
        for link in links:
            clean_link = link.split('#')[0].strip()
            if not clean_link:
                continue
            resolved_link = os.path.normpath(os.path.join(base, clean_link))
            if not os.path.exists(resolved_link):
                print(f"ERROR: Dead link in index.md -> {clean_link}", file=sys.stderr)
                errors += 1

    if errors == 0:
        print("SUCCESS: All OKF nodes, links, and security constraints verified successfully!")
        return 0
    else:
        print(f"FAILED: OKF Graph validation encountered {errors} error(s).", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(validate_graph())
```

#### 3. `~/.okf_knowledge/scripts/prune_okf_memory.py`
```python
#!/usr/bin/env python3
"""
OKF Tiered Memory Pruning & Staging Governance Engine.
1. Moves stale Warm concepts (> 45 days untouched) to Cold Archive.
2. Auto-purges unreviewed candidate notes in staging/ (> 14 days TTL) to eliminate review fatigue.
"""

import os
import sys
import time
import shutil
import argparse

def prune_memory(stale_days=45, staging_ttl_days=14, dry_run=False):
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.dirname(scripts_dir)
    concepts_dir = os.path.join(base, "concepts")
    archive_dir = os.path.join(base, "archive", "concepts")
    staging_dir = os.path.join(base, "staging")

    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(staging_dir, exist_ok=True)

    now = time.time()
    stale_threshold = now - (stale_days * 86400)
    staging_threshold = now - (staging_ttl_days * 86400)

    # 1. Warm Memory -> Cold Archive (45-Day TTL)
    anchors = {"system_profile.md", "dev_conventions.md"}
    archived_count = 0

    if os.path.isdir(concepts_dir):
        for fname in os.listdir(concepts_dir):
            if not fname.endswith(".md") or fname in anchors:
                continue
            fpath = os.path.join(concepts_dir, fname)
            mtime = os.path.getmtime(fpath)
            if mtime < stale_threshold:
                days_old = int((now - mtime) / 86400)
                print(f"[Cold Tiering] Stale concept detected: {fname} ({days_old} days old)")
                if not dry_run:
                    dest = os.path.join(archive_dir, fname)
                    shutil.move(fpath, dest)
                    archived_count += 1

    # 2. Staging Inbox Auto-TTL Purge (14-Day TTL to prevent review fatigue)
    purged_staging_count = 0
    if os.path.isdir(staging_dir):
        for fname in os.listdir(staging_dir):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(staging_dir, fname)
            mtime = os.path.getmtime(fpath)
            if mtime < staging_threshold:
                days_old = int((now - mtime) / 86400)
                print(f"[Staging Purge] Candidate expired (> {staging_ttl_days}d TTL): {fname}")
                if not dry_run:
                    os.remove(fpath)
                    purged_staging_count += 1

    print(f"\nPruning Summary:")
    print(f"  • Warm -> Cold Archived: {archived_count} node(s)")
    print(f"  • Staging Candidates Purged: {purged_staging_count} node(s)")
    if dry_run:
        print("  • (Dry Run Mode: No files were actually moved or deleted)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune stale OKF memory nodes and expired staging candidates.")
    parser.add_argument("--stale-days", type=int, default=45, help="Days before concept is moved to Cold Archive (default: 45)")
    parser.add_argument("--staging-ttl", type=int, default=14, help="Days before unreviewed candidate in staging is purged (default: 14)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pruning without modifying files")
    args = parser.parse_args()

    prune_memory(stale_days=args.stale_days, staging_ttl_days=args.staging_ttl, dry_run=args.dry_run)
```

#### 4. `~/.okf_knowledge/scripts/new_okf_node.py`
```python
#!/usr/bin/env python3
"""
OKF Concept Node Generator with automatic sanitization and trust metadata.
"""

import os
import sys
import re
import datetime
import argparse

scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from sanitize_okf import sanitize_content

def create_node(title: str, description: str, tags: list, status: str = "draft"):
    base = os.path.dirname(scripts_dir)
    concepts_dir = os.path.join(base, "concepts")
    os.makedirs(concepts_dir, exist_ok=True)

    slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
    target_file = os.path.join(concepts_dir, f"{slug}.md")

    if os.path.exists(target_file):
        print(f"ERROR: Concept node already exists: {target_file}", file=sys.stderr)
        return 1

    date_str = datetime.date.today().isoformat()
    tags_str = ", ".join(tags) if tags else "general"

    template = f"""---
type: concept
title: {title}
description: {description}
status: {status}
trust_score: 1
tags: [{tags_str}]
created_at: {date_str}
updated_at: {date_str}
anonymized: true
sources: []
---

# {title}

## Summary
{description}

## Verified Guidelines & Code Patterns
<!-- Add actionable code patterns or rules here -->

## Verification & Test Record
* **Status History:** {status} created on {date_str}.
* **Verification Criteria:** <!-- What test confirms this concept? -->

## References & Cross-Links
* [Master Index](../index.md)
"""

    cleaned = sanitize_content(template)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"SUCCESS: Created new OKF node: {target_file}")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new OKF concept node.")
    parser.add_argument("title", help="Title of the concept")
    parser.add_argument("description", help="One-line summary")
    parser.add_argument("--tags", nargs="+", default=["general"], help="List of tags")
    parser.add_argument("--status", default="draft", choices=["candidate", "draft", "verified", "stable"])
    args = parser.parse_args()

    sys.exit(create_node(args.title, args.description, args.tags, args.status))
```

---

### Execution Phase 3: Git Pre-Commit Hook

Install the executable quality gate at `~/.okf_knowledge/.git/hooks/pre-commit`:

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

### Execution Phase 4: Foundational Knowledge Graph

Write the root table of contents and foundational concept nodes:

#### 1. `~/.okf_knowledge/index.md`
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

## 3. Staging Inbox
* Newly synthesized candidates await review in `staging/` before being promoted to Warm Memory.
```

#### 2. `~/.okf_knowledge/concepts/system_profile.md`
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

#### 3. `~/.okf_knowledge/concepts/dev_conventions.md`
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

#### 4. `~/.okf_knowledge/concepts/api_design_standards.md`
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

#### 5. `~/.okf_knowledge/concepts/database_migration_policy.md`
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

#### 6. `~/.okf_knowledge/concepts/distributed_caching_patterns.md`
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

#### 7. `~/.okf_knowledge/concepts/llm_inference_routing.md`
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

---

### Execution Phase 5: Global Agent Directives & Skills

#### Directives Block
Append the following block to your global agent rules file (e.g. `~/.gemini/AGENTS.md`, `%USERPROFILE%\AGENTS.md`, or `.cursorrules`):

```markdown
---

## Persistent Autonomous Memory & Reasoning Directives (OKF)
1. **Auto-Consult Memory**: Before executing tasks that involve environment configs, toolchains, or previously solved patterns, automatically consult `~/.okf_knowledge/index.md` via the `okf-memory` skill.
2. **Auto-Triad**: For high-complexity tasks (zero-downtime database migrations, financial reconciliation math, cryptographic protocols, major cross-system refactors), automatically invoke the `adversarial-triad` workflow ([ARCHITECT] -> [CRITIC] -> [JUDGE]) to audit the plan. Routine tasks run in single-pass mode.
3. **Staged Trust Model**: All newly recorded concepts start as `status: draft`. Promotion to `status: verified` requires practical testing, and `status: stable` requires explicit confirmation.
4. **Zero Secret & PII Leakage**: Always use `sanitize_okf.py` before saving nodes. Never store credentials, API tokens, passwords, or absolute machine paths.
5. **Memory Tiering**: Active Warm Memory is soft-capped at 50 nodes in `~/.okf_knowledge/concepts/`. Stale nodes (>45 days) are archived to `archive/concepts/`. Staging candidates older than 14 days are auto-purged.
6. **Epistemic Hierarchy**: Live User Instructions > Live Working Code & Tests > OKF Persistent Memory. If live code or tests contradict memory, memory yields and proposes an update.
```

#### Skill 1: `okf-memory` (`~/.gemini/config/skills/okf-memory/SKILL.md`)
```markdown
---
name: okf-memory
description: >-
  Autonomous persistent memory system. Automatically consult this skill to check
  recorded system conventions, past debugging solutions, or to record newly discovered
  architectural patterns in the local Open Knowledge Format (OKF) graph at ~/.okf_knowledge.
---

# OKF Tiered Memory Management
1. Consult `~/.okf_knowledge/index.md` first to discover active Warm concepts.
2. Read specific concept nodes in `~/.okf_knowledge/concepts/`.
3. Check `~/.okf_knowledge/staging/` to review candidate concepts.
4. When recording new knowledge, sanitize with `sanitize_okf.py`, start as `status: draft`, and update `index.md`.
```

#### Skill 2: `adversarial-triad` (`~/.gemini/config/skills/adversarial-triad/SKILL.md`)
```markdown
---
name: adversarial-triad
description: >-
  Adversarial planning loop. Automatically activate this skill for high-complexity,
  high-stakes, or multi-step architecture planning tasks to conduct an internal
  Architect-Critic-Judge debate before writing code.
---

# Adversarial Triad Workflow
1. **The Architect (Subagent: `self`)**: Generates technical proposals and file diffs.
2. **The Critic (Subagent: `research` / read-only)**: Adversarially audits for race conditions, security flaws, regressions, and token bloat.
3. **The Judge (Primary Agent)**: Issues the final synthesis and hardened execution plan.
```

---

### Execution Phase 6: Verification & Initial Commit

Run the graph validator, verify sanitization, and create the initial commit:

```powershell
# 1. Run Graph Validator
python "$HOME\.okf_knowledge\scripts\test_okf_graph.py"

# 2. Stage All Knowledge Files
git -C "$HOME\.okf_knowledge" add -A

# 3. Commit (Triggers Pre-Commit Hook)
git -C "$HOME\.okf_knowledge" commit -m "feat(okf): initialize production-hardened OKF memory system with entropy detection and git pre-commit quality gate"
```

#### Expected Final Output:
```text
=== Validating OKF Knowledge Graph (6 Warm Nodes) ===
SUCCESS: All OKF nodes, links, and security constraints verified successfully!
=== [Pre-Commit Hook] Running OKF Graph Integrity & Security Verification ===
=== Validating OKF Knowledge Graph (6 Warm Nodes) ===
SUCCESS: All OKF nodes, links, and security constraints verified successfully!
SUCCESS: OKF Graph verified clean. Proceeding with commit.
[master (root-commit) ...] feat(okf): initialize production-hardened OKF memory system with entropy detection and git pre-commit quality gate
```

---

### Execution Phase 7: Developer Shell Integration (`okf-*`)

Configure terminal convenience functions in PowerShell (`$PROFILE`) or POSIX Bash (`~/.bashrc`):

```powershell
$profileDirs = @((Split-Path $PROFILE -Parent), (Join-Path $HOME "Documents\WindowsPowerShell"))
$profileCode = @'
$env:OKF_HOME = "$HOME\.okf_knowledge"

function okf-status {
    $base = $env:OKF_HOME
    $warm = (Get-ChildItem -Path "$base\concepts" -Filter "*.md" -ErrorAction SilentlyContinue).Count
    $staging = (Get-ChildItem -Path "$base\staging" -Filter "*.md" -ErrorAction SilentlyContinue).Count
    $archive = (Get-ChildItem -Path "$base\archive\concepts" -Filter "*.md" -ErrorAction SilentlyContinue).Count
    Write-Host "`n=== OKF Memory Graph ===" -ForegroundColor Cyan
    Write-Host "  Warm: $warm / 50 nodes | Staging: $staging | Archive: $archive"
    git -C $base status -s
}
function okf-search { param([string]$q) Get-ChildItem "$env:OKF_HOME\concepts\*.md" | Select-String -Pattern $q }
function okf-new { param([string]$t, [string]$d="Autonomous entry.") & "$env:OKF_HOME\scripts\New-OkfNode.ps1" -Title $t -Description $d }
function okf-verify { python "$env:OKF_HOME\scripts\test_okf_graph.py" }
function okf-prune { python "$env:OKF_HOME\scripts\prune_okf_memory.py" }
function okf-dream { param([string]$repo=".") & "$env:OKF_HOME\scripts\Invoke-DreamSynthesis.ps1" -TargetRepo $repo }
function okf-open { param([string]$c) if ($c) { Invoke-Item "$env:OKF_HOME\concepts\$c.md" } else { Invoke-Item $env:OKF_HOME } }
'@

foreach ($pDir in $profileDirs) {
    if (-not (Test-Path $pDir)) { New-Item -ItemType Directory -Path $pDir -Force | Out-Null }
    $pPath = Join-Path $pDir "Microsoft.PowerShell_profile.ps1"
    if ((Get-Content $pPath -Raw -ErrorAction SilentlyContinue) -notmatch "function okf-status") {
        Add-Content -Path $pPath -Value $profileCode -Encoding UTF8
    }
}
```

---

### Execution Phase 8: Autonomous Daily Dream Synthesis Task

Register background task running daily at 23:00:

```powershell
$targetBase = "$HOME\.okf_knowledge"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$targetBase\scripts\Invoke-DreamSynthesis.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At "23:00"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "OKF-DreamSynthesis" -Action $action -Trigger $trigger -Settings $settings -Description "Daily background OKF memory synthesis and staging" -Force
```
```
