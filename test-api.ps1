# Simple API Test Script for Windows
Write-Host "Testing TimeLab API..." -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"

# Test health endpoint
Write-Host "`n1. Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "   ✓ Health check: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test root endpoint
Write-Host "`n2. Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   ✓ Root endpoint: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Root endpoint failed: $_" -ForegroundColor Red
}

# Test datasets endpoint
Write-Host "`n3. Testing datasets endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/datasets/" -Method Get
    Write-Host "   ✓ Datasets endpoint: Found $($response.Count) datasets" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Datasets endpoint failed: $_" -ForegroundColor Red
}

# Test preprocessing transformations
Write-Host "`n4. Testing preprocessing endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/preprocessing/transformations" -Method Get
    Write-Host "   ✓ Transformations endpoint: $($response.transformations.Count) transformations available" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Transformations endpoint failed: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "API Test Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nVisit http://localhost:8000/docs for full API documentation" -ForegroundColor White

