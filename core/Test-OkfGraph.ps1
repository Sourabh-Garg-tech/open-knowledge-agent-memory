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

if ($errors -eq 0) {
    Write-Host "All OKF nodes and hyperlinks verified successfully!" -ForegroundColor Green
} else {
    Write-Error "Graph validation failed with $errors error(s)."
}
