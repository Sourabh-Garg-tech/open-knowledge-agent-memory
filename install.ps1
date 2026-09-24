<#
.SYNOPSIS
    Open Knowledge Format (OKF) 1-Click Turnkey Installer for Windows / PowerShell.
    Deploys the complete cognitive architecture, core Python engines, starter knowledge graph,
    and Git pre-commit quality gate into $HOME\.okf_knowledge.
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Open Knowledge Agent Memory (OKF) Turnkey Installer    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$tmpDir = $null

if (-not (Test-Path (Join-Path $scriptRoot "core"))) {
    Write-Host "  + Remote execution detected. Fetching repository components..." -ForegroundColor Cyan
    $tmpDir = Join-Path ([System.IO.Path]::GetTempPath()) "okf_install_$(Get-Random)"
    $repoUrl = if ($env:OKF_REPO_URL) { $env:OKF_REPO_URL } else { "https://github.com/open-knowledge-format/open-knowledge-agent-memory.git" }
    git clone --depth 1 $repoUrl $tmpDir 2>$null
    if (Test-Path (Join-Path $tmpDir "core")) {
        $scriptRoot = $tmpDir
    } else {
        Write-Error "Failed to fetch repository components via git clone."
    }
}

$targetBase = Join-Path $HOME ".okf_knowledge"

Write-Host "[1/6] Setting up directory hierarchy at $targetBase..." -ForegroundColor Yellow
$dirs = @(
    (Join-Path $targetBase "concepts"),
    (Join-Path $targetBase "archive\concepts"),
    (Join-Path $targetBase "staging"),
    (Join-Path $targetBase "scripts")
)

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
        Write-Host "  + Created: $d" -ForegroundColor Green
    }
}

Write-Host "[2/6] Deploying core Python 3 & PowerShell engines..." -ForegroundColor Yellow
$coreSrc = Join-Path $scriptRoot "core"
if (Test-Path $coreSrc) {
    Get-ChildItem -Path $coreSrc -File | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination (Join-Path $targetBase "scripts\$($_.Name)") -Force
    }
    Write-Host "  + Engines deployed to $targetBase\scripts" -ForegroundColor Green
} else {
    Write-Error "Core scripts directory not found at $coreSrc"
}

Write-Host "[3/6] Deploying starter knowledge graph..." -ForegroundColor Yellow
$starterSrc = Join-Path $scriptRoot "starter_graph"
if (Test-Path $starterSrc) {
    # Copy index.md if not already present
    $targetIndex = Join-Path $targetBase "index.md"
    if (-not (Test-Path $targetIndex)) {
        Copy-Item -Path (Join-Path $starterSrc "index.md") -Destination $targetIndex -Force
        Write-Host "  + Created master index.md" -ForegroundColor Green
    }

    # Copy concepts if not already present
    $conceptsSrc = Join-Path $starterSrc "concepts"
    if (Test-Path $conceptsSrc) {
        Get-ChildItem -Path $conceptsSrc -Filter "*.md" | ForEach-Object {
            $destFile = Join-Path $targetBase "concepts\$($_.Name)"
            if (-not (Test-Path $destFile)) {
                Copy-Item -Path $_.FullName -Destination $destFile -Force
                Write-Host "  + Deployed concept: $($_.Name)" -ForegroundColor Green
            }
        }
    }
}

Write-Host "[4/6] Initializing Git repository and quality gate..." -ForegroundColor Yellow
$gitDir = Join-Path $targetBase ".git"
if (-not (Test-Path $gitDir)) {
    git -C $targetBase init -b master 2>$null
    Write-Host "  + Initialized Git repository on 'master'" -ForegroundColor Green
}

# Copy .gitignore
$gitignoreSrc = Join-Path $scriptRoot ".gitignore"
if (Test-Path $gitignoreSrc) {
    Copy-Item -Path $gitignoreSrc -Destination (Join-Path $targetBase ".gitignore") -Force
}

# Install pre-commit hook
$hooksDir = Join-Path $targetBase ".git\hooks"
if (-not (Test-Path $hooksDir)) { New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null }
$preCommitPath = Join-Path $hooksDir "pre-commit"
$preCommitScript = @"
#!/usr/bin/env bash
# OKF Graph Integrity & Security Pre-Commit Guard

echo "=== [Pre-Commit Hook] Running OKF Graph Integrity & Security Verification ==="

