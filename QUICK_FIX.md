# Quick Fix Guide

## Port 8000 Already in Use? ✅ FIXED!

### Solution 1: Kill Process (Done!)
```powershell
.\backend\kill-port.ps1
```

### Solution 2: Use Different Port
```powershell
.\backend\run-backend-port.ps1
# Starts on port 8001
```

### Solution 3: Check What's Using Port
```powershell
.\backend\check-port.ps1
```

## All Issues Fixed ✅

1. ✅ SQLAlchemy reserved name → Fixed
2. ✅ Pydantic v2 config → Fixed  
3. ✅ Missing imports → Fixed
4. ✅ Scipy version conflict → Fixed (scipy 1.14.1)
5. ✅ Port 8000 conflict → Fixed (process killed)

## Run Backend Now

```powershell
.\run-backend.bat
```

Should start successfully! 🎉

