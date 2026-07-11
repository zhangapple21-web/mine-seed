# ACE Heartbeat Launcher - Windows Task Scheduler entry point
# Runs a single heartbeat beat (no loop, Task Scheduler handles repetition)
# English comments only to avoid PowerShell encoding issues

$ErrorActionPreference = "Continue"
$workspace = "C:\Users\User\ace_workspace\mine-seed"
# Use full path: SYSTEM account may not have user PATH
$python = "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe"

# Change to workspace
Set-Location $workspace

# Run single heartbeat beat
& $python "04_PROTOCOLS\heartbeat.py" 2>&1 | Out-Null

# Exit with heartbeat's exit code
exit $LASTEXITCODE
