# Volume 6: Turnkey Replication, Bootstrap Automation, and Operational Runbook

---

## 1. 1-Click Bootstrap Automation Script (PowerShell)

Any AI agent or developer can provision a complete, production-hardened OKF system on a new Windows machine by running the following automated PowerShell script:

```powershell
<#
.SYNOPSIS
    OKF Turnkey Bootstrap Provisioner
    Instantiates the entire OKF memory graph, Python engines, PowerShell wrappers,
    Git version control, and pre-commit security gates.
#>

$ErrorActionPreference = "Stop"
$base = "$HOME\.okf_knowledge"

Write-Host "=== Initializing OKF Cognitive Architecture at $base ===" -ForegroundColor Cyan

# 1. Create Directory Hierarchy
$dirs = @(
    (Join-Path $base "concepts"),
    (Join-Path $base "archive\concepts"),
    (Join-Path $base "staging"),
    (Join-Path $base "scripts"),
    (Join-Path $base "tests")
)

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
        Write-Host "Created: $d" -ForegroundColor Green
    }
}

# 2. Initialize Git Repository
if (-not (Test-Path (Join-Path $base ".git"))) {
    git -C $base init -b master
    Write-Host "Initialized Git repository on branch 'master'." -ForegroundColor Green
}

# 3. Create .gitignore
$gitignorePath = Join-Path $base ".gitignore"
$gitignoreContent = @"
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
"@
Set-Content -Path $gitignorePath -Value $gitignoreContent -Encoding UTF8

# 4. Install Git Pre-Commit Quality Gate
$hooksDir = Join-Path $base ".git\hooks"
if (-not (Test-Path $hooksDir)) { New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null }
$preCommitPath = Join-Path $hooksDir "pre-commit"
$preCommitScript = @"
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
"@
[System.IO.File]::WriteAllText($preCommitPath, ($preCommitScript -replace "`r`n", "`n"), [System.Text.Encoding]::ASCII)
Write-Host "Installed Git pre-commit quality gate." -ForegroundColor Green

Write-Host "`n=== OKF System Bootstrap Complete! ===" -ForegroundColor Cyan
Write-Host "Deploy scripts from Volume 3 into $base\scripts\, then execute:"
Write-Host "  python $base\scripts\test_okf_graph.py"
```

---

## 2. Comprehensive Verification Test Battery

To verify that an OKF installation is completely healthy, operational, and airtight, execute the following battery of 5 tests:

### Test 1: Knowledge Graph Integrity Audit
```powershell
python "$HOME\.okf_knowledge\scripts\test_okf_graph.py"
```
* **Expected Output:**
  ```text
  === Validating OKF Knowledge Graph (6 Warm Nodes) ===
  SUCCESS: All OKF nodes, links, and security constraints verified successfully!
  ```

---

### Test 2: Shannon Entropy & Secret Sanitization
Execute this test snippet to verify that high-entropy strings, tokens, and system paths are scrubbed while normal prose is preserved:

```powershell
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path.home() / '.okf_knowledge' / 'scripts'))
import sanitize_okf

test_input = '''
API_KEY=sk-proj-DummyRandomKey9876543210ZYXWVUTSRQPONMLK
HF_TOKEN=hf_MockVendorToken1234567890abcdefghijkl
Path: C:\\Users\\johndoe\\Desktop\\secret_project
High entropy: dK3#m9!xP7$qR2*vL5^tY8@bN1&jM4~
Normal prose: Just a normal sentence describing software architecture and design patterns.
'''

