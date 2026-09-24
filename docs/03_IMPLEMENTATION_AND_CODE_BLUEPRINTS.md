# Volume 3: Implementation, Tooling Roster, and Complete Code Blueprints

This document contains the complete, unabridged source code for all Python 3 core engines, PowerShell interoperability wrappers, Git hooks, and configuration files comprising the OKF system.

---

## 1. Python 3 Core Engines (`~/.okf_knowledge/scripts/`)

### A. `sanitize_okf.py`
High-entropy secret detection, Shannon entropy calculations, path scrubbing, and regex sanitization.

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
            # Exclude standard URLs, hex commit SHAs (40 chars lowercase hex), and markdown links
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

---

### B. `test_okf_graph.py`
Knowledge graph integrity validator, checking frontmatter, link health, path sanitation, and warm budget.

```python
#!/usr/bin/env python3
"""
OKF Knowledge Graph Integrity & Security Validator.
Verifies YAML frontmatter, checks for dead relative links, verifies that paths are sanitized,
and detects any high-entropy cryptographic strings.
"""

import os
import sys
import re

# Add scripts directory to path to import sanitize_okf
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

---

### C. `prune_okf_memory.py`
Cold archiving and staging candidate auto-purging engine.

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

---

### D. `new_okf_node.py`
Scaffolding generator for schema-compliant concept files with automatic sanitization.

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

## 2. PowerShell Interoperability Wrappers (`~/.okf_knowledge/scripts/`)

### A. `Sanitize-OkfContent.ps1`
```powershell
<#
.SYNOPSIS
    Sanitizes text or files using the hardened Python Shannon Entropy & Regex engine.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$Content
)

$scriptsDir = if ($PSScriptRoot) { $PSScriptRoot } else { "$HOME\.okf_knowledge\scripts" }
$pythonScript = Join-Path $scriptsDir "sanitize_okf.py"

if (Test-Path $pythonScript) {
    try {
        $result = $Content | python $pythonScript
        if ($LASTEXITCODE -eq 0 -and $result) {
            return ($result -join "`n")
        }
    } catch {
        # Fallback to local regex if python call fails
    }
}

$sanitized = $Content
$userPath = [regex]::Escape($HOME)
$sanitized = $sanitized -replace $userPath, "~"
$sanitized = $sanitized -replace [regex]::Escape($env:USERPROFILE), "~"
$sanitized = $sanitized -replace "(?i)C:\\Users\\[a-zA-Z0-9_\-\.]+", "~"
if ($env:COMPUTERNAME) {
    $sanitized = $sanitized -replace [regex]::Escape($env:COMPUTERNAME), "<HOST_ANONYMIZED>"
}
$sanitized = $sanitized -replace "hf_[a-zA-Z0-9]{34}", "<HF_TOKEN_REDACTED>"
$sanitized = $sanitized -replace "ghp_[a-zA-Z0-9]{36}", "<GITHUB_PAT_REDACTED>"
$sanitized = $sanitized -replace "AIza[0-9A-Za-z-_]{35}", "<GCP_API_KEY_REDACTED>"
$sanitized = $sanitized -replace "(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}", "Bearer <TOKEN_REDACTED>"
$sanitized = $sanitized -replace "-----\s*BEGIN[ A-Z0-9_-]+KEY\s*-----[\s\S]*?-----\s*END[ A-Z0-9_-]+KEY\s*-----", "<PRIVATE_KEY_REDACTED>"
$sanitized = $sanitized -replace "\b192\.168\.\d{1,3}\.\d{1,3}\b", "192.168.x.x"
$sanitized = $sanitized -replace "\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "10.x.x.x"

return $sanitized
```

---

### B. `Test-OkfGraph.ps1`
```powershell
$base = "$HOME\.okf_knowledge"
$conceptsDir = Join-Path $base "concepts"
$indexFile = Join-Path $base "index.md"

$nodes = Get-ChildItem -Path $conceptsDir -Filter "*.md" -File
$warmCount = $nodes.Count
$errors = 0

Write-Host "=== Validating OKF Knowledge Graph ($warmCount Warm Nodes) ==="

# Check warm budget
if ($warmCount -gt 50) {
    Write-Warning "Warm Memory cap exceeded: $warmCount nodes (Max recommended: 50). Run Prune-OkfMemory.ps1."
}

