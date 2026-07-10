# ACE 共享API保活 - Windows 适配运行脚本
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"
$LogFile = "$Workspace\mine_output\shared_api.log"

New-Item -ItemType Directory -Force -Path "$Workspace\mine_output" | Out-Null

# 加载环境变量
$EnvFile = "$Workspace\05_TOOLS\miner\miner_env.sh"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^export\s+(\w+)="?(.+?)"?$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# 运行共享API（后台保活）
Start-Process -FilePath $Python -ArgumentList "$Workspace\04_PROTOCOLS\shared_api.py" -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile
