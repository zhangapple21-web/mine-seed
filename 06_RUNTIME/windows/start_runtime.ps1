# ACE Runtime - Windows Background Launcher (PowerShell)
# Usage: .\start_runtime.ps1 [-ChatId <id>] [-Verbose]
param(
    [string]$ChatId = $env:TG_CHAT_ID,
    [switch]$Verbose
)

$Workspace = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$LogDir = Join-Path $Workspace "02_MEMORY\logs"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$PythonExe = "python"
$Cmd = "cd `"$Workspace`"; $PythonExe 06_RUNTIME\core\runtime_main.py --daemon"

if ($ChatId) {
    $Cmd += " --chat-id $ChatId"
}

if ($Verbose) {
    $Cmd += " --verbose"
    Write-Host "Starting ACE Runtime in foreground (verbose mode)..." -ForegroundColor Cyan
    Invoke-Expression $Cmd
} else {
    # Start in background using Start-Process with -WindowStyle Hidden
    $ArgList = "06_RUNTIME\core\runtime_main.py", "--daemon"
    if ($ChatId) {
        $ArgList += "--chat-id", $ChatId
    }
    
    Start-Process -FilePath $PythonExe -ArgumentList $ArgList `
        -WorkingDirectory $Workspace -WindowStyle Hidden
    
    Write-Host "ACE Runtime started in background" -ForegroundColor Green
    Write-Host "Logs: $LogDir\runtime_$(Get-Date -Format 'yyyyMMdd').log" -ForegroundColor Gray
}