python scripts/test_okf_graph.py
EXIT_CODE=`$?

if [ `$EXIT_CODE -ne 0 ]; then
    echo "ERROR: OKF Graph validation failed! Commit aborted."
    echo "Check for dead links, unsanitized paths, or frontmatter errors before committing."
    exit 1
fi

echo "SUCCESS: OKF Graph verified clean. Proceeding with commit."
exit 0
"@
[System.IO.File]::WriteAllText($preCommitPath, ($preCommitScript -replace "`r`n", "`n"), [System.Text.Encoding]::ASCII)
Write-Host "  + Installed Git pre-commit quality gate hook" -ForegroundColor Green

Write-Host "[5/6] Deploying agent skills (if Antigravity/Gemini environment present)..." -ForegroundColor Yellow
$skillsDir = Join-Path $HOME ".gemini\config\skills"
$repoSkills = Join-Path $scriptRoot "integrations\skills"
if (Test-Path $repoSkills) {
    if (-not (Test-Path $skillsDir)) { New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null }
    Get-ChildItem -Path $repoSkills -Directory | ForEach-Object {
        $destSkill = Join-Path $skillsDir $_.Name
        if (-not (Test-Path $destSkill)) { New-Item -ItemType Directory -Path $destSkill -Force | Out-Null }
        Copy-Item -Path (Join-Path $_.FullName "SKILL.md") -Destination (Join-Path $destSkill "SKILL.md") -Force
        Write-Host "  + Deployed skill: $($_.Name)" -ForegroundColor Green
    }
}

Write-Host "[6/6] Verifying graph integrity..." -ForegroundColor Yellow
$validatorScript = Join-Path $targetBase "scripts\test_okf_graph.py"
if (Test-Path $validatorScript) {
    python $validatorScript
    if ($LASTEXITCODE -eq 0) {
        # Initial commit if repo is clean
        git -C $targetBase add -A
        $status = git -C $targetBase status --porcelain
        if ($status) {
            git -C $targetBase commit -m "feat(okf): initialize cognitive memory system" 2>$null
            Write-Host "  + Initial commit created" -ForegroundColor Green
        }
    }
}

Write-Host "[7/8] Installing PowerShell CLI shortcuts (okf-status, okf-search, etc.)..." -ForegroundColor Yellow
$profileDirs = @(
    (Split-Path $PROFILE -Parent),
    (Join-Path $HOME "Documents\WindowsPowerShell")
)
$profileCode = @'

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
'@

foreach ($pDir in $profileDirs) {
    if (-not (Test-Path $pDir)) { New-Item -ItemType Directory -Path $pDir -Force | Out-Null }
    $pPath = Join-Path $pDir "Microsoft.PowerShell_profile.ps1"
    $existing = if (Test-Path $pPath) { Get-Content $pPath -Raw } else { "" }
    if ($existing -notmatch "function okf-status") {
        Add-Content -Path $pPath -Value $profileCode -Encoding UTF8
        Write-Host "  + Added CLI functions to $pPath" -ForegroundColor Green
    } else {
        Write-Host "  + CLI functions already present in $pPath" -ForegroundColor DarkGray
    }
}

Write-Host "[8/8] Registering daily background Dream Synthesis task..." -ForegroundColor Yellow
try {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$targetBase\scripts\Invoke-DreamSynthesis.ps1`""
    $trigger = New-ScheduledTaskTrigger -Daily -At "23:00"
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    Register-ScheduledTask -TaskName "OKF-DreamSynthesis" -Action $action -Trigger $trigger -Settings $settings -Description "Daily background OKF memory synthesis and staging" -Force | Out-Null
    Write-Host "  + Registered OKF-DreamSynthesis scheduled task (Daily at 23:00)" -ForegroundColor Green
} catch {
    Write-Host "  ! Note: Could not register scheduled task (may require administrator permissions). You can run okf-dream manually." -ForegroundColor DarkYellow
}

if ($tmpDir -and (Test-Path $tmpDir)) {
    Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  SUCCESS: OKF Cognitive Memory System is 100% Deployed!   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Next Step: Add the directives block from integrations/directives/AGENTS.md"
Write-Host "to your system prompt or rules file (e.g. AGENTS.md, .cursorrules)."
Write-Host "Available CLI commands: okf-status, okf-search, okf-new, okf-verify, okf-prune, okf-dream, okf-open"
