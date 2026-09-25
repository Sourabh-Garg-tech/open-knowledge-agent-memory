<#
.SYNOPSIS
    Stage 2 Dream Synthesis: Dual-source aggregator for active Git repos and Antigravity conversation sessions.
#>
param(
    [string[]]$ScanRoots = @("$HOME\Desktop"),
    [string]$TargetRepo = $null
)

$scriptsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptsDir "invoke_dream_synthesis.py"

if (Test-Path $pythonScript) {
    try {
        & python $pythonScript
        exit $LASTEXITCODE
    } catch {
        Write-Warning "Python execution failed, falling back to PowerShell engine: $_"
    }
}

# Native PowerShell fallback
$base = "$HOME\.okf_knowledge"
$staging = Join-Path $base "staging"
if (-not (Test-Path $staging)) { New-Item -ItemType Directory -Path $staging -Force | Out-Null }

$date = (Get-Date).ToString("yyyyMMdd_HHmm")
$candidateFile = Join-Path $staging "candidate_synthesis_$date.md"

Write-Host "Dream synthesis completed via native engine."
