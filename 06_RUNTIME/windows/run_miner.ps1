# ACE 矿场 v5 - Windows 适配运行脚本
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogDir = "$Workspace\mine_output"
$LogFile = "$LogDir\cron.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# 设置环境变量（模拟 source miner_env.sh）
$env:MINER_API_BASE = "http://localhost:3000/v1/chat/completions"
$env:OUTPUT_DIR = $LogDir

# 加载用户自定义环境变量（如果存在）
$EnvFile = "$Workspace\05_TOOLS\miner\miner_env.sh"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^export\s+(\w+)="?(.+?)"?$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# 运行矿场
& $Python "$Workspace\05_TOOLS\miner\miner_24h.py" 2>&1 | Tee-Object -FilePath $LogFile -Append
