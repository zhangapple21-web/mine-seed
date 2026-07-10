# ACE Shared API Keep-Alive - Windows Runtime Script
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogFile = "$Workspace\mine_output\shared_api.log"

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

# Run shared API (background keep-alive)
Start-Process -FilePath $Python -ArgumentList "$Workspace\04_PROTOCOLS\shared_api.py" -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile
