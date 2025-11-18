# Check what's using port 8000
Write-Host "Checking port 8000..." -ForegroundColor Yellow

$port = 8000
$connections = netstat -ano | findstr ":$port"

if ($connections) {
    Write-Host "Port $port is in use:" -ForegroundColor Red
    Write-Host $connections
    
    $pids = $connections | ForEach-Object {
        if ($_ -match '\s+(\d+)$') {
            $matches[1]
        }
    } | Sort-Object -Unique
    
    Write-Host ""
    Write-Host "Process IDs using port $port:" -ForegroundColor Yellow
    foreach ($pid in $pids) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "PID $pid : $($process.ProcessName) - $($process.Path)" -ForegroundColor Cyan
        }
    }
    
    Write-Host "`nTo kill a process, run:" -ForegroundColor Yellow
    Write-Host "taskkill /PID <PID> /F" -ForegroundColor White
} else {
    Write-Host "Port $port is available!" -ForegroundColor Green
}

