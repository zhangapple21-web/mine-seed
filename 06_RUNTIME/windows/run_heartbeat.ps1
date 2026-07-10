# ACE Cross-Machine Heartbeat - Windows Runtime Script
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogFile = "$Workspace\mine_output\lab_ntfy.log"

New-Item -ItemType Directory -Force -Path "$Workspace\mine_output" | Out-Null

# Load environment variables
$EnvFile = "$Workspace\05_TOOLS\miner\miner_env.sh"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^export\s+(\w+)="?(.+?)"?$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Send heartbeat
& $Python "$Workspace\04_PROTOCOLS\lab_ntfy.py" ping 2>&1 | Tee-Object -FilePath $LogFile -Append