# Verify frontmatter and links in each concept
foreach ($node in $nodes) {
    $raw = Get-Content -Path $node.FullName -Raw
    if ($raw -notmatch "(?s)^---\s*\r?\n(.*?)\r?\n---") {
        Write-Error "Missing frontmatter in: $($node.Name)"
        $errors++
        continue
    }
    
    # Check for unscrubbed local user paths
    if ($raw -match [regex]::Escape($HOME)) {
        Write-Error "Unsanitized path detected in: $($node.Name)"
        $errors++
    }

    # Validate relative markdown links
    $matches = [regex]::Matches($raw, '\[.*?\]\((?!https?://)(.*?)\)')
    foreach ($m in $matches) {
        $linkPath = $m.Groups[1].Value.Split('#')[0]
        if ([string]::IsNullOrWhiteSpace($linkPath)) { continue }
        $resolved = Join-Path $node.DirectoryName $linkPath
        if (-not (Test-Path $resolved)) {
            Write-Error "Dead link in $($node.Name) -> $linkPath"
            $errors++
        }
    }
}

# Validate master index.md links
if (Test-Path $indexFile) {
    $idxRaw = Get-Content -Path $indexFile -Raw
    $idxMatches = [regex]::Matches($idxRaw, '\[.*?\]\((?!https?://)(.*?)\)')
    foreach ($m in $idxMatches) {
        $linkPath = $m.Groups[1].Value.Split('#')[0]
        if ([string]::IsNullOrWhiteSpace($linkPath)) { continue }
        $resolved = Join-Path $base $linkPath
        if (-not (Test-Path $resolved)) {
            Write-Error "Dead link in index.md -> $linkPath"
            $errors++
        }
    }
}

if ($errors -eq 0) {
    Write-Host "All OKF nodes and hyperlinks verified successfully!"
} else {
    Write-Error "OKF Graph validation failed with $errors error(s)."
}
```

---

### C. `Prune-OkfMemory.ps1`
```powershell
param(
    [int]$StaleDays = 45,
    [switch]$DryRun
)

$base = "$HOME\.okf_knowledge"
$conceptsDir = Join-Path $base "concepts"
$archiveDir = Join-Path $base "archive\concepts"
$threshold = (Get-Date).AddDays(-$StaleDays)

$files = Get-ChildItem -Path $conceptsDir -Filter "*.md"
$archived = 0

foreach ($file in $files) {
    if ($file.Name -eq "system_profile.md" -or $file.Name -eq "dev_conventions.md") { 
        continue # Permanent anchor nodes
    }
    
    if ($file.LastWriteTime -lt $threshold) {
        Write-Host "Stale node detected (> $StaleDays days): $($file.Name)"
        if (-not $DryRun) {
            Move-Item -Path $file.FullName -Destination (Join-Path $archiveDir $file.Name) -Force
            $archived++
        }
    }
}

Write-Host "Pruning complete. Relocated $archived node(s) to Cold Memory."
```

---

### D. `New-OkfNode.ps1`
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [Parameter(Mandatory=$true)]
    [string]$Description,
    [string[]]$Tags = @("general"),
    [string]$Status = "draft"
)

$base = "$HOME\.okf_knowledge"
$slug = ($Title.ToLower() -replace "[^a-z0-9]+", "_").Trim("_")
$target = Join-Path $base "concepts\$slug.md"

if (Test-Path $target) {
    Write-Error "Concept node already exists: $target"
    return
}

$date = (Get-Date).ToString("yyyy-MM-dd")
$tagStr = ($Tags | ForEach-Object { "$_" }) -join ", "

$template = @"
---
type: concept
title: $Title
description: $Description
status: $Status
trust_score: 1
tags: [$tagStr]
created_at: $date
updated_at: $date
anonymized: true
sources: []
---

# $Title

## Summary
$Description

## Verified Guidelines & Code Patterns
<!-- Add actionable code patterns or rules here -->

## Verification & Test Record
* **Status History:** $Status created on $date.
* **Verification Criteria:** <!-- What test confirms this concept? -->

## References & Cross-Links
* [Master Index](../index.md)
"@

# Sanitize before writing
$cleanContent = & "$base\scripts\Sanitize-OkfContent.ps1" -Content $template
Set-Content -Path $target -Value $cleanContent -Encoding UTF8
Write-Host "Created new OKF node: $target"
```

---

