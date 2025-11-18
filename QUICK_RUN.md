# 🚀 Quick Run Guide

## Super Simple - Just Double Click!

### Option 1: Batch Files (.bat) - Easiest!

**Backend:**
- Double-click `run-backend.bat`
- Wait for it to start
- Backend runs at: http://localhost:8000

**Frontend:**
- Double-click `run-frontend.bat`
- Wait for it to start
- Frontend runs at: http://localhost:3000

### Option 2: PowerShell (.ps1)

**Backend:**
- Right-click `run-backend.ps1` → Run with PowerShell
- Or: `.\run-backend.ps1`

**Frontend:**
- Right-click `run-frontend.ps1` → Run with PowerShell
- Or: `.\run-frontend.ps1`

## What Happens Automatically

✅ Creates virtual environment (backend)  
✅ Installs dependencies  
✅ Creates config files  
✅ Runs database migrations  
✅ Starts the server  

## Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Stop

Press `Ctrl+C` in the terminal window

## Troubleshooting

**"Python not found"**
- Install Python 3.11+ from python.org
- Make sure Python is in your PATH

**"npm not found"**
- Install Node.js 18+ from nodejs.org
- Restart terminal after installation

**Port already in use**
- Close other applications using ports 3000 or 8000
- Or modify ports in the scripts

## That's It! 🎉

Just run both files and you're ready to go!

