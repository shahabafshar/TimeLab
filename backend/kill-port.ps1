# Kill process using port 8000
param(
    [int]$Port = 8000
)

Write-Host "Finding process using port $Port..." -ForegroundColor Yellow

$connections = netstat -ano | findstr ":$Port" | findstr "LISTENING"

if ($connections) {
    $pids = $connections | ForEach-Object {
        if ($_ -match '\s+(\d+)$') {
            $matches[1]
        }
    } | Sort-Object -Unique
    
    foreach ($pid in $pids) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Killing PID $pid : $($process.ProcessName)" -ForegroundColor Red
            taskkill /PID $pid /F
        }
    }
    Write-Host "Port $Port is now free!" -ForegroundColor Green
} else {
    Write-Host "Port $Port is not in use." -ForegroundColor Green
}

