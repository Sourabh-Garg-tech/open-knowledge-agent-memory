<#
.SYNOPSIS
    Stage 2 Dream Synthesis: Scans active project repositories, aggregates recent commits (last 24 hours),
    sanitizes PII/credentials, and stages candidate nodes in staging/ with 14-day auto-TTL.
#>
param(
    [string[]]$ScanRoots = @("$HOME\Desktop"),
    [string]$TargetRepo = $null
)

$base = "$HOME\.okf_knowledge"
$staging = Join-Path $base "staging"
if (-not (Test-Path $staging)) {
    New-Item -ItemType Directory -Path $staging -Force | Out-Null
}

$gitRepos = @()

if ($TargetRepo -and (Test-Path $TargetRepo)) {
    $gitRepos += (Get-Item $TargetRepo)
} else {
    foreach ($root in $ScanRoots) {
        if (Test-Path $root) {
            $found = Get-ChildItem -Path $root -Directory -Recurse -Depth 3 -Filter ".git" -Force -ErrorAction SilentlyContinue |
                     Where-Object { $_.FullName -notmatch "node_modules|\.venv|\.git\\modules" } |
                     Select-Object -ExpandProperty Parent
            if ($found) { $gitRepos += $found }
        }
    }
}

if (-not $gitRepos -or $gitRepos.Count -eq 0) {
    Write-Host "No git repositories found to scan."
    return
}

# 1. Collect recent commits from all discovered repositories (last 24 hours)
$aggregatedLogs = [System.Collections.Generic.List[string]]::new()
$repoCountWithCommits = 0

foreach ($repo in $gitRepos) {
    $commits = git -C $repo.FullName log --since="24 hours ago" --format="%h - %s (%cd)" --date=short 2>$null
    if ($commits) {
        $repoCountWithCommits++
        $aggregatedLogs.Add("### Repository: $($repo.Name)")
        foreach ($c in $commits) {
            $aggregatedLogs.Add("- $c")
        }
        $aggregatedLogs.Add("")
    }
}

if ($aggregatedLogs.Count -eq 0) {
    Write-Host "No recent commits in the last 24 hours across $($gitRepos.Count) repositories."
    return
}

$rawText = $aggregatedLogs -join "`n"
$sanitizedLogs = & "$base\scripts\Sanitize-OkfContent.ps1" -Content $rawText

$date = (Get-Date).ToString("yyyyMMdd_HHmm")
$candidateFile = Join-Path $staging "candidate_synthesis_$date.md"

$content = @"
---
type: concept
title: Candidate Learnings ($date)
description: Background dream synthesis proposal derived from recent project commits.
status: candidate
trust_score: 1
tags: [synthesis, candidate]
created_at: $((Get-Date).ToString('yyyy-MM-dd'))
updated_at: $((Get-Date).ToString('yyyy-MM-dd'))
anonymized: true
sources: [git-history]
---

# Candidate Learnings ($date)

## Raw Sanitized Commits ($repoCountWithCommits Repositories)
$sanitizedLogs

## Proposed Concepts / Conventions
<!-- Review and promote to Warm Memory (~/.okf_knowledge/concepts/) if verified -->
"@

Set-Content -Path $candidateFile -Value $content -Encoding UTF8
Write-Host "Candidate synthesis created: $candidateFile"

# 2. Prune staging candidates older than 14 days (TTL)
$cutoff = (Get-Date).AddDays(-14)
Get-ChildItem -Path $staging -Filter "candidate_*.md" -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt $cutoff } |
    ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "Pruned expired staging candidate: $($_.Name)"
    }

# 3. Commit to .okf_knowledge
try {
    git -C $base add "staging/" 2>$null
    git -C $base commit -m "chore(dream): synthesize candidate learnings for $date" 2>$null
} catch {
    # Commit failure is non-fatal
}
