# ACE 信号发现 - Windows 适配运行脚本
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogDir = "$Workspace\mine_output\signals"
$LogFile = "$LogDir\signal_cron.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# 加载环境变量
$EnvFile = "$Workspace\05_TOOLS\miner\miner_env.sh"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^export\s+(\w+)="?(.+?)"?$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# 运行信号发现
& $Python "$Workspace\05_TOOLS\signals\signal_discovery.py" 2>&1 | Tee-Object -FilePath $LogFile -Append
