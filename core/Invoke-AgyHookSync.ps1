<#
.SYNOPSIS
    Antigravity Lifecycle Hook Handler Wrapper: Pipes Antigravity stdin to agy_hook_sync.py.
#>
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptsDir "agy_hook_sync.py"

try {
    $inputJson = [Console]::In.ReadToEnd()
    if ($inputJson -and (Test-Path $pythonScript)) {
        $result = $inputJson | python $pythonScript 2>$null
        if ($result) {
            Write-Output $result
            exit 0
        }
    }
} catch {
    # Non-blocking, failsafe
}

Write-Output "{}"
