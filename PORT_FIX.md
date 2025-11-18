# Port 8000 Access Error - Solutions

## Error
```
ERROR: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions
```

This means port 8000 is either:
- Already in use by another process
- Blocked by Windows firewall/antivirus
- Requires admin privileges

## Quick Fixes

### Option 1: Use Different Port (Easiest)

**Windows Batch:**
```batch
.\backend\run-backend-port.bat
```
Or specify custom port:
```batch
.\backend\run-backend-port.bat 9000
```

**PowerShell:**
```powershell
.\backend\run-backend-port.ps1
```
Or specify custom port:
```powershell
.\backend\run-backend-port.ps1 -Port 9000
```

### Option 2: Find and Kill Process Using Port 8000

**Check what's using port 8000:**
```powershell
.\backend\check-port.ps1
```

**Kill the process:**
```powershell
# Replace <PID> with the process ID from check-port.ps1
taskkill /PID <PID> /F
```

**Or manually:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Option 3: Run as Administrator

Right-click PowerShell/CMD → "Run as Administrator", then:
```powershell
.\run-backend.bat
```

### Option 4: Change Default Port in Code

Edit `run-backend.bat` and change:
```batch
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Recommended Solution

Use the alternative port script:
```powershell
.\backend\run-backend-port.ps1
```

This will start on port 8001 by default. Then update frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Common Ports Already in Use

- **8000** - Common development port
- **3000** - React/Next.js default
- **5432** - PostgreSQL default
- **6379** - Redis default

## Test Port Availability

```powershell
Test-NetConnection -ComputerName localhost -Port 8000
```

If it says "TcpTestSucceeded: True", the port is in use.

