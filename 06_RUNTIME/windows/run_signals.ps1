# ACE Signal Discovery - Windows Runtime Script
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$ScriptDir = "$Workspace\06_RUNTIME\windows"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogDir = "$Workspace\mine_output\signals"
$LogFile = "$LogDir\signal_cron.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Load environment variables
$EnvFile = "$Workspace\05_TOOLS\miner\miner_env.sh"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^export\s+(\w+)="?(.+?)"?$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Run signal discovery via Windows adapter
& $Python "$ScriptDir\win_run.py" "$Workspace\05_TOOLS\signals\signal_discovery.py" 2>&1 | Tee-Object -FilePath $LogFile -Append
