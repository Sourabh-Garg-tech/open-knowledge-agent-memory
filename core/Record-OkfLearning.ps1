<#
.SYNOPSIS
    Autonomous OKF Ingestion Engine: Creates, sanitizes, indexes, and commits newly learned concepts.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [Parameter(Mandatory=$true)]
    [string]$Description,
    [Parameter(Mandatory=$true)]
    [string]$Content,
    [string[]]$Tags = @("general"),
    [string]$Status = "draft",
    [string[]]$Sources = @("agent-session")
)

$ErrorActionPreference = "Stop"
$base = "$HOME\.okf_knowledge"
$conceptsDir = Join-Path $base "concepts"
$indexFile = Join-Path $base "index.md"
$slug = ($Title.ToLower() -replace "[^a-z0-9]+", "_").Trim("_")
$targetFile = Join-Path $conceptsDir "$slug.md"

# 1. Warm Memory Cap Check (< 50 nodes)
$warmNodes = Get-ChildItem -Path $conceptsDir -Filter "*.md" -ErrorAction SilentlyContinue
if ($warmNodes -and $warmNodes.Count -ge 50 -and -not (Test-Path $targetFile)) {
    Write-Warning "Warm Memory cap (50 nodes) reached. Running auto-prune before writing..."
    & "$base\scripts\Prune-OkfMemory.ps1"
}

$date = (Get-Date).ToString("yyyy-MM-dd")
$tagStr = ($Tags | ForEach-Object { "$_" }) -join ", "
$sourceStr = ($Sources | ForEach-Object { "$_" }) -join ", "

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
sources: [$sourceStr]
---

# $Title

## Summary
$Description

## Verified Guidelines & Code Patterns
$Content

## Verification & Test Record
* **Status History:** $Status created on $date.
* **Verification Criteria:** Turn execution verified via agent testing.

## References & Cross-Links
* [Master Index](../index.md)
"@

# 2. Sanitize content using Shannon Entropy & Regex engine
$cleanContent = & "$base\scripts\Sanitize-OkfContent.ps1" -Content $template
Set-Content -Path $targetFile -Value $cleanContent -Encoding UTF8
Write-Host "Created/Updated OKF node: $targetFile"

# 3. Update index.md if link is not present
if (Test-Path $indexFile) {
    $indexContent = Get-Content -Path $indexFile -Raw -Encoding UTF8
    $relativeLink = "./concepts/$slug.md"
    if ($indexContent -notmatch [regex]::Escape($relativeLink)) {
        $newEntry = "* [$Title]($relativeLink) — $Description"
        if ($indexContent -match "(?s)(## 1\. Warm Memory Graph \(Active Concepts\)\r?\n)(.*?)((\r?\n## |\Z))") {
            $updatedIndex = $indexContent -replace "(?s)(## 1\. Warm Memory Graph \(Active Concepts\)\r?\n.*?)(\r?\n## )", "`$1$newEntry`r`n`$2"
            if ($updatedIndex -ne $indexContent) {
                Set-Content -Path $indexFile -Value $updatedIndex -Encoding UTF8
                Write-Host "Updated index.md with new concept link: $slug"
            }
        }
    }
}

# 4. Atomic Git commit in .okf_knowledge
try {
    git -C $base add "concepts/$slug.md" "index.md" 2>$null
    git -C $base commit -m "feat(memory): auto-record $slug" 2>$null
    Write-Host "Committed changes to .okf_knowledge repository."
} catch {
    Write-Warning "Could not commit to git: $_"
}