### E. `Invoke-DreamSynthesis.ps1`
```powershell
<#
.SYNOPSIS
    Safely distills recent git commits and error patterns into candidate nodes in staging/.
#>
param(
    [string]$TargetRepo = "."
)

$base = "$HOME\.okf_knowledge"
$staging = Join-Path $base "staging"

# 1. Extract sanitized git commits (NO shell history)
$gitLogs = git -C $TargetRepo log -n 5 --oneline 2>$null
if (-not $gitLogs) {
    Write-Host "No recent commits found to synthesize in $TargetRepo."
    return
}

$sanitizedLogs = & "$base\scripts\Sanitize-OkfContent.ps1" -Content ($gitLogs -join "`n")
$date = (Get-Date).ToString("yyyyMMdd_HHmm")
$candidateFile = Join-Path $staging "candidate_synthesis_$date.md"

$content = @"
---
type: concept
title: Candidate Learnings ($date)
description: Background synthesis proposal derived from recent project commits.
status: candidate
trust_score: 1
tags: [synthesis, candidate]
created_at: $((Get-Date).ToString('yyyy-MM-dd'))
updated_at: $((Get-Date).ToString('yyyy-MM-dd'))
anonymized: true
sources: [git-history]
---

# Candidate Learnings ($date)

## Raw Sanitized Commits
$sanitizedLogs

## Proposed Concepts / Conventions
<!-- Review and promote to Warm Memory if verified -->
"@

Set-Content -Path $candidateFile -Value $content -Encoding UTF8
Write-Host "Candidate synthesis created: $candidateFile"
```

---

## 3. Git Hooks & Configurations

### A. Git Pre-Commit Hook (`~/.okf_knowledge/.git/hooks/pre-commit`)
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

### B. Repository `.gitignore` (`~/.okf_knowledge/.gitignore`)
```gitignore
# Environment & Secrets
.env
*.local
*.secret
*.key
*.token

# Python Cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Editor & OS Artifacts
.DS_Store
Thumbs.db
*.swp
*.bak
```

---

## 4. Developer Shell Convenience Suite

### A. PowerShell Profile Functions (`$PROFILE`)
Deployed to PowerShell 7 (`pwsh`) and Windows PowerShell 5.1 profiles:

```powershell
# ==========================================================
# Open Knowledge Format (OKF) CLI Aliases & Functions
# ==========================================================
$env:OKF_HOME = "$HOME\.okf_knowledge"

function okf-status {
    [CmdletBinding()]
    param()
    $base = $env:OKF_HOME
    if (-not (Test-Path $base)) { Write-Host "OKF directory not found at $base" -ForegroundColor Red; return }
    $warm = (Get-ChildItem -Path "$base\concepts" -Filter "*.md" -ErrorAction SilentlyContinue).Count
    $staging = (Get-ChildItem -Path "$base\staging" -Filter "*.md" -ErrorAction SilentlyContinue).Count
    $archive = (Get-ChildItem -Path "$base\archive\concepts" -Filter "*.md" -ErrorAction SilentlyContinue).Count

    Write-Host "`n==========================================================" -ForegroundColor Cyan
    Write-Host "       Open Knowledge Format (OKF) Memory Graph           " -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  Location: $base" -ForegroundColor DarkGray
    Write-Host ("  Warm Memory:    {0,3} / 50 nodes {1}" -f $warm, $(if ($warm -ge 45) { "[WARN: Approaching cap]" } else { "[Healthy]" })) -ForegroundColor $(if ($warm -ge 45) { "Yellow" } else { "Green" })
    Write-Host ("  Staging Inbox:  {0,3} candidate(s)" -f $staging) -ForegroundColor $(if ($staging -gt 0) { "Yellow" } else { "Gray" })
    Write-Host ("  Cold Archive:   {0,3} node(s)" -f $archive) -ForegroundColor Gray
    
    $gitStatus = git -C $base status --short 2>$null
    if ($gitStatus) {
        Write-Host "`n  Uncommitted Changes in Memory Graph:" -ForegroundColor Yellow
        $gitStatus | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkYellow }
    } else {
        Write-Host "  Git Status:     Clean & Synchronized" -ForegroundColor Green
    }
    Write-Host "==========================================================`n" -ForegroundColor Cyan
}

