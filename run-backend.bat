@echo off
echo Starting TimeLab Backend...
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
alembic upgrade head

REM Start server
echo.
echo ========================================
echo Backend starting...
echo ========================================
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

