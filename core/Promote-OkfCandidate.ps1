<#
.SYNOPSIS
    PowerShell wrapper for OKF Candidate Review and Promotion.
#>
param(
    [switch]$List,
    [string]$Candidate,
    [string]$Title,
    [string]$Description = "Promoted architectural concept.",
    [string]$Content = "",
    [string[]]$Tags = @("promoted"),
    [string]$Status = "verified",
    [switch]$Keep
)

$scriptsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptsDir "promote_okf_candidate.py"

if ($List -or -not $Candidate) {
    & python $pythonScript --list
    exit $LASTEXITCODE
}

$cmdArgs = @($pythonScript, "--candidate", $Candidate, "--title", $Title, "--description", $Description, "--status", $Status)
if ($Content) { $cmdArgs += @("--content", $Content) }
if ($Keep) { $cmdArgs += "--keep" }
if ($Tags) {
    $cmdArgs += "--tags"
    $cmdArgs += $Tags
}

& python $cmdArgs
exit $LASTEXITCODE
