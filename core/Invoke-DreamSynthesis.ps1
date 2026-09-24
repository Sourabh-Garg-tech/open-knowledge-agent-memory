<#
.SYNOPSIS
    Stage 2: Safely distills recent git commits and error patterns into candidate nodes in staging/.
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
