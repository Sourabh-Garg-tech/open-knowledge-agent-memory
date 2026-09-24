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
