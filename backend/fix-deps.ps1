# Fix dependencies
Write-Host "Fixing scipy version compatibility..." -ForegroundColor Yellow

& "venv\Scripts\activate.ps1"

Write-Host "Uninstalling scipy..." -ForegroundColor Yellow
pip uninstall scipy -y 2>$null

Write-Host "Installing compatible scipy version (pre-built wheel)..." -ForegroundColor Yellow
pip install "scipy==1.14.1" --only-binary :all:

Write-Host "Testing imports..." -ForegroundColor Yellow
python -c "import scipy; print('scipy version:', scipy.__version__)"
python -c "import statsmodels.api as sm; print('statsmodels import: OK')"
python -c "from app.main import app; print('app import: OK')"

Write-Host "Done!" -ForegroundColor Green
