<#
.SYNOPSIS
    Sanitizes text or files using the hardened Python Shannon Entropy & Regex engine.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$Content
)

$scriptsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptsDir "sanitize_okf.py"

if (Test-Path $pythonScript) {
    try {
        $result = $Content | python $pythonScript
        if ($LASTEXITCODE -eq 0 -and $result) {
            return ($result -join "`n")
        }
    } catch {
        # Fallback to local regex if python call fails
    }
}

$sanitized = $Content
$userPath = [regex]::Escape($HOME)
$sanitized = $sanitized -replace $userPath, "~"
$sanitized = $sanitized -replace [regex]::Escape($env:USERPROFILE), "~"
$sanitized = $sanitized -replace "(?i)C:\\Users\\[a-zA-Z0-9_\-\.]+", "~"
if ($env:COMPUTERNAME) {
    $sanitized = $sanitized -replace [regex]::Escape($env:COMPUTERNAME), "<HOST_ANONYMIZED>"
}
$sanitized = $sanitized -replace "hf_[a-zA-Z0-9]{34}", "<HF_TOKEN_REDACTED>"
$sanitized = $sanitized -replace "ghp_[a-zA-Z0-9]{36}", "<GITHUB_PAT_REDACTED>"
$sanitized = $sanitized -replace "AIza[0-9A-Za-z-_]{35}", "<GCP_API_KEY_REDACTED>"
$sanitized = $sanitized -replace "(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}", "Bearer <TOKEN_REDACTED>"
$sanitized = $sanitized -replace "-----\s*BEGIN[ A-Z0-9_-]+KEY\s*-----[\s\S]*?-----\s*END[ A-Z0-9_-]+KEY\s*-----", "<PRIVATE_KEY_REDACTED>"
$sanitized = $sanitized -replace "\b192\.168\.\d{1,3}\.\d{1,3}\b", "192.168.x.x"
$sanitized = $sanitized -replace "\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "10.x.x.x"

return $sanitized
