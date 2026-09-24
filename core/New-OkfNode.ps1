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
