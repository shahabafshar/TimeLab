@echo off
REM Start Backend on Alternative Port (default: 8001)
set PORT=8001
if not "%1"=="" set PORT=%1

echo Starting TimeLab Backend on port %PORT%...
echo.

cd backend

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file with SQLite...
    echo DATABASE_URL=sqlite:///./timelab.db > .env
)

REM Run migrations
echo Running database migrations...
alembic upgrade head 2>nul

REM Start server
echo.
echo ========================================
echo Backend starting on port %PORT%...
echo ========================================
echo Backend:   http://localhost:%PORT%
echo API Docs:  http://localhost:%PORT%/docs
echo.
echo Press Ctrl+C to stop
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port %PORT%

pause

