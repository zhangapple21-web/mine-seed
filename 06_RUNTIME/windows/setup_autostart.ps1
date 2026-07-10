# ACE Runtime - Setup Windows Auto-Start
# Run once to register ACE Runtime as auto-start on user login
# After this, Runtime starts silently every time you log into Windows
# No manual intervention needed

param(
    [string]$ChatId = $env:TG_CHAT_ID
)

$TaskName = "ACE_Runtime"
$Workspace = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$PythonExe = "python"
$ScriptPath = Join-Path $Workspace "06_RUNTIME\core\runtime_main.py"
$LogDir = Join-Path $Workspace "02_MEMORY\logs"

# Find Python in PATH or registry
$PythonPaths = @(
    "python",
    "python3",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:ProgramFiles\Python311\python.exe",
    "$env:ProgramFiles\Python310\python.exe"
)

foreach ($p in $PythonPaths) {
    try {
        $result = & $p --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PythonExe = $p
            break
        }
    } catch {
        continue
    }
}

# Build arguments
$ArgList = @("06_RUNTIME\core\runtime_main.py", "--daemon")
if ($ChatId) {
    $ArgList += "--chat-id", $ChatId
}

$ArgString = $ArgList -join " "

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "ACE Runtime Auto-Start Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Task Name:    $TaskName" -ForegroundColor Gray
Write-Host "Workspace:    $Workspace" -ForegroundColor Gray
Write-Host "Python:       $PythonExe" -ForegroundColor Gray
Write-Host "Arguments:    $ArgString" -ForegroundColor Gray
Write-Host "Logs:         $LogDir" -ForegroundColor Gray
Write-Host ""

# Create log directory if needed
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Delete existing task if exists
try {
    & schtasks /Delete /TN $TaskName /F
    Write-Host "[OK] Removed existing task" -ForegroundColor Yellow
} catch {
    # Ignore if not found
}

# Create task with highest privileges, hidden window, run whether user is logged on or not
$action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument $ArgString `
    -WorkingDirectory $Workspace

$trigger = New-ScheduledTaskTrigger -AtLogOn

$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -Hidden `
    -ExecutionTimeLimit (New-TimeSpan -Hours 24) `
    -StartWhenAvailable

$task = New-ScheduledTask `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings

try {
    Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force
    Write-Host "[OK] Task registered successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "ACE Runtime will now start AUTOMATICALLY" -ForegroundColor Green
    Write-Host "every time you log into Windows." -ForegroundColor Green
    Write-Host ""
    Write-Host "Logs will be written to:" -ForegroundColor Gray
    Write-Host "  $LogDir\runtime_YYYYMMDD.log" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To manually start now:" -ForegroundColor Gray
    Write-Host "  schtasks /Run /TN $TaskName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To stop the service:" -ForegroundColor Gray
    Write-Host "  .\stop_runtime.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To remove auto-start:" -ForegroundColor Gray
    Write-Host "  schtasks /Delete /TN $TaskName /F" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Failed to register task: $_" -ForegroundColor Red
    
    # Fallback: try with schtasks command directly
    Write-Host "[INFO] Trying fallback registration..." -ForegroundColor Yellow
    $cmdArgs = @(
        "/Create",
        "/TN", $TaskName,
        "/TR", "`"$PythonExe`" $ArgString",
        "/SC", "ONLOGON",
        "/RU", "$env:USERDOMAIN\$env:USERNAME",
        "/RL", "HIGHEST",
        "/F",
        "/V1"
    )
    
    try {
        & schtasks $cmdArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Task registered via fallback method" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Fallback also failed" -ForegroundColor Red
            Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[ERROR] Fallback error: $_" -ForegroundColor Red
    }
}