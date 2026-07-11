# Register ACE_Heartbeat: SYSTEM account, At Startup + repeat every 15 min
# English comments only to avoid PowerShell encoding issues

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Users\User\ace_workspace\mine-seed\run_heartbeat.ps1" -WorkingDirectory "C:\Users\User\ace_workspace\mine-seed"

# Trigger 1: At system startup
$trigger1 = New-ScheduledTaskTrigger -AtStartup

# Trigger 2: One-time trigger with 15-min repetition (keeps it running every 15 min)
$trigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "ACE_Heartbeat" -Action $action -Trigger @($trigger1, $trigger2) -Settings $settings -Principal $principal -Force

Write-Host "Task registered. Verifying..."
Get-ScheduledTask -TaskName "ACE_Heartbeat" | Format-List TaskName, State, @{N="User";E={$_.Principal.UserId}}, @{N="LogonType";E={$_.Principal.LogonType}}
Get-ScheduledTask -TaskName "ACE_Heartbeat" | Select-Object -ExpandProperty Triggers | Format-List
