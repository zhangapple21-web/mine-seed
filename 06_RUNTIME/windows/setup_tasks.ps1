# ACE Windows Daily Loop - Task Scheduler Configuration Script
# Run PowerShell as Administrator to execute this script

$Workspace = "C:\Users\User\ace_workspace\mine-seed"
$ScriptDir = "$Workspace\06_RUNTIME\windows"

# 1. Miner v5 - Every 4 hours
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_miner.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 4) -RepetitionDuration (New-TimeSpan -Days 3650)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "ACE_Miner_v5" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

# 2. Signal Discovery - Every 6 hours
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_signals.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(10) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 3650)
Register-ScheduledTask -TaskName "ACE_Signal_Discovery" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

# 3. Archivist - Daily at 20:04
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_archivist.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At "20:04"
Register-ScheduledTask -TaskName "ACE_Archivist" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

# 4. Shared API Keep-Alive - On boot + every minute check
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_shared_api.ps1`""
$TriggerBoot = New-ScheduledTaskTrigger -AtLogOn
$TriggerMin = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 3650)
Register-ScheduledTask -TaskName "ACE_SharedAPI" -Action $Action -Trigger $TriggerBoot,$TriggerMin -Principal $Principal -Settings $Settings -Force

# 5. Heartbeat - Every hour
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptDir\run_heartbeat.ps1`""
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(15) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)
Register-ScheduledTask -TaskName "ACE_Heartbeat" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

Write-Host "ACE Windows Daily Loop Tasks configured successfully!"
Write-Host "Open Task Scheduler (taskschd.msc) to view and manage tasks."
