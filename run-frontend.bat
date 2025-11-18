@echo off
echo Starting TimeLab Frontend...
echo.

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

REM Create .env.local if it doesn't exist
if not exist ".env.local" (
    echo Creating .env.local file...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
)

REM Start dev server
echo.
echo ========================================
echo Frontend starting...
echo ========================================
echo Frontend:  http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.

call npm run dev

pause

