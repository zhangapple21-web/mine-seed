# ACE Miner v5 - Windows Runtime Script
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogDir = "$Workspace\mine_output"
$LogFile = "$LogDir\cron.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Set environment variables (simulate source miner_env.sh)
$env:MINER_API_BASE = "http://localhost:3000/v1/chat/completions"
$env:OUTPUT_DIR = $LogDir

# Load user custom environment variables (if exists)
$EnvFile = "$Workspace\05_TOOLS\miner\miner_env.sh"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^export\s+(\w+)="?(.+?)"?$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Run miner
& $Python "$Workspace\05_TOOLS\miner\miner_24h.py" 2>&1 | Tee-Object -FilePath $LogFile -Append
