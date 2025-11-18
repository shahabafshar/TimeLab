# TimeLab Setup Guide

## 🚀 Super Simple Start

### Windows
```powershell
.\start.ps1
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

That's it! Everything starts automatically.

## 📋 Prerequisites

- **Docker Desktop** (includes Docker Compose)
- **Node.js 18+** (for local frontend development, optional)
- **Python 3.11+** (for local backend development, optional)

## 🐳 Docker Setup (Recommended)

### Quick Start
1. Run the startup script:
   - Windows: `.\start.ps1`
   - Linux/Mac: `./start.sh`

2. Wait ~30 seconds for services to start

3. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Docker Commands

**Start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop services:**
```bash
docker-compose down
```

**Run migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

## 💻 Local Development

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start server:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with API URL (default: http://localhost:8000)
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   Navigate to http://localhost:3000

## 🧪 Testing

### Test API (Simple)

**Windows:**
```powershell
.\test-api.ps1
```

**Linux/Mac:**
```bash
chmod +x test-api.sh
./test-api.sh
```

### Manual API Tests

**Health check:**
```bash
curl http://localhost:8000/health
```

**List datasets:**
```bash
curl http://localhost:8000/api/v1/datasets/
```

**API Documentation:**
Visit http://localhost:8000/docs for interactive API testing

## 📁 Project Structure

```
TimeLab/
├── frontend/          # Next.js React frontend
│   ├── app/           # Next.js pages
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── lib/         # Utilities
│   │   └── types/       # TypeScript types
│   └── package.json
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── api/        # API endpoints
│   │   ├── core/       # Configuration
│   │   ├── models/     # Database models
│   │   ├── services/   # Business logic
│   │   └── schemas/    # Pydantic schemas
│   ├── alembic/        # Database migrations
│   └── requirements.txt
├── arauto/            # Original Arauto (reference)
├── docs/              # Documentation
├── docker-compose.yml # Docker services
├── start.ps1          # Windows startup
├── start.sh           # Linux/Mac startup
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/timelab
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend Environment Variables

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Port Already in Use
If ports 3000, 8000, 5432, or 6379 are in use:
- Stop conflicting services
- Or modify ports in `docker-compose.yml`

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Backend Won't Start
```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend
docker-compose build backend
docker-compose up -d backend
```

### Frontend Won't Start
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 📚 Key Features

- ✅ Data import (CSV, Excel)
- ✅ Time series transformation
- ✅ Stationarity testing
- ✅ ACF/PACF analysis
- ✅ SARIMAX model training
- ✅ Grid search (async)
- ✅ Model evaluation
- ✅ Forecasting
- ✅ Code generation

## 🎯 Next Steps

1. Upload a dataset via API or UI
2. Transform and test stationarity
3. Analyze ACF/PACF
4. Train a SARIMAX model
5. Generate forecasts
6. Export code

## 📖 Additional Documentation

- `README.md` - Main project README
- `QUICK_START.md` - Quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `docs/arauto/` - Arauto analysis docs
