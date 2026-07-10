# Stop ACE Runtime daemon
$Processes = Get-Process | Where-Object { $_.ProcessName -match "python" -and $_.CommandLine -match "runtime_main.py" }

if ($Processes) {
    foreach ($proc in $Processes) {
        Stop-Process -Id $proc.Id -Force
        Write-Host "Stopped PID $($proc.Id)" -ForegroundColor Green
    }
} else {
    Write-Host "No ACE Runtime process found" -ForegroundColor Yellow
}