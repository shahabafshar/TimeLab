# Start Backend - Simple Version
Write-Host "Starting TimeLab Backend..." -ForegroundColor Green
Write-Host ""

Set-Location backend

# Create venv if needed
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies if needed
try {
    python -c "import fastapi" 2>$null
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Create .env if needed
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file with SQLite..." -ForegroundColor Yellow
    "DATABASE_URL=sqlite:///./timelab.db" | Out-File -FilePath ".env" -Encoding utf8
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

# Start server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

