# ACE Miner v5 - Windows Runtime Script
$ErrorActionPreference = "Stop"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$ScriptDir = "$Workspace\06_RUNTIME\windows"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogDir = "$Workspace\mine_output"
$LogFile = "$LogDir\cron.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$env:OUTPUT_DIR = $LogDir
$env:CLOUD_DIR = "$Workspace\cloud\miner"

& $Python "$Workspace\05_TOOLS\miner\miner_24h_free_v7.py" 2>&1 | Tee-Object -FilePath $LogFile -Append
exit $LASTEXITCODE
