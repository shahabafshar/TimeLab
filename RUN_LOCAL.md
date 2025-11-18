# 🐛 Run Locally (No Docker) - For Debugging

## Quick Start

### Step 1: Start Database (PostgreSQL)

**Option A: Use existing PostgreSQL**
- Make sure PostgreSQL is running on port 5432
- Create database: `createdb timelab` (or use pgAdmin)

**Option B: Use SQLite (Simpler for debugging)**
- No setup needed! Backend will use SQLite automatically

### Step 2: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
# For SQLite (easiest):
echo DATABASE_URL=sqlite:///./timelab.db > .env

# For PostgreSQL:
# echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/timelab > .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: http://localhost:8000

### Step 3: Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local

# Start dev server
npm run dev
```

Frontend will be at: http://localhost:3000

## Test It

Open browser:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
# Then update frontend .env.local: NEXT_PUBLIC_API_URL=http://localhost:8001
```

**Database connection error:**
- Check PostgreSQL is running: `pg_isready`
- Or use SQLite (change DATABASE_URL in .env)

**Import errors:**
```bash
# Make sure you're in backend directory
cd backend
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Use different port
npm run dev -- -p 3001
```

**API connection error:**
- Check backend is running: http://localhost:8000/health
- Check .env.local has correct API URL
- Check CORS settings in backend/app/core/config.py

**Module not found:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Skip Redis/Celery (Optional)

For debugging, you can skip Redis and Celery:
- Grid search will still work (just slower, synchronous)
- Other features work fine without Redis

## Environment Variables

### Backend (.env)
```env
# SQLite (simplest)
DATABASE_URL=sqlite:///./timelab.db

# OR PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/timelab

# Optional (for async tasks)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS (allow frontend)
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Quick Commands

**Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Debug Tips

1. **Backend logs:** Check terminal where uvicorn is running
2. **Frontend logs:** Check browser console (F12)
3. **API testing:** Use http://localhost:8000/docs
4. **Database:** Use SQLite for simplicity (no setup needed)
5. **Hot reload:** Both backend and frontend auto-reload on code changes