sanitized = sanitize_okf.sanitize_content(test_input)
print(sanitized)
assert 'sk-proj' not in sanitized
assert 'hf_' not in sanitized
assert 'johndoe' not in sanitized
assert '<HIGH_ENTROPY' in sanitized
assert 'Normal prose' in sanitized
print('\n[PASS] Shannon entropy and secret sanitization verified!')
"
```

---

### Test 3: PowerShell Sanitizer Interop
```powershell
pwsh -File "$HOME\.okf_knowledge\scripts\Sanitize-OkfContent.ps1" -Content "API_KEY=sk-proj-DummyRandomKey9876543210ZYXWVUTSRQPONMLK"
```
* **Expected Output:**
  ```text
  API_KEY=<HIGH_ENTROPY_SECRET_REDACTED>
  ```

---

### Test 4: Cold Archiving & Staging TTL Pruning (Dry-Run)
```powershell
python "$HOME\.okf_knowledge\scripts\prune_okf_memory.py" --dry-run
```
* **Expected Output:**
  ```text
  Pruning Summary:
    • Warm -> Cold Archived: 0 node(s)
    • Staging Candidates Purged: 0 node(s)
    • (Dry Run Mode: No files were actually moved or deleted)
  ```

---

### Test 5: Git Pre-Commit Hook Interception Guard
Verify that Git actively blocks commits that contain broken links or unredacted secrets:

```powershell
# 1. Create a bad test concept with a dead link
$badFile = "$HOME\.okf_knowledge\concepts\temp_bad_test.md"
@"
---
type: concept
title: Bad Test
description: Temporary test file
status: draft
trust_score: 1
tags: [test]
created_at: 2026-09-24
updated_at: 2026-09-24
anonymized: true
sources: []
---
# Bad Test
[Dead Link](./non_existent_file.md)
"@ | Set-Content -Path $badFile -Encoding UTF8

# 2. Stage and attempt commit
git -C "$HOME\.okf_knowledge" add concepts/temp_bad_test.md
git -C "$HOME\.okf_knowledge" commit -m "test: expect failure"

# 3. Observe hook rejection, then cleanup
Remove-Item -Path $badFile -Force
git -C "$HOME\.okf_knowledge" reset HEAD concepts/temp_bad_test.md
```
* **Expected Result:** Git aborts the commit with exit code 1 and outputs `ERROR: Dead link in temp_bad_test.md -> ./non_existent_file.md`.

---

## 3. Operational Maintenance Protocols

### Protocol A: Reviewing & Promoting Staging Candidates
When background synthesis or offline distillation generates proposals in `~/.okf_knowledge/staging/`:
1. Check for files in `staging/`: `Get-ChildItem "$HOME\.okf_knowledge\staging"`
2. If a candidate is verified by the developer:
   * Move the file from `staging/` to `concepts/`.
   * Update frontmatter: change `status: candidate` to `status: verified` or `status: stable`.
   * Add a markdown link into `~/.okf_knowledge/index.md`.
   * Commit the change to Git.
3. If a candidate is uninteresting or irrelevant:
   * Ignore it. The `prune_okf_memory.py` engine will automatically delete candidates older than 14 days.

### Protocol B: Managing the 50-Node Warm Budget
If `test_okf_graph.py` emits a warning that the Warm Memory cap is approaching 50 nodes:
1. Run `python "$HOME\.okf_knowledge\scripts\prune_okf_memory.py" --dry-run` to see candidates for archiving.
2. Run `python "$HOME\.okf_knowledge\scripts\prune_okf_memory.py"` (without `--dry-run`) to relocate stale nodes to `archive/concepts/`.
3. Commit the archived nodes to Git:
   ```powershell
   git -C "$HOME\.okf_knowledge" add -A
   git -C "$HOME\.okf_knowledge" commit -m "chore(okf): relocate stale nodes to cold archive"
   ```

### Protocol C: Disaster Recovery & Rollback
Because OKF is backed by a local Git repository:
* To inspect changes: `git -C "$HOME\.okf_knowledge" log -p -n 3`
* To revert a corrupted concept: `git -C "$HOME\.okf_knowledge" checkout HEAD -- concepts/target.md`
* To reset uncommitted experiments: `git -C "$HOME\.okf_knowledge" restore .`

### Protocol D: Fast Shell Navigation & Operations (okf-*)
Loaded into $PROFILE or ~/.bashrc:
* okf-status: Visual terminal dashboard showing Warm/Staging/Archive counts, health, and Git status.
* okf-search "<query>": Greps across concepts.
* okf-new "<Title>": Scaffolds a schema-compliant node.
* okf-verify: Validates graph links and Shannon entropy.
* okf-prune: Runs TTL archiving and purge.
* okf-dream [repoPath]: Triggers background commit synthesis into staging.
* okf-open [concept]: Opens concept file in editor.

### Protocol E: Autonomous Daily Dream Synthesis
* **Windows Task Scheduler:** Registered as OKF-DreamSynthesis executing Invoke-DreamSynthesis.ps1 daily at 23:00 (hidden).
* **Linux Cron:** Add   23 * * * python3 ~/.okf_knowledge/scripts/prune_okf_memory.py to crontab.
