# ACE 档案官 - Windows 适配运行脚本
$ErrorActionPreference = "Continue"

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$Python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"

# 加载环境变量
$EnvFile = "$Workspace\05_TOOLS\miner\miner_env.sh"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^export\s+(\w+)="?(.+?)"?$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# 运行档案官
& $Python "$Workspace\05_TOOLS\memory\archivist.py" 2>&1