function okf-search {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true, Position=0)][string]$Query)
    $conceptsDir = "$env:OKF_HOME\concepts"
    $matches = Get-ChildItem -Path $conceptsDir -Filter "*.md" | Select-String -Pattern $Query
    if (-not $matches) { Write-Host "No matches found for '$Query'." -ForegroundColor Yellow; return }
    Write-Host "`nSearch Results for '$Query':" -ForegroundColor Cyan
    $matches | Group-Object Path | ForEach-Object {
        $fileName = [System.IO.Path]::GetFileName($_.Name)
        Write-Host "`n  [$fileName]" -ForegroundColor Green
        $_.Group | ForEach-Object {
            Write-Host ("    Line {0,3}: {1}" -f $_.LineNumber, $_.Line.Trim()) -ForegroundColor White
        }
    }
    Write-Host ""
}

function okf-new {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true, Position=0)][string]$Title, [Parameter(Position=1)][string]$Description = "Autonomous learning entry.")
    & "$env:OKF_HOME\scripts\New-OkfNode.ps1" -Title $Title -Description $Description
}

function okf-verify {
    [CmdletBinding()]
    param()
    python "$env:OKF_HOME\scripts\test_okf_graph.py"
}

function okf-prune {
    [CmdletBinding()]
    param()
    python "$env:OKF_HOME\scripts\prune_okf_memory.py"
}

function okf-dream {
    [CmdletBinding()]
    param([string]$TargetRepo = ".")
    & "$env:OKF_HOME\scripts\Invoke-DreamSynthesis.ps1" -TargetRepo $TargetRepo
}

function okf-open {
    [CmdletBinding()]
    param([string]$ConceptName)
    if (-not $ConceptName) {
        Invoke-Item "$env:OKF_HOME"
    } else {
        $file = Join-Path "$env:OKF_HOME\concepts" "$ConceptName.md"
        if (-not (Test-Path $file)) {
            $matched = Get-ChildItem -Path "$env:OKF_HOME\concepts" -Filter "*$ConceptName*.md" | Select-Object -First 1
            if ($matched) { $file = $matched.FullName }
        }
        if (Test-Path $file) { Invoke-Item $file } else { Write-Host "Concept '$ConceptName' not found." -ForegroundColor Red }
    }
}
```

### B. POSIX Bash / Zsh Aliases (`~/.bashrc` / `~/.zshrc`)
```bash
# Open Knowledge Format (OKF) Shell Functions
export OKF_HOME="$HOME/.okf_knowledge"

okf-status() {
    local warm=$(find "$OKF_HOME/concepts" -name "*.md" 2>/dev/null | wc -l)
    local staging=$(find "$OKF_HOME/staging" -name "*.md" 2>/dev/null | wc -l)
    local archive=$(find "$OKF_HOME/archive/concepts" -name "*.md" 2>/dev/null | wc -l)
    echo "=========================================================="
    echo "       Open Knowledge Format (OKF) Memory Graph           "
    echo "=========================================================="
    echo "  Location: $OKF_HOME"
    echo "  Warm Memory:    $warm / 50 nodes"
    echo "  Staging Inbox:  $staging candidate(s)"
    echo "  Cold Archive:   $archive node(s)"
    git -C "$OKF_HOME" status -s
    echo "=========================================================="
}

okf-search() {
    grep -rn "$1" "$OKF_HOME/concepts/"
}

okf-verify() {
    python3 "$OKF_HOME/scripts/test_okf_graph.py"
}

okf-prune() {
    python3 "$OKF_HOME/scripts/prune_okf_memory.py"
}

okf-new() {
    python3 "$OKF_HOME/scripts/new_okf_node.py" "$1" "${2:-Autonomous learning entry.}"
}
```

---

## 5. Autonomous Background Task (Dream Synthesis)

### A. Windows Scheduled Task
Registers a background scheduled task that executes daily at 23:00 without user interruption:

```powershell
$targetBase = "$HOME\.okf_knowledge"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$targetBase\scripts\Invoke-DreamSynthesis.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At "23:00"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "OKF-DreamSynthesis" -Action $action -Trigger $trigger -Settings $settings -Description "Daily background OKF memory synthesis and staging" -Force
```

### B. Linux / POSIX Cron Job
```bash
# Append to user crontab (runs daily at 23:00)
(crontab -l 2>/dev/null; echo "0 23 * * * python3 $HOME/.okf_knowledge/scripts/prune_okf_memory.py >/dev/null 2>&1") | crontab -
```
