# ACE Free Zone Daemon - Stop Script
# Stops the 24h free zone daemon

Write-Host "Stopping ACE Free Zone Daemon..." -ForegroundColor Yellow

$daemonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match "free_zone" -or $_.CommandLine -match "daemon.py"
}

if ($daemonProcesses) {
    foreach ($proc in $daemonProcesses) {
        Write-Host "  Stopping PID: $($proc.Id)" -ForegroundColor Cyan
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "Free Zone Daemon stopped." -ForegroundColor Green
} else {
    Write-Host "No Free Zone Daemon process found." -ForegroundColor Gray
}