# ACE Windows 每日自主循环 - Task Scheduler 配置脚本
# 以管理员身份运行 PowerShell 后执行此脚本

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$ScriptDir = "$Workspace\06_RUNTIME\windows"

# 1. 矿场 v5 — 每4小时
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_miner.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 4) -RepetitionDuration (New-TimeSpan -Days 3650)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "ACE_Miner_v5" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

# 2. 信号发现 — 每6小时
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_signals.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(10) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 3650)
Register-ScheduledTask -TaskName "ACE_Signal_Discovery" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

# 3. 档案官 — 每天 20:04
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_archivist.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At "20:04"
Register-ScheduledTask -TaskName "ACE_Archivist" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

# 4. 共享API保活 — 开机启动 + 每分钟检查
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_shared_api.ps1`""
$TriggerBoot = New-ScheduledTaskTrigger -AtLogOn
$TriggerMin = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 3650)
Register-ScheduledTask -TaskName "ACE_SharedAPI" -Action $Action -Trigger $TriggerBoot,$TriggerMin -Principal $Principal -Settings $Settings -Force

# 5. 跨机心跳 — 每小时
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_heartbeat.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(15) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)
Register-ScheduledTask -TaskName "ACE_Heartbeat" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

Write-Host "ACE Windows 自主循环任务已配置完成！"
Write-Host "打开 任务计划程序（taskschd.msc）查看和管理任务。"